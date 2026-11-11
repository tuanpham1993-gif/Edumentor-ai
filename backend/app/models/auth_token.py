"""Bảng token của module 01 (Tuấn): chỉ lưu BẢN BĂM SHA-256, không lưu token gốc.

- PasswordResetToken (GĐ5, 06/11): link đặt lại mật khẩu, dùng 1 lần (used_at), hết hạn sau 30 phút.
- RefreshToken (GĐ6, 07/11): làm mới access token, xoay vòng; revoked_at = đã thu hồi.

Xóa user → token tự xóa theo (ForeignKey ... ondelete="CASCADE").
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)  # None = chưa dùng
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)  # None = còn hiệu lực
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
