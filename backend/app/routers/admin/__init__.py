from app.core.dependencies import require_admin
from app.routers.admin.course_skill_relations import (
    router as admin_course_skill_relations_router,
)
from app.routers.admin.courses import router as admin_courses_router
from app.routers.admin.skills import router as admin_skills_router
from fastapi import APIRouter, Depends

admin_router = APIRouter(
    dependencies=[Depends(require_admin)],
    responses={
        401: {"description": "Chưa đăng nhập hoặc phiên đăng nhập không hợp lệ"},
        403: {"description": "Không có quyền thực hiện thao tác này (Chỉ Admin)"},
    },
)

admin_router.include_router(
    admin_courses_router, prefix="/courses", tags=["Admin Courses"]
)
admin_router.include_router(
    admin_skills_router, prefix="/skills", tags=["Admin Skills"]
)
admin_router.include_router(
    admin_course_skill_relations_router,
    prefix="/course-skill-relations",
    tags=["Admin Course-Skill Relations"],
)
