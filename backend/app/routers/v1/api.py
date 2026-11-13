"""
Tập hợp tất cả các Sub-router của API v1 thành một Router thống nhất.
"""

from fastapi import APIRouter

from app.routers.admin import admin_router

from app.routers.v1.endpoints import (
    auth,
    course_tracking,
    courses,
    health,
    learning_path_node_service,
    learning_path_service,
    email_preferences,
    recommendation_service,
    me,
    notifications,
    review,
    skill_service,
)

# Chatbot Tutor của Tâm
from app.routers.v1.chat_tutor import (
    router as chat_tutor_router,
    public_router as public_chat_router,
)

# Tạm comment để tránh tải SentenceTransformer khi chạy server hoặc pytest
# from app.routers.v1.endpoints import recommendation_service


api_router = APIRouter()

# 1. Kiểm tra sức khỏe hệ thống
api_router.include_router(
    health.router,
    tags=["System Health"],
    prefix="/health",
)

# 2. Tài khoản và hồ sơ
api_router.include_router(auth.router, tags=["Auth"], prefix="/auth")
api_router.include_router(me.router, tags=["Me"], prefix="/me")

# Thông báo
api_router.include_router(
    notifications.router,
    tags=["Notifications (Thông báo)"],
    prefix="/me/notifications",
)

# Tùy chọn nhận email
api_router.include_router(
    email_preferences.router,
    tags=["Me"],
    prefix="/me/email-preferences",
)

# 3. Khóa học và ôn tập
api_router.include_router(
    courses.router,
    tags=["Course Catalog"],
    prefix="/courses",
)

api_router.include_router(
    course_tracking.router,
    tags=["Course Tracking"],
)

api_router.include_router(
    review.router,
    tags=["Review (Ôn tập)"],
)

# 4. Lộ trình và kỹ năng
api_router.include_router(
    learning_path_service.router,
    tags=["learning path endpoint"],
    prefix="/learning-paths",
)

api_router.include_router(
    learning_path_node_service.router,
    tags=["learning path node endpoint"],
    prefix="/learning-paths-nodes",
)

api_router.include_router(
    skill_service.router,
    tags=["skill endpoint"],
    prefix="/skills",
)

# Tạm thời chưa bật recommendation service
api_router.include_router(
    recommendation_service.router,
    tags=["learning path generation"],
    prefix="/learning-paths-generation",
)

# 5. Chatbot gia sư của Tâm

# Chatbot dành cho người đã đăng nhập
api_router.include_router(
    chat_tutor_router,
)

# Chatbot dành cho khách chưa đăng nhập
api_router.include_router(
    public_chat_router,
)

# 6. Quản trị Admin
api_router.include_router(
    admin_router,
    prefix="/admin",
)
