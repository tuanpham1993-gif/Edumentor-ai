"""AI soạn câu ôn tập cho MỘT kỹ năng (module 09 · Tuấn · G3b, 25/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md mục 7.3).

    generate(db, skill_id, write=..., need=FULL_EXAM) → {"questions": [...], "rejected": [...], "calls": n, "missing": {...}}

Chỉ SOẠN + KIỂM, **không lưu DB** (Tuấn chốt 25/11): câu chỉ vào ngân hàng (`auto_approved`) sau cổng G3c, trong luồng
soạn ở nền G3d. Ôn theo khóa vẫn dùng đường cũ (review_service, D2).

Luồng: kỹ năng phải MỞ (G3.0) và có đoạn tri thức (G3a, D7) → 2 lần gọi (trắc nghiệm, tự luận) → check_questions →
cổng G3c (ai/review/question_gate.py: giải mù, L1, gần trùng theo nghĩa, bài giả tự luận) → câu hỏng / còn thiếu thì
soạn lại CHỈ phần thiếu, kèm lý do, tối đa MAX_RETRIES lần; vẫn hỏng → bỏ (D3).
Mỗi câu: `chunk_id` = đoạn AI ghi trong `passage` (không còn gắn mọi câu vào đoạn đầu) + `ai_check.gen` (phiên bản prompt,
model, lần soạn, câu trích). `write(...)` truyền vào → test dùng AI giả, không gọi mạng. Lỗi AI (503…) → AIUnavailableError
đi thẳng ra ngoài cho người gọi chờ / thử lại (P14).
"""

import logging
import random
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.prompts.review_generate import GEN_PROMPT_VERSION
from app.ai.review.grading_schema import AIOutputError
from app.ai.review.question_gate import Embed, GateContext, Solve, model_answer, run_gate
from app.ai.review.question_schema import check_questions
from app.models.review_question import ReviewQuestion
from app.repositories import knowledge_repository
from app.repositories import skill_scope_repository as scope_repo
from app.services import skill_scope_service

logger = logging.getLogger(__name__)

FULL_EXAM = {"recognize": 6, "understand": 6, "easy": 2, "advanced": 1}  # khung đề 15 câu (G2c)
SKILL_TARGET = {"recognize": 12, "understand": 12, "easy": 4, "advanced": 2}  # ~30 câu / kỹ năng (D25)
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


def existing_questions(db: Session, skill_id: int) -> list[tuple[int, str, str]]:
    """(question_id, đề, loại) đã có của kỹ năng (mọi trạng thái, mới nhất trước) — gửi kèm prompt + so trùng."""
    return list(
        db.execute(
            select(ReviewQuestion.question_id, ReviewQuestion.content, ReviewQuestion.type)
            .where(ReviewQuestion.skill_id == skill_id)
            .order_by(ReviewQuestion.question_id.desc())
        ).all()
    )


def existing_contents(db: Session, skill_id: int) -> list[str]:
    return [content for _, content, _ in existing_questions(db, skill_id)]


def _generate_kind(
    write: Write, chunks, kind, need, ctx: GateContext, model
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
        seen = [content for _, content, _ in ctx.existing]
        try:
            data = write(ctx.skill, passages, kind, left, seen, feedback)
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
        # G3c: cổng kiểm — câu hỏng bị loại, lý do gửi lại cho AI khi soạn lại (D3)
        passed, failed = run_gate(good, kind, ctx)
        errors = [f'Question "{q["content"][:60]}": {reason}' for q, reason in failed] + errors
        for q in passed:
            left[q["level"]] -= 1
            ctx.existing.append((None, q["content"], kind))
            if kind == "essay":
                ctx.other_answers.append(model_answer(q))
        accepted += passed
        left = {level: n for level, n in left.items() if n > 0}
        if left and not any(e.startswith("still missing") for e in errors):
            errors.append("still missing: " + ", ".join(f"{n} {level}" for level, n in left.items()))
        if errors:
            rejected.append({"kind": kind, "attempt": attempt + 1, "errors": errors,
                             "gate_failed": len(failed)})  # fmt: skip
        feedback = errors[:8]
    return accepted, rejected, calls, left


def generate(
    db: Session,
    skill_id: int,
    *,
    write: Write,
    need: dict[str, int] | None = None,
    model: str = "",
    solve: Solve | None = None,
    embed: Embed | None = None,
    rng: random.Random | None = None,
) -> dict:
    """→ {"skill_id", "skill", "questions": [câu đạt cổng kèm chunk_id + ai_check {gen, gate}], "rejected": [...],
    "calls": số lần gọi AI soạn, "solve_calls": số lần gọi giải mù, "missing": {mức: số câu chưa soạn được}}.
    solve / embed = None → bỏ qua phép kiểm tương ứng (ghi "skipped"). KHÔNG ghi DB."""
    name = scope_repo.skill_name(db, skill_id)
    if name is None:
        raise GenError("not_found", "Không tìm thấy kỹ năng.")
    if not skill_scope_service.is_open(db, skill_id):
        raise GenError("not_open", "Kỹ năng chưa được mở cho AI soạn (xem trang Phạm vi kỹ năng).")
    chunks = knowledge_repository.chunks_for_skill(db, skill_id)
    if not chunks:
        raise GenError("no_source", "Kỹ năng chưa có đoạn tài liệu (G3a) — chưa soạn được câu.")

    solve_calls = 0

    def counted_solve(skill, items):
        nonlocal solve_calls
        solve_calls += 1
        return solve(skill, items)

    ctx = GateContext(
        skill=name,
        chunks={c.chunk_id: c.content for c in chunks},
        existing=existing_questions(db, skill_id),
        solve=counted_solve if solve else None,
        embed=embed,
        rng=rng or random.Random(),
    )
    need = need or FULL_EXAM
    result = {"skill_id": skill_id, "skill": name, "questions": [], "rejected": [], "calls": 0, "missing": {}}
    for kind, levels in KINDS.items():
        part = {level: need.get(level, 0) for level in levels if need.get(level, 0) > 0}
        if not part:
            continue
        accepted, rejected, calls, missing = _generate_kind(write, chunks, kind, part, ctx, model)
        result["questions"] += accepted
        result["rejected"] += rejected
        result["calls"] += calls
        result["missing"] |= missing
    result["solve_calls"] = solve_calls
    logger.info("Soạn câu kỹ năng %s (%s): %d câu, %d lần soạn + %d lần giải mù, thiếu %s", skill_id, name,
                len(result["questions"]), result["calls"], solve_calls, result["missing"])  # fmt: skip
    return result
