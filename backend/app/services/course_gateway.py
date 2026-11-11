"""Cổng nối module 09 (Ôn tập) với module Khóa học của Hòa (Tuấn · GĐ2, 09/11/2026).

Module 09 KHÔNG đọc/ghi thẳng bảng đăng ký khóa học của Hòa — chỉ đi qua 2 hàm dưới đây
(đặc tả đã gửi Hòa: BA-nhom/Gui-Hoa-On-tap-09-va-Khoa-hoc.md, chốt 6a).

⚠️ TẠM THỜI LÀ HÀM GIẢ: nhánh hiện tại chưa có bảng đăng ký khóa học (models/user_course.py rỗng).
   - get_enrollment_status: coi như MỌI người dùng đang học mọi khóa → ôn tập được để code / demo.
   - mark_course_completed: không làm gì.
   Khi Hòa có hàm thật: CHỈ sửa file này (gọi sang service của Hòa, đổi tên trạng thái cho khớp),
   phần còn lại của module 09 giữ nguyên. Test giả lập các trạng thái bằng monkeypatch.
"""

from sqlalchemy.orm import Session

IN_PROGRESS = "in_progress"  # đang học
COMPLETED = "completed"  # đã hoàn thành (chỉ do module 09 đặt khi đạt ôn tập — B1)
ABANDONED = "abandoned"  # đã bỏ khóa


def get_enrollment_status(db: Session, user_id: int, course_id: int) -> str | None:
    """Trạng thái đăng ký khóa của người dùng; None = chưa đăng ký."""
    return IN_PROGRESS  # TODO(Hòa): thay bằng hàm thật của module khóa học


def mark_course_completed(db: Session, user_id: int, course_id: int) -> None:
    """Chuyển khóa sang Hoàn thành — CHỈ flush, module 09 commit chung (GĐ3)."""
    # TODO(Hòa): thay bằng hàm thật của module khóa học — hiện chưa làm gì
