"""
Tập hợp tất cả các Sub-router của API v1 thành một Router thống nhất.
"""

from fastapi import APIRouter

from app.routers.v1.endpoints import health
from app.routers.v1.chat_tutor import router as chat_tutor_router
api_router = APIRouter()

# 1. Kiểm tra sức khỏe hệ thống
api_router.include_router(health.router, tags=["System Health"])

# 2. Chatbot gia sư
api_router.include_router(chat_tutor_router)