"""Repository token: reset mật khẩu (GĐ5) và refresh token (GĐ6). Chỉ truy vấn, không commit."""

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.auth_token import PasswordResetToken, RefreshToken


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
        .where(
            PasswordResetToken.user_id == user_id, PasswordResetToken.used_at.is_(None)
        )
        .values(used_at=now)
    )


def create_refresh_token(
    db: Session, *, user_id: int, token_hash: str, expires_at: datetime
) -> RefreshToken:
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(refresh_token)
    db.flush()
    return refresh_token


def get_refresh_token_by_hash(db: Session, token_hash: str) -> RefreshToken | None:
    return db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))


def revoke_all_refresh_tokens(db: Session, user_id: int, now: datetime) -> None:
    """Thu hồi MỌI refresh token còn hiệu lực của user (đăng xuất mọi nơi)."""
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
