"""Ôn tập theo KỸ NĂNG — mở từ node lộ trình (module 09 · Tuấn · G2c, 22/11/2026 — docs/guide.md mục 1, 3).

    skill_readiness(db, skill_id)                    → kỹ năng nào trong nhóm tên trùng giữ ngân hàng câu, đủ đề chưa
    start_skill_attempt(db, user, skill_id, path_id) → có lượt dở cùng kỹ năng → trả lại; không → ráp đề mới

Đề 15 câu CÙNG MỘT kỹ năng, cùng khung với ôn theo khóa (exam_builder.plan_exam với 1 kỹ năng): 6 nhận biết +
6 thông hiểu + 2 tự luận dễ + 1 nâng cao. Làm bài / lưu / nộp / chấm / kết quả dùng lại review_service.

Tên trùng (G1): node lộ trình "JavaScript" (#4) nhưng ngân hàng câu gắn "Javascript" (#4919) → đề lấy câu của id
NHIỀU câu nhất trong nhóm tên trùng (skill_search.normalize); lượt vẫn ghi skill_id của node (người học ôn kỹ năng nào).
G2 chỉ dùng câu có sẵn trong ngân hàng; thiếu câu → "Chưa có đề" (AI soạn khi thiếu là G3).
"""

import random
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.review import get_review_ai
from app.ai.review.base import ReviewAI
from app.ai.review.pipeline.skill_search import normalize
from app.core.config import settings
from app.models.review_attempt import ReviewAttempt
from app.models.user import Users
from app.repositories import review_repository as repo
from app.services import exam_builder, review_rag_service
from app.services import review_service as core
from app.services.review_service import ReviewBlockedError, ReviewError

NO_SKILL_BANK = "Chưa có đề ôn tập cho kỹ năng này."


class SkillNotFoundError(ReviewError):
    """Không có kỹ năng này hoặc kỹ năng đã ngừng dùng."""


class PathNotFoundError(ReviewError):
    """Lộ trình không phải của người học / không có node kỹ năng này — 404 như nhau (không lộ lộ trình người khác)."""


class SkillBankMissingError(ReviewError):
    def __init__(self):
        super().__init__(NO_SKILL_BANK)
        self.code = "no_question_bank"
        self.message = NO_SKILL_BANK


@dataclass
class Readiness:
    skill_id: int  # kỹ năng người học chọn (node lộ trình)
    skill: str
    bank_skill_id: int  # kỹ năng giữ ngân hàng câu (có thể là tên trùng khác id)
    available: dict[tuple[int, str], int]  # số câu đang bật của bank_skill_id theo mức độ
    ready: bool


def _group_ids(db: Session, skill_id: int, name: str) -> list[int]:
    """Các id kỹ năng cùng tên chuẩn hóa (nhóm tên trùng của G1), luôn gồm chính skill_id."""
    from app.services import skill_search_service

    index = skill_search_service.get_index(db)
    ids = {index.ids[i] for i in index.by_norm.get(normalize(name), [])}
    return sorted(ids | {skill_id})


def skill_readiness(db: Session, skill_id: int) -> Readiness:
    name = repo.get_active_skill_name(db, skill_id)
    if name is None:
        raise SkillNotFoundError
    ids = _group_ids(db, skill_id, name)
    counts = repo.bank_counts(db, ids)
    totals = {i: sum(n for (s, _), n in counts.items() if s == i) for i in ids}
    bank_id = max(ids, key=lambda i: (totals[i], i == skill_id, -i))  # nhiều câu nhất; bằng nhau → chính nó
    available = {k: n for k, n in counts.items() if k[0] == bank_id}
    try:
        exam_builder.plan_exam([bank_id], available, random.Random(0))
        ready = True
    except exam_builder.NotEnoughQuestionsError:
        ready = False
    return Readiness(skill_id, name, bank_id, available, ready)


def start_skill_attempt(
    db: Session,
    user: Users,
    skill_id: int,
    path_id: int | None = None,
    *,
    rng: random.Random | None = None,
    ai: ReviewAI | None = None,
    embedder: review_rag_service.Embedder | None = None,
) -> dict:
    info = skill_readiness(db, skill_id)
    if path_id is not None and not repo.path_has_skill(db, path_id, user.user_id, skill_id):
        raise PathNotFoundError

    existing = repo.get_in_progress(db, user.user_id, skill_id=skill_id)
    if existing:
        return core.attempt_view(db, existing.attempt_id, resumed=True)
    if repo.count_in_progress(db, user.user_id) >= settings.REVIEW_MAX_UNFINISHED:
        raise ReviewBlockedError("too_many_unfinished")
    if not info.ready:
        raise SkillBankMissingError

    rng = rng or random.Random()
    ai = ai or get_review_ai()
    bank_id = info.bank_skill_id
    previous = repo.last_submitted_questions(db, user.user_id, skill_id=skill_id)
    family = repo.family_questions(db, [q.question_id for q in previous])  # tránh mọi phiên bản cùng họ (7.5a)
    fresh = dict(info.available)
    for q in family:
        if q.is_active and (q.skill_id, q.level) in fresh:
            fresh[(q.skill_id, q.level)] -= 1
    try:
        plan = exam_builder.plan_exam([bank_id], info.available, rng, fresh=fresh)
    except exam_builder.NotEnoughQuestionsError:
        raise SkillBankMissingError from None

    avoid = {q.question_id for q in family}
    trace = core._new_trace(ai, avoid)
    trace.update(mode="skill", skill_id=skill_id, bank_skill_id=bank_id, path_id=path_id)
    try:
        picked = core.pick_questions(db, title=info.skill, names={bank_id: info.skill}, plan=plan, ai=ai, rng=rng,
                                     embedder=embedder, avoid=avoid, trace=trace)  # fmt: skip
    except exam_builder.NotEnoughQuestionsError:
        raise SkillBankMissingError from None
    attempt = ReviewAttempt(user_id=user.user_id, skill_id=skill_id, path_id=path_id, trace=trace)
    return core.save_new_attempt(
        db, attempt, picked, rng, lambda: repo.get_in_progress(db, user.user_id, skill_id=skill_id)
    )
