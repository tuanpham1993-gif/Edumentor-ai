from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CourseSkillCreate(BaseModel):
    course_id: int = Field(..., description="ID của khóa học")
    skill_id: int = Field(..., description="ID của kỹ năng")


class CourseSkillResponse(BaseModel):
    course_id: int
    skill_id: int
    model_config = ConfigDict(from_attributes=True)


class CourseSkillDetailResponse(BaseModel):
    course_id: int
    course_title: str
    skill_id: int
    skill_name: str
    model_config = ConfigDict(from_attributes=True)

