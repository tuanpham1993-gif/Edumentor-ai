
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class CareerLevel(str, Enum):
    BEGINNER = "beginner"
    INTERN = "intern"
    FRESHER = "fresher"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    LEAD = "lead"
    ARCHITECT = "architect"
    MANAGER = "manager"
    CAREER_SWITCHER = "career_switcher"
    STUDENT = "student"


class ProficiencyLevel(str, Enum):
    BASIC = "basic"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class EvidenceType(str, Enum):
    EXPLICITLY_REPORTED = "explicitly_reported"
    USER_PROVIDED_STRUCTURED = "user_provided_structured"
    INFERRED_FROM_CONTEXT = "inferred_from_context"

class GoalType(str, Enum):
    # v1 supports only these two goal types.
    # project: build a specific product/application/project.
    # career: everything else (reach a role, move into a field,
    # learn technologies for work).
    CAREER = "career"
    PROJECT = "project"

class G1Status(str, Enum):
    READY = "ready"
    NEEDS_CLARIFICATION = "needs_clarification"

class TimeUnit(str, Enum):
    HOURS = "hours"
    MINUTES = "minutes"


class TimePeriod(str, Enum):
    PER_DAY = "per_day"
    PER_WEEK = "per_week"


class DeadlineType(str, Enum):
    FIXED_DATE = "fixed_date"
    RELATIVE_DURATION = "relative_duration"


class DurationUnit(str, Enum):
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"

class AvailableStudyTime(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: float = Field(gt=0)
    unit: TimeUnit
    period: TimePeriod


class Deadline(BaseModel):
    model_config = ConfigDict(extra="forbid")

    deadline_type: DeadlineType
    target_date: Optional[str] = None
    duration_value: Optional[float] = Field(default=None, gt=0)
    duration_unit: Optional[DurationUnit] = None

class LearningConstraintsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    available_study_time: Optional[AvailableStudyTime] = None
    deadline: Optional[Deadline] = None

class SkillProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skill_name: str
    proficiency_level: Optional[ProficiencyLevel] = None
    experience_duration: Optional[str] = None

class LearnerInput(BaseModel):
    """Structured learner information supplied by the frontend."""
    model_config = ConfigDict(extra="forbid")
    current_job_title: Optional[str] = None
    career_level: Optional[CareerLevel] = None
    relevant_it_work_experience: Optional[str] = None
    industry: Optional[str] = None
    technical_domains: list[str] = Field(default_factory=list)
    skill_profiles: list[SkillProfileInput] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    learning_constraints: LearningConstraintsInput = Field(
        default_factory=LearningConstraintsInput
    )

class G1Input(BaseModel): #user profile loaded 
    """Complete input received by G1."""
    model_config = ConfigDict(extra="forbid")
    original_query: str = Field(min_length=1)
    learner_input: LearnerInput = Field(default_factory=LearnerInput)

# ============================================================
# 3. OUTPUT MODELS
# ============================================================

#goal
class TargetRole(BaseModel):
    model_config = ConfigDict(extra="forbid")
    raw_name: Optional[str] = None
    canonical_name: Optional[str] = None
    role_id: Optional[int] = None


class GoalOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    original_query: str
    target_role: TargetRole
    target_technologies: list[str] = Field(default_factory=list)
    goal_type: GoalType


#career_background
class CareerBackground(BaseModel):
    model_config = ConfigDict(extra="forbid")
    career_level: Optional[CareerLevel] = None
    current_job_title: Optional[str] = None
    industry: Optional[str] = None

    technical_domains: list[str] = Field(
        default_factory=list
    )
    certifications: list[str] = Field(
        default_factory=list
    )
    previous_job_roles: list[str] = Field(
        default_factory=list
    )

    relevant_it_work_experience: Optional[str] = None
#skills_profiles
class OutputSkillProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_name: str
    proficiency_level: Optional[ProficiencyLevel] = None
    experience_duration: Optional[str] = None
    evidence_type: EvidenceType
#practical experience 
class PracticalExperience(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str
    related_skills: list[str] = Field(
        default_factory=list
    )
    evidence_type: EvidenceType

#learning_contraints
class LearningConstraintsOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    available_study_time: Optional[AvailableStudyTime] = None
    deadline: Optional[Deadline] = None

#output profiles

class ClarificationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    question: str
    options: Optional[list[str]] = None
class G1Output(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal: GoalOutput
    career_background: CareerBackground
    skill_profiles: list[OutputSkillProfile] = Field(
        default_factory=list
    )
    status: G1Status
    practical_experience: list[PracticalExperience] = Field(
        default_factory=list
    )
    learning_constraints: LearningConstraintsOutput
    clarification_required: list[ClarificationItem] = Field(
        default_factory=list
    )
    unknown_fields: list[str] = Field(default_factory=list)

# ============================================================
# 4. DATASET MODELS
# ============================================================

class G1Metadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_type: str
    difficulty: str

#compose of input and output
class G1DatasetSample(BaseModel):
    """One manually annotated G1 benchmark sample."""

    model_config = ConfigDict(extra="forbid")
    sample_id: str
    input: G1Input
    expected_output: G1Output
    metadata: G1Metadata


# ============================================================
# 5. NORMALIZED OUTPUT MODELS (Phase 3)
# ============================================================
# Produced by Python after G1Output passes validation.
# Qwen never generates these models. They keep the same top-level
# structure as G1Output and add canonical names and database IDs
# next to the original extracted wording, which is never overwritten.

class MatchMethod(str, Enum):
    EXACT = "exact"          # exact canonical name (case/space-insensitive)
    ALIAS = "alias"          # exact match on a registered alias
    FUZZY = "fuzzy"          # string similarity above the configured threshold
    SEMANTIC = "semantic"    # Qdrant embedding similarity above the threshold


class ResolutionStatus(str, Enum):
    MATCHED = "matched"        # exactly one reliable candidate
    AMBIGUOUS = "ambiguous"    # several candidates, none accepted automatically
    UNRESOLVED = "unresolved"  # no sufficiently reliable candidate


class EntityMatch(BaseModel):
    """Shared matching result fields.

    canonical_id refers to the reference dataset (job roles,
    industries, technical domains, certifications).
    match_score is the raw score of the method used (string or
    embedding similarity). It is NOT a probability of correctness.
    """
    model_config = ConfigDict(extra="forbid")

    raw_name: str
    canonical_name: Optional[str] = None
    canonical_id: Optional[int] = None
    match_method: Optional[MatchMethod] = None
    match_score: Optional[float] = None
    resolution_status: ResolutionStatus
    candidate_ids: list[int] = Field(default_factory=list)  # filled when ambiguous


class SkillLink(BaseModel):
    """A skill name resolved against the Skills table (skills.skill_id)."""
    model_config = ConfigDict(extra="forbid")

    raw_name: str
    skill_id: Optional[int] = None
    canonical_name: Optional[str] = None
    match_method: Optional[MatchMethod] = None
    match_score: Optional[float] = None
    resolution_status: ResolutionStatus
    candidate_ids: list[int] = Field(default_factory=list)


class NormalizedTargetRole(BaseModel):
    """TargetRole after Python fills canonical_name and role_id."""
    model_config = ConfigDict(extra="forbid")

    raw_name: Optional[str] = None
    canonical_name: Optional[str] = None
    role_id: Optional[int] = None
    match_method: Optional[MatchMethod] = None
    match_score: Optional[float] = None
    resolution_status: Optional[ResolutionStatus] = None  # null when raw_name is null


class NormalizedGoal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    original_query: str
    target_role: NormalizedTargetRole
    target_technologies: list[SkillLink] = Field(default_factory=list)
    goal_type: GoalType


class NormalizedCareerBackground(BaseModel):
    model_config = ConfigDict(extra="forbid")

    career_level: Optional[CareerLevel] = None  # already a controlled enum
    current_job_title: Optional[EntityMatch] = None
    industry: Optional[EntityMatch] = None
    technical_domains: list[EntityMatch] = Field(default_factory=list)
    certifications: list[EntityMatch] = Field(default_factory=list)
    previous_job_roles: list[EntityMatch] = Field(default_factory=list)
    relevant_it_work_experience: Optional[str] = None


class LinkedSkillProfile(BaseModel):
    """OutputSkillProfile plus its Skills-table link."""
    model_config = ConfigDict(extra="forbid")

    skill_name: str                      # original extracted wording
    proficiency_level: Optional[ProficiencyLevel] = None
    experience_duration: Optional[str] = None
    evidence_type: EvidenceType
    link: SkillLink


class NormalizedPracticalExperience(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str
    related_skills: list[SkillLink] = Field(default_factory=list)
    evidence_type: EvidenceType


class NormalizedG1Output(BaseModel):
    """G1Output enriched by Phase 3 normalization and skill linking."""
    model_config = ConfigDict(extra="forbid")

    goal: NormalizedGoal
    career_background: NormalizedCareerBackground
    skill_profiles: list[LinkedSkillProfile] = Field(default_factory=list)
    status: G1Status
    practical_experience: list[NormalizedPracticalExperience] = Field(
        default_factory=list
    )
    learning_constraints: LearningConstraintsOutput
    clarification_required: list[ClarificationItem] = Field(
        default_factory=list
    )
    unknown_fields: list[str] = Field(default_factory=list)


class ProcessingMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    model_name: str
    adapter_version: Optional[str] = None   # null when the base model is used
    prompt_version: str
    schema_version: str
    reference_data_version: Optional[str] = None
    skill_catalogue_version: Optional[str] = None
    retry_count: int = 0
    duration_ms: Optional[int] = None


class G1ParseResponse(NormalizedG1Output):
    """Response body of POST /api/ai/parse-learner-profile.

    Same top-level fields as G1Output (status and
    clarification_required stay at the top level), plus
    processing_metadata. Errors are returned as HTTP errors,
    not inside this body.
    """
    processing_metadata: ProcessingMetadata