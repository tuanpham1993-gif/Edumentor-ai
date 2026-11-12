from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.course_service import CourseService
from app.schemas.course import (
    AdminCourseDetailResponse,
    CourseCreate,
    CourseLevel,
    CourseResponse,
    CourseUpdate,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[CourseResponse],
    summary="Lấy danh sách khóa học để quản trị",
    description="Hỗ trợ phân trang, tìm kiếm theo tiêu đề/mô tả/giảng viên/tổ chức và lọc theo cấp độ (level).",
)
def get_admin_courses(
    page: int = Query(default=1, ge=1, description="Số trang (bắt đầu từ 1)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Số bản ghi trên mỗi trang"),
    search: Optional[str] = Query(default=None, description="Từ khóa tìm kiếm"),
    level: Optional[CourseLevel] = Query(
        default=None,
        description="Lọc theo cấp độ khóa học (beginner, intermediate, advanced)",
    ),
    db: Session = Depends(get_db),
):
    service = CourseService(db)
    return service.list_courses(page=page, page_size=page_size, search=search, level=level)


@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm khóa học mới",
    description="Tạo khóa học mới vào hệ thống.",
)
def create_admin_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
):
    service = CourseService(db)
    return service.create_course(data)


@router.get(
    "/{course_id}",
    response_model=AdminCourseDetailResponse,
    summary="Lấy chi tiết khóa học",
    description="Lấy thông tin chi tiết khóa học kèm danh sách kỹ năng liên kết.",
)
def get_admin_course_detail(
    course_id: int,
    db: Session = Depends(get_db),
):
    service = CourseService(db)
    return service.get_course_detail(course_id)


@router.patch(
    "/{course_id}",
    response_model=CourseResponse,
    summary="Cập nhật thông tin khóa học",
    description="Cập nhật một phần thông tin khóa học theo ID.",
)
def update_admin_course(
    course_id: int,
    data: CourseUpdate,
    db: Session = Depends(get_db),
):
    service = CourseService(db)
    return service.update_course(course_id, data)


@router.delete(
    "/{course_id}",
    summary="Xóa khóa học khỏi danh mục",
    description="Xóa khóa học và các liên kết trong CourseSkill khỏi hệ thống.",
)
def delete_admin_course(
    course_id: int,
    db: Session = Depends(get_db),
):
    service = CourseService(db)
    return service.delete_course(course_id)

