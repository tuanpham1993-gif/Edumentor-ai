"""
Tập hợp tất cả các Sub-router của API v1 thành một Router thống nhất.

Thứ tự khai báo dưới đây cũng chính là thứ tự các nhóm hiển thị trên Swagger UI,
nên hãy xếp theo đúng trình tự bài giảng để sinh viên dễ theo dõi.
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
    me,
    notifications,
    review,
    skill_service,
)

# Tạm comment để khỏi tải/nạp SentenceTransformer ngay khi chạy server hay pytest;
# nếu cần test /api/learning-paths-generation thì bỏ comment dòng này và dòng include_router ở cuối file:
# from app.routers.v1.endpoints import recommendation_service

api_router = APIRouter()

# 1. Kiểm tra sức khỏe hệ thống
api_router.include_router(health.router, tags=["System Health"], prefix="/health")
# 2. Tài khoản & hồ sơ (Tuấn)
api_router.include_router(auth.router, tags=["Auth"], prefix="/auth")
api_router.include_router(me.router, tags=["Me"], prefix="/me")
# Thông báo (chuông trên header — Tuấn, 11/11)
api_router.include_router(notifications.router, tags=["Notifications (Thông báo)"], prefix="/me/notifications")
# Tùy chọn nhận email (Tuấn, 11/11)
api_router.include_router(email_preferences.router, tags=["Me"], prefix="/me/email-preferences")
# 3. Khóa học & Ôn tập
api_router.include_router(courses.router, tags=["Course Catalog"], prefix="/courses")
api_router.include_router(course_tracking.router, tags=["Course Tracking"])
# Ôn tập (Tuấn, module 09) — không prefix: router tự khai đường dẫn /courses/... và /review-attempts/...
api_router.include_router(review.router, tags=["Review (Ôn tập)"])
# 4. Lộ trình, kỹ năng, gợi ý (Hòa)
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
    skill_service.router, tags=["skill endpoint"], prefix="/skills"
)
# api_router.include_router(recommendation_service.router, tags=["learning path generation"], prefix="/learning-paths-generation")

# Quản trị (Admin)
api_router.include_router(admin_router, prefix="/admin")
