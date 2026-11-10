from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.skills_service import SkillsService
from app.schemas.skill import (
    SkillCreate,
    SkillUpdate,
    SkillRequestResponse,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[SkillRequestResponse],
    summary="Lấy danh sách kỹ năng",
    description="Hỗ trợ phân trang, tìm kiếm theo tên kỹ năng và lọc theo trạng thái hoạt động.",
)
def get_admin_skills(
    page: int = Query(default=1, ge=1, description="Số trang (bắt đầu từ 1)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Số bản ghi trên mỗi trang"),
    search: Optional[str] = Query(default=None, description="Tìm kiếm theo tên kỹ năng"),
    is_active: Optional[bool] = Query(default=None, description="Lọc theo trạng thái hoạt động"),
    db: Session = Depends(get_db),
):
    service = SkillsService(db)
    return service.list_skills_admin(page=page, page_size=page_size, search=search, is_active=is_active)


@router.post(
    "",
    response_model=SkillRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm kỹ năng mới",
    description="Thêm một kỹ năng mới vào hệ thống (không trùng tên).",
)
def create_admin_skill(
    data: SkillCreate,
    db: Session = Depends(get_db),
):
    service = SkillsService(db)
    return service.create_skill(data)


@router.patch(
    "/{skill_id}",
    response_model=SkillRequestResponse,
    summary="Cập nhật thông tin kỹ năng",
    description="Đổi tên hoặc trạng thái kích hoạt của kỹ năng.",
)
def update_admin_skill(
    skill_id: int,
    data: SkillUpdate,
    db: Session = Depends(get_db),
):
    service = SkillsService(db)
    return service.update_skill(skill_id, data)


@router.delete(
    "/{skill_id}",
    summary="Xóa kỹ năng khi việc xóa không gây ảnh hưởng không mong muốn",
    description="Nếu kỹ năng đang được liên kết trong khóa học, lộ trình hoặc quan hệ kỹ năng, hệ thống sẽ tự động chuyển sang vô hiệu hóa (is_active = False) để đảm bảo toàn vẹn dữ liệu.",
)
def delete_admin_skill(
    skill_id: int,
    db: Session = Depends(get_db),
):
    service = SkillsService(db)
    return service.delete_skill(skill_id)

