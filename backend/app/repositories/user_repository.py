"""Repository bảng `users` (module 01 · Tuấn · GĐ2, 05/11/2026).

Lớp REPOSITORY = "thủ kho": CHỈ truy vấn / thêm dữ liệu, không chứa quy tắc nghiệp vụ,
và KHÔNG commit — service mới quyết định khi nào lưu hẳn.
  flush()  : gửi INSERT xuống DB, DB cấp user_id, nhưng còn hủy được bằng rollback()
  commit() : lưu vĩnh viễn (do service gọi)
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import Users


def get_by_email(db: Session, email: str) -> Users | None:
    # Tương đương SQL: SELECT * FROM users WHERE email = :email
    # db.scalar(...) lấy MỘT kết quả, hoặc None nếu không có.
    return db.scalar(select(Users).where(Users.email == email))


def get_by_id(db: Session, user_id: int) -> Users | None:
    return db.get(Users, user_id)  # tìm theo khóa chính


# Dấu `*`: bắt buộc gọi bằng tên tham số (email=..., full_name=...) → không truyền nhầm thứ tự.
def create(db: Session, *, email: str, full_name: str, hashed_password: str) -> Users:
    # Không truyền role → model tự điền "student" (FR-40).
    user = Users(email=email, full_name=full_name, hashed_password=hashed_password)
    db.add(user)
    db.flush()  # gửi INSERT để có user_id, nhưng chưa commit
    return user
