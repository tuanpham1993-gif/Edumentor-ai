from typing import Literal
from sqlalchemy import func, select, or_
from sqlalchemy.orm import Session, selectinload
from app.models.course import Courses
from app.models.skill import Skills
from app.models.course_skill import CourseSkill


def list_courses(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    skill_id: int | None = None,
    level: str | None = None,
    sort_by: Literal["rating", "num_reviews"] | None = None,
) -> tuple[int, list[Courses]]:
    """Lấy danh sách khóa học có bộ lọc tìm kiếm, level, skill_id, sắp xếp và phân trang."""
    query = select(Courses)

    # 1. Bộ lọc tìm kiếm từ khóa
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Courses.title.ilike(term),
                Courses.instructor.ilike(term),
                Courses.organization.ilike(term),
                Courses.description.ilike(term),
            )
        )

    # 2. Bộ lọc theo độ khó
    if level and level.strip():
        query = query.where(Courses.level.ilike(level.strip()))

    # 3. Bộ lọc theo skill_id
    if skill_id is not None:
        query = query.join(CourseSkill, Courses.course_id == CourseSkill.course_id).where(
            CourseSkill.skill_id == skill_id
        )

    # Đếm tổng số bản ghi khớp điều kiện
    count_query = select(func.count()).select_from(query.order_by(None).subquery())
    total = db.scalar(count_query) or 0

    # 4. Sắp xếp
    if sort_by == "rating":
        query = query.order_by(
            Courses.rating.desc().nullslast(),
            Courses.num_reviews.desc().nullslast(),
            Courses.course_id.asc(),
        )
    elif sort_by == "num_reviews":
        query = query.order_by(
            Courses.num_reviews.desc().nullslast(),
            Courses.rating.desc().nullslast(),
            Courses.course_id.asc(),
        )
    else:
        query = query.order_by(Courses.course_id.asc())

    # 5. Phân trang
    offset = max(0, (page - 1) * page_size)
    items = db.scalars(
        query.options(selectinload(Courses.skills_info))
        .offset(offset)
        .limit(page_size)
    ).unique().all()

    return total, list(items)


def get_course(db: Session, course_id: int) -> Courses | None:
    """Lấy chi tiết khóa học kèm danh sách kỹ năng."""
    return db.scalars(
        select(Courses)
        .options(selectinload(Courses.skills_info))
        .where(Courses.course_id == course_id)
    ).unique().one_or_none()


def get_course_skills(db: Session, course_id: int) -> list[Skills] | None:
    """Lấy danh sách các kỹ năng liên quan của một khóa học."""
    course = db.scalars(
        select(Courses)
        .options(selectinload(Courses.skills_info))
        .where(Courses.course_id == course_id)
    ).unique().one_or_none()

    if course is None:
        return None

    return list(course.skills_info)

