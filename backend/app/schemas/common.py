from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="Danh sách dữ liệu trong trang hiện tại")
    total: int = Field(..., description="Tổng số bản ghi thỏa mãn điều kiện")
    page: int = Field(..., ge=1, description="Số trang hiện tại (bắt đầu từ 1)")
    page_size: int = Field(..., ge=1, description="Số bản ghi trên mỗi trang")

