"""Job roles, role aliases and role candidate skills (stored in Qdrant collection edumentor_job_roles).

role_id values are stable integers from datajson/job_roles.json; they are also
TargetRole.role_id in the G1 schema and learner_profiles.role_id.
candidate skills are skills.skill_id values validated against Postgres `skills`.
Service: app/services/ai_reference_service.py.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _clean(value: str) -> str:
    value = " ".join(value.split())
    if not value:
        raise ValueError("Tên không được để trống.")
    return value


class CandidateSkillItem(BaseModel):
    skill_id: int = Field(gt=0)
    skill: str


class JobRoleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_id: Optional[int] = Field(default=None, gt=0)   # null -> next free id
    role_name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)
    candidate_skill_ids: list[int] = Field(default_factory=list)

    _clean_name = field_validator("role_name")(lambda cls, v: _clean(v))

    @field_validator("aliases")
    @classmethod
    def clean_aliases(cls, value: list[str]) -> list[str]:
        return [_clean(a) for a in value]


class JobRoleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("role_name")
    @classmethod
    def clean_name(cls, value: Optional[str]) -> Optional[str]:
        return _clean(value) if value is not None else value


class JobRoleAliasCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alias_name: str = Field(min_length=1, max_length=150)
    _clean_alias = field_validator("alias_name")(lambda cls, v: _clean(v))


class RoleCandidateSkillCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_id: int = Field(gt=0)


class JobRoleAliasResponse(BaseModel):
    role_id: int
    role_name: str
    alias_name: str


class JobRoleResponse(BaseModel):
    role_id: int
    role_name: str
    description: Optional[str] = None
    is_active: bool
    aliases: list[str] = Field(default_factory=list)
    candidate_skills: list[CandidateSkillItem] = Field(default_factory=list)
