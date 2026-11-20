"""Bảng `review_due_reminders` — nhắc "Đến hạn ôn" đã gửi (module 09 · Tuấn · 21/11/2026, Q12 guide.md).

Mỗi dòng = một lần MỘT kỹ năng của MỘT người dùng đến hạn ôn (due_at). Dùng để KHÔNG nhắc lặp:
  - notified_at: đã gom vào thông báo chuông (NULL = chưa).
  - emailed_at:  đã gom vào email nhắc (NULL = chưa; email tối đa 1 lần / tuần, theo cài đặt "Nhắc ôn tập").
Ôn lại xong (đạt hay chưa) → hạn mới khác due_at → dòng mới khi tới hạn mới. Bảng MỚI nên create_all tự tạo,
không cần migration. Không lưu nội dung bài làm.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint, func

from app.core.database import Base


class ReviewDueReminder(Base):
    __tablename__ = "review_due_reminders"

    reminder_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.skill_id", ondelete="CASCADE"), nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=False)
    notified_at = Column(DateTime(timezone=True), nullable=True)
    emailed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "skill_id", "due_at", name="uq_review_due_reminders"),)
