"""Model bảng `notifications` — thông báo trong app (chuông trên header) (module 01 · Tuấn · 11/11/2026).

Mỗi dòng = một thông báo gửi tới MỘT người dùng.
  - type: loại thông báo (TYPES) — frontend chọn icon / màu theo loại.
  - title, body: CHỮ THUẦN (không HTML) — frontend hiển thị dạng text.
  - link: đường dẫn NỘI BỘ khi bấm (bắt đầu bằng "/"), vd /review/27/result.
  - source_id: mã đối tượng gây ra thông báo (attempt_id, course_id…) → chống tạo trùng.
KHÔNG lưu mật khẩu, token, link đặt lại mật khẩu, nội dung bài làm.
Module khác KHÔNG ghi thẳng bảng này — gọi services/notification_service.notify().
"""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)

from app.core.database import Base

# Chốt 11/11 (Tuấn). Module khác cần loại mới → thêm vào đây (CHECK tạo cùng bảng).
TYPES = ("review_graded", "course_completed", "password_changed", "welcome")


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),  # xóa tài khoản → xóa thông báo
        nullable=False,
    )
    type = Column(String(40), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=True)
    link = Column(String(500), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False, server_default="false")
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source_id = Column(Integer, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "type IN (" + ", ".join(f"'{t}'" for t in TYPES) + ")",
            name="ck_notifications_type",
        ),
        CheckConstraint("link IS NULL OR link LIKE '/%'", name="ck_notifications_link_internal"),
        # Chuông hỏi số chưa đọc ~60 giây/lần + danh sách mới nhất → index theo đúng truy vấn đó
        Index("ix_notifications_user_read_created", "user_id", "is_read", "created_at"),
        # Một đối tượng chỉ sinh MỘT thông báo mỗi loại (vd 1 lượt ôn tập → 1 "kết quả ôn tập")
        Index(
            "uq_notifications_source",
            "user_id",
            "type",
            "source_id",
            unique=True,
            postgresql_where=text("source_id IS NOT NULL"),
            sqlite_where=text("source_id IS NOT NULL"),
        ),
    )
