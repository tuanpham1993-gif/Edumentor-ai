"""Thông báo trong app — chuông trên header (module 01 · Tuấn · 11/11/2026).

    notify(...)        — tạo thông báo. CHỈ FLUSH: gọi bên trong transaction của module khác,
                         module đó commit một lần (giống add_learning_from_course / mark_known).
    list_notifications — danh sách (tab "Tất cả" / "Chưa đọc") + số chưa đọc
    unread_count       — số chưa đọc (chuông hỏi ~60 giây/lần)
    mark_read / mark_all_read — đánh dấu đã đọc (service này commit)

Giữ tối đa KEEP_MAX thông báo / người và không quá KEEP_DAYS ngày — dọn ngay khi tạo thông báo mới.

Ví dụ module khác dùng (Khôi, Hòa, Tâm):
    from app.services import notification_service
    notification_service.notify(db, user_id, "course_recommended", "Có khóa học mới phù hợp", link="/courses/12")
    db.commit()   # module của bạn commit
(Loại mới phải thêm vào models/notification.TYPES.)
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.notification import TYPES, Notification
from app.repositories import notification_repository as repo

KEEP_MAX = 100  # tối đa 100 thông báo mỗi người (chốt 11/11)
KEEP_DAYS = 90  # và không quá 90 ngày


class NotificationNotFoundError(Exception):
    """Không có thông báo này HOẶC của người khác — trả 404 như nhau."""


def notify(
    db: Session,
    user_id: int,
    type_: str,
    title: str,
    *,
    body: str | None = None,
    link: str | None = None,
    source_id: int | None = None,
) -> Notification | None:
    """Tạo một thông báo (chỉ flush). Đã có thông báo cùng (loại, source_id) → bỏ qua, trả None."""
    if type_ not in TYPES:
        raise ValueError(f"Loại thông báo chưa khai báo: {type_}")
    if link is not None and not link.startswith("/"):
        raise ValueError("link phải là đường dẫn nội bộ, bắt đầu bằng '/'")
    if source_id is not None and repo.exists_for_source(db, user_id, type_, source_id):
        return None
    notification = repo.add(
        db,
        Notification(
            user_id=user_id,
            type=type_,
            title=title[:200],
            body=body,
            link=link,
            source_id=source_id,
        ),
    )
    repo.prune(db, user_id, older_than=datetime.now(UTC) - timedelta(days=KEEP_DAYS), keep=KEEP_MAX)
    return notification


def _item(n: Notification) -> dict:
    return {
        "notification_id": n.notification_id,
        "type": n.type,
        "title": n.title,
        "body": n.body,
        "link": n.link,
        "is_read": n.is_read,
        "created_at": n.created_at,
    }


def list_notifications(
    db: Session, user_id: int, *, unread_only: bool = False, page: int = 1, size: int = 20
) -> dict:
    items = repo.list_for_user(db, user_id, unread_only=unread_only, offset=(page - 1) * size, limit=size)
    return {
        "items": [_item(n) for n in items],
        "total": repo.count(db, user_id, unread_only=unread_only),
        "unread_count": repo.count(db, user_id, unread_only=True),
        "page": page,
        "size": size,
    }


def unread_count(db: Session, user_id: int) -> int:
    return repo.count(db, user_id, unread_only=True)


def mark_read(db: Session, user_id: int, notification_id: int) -> dict:
    notification = repo.get_owned(db, user_id, notification_id)
    if notification is None:
        raise NotificationNotFoundError
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(UTC)
        db.commit()
    return _item(notification)


def mark_all_read(db: Session, user_id: int) -> int:
    changed = repo.mark_all_read(db, user_id, datetime.now(UTC))
    db.commit()
    return changed
