from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SkillCreate(BaseModel):
    skill: str = Field(min_length=1, max_length=255)

    @field_validator("skill")
    @classmethod
    def validate_skill(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Tên kỹ năng không được để trống.")
        return value


class SkillUpdate(BaseModel):
    skill: Optional[str] = Field(default=None, min_length=1, max_length=255)
    is_active: Optional[bool] = None

    @field_validator("skill")
    @classmethod
    def validate_skill(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Tên kỹ năng không được để trống nếu được cập nhật.")
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
    limit: int
    current_total: int
    data: list[SkillRequestResponse]


# ============================================================
# SKILL ALIASES
# ============================================================
# Stored in Qdrant (collection edumentor_skills, points with kind="alias"), one point per alias.
# An alias is identified by its normalized text, so there is no alias_id.
# Rules (enforced by app/services/ai_reference_service.py):
#   - one alias -> one skill (case-insensitive)
#   - an alias must not equal any skills.skill name (exact match and alias match would disagree)
#   - skill_id must be an active skill in Postgres `skills`
# Seed data: datajson/skill_alias.json ([{skill_id, skill, aliases: [...]}]).


def _clean_alias(value: str) -> str:
    value = " ".join(value.split())
    if not value:
        raise ValueError("Tên alias không được để trống.")
    return value


class SkillAliasCreate(BaseModel):
    skill_id: int = Field(gt=0)
    alias_name: str = Field(min_length=1, max_length=255)

    @field_validator("alias_name")
    @classmethod
    def validate_alias_name(cls, value: str) -> str:
        return _clean_alias(value)


class SkillAliasUpdate(BaseModel):
    """Rename an alias and/or move it to another skill."""
    skill_id: Optional[int] = Field(default=None, gt=0)
    alias_name: Optional[str] = Field(default=None, min_length=1, max_length=255)

    @field_validator("alias_name")
    @classmethod
    def validate_alias_name(cls, value: Optional[str]) -> Optional[str]:
        return _clean_alias(value) if value is not None else value


class SkillAliasResponse(BaseModel):
    skill_id: int
    skill: str
    alias_name: str
