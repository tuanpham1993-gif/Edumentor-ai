from app.core.database import get_db
from app.core.dependencies import require_admin
from app.schemas.common import PaginatedResponse
from app.schemas.course_skill import (
    CourseSkillCreate,
    CourseSkillDetailResponse,
    CourseSkillResponse,
)
from app.services.course_service import CourseService
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get(
    "",
    response_model=PaginatedResponse[CourseSkillDetailResponse],
    summary="Lấy danh sách liên kết giữa khóa học và kỹ năng",
    description="Hỗ trợ phân trang, lọc theo ID khóa học hoặc ID kỹ năng.",
)
def get_admin_course_skill_relations(
    page: int = Query(default=1, ge=1, description="Số trang (bắt đầu từ 1)"),
    page_size: int = Query(
        default=20, ge=1, le=100, description="Số bản ghi trên mỗi trang"
    ),
    course_id: int | None = Query(default=None, description="Lọc theo ID khóa học"),
    skill_id: int | None = Query(default=None, description="Lọc theo ID kỹ năng"),
    db: Session = Depends(get_db),
):
    service = CourseService(db)
    return service.list_course_skill_relations(
        page=page, page_size=page_size, course_id=course_id, skill_id=skill_id
    )


@router.post(
    "",
    response_model=CourseSkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Liên kết một khóa học với một kỹ năng",
    description="Tạo mối liên kết giữa khóa học và kỹ năng mà khóa học đó giảng dạy.",
)
def create_admin_course_skill_relation(
    data: CourseSkillCreate,
    db: Session = Depends(get_db),
):
    service = CourseService(db)
    return service.add_course_skill_relation(data)


@router.delete(
    "/{course_id}/{skill_id}",
    summary="Xóa liên kết giữa khóa học và kỹ năng",
    description="Gỡ bỏ kỹ năng khỏi danh sách kỹ năng mà khóa học giảng dạy.",
)
def delete_admin_course_skill_relation(
    course_id: int,
    skill_id: int,
    db: Session = Depends(get_db),
):
    service = CourseService(db)
    return service.delete_course_skill_relation(course_id=course_id, skill_id=skill_id)
