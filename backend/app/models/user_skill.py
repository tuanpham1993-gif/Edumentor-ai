"""Model bảng `user_skills` — kỹ năng trong hồ sơ người dùng (module 01 · Tuấn · GĐ4, 08/11/2026).

Mỗi dòng = "người dùng X có kỹ năng Y ở trạng thái Z".
  - status: 'known' (đã biết) | 'learning' (đang học)                       — FR-04
  - source: kỹ năng vào hồ sơ từ đâu (chốt S5, 08/11):
        'manual' — người dùng tự thêm qua PATCH /api/me/skills
        'course' — bấm tham gia khóa học → các kỹ năng của khóa thành 'learning' (module khóa học)
        'review' — làm ĐẠT bài ôn tập → các kỹ năng của khóa thành 'known' (module 09)

Khóa chính KÉP (user_id, skill_id): một người – một kỹ năng chỉ có ĐÚNG MỘT dòng,
DB tự chặn trùng (không cần code kiểm tra).
Bảng `skills` là của Hòa (models/skill.py), khóa chính `skill_id`.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)

from app.core.database import Base

STATUSES = ("known", "learning")
SOURCES = ("manual", "course", "review")


class UserSkill(Base):
    __tablename__ = "user_skills"

    # Xóa user / xóa kỹ năng → các dòng liên quan tự xóa theo (ON DELETE CASCADE).
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    # index=True: tra "ai đang có kỹ năng Y" nhanh (khóa chính kép chỉ đánh index theo user_id trước).
    skill_id = Column(
        Integer,
        ForeignKey("skills.skill_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    status = Column(String(20), nullable=False)
    source = Column(
        String(20), nullable=False, default="manual", server_default="manual"
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # onupdate: đổi known ↔ learning thì thời gian cập nhật tự đổi theo.
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Ràng buộc ở tầng DB (giống ck_users_role): code có lỗi thì DB vẫn không cho lưu giá trị lạ.
    __table_args__ = (
        CheckConstraint(
            "status IN ('known', 'learning')", name="ck_user_skills_status"
        ),
        CheckConstraint(
            "source IN ('manual', 'course', 'review')", name="ck_user_skills_source"
        ),
    )
