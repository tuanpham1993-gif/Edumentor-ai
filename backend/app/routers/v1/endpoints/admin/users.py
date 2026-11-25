"""Router admin: tổng hợp số liệu, danh sách user và chi tiết lộ trình người dùng (F14)."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.schemas.admin import (
    AdminUserPathsDetailResponse,
    AdminUserPathsOverviewResponse,
    AdminUserPathSummaryItem,
)
from app.schemas.common import PaginatedResponse
from app.services.admin_user_path_service import AdminUserPathService

router = APIRouter(dependencies=[Depends(require_admin)])

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/overview",
    response_model=AdminUserPathsOverviewResponse,
    summary="Tổng hợp số liệu lộ trình toàn hệ thống",
    description="Trả về thống kê người dùng, trạng thái lộ trình và danh sách mục tiêu phổ biến.",
)
def get_admin_user_paths_overview(db: DbSession):
    service = AdminUserPathService(db)
    return service.get_overview()


@router.get(
    "/users",
    response_model=PaginatedResponse[AdminUserPathSummaryItem],
    summary="Danh sách người dùng kèm số liệu lộ trình",
    description="Hỗ trợ phân trang, tìm theo tên/email hoặc theo mục tiêu lộ trình, và lọc theo mục tiêu phổ biến.",
)
def list_admin_user_paths_users(
    db: DbSession,
    page: Annotated[int, Query(ge=1, description="Số trang (bắt đầu từ 1)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Số người dùng mỗi trang")] = 20,
    search: Annotated[str | None, Query(description="Từ khóa tìm kiếm")] = None,
    search_by: Annotated[
        Literal["user", "goal"],
        Query(description="Tìm theo người dùng (tên/email) hoặc theo mục tiêu lộ trình"),
    ] = "user",
    goal: Annotated[str | None, Query(description="Lọc theo mục tiêu phổ biến chính xác")] = None,
):
    service = AdminUserPathService(db)
    return service.list_users(
        page=page,
        page_size=page_size,
        search=search,
        search_by=search_by,
        goal=goal,
    )


@router.get(
    "/users/{user_id}",
    response_model=AdminUserPathsDetailResponse,
    summary="Xem chi tiết các lộ trình của một người dùng",
    description="Trả về thông tin người dùng, bộ đếm trạng thái và danh sách lộ trình kèm tiến độ kỹ năng (chỉ xem).",
)
def get_admin_user_paths_detail(user_id: int, db: DbSession):
    service = AdminUserPathService(db)
    return service.get_user_paths_detail(user_id)
