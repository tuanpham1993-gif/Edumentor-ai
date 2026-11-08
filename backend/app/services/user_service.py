"""Nghiệp vụ hồ sơ người dùng (module 01 · Tuấn · GĐ3 06/11; ảnh đại diện GĐ7 07/11).

Không cần repository ở đây: `user` đã được lấy từ DB trong get_current_user.
Chỉ cần sửa thuộc tính rồi commit — SQLAlchemy tự theo dõi object bị sửa và
tự sinh câu UPDATE users SET ... WHERE user_id = ...
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import Users
from app.repositories import token_repository
from app.utils import files


class WrongCurrentPasswordError(Exception):
    """Mật khẩu hiện tại nhập vào không đúng."""


class SamePasswordError(Exception):
    """Mật khẩu mới trùng mật khẩu hiện tại (08/11)."""


def update_profile(db: Session, user: Users, *, full_name: str) -> Users:
    """Sửa họ tên (FR-03). Email và vai trò không đổi được."""
    user.full_name = full_name
    db.commit()  # SQLAlchemy tự gửi UPDATE
    db.refresh(user)  # đọc lại updated_at mới do DB điền
    return user


def change_password(
    db: Session, user: Users, *, current_password: str, new_password: str
) -> None:
    """Đổi mật khẩu (FR-48). Sai mật khẩu hiện tại → WrongCurrentPasswordError;
    mật khẩu mới trùng mật khẩu cũ → SamePasswordError.

    Lưu ý: access token cũ vẫn dùng được tới khi hết hạn (JWT không thu hồi được);
    đổi mật khẩu thì thu hồi mọi refresh token của user (Q10, GĐ6).
    """
    # Phải nhập đúng mật khẩu hiện tại — chặn người khác dùng máy đang đăng nhập để đổi.
    if not verify_password(current_password, user.hashed_password):
        raise WrongCurrentPasswordError  # nhập sai → không đổi gì cả

    # Mật khẩu mới trùng mật khẩu đang dùng → không đổi (08/11).
    # Đặt SAU bước kiểm mật khẩu hiện tại: người chưa biết mật khẩu không dò được qua lỗi này.
    if verify_password(new_password, user.hashed_password):
        raise SamePasswordError

    user.hashed_password = hash_password(new_password)  # vẫn chỉ lưu bản băm
    # Q10: đổi mật khẩu → đăng xuất mọi nơi (kể cả phiên hiện tại khi access hết hạn)
    token_repository.revoke_all_refresh_tokens(
        db, user.user_id, datetime.now(timezone.utc)
    )
    db.commit()


def update_avatar(db: Session, user: Users, *, data: bytes) -> Users:
    """Lưu ảnh mới, cập nhật avatar_url, xóa ảnh cũ (FR-03).

    Lỗi kiểm tra → files.FileTooLargeError / files.UnsupportedImageError (router đổi thành 413 / 415).
    """
    old_url = user.avatar_url
    new_url = files.save_avatar(user.user_id, data)  # lưu file TRƯỚC
    try:
        user.avatar_url = new_url
        db.commit()
    except Exception:
        db.rollback()
        files.delete_avatar(new_url)  # DB lỗi → dọn file vừa lưu, không để rác
        raise
    files.delete_avatar(old_url)  # xóa ảnh cũ SAU KHI lưu DB thành công
    db.refresh(user)
    return user
