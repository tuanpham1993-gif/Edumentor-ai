from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    CheckConstraint,
    func
)

from app.core.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    # Khóa chính
    feedback_id = Column(Integer, primary_key=True, index=True)

    # Người gửi phản hồi
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )

    # Loại đối tượng phản hồi
    target_type = Column(String(10), nullable=False)

    # Khóa học được phản hồi
    course_id = Column(
        Integer,
        ForeignKey("course.course_id", ondelete="CASCADE"),
        nullable=True
    )

    # Kỹ năng được phản hồi
    skill_id = Column(
        Integer,
        ForeignKey("skill.skill_id", ondelete="RESTRICT"),
        nullable=True
    )

    # Loại phản hồi
    feedback_type = Column(String(100), nullable=True)

    # Tiêu đề phản hồi
    title = Column(String(255), nullable=True)

    # Nội dung phản hồi
    content = Column(Text, nullable=False)

    # Đường dẫn ảnh đính kèm
    image_url = Column(String(500), nullable=True)

    # Trạng thái xử lý
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending"
    )

    # Nội dung Admin trả lời
    admin_response = Column(Text, nullable=True)

    # Thời gian Admin phản hồi
    responded_at = Column(DateTime(timezone=True), nullable=True)

    # Trạng thái xóa
    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    # Thời gian xóa
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Thời gian gửi phản hồi
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Ràng buộc dữ liệu
    __table_args__ = (
        CheckConstraint(
            "target_type IN ('course', 'skill', 'system', 'other')",
            name="ck_feedback_target_type"
        ),
        CheckConstraint(
            """
            (
                target_type = 'course'
                AND course_id IS NOT NULL
                AND skill_id IS NULL
            )
            OR
            (
                target_type = 'skill'
                AND course_id IS NULL
                AND skill_id IS NOT NULL
            )
            OR
            (
                target_type IN ('system', 'other')
                AND course_id IS NULL
                AND skill_id IS NULL
            )
            """,
            name="ck_feedback_target"
        ),
        CheckConstraint(
            "target_type <> 'other' OR title IS NOT NULL",
            name="ck_feedback_other_title"
        ),
        CheckConstraint(
            "status IN ('pending', 'in_review', 'resolved', 'rejected')",
            name="ck_feedback_status"
        ),
    )
