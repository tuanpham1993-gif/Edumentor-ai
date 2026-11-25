"""Repository ôn tập: CHỈ truy vấn DB, không chứa nghiệp vụ (module 09 · Tuấn · GĐ2, 09/11/2026).

Bảng courses, skills, course_skill là của Hòa/Khôi — ở đây chỉ ĐỌC.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.course import Courses
from app.models.course_skill import CourseSkill
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.learning_path import LearningPath, LearningPathNode
from app.models.review_attempt import ReviewAnswer, ReviewAttempt
from app.models.review_question import ReviewQuestion
from app.models.review_question_meta import ReviewQuestionMeta
from app.models.skill import Skills
from app.models.user import Users
from app.models.user_skill import UserSkill

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


def course_skills_many(db: Session, course_ids: list[int]) -> dict[int, list[tuple[int, str]]]:
    """Như course_skills nhưng cho nhiều khóa trong 1 truy vấn (7.4: ~200 khóa dùng chung kỹ năng)."""
    out: dict[int, list[tuple[int, str]]] = {cid: [] for cid in course_ids}
    if not course_ids:
        return out
    rows = db.execute(
        select(CourseSkill.course_id, Skills.skill_id, Skills.skill)
        .join(Skills, Skills.skill_id == CourseSkill.skill_id)
        .where(CourseSkill.course_id.in_(course_ids), Skills.is_active.is_(True))
        .order_by(CourseSkill.course_id, Skills.skill_id)
    )
    for r in rows:
        out[r.course_id].append((r.skill_id, r.skill))
    return out


# ─────────────── Ngân hàng câu hỏi, đoạn tri thức ───────────────


def _usable(stmt, include_auto: bool):
    """Câu ĐƯỢC DÙNG ra đề. Ôn theo KHÓA (mặc định): chỉ câu đã duyệt / chưa có meta (nạp trước 13/11) — KHÔNG lẫn câu
    AI tự duyệt (D2). Ôn theo KỸ NĂNG (include_auto=True, G3d): thêm câu `auto_approved`; câu soạn sẵn ban đêm
    (origin='nightly') chỉ dùng khi mentor đã Đạt (D26)."""
    stmt = stmt.outerjoin(ReviewQuestionMeta, ReviewQuestionMeta.question_id == ReviewQuestion.question_id)
    approved = ReviewQuestionMeta.question_id.is_(None) | (ReviewQuestionMeta.review_status == "approved")
    if not include_auto:
        return stmt.where(approved)
    auto = (ReviewQuestionMeta.review_status == "auto_approved") & (
        ReviewQuestionMeta.origin.is_distinct_from("nightly") | (ReviewQuestionMeta.mentor_status == "passed")
    )
    return stmt.where(approved | auto)


def bank_counts(db: Session, skill_ids: list[int], *, include_auto: bool = False) -> dict[tuple[int, str], int]:
    """Số câu ĐANG BẬT, được dùng ra đề, theo (skill_id, level). include_auto: xem _usable."""
    if not skill_ids:
        return {}
    stmt = select(ReviewQuestion.skill_id, ReviewQuestion.level, func.count()).where(
        ReviewQuestion.skill_id.in_(skill_ids), ReviewQuestion.is_active.is_(True)
    )
    rows = db.execute(_usable(stmt, include_auto).group_by(ReviewQuestion.skill_id, ReviewQuestion.level))
    return {(skill_id, level): n for skill_id, level, n in rows}


def stocked_counts(db: Session, skill_id: int) -> dict[str, int]:
    """G3d-3: số câu ĐANG BẬT theo mức, gồm cả câu soạn sẵn ban đêm chưa được mentor Đạt (đã soạn rồi → không soạn
    thêm). Không tính câu chờ duyệt / bị từ chối (luôn tắt)."""
    stmt = (
        select(ReviewQuestion.level, func.count())
        .outerjoin(ReviewQuestionMeta, ReviewQuestionMeta.question_id == ReviewQuestion.question_id)
        .where(ReviewQuestion.skill_id == skill_id, ReviewQuestion.is_active.is_(True))
        .group_by(ReviewQuestion.level)
    )
    return dict(db.execute(stmt).all())


def bank_questions(db: Session, skill_id: int, *, include_auto: bool = False) -> list[ReviewQuestion]:
    stmt = select(ReviewQuestion).where(ReviewQuestion.skill_id == skill_id, ReviewQuestion.is_active.is_(True))
    return list(db.scalars(_usable(stmt, include_auto).order_by(ReviewQuestion.question_id)))


def pending_count(db: Session, skill_id: int) -> int:
    """Số câu của kỹ năng đang CHỜ DUYỆT (AI soạn — QT6-A, 7.5c). Tính vào ngưỡng "ngân hàng đủ câu" để mỗi lượt
    làm bài không bắt AI soạn thêm một loạt câu chờ duyệt trùng nhau."""
    return db.scalar(
        select(func.count())
        .select_from(ReviewQuestion)
        .join(ReviewQuestionMeta, ReviewQuestionMeta.question_id == ReviewQuestion.question_id)
        .where(ReviewQuestion.skill_id == skill_id, ReviewQuestionMeta.review_status == "pending")
    )


def pending_counts(db: Session, skill_ids: list[int]) -> dict[int, int]:
    """{skill_id: số câu CHỜ DUYỆT} — một truy vấn cho cả khóa (7.4 mức sẵn sàng)."""
    if not skill_ids:
        return {}
    rows = db.execute(
        select(ReviewQuestion.skill_id, func.count())
        .join(ReviewQuestionMeta, ReviewQuestionMeta.question_id == ReviewQuestion.question_id)
        .where(ReviewQuestion.skill_id.in_(skill_ids), ReviewQuestionMeta.review_status == "pending")
        .group_by(ReviewQuestion.skill_id)
    )
    return {skill_id: n for skill_id, n in rows}


def courses_with_questions(db: Session) -> list[tuple[int, str]]:
    """[(course_id, title)] các khóa có ít nhất một kỹ năng ĐANG BẬT đã có câu trong ngân hàng (mọi trạng thái)."""
    has_question = select(ReviewQuestion.question_id).where(ReviewQuestion.skill_id == CourseSkill.skill_id).exists()
    rows = db.execute(
        select(Courses.course_id, Courses.title)
        .join(CourseSkill, CourseSkill.course_id == Courses.course_id)
        .join(Skills, Skills.skill_id == CourseSkill.skill_id)
        .where(Skills.is_active.is_(True), has_question)
        .distinct()
        .order_by(Courses.course_id)
    )
    return [(r.course_id, r.title) for r in rows]


def count_courses(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Courses))


def chunks_for_skill(db: Session, skill_id: int) -> list[KnowledgeChunk]:
    return list(
        db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.skill_id == skill_id).order_by(KnowledgeChunk.chunk_id))
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


def _target(course_id: int | None, skill_id: int | None):
    """Lượt theo khóa (course_id) hoặc theo kỹ năng (skill_id — G2c, 22/11)."""
    if skill_id is not None:
        return ReviewAttempt.skill_id == skill_id
    return ReviewAttempt.course_id == course_id


def get_in_progress(
    db: Session, user_id: int, course_id: int | None = None, *, skill_id: int | None = None
) -> ReviewAttempt | None:
    return db.scalar(
        select(ReviewAttempt).where(
            ReviewAttempt.user_id == user_id,
            _target(course_id, skill_id),
            ReviewAttempt.status == "in_progress",
        )
    )


def list_in_progress(db: Session, user_id: int) -> list[ReviewAttempt]:
    """Mọi lượt đang làm dở của người dùng (mọi khóa), cũ nhất trước — kèm câu trả lời để đếm số câu đã làm."""
    return list(
        db.scalars(
            select(ReviewAttempt)
            .where(ReviewAttempt.user_id == user_id, ReviewAttempt.status == "in_progress")
            .options(selectinload(ReviewAttempt.answers))
            .order_by(ReviewAttempt.started_at, ReviewAttempt.attempt_id)
        )
    )


def count_in_progress(db: Session, user_id: int) -> int:
    return db.scalar(
        select(func.count())
        .select_from(ReviewAttempt)
        .where(ReviewAttempt.user_id == user_id, ReviewAttempt.status == "in_progress")
    )


def list_attempts(
    db: Session, user_id: int, course_id: int | None = None, *, skill_id: int | None = None
) -> list[ReviewAttempt]:
    """Mới nhất trước. Theo khóa, hoặc theo kỹ năng (skill_id — G2d)."""
    return list(
        db.scalars(
            select(ReviewAttempt)
            .where(ReviewAttempt.user_id == user_id, _target(course_id, skill_id))
            .order_by(ReviewAttempt.started_at.desc(), ReviewAttempt.attempt_id.desc())
        )
    )


def family_questions(db: Session, question_ids: list[int]) -> list[ReviewQuestion]:
    """MỌI phiên bản cùng họ với các câu đã cho (7.5a, 16/11). Họ = review_question_meta.family_id; câu chưa có meta
    (nạp trước 13/11) là họ của chính nó. Vd lượt trước làm câu v1, admin sửa thành v2 → trả cả v1 lẫn v2."""
    if not question_ids:
        return []
    family = func.coalesce(ReviewQuestionMeta.family_id, ReviewQuestion.question_id)
    families = (
        select(family)
        .select_from(ReviewQuestion)
        .outerjoin(ReviewQuestionMeta, ReviewQuestionMeta.question_id == ReviewQuestion.question_id)
        .where(ReviewQuestion.question_id.in_(question_ids))
    )
    return list(
        db.scalars(
            select(ReviewQuestion)
            .outerjoin(ReviewQuestionMeta, ReviewQuestionMeta.question_id == ReviewQuestion.question_id)
            .where(family.in_(families))
            .order_by(ReviewQuestion.question_id)
        )
    )


def recent_submitted_question_ids(
    db: Session, user_id: int, course_id: int | None = None, *, skill_id: int | None = None, attempts: int = 3
) -> dict[int, int]:
    """G3e P2 (D29): {question_id: mức phạt} của N lượt ĐÃ NỘP gần nhất (cùng khóa / kỹ năng). Lượt gần nhất phạt N,
    lượt cũ nhất phạt 1 → khi phải lặp câu thì lặp câu CŨ NHẤT trước. Câu có ở nhiều lượt lấy mức phạt cao nhất."""
    attempt_ids = list(
        db.scalars(
            select(ReviewAttempt.attempt_id)
            .where(ReviewAttempt.user_id == user_id, _target(course_id, skill_id), ReviewAttempt.status != "in_progress")
            .order_by(ReviewAttempt.started_at.desc(), ReviewAttempt.attempt_id.desc())
            .limit(attempts)
        )
    )
    if not attempt_ids:
        return {}
    penalty = {aid: attempts - i for i, aid in enumerate(attempt_ids)}
    out: dict[int, int] = {}
    rows = db.execute(
        select(ReviewAnswer.question_id, ReviewAnswer.attempt_id).where(ReviewAnswer.attempt_id.in_(attempt_ids))
    )
    for question_id, attempt_id in rows:
        out[question_id] = max(out.get(question_id, 0), penalty[attempt_id])
    return out


def question_sources(db: Session, *, question_ids: list[int] | None = None, skill_id: int | None = None) -> list:
    """Bước A chống trùng ý (25/11): (question_id, type, chunk_id, nội dung đoạn, ai_check, is_active, disabled_reason,
    mentor_status) của câu CÓ meta (câu AI soạn / qua kho) — theo danh sách id hoặc theo kỹ năng."""
    stmt = (
        select(
            ReviewQuestion.question_id, ReviewQuestion.type, ReviewQuestion.chunk_id, KnowledgeChunk.content,
            ReviewQuestionMeta.ai_check, ReviewQuestion.is_active, ReviewQuestionMeta.disabled_reason,
            ReviewQuestionMeta.mentor_status,
        )  # fmt: skip
        .join(ReviewQuestionMeta, ReviewQuestionMeta.question_id == ReviewQuestion.question_id)
        .outerjoin(KnowledgeChunk, KnowledgeChunk.chunk_id == ReviewQuestion.chunk_id)
        .order_by(ReviewQuestion.question_id)
    )
    if question_ids is not None:
        if not question_ids:
            return []
        stmt = stmt.where(ReviewQuestion.question_id.in_(question_ids))
    if skill_id is not None:
        stmt = stmt.where(ReviewQuestion.skill_id == skill_id)
    return list(db.execute(stmt).all())


def family_ids(db: Session, question_ids: list[int]) -> dict[int, int]:
    """{question_id: family_id} — câu chưa có meta là họ của chính nó."""
    if not question_ids:
        return {}
    family = func.coalesce(ReviewQuestionMeta.family_id, ReviewQuestion.question_id)
    rows = db.execute(
        select(ReviewQuestion.question_id, family)
        .outerjoin(ReviewQuestionMeta, ReviewQuestionMeta.question_id == ReviewQuestion.question_id)
        .where(ReviewQuestion.question_id.in_(question_ids))
    )
    return dict(rows.all())


def last_submitted_questions(
    db: Session, user_id: int, course_id: int | None = None, *, skill_id: int | None = None
) -> list[ReviewQuestion]:
    """Các câu của lượt ĐÃ NỘP gần nhất (cùng khóa, hoặc cùng kỹ năng) — để lượt mới tránh lặp (A1)."""
    last_id = db.scalar(
        select(ReviewAttempt.attempt_id)
        .where(
            ReviewAttempt.user_id == user_id,
            _target(course_id, skill_id),
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


def get_active_skill_name(db: Session, skill_id: int) -> str | None:
    return db.scalar(select(Skills.skill).where(Skills.skill_id == skill_id, Skills.is_active.is_(True)))


def path_has_skill(db: Session, path_id: int, user_id: int, skill_id: int) -> bool:
    """Lộ trình là của người học này VÀ có node kỹ năng này (bảng của Hòa — chỉ đọc). G2c, 22/11."""
    return (
        db.scalar(
            select(LearningPathNode.skill_id)
            .join(LearningPath, LearningPath.record_id == LearningPathNode.path_id)
            .where(
                LearningPathNode.path_id == path_id,
                LearningPathNode.skill_id == skill_id,
                LearningPath.student_id == user_id,
            )
        )
        is not None
    )


# ─────────────── "Đến hạn ôn" (21/11, Q12 guide.md) ───────────────


def skill_review_history(db: Session, user_id: int, skill_ids) -> list[tuple[int, object, bool, object]]:
    """Mỗi lượt ôn ĐÃ CHẤM của người học, tách theo từng kỹ năng của khóa (đạt bài khóa = đã ôn mọi kỹ năng
    của khóa). Trả (skill_id, submitted_at, passed, score), cũ trước."""
    ids = list(set(skill_ids))
    if not ids:
        return []
    stmt = (
        select(CourseSkill.skill_id, ReviewAttempt.submitted_at, ReviewAttempt.passed, ReviewAttempt.score)
        .join(CourseSkill, CourseSkill.course_id == ReviewAttempt.course_id)
        .where(
            ReviewAttempt.user_id == user_id,
            ReviewAttempt.status == "graded",
            ReviewAttempt.passed.is_not(None),
            ReviewAttempt.submitted_at.is_not(None),
            CourseSkill.skill_id.in_(ids),
        )
        .order_by(ReviewAttempt.submitted_at, ReviewAttempt.attempt_id)
    )
    # G2d: lượt ôn THẲNG theo kỹ năng cũng là một lần ôn kỹ năng đó
    direct = (
        select(ReviewAttempt.skill_id, ReviewAttempt.submitted_at, ReviewAttempt.passed, ReviewAttempt.score)
        .where(
            ReviewAttempt.user_id == user_id,
            ReviewAttempt.status == "graded",
            ReviewAttempt.passed.is_not(None),
            ReviewAttempt.submitted_at.is_not(None),
            ReviewAttempt.skill_id.in_(ids),
        )
        .order_by(ReviewAttempt.submitted_at, ReviewAttempt.attempt_id)
    )
    rows = [tuple(r) for r in db.execute(stmt).all()] + [tuple(r) for r in db.execute(direct).all()]
    return sorted(rows, key=lambda r: r[1])  # cũ trước


def known_skill_ids(db: Session, user_id: int, skill_ids=None) -> set[int]:
    """Kỹ năng người học đang để "Đã biết" (bảng user_skills, module 01)."""
    stmt = select(UserSkill.skill_id).where(UserSkill.user_id == user_id, UserSkill.status == "known")
    if skill_ids is not None:
        stmt = stmt.where(UserSkill.skill_id.in_(list(set(skill_ids))))
    return set(db.scalars(stmt))


def users_with_passed_review(db: Session) -> list[int]:
    """Người học từng có ít nhất một lượt ôn ĐẠT — chỉ những người này có thể có kỹ năng đến hạn ôn."""
    stmt = (
        select(ReviewAttempt.user_id)
        .where(ReviewAttempt.status == "graded", ReviewAttempt.passed.is_(True))
        .distinct()
        .order_by(ReviewAttempt.user_id)
    )
    return list(db.scalars(stmt))


def graded_attempts(db: Session, course_id: int | None = None) -> list[ReviewAttempt]:
    """Mọi lượt ĐÃ CHẤM (mới nộp trước), kèm câu trả lời + câu hỏi — trang "Bài cần xem lại" (17/11).
    Cờ nằm trong trace JSON nên lọc ở service; số lượt ôn tập của đồ án nhỏ (vài trăm) nên đọc hết được."""
    stmt = (
        select(ReviewAttempt)
        .where(ReviewAttempt.status == "graded")
        .options(selectinload(ReviewAttempt.answers).selectinload(ReviewAnswer.question))
        .order_by(ReviewAttempt.submitted_at.desc(), ReviewAttempt.attempt_id.desc())
    )
    if course_id is not None:
        stmt = stmt.where(ReviewAttempt.course_id == course_id)
    return list(db.scalars(stmt))


def user_names(db: Session, user_ids) -> dict[int, tuple[str, str]]:
    """{user_id: (họ tên, email)} — chỉ dùng cho trang admin."""
    ids = list(set(user_ids))
    if not ids:
        return {}
    rows = db.execute(select(Users.user_id, Users.full_name, Users.email).where(Users.user_id.in_(ids))).all()
    return {uid: (name, email) for uid, name, email in rows}


def course_titles(db: Session, course_ids) -> dict[int, str]:
    ids = list(set(course_ids))
    if not ids:
        return {}
    return dict(db.execute(select(Courses.course_id, Courses.title).where(Courses.course_id.in_(ids))).all())


def list_history(
    db: Session,
    user_id: int,
    *,
    course_id: int | None = None,
    passed: bool | None = None,
    offset: int = 0,
    limit: int = 10,
) -> tuple[list[ReviewAttempt], int]:
    """Các lượt ĐÃ NỘP của người dùng (theo khóa và theo kỹ năng, mới nhất trước) + tổng số dòng khớp bộ lọc."""
    conditions = [ReviewAttempt.user_id == user_id, ReviewAttempt.status != "in_progress"]
    if course_id is not None:
        conditions.append(ReviewAttempt.course_id == course_id)
    if passed is not None:
        conditions.append(ReviewAttempt.passed.is_(passed))
    total = db.scalar(select(func.count()).select_from(ReviewAttempt).where(*conditions))
    # G2d: không JOIN courses — lượt theo kỹ năng (course_id NULL) vẫn phải có trong lịch sử; tên do service lấy
    rows = db.scalars(
        select(ReviewAttempt)
        .where(*conditions)
        .order_by(ReviewAttempt.submitted_at.desc(), ReviewAttempt.attempt_id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return list(rows), total


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


def codes_for_skill(db: Session, skill_id: int) -> list[str]:
    """Mọi mã câu (kể cả phiên bản cũ "~v1") của một kỹ năng — để gợi ý mã khi duyệt."""
    return list(
        db.scalars(
            select(ReviewQuestion.code).where(ReviewQuestion.skill_id == skill_id, ReviewQuestion.code.is_not(None))
        )
    )


def skill_exists(db: Session, skill_id: int) -> bool:
    return db.scalar(select(func.count()).select_from(Skills).where(Skills.skill_id == skill_id)) > 0


def chunk_skill_id(db: Session, chunk_id: int) -> int | None:
    """Kỹ năng của đoạn tri thức (None = đoạn không tồn tại)."""
    return db.scalar(select(KnowledgeChunk.skill_id).where(KnowledgeChunk.chunk_id == chunk_id))


def list_questions(
    db: Session,
    *,
    skill_ids: list[int] | None = None,
    type: str | None = None,
    level: str | None = None,
    source: str | None = None,
    is_active: bool | None = None,
    review_status: str | None = None,
    q: str | None = None,
    latest_only: bool = True,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list, int]:
    """Danh sách câu hỏi cho trang quản trị + tổng số dòng khớp bộ lọc.

    Mỗi dòng: (ReviewQuestion, version, family_id, review_status, used_count, skill_name, mentor_status).
    - Câu chưa có meta (nạp trước 13/11) → coi như phiên bản 1, họ = chính nó, đã duyệt (OUTER JOIN + COALESCE).
    - used_count đếm bằng subquery GROUP BY — một truy vấn cho cả trang (không N+1).
    - latest_only: chỉ phiên bản mới nhất của mỗi họ (bản cũ xem ở "Lịch sử phiên bản" của trang chi tiết).
    - skill_ids=[] (vd khóa không có kỹ năng) → không có dòng nào.
    """
    used = select(ReviewAnswer.question_id, func.count().label("n")).group_by(ReviewAnswer.question_id).subquery()
    latest = (
        select(
            ReviewQuestionMeta.family_id,
            func.max(ReviewQuestionMeta.version).label("max_version"),
        )
        .group_by(ReviewQuestionMeta.family_id)
        .subquery()
    )
    version = func.coalesce(ReviewQuestionMeta.version, 1)
    family = func.coalesce(ReviewQuestionMeta.family_id, ReviewQuestion.question_id)
    status = func.coalesce(ReviewQuestionMeta.review_status, "approved")

    conditions = []
    if skill_ids is not None:
        conditions.append(ReviewQuestion.skill_id.in_(skill_ids))
    if type is not None:
        conditions.append(ReviewQuestion.type == type)
    if level is not None:
        conditions.append(ReviewQuestion.level == level)
    if source is not None:
        conditions.append(ReviewQuestion.source == source)
    if is_active is not None:
        conditions.append(ReviewQuestion.is_active.is_(is_active))
    if review_status is not None:
        conditions.append(status == review_status)
    if q:
        text = q.strip().lower()
        conditions.append(
            func.lower(ReviewQuestion.content).contains(text, autoescape=True)
            | func.lower(func.coalesce(ReviewQuestion.code, "")).contains(text, autoescape=True)
        )
    if latest_only:
        conditions.append(
            ReviewQuestionMeta.question_id.is_(None) | (ReviewQuestionMeta.version == latest.c.max_version)
        )

    def _from(stmt):
        stmt = stmt.outerjoin(
            ReviewQuestionMeta,
            ReviewQuestionMeta.question_id == ReviewQuestion.question_id,
        )
        if latest_only:
            stmt = stmt.outerjoin(latest, latest.c.family_id == ReviewQuestionMeta.family_id)
        return stmt.where(*conditions)

    total = db.scalar(_from(select(func.count()).select_from(ReviewQuestion)))
    rows = db.execute(
        _from(
            select(
                ReviewQuestion,
                version.label("version"),
                family.label("family_id"),
                status.label("review_status"),
                func.coalesce(used.c.n, 0).label("used_count"),
                Skills.skill.label("skill_name"),
                ReviewQuestionMeta.mentor_status.label("mentor_status"),  # G3f (25/11): mentor duyệt câu AI soạn
            ).select_from(ReviewQuestion)
        )
        .outerjoin(used, used.c.question_id == ReviewQuestion.question_id)
        .outerjoin(Skills, Skills.skill_id == ReviewQuestion.skill_id)
        .order_by(ReviewQuestion.question_id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return rows, total


def family_metas(db: Session, family_id: int) -> list[ReviewQuestionMeta]:
    """Mọi phiên bản của một họ câu hỏi, mới nhất trước."""
    return list(
        db.scalars(
            select(ReviewQuestionMeta)
            .where(ReviewQuestionMeta.family_id == family_id)
            .order_by(ReviewQuestionMeta.version.desc())
        )
    )
