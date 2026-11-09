"""Nghiệp vụ ôn tập — luồng chính (module 09 · Tuấn · GĐ2, 09/11/2026).

    review_info     GET   /courses/{id}/review             — thông tin + lý do chưa thể ôn
    start_attempt   POST  /courses/{id}/review-attempts    — có lượt dở → trả lại; không → sinh đề mới
    get_attempt     GET   /review-attempts/{id}            — đề + câu trả lời đã lưu (không lộ đáp án)
    save_answers    PATCH /review-attempts/{id}/answers    — lưu khi Tạm rời (FR-29)

Sinh đề (A1, A4–A6 — chốt 09/11), cho TỪNG kỹ năng theo khung exam_builder.plan_exam:
    RAG lấy đoạn tri thức → dựng prompt thật → AI (mock: bốc câu gắn với đoạn RAG)
    → validator kiểm → sai thì sinh lại (≤ MAX_RETRIES) → vẫn sai / AI lỗi thì NGÂN HÀNG DỰ PHÒNG.
    Mọi bước ghi vào attempt.trace (xem qua API debug admin — GĐ3).
CHỈ service này commit (một lần cho mỗi thao tác).
"""

import logging
import random

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.ai.prompts.review import GENERATE_SYSTEM_PROMPT, build_generation_prompt
from app.ai.review import get_review_ai
from app.ai.review.base import AIUnavailableError, GenerationRequest, ReviewAI
from app.ai.review.mock_ai import pick_from_bank
from app.ai.review.validator import generated_errors
from app.core.config import settings
from app.models.review_attempt import ReviewAnswer, ReviewAttempt
from app.models.review_question import ReviewQuestion
from app.models.user import Users
from app.repositories import review_repository as repo
from app.schemas.review import SaveAnswersRequest
from app.services import course_gateway, exam_builder, rag_service

logger = logging.getLogger(__name__)

MAX_RETRIES = 2  # sinh lại tối đa 2 lần khi AI trả sai định dạng (A6)

BLOCK_MESSAGES = {
    "not_enrolled": "Bạn chưa tham gia khóa học này. Hãy tham gia khóa học để ôn tập.",
    "abandoned": "Bạn đã bỏ khóa học này. Tham gia lại khóa học để ôn tập.",
    "no_question_bank": "Chưa có đề ôn tập cho khóa học này.",
}


class ReviewError(Exception):
    pass


class CourseNotFoundError(ReviewError):
    pass


class ReviewBlockedError(ReviewError):
    def __init__(self, code: str):
        super().__init__(BLOCK_MESSAGES[code])
        self.code = code
        self.message = BLOCK_MESSAGES[code]


class AttemptNotFoundError(ReviewError):
    """Không có lượt này HOẶC lượt của người khác — trả 404 như nhau để không lộ lượt có tồn tại (Q6)."""


class AttemptLockedError(ReviewError):
    """Lượt đã nộp — không sửa câu trả lời được nữa."""


class InvalidAnswerError(ReviewError):
    pass


# ─────────────── Thông tin ôn tập ───────────────


def _enrollment_block(db: Session, user: Users, course_id: int) -> str | None:
    status = course_gateway.get_enrollment_status(db, user.user_id, course_id)
    if status == course_gateway.ABANDONED:
        return "abandoned"
    if status not in (course_gateway.IN_PROGRESS, course_gateway.COMPLETED):
        return "not_enrolled"
    return None


def _has_question_bank(db: Session, skill_ids: list[int]) -> bool:
    try:
        exam_builder.plan_exam(skill_ids, repo.bank_counts(db, skill_ids), random.Random(0))
    except exam_builder.NotEnoughQuestionsError:
        return False
    return True


def _structure() -> dict:
    return {
        **exam_builder.STRUCTURE,
        "total_questions": exam_builder.TOTAL_QUESTIONS,
        "max_score": 10.0,
    }


def _summary(a: ReviewAttempt) -> dict:
    return {
        "attempt_id": a.attempt_id,
        "status": a.status,
        "score": float(a.score) if a.score is not None else None,
        "passed": a.passed,
        "started_at": a.started_at,
        "submitted_at": a.submitted_at,
    }


def review_info(db: Session, user: Users, course_id: int) -> dict:
    title = repo.get_course_title(db, course_id)
    if title is None:
        raise CourseNotFoundError
    skills = repo.course_skills(db, course_id)
    in_progress = repo.get_in_progress(db, user.user_id, course_id)

    block = _enrollment_block(db, user, course_id)
    if block is None and in_progress is None and not _has_question_bank(db, [s for s, _ in skills]):
        block = "no_question_bank"

    return {
        "course_id": course_id,
        "course_title": title,
        "skills": [{"skill_id": s, "skill": name} for s, name in skills],
        "structure": _structure(),
        "pass_score": settings.REVIEW_PASS_SCORE,
        "can_start": block is None,
        "blocked": {"code": block, "message": BLOCK_MESSAGES[block]} if block else None,
        "in_progress_attempt_id": in_progress.attempt_id if in_progress else None,
        "attempts": [_summary(a) for a in repo.list_attempts(db, user.user_id, course_id)],
    }


# ─────────────── Sinh đề ───────────────


def _question_dict(q: ReviewQuestion) -> dict:
    return {
        "question_id": q.question_id,
        "chunk_id": q.chunk_id,
        "type": q.type,
        "level": q.level,
        "content": q.content,
        "options": q.options,
        "correct_index": q.correct_index,
        "rubric": q.rubric,
        "explanation": q.explanation,
    }


def _generate_with_fallback(
    ai: ReviewAI, request: GenerationRequest, rng: random.Random
) -> tuple[list[dict], dict]:
    """AI sinh → validator → sinh lại ≤ MAX_RETRIES → ngân hàng dự phòng. Trả (câu hỏi, vết)."""
    errors: list[str] = []
    for _ in range(1 + MAX_RETRIES):
        try:
            questions = ai.generate_questions(request, rng)
        except AIUnavailableError as err:
            errors.append(f"AI không dùng được: {err}")
            break
        problems = generated_errors(questions, request.need)
        if not problems:
            return questions, {"retries": len(errors), "fallback": False, "errors": errors}
        errors.append("; ".join(problems[:3]))
        logger.warning("Ôn tập: AI trả câu không hợp lệ (kỹ năng %s): %s", request.skill_id, problems[:3])

    questions = pick_from_bank(
        request.candidates, request.need, rng, avoid_question_ids=request.avoid_question_ids
    )
    if generated_errors(questions, request.need):
        raise exam_builder.NotEnoughQuestionsError(f"Ngân hàng kỹ năng {request.skill_id} không đủ câu")
    return questions, {"retries": len(errors), "fallback": True, "errors": errors}


def _save_ai_question(db: Session, skill_id: int, q: dict) -> int:
    """Câu AI sinh MỚI (giai đoạn 2) → lưu vào ngân hàng, source='ai' (ngân hàng bước 3)."""
    row = ReviewQuestion(
        skill_id=skill_id,
        chunk_id=q.get("chunk_id"),
        type=q["type"],
        level=q["level"],
        content=q["content"],
        options=q.get("options"),
        correct_index=q.get("correct_index"),
        rubric=q.get("rubric"),
        explanation=q.get("explanation"),
        source="ai",
    )
    db.add(row)
    db.flush()
    return row.question_id


def start_attempt(
    db: Session,
    user: Users,
    course_id: int,
    *,
    rng: random.Random | None = None,
    ai: ReviewAI | None = None,
    embedder: rag_service.Embedder | None = None,
) -> dict:
    title = repo.get_course_title(db, course_id)
    if title is None:
        raise CourseNotFoundError
    block = _enrollment_block(db, user, course_id)
    if block:
        raise ReviewBlockedError(block)

    existing = repo.get_in_progress(db, user.user_id, course_id)
    if existing:
        return attempt_view(db, existing.attempt_id, resumed=True)

    rng = rng or random.Random()
    ai = ai or get_review_ai()
    skills = repo.course_skills(db, course_id)
    names = dict(skills)
    skill_ids = list(names)
    previous = repo.last_submitted_questions(db, user.user_id, course_id)
    available = repo.bank_counts(db, skill_ids)
    fresh = dict(available)
    for q in previous:
        if q.is_active and (q.skill_id, q.level) in fresh:
            fresh[(q.skill_id, q.level)] -= 1
    try:
        plan = exam_builder.plan_exam(
            skill_ids,
            available,
            rng,
            previous_skill_ids={q.skill_id for q in previous},
            fresh=fresh,
        )
    except exam_builder.NotEnoughQuestionsError:
        raise ReviewBlockedError("no_question_bank") from None

    avoid = {q.question_id for q in previous}
    trace = {
        "ai_mode": settings.AI_MODE,
        "ai": ai.name,
        "embedding_model": settings.REVIEW_EMBEDDING_MODEL,
        "system_prompt": GENERATE_SYSTEM_PROMPT,
        "avoided_question_ids": sorted(avoid),
        "skills": [],
    }
    picked: list[dict] = []
    try:
        for skill_id, need in plan.items():
            chunks = rag_service.retrieve_chunks(db, skill_id, names[skill_id], embedder=embedder)
            prompt = build_generation_prompt(
                course_title=title, skill_name=names[skill_id], chunks=chunks, need=need
            )
            request = GenerationRequest(
                course_title=title,
                skill_id=skill_id,
                skill_name=names[skill_id],
                need=need,
                chunks=chunks,
                candidates=[_question_dict(q) for q in repo.bank_questions(db, skill_id)],
                avoid_question_ids=avoid,
                system_prompt=GENERATE_SYSTEM_PROMPT,
                prompt=prompt,
            )
            questions, info = _generate_with_fallback(ai, request, rng)
            picked += [{**q, "skill_id": skill_id} for q in questions]
            trace["skills"].append(
                {
                    "skill_id": skill_id,
                    "skill": names[skill_id],
                    "need": need,
                    "chunks": [{"chunk_id": c.chunk_id, "code": c.code, "score": c.score} for c in chunks],
                    "prompt": prompt,
                    **info,
                }
            )
    except exam_builder.NotEnoughQuestionsError:
        raise ReviewBlockedError("no_question_bank") from None

    attempt = ReviewAttempt(user_id=user.user_id, course_id=course_id, trace=trace)
    for item in exam_builder.order_exam(picked, rng):
        question_id = item.get("question_id") or _save_ai_question(db, item["skill_id"], item)
        attempt.answers.append(
            ReviewAnswer(
                position=item["position"],
                question_id=question_id,
                option_order=item.get("option_order"),
                max_points=item["max_points"],
            )
        )
    db.add(attempt)
    try:
        db.commit()
    except IntegrityError:
        # Bấm "Bắt đầu" 2 lần cùng lúc: unique index chỉ cho 1 lượt đang làm → trả lại lượt kia.
        db.rollback()
        existing = repo.get_in_progress(db, user.user_id, course_id)
        if existing is None:
            raise
        return attempt_view(db, existing.attempt_id, resumed=True)
    return attempt_view(db, attempt.attempt_id, resumed=False)


# ─────────────── Xem đề, lưu câu trả lời ───────────────


def _owned_attempt(db: Session, user: Users, attempt_id: int) -> ReviewAttempt:
    attempt = repo.get_attempt(db, attempt_id)
    if attempt is None or attempt.user_id != user.user_id:
        raise AttemptNotFoundError
    return attempt


def _is_answered(a: ReviewAnswer) -> bool:
    return a.selected_index is not None or bool(a.text_answer and a.text_answer.strip())


def attempt_view(db: Session, attempt_id: int, *, resumed: bool = False) -> dict:
    db.expire_all()  # đọc lại từ DB (sau commit) cho chắc
    attempt = repo.get_attempt(db, attempt_id)
    names = repo.skill_names(db, [a.question.skill_id for a in attempt.answers])
    questions = []
    for a in attempt.answers:
        q = a.question
        options = [q.options[i] for i in a.option_order] if q.type == "mcq" else None
        questions.append(
            {
                "position": a.position,
                "type": q.type,
                "level": q.level,
                "skill_id": q.skill_id,
                "skill": names.get(q.skill_id, ""),
                "content": q.content,
                "options": options,
                "max_points": float(a.max_points),
                "selected_index": a.selected_index,
                "text_answer": a.text_answer,
            }
        )
    return {
        "attempt_id": attempt.attempt_id,
        "course_id": attempt.course_id,
        "course_title": repo.get_course_title(db, attempt.course_id) or "",
        "status": attempt.status,
        "started_at": attempt.started_at,
        "resumed": resumed,
        "answered": sum(_is_answered(a) for a in attempt.answers),
        "total_questions": len(attempt.answers),
        "questions": questions,
    }


def get_attempt(db: Session, user: Users, attempt_id: int) -> dict:
    _owned_attempt(db, user, attempt_id)
    return attempt_view(db, attempt_id)


def save_answers(db: Session, user: Users, attempt_id: int, request: SaveAnswersRequest) -> dict:
    """Lưu một phần hoặc toàn bộ câu trả lời. Sai ở câu nào → báo, KHÔNG lưu câu nào."""
    attempt = _owned_attempt(db, user, attempt_id)
    if attempt.status != "in_progress":
        raise AttemptLockedError
    by_position = {a.position: a for a in attempt.answers}

    for item in request.answers:
        answer = by_position.get(item.position)
        if answer is None:
            raise InvalidAnswerError(f"Câu {item.position} không có trong đề.")
        sent = item.model_fields_set
        if answer.question.type == "mcq" and "text_answer" in sent:
            raise InvalidAnswerError(f"Câu {item.position} là trắc nghiệm — gửi selected_index.")
        if answer.question.type == "essay" and "selected_index" in sent:
            raise InvalidAnswerError(f"Câu {item.position} là tự luận — gửi text_answer.")

    for item in request.answers:
        answer = by_position[item.position]
        sent = item.model_fields_set
        if "selected_index" in sent:
            answer.selected_index = item.selected_index
        if "text_answer" in sent:
            text = (item.text_answer or "").strip()
            answer.text_answer = text or None
    db.commit()
    return attempt_view(db, attempt_id)
