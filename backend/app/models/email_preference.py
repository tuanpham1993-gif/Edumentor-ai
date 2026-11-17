"""Model bảng `email_preferences` — người dùng chọn nhận loại email nào (module 01 · Tuấn · 11/11/2026).

Một dòng / người dùng. CHƯA có dòng = dùng mặc định (DEFAULTS) — không cần tạo dòng lúc đăng ký.
Bảng RIÊNG (không thêm cột vào `users`): repo tạo bảng bằng create_all(), lệnh này KHÔNG thêm cột
vào bảng đã có → thêm cột vào users sẽ không chạy trên DB của nhóm.

Chỉ áp dụng cho email "tin tức / nhắc nhở". Email BẢO MẬT (quên mật khẩu, mật khẩu vừa đổi) và email
kết quả ôn tập luôn gửi, không tắt được.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, func

from app.core.database import Base

# Mặc định theo màn thiết kế Tuấn gửi 11/11
DEFAULTS = {
    "review_reminder": True,  # Nhắc ôn tập đến hạn — tối đa 1 email / tuần
    "course_suggestions": False,  # Khóa học gợi ý mới cho lộ trình
    "feedback_replies": True,  # Phản hồi góp ý (quản trị viên trả lời)
}


class EmailPreference(Base):
    __tablename__ = "email_preferences"

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),  # xóa tài khoản → xóa tùy chọn
        primary_key=True,
    )
    review_reminder = Column(Boolean, nullable=False, default=True, server_default="true")
    course_suggestions = Column(Boolean, nullable=False, default=False, server_default="false")
    feedback_replies = Column(Boolean, nullable=False, default=True, server_default="true")
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
