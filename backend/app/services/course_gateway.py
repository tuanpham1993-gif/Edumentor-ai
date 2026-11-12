"""Cổng nối module 09 (Ôn tập) với module Theo dõi khóa học (`user_courses`).

Module 09 KHÔNG đọc/ghi thẳng bảng `user_courses` — chỉ đi qua 2 hàm dưới đây:
  - `get_enrollment_status`: ánh xạ `ongoing` -> `IN_PROGRESS`, `completed` -> `COMPLETED`,
    `abandoned` -> `ABANDONED`, `bookmarked` / chưa có bản ghi -> `None`.
  - `mark_course_completed`: chuyển `ongoing` -> `completed`, CHỈ `db.flush()` để module 09
    commit/rollback chung trong cùng transaction nộp bài.
"""

from sqlalchemy.orm import Session

from app.services import course_tracking_service

IN_PROGRESS = "in_progress"  # đang học (ánh xạ từ user_courses.status == 'ongoing')
COMPLETED = "completed"  # đã hoàn thành (chỉ do module 09 đặt khi đạt ôn tập — B1)
ABANDONED = "abandoned"  # đã bỏ khóa

_STATUS_TO_GATEWAY = {
    "ongoing": IN_PROGRESS,
    "completed": COMPLETED,
    "abandoned": ABANDONED,
}


def get_enrollment_status(db: Session, user_id: int, course_id: int) -> str | None:
    """Trạng thái đăng ký khóa của người dùng; None = chưa tham gia (gồm bookmarked)."""
    raw_status = course_tracking_service.get_tracking_status_value(
        db, user_id, course_id
    )
    if raw_status is None:
        return None
    return _STATUS_TO_GATEWAY.get(raw_status)


def mark_course_completed(db: Session, user_id: int, course_id: int) -> None:
    """Chuyển khóa sang Hoàn thành — CHỈ flush, module 09 commit chung (GĐ3)."""
    course_tracking_service.mark_course_completed_in_tx(db, user_id, course_id)
