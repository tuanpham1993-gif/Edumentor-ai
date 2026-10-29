from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base

class CourseSkill(Base):
    __tablename__ = "course_skill"
    
    course_id = Column(Integer, ForeignKey("courses.course_id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.skill_id"), primary_key=True)

