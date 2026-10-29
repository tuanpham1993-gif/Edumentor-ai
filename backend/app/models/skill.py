from sqlalchemy import Column, Integer, String
from app.core.database import Base
from sqlalchemy.orm import relationship
class Skills(Base):
    __tablename__ = "skills"

    skill_id = Column(Integer, primary_key=True, index=True)
    skill = Column(String(255), nullable=False)
    courses_info = relationship("Courses", secondary="course_skill", back_populates="skills_info", lazy="joined")

    relations_from = relationship("SkillRelation",foreign_keys="SkillRelation.from_skill_id",back_populates="from_skill",)
    relations_to = relationship("SkillRelation",foreign_keys="SkillRelation.to_skill_id",back_populates="to_skill",)
    
    learning_path_nodes = relationship("LearningPathNode",back_populates="skill",)
    learning_path_edges_from = relationship("LearningPathEdge",foreign_keys="LearningPathEdge.from_skill_id",back_populates="from_skill",)

    learning_path_edges_to = relationship("LearningPathEdge",foreign_keys="LearningPathEdge.to_skill_id",back_populates="to_skill",)