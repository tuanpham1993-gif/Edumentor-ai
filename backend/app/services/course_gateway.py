"""Cổng nối module 09 (Ôn tập) với module Theo dõi khóa học của Khôi (`user_courses`)
(Tuấn · GĐ2, 09/11/2026; nối hàm thật của Khôi 12/11).

Module 09 KHÔNG đọc/ghi thẳng bảng `user_courses` — chỉ đi qua 2 hàm dưới đây (đặc tả 6a:
BA-nhom/Gui-Khoi-On-tap-09-va-Khoa-hoc.md), gọi sang `course_tracking_service` của Khôi:
  - get_enrollment_status: 'ongoing' | 'completed' | 'abandoned'; 'bookmarked' (mới lưu, chưa tham gia)
    hoặc chưa có bản ghi → None (không cho ôn).
  - mark_course_completed: 'ongoing' → 'completed' + completed_at, CHỈ flush — module 09 commit/rollback
    chung trong transaction nộp bài (B1). Hàm của Khôi im lặng khi khóa không 'ongoing' → cổng tự đọc lại,
    chưa 'completed' thì báo EnrollmentChangedError (lỗi L1 — bỏ khóa đúng lúc đang chấm).
"""

from sqlalchemy.orm import Session

from app.services import course_tracking_service

# Giá trị trạng thái đúng như cột user_courses.status của Khôi
IN_PROGRESS = "ongoing"  # đang học
COMPLETED = "completed"  # đã hoàn thành (chỉ do module 09 đặt khi đạt ôn tập — B1)
ABANDONED = "abandoned"  # đã bỏ khóa
BOOKMARKED = "bookmarked"  # mới lưu khóa, chưa tham gia → không được ôn

_ENROLLED = (IN_PROGRESS, COMPLETED, ABANDONED)


class EnrollmentChangedError(Exception):
    """Trạng thái khóa vừa đổi giữa lúc chấm (vd người học bấm "Bỏ khóa") → không chuyển Hoàn thành được.
    review_service rollback cả lần nộp; router trả 409 để người học nộp lại."""


def count_courses(db: Session, user, status: str) -> int:
    """Số khóa của người dùng ở một trạng thái (ongoing / completed …) — cho ô thống kê trang Hồ sơ (7.2).
    Dùng `list_my_courses` của Khôi (đã có `total`), lấy 1 dòng để chỉ đọc tổng."""
    return course_tracking_service.list_my_courses(db, user, status_filter=status, page_size=1)["total"]


def get_enrollment_status(db: Session, user_id: int, course_id: int) -> str | None:
    """Trạng thái tham gia khóa của người dùng; None = chưa tham gia (kể cả mới bookmarked)."""
    raw_status = course_tracking_service.get_tracking_status_value(db, user_id, course_id)
    return raw_status if raw_status in _ENROLLED else None


def mark_course_completed(db: Session, user_id: int, course_id: int) -> None:
    """Chuyển khóa sang Hoàn thành — CHỈ flush, module 09 commit chung (GĐ3)."""
    course_tracking_service.mark_course_completed_in_tx(db, user_id, course_id)
    status = course_tracking_service.get_tracking_status_value(db, user_id, course_id)
    if status != COMPLETED:
        raise EnrollmentChangedError(f"Khóa {course_id} đang '{status}', không chuyển Hoàn thành được")
