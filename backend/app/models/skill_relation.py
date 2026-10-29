
from sqlalchemy import (
    Column, Integer,
    String, ForeignKey,
    CheckConstraint,
)
from app.core.database import Base
from sqlalchemy.orm import relationship

class SkillRelation(Base):
    __tablename__ = "skill_relation"

    from_skill_id = Column(Integer, ForeignKey("skills.skill_id"),primary_key=True,)
    to_skill_id = Column(Integer,ForeignKey("skills.skill_id"),primary_key=True,)
    relation_type = Column(String(20),nullable=False,)

    from_skill = relationship("Skills",foreign_keys=[from_skill_id],back_populates="relations_from")

    to_skill = relationship("Skills",foreign_keys=[to_skill_id],back_populates="relations_to")

    __table_args__ = (
        CheckConstraint(
            "relation_type IN ('prerequisite', 'related', 'extension')",
            name="ck_skill_relation_type",
        ),
        CheckConstraint(
            "from_skill_id != to_skill_id",
            name="ck_skill_relation_different_skills",
        ),
    )
