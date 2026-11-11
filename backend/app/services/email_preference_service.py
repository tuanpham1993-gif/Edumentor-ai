"""Tùy chọn nhận email (module 01 · Tuấn · 11/11/2026).

    get_preferences(db, user_id)          — 3 công tắc (chưa lưu lần nào → mặc định)
    update_preferences(db, user_id, ...)  — đổi một phần hoặc tất cả (service này commit)
    wants_email(db, user_id, key)         — module GỬI email hỏi trước khi gửi

Module khác dùng (vd Khôi gửi email khóa gợi ý, nhắc ôn tập đến hạn, phản hồi góp ý):
    from app.services import email_preference_service
    if email_preference_service.wants_email(db, user_id, "course_suggestions"):
        send_email(...)
"""

from sqlalchemy.orm import Session

from app.models.email_preference import DEFAULTS, EmailPreference

KEYS = tuple(DEFAULTS)


def _row(db: Session, user_id: int) -> EmailPreference | None:
    return db.get(EmailPreference, user_id)


def get_preferences(db: Session, user_id: int) -> dict:
    row = _row(db, user_id)
    if row is None:
        return dict(DEFAULTS)
    return {key: getattr(row, key) for key in KEYS}


def update_preferences(db: Session, user_id: int, changes: dict) -> dict:
    """changes: chỉ các khóa trong KEYS (schema đã lọc). Chưa có dòng → tạo từ mặc định rồi áp thay đổi."""
    row = _row(db, user_id)
    if row is None:
        row = EmailPreference(user_id=user_id, **DEFAULTS)
        db.add(row)
    for key, value in changes.items():
        if key in KEYS:
            setattr(row, key, bool(value))
    db.commit()
    return get_preferences(db, user_id)


def wants_email(db: Session, user_id: int, key: str) -> bool:
    if key not in KEYS:
        raise ValueError(f"Loại email chưa khai báo: {key}")
    return get_preferences(db, user_id)[key]
