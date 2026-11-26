import math
from typing import Literal, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.course import Courses
from app.models.skill import Skills
from app.repositories import course_repository
from app.repositories.course_repository import CourseRepository
from app.repositories.skill_repository import SkillRepository
from app.schemas.common import PaginatedResponse
from app.schemas.course import (
    AdminCourseDetailResponse,
    CourseCreate,
    CourseLevel,
    CourseRecommendationResponse,
    CourseResponse,
    CourseSkillItem,
    CourseUpdate,
    RecommendedCourseItem,
)
from app.schemas.course_skill import (
    CourseSkillCreate,
    CourseSkillDetailResponse,
    CourseSkillResponse,
)


class CourseService:
    def __init__(self, db: Session):
        self.db = db
        self.course_repo = CourseRepository(db)
        self.skill_repo = SkillRepository(db)

    def list_courses(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        level: Optional[CourseLevel] = None,
    ) -> PaginatedResponse[CourseResponse]:
        total, items = self.course_repo.list_courses(
            page=page, page_size=page_size, search=search, level=level
        )
        return PaginatedResponse(
            items=[CourseResponse.model_validate(c) for c in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_course_detail(self, course_id: int) -> AdminCourseDetailResponse:
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với id {course_id}",
            )

        skills_list = [
            CourseSkillItem(
                skill_id=s.skill_id,
                skill=s.skill,
                is_active=s.is_active,
            )
            for s in course.skills_info
        ]

        course_res = AdminCourseDetailResponse.model_validate(course)
        course_res.skills = skills_list
        return course_res

    def create_course(self, data: CourseCreate) -> CourseResponse:
        if data.url:
            existing = self.course_repo.get_by_url(data.url)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"URL khóa học '{data.url}' đã tồn tại trong hệ thống.",
                )

        course = self.course_repo.create(data.model_dump())
        return CourseResponse.model_validate(course)

    def update_course(self, course_id: int, data: CourseUpdate) -> CourseResponse:
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với id {course_id}",
            )

        update_dict = data.model_dump(exclude_unset=True)

        new_url = update_dict.get("url")
        if new_url and new_url != course.url:
            existing = self.course_repo.get_by_url(new_url)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"URL khóa học '{new_url}' đã được sử dụng.",
                )

        updated_course = self.course_repo.update(course, update_dict)
        return CourseResponse.model_validate(updated_course)

    def delete_course(self, course_id: int) -> dict:
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với id {course_id}",
            )

        self.course_repo.delete(course)
        return {"message": f"Đã xóa thành công khóa học {course_id}"}

    # Course - Skill Relations
    def list_course_skill_relations(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        skill_id: Optional[int] = None,
    ) -> PaginatedResponse[CourseSkillDetailResponse]:
        total, items = self.course_repo.list_relations(
            page=page, page_size=page_size, course_id=course_id, skill_id=skill_id
        )
        return PaginatedResponse(
            items=[CourseSkillDetailResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def add_course_skill_relation(self, data: CourseSkillCreate) -> CourseSkillResponse:
        # 1. Kiểm tra Course có tồn tại không
        course = self.course_repo.get_by_id(data.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy khóa học với id {data.course_id}",
            )

        # 2. Kiểm tra Skill có tồn tại không
        skill = self.skill_repo.get_by_id(data.skill_id)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy kỹ năng với id {data.skill_id}",
            )

        # 3. Kiểm tra liên kết đã tồn tại chưa
        existing = self.course_repo.get_relation(data.course_id, data.skill_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Khóa học {data.course_id} đã được liên kết với kỹ năng {data.skill_id}.",
            )

        relation = self.course_repo.add_relation(data.course_id, data.skill_id)
        return CourseSkillResponse.model_validate(relation)

    def delete_course_skill_relation(self, course_id: int, skill_id: int) -> dict:
        deleted = self.course_repo.delete_relation(course_id, skill_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy liên kết giữa khóa học {course_id} và kỹ năng {skill_id}.",
            )
        return {"message": f"Đã xóa liên kết giữa khóa học {course_id} và kỹ năng {skill_id}"}


def list_courses(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    skill_id: int | None = None,
    level: str | None = None,
    sort_by: Literal["relevance", "rating", "num_reviews"] | None = None,
) -> tuple[int, list[Courses]]:
    """Xử lý nghiệp vụ lấy danh sách khóa học kèm bộ lọc và phân trang."""
    return course_repository.list_courses(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        skill_id=skill_id,
        level=level,
        sort_by=sort_by,
    )


def get_course(db: Session, course_id: int) -> Courses | None:
    """Xử lý nghiệp vụ lấy chi tiết khóa học theo ID."""
    return course_repository.get_course_by_id(db=db, course_id=course_id)


def get_course_skills(db: Session, course_id: int) -> list[Skills] | None:
    """Xử lý nghiệp vụ lấy danh sách kỹ năng của khóa học."""
    return course_repository.get_course_skills(db=db, course_id=course_id)


def _score_course_for_skill(
    course: Courses,
    skill_name: str,
    match_type: Literal["direct", "keyword_fallback"],
) -> tuple[float, str]:
    """Tính điểm gợi ý theo mức độ liên quan kỹ năng + độ tin cậy cộng đồng.

    Tuân thủ quy tắc dự án:
    - Mức độ liên quan kỹ năng là yếu tố hàng đầu; rating không phải bằng chứng duy nhất.
    - Không sử dụng điểm bài ôn tập trong xếp hạng khóa học.
    """
    score = 100.0 if match_type == "direct" else 0.0
    title_low = (course.title or "").lower()
    skill_low = skill_name.strip().lower()

    title_exact_focus = bool(skill_low and skill_low in title_low)
    if title_exact_focus:
        score += 60.0
    else:
        tokens = [t for t in skill_low.replace("(", " ").replace(")", " ").split() if len(t) >= 3]
        if tokens and all(t in title_low for t in tokens):
            score += 40.0
        elif tokens and any(t in title_low for t in tokens):
            score += 18.0

    # Độ tập trung kỹ năng: khóa học chuyên biệt ít kỹ năng loãng được cộng thêm điểm
    skill_count = len(course.skills_info) if course.skills_info else 1
    score += max(0.0, 20.0 - max(0, skill_count - 1) * 2.5)

    # Độ tin cậy đánh giá: rating chỉ phát huy khi đi cùng số lượt đánh giá đủ lớn
    rating = float(course.rating or 0.0)
    num_reviews = int(course.num_reviews or 0)
    num_enrolled = int(course.num_enrolled or 0)
    score += rating * min(math.log10(num_reviews + 1), 4.0) * 4.0
    score += min(math.log10(num_enrolled + 1), 6.0) * 1.5

    if match_type == "keyword_fallback":
        reason = "Tìm theo từ khóa tên kỹ năng"
    elif title_exact_focus:
        reason = "Khớp trọng tâm kỹ năng"
    elif num_reviews >= 500 and rating >= 4.5:
        reason = "Liên kết trực tiếp · Đánh giá cao"
    else:
        reason = "Liên kết trực tiếp với kỹ năng"

    return score, reason


def recommend_courses_for_skill(
    db: Session,
    *,
    skill_id: int,
    level: str | None = None,
    limit: int = 8,
    user_id: int | None = None,
) -> CourseRecommendationResponse:
    """Truy xuất và xếp hạng khóa học gợi ý khi người dùng bấm chọn 1 node kỹ năng."""
    skill = course_repository.get_skill_by_id(db=db, skill_id=skill_id)
    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy kỹ năng với id {skill_id}.",
        )

    has_direct = course_repository.has_any_course_for_skill(db=db, skill_id=skill_id)
    if has_direct:
        match_type: Literal["direct", "keyword_fallback"] = "direct"
        candidates = course_repository.list_direct_courses_for_skill(
            db=db, skill_id=skill_id, level=level, candidate_limit=100
        )
    else:
        match_type = "keyword_fallback"
        _, candidates = course_repository.list_courses(
            db=db,
            page=1,
            page_size=min(limit * 3, 30),
            search=skill.skill,
            level=level,
            sort_by="relevance",
        )

    scored: list[tuple[float, str, Courses]] = []
    for course in candidates:
        sc, reason = _score_course_for_skill(course, skill.skill, match_type)
        scored.append((sc, reason, course))

    scored.sort(
        key=lambda x: (
            -x[0],
            -(x[2].num_reviews or 0),
            -(x[2].rating or 0.0),
            x[2].course_id,
        )
    )

    total_matched = len(scored)
    top_scored = scored[:limit]

    course_ids = [c.course_id for _, _, c in top_scored]
    user_course_map: dict[int, str] = {}
    user_skill_status: str | None = None

    if user_id is not None:
        user_course_map = course_repository.get_user_course_statuses(
            db=db, user_id=user_id, course_ids=course_ids
        )
        user_skill_status = course_repository.get_user_skill_status(
            db=db, user_id=user_id, skill_id=skill_id
        )

    items: list[RecommendedCourseItem] = []
    for _, reason, course in top_scored:
        u_status = user_course_map.get(course.course_id)
        items.append(
            RecommendedCourseItem(
                course_id=course.course_id,
                title=course.title,
                num_enrolled=course.num_enrolled,
                rating=course.rating,
                num_reviews=course.num_reviews,
                instructor=course.instructor,
                organization=course.organization,
                level=course.level,
                image=course.image,
                url=course.url,
                skills_info=[
                    CourseSkillItem(
                        skill_id=s.skill_id,
                        skill=s.skill,
                        is_active=s.is_active,
                    )
                    for s in (course.skills_info or [])
                ],
                relevance_reason=reason,
                match_type=match_type,
                user_status=u_status,
                is_bookmarked=(u_status == "bookmarked"),
            )
        )

    return CourseRecommendationResponse(
        skill_id=skill.skill_id,
        skill_name=skill.skill,
        user_skill_status=user_skill_status if user_skill_status in ("known", "learning") else None,
        total=total_matched,
        items=items,
    )
