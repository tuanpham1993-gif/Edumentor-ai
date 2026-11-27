"""Learner profile snapshot saved with each learning path (one table).

One learner_profiles row per learning path (path_id -> learning_paths.record_id, unique).
It stores the normalized G1 result the path was generated from: goal, career background,
skills, target technologies, practical experience and learning constraints. The course
recommender and later steps read the learner context from here.

This is a per-path snapshot, not the user's account profile (user_profiles / user_skills
belong to module 01). Two paths of the same user can have different snapshots.

List fields are JSON (shapes in app/schemas/learner_profile.py):
    target_technologies   [{raw_name, skill_id}]
    skill_profiles        [{raw_skill_name, skill_id, proficiency_level, experience_duration, evidence_type}]
    practical_experiences [{description, related_skills: [{raw_name, skill_id}], evidence_type}]
skill_id is null when the name could not be linked to the skills table; the raw name is always kept.
Value lists mirror app/utils/learner_analyzer/schemas.py.
"""
from sqlalchemy import (
    JSON,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import backref, relationship

from app.core.database import Base

CAREER_LEVELS = ("beginner", "intern", "fresher", "junior", "middle", "senior",
                 "lead", "architect", "manager", "career_switcher", "student")


def _in(col: str, values: tuple[str, ...]) -> str:
    return f"{col} IN (" + ", ".join(f"'{v}'" for v in values) + ")"


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    path_id = Column(Integer, ForeignKey("learning_paths.record_id", ondelete="CASCADE"),
                     nullable=False, unique=True)

    # goal
    original_query = Column(Text, nullable=False)
    goal_type = Column(String(20), nullable=False)
    target_role_raw = Column(String(255), nullable=True)    # wording extracted by G1
    role_id = Column(Integer, nullable=True, index=True)    # job role id in Qdrant (edumentor_job_roles), after matching
    role_name = Column(String(150), nullable=True)          # canonical role name at generation time
    target_technologies = Column(JSON, nullable=False, default=list)

    # career background
    career_level = Column(String(30), nullable=True)
    current_job_title = Column(String(255), nullable=True)
    industry = Column(String(255), nullable=True)
    relevant_it_work_experience = Column(String(50), nullable=True)
    technical_domains = Column(JSON, nullable=False, default=list)      # list[str]
    certifications = Column(JSON, nullable=False, default=list)         # list[str], held only
    previous_job_roles = Column(JSON, nullable=False, default=list)     # list[str]

    # existing skills and practical experience
    skill_profiles = Column(JSON, nullable=False, default=list)
    practical_experiences = Column(JSON, nullable=False, default=list)

    # learning constraints
    study_time_value = Column(Float, nullable=True)
    study_time_unit = Column(String(10), nullable=True)                 # hours | minutes
    study_time_period = Column(String(10), nullable=True)               # per_day | per_week
    deadline_type = Column(String(20), nullable=True)                   # fixed_date | relative_duration
    deadline_target_date = Column(Date, nullable=True)
    deadline_duration_value = Column(Float, nullable=True)
    deadline_duration_unit = Column(String(10), nullable=True)          # days | weeks | months | years

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # LearningPath.learner_profile is added by this backref (one profile per path)
    learning_path = relationship(
        "LearningPath",
        backref=backref("learner_profile", uselist=False, cascade="all, delete-orphan", passive_deletes=True),
    )

    __table_args__ = (
        CheckConstraint("goal_type IN ('career', 'project')", name="ck_learner_profiles_goal_type"),
        CheckConstraint("career_level IS NULL OR " + _in("career_level", CAREER_LEVELS),
                        name="ck_learner_profiles_career_level"),
        CheckConstraint(
            "(study_time_value IS NULL AND study_time_unit IS NULL AND study_time_period IS NULL) OR "
            "(study_time_value > 0 AND study_time_unit IN ('hours', 'minutes') "
            "AND study_time_period IN ('per_day', 'per_week'))",
            name="ck_learner_profiles_study_time",
        ),
        CheckConstraint(
            "(deadline_type IS NULL AND deadline_target_date IS NULL "
            " AND deadline_duration_value IS NULL AND deadline_duration_unit IS NULL) OR "
            "(deadline_type = 'fixed_date' AND deadline_target_date IS NOT NULL "
            " AND deadline_duration_value IS NULL AND deadline_duration_unit IS NULL) OR "
            "(deadline_type = 'relative_duration' AND deadline_target_date IS NULL "
            " AND deadline_duration_value > 0 "
            " AND deadline_duration_unit IN ('days', 'weeks', 'months', 'years'))",
            name="ck_learner_profiles_deadline",
        ),
    )
