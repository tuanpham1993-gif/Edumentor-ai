"""Nghiệp vụ ôn tập — luồng chính (module 09 · Tuấn · GĐ2, 09/11/2026).

    review_info     GET   /courses/{id}/review             — thông tin + lý do chưa thể ôn
    start_attempt   POST  /courses/{id}/review-attempts    — có lượt dở → trả lại; không → sinh đề mới
    get_attempt     GET   /review-attempts/{id}            — đề + câu trả lời đã lưu (không lộ đáp án)
    save_answers    PATCH /review-attempts/{id}/answers    — lưu khi Tạm rời (FR-29)
    submit_attempt  POST  /review-attempts/{id}/submit     — chấm + (đạt lần đầu) Hoàn thành khóa + kỹ năng
                                                            (AI chấm quá 20 giây → "grading", chấm tiếp ở nền — T1)
    history_list    GET   /me/review-history               — các lượt đã nộp
    history_detail  GET   /me/review-history/{id}          — từng câu, đáp án đúng, điểm từng ý + bằng chứng
    attempt_trace   GET   /admin/review-attempts/{id}/trace — vết RAG + prompt (admin)

Sinh đề (A1, A4–A6 — chốt 09/11), cho TỪNG kỹ năng theo khung exam_builder.plan_exam:
    RAG lấy đoạn tri thức → dựng prompt thật → AI (mock: bốc câu gắn với đoạn RAG)
    → validator kiểm → sai thì sinh lại (≤ MAX_RETRIES) → vẫn sai / AI lỗi thì NGÂN HÀNG DỰ PHÒNG.
    Mọi bước ghi vào attempt.trace (xem qua API debug admin — GĐ3).
CHỈ service này commit (một lần cho mỗi thao tác).
"""

import logging
import random
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.ai.prompts.review import GENERATE_SYSTEM_PROMPT, build_generation_prompt
from app.ai.review import get_review_ai
from app.ai.review.base import AIUnavailableError, GenerationRequest, ReviewAI
from app.ai.review.mock_ai import pick_from_bank
from app.ai.review.validator import generated_errors
from app.core import database
from app.core.config import settings
from app.core.email import send_review_result_email
from app.models.review_attempt import ReviewAnswer, ReviewAttempt
from app.models.review_question import ReviewQuestion
from app.models.user import Users
from app.repositories import review_repository as repo
from app.schemas.review import SaveAnswersRequest
from app.services import (
    course_gateway,
    exam_builder,
    notification_service,
    review_bank_service,
    review_due_service,
    review_grader,
    review_rag_service,
    user_skill_service,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 2  # sinh lại tối đa 2 lần khi AI trả sai định dạng (A6)

BLOCK_MESSAGES = {
    "not_enrolled": "Bạn chưa tham gia khóa học này. Hãy tham gia khóa học để ôn tập.",
    "abandoned": "Bạn đã bỏ khóa học này. Tham gia lại khóa học để ôn tập.",
    "no_question_bank": "Chưa có đề ôn tập cho khóa học này.",
    # 19/11: đã đủ REVIEW_MAX_UNFINISHED bài làm dở (số thật điền lúc báo — xem block_message)
    "too_many_unfinished": "Bạn đang có {n} bài ôn tập làm dở. Hãy hoàn thành hoặc bỏ bớt một bài để bắt đầu bài mới.",
}


def block_message(code: str) -> str:
    return BLOCK_MESSAGES[code].format(n=settings.REVIEW_MAX_UNFINISHED)


class ReviewError(Exception):
    pass


class CourseNotFoundError(ReviewError):
    pass


class ReviewBlockedError(ReviewError):
    def __init__(self, code: str):
        super().__init__(block_message(code))
        self.code = code
        self.message = block_message(code)


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
    recover_stuck_grading(db, user)
    skills = repo.course_skills(db, course_id)
    in_progress = repo.get_in_progress(db, user.user_id, course_id)

    block = _enrollment_block(db, user, course_id)
    unfinished = []
    if block is None and in_progress is None:
        unfinished = repo.list_in_progress(db, user.user_id)
        if len(unfinished) >= settings.REVIEW_MAX_UNFINISHED:
            block = "too_many_unfinished"
    if block is None and in_progress is None and not _has_question_bank(db, [s for s, _ in skills]):
        block = "no_question_bank"

    return {
        "course_id": course_id,
        "course_title": title,
        "skills": [{"skill_id": s, "skill": name} for s, name in skills],
        "structure": _structure(),
        "pass_score": settings.REVIEW_PASS_SCORE,
        "can_start": block is None,
        "blocked": {"code": block, "message": block_message(block)} if block else None,
        "in_progress_attempt_id": in_progress.attempt_id if in_progress else None,
        # Đủ số bài dở → kèm danh sách để người học Tiếp tục / Bỏ bớt ngay trên màn Bắt đầu
        "unfinished_attempts": _unfinished_view(db, unfinished) if block == "too_many_unfinished" else [],
        "attempts": [_summary(a) for a in repo.list_attempts(db, user.user_id, course_id)],
    }


# ─────────────── Ôn tập trên đồ thị lộ trình (20/11) ───────────────

MAX_SKILLS_PER_REQUEST = 100  # một đồ thị lộ trình có vài chục node


def skill_reviews(db: Session, user: Users, skill_ids: list[int]) -> dict:
    """Mỗi kỹ năng → các khóa người học ĐANG HỌC / ĐÃ HOÀN THÀNH có dạy kỹ năng đó VÀ ôn tập được (đủ đề, hoặc
    đang có bài dở / đã từng làm), kèm lần chấm gần nhất và bài đang làm dở. Dùng cho huy hiệu ôn tập trên node
    (proposals/review-on-graph). Khóa chưa tham gia không hiện — ôn tập theo khóa cần tham gia trước.
    Thứ tự khóa: đang làm dở → chưa ôn → đã ôn (cũ nhất trước, nên ôn lại trước)."""
    wanted = list(dict.fromkeys(skill_ids))[:MAX_SKILLS_PER_REQUEST]
    if not wanted:
        return {"items": []}
    recover_stuck_grading(db, user)
    courses = [c for c in course_gateway.enrolled_courses(db, user) if set(c["skill_ids"]) & set(wanted)]
    rows = []
    for c in courses:
        attempts = repo.list_attempts(db, user.user_id, c["course_id"])  # mới nhất trước
        in_progress = next((a for a in attempts if a.status == "in_progress"), None)
        last = next((a for a in attempts if a.status in ("graded", "grading")), None)
        if in_progress is None and last is None and not _has_question_bank(db, c["skill_ids"]):
            continue  # chưa có đề, chưa từng làm → không có gì để ôn
        rows.append(
            {
                "skill_ids": c["skill_ids"],
                "course": {
                    "course_id": c["course_id"],
                    "course_title": c["title"],
                    "enrollment": c["status"],
                    "in_progress_attempt_id": in_progress.attempt_id if in_progress else None,
                    "last_attempt": _summary(last) if last else None,
                },
            }
        )

    def order(course: dict):
        last = course["last_attempt"]
        if course["in_progress_attempt_id"]:
            return (0, "")
        if last is None:
            return (1, course["course_title"])
        return (2, str(last["submitted_at"] or last["started_at"]))

    due = review_due_service.due_info(db, user.user_id, wanted)  # 21/11 (Q12): "Đến hạn ôn" theo kỹ năng
    from app.services import skill_review_service  # import vòng: skill_review_service dùng review_service

    items = []
    for skill_id in wanted:
        found = sorted((r["course"] for r in rows if skill_id in r["skill_ids"]), key=order)
        items.append(
            {
                "skill_id": skill_id,
                "courses": found,
                "due": due.get(skill_id),
                "skill": skill_review_service.direct_review(db, user, skill_id),  # G2d: ôn thẳng theo kỹ năng
            }
        )
    return {"items": items}


# ─────────────── Sinh đề ───────────────


def recent_avoid(
    db: Session, user_id: int, course_id: int | None = None, *, skill_id: int | None = None
) -> tuple[list[ReviewQuestion], dict[int, int]]:
    """G3e P2 (D29): (mọi phiên bản cùng họ với câu của REVIEW_AVOID_LAST_ATTEMPTS lượt nộp gần nhất, {question_id: mức
    phạt}). 7.5a: tránh cả phiên bản mới của câu đã làm (v1 → v2 chỉ khác vài chữ)."""
    recent = repo.recent_submitted_question_ids(db, user_id, course_id, skill_id=skill_id,
                                                attempts=max(1, settings.REVIEW_AVOID_LAST_ATTEMPTS))  # fmt: skip
    family = repo.family_questions(db, list(recent))
    fam_of = repo.family_ids(db, list(recent) + [q.question_id for q in family])
    fam_penalty: dict[int, int] = {}
    for qid, p in recent.items():
        fam_penalty[fam_of[qid]] = max(fam_penalty.get(fam_of[qid], 0), p)
    return family, {q.question_id: fam_penalty[fam_of[q.question_id]] for q in family}


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


def _generate_with_fallback(ai: ReviewAI, request: GenerationRequest, rng: random.Random) -> tuple[list[dict], dict]:
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

    questions = pick_from_bank(request.candidates, request.need, rng, avoid_question_ids=request.avoid_question_ids)
    if generated_errors(questions, request.need):
        raise exam_builder.NotEnoughQuestionsError(f"Ngân hàng kỹ năng {request.skill_id} không đủ câu")
    return questions, {"retries": len(errors), "fallback": True, "errors": errors}


def _save_pending(db: Session, skill_id: int, questions: list[dict]) -> int:
    """QT6-A (7.5c, 16/11): câu AI soạn MỚI chỉ vào ngân hàng ở trạng thái CHỜ DUYỆT (tắt) — admin duyệt mới được
    ra đề. Đi qua review_bank_service.create_question (cùng kiểm tra + phiên bản như admin thêm câu).
    Câu nào lỗi kiểm tra → bỏ qua, ghi log; KHÔNG làm hỏng lượt làm bài của học viên. Trả số câu đã lưu."""
    saved = 0
    for q in questions:
        data = {k: q.get(k) for k in ("chunk_id", "type", "level", "content", "options", "correct_index", "rubric",
                                      "explanation")}  # fmt: skip
        try:
            with db.begin_nested():  # lỗi một câu chỉ hủy câu đó, không hủy cả lượt làm bài
                review_bank_service.create_question(
                    db, {**data, "skill_id": skill_id}, source="ai", review_status="pending"
                )
            saved += 1
        except review_bank_service.BankError as err:
            logger.warning("Ôn tập: bỏ câu AI soạn không hợp lệ (kỹ năng %s): %s", skill_id, err)
    return saved


def _new_trace(ai: ReviewAI, avoid: set[int]) -> dict:
    return {
        "ai_mode": settings.AI_MODE,
        "ai": ai.name,
        "embedding_model": settings.REVIEW_EMBEDDING_MODEL,
        "system_prompt": GENERATE_SYSTEM_PROMPT,
        "avoided_question_ids": sorted(avoid),
        "skills": [],
    }


def pick_questions(
    db: Session,
    *,
    title: str,
    names: dict[int, str],
    plan: exam_builder.Plan,
    ai: ReviewAI,
    rng: random.Random,
    embedder: review_rag_service.Embedder | None,
    avoid: dict[int, int] | set[int],  # G3e: {question_id: mức phạt}
    trace: dict,
    include_auto: bool = False,
) -> list[dict]:
    """Lấy câu cho TỪNG kỹ năng của plan (RAG → AI → validator → ngân hàng dự phòng), ghi vết vào trace.
    Dùng chung cho ôn theo khóa và theo kỹ năng (G2c). Không đủ câu → NotEnoughQuestionsError."""
    picked: list[dict] = []
    for skill_id, need in plan.items():
        chunks = review_rag_service.retrieve_chunks(db, skill_id, names[skill_id], embedder=embedder)
        prompt = build_generation_prompt(course_title=title, skill_name=names[skill_id], chunks=chunks, need=need)
        request = GenerationRequest(
            course_title=title,
            skill_id=skill_id,
            skill_name=names[skill_id],
            need=need,
            chunks=chunks,
            candidates=[_question_dict(q) for q in repo.bank_questions(db, skill_id, include_auto=include_auto)],
            avoid_question_ids=avoid,
            system_prompt=GENERATE_SYSTEM_PROMPT,
            prompt=prompt,
            pending_count=repo.pending_count(db, skill_id),
        )
        questions, info = _generate_with_fallback(ai, request, rng)
        new = [q for q in questions if not q.get("question_id")]
        if new:
            # QT6-A: câu AI soạn mới → Chờ duyệt; đề của kỹ năng này bốc câu ĐÃ DUYỆT trong ngân hàng
            info["ai_new_pending"] = _save_pending(db, skill_id, new)
            questions = pick_from_bank(
                request.candidates,
                need,
                rng,
                prefer_chunk_ids={c.chunk_id for c in chunks},
                avoid_question_ids=avoid,
            )
            if generated_errors(questions, need):
                raise exam_builder.NotEnoughQuestionsError(f"Ngân hàng kỹ năng {skill_id} không đủ câu")
            info["fallback"] = True
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
    return picked


def save_new_attempt(
    db: Session,
    attempt: ReviewAttempt,
    picked: list[dict],
    rng: random.Random,
    find_existing: Callable[[], ReviewAttempt | None],
) -> dict:
    """Xếp đề, lưu lượt mới. Bấm "Bắt đầu" 2 lần cùng lúc: unique index chỉ cho 1 lượt đang làm → trả lại lượt kia."""
    for item in exam_builder.order_exam(picked, rng):
        attempt.answers.append(
            ReviewAnswer(
                position=item["position"],
                question_id=item["question_id"],  # 7.5c: mọi câu trong đề đều là câu đã duyệt có sẵn trong ngân hàng
                option_order=item.get("option_order"),
                max_points=item["max_points"],
            )
        )
    db.add(attempt)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = find_existing()
        if existing is None:
            raise
        return attempt_view(db, existing.attempt_id, resumed=True)
    return attempt_view(db, attempt.attempt_id, resumed=False)


def start_attempt(
    db: Session,
    user: Users,
    course_id: int,
    *,
    rng: random.Random | None = None,
    ai: ReviewAI | None = None,
    embedder: review_rag_service.Embedder | None = None,
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
    if repo.count_in_progress(db, user.user_id) >= settings.REVIEW_MAX_UNFINISHED:
        raise ReviewBlockedError("too_many_unfinished")

    rng = rng or random.Random()
    ai = ai or get_review_ai()
    skills = repo.course_skills(db, course_id)
    names = dict(skills)
    skill_ids = list(names)
    previous = repo.last_submitted_questions(db, user.user_id, course_id)
    # 7.5a (16/11): tránh MỌI phiên bản cùng họ với câu lượt trước — admin sửa câu v1 thành v2 thì lượt sau
    # cũng không ra v2 (chỉ khác vài chữ). fresh trừ phiên bản ĐANG BẬT của họ (v1 đã tắt, v2 đang bật).
    # G3e P2 (D29): tránh câu của 3 lượt nộp gần nhất (không chỉ 1); phải lặp thì lặp câu cũ nhất trước.
    family, avoid = recent_avoid(db, user.user_id, course_id)
    available = repo.bank_counts(db, skill_ids)
    fresh = dict(available)
    for q in family:
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

    trace = _new_trace(ai, avoid)
    try:
        picked = pick_questions(db, title=title, names=names, plan=plan, ai=ai, rng=rng, embedder=embedder,
                                avoid=avoid, trace=trace)  # fmt: skip
    except exam_builder.NotEnoughQuestionsError:
        raise ReviewBlockedError("no_question_bank") from None
    attempt = ReviewAttempt(user_id=user.user_id, course_id=course_id, trace=trace)
    return save_new_attempt(db, attempt, picked, rng, lambda: repo.get_in_progress(db, user.user_id, course_id))


# ─────────────── Xem đề, lưu câu trả lời ───────────────


def _owned_attempt(db: Session, user: Users, attempt_id: int, *, lock: bool = False) -> ReviewAttempt:
    """lock=True (lưu / nộp): khóa dòng tới khi commit — bấm Nộp 2 lần cùng lúc, request sau chờ rồi nhận 409."""
    attempt = repo.get_attempt(db, attempt_id, for_update=lock)
    if attempt is None or attempt.user_id != user.user_id:
        raise AttemptNotFoundError
    return attempt


def _unfinished_view(db: Session, attempts: list[ReviewAttempt]) -> list[dict]:
    names = target_names(db, attempts)
    return [
        {
            "attempt_id": a.attempt_id,
            **target_fields(db, a, names),
            "answered": sum(1 for x in a.answers if _is_answered(x)),
            "total": len(a.answers),
            "started_at": a.started_at,
        }
        for a in attempts
    ]


def abandon_attempt(db: Session, user: Users, attempt_id: int) -> None:
    """Bỏ bài làm dở (19/11): XÓA hẳn lượt + câu trả lời — chưa chấm nên không có điểm, không vào lịch sử,
    không gọi AI. Chỉ bỏ được lượt đang làm của chính mình; lượt đã nộp → AttemptLockedError (409)."""
    attempt = _owned_attempt(db, user, attempt_id, lock=True)
    if attempt.status != "in_progress":
        raise AttemptLockedError
    db.delete(attempt)
    db.commit()


def _is_answered(a: ReviewAnswer) -> bool:
    return a.selected_index is not None or bool(a.text_answer and a.text_answer.strip())


def target_names(db: Session, attempts: list[ReviewAttempt]) -> tuple[dict[int, str], dict[int, str]]:
    """(tên khóa theo course_id, tên kỹ năng theo skill_id) cho nhiều lượt — 2 truy vấn."""
    courses = repo.course_titles(db, [a.course_id for a in attempts if a.course_id is not None])
    skills = repo.skill_names(db, [a.skill_id for a in attempts if a.skill_id is not None])
    return courses, skills


def target_fields(db: Session, attempt: ReviewAttempt, names=None) -> dict:
    """Lượt thuộc khóa nào HOẶC kỹ năng nào (G2c/G2d, 22/11): lượt theo kỹ năng có course_id None, course_title ""."""
    courses, skills = names or target_names(db, [attempt])
    return {
        "course_id": attempt.course_id,
        "course_title": courses.get(attempt.course_id, "") if attempt.course_id is not None else "",
        "skill_id": attempt.skill_id,
        "skill_name": skills.get(attempt.skill_id) if attempt.skill_id is not None else None,
        "path_id": attempt.path_id,
    }


def email_target(view: dict) -> tuple[str, str]:
    """(tên, "khóa học" | "kỹ năng") cho email kết quả, từ kết quả / mục báo lỗi có course_id + course_title + skill_name."""
    if view.get("course_id") is None:
        return view.get("skill_name") or "", "kỹ năng"
    return view.get("course_title") or "", "khóa học"


def target_title(db: Session, attempt: ReviewAttempt) -> str:
    """Tên hiển thị: tên khóa, hoặc tên kỹ năng với lượt theo kỹ năng (thông báo, email)."""
    fields = target_fields(db, attempt)
    return fields["course_title"] if attempt.course_id is not None else (fields["skill_name"] or "")


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
        **target_fields(db, attempt),
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
    attempt = _owned_attempt(db, user, attempt_id, lock=True)
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


# ─────────────── Nộp bài, chấm điểm (GĐ3) ───────────────


def submit_attempt(
    db: Session,
    user: Users,
    attempt_id: int,
    *,
    ai: ReviewAI | None = None,
    schedule: Callable[[Callable[[], None]], None] | None = None,
) -> dict:
    """Nộp bài. Chấm và lưu kết quả trong MỘT lần commit (B1, FR-43):
        điểm từng câu + tổng → (đạt LẦN ĐẦU, đang học) khóa Hoàn thành + mọi kỹ năng của khóa "Đã biết".
    Lỗi giữa chừng → rollback toàn bộ, bài vẫn ở trạng thái đang làm (nộp lại được).

    T1 (12/11/2026): các câu tự luận gửi AI SONG SONG, chờ tối đa REVIEW_GRADING_TIMEOUT giây.
      - Xong kịp → trả kết quả "graded" như cũ (router gửi email).
      - Chưa xong → lưu bài ở trạng thái "grading" (khóa câu trả lời, chưa có điểm) rồi trả về ngay;
        `schedule(job)` (router truyền BackgroundTasks.add_task) chạy `finish_grading` sau khi phản hồi:
        chờ AI tới REVIEW_GRADING_MAX_WAIT giây kể từ lúc nộp, câu chưa xong → chấm từ khóa,
        rồi lưu điểm + chuông + email. Không truyền schedule (test gọi thẳng) → chấm nốt ngay tại chỗ.
    """
    attempt = _owned_attempt(db, user, attempt_id, lock=True)
    if attempt.status != "in_progress":
        raise AttemptLockedError

    ai = ai or get_review_ai()
    started = time.monotonic()
    futures = review_grader.start_ai_grading(ai, attempt.answers)
    ai_results, pending = review_grader.collect(futures, settings.REVIEW_GRADING_TIMEOUT)
    if not pending:
        _finalize(db, user, attempt, ai, ai_results)
        return result_view(db, attempt_id)

    # Quá thời gian chờ → "Đang chấm": bài khóa lại (không sửa / nộp lại được), chưa báo đạt / chưa đạt.
    try:
        attempt.status = "grading"
        attempt.submitted_at = datetime.now(UTC)
        db.commit()
    except Exception:
        db.rollback()
        raise
    deadline = started + settings.REVIEW_GRADING_MAX_WAIT

    def job() -> None:
        finish_grading(attempt_id, ai, futures, deadline)

    if schedule is None:
        finish_grading(attempt_id, ai, futures, deadline, db=db)
    else:
        schedule(job)
    return result_view(db, attempt_id)


def _finalize(
    db: Session,
    user: Users,
    attempt: ReviewAttempt,
    ai: ReviewAI,
    ai_results: dict | None,
) -> None:
    """Ghi điểm + đạt / chưa đạt + (đạt lần đầu) Hoàn thành khóa + chuông — một lần commit. Lỗi → rollback."""
    try:
        total, grading = review_grader.grade_answers(attempt.answers, ai, ai_results)
        attempt.score = round(total, 2)
        # So trên tổng chưa làm tròn 2 chữ số (Q7); round 6 chỉ để bỏ sai số cộng số thực (1.4000000000000001)
        attempt.passed = round(total, 6) >= settings.REVIEW_PASS_SCORE
        attempt.status = "graded"
        attempt.submitted_at = attempt.submitted_at or datetime.now(UTC)  # "grading": giữ giờ nộp thật

        complete_if_first_pass(db, user.user_id, attempt)
        # JSON: gán dict MỚI để SQLAlchemy biết cột đã đổi
        attempt.trace = {**(attempt.trace or {}), "grading": grading}
        _notify_result(db, user, attempt)  # chuông (11/11) — cùng commit, nộp lỗi thì không có thông báo
        db.commit()
    except Exception:
        db.rollback()
        raise


def complete_if_first_pass(db: Session, user_id: int, attempt: ReviewAttempt) -> bool:
    """Đạt + khóa đang 'ongoing' → khóa Hoàn thành + mọi kỹ năng của khóa "Đã biết" (B1). Không commit.
    Hoàn thành = đạt + khóa đang 'ongoing' (chốt với Khôi, điểm 3 — 12/11). Khóa đã Hoàn thành không bỏ được và
    Khôi giữ nguyên 'completed' khi tham gia lại → không cần kiểm "lần đạt đầu"; bỏ khóa rồi tham gia lại (T9)
    vẫn Hoàn thành được. Dùng chung cho nộp bài và admin chấm lại (review_flag_service, 17/11).
    Lượt theo KỸ NĂNG (G2d, 22/11): đạt → CHỈ kỹ năng đó "Đã biết", không đụng khóa nào; is_first_pass luôn False
    (cột này = "lượt làm khóa Hoàn thành")."""
    if attempt.course_id is None:
        attempt.is_first_pass = False
        if attempt.passed and attempt.skill_id is not None:
            user_skill_service.mark_known(db, user_id, [attempt.skill_id], source="review")
        return False
    enrollment = course_gateway.get_enrollment_status(db, user_id, attempt.course_id)
    first_pass = bool(attempt.passed) and enrollment == course_gateway.IN_PROGRESS
    attempt.is_first_pass = first_pass
    if first_pass:  # B1 + 6b: kể cả kỹ năng người dùng đã tự gỡ
        course_gateway.mark_course_completed(db, user_id, attempt.course_id)
        skill_ids = [s for s, _ in repo.course_skills(db, attempt.course_id)]
        user_skill_service.mark_known(db, user_id, skill_ids, source="review")
    return first_pass


def finish_grading(
    attempt_id: int,
    ai: ReviewAI,
    futures: dict,
    deadline: float,
    *,
    db: Session | None = None,
) -> None:
    """Chấm nốt lượt "grading" ở NỀN (T1): chờ AI tới `deadline` (time.monotonic) → câu chưa xong chấm từ khóa
    → lưu điểm + chuông → gửi email. Chạy sau khi đã trả phản hồi nên mở phiên DB RIÊNG (db=None).
    Lỗi chỉ ghi log — bài ở lại "grading" và được recover_stuck_grading cứu khi người dùng mở trang sau."""
    ai_results, _ = review_grader.collect(futures, deadline - time.monotonic())
    own_session = db is None
    session = database.SessionLocal() if own_session else db
    try:
        attempt = repo.get_attempt(session, attempt_id, for_update=True)
        if attempt is None or attempt.status != "grading":
            return  # đã được chấm ở chỗ khác (vd recover) — không chấm 2 lần
        user = session.get(Users, attempt.user_id)
        _finalize(session, user, attempt, ai, ai_results)
        if own_session:  # chạy nền từ router → tự gửi email (router đã trả phản hồi "grading" rồi)
            result = result_view(session, attempt_id)
            send_review_result_email(
                user.email,
                user.full_name,
                target_title(session, attempt),
                result["score"],
                result["passed"],
                result["completed_course"],
                attempt_id,
                target="khóa học" if attempt.course_id is not None else "kỹ năng",
            )
    except Exception:
        logger.exception("Ôn tập: chấm nền lượt %s lỗi — chờ recover_stuck_grading", attempt_id)
    finally:
        if own_session:
            session.close()


def recover_stuck_grading(db: Session, user: Users) -> None:
    """Lượt "grading" quá REVIEW_GRADING_MAX_WAIT + 60 giây vẫn chưa có điểm = luồng chấm nền đã mất
    (server khởi động lại giữa chừng). Chấm lại bằng từ khóa để người học không kẹt mãi ở "Đang chấm".
    Gọi khi người dùng mở trang ôn tập / lịch sử / kết quả. Có chuông; không gửi email (đang trong request)."""
    cutoff = datetime.now(UTC) - timedelta(seconds=settings.REVIEW_GRADING_MAX_WAIT + 60)
    for attempt_id in repo.stuck_grading_ids(db, user.user_id, cutoff):
        attempt = repo.get_attempt(db, attempt_id, for_update=True)
        if attempt is None or attempt.status != "grading":
            continue
        logger.warning("Ôn tập: lượt %s kẹt ở 'grading' — chấm lại bằng từ khóa", attempt_id)
        try:
            _finalize(db, user, attempt, get_review_ai(), {})
        except Exception:
            logger.exception("Ôn tập: cứu lượt %s thất bại", attempt_id)


def _notify_result(db: Session, user: Users, attempt: ReviewAttempt, *, renew: bool = False) -> None:
    """Thông báo trên chuông: kết quả ôn tập; đạt lần đầu thì thêm \"khóa đã hoàn thành\".
    renew=True (admin chấm lại, 17/11): cập nhật thông báo kết quả cũ của lượt này + đặt lại chưa đọc."""
    title = target_title(db, attempt)
    verdict = "Đạt" if attempt.passed else "Chưa đạt"
    send = notification_service.renotify if renew else notification_service.notify
    send(
        db,
        user.user_id,
        "review_graded",
        f"Kết quả ôn tập: {float(attempt.score):g}/10 — {verdict}",
        body=title if attempt.course_id is not None else f"Kỹ năng: {title}",
        link=f"/review/{attempt.attempt_id}/result",
        source_id=attempt.attempt_id,
    )
    if attempt.is_first_pass:
        notification_service.notify(
            db,
            user.user_id,
            "course_completed",
            f"Chúc mừng! Bạn đã hoàn thành khóa {title}",
            body="Các kỹ năng của khóa đã được ghi nhận là Đã biết.",
            link="/me/skills",
            source_id=attempt.course_id,
        )


def result_view(db: Session, attempt_id: int) -> dict:
    """Kết quả chi tiết của lượt ĐÃ NỘP — lúc này mới có đáp án đúng, barem, giải thích (FR-28)."""
    db.expire_all()
    attempt = repo.get_attempt(db, attempt_id)
    if attempt.status == "grading":
        # Đang chấm (T1): chưa có điểm → chưa trả đáp án / từng câu; frontend hiện "Đang chấm" và hỏi lại sau.
        return {
            "attempt_id": attempt.attempt_id,
            **target_fields(db, attempt),
            "status": attempt.status,
            "score": None,
            "passed": None,
            "pass_score": settings.REVIEW_PASS_SCORE,
            "mcq_score": None,
            "essay_score": None,
            "completed_course": False,
            "started_at": attempt.started_at,
            "submitted_at": attempt.submitted_at,
            "questions": [],
        }
    names = repo.skill_names(db, [a.question.skill_id for a in attempt.answers])
    # B11: thông tin chấm tự luận lưu trong trace (B6–B8). Lượt chấm trước B6 không có "essays" → giá trị mặc định.
    grading = (attempt.trace or {}).get("grading") or {}
    fallback = {f["position"] for f in grading.get("keyword_fallback", [])}
    essays = {e["position"]: e for e in grading.get("essays", [])}
    keyword_only = grading.get("ai") in ("mock", "unavailable")  # AI_MODE=mock thực chất là chấm từ khóa
    # G3e P3 (D29): lượt CHƯA ĐẠT ẩn đáp án theo REVIEW_REVEAL_ON_FAIL (mcq_only: ẩn bài mẫu tự luận; none: ẩn cả đáp án
    # trắc nghiệm). Ý barem + lý do chấm vẫn hiện để học viên biết mình thiếu gì. Lượt Đạt luôn hiện đủ.
    reveal = "all" if attempt.passed else settings.REVIEW_REVEAL_ON_FAIL
    questions = []
    mcq_score = essay_score = 0.0
    for a in attempt.answers:
        q = a.question
        points = float(a.points) if a.points is not None else 0.0
        item = {
            "position": a.position,
            "type": q.type,
            "level": q.level,
            "skill_id": q.skill_id,
            "skill": names.get(q.skill_id, ""),
            "content": q.content,
            "max_points": float(a.max_points),
            "points": points,
            "explanation": q.explanation,
            "options": None,
            "selected_index": None,
            "correct_index": None,
            "is_correct": None,
            "text_answer": None,
            "rubric": None,
            "graded_by": None,  # B11 — chỉ câu tự luận có bài làm mới có
            "needs_review": False,
            "reviewed": False,
            "feedback": None,
            "answer_hidden": False,
        }
        if q.type == "mcq":
            mcq_score += points
            item.update(
                options=[q.options[i] for i in a.option_order],
                selected_index=a.selected_index,
                correct_index=review_grader.displayed_correct_index(a),
                is_correct=review_grader.is_mcq_correct(a),
            )
            if reveal == "none":
                item.update(correct_index=None, explanation=None, answer_hidden=True)
        else:
            essay_score += points
            if reveal in ("mcq_only", "none") and q.explanation:
                item.update(explanation=None, answer_hidden=True)
            results = a.rubric_result or [{} for _ in q.rubric]
            item.update(
                text_answer=a.text_answer,
                rubric=[
                    {
                        "text": r["text"],
                        "max_points": float(r["max_points"]),
                        "result": res.get("result", "none"),
                        "points": float(res.get("points", 0.0)),
                        "evidence": res.get("evidence"),
                        "reason": res.get("reason"),
                    }
                    for r, res in zip(q.rubric, results, strict=True)
                ],
            )
            if a.text_answer and a.text_answer.strip() and grading:
                essay = essays.get(a.position, {})
                item.update(
                    graded_by="keyword" if keyword_only or a.position in fallback else "ai",
                    needs_review=bool(essay.get("needs_review")),
                    reviewed=bool(essay.get("review")),
                    feedback=essay.get("feedback"),
                )
        questions.append(item)
    return {
        "attempt_id": attempt.attempt_id,
        **target_fields(db, attempt),
        "status": attempt.status,
        "score": float(attempt.score) if attempt.score is not None else None,
        "passed": attempt.passed,
        "pass_score": settings.REVIEW_PASS_SCORE,
        "mcq_score": round(mcq_score, 2),
        "essay_score": round(essay_score, 2),
        "answers_hidden": any(item["answer_hidden"] for item in questions),
        "completed_course": attempt.is_first_pass,
        "skill_known": bool(attempt.passed) and attempt.skill_id is not None,
        "started_at": attempt.started_at,
        "submitted_at": attempt.submitted_at,
        "questions": questions,
    }


# ─────────────── Lịch sử (GĐ3) ───────────────


def history_list(
    db: Session,
    user: Users,
    *,
    course_id: int | None = None,
    passed: bool | None = None,
    page: int = 1,
    size: int = 10,
) -> dict:
    recover_stuck_grading(db, user)
    rows, total = repo.list_history(
        db, user.user_id, course_id=course_id, passed=passed, offset=(page - 1) * size, limit=size
    )
    names = target_names(db, rows)
    return {
        "items": [{**_summary(a), **target_fields(db, a, names), "completed_course": a.is_first_pass} for a in rows],
        "total": total,
        "page": page,
        "size": size,
    }


def history_detail(db: Session, user: Users, attempt_id: int) -> dict:
    """Chỉ lượt ĐÃ NỘP của CHÍNH người dùng; lượt đang làm → 404 (không lộ đáp án khi chưa nộp)."""
    attempt = _owned_attempt(db, user, attempt_id)
    if attempt.status == "in_progress":
        raise AttemptNotFoundError
    if attempt.status == "grading":
        recover_stuck_grading(db, user)
    return result_view(db, attempt_id)


def attempt_trace(db: Session, attempt_id: int) -> dict:
    """Vết RAG + prompt + chấm của một lượt (API debug admin — A4)."""
    attempt = repo.get_attempt(db, attempt_id)
    if attempt is None:
        raise AttemptNotFoundError
    return {
        "attempt_id": attempt.attempt_id,
        "user_id": attempt.user_id,
        "course_id": attempt.course_id,
        "skill_id": attempt.skill_id,
        "status": attempt.status,
        "score": float(attempt.score) if attempt.score is not None else None,
        "started_at": attempt.started_at,
        "submitted_at": attempt.submitted_at,
        "trace": attempt.trace or {},
    }
