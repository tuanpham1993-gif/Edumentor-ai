"""Ôn tập theo KỸ NĂNG — mở từ node lộ trình (module 09 · Tuấn · G2c, 22/11/2026 — docs/guide.md mục 1, 3).

    skill_readiness(db, skill_id)                    → kỹ năng nào trong nhóm tên trùng giữ ngân hàng câu, đủ đề chưa
    skill_review_info   GET  /skills/{id}/review               — thông tin + lý do chưa thể ôn (G2d)
    start_skill_attempt POST /skills/{id}/review-attempts?path= — có lượt dở cùng kỹ năng → trả lại; không → ráp đề
    direct_review(db, user, skill_id)                → phần "ôn thẳng theo kỹ năng" của huy hiệu trên node lộ trình

Đề 15 câu CÙNG MỘT kỹ năng, cùng khung với ôn theo khóa (exam_builder.plan_exam với 1 kỹ năng): 6 nhận biết +
6 thông hiểu + 2 tự luận dễ + 1 nâng cao. Làm bài / lưu / nộp / chấm / kết quả dùng lại review_service.

Tên trùng (G1): node lộ trình "JavaScript" (#4) nhưng ngân hàng câu gắn "Javascript" (#4919) → đề lấy câu của id
NHIỀU câu nhất trong nhóm tên trùng (skill_search.normalize); lượt vẫn ghi skill_id của node (người học ôn kỹ năng nào).
G3d-1 (25/11): ngân hàng gồm câu đã duyệt + câu AI tự duyệt (`include_auto`). Ráp đề CHỈ bốc câu có sẵn (không gọi
đường sinh câu cũ của ôn theo khóa). Thiếu câu → kỹ năng soạn được (Mở + có nguồn + có AI thật) thì tạo việc soạn ở nền
(review_generation_service) và báo GenerationPending (API trả 202 + tiến độ); không soạn được → "Chưa có đề" như G2.
"""

import random
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.review.base import ReviewAI
from app.ai.review.mock_ai import MockAI
from app.ai.review.pipeline.skill_search import normalize
from app.core.config import settings
from app.models.review_attempt import ReviewAttempt
from app.models.user import Users
from app.repositories import review_repository as repo
from app.services import exam_builder, review_rag_service
from app.services import review_service as core
from app.services.review_service import ReviewBlockedError, ReviewError

NO_SKILL_BANK = "Chưa có đề ôn tập cho kỹ năng này."
NOT_OPEN = "Kỹ năng này chưa được mở cho AI soạn đề ôn tập."


class SkillNotFoundError(ReviewError):
    """Không có kỹ năng này hoặc kỹ năng đã ngừng dùng."""


class PathNotFoundError(ReviewError):
    """Lộ trình không phải của người học / không có node kỹ năng này — 404 như nhau (không lộ lộ trình người khác)."""


class SkillBankMissingError(ReviewError):
    def __init__(self, message: str = NO_SKILL_BANK):
        super().__init__(message)
        self.code = "no_question_bank"
        self.message = message


class GenerationPending(ReviewError):
    """Thiếu câu → đang soạn ở nền (G3d). job: review_generation_service.job_view."""

    def __init__(self, job: dict):
        super().__init__("Đang soạn đề")
        self.job = job


class _BankOnly(MockAI):
    """Ôn theo kỹ năng chỉ bốc câu CÓ SẴN — không gọi đường sinh câu cũ (lỗ hổng B, G3d-1)."""

    name = "bank"


def _missing_message(reason: str | None) -> str:
    return NOT_OPEN if reason == "not_open" else NO_SKILL_BANK


def _topup_if_short(db: Session, user: Users, bank_id: int, fresh: dict) -> None:
    """D25 (G3d-3): làm lại mà không đủ câu CHƯA làm ở lượt trước cho một đề → ngân hàng chưa tới ~30 câu và AI soạn được
    thì tạo việc soạn bổ sung + GenerationPending ("Đề mới đang được soạn"); không thì ráp đề như cũ (lặp một phần)."""
    from app.services import question_gen_service
    from app.services import review_generation_service as gen

    short = any(fresh.get((bank_id, lv), 0) < n for lv, n in question_gen_service.FULL_EXAM.items())
    if not short or not gen.missing_for(db, bank_id, "topup") or gen.cannot_generate(db, bank_id):
        return
    raise GenerationPending(gen.job_view(gen.request(db, bank_id, user.user_id, kind="topup")))


def _generate_or_missing(db: Session, user: Users, info: "Readiness"):
    """Thiếu câu: soạn được → tạo / vào việc soạn rồi ném GenerationPending; không → SkillBankMissingError."""
    from app.services import review_generation_service as gen

    try:
        job = gen.request(db, info.bank_skill_id, user.user_id)
    except gen.GenerationError as err:
        raise SkillBankMissingError(_missing_message(err.code)) from None
    raise GenerationPending(gen.job_view(job))


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
    counts = repo.bank_counts(db, ids, include_auto=True)  # G3d: + câu AI tự duyệt
    totals = {i: sum(n for (s, _), n in counts.items() if s == i) for i in ids}
    bank_id = max(ids, key=lambda i: (totals[i], i == skill_id, -i))  # nhiều câu nhất; bằng nhau → chính nó
    available = {k: n for k, n in counts.items() if k[0] == bank_id}
    try:
        exam_builder.plan_exam([bank_id], available, random.Random(0))
        ready = True
    except exam_builder.NotEnoughQuestionsError:
        ready = False
    return Readiness(skill_id, name, bank_id, available, ready)


def _blocked(code: str) -> dict:
    message = NO_SKILL_BANK if code == "no_question_bank" else core.block_message(code)
    return {"code": code, "message": message}


def skill_review_info(db: Session, user: Users, skill_id: int) -> dict:
    info = skill_readiness(db, skill_id)
    core.recover_stuck_grading(db, user)
    in_progress = repo.get_in_progress(db, user.user_id, skill_id=skill_id)
    from app.services import review_generation_service as gen

    block, unfinished, reason = None, [], None
    if in_progress is None:
        unfinished = repo.list_in_progress(db, user.user_id)
        if len(unfinished) >= settings.REVIEW_MAX_UNFINISHED:
            block = "too_many_unfinished"
        elif not info.ready:
            reason = gen.cannot_generate(db, info.bank_skill_id)
            if reason:
                block = "no_question_bank"
    job = gen.latest_job(db, info.bank_skill_id) if not info.ready else None
    if block == "no_question_bank":
        blocked = {"code": block, "message": _missing_message(reason)}
    else:
        blocked = _blocked(block) if block else None
    return {
        "skill_id": skill_id,
        "skill": info.skill,
        "structure": core._structure(),
        "pass_score": settings.REVIEW_PASS_SCORE,
        "can_start": block is None,
        "blocked": blocked,
        "will_generate": in_progress is None and not info.ready and block is None,  # G3d: bấm Bắt đầu → AI soạn
        "generation": gen.job_view(job),
        "in_progress_attempt_id": in_progress.attempt_id if in_progress else None,
        "unfinished_attempts": core._unfinished_view(db, unfinished) if block == "too_many_unfinished" else [],
        "attempts": [core._summary(a) for a in repo.list_attempts(db, user.user_id, skill_id=skill_id)],
    }


def direct_review(db: Session, user: Users, skill_id: int) -> dict | None:
    """{ready, in_progress_attempt_id, last_attempt} — None nếu kỹ năng không tồn tại / ngừng dùng."""
    try:
        info = skill_readiness(db, skill_id)
    except SkillNotFoundError:
        return None
    attempts = repo.list_attempts(db, user.user_id, skill_id=skill_id)  # mới nhất trước
    in_progress = next((a for a in attempts if a.status == "in_progress"), None)
    last = next((a for a in attempts if a.status in ("graded", "grading")), None)
    from app.services import review_generation_service as gen

    return {
        "ready": info.ready,
        "can_generate": not info.ready and gen.cannot_generate(db, info.bank_skill_id) is None,  # G3d
        "in_progress_attempt_id": in_progress.attempt_id if in_progress else None,
        "last_attempt": core._summary(last) if last else None,
    }


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
        _generate_or_missing(db, user, info)

    rng = rng or random.Random()
    ai = ai or _BankOnly()
    bank_id = info.bank_skill_id
    previous = repo.last_submitted_questions(db, user.user_id, skill_id=skill_id)
    family, avoid = core.recent_avoid(db, user.user_id, skill_id=skill_id)  # 3 lượt gần nhất (D29), cả họ (7.5a)
    fresh = dict(info.available)
    for q in family:
        if q.is_active and (q.skill_id, q.level) in fresh:
            fresh[(q.skill_id, q.level)] -= 1
    if previous:
        _topup_if_short(db, user, bank_id, fresh)
    try:
        plan = exam_builder.plan_exam([bank_id], info.available, rng, fresh=fresh)
    except exam_builder.NotEnoughQuestionsError:
        raise SkillBankMissingError from None

    trace = core._new_trace(ai, avoid)
    trace.update(mode="skill", skill_id=skill_id, bank_skill_id=bank_id, path_id=path_id)
    try:
        picked = core.pick_questions(db, title=info.skill, names={bank_id: info.skill}, plan=plan, ai=ai, rng=rng,
                                     embedder=embedder, avoid=avoid, trace=trace, include_auto=True)  # fmt: skip
    except exam_builder.NotEnoughQuestionsError:
        raise SkillBankMissingError from None
    attempt = ReviewAttempt(user_id=user.user_id, skill_id=skill_id, path_id=path_id, trace=trace)
    return core.save_new_attempt(
        db, attempt, picked, rng, lambda: repo.get_in_progress(db, user.user_id, skill_id=skill_id)
    )
