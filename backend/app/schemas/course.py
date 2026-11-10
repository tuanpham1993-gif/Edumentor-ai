from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


CourseLevel = Literal["beginner", "intermediate", "advanced"]


class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Tên khóa học")
    num_enrolled: Optional[int] = Field(default=0, ge=0, description="Số người đã đăng ký")
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="Điểm đánh giá (0-5)")
    num_reviews: Optional[int] = Field(default=0, ge=0, description="Số lượt đánh giá")
    instructor: Optional[str] = Field(default=None, max_length=255, description="Tên giảng viên")
    organization: Optional[str] = Field(default=None, max_length=255, description="Đơn vị cung cấp")
    description: Optional[str] = Field(default=None, description="Mô tả nội dung khóa học")
    modules: Optional[str] = Field(default=None, max_length=100, description="Số chương / modules")
    level: Optional[str] = Field(default=None, description="Độ khó: beginner, intermediate, advanced...")
    schedule: Optional[str] = Field(default=None, max_length=255, description="Lịch trình học")
    url: Optional[str] = Field(default=None, max_length=500, description="Đường link khóa học gốc")
    image: Optional[str] = Field(default=None, max_length=500, description="Ảnh đại diện khóa học")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title không được để trống")
        return v


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    num_enrolled: Optional[int] = Field(default=None, ge=0)
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    num_reviews: Optional[int] = Field(default=None, ge=0)
    instructor: Optional[str] = Field(default=None, max_length=255)
    organization: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    modules: Optional[str] = Field(default=None, max_length=100)
    level: Optional[str] = Field(default=None, description="Độ khó: beginner, intermediate, advanced...")
    schedule: Optional[str] = Field(default=None, max_length=255)
    url: Optional[str] = Field(default=None, max_length=500)
    image: Optional[str] = Field(default=None, max_length=500)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title không được để trống nếu được cập nhật")
        return v


class CourseSkillItem(BaseModel):
    skill_id: int
    skill: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class CourseResponse(CourseBase):
    course_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CourseDetailResponse(CourseResponse):
    skills: List[CourseSkillItem] = Field(default_factory=list, description="Danh sách kỹ năng khóa học giảng dạy")

