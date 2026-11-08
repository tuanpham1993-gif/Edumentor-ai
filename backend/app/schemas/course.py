from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class CourseSkillItem(BaseModel):
    skill_id: int
    skill: str
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class CourseSummaryResponse(BaseModel):
    course_id: int
    title: str
    num_enrolled: int | None = 0
    rating: float | None = 0.0
    num_reviews: int | None = 0
    instructor: str | None = None
    organization: str | None = None
    level: str | None = None
    image: str | None = None
    url: str | None = None
    skills_info: list[CourseSkillItem] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CourseDetailResponse(CourseSummaryResponse):
    description: str | None = None
    modules: str | None = None
    schedule: str | None = None


class CourseListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: list[CourseSummaryResponse]

