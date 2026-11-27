"""Schemas for the per-learning-path learner profile snapshot (models/learner_profile.py).

The profile is one table; skills, target technologies and practical experiences are JSON
lists validated by the item models below. Enum values come from the G1 contract so the
database snapshot, the parser output and the dataset share one vocabulary.

LearnerProfileCreate.from_normalized() builds the snapshot from the NormalizedG1Output
(G1 parse + Python skill/role linking) once the learning path row exists.
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.utils.learner_analyzer.schemas import (
    CareerLevel,
    DeadlineType,
    DurationUnit,
    EvidenceType,
    GoalType,
    NormalizedG1Output,
    ProficiencyLevel,
    SkillLink,
    TimePeriod,
    TimeUnit,
)


class LinkedName(BaseModel):
    """A name from the query and the skills.skill_id it was linked to (null if unresolved)."""
    model_config = ConfigDict(extra="forbid")

    raw_name: str = Field(min_length=1, max_length=255)
    skill_id: Optional[int] = Field(default=None, gt=0)


class ProfileSkillItem(BaseModel):
    """A skill the learner already has."""
    model_config = ConfigDict(extra="forbid")

    raw_skill_name: str = Field(min_length=1, max_length=255)
    skill_id: Optional[int] = Field(default=None, gt=0)
    proficiency_level: Optional[ProficiencyLevel] = None
    experience_duration: Optional[str] = Field(default=None, max_length=50)
    evidence_type: EvidenceType


class PracticalExperienceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1)
    related_skills: list[LinkedName] = Field(default_factory=list)
    evidence_type: EvidenceType


class LearnerProfileBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    original_query: str = Field(min_length=1)
    goal_type: GoalType
    target_role_raw: Optional[str] = Field(default=None, max_length=255)
    role_id: Optional[int] = Field(default=None, gt=0)
    role_name: Optional[str] = Field(default=None, max_length=150)
    target_technologies: list[LinkedName] = Field(default_factory=list)

    career_level: Optional[CareerLevel] = None
    current_job_title: Optional[str] = Field(default=None, max_length=255)
    industry: Optional[str] = Field(default=None, max_length=255)
    relevant_it_work_experience: Optional[str] = Field(default=None, max_length=50)
    technical_domains: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    previous_job_roles: list[str] = Field(default_factory=list)

    skill_profiles: list[ProfileSkillItem] = Field(default_factory=list)
    practical_experiences: list[PracticalExperienceItem] = Field(default_factory=list)

    study_time_value: Optional[float] = Field(default=None, gt=0)
    study_time_unit: Optional[TimeUnit] = None
    study_time_period: Optional[TimePeriod] = None
    deadline_type: Optional[DeadlineType] = None
    deadline_target_date: Optional[date] = None
    deadline_duration_value: Optional[float] = Field(default=None, gt=0)
    deadline_duration_unit: Optional[DurationUnit] = None

    @model_validator(mode="after")
    def check_constraints(self):
        study = (self.study_time_value, self.study_time_unit, self.study_time_period)
        if any(v is not None for v in study) and any(v is None for v in study):
            raise ValueError("study time needs value, unit and period together")
        if self.deadline_type is None:
            if any(v is not None for v in (self.deadline_target_date, self.deadline_duration_value,
                                           self.deadline_duration_unit)):
                raise ValueError("deadline fields set without deadline_type")
        elif self.deadline_type == DeadlineType.FIXED_DATE:
            if self.deadline_target_date is None or self.deadline_duration_value or self.deadline_duration_unit:
                raise ValueError("fixed_date needs only deadline_target_date")
        elif self.deadline_target_date is not None or self.deadline_duration_value is None \
                or self.deadline_duration_unit is None:
            raise ValueError("relative_duration needs duration value and unit only")
        return self


class LearnerProfileCreate(LearnerProfileBase):
    path_id: int = Field(gt=0)

    @classmethod
    def from_normalized(cls, path_id: int, out: NormalizedG1Output) -> "LearnerProfileCreate":
        """Map a NormalizedG1Output onto the snapshot columns."""
        def link(s: SkillLink) -> LinkedName:
            return LinkedName(raw_name=s.raw_name, skill_id=s.skill_id)

        goal, cb, lc = out.goal, out.career_background, out.learning_constraints
        st, dl = lc.available_study_time, lc.deadline
        target_date = None
        if dl and dl.deadline_type == DeadlineType.FIXED_DATE:
            try:
                target_date = date.fromisoformat(dl.target_date or "")
            except ValueError:   # LLM date not in ISO format: keep no deadline rather than fail
                dl = None
        return cls(
            path_id=path_id,
            original_query=goal.original_query,
            goal_type=goal.goal_type,
            target_role_raw=goal.target_role.raw_name,
            role_id=goal.target_role.role_id,
            role_name=goal.target_role.canonical_name,
            target_technologies=[link(t) for t in goal.target_technologies],
            career_level=cb.career_level,
            current_job_title=cb.current_job_title.raw_name if cb.current_job_title else None,
            industry=cb.industry.raw_name if cb.industry else None,
            relevant_it_work_experience=cb.relevant_it_work_experience,
            technical_domains=[d.raw_name for d in cb.technical_domains],
            certifications=[c.raw_name for c in cb.certifications],
            previous_job_roles=[r.raw_name for r in cb.previous_job_roles],
            skill_profiles=[
                ProfileSkillItem(raw_skill_name=s.skill_name, skill_id=s.link.skill_id,
                                 proficiency_level=s.proficiency_level,
                                 experience_duration=s.experience_duration, evidence_type=s.evidence_type)
                for s in out.skill_profiles
            ],
            practical_experiences=[
                PracticalExperienceItem(description=p.description,
                                        related_skills=[link(r) for r in p.related_skills],
                                        evidence_type=p.evidence_type)
                for p in out.practical_experience
            ],
            study_time_value=st.value if st else None,
            study_time_unit=st.unit if st else None,
            study_time_period=st.period if st else None,
            deadline_type=dl.deadline_type if dl else None,
            deadline_target_date=target_date,
            deadline_duration_value=dl.duration_value if dl else None,
            deadline_duration_unit=dl.duration_unit if dl else None,
        )


class LearnerProfileResponse(LearnerProfileBase):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    profile_id: int
    path_id: int
    created_at: datetime
