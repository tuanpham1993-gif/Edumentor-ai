from typing import Literal
from sqlalchemy.orm import Session
from app.models.course import Courses
from app.models.skill import Skills
from app.repositories import course_repository


def list_courses(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    skill_id: int | None = None,
    level: str | None = None,
    sort_by: Literal["rating", "num_reviews"] | None = None,
) -> tuple[int, list[Courses]]:
    """Xử lý nghiệp vụ lấy danh sách khóa học kèm bộ lọc và phân trang."""
    return course_repository.list_courses(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        skill_id=skill_id,
        level=level,
        sort_by=sort_by,
    )


def get_course(db: Session, course_id: int) -> Courses | None:
    """Xử lý nghiệp vụ lấy chi tiết khóa học theo ID."""
    return course_repository.get_course_by_id(db=db, course_id=course_id)


def get_course_skills(db: Session, course_id: int) -> list[Skills] | None:
    """Xử lý nghiệp vụ lấy danh sách kỹ năng của khóa học."""
    return course_repository.get_course_skills(db=db, course_id=course_id)
