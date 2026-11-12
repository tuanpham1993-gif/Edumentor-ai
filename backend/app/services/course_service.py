from typing import Literal, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.course import Courses
from app.models.skill import Skills
from app.repositories import course_repository
from app.repositories.course_repository import CourseRepository
from app.repositories.skill_repository import SkillRepository
from app.schemas.common import PaginatedResponse
from app.schemas.course import (
    AdminCourseDetailResponse,
    CourseCreate,
    CourseLevel,
    CourseResponse,
    CourseSkillItem,
    CourseUpdate,
)
from app.schemas.course_skill import (
    CourseSkillCreate,
    CourseSkillDetailResponse,
    CourseSkillResponse,
)


class CourseService:
    def __init__(self, db: Session):
        self.db = db
        self.course_repo = CourseRepository(db)
        self.skill_repo = SkillRepository(db)

    def list_courses(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        level: Optional[CourseLevel] = None,
    ) -> PaginatedResponse[CourseResponse]:
        total, items = self.course_repo.list_courses(
            page=page, page_size=page_size, search=search, level=level
        )
        return PaginatedResponse(
            items=[CourseResponse.model_validate(c) for c in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_course_detail(self, course_id: int) -> AdminCourseDetailResponse:
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với id {course_id}",
            )

        skills_list = [
            CourseSkillItem(
                skill_id=s.skill_id,
                skill=s.skill,
                is_active=s.is_active,
            )
            for s in course.skills_info
        ]

        course_res = AdminCourseDetailResponse.model_validate(course)
        course_res.skills = skills_list
        return course_res

    def create_course(self, data: CourseCreate) -> CourseResponse:
        if data.url:
            existing = self.course_repo.get_by_url(data.url)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"URL khóa học '{data.url}' đã tồn tại trong hệ thống.",
                )

        course = self.course_repo.create(data.model_dump())
        return CourseResponse.model_validate(course)

    def update_course(self, course_id: int, data: CourseUpdate) -> CourseResponse:
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với id {course_id}",
            )

        update_dict = data.model_dump(exclude_unset=True)

        if "url" in update_dict and update_dict["url"] != course.url:
            existing = self.course_repo.get_by_url(update_dict["url"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"URL khóa học '{update_dict['url']}' đã được sử dụng.",
                )

        updated_course = self.course_repo.update(course, update_dict)
        return CourseResponse.model_validate(updated_course)

    def delete_course(self, course_id: int) -> dict:
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với id {course_id}",
            )

        self.course_repo.delete(course)
        return {"message": f"Đã xóa thành công khóa học {course_id}"}

    # Course - Skill Relations
    def list_course_skill_relations(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        skill_id: Optional[int] = None,
    ) -> PaginatedResponse[CourseSkillDetailResponse]:
        total, items = self.course_repo.list_relations(
            page=page, page_size=page_size, course_id=course_id, skill_id=skill_id
        )
        return PaginatedResponse(
            items=[CourseSkillDetailResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def add_course_skill_relation(self, data: CourseSkillCreate) -> CourseSkillResponse:
        # 1. Kiểm tra Course có tồn tại không
        course = self.course_repo.get_by_id(data.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với id {data.course_id}",
            )

        # 2. Kiểm tra Skill có tồn tại không
        skill = self.skill_repo.get_by_id(data.skill_id)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy kỹ năng với id {data.skill_id}",
            )

        # 3. Kiểm tra liên kết đã tồn tại chưa
        existing = self.course_repo.get_relation(data.course_id, data.skill_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Khóa học {data.course_id} đã được liên kết với kỹ năng {data.skill_id}.",
            )

        relation = self.course_repo.add_relation(data.course_id, data.skill_id)
        return CourseSkillResponse.model_validate(relation)

    def delete_course_skill_relation(self, course_id: int, skill_id: int) -> dict:
        deleted = self.course_repo.delete_relation(course_id, skill_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy liên kết giữa khóa học {course_id} và kỹ năng {skill_id}.",
            )
        return {"message": f"Đã xóa liên kết giữa khóa học {course_id} và kỹ năng {skill_id}"}


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
