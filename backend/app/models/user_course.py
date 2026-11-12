"""Model bảng `user_courses` — lưu khóa học và theo dõi trạng thái học tập của người dùng.

Mỗi dòng = một cặp (user_id, course_id) duy nhất với 4 trạng thái hợp lệ:
  - 'bookmarked': Đã lưu để học sau.
  - 'ongoing':    Người dùng đã tham gia khóa học bên ngoài.
  - 'completed':  Người dùng đã hoàn thành bài kiểm tra ôn tập (chỉ module 09 đặt khi đạt).
  - 'abandoned':  Người dùng đã ngừng theo dõi khóa học.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base

COURSE_STATUSES = ("bookmarked", "ongoing", "completed", "abandoned")


class UserCourse(Base):
    __tablename__ = "user_courses"

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    course_id = Column(
        Integer,
        ForeignKey("courses.course_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    status = Column(String(20), nullable=False)
    joined_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    course = relationship("Courses")

    __table_args__ = (
        CheckConstraint(
            "status IN ('bookmarked', 'ongoing', 'completed', 'abandoned')",
            name="ck_user_courses_status",
        ),
        Index(
            "ix_user_courses_user_status_updated",
            "user_id",
            "status",
            "updated_at",
        ),
    )
