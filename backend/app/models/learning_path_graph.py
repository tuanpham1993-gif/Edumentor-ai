"""Generated learning graph saved with an AI learning path (one row per path).

learning_paths (+ learning_path_nodes / learning_path_edges) keep the editable path that the
existing screens use. This table keeps what the AI pipeline (G1 -> role/skill linking ->
prerequisite graph -> personalization) produced when the learner accepted the path, and links
it to the learner profile snapshot it was built from:

    learning_paths 1 ── 1 learner_profiles 1 ── 1 learning_path_graphs

JSON shapes (app/schemas/learning_path_generation_v2.py):
    targets      [{skill_id, skill_name, source: "role" | "technology"}]
    node_states  {"<skill_id>": "known" | "satisfied" | "learning" | "eligible" | "locked"}
    layer        {"<layer>": [skill_id, ...]}   (prerequisites first)
    warnings     [str]
"""
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import backref, relationship

from app.core.database import Base


class LearningPathGraph(Base):
    __tablename__ = "learning_path_graphs"

    graph_id = Column(Integer, primary_key=True, autoincrement=True)
    path_id = Column(Integer, ForeignKey("learning_paths.record_id", ondelete="CASCADE"),
                     nullable=False, unique=True)
    profile_id = Column(Integer, ForeignKey("learner_profiles.profile_id", ondelete="CASCADE"),
                        nullable=False, unique=True)

    role_id = Column(Integer, nullable=True)          # job role (Qdrant edumentor_job_roles) used for targets
    targets = Column(JSON, nullable=False, default=list)
    node_states = Column(JSON, nullable=False, default=dict)
    layer = Column(JSON, nullable=False, default=dict)
    retrieval_status = Column(String(20), nullable=False, default="complete")   # complete | incomplete
    warnings = Column(JSON, nullable=False, default=list)
    generator_version = Column(String(30), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    learning_path = relationship(
        "LearningPath",
        backref=backref("generated_graph", uselist=False, cascade="all, delete-orphan", passive_deletes=True),
    )
    learner_profile = relationship(
        "LearnerProfile",
        backref=backref("generated_graph", uselist=False, passive_deletes=True),
    )
