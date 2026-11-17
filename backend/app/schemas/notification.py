"""Schema API thông báo (module 01 · Tuấn · 11/11/2026)."""

from datetime import datetime

from pydantic import BaseModel


class NotificationOut(BaseModel):
    notification_id: int
    type: str
    title: str
    body: str | None
    link: str | None
    is_read: bool
    created_at: datetime


class NotificationPage(BaseModel):
    items: list[NotificationOut]
    total: int  # tổng theo tab đang xem (Tất cả / Chưa đọc)
    unread_count: int  # số chưa đọc (hiện trên chuông)
    page: int
    size: int


class UnreadCountOut(BaseModel):
    unread_count: int


class MarkAllReadOut(BaseModel):
    updated: int
