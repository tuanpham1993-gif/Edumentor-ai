"""API thông báo — chuông trên header (module 01 · Tuấn · 11/11/2026). Prefix /api/me/notifications.

    GET   /api/me/notifications?unread_only=&page=&size=  — danh sách (tab Tất cả / Chưa đọc) + số chưa đọc
    GET   /api/me/notifications/unread-count               — số chưa đọc (frontend hỏi ~60 giây/lần)
    PATCH /api/me/notifications/{id}/read                  — đánh dấu một thông báo đã đọc
    POST  /api/me/notifications/read-all                   — đánh dấu tất cả đã đọc
Chỉ thấy / sửa thông báo của CHÍNH mình; của người khác → 404.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import Users
from app.schemas.notification import (
    MarkAllReadOut,
    NotificationOut,
    NotificationPage,
    UnreadCountOut,
)
from app.services import notification_service

router = APIRouter()


@router.get("", response_model=NotificationPage, summary="Thông báo của tôi (lọc ?unread_only=true)")
def read_notifications(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return notification_service.list_notifications(
        db, current_user.user_id, unread_only=unread_only, page=page, size=size
    )


@router.get("/unread-count", response_model=UnreadCountOut, summary="Số thông báo chưa đọc")
def read_unread_count(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"unread_count": notification_service.unread_count(db, current_user.user_id)}


@router.patch("/{notification_id}/read", response_model=NotificationOut, summary="Đánh dấu đã đọc")
def mark_notification_read(
    notification_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return notification_service.mark_read(db, current_user.user_id, notification_id)
    except notification_service.NotificationNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy thông báo.") from None


@router.post("/read-all", response_model=MarkAllReadOut, summary="Đánh dấu tất cả đã đọc")
def mark_all_notifications_read(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"updated": notification_service.mark_all_read(db, current_user.user_id)}
