"""AI soạn câu ôn tập cho MỘT kỹ năng (module 09 · Tuấn · G3b, 25/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md mục 7.3).

    generate(db, skill_id, write=..., need=FULL_EXAM) → {"questions": [...], "rejected": [...], "calls": n, "missing": {...}}

Chỉ SOẠN + KIỂM, **không lưu DB** (Tuấn chốt 25/11): câu chỉ vào ngân hàng (`auto_approved`) sau cổng G3c, trong luồng
soạn ở nền G3d. Ôn theo khóa vẫn dùng đường cũ (review_service, D2).

Luồng: kỹ năng phải MỞ (G3.0) và có đoạn tri thức (G3a, D7) → 2 lần gọi (trắc nghiệm, tự luận) → check_questions →
câu hỏng / còn thiếu thì soạn lại CHỈ phần thiếu, kèm lỗi lần trước, tối đa MAX_RETRIES lần; vẫn hỏng → bỏ (D3).
Mỗi câu: `chunk_id` = đoạn AI ghi trong `passage` (không còn gắn mọi câu vào đoạn đầu) + `ai_check.gen` (phiên bản prompt,
model, lần soạn, câu trích). `write(...)` truyền vào → test dùng AI giả, không gọi mạng. Lỗi AI (503…) → AIUnavailableError
đi thẳng ra ngoài cho người gọi chờ / thử lại (P14).
"""

import logging
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.prompts.review_generate import GEN_PROMPT_VERSION
from app.ai.review.grading_schema import AIOutputError
from app.ai.review.question_schema import check_questions
from app.models.review_question import ReviewQuestion
from app.repositories import knowledge_repository
from app.repositories import skill_scope_repository as scope_repo
from app.services import skill_scope_service

logger = logging.getLogger(__name__)

FULL_EXAM = {"recognize": 6, "understand": 6, "easy": 2, "advanced": 1}  # khung đề 15 câu (G2c)
KINDS = {"mcq": ("recognize", "understand"), "essay": ("easy", "advanced")}
MAX_RETRIES = 2  # D3: soạn lại tối đa 2 lần

# write(skill, passages, kind, need, existing, feedback) -> JSON thô {"questions": [...]}
Write = Callable[[str, list[dict], str, dict, list[str], list[str]], object]


class GenError(Exception):
    """code: not_found | not_open | no_source"""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def existing_contents(db: Session, skill_id: int) -> list[str]:
    """Đề bài đã có của kỹ năng (mọi trạng thái, mới nhất trước) — gửi kèm prompt + so trùng."""
    return list(
        db.scalars(
            select(ReviewQuestion.content)
            .where(ReviewQuestion.skill_id == skill_id)
            .order_by(ReviewQuestion.question_id.desc())
        )
    )


def _generate_kind(
    write: Write, skill, chunks, kind, need, existing, model
) -> tuple[list[dict], list[dict], int, dict]:
    passages = [{"title": c.title, "content": c.content} for c in chunks]
    contents = [c.content for c in chunks]
    left = {level: n for level, n in need.items() if n > 0}
    accepted: list[dict] = []
    rejected: list[dict] = []
    feedback: list[str] = []
    calls = 0
    for attempt in range(1 + MAX_RETRIES):
        if not left:
            break
        calls += 1
        seen = existing + [q["content"] for q in accepted]
        try:
            data = write(skill, passages, kind, left, seen, feedback)
        except AIOutputError as err:
            feedback = [f"the answer was not valid JSON for the schema ({err})"]
            rejected.append({"kind": kind, "attempt": attempt + 1, "errors": feedback})
            continue
        good, errors = check_questions(data, kind, left, passages=contents, existing=seen)
        for q in good:
            chunk = chunks[q.pop("passage") - 1]
            quote = q.pop("source_quote")
            q["chunk_id"] = chunk.chunk_id
            q["ai_check"] = {"gen": {"prompt_version": GEN_PROMPT_VERSION, "model": model or None,
                                     "attempt": attempt + 1, "source_quote": quote}}  # fmt: skip
            left[q["level"]] -= 1
        accepted += good
        left = {level: n for level, n in left.items() if n > 0}
        if errors:
            rejected.append({"kind": kind, "attempt": attempt + 1, "errors": errors})
        feedback = errors[:8]
    return accepted, rejected, calls, left


def generate(db: Session, skill_id: int, *, write: Write, need: dict[str, int] | None = None, model: str = "") -> dict:
    """→ {"skill_id", "skill", "questions": [câu hợp lệ kèm chunk_id + ai_check], "rejected": [{kind, attempt, errors}],
    "calls": số lần gọi AI, "missing": {mức: số câu chưa soạn được}}. KHÔNG ghi DB."""
    name = scope_repo.skill_name(db, skill_id)
    if name is None:
        raise GenError("not_found", "Không tìm thấy kỹ năng.")
    if not skill_scope_service.is_open(db, skill_id):
        raise GenError("not_open", "Kỹ năng chưa được mở cho AI soạn (xem trang Phạm vi kỹ năng).")
    chunks = knowledge_repository.chunks_for_skill(db, skill_id)
    if not chunks:
        raise GenError("no_source", "Kỹ năng chưa có đoạn tài liệu (G3a) — chưa soạn được câu.")

    need = need or FULL_EXAM
    existing = existing_contents(db, skill_id)
    result = {"skill_id": skill_id, "skill": name, "questions": [], "rejected": [], "calls": 0, "missing": {}}
    for kind, levels in KINDS.items():
        part = {level: need.get(level, 0) for level in levels if need.get(level, 0) > 0}
        if not part:
            continue
        accepted, rejected, calls, missing = _generate_kind(write, name, chunks, kind, part, existing, model)
        existing = existing + [q["content"] for q in accepted]
        result["questions"] += accepted
        result["rejected"] += rejected
        result["calls"] += calls
        result["missing"] |= missing
    logger.info("Soạn câu kỹ năng %s (%s): %d câu, %d lần gọi, thiếu %s", skill_id, name, len(result["questions"]),
                result["calls"], result["missing"])  # fmt: skip
    return result
