from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user_optional
from app.models.user import Users
from app.schemas.course import (
    CourseDetailResponse,
    CourseListResponse,
    CourseRecommendationResponse,
    CourseSkillItem,
)
from app.services import course_service

router = APIRouter()


@router.get(
    "/recommendations",
    response_model=CourseRecommendationResponse,
    summary="Gợi ý khóa học cho một node kỹ năng",
    description="Truy xuất theo yêu cầu khi người dùng chọn 1 node kỹ năng; xếp hạng ưu tiên mức độ liên quan kỹ năng.",
)
def get_recommended_courses_for_skill(
    skill_id: Annotated[int, Query(ge=1, description="Mã kỹ năng cần gợi ý khóa học")],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users | None, Depends(get_current_user_optional)],
    level: Annotated[
        Literal["beginner", "intermediate", "advanced"] | None,
        Query(description="Lọc theo độ khó"),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=20, description="Số khóa học tối đa")] = 8,
):
    return course_service.recommend_courses_for_skill(
        db=db,
        skill_id=skill_id,
        level=level,
        limit=limit,
        user_id=current_user.user_id if current_user else None,
    )


@router.get(
    "",
    response_model=CourseListResponse,
    summary="Lấy danh mục khóa học (có tìm kiếm, lọc, sắp xếp, phân trang)",
)
def get_courses(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Số trang (bắt đầu từ 1)"),
    page_size: int = Query(default=10, ge=1, le=50, description="Số bản ghi mỗi trang (1-50)"),
    search: str | None = Query(default=None, description="Tìm kiếm theo từ khóa"),
    skill_id: int | None = Query(default=None, description="Lọc theo mã kỹ năng"),
    level: Literal["beginner", "intermediate", "advanced"] | None = Query(
        default=None, description="Lọc theo độ khó (beginner, intermediate, advanced)"
    ),
    sort_by: Literal["relevance", "rating", "num_reviews"] | None = Query(
        default=None, description="Sắp xếp theo 'relevance', 'rating' hoặc 'num_reviews'"
    ),
):
    total, items = course_service.list_courses(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        skill_id=skill_id,
        level=level,
        sort_by=sort_by,
    )
    return CourseListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=items,
    )


@router.get(
    "/{course_id}",
    response_model=CourseDetailResponse,
    summary="Lấy thông tin chi tiết của một khóa học",
)
def get_course_detail(course_id: int, db: Session = Depends(get_db)):
    course = course_service.get_course(db=db, course_id=course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )
    return course


@router.get(
    "/{course_id}/skills",
    response_model=list[CourseSkillItem],
    summary="Lấy danh sách kỹ năng liên quan đến một khóa học",
)
def get_course_skills(course_id: int, db: Session = Depends(get_db)):
    skills = course_service.get_course_skills(db=db, course_id=course_id)
    if skills is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )
    return skills

