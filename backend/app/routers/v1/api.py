"""
Tập hợp tất cả các Sub-router của API v1 thành một Router thống nhất.

Thứ tự khai báo dưới đây cũng chính là thứ tự các nhóm hiển thị trên Swagger UI,
nên hãy xếp theo đúng trình tự bài giảng để sinh viên dễ theo dõi.
"""

from fastapi import APIRouter
from app.routers.v1.endpoints import health

api_router = APIRouter()

# 1. Kiểm tra sức khỏe hệ thống
api_router.include_router(health.router, tags=["System Health"])