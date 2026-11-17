"""Model bảng `user_profiles` — thông tin cá nhân thêm của người dùng (module 01 · Tuấn · 12/11/2026).

Một dòng / người dùng (chưa nhập gì = chưa có dòng). Bảng RIÊNG, không thêm cột vào `users`:
repo tạo bảng bằng create_all(), lệnh này KHÔNG thêm cột vào bảng đã có.

Số CCCD là dữ liệu nhạy cảm:
  - citizen_id_encrypted : số đầy đủ ĐÃ MÃ HÓA (core/security.encrypt_pii) — không lưu dạng chữ thường
  - citizen_id_masked    : bản che để hiển thị, vd "345*********" (chỉ lộ 3 số đầu)
  - citizen_id_hash      : dấu vân tay HMAC một chiều → UNIQUE: một CCCD không dùng cho 2 tài khoản
  API KHÔNG BAO GIỜ trả số đầy đủ — chỉ trả bản che.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from app.core.database import Base

GENDERS = ("male", "female")  # Nam / Nữ (chốt 12/11)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),  # xóa tài khoản → xóa thông tin cá nhân
        primary_key=True,
    )
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    hometown = Column(String(100), nullable=True)  # Quê quán
    phone = Column(String(15), nullable=True)  # Số điện thoại, lưu dạng 0xxxxxxxxx
    citizen_id_encrypted = Column(Text, nullable=True)
    citizen_id_masked = Column(String(12), nullable=True)
    citizen_id_hash = Column(String(64), nullable=True, unique=True)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("gender IS NULL OR gender IN ('male', 'female')", name="ck_user_profiles_gender"),
    )
