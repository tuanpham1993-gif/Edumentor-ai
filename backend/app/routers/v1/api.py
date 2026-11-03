"""
Tập hợp tất cả các Sub-router của API v1 thành một Router thống nhất.

Thứ tự khai báo dưới đây cũng chính là thứ tự các nhóm hiển thị trên Swagger UI,
nên hãy xếp theo đúng trình tự bài giảng để sinh viên dễ theo dõi.
"""

from fastapi import APIRouter
from app.routers.v1.endpoints import health, learning_path_node_service, learning_path_service, skill_service

api_router = APIRouter()

# 1. Kiểm tra sức khỏe hệ thống
api_router.include_router(health.router, tags=["System Health"])
api_router.include_router(learning_path_service.router, tags=["learning path endpoint"])
api_router.include_router(learning_path_node_service.router, tags=["learning path node endpoint"])
api_router.include_router(skill_service.router, tags=["skill endpoint"])