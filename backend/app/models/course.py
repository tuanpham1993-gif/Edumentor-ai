from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, ForeignKey,
    Integer, Numeric, String, Text, func,
)
from app.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, Float


class Courses(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)

    num_enrolled = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)
    num_reviews = Column(Integer, nullable=True)

    instructor = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)

    description = Column(Text, nullable=True)
    modules = Column(String(100), nullable=True)
    level = Column(String(20), nullable=True)
    schedule = Column(String(255), nullable=True)

    url = Column(String(500), nullable=True)
    image = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (CheckConstraint("rating >= 0 AND rating <= 5", name="ck_course_rating_range"),)

    skills_info = relationship("Skills", secondary="course_skill", back_populates="courses_info", lazy="joined")