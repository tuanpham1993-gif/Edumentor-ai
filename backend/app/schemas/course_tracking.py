"""Schema request/response cho module Lưu khóa học và Theo dõi trạng thái."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.course import CourseSkillItem

CourseTrackingStatus = Literal["bookmarked", "ongoing", "completed", "abandoned"]


class BookmarkCreateRequest(BaseModel):
    course_id: int = Field(..., gt=0, description="ID khóa học cần lưu để học sau")


class CourseStatusUpdateRequest(BaseModel):
    status: CourseTrackingStatus = Field(
        ...,
        description="Trạng thái mới được phép chuyển đổi (bookmarked | ongoing | abandoned)",
    )

    @field_validator("status")
    @classmethod
    def reject_manual_completed(
        cls, value: CourseTrackingStatus
    ) -> CourseTrackingStatus:
        if value == "completed":
            raise ValueError(
                "Không thể tự đánh dấu trạng thái 'completed'. "
                "Khóa học chỉ hoàn thành khi bạn làm đạt bài ôn tập."
            )
        return value


class CourseTrackingItemOut(BaseModel):
    course_id: int
    title: str
    instructor: str | None = None
    organization: str | None = None
    level: str | None = None
    rating: float | None = None
    num_reviews: int | None = None
    url: str | None = None
    image: str | None = None
    skills_info: list[CourseSkillItem] = Field(default_factory=list)
    status: CourseTrackingStatus
    joined_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseJoinOut(BaseModel):
    course_id: int
    title: str
    status: CourseTrackingStatus
    url: str | None = None
    joined_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime


class CourseStatusOut(BaseModel):
    course_id: int
    status: CourseTrackingStatus | None = None
    is_bookmarked: bool
    joined_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime | None = None
