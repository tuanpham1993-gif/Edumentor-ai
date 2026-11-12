from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


CourseLevel = Literal["beginner", "intermediate", "advanced"]


class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Tên khóa học")
    num_enrolled: Optional[int] = Field(default=0, ge=0, description="Số người đã đăng ký")
    rating: Optional[float] = Field(
        default=None,
        description="Điểm đánh giá (0-5)",
        json_schema_extra={"minimum": 0.0, "maximum": 5.0},
    )
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

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 5.0):
            raise ValueError("Điểm đánh giá (rating) phải nằm trong khoảng từ 0 đến 5")
        return v


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    num_enrolled: Optional[int] = Field(default=None, ge=0)
    rating: Optional[float] = Field(
        default=None,
        description="Điểm đánh giá (0-5)",
        json_schema_extra={"minimum": 0.0, "maximum": 5.0},
    )
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

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 5.0):
            raise ValueError("Điểm đánh giá (rating) phải nằm trong khoảng từ 0 đến 5")
        return v


class CourseSkillItem(BaseModel):
    skill_id: int
    skill: str
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


# --- Schema dùng cho Admin (F11) ---
class CourseResponse(CourseBase):
    course_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AdminCourseDetailResponse(CourseResponse):
    skills: List[CourseSkillItem] = Field(default_factory=list, description="Danh sách kỹ năng khóa học giảng dạy")


# --- Schema dùng cho Danh mục công khai (F02) ---
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