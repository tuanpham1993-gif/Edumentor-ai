from pydantic import BaseModel, ConfigDict, Field, field_validator


class SkillCreate(BaseModel):
    skill: str = Field(min_length=1, max_length=255)

    @field_validator("skill")
    @classmethod
    def validate_skill(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Skill name cannot be empty.")
        return value

class SkillUpdate(BaseModel):
    skill: str = Field(min_length=1, max_length=255)

    @field_validator("skill")
    @classmethod
    def validate_skill(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Skill name cannot be empty.")
        return value

class SkillRequestResponse(BaseModel):
    skill: str
    skill_id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class SkillWithCoursesResponse(SkillRequestResponse):
    total_courses: int

class SkillListResponse(BaseModel):
    total: int
    skip: int
    limit:int
    current_total: int
    data: list[SkillRequestResponse]