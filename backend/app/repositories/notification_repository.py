"""Repository bảng `notifications` (module 01 · Tuấn · 11/11/2026). Chỉ truy vấn — KHÔNG commit."""

from datetime import datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.models.notification import Notification


def exists_for_source(db: Session, user_id: int, type_: str, source_id: int) -> bool:
    return (
        db.scalar(
            select(Notification.notification_id).where(
                Notification.user_id == user_id,
                Notification.type == type_,
                Notification.source_id == source_id,
            )
        )
        is not None
    )


def add(db: Session, notification: Notification) -> Notification:
    db.add(notification)
    db.flush()
    return notification


def list_for_user(
    db: Session, user_id: int, *, unread_only: bool, offset: int, limit: int
) -> list[Notification]:
    query = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        query = query.where(Notification.is_read.is_(False))
    query = query.order_by(Notification.created_at.desc(), Notification.notification_id.desc())
    return list(db.scalars(query.offset(offset).limit(limit)))


def count(db: Session, user_id: int, *, unread_only: bool) -> int:
    query = select(func.count()).select_from(Notification).where(Notification.user_id == user_id)
    if unread_only:
        query = query.where(Notification.is_read.is_(False))
    return db.scalar(query)


def get_owned(db: Session, user_id: int, notification_id: int) -> Notification | None:
    return db.scalar(
        select(Notification).where(
            Notification.notification_id == notification_id, Notification.user_id == user_id
        )
    )


def mark_all_read(db: Session, user_id: int, now: datetime) -> int:
    result = db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True, read_at=now)
    )
    return result.rowcount


def prune(db: Session, user_id: int, *, older_than: datetime, keep: int) -> None:
    """Xóa thông báo cũ hơn `older_than` và phần vượt quá `keep` thông báo mới nhất."""
    db.execute(
        delete(Notification).where(
            Notification.user_id == user_id, Notification.created_at < older_than
        ).execution_options(synchronize_session="fetch")  # để DB tự lọc theo thời gian
    )
    keep_ids = select(Notification.notification_id).where(Notification.user_id == user_id).order_by(
        Notification.created_at.desc(), Notification.notification_id.desc()
    ).limit(keep)
    db.execute(
        delete(Notification).where(
            Notification.user_id == user_id,
            Notification.notification_id.not_in(keep_ids.scalar_subquery()),
        ).execution_options(synchronize_session="fetch")
    )
