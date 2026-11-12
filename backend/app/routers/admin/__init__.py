from fastapi import APIRouter
from app.routers.admin.courses import router as admin_courses_router
from app.routers.admin.skills import router as admin_skills_router
from app.routers.admin.course_skill_relations import router as admin_course_skill_relations_router

admin_router = APIRouter()

admin_router.include_router(admin_courses_router, prefix="/courses", tags=["Admin Courses"])
admin_router.include_router(admin_skills_router, prefix="/skills", tags=["Admin Skills"])
admin_router.include_router(
    admin_course_skill_relations_router,
    prefix="/course-skill-relations",
    tags=["Admin Course-Skill Relations"],
)

