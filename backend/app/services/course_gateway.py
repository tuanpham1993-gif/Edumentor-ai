"""Cổng nối module 09 (Ôn tập) với module Khóa học của Khôi (Tuấn · GĐ2, 09/11/2026; đính chính 11/11).

Module 09 KHÔNG đọc/ghi thẳng bảng đăng ký khóa học của Khôi — chỉ đi qua 2 hàm dưới đây
(đặc tả đã gửi Khôi: BA-nhom/Gui-Khoi-On-tap-09-va-Khoa-hoc.md, chốt 6a).

Khôi trả lời 11/11 (Q12): bảng `student_courses`, cột `status`, giá trị
'bookmarked' | 'ongoing' | 'completed' | 'abandoned'; 2 hàm thật sẽ nằm trong
`services/course_tracking_service.py` (hẹn trước 12/11). 'bookmarked' = mới lưu khóa, CHƯA đăng ký
→ module 09 coi như chưa tham gia (không cho ôn).

⚠️ TẠM THỜI LÀ HÀM GIẢ: nhánh hiện tại chưa có bảng đăng ký khóa học (models/user_course.py rỗng).
   - get_enrollment_status: coi như MỌI người dùng đang học mọi khóa → ôn tập được để code / demo.
   - mark_course_completed: không làm gì.
   Khi Khôi có hàm thật: CHỈ sửa file này (gọi sang course_tracking_service),
   phần còn lại của module 09 giữ nguyên. Test giả lập các trạng thái bằng monkeypatch.
"""

from sqlalchemy.orm import Session

# Giá trị trạng thái đúng như bảng student_courses của Khôi (Q12, 11/11)
IN_PROGRESS = "ongoing"  # đang học
COMPLETED = "completed"  # đã hoàn thành (chỉ do module 09 đặt khi đạt ôn tập — B1)
ABANDONED = "abandoned"  # đã bỏ khóa
BOOKMARKED = "bookmarked"  # mới lưu khóa, chưa đăng ký → không được ôn


def get_enrollment_status(db: Session, user_id: int, course_id: int) -> str | None:
    """Trạng thái đăng ký khóa của người dùng; None = chưa đăng ký."""
    return IN_PROGRESS  # TODO(Khôi): thay bằng course_tracking_service.get_enrollment_status


def mark_course_completed(db: Session, user_id: int, course_id: int) -> None:
    """Chuyển khóa sang Hoàn thành — CHỈ flush, module 09 commit chung (GĐ3)."""
    # TODO(Khôi): thay bằng course_tracking_service.mark_course_completed — hiện chưa làm gì
