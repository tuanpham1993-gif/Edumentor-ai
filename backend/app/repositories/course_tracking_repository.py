"""Repository bảng `user_courses`: chỉ truy vấn DB, không chứa nghiệp vụ."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.course import Courses
from app.models.course_skill import CourseSkill
from app.models.skill import Skills
from app.models.user_course import UserCourse


def get_course(db: Session, course_id: int) -> Courses | None:
    return db.get(Courses, course_id)


def get_tracking(
    db: Session,
    user_id: int,
    course_id: int,
    *,
    for_update: bool = False,
) -> UserCourse | None:
    stmt = select(UserCourse).where(
        UserCourse.user_id == user_id,
        UserCourse.course_id == course_id,
    )
    if for_update:
        stmt = stmt.with_for_update().execution_options(populate_existing=True)
    return db.scalar(stmt)


def get_tracking_with_course(
    db: Session,
    user_id: int,
    course_id: int,
) -> UserCourse | None:
    stmt = (
        select(UserCourse)
        .where(
            UserCourse.user_id == user_id,
            UserCourse.course_id == course_id,
        )
        .options(joinedload(UserCourse.course).selectinload(Courses.skills_info))
    )
    return db.scalars(stmt).unique().one_or_none()


def add_tracking(
    db: Session,
    *,
    user_id: int,
    course_id: int,
    status: str,
    joined_at: datetime | None = None,
) -> UserCourse:
    row = UserCourse(
        user_id=user_id,
        course_id=course_id,
        status=status,
        joined_at=joined_at,
    )
    db.add(row)
    return row


def delete_tracking(db: Session, row: UserCourse) -> None:
    db.delete(row)


def get_active_course_skill_ids(db: Session, course_id: int) -> list[int]:
    """Các skill_id đang bật (is_active=True) gắn với khóa học."""
    stmt = (
        select(Skills.skill_id)
        .join(CourseSkill, CourseSkill.skill_id == Skills.skill_id)
        .where(
            CourseSkill.course_id == course_id,
            Skills.is_active.is_(True),
        )
        .order_by(Skills.skill_id)
    )
    return list(db.scalars(stmt))


def get_other_ongoing_skill_ids(
    db: Session,
    user_id: int,
    *,
    exclude_course_id: int,
) -> set[int]:
    """Các skill_id đang bật thuộc những khóa KHÁC mà user vẫn đang học (ongoing)."""
    stmt = (
        select(CourseSkill.skill_id)
        .join(UserCourse, UserCourse.course_id == CourseSkill.course_id)
        .join(Skills, Skills.skill_id == CourseSkill.skill_id)
        .where(
            UserCourse.user_id == user_id,
            UserCourse.status == "ongoing",
            UserCourse.course_id != exclude_course_id,
            Skills.is_active.is_(True),
        )
    )
    return set(db.scalars(stmt))


def list_by_user(
    db: Session,
    user_id: int,
    *,
    status: str | None = None,
    exclude_statuses: tuple[str, ...] = (),
    page: int = 1,
    page_size: int = 10,
) -> tuple[int, list[UserCourse]]:
    conditions = [UserCourse.user_id == user_id]
    if status is not None:
        conditions.append(UserCourse.status == status)
    elif exclude_statuses:
        conditions.append(UserCourse.status.notin_(exclude_statuses))

    total = (
        db.scalar(select(func.count()).select_from(UserCourse).where(*conditions)) or 0
    )

    offset = max(0, (page - 1) * page_size)
    stmt = (
        select(UserCourse)
        .where(*conditions)
        .order_by(UserCourse.updated_at.desc(), UserCourse.course_id.desc())
        .options(joinedload(UserCourse.course).selectinload(Courses.skills_info))
        .offset(offset)
        .limit(page_size)
    )
    rows = list(db.scalars(stmt).unique().all())
    return total, rows
