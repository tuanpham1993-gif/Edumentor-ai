"""Nghiệp vụ đăng ký / đăng nhập (module 01 · Tuấn · GĐ2, 05/11/2026).

Lớp SERVICE = "quản lý": giữ quy tắc nghiệp vụ và là lớp DUY NHẤT gọi commit/rollback.
Service KHÔNG biết HTTP: báo "chuyện gì xảy ra" bằng exception có tên rõ nghĩa
(EmailAlreadyExistsError) hoặc trả None; router mới dịch sang mã HTTP (409, 401).
Nhờ vậy script (vd create_admin.py) cũng gọi lại được service này.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import Users
from app.repositories import user_repository


class EmailAlreadyExistsError(Exception):
    """Email đã được dùng để đăng ký."""


def register(db: Session, *, email: str, full_name: str, password: str) -> Users:
    """Tạo tài khoản student mới (FR-01). Email trùng → EmailAlreadyExistsError.

    Không có tham số `role` → mọi tài khoản tạo qua đây đều là student.
    """
    # Kiểm tra trùng lần 1: bắt gần như mọi trường hợp, báo lỗi rõ ràng.
    if user_repository.get_by_email(db, email) is not None:
        raise EmailAlreadyExistsError

    try:
        user = user_repository.create(
            db,
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),  # chỉ lưu bản băm
        )
        db.commit()
    except IntegrityError:
        # Kiểm tra trùng lần 2: hai người bấm đăng ký cùng email CÙNG LÚC — cả hai đều
        # qua lần 1, nhưng ràng buộc unique của DB chặn người thứ hai → IntegrityError.
        db.rollback()
        # `from None`: không in kèm lỗi gốc IntegrityError dài dòng vào log.
        raise EmailAlreadyExistsError from None

    db.refresh(user)  # đọc lại các giá trị DB tự điền: role, created_at...
    return user


def login(db: Session, *, email: str, password: str) -> tuple[str, Users] | None:
    """Đúng email + mật khẩu và tài khoản còn hoạt động → (token, user). Ngược lại → None.

    Cả 3 trường hợp thất bại đều trả None → router không phân biệt được lý do →
    không lộ cho người ngoài biết email nào đã đăng ký.
    """
    user = user_repository.get_by_email(db, email)
    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    token = create_access_token(user.user_id)
    return token, user
