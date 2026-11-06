"""Nghiệp vụ hồ sơ người dùng (module 01 · Tuấn · GĐ3, 06/11/2026).

Không cần repository ở đây: `user` đã được lấy từ DB trong get_current_user.
Chỉ cần sửa thuộc tính rồi commit — SQLAlchemy tự theo dõi object bị sửa và
tự sinh câu UPDATE users SET ... WHERE user_id = ...
"""

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import Users


class WrongCurrentPasswordError(Exception):
    """Mật khẩu hiện tại nhập vào không đúng."""


def update_profile(db: Session, user: Users, *, full_name: str) -> Users:
    """Sửa họ tên (FR-03). Email và vai trò không đổi được."""
    user.full_name = full_name
    db.commit()  # SQLAlchemy tự gửi UPDATE
    db.refresh(user)  # đọc lại updated_at mới do DB điền
    return user


def change_password(
    db: Session, user: Users, *, current_password: str, new_password: str
) -> None:
    """Đổi mật khẩu (FR-48). Sai mật khẩu hiện tại → WrongCurrentPasswordError.

    Lưu ý: access token cũ vẫn dùng được tới khi hết hạn (JWT không thu hồi được);
    có hủy các phiên khác khi đổi mật khẩu không là câu hỏi Q10 (GĐ6 refresh token).
    """
    # Phải nhập đúng mật khẩu hiện tại — chặn người khác dùng máy đang đăng nhập để đổi.
    if not verify_password(current_password, user.hashed_password):
        raise WrongCurrentPasswordError  # nhập sai → không đổi gì cả

    user.hashed_password = hash_password(new_password)  # vẫn chỉ lưu bản băm
    db.commit()
