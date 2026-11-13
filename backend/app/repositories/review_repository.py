"""Repository ôn tập: CHỈ truy vấn DB, không chứa nghiệp vụ (module 09 · Tuấn · GĐ2, 09/11/2026).

Bảng courses, skills, course_skill là của Hòa/Khôi — ở đây chỉ ĐỌC.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.course import Courses
from app.models.course_skill import CourseSkill
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.review_attempt import ReviewAnswer, ReviewAttempt
from app.models.review_question import ReviewQuestion
from app.models.review_question_meta import ReviewQuestionMeta
from app.models.skill import Skills

# ─────────────── Khóa học, kỹ năng (chỉ đọc) ───────────────


def get_course_title(db: Session, course_id: int) -> str | None:
    return db.scalar(select(Courses.title).where(Courses.course_id == course_id))


def course_skills(db: Session, course_id: int) -> list[tuple[int, str]]:
    """[(skill_id, tên)] các kỹ năng ĐANG BẬT của khóa, theo skill_id."""
    rows = db.execute(
        select(Skills.skill_id, Skills.skill)
        .join(CourseSkill, CourseSkill.skill_id == Skills.skill_id)
        .where(CourseSkill.course_id == course_id, Skills.is_active.is_(True))
        .order_by(Skills.skill_id)
    )
    return [(r.skill_id, r.skill) for r in rows]


# ─────────────── Ngân hàng câu hỏi, đoạn tri thức ───────────────


def bank_counts(db: Session, skill_ids: list[int]) -> dict[tuple[int, str], int]:
    """Số câu ĐANG BẬT theo (skill_id, level)."""
    if not skill_ids:
        return {}
    rows = db.execute(
        select(ReviewQuestion.skill_id, ReviewQuestion.level, func.count())
        .where(ReviewQuestion.skill_id.in_(skill_ids), ReviewQuestion.is_active.is_(True))
        .group_by(ReviewQuestion.skill_id, ReviewQuestion.level)
    )
    return {(skill_id, level): n for skill_id, level, n in rows}


def bank_questions(db: Session, skill_id: int) -> list[ReviewQuestion]:
    return list(
        db.scalars(
            select(ReviewQuestion)
            .where(ReviewQuestion.skill_id == skill_id, ReviewQuestion.is_active.is_(True))
            .order_by(ReviewQuestion.question_id)
        )
    )


def chunks_for_skill(db: Session, skill_id: int) -> list[KnowledgeChunk]:
    return list(
        db.scalars(
            select(KnowledgeChunk)
            .where(KnowledgeChunk.skill_id == skill_id)
            .order_by(KnowledgeChunk.chunk_id)
        )
    )


# ─────────────── Lượt làm bài ───────────────


def get_attempt(db: Session, attempt_id: int, *, for_update: bool = False) -> ReviewAttempt | None:
    """Kèm sẵn câu trả lời + câu hỏi (tránh truy vấn lặp khi hiển thị đề).

    for_update=True: khóa dòng lượt làm bài tới khi commit/rollback (SELECT … FOR UPDATE) — dùng khi
    LƯU / NỘP để 2 request cùng lúc phải xếp hàng: request sau đọc lại trạng thái mới nhất → 409.
    """
    stmt = (
        select(ReviewAttempt)
        .where(ReviewAttempt.attempt_id == attempt_id)
        .options(selectinload(ReviewAttempt.answers).selectinload(ReviewAnswer.question))
    )
    if for_update:
        # populate_existing: nếu object đã nằm trong session thì vẫn ghi đè bằng dữ liệu vừa khóa
        stmt = stmt.with_for_update(of=ReviewAttempt).execution_options(populate_existing=True)
    return db.scalar(stmt)


def stuck_grading_ids(db: Session, user_id: int, submitted_before) -> list[int]:
    """Lượt 'grading' nộp TRƯỚC mốc thời gian — luồng chấm nền đã mất (server khởi động lại / lỗi) (T1)."""
    return list(
        db.scalars(
            select(ReviewAttempt.attempt_id).where(
                ReviewAttempt.user_id == user_id,
                ReviewAttempt.status == "grading",
                ReviewAttempt.submitted_at < submitted_before,
            )
        )
    )


def get_in_progress(db: Session, user_id: int, course_id: int) -> ReviewAttempt | None:
    return db.scalar(
        select(ReviewAttempt).where(
            ReviewAttempt.user_id == user_id,
            ReviewAttempt.course_id == course_id,
            ReviewAttempt.status == "in_progress",
        )
    )


def list_attempts(db: Session, user_id: int, course_id: int) -> list[ReviewAttempt]:
    """Mới nhất trước."""
    return list(
        db.scalars(
            select(ReviewAttempt)
            .where(ReviewAttempt.user_id == user_id, ReviewAttempt.course_id == course_id)
            .order_by(ReviewAttempt.started_at.desc(), ReviewAttempt.attempt_id.desc())
        )
    )


def last_submitted_questions(db: Session, user_id: int, course_id: int) -> list[ReviewQuestion]:
    """Các câu của lượt ĐÃ NỘP gần nhất — để lượt mới tránh lặp (A1)."""
    last_id = db.scalar(
        select(ReviewAttempt.attempt_id)
        .where(
            ReviewAttempt.user_id == user_id,
            ReviewAttempt.course_id == course_id,
            ReviewAttempt.status != "in_progress",
        )
        .order_by(ReviewAttempt.started_at.desc(), ReviewAttempt.attempt_id.desc())
        .limit(1)
    )
    if last_id is None:
        return []
    return list(
        db.scalars(
            select(ReviewQuestion)
            .join(ReviewAnswer, ReviewAnswer.question_id == ReviewQuestion.question_id)
            .where(ReviewAnswer.attempt_id == last_id)
        )
    )


def skill_names(db: Session, skill_ids) -> dict[int, str]:
    ids = list(set(skill_ids))
    if not ids:
        return {}
    return dict(db.execute(select(Skills.skill_id, Skills.skill).where(Skills.skill_id.in_(ids))).all())


def list_history(
    db: Session,
    user_id: int,
    *,
    course_id: int | None = None,
    passed: bool | None = None,
    offset: int = 0,
    limit: int = 10,
) -> tuple[list[tuple[ReviewAttempt, str]], int]:
    """Các lượt ĐÃ NỘP của người dùng (mới nhất trước) kèm tên khóa + tổng số dòng khớp bộ lọc."""
    conditions = [ReviewAttempt.user_id == user_id, ReviewAttempt.status != "in_progress"]
    if course_id is not None:
        conditions.append(ReviewAttempt.course_id == course_id)
    if passed is not None:
        conditions.append(ReviewAttempt.passed.is_(passed))
    total = db.scalar(select(func.count()).select_from(ReviewAttempt).where(*conditions))
    rows = db.execute(
        select(ReviewAttempt, Courses.title)
        .join(Courses, Courses.course_id == ReviewAttempt.course_id)
        .where(*conditions)
        .order_by(ReviewAttempt.submitted_at.desc(), ReviewAttempt.attempt_id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return [(attempt, title) for attempt, title in rows], total


# ─────────────── Quản trị ngân hàng câu hỏi (GĐ7 · 13/11) ───────────────


def get_question(db: Session, question_id: int, *, for_update: bool = False) -> ReviewQuestion | None:
    stmt = select(ReviewQuestion).where(ReviewQuestion.question_id == question_id)
    if for_update:
        stmt = stmt.with_for_update().execution_options(populate_existing=True)
    return db.scalar(stmt)


def get_question_by_code(db: Session, code: str) -> ReviewQuestion | None:
    return db.scalar(select(ReviewQuestion).where(ReviewQuestion.code == code))


def used_count(db: Session, question_id: int) -> int:
    """Số bài làm (lượt) đã có câu này — > 0 thì sửa nội dung phải tạo phiên bản mới."""
    return db.scalar(select(func.count()).select_from(ReviewAnswer).where(ReviewAnswer.question_id == question_id))


def get_meta(db: Session, question_id: int) -> ReviewQuestionMeta | None:
    return db.get(ReviewQuestionMeta, question_id)


def family_metas(db: Session, family_id: int) -> list[ReviewQuestionMeta]:
    """Mọi phiên bản của một họ câu hỏi, mới nhất trước."""
    return list(
        db.scalars(
            select(ReviewQuestionMeta)
            .where(ReviewQuestionMeta.family_id == family_id)
            .order_by(ReviewQuestionMeta.version.desc())
        )
    )
