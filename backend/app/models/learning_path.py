from sqlalchemy import (
    Column, Integer, String, Boolean,
    Text, CheckConstraint, ForeignKey,
)
from sqlalchemy.orm import relationship
from app.core.database import Base

class LearningPath(Base):
    __tablename__ = "learning_paths"

    record_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)
    original_query = Column(Text, nullable=False)
    goal_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)

    nodes = relationship("LearningPathNode",back_populates="learning_path",)
    edges = relationship("LearningPathEdge",back_populates="learning_path",)

    __table_args__ = (
        CheckConstraint("goal_type IN ('career', 'project')",name="ck_learning_path_goal_type",),
        CheckConstraint("status IN ('completed', 'ongoing', 'abandoned')",name="ck_learning_path_status",),
)


class LearningPathNode(Base):
    __tablename__ = "learning_path_nodes"

    path_id = Column(Integer, ForeignKey("learning_paths.record_id"), primary_key=True,)
    skill_id = Column( Integer, ForeignKey("skills.skill_id"), primary_key=True,)

    node_role = Column(String(30), nullable=True)
    is_target = Column(Boolean, nullable=False)
    added_by = Column(String(20), nullable=False)
    is_required = Column(Boolean, nullable=False)
    display_order = Column(Integer, nullable=False)

    learning_path = relationship("LearningPath",back_populates="nodes",)
    skill = relationship("Skills",back_populates="learning_path_nodes",)

    __table_args__ = (
        CheckConstraint("is_target IN (TRUE, FALSE)", name="ck_learning_path_node_is_target"),
        CheckConstraint("added_by IN ('system', 'user')",name="ck_learning_path_node_added_by"),
        CheckConstraint("is_required IN (TRUE, FALSE)",name="ck_learning_path_node_is_required"),
    )

class LearningPathEdge(Base):
    __tablename__ = "learning_path_edges"

    path_id = Column(Integer, ForeignKey("learning_paths.record_id"), primary_key=True,)
    from_skill_id = Column(Integer,ForeignKey("skills.skill_id"),primary_key=True,)
    to_skill_id = Column(Integer,ForeignKey("skills.skill_id"), primary_key=True,)

    relation_type = Column(String(20), nullable=False)

    learning_path = relationship("LearningPath",back_populates="edges",)
    from_skill = relationship("Skills",foreign_keys=[from_skill_id],back_populates="learning_path_edges_from",)
    to_skill = relationship("Skills",foreign_keys=[to_skill_id],back_populates="learning_path_edges_to",)

    __table_args__ = (
        CheckConstraint("relation_type IN ('prerequisite', 'related', 'extension')",name="ck_learning_path_edge_relation_type"),
        CheckConstraint("from_skill_id != to_skill_id",name="ck_learning_path_edge_different_skills"),
    )