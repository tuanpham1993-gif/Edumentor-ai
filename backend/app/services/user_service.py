from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import Users


class WrongCurrentPasswordError(Exception):
    """Mật khẩu hiện tại nhập vào không đúng."""


def update_profile(db: Session, user: Users, *, full_name: str) -> Users:
    """Sửa họ tên (FR-03). Email và vai trò không đổi được."""
    user.full_name = full_name
    db.commit()
    db.refresh(user)
    return user


def change_password(
    db: Session, user: Users, *, current_password: str, new_password: str
) -> None:
    """Đổi mật khẩu (FR-48). Sai mật khẩu hiện tại → WrongCurrentPasswordError."""
    if not verify_password(current_password, user.hashed_password):
        raise WrongCurrentPasswordError

    user.hashed_password = hash_password(new_password)
    db.commit()
