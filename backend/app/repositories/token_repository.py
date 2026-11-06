"""Repository token: reset mật khẩu (GĐ5) — refresh token thêm ở GĐ6."""

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.auth_token import PasswordResetToken


def create_reset_token(
    db: Session, *, user_id: int, token_hash: str, expires_at: datetime
) -> PasswordResetToken:
    reset_token = PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(reset_token)
    db.flush()  # có id ngay, nhưng chưa commit — service sẽ commit
    return reset_token


def get_reset_token_by_hash(db: Session, token_hash: str) -> PasswordResetToken | None:
    return db.scalar(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )


def invalidate_unused_reset_tokens(db: Session, user_id: int, now: datetime) -> None:
    """Đánh dấu MỌI token chưa dùng của user là đã dùng (vô hiệu link cũ).

    SQL: UPDATE password_reset_tokens SET used_at = :now
         WHERE user_id = :user_id AND used_at IS NULL
    """
    db.execute(
        update(PasswordResetToken)
        .where(PasswordResetToken.user_id == user_id, PasswordResetToken.used_at.is_(None))
        .values(used_at=now)
    )
