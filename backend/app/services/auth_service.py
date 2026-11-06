"""Nghiệp vụ tài khoản (module 01 · Tuấn).

- GĐ2 (05/11/2026): đăng ký, đăng nhập.
- GĐ5 (06/11/2026): quên mật khẩu, đặt lại mật khẩu (token một lần dùng, chỉ lưu bản băm).

Lớp SERVICE = "quản lý": giữ quy tắc nghiệp vụ và là lớp DUY NHẤT gọi commit/rollback.
Service KHÔNG biết HTTP: báo "chuyện gì xảy ra" bằng exception có tên rõ nghĩa
(EmailAlreadyExistsError) hoặc trả None; router mới dịch sang mã HTTP (409, 401).
Nhờ vậy script (vd create_admin.py) cũng gọi lại được service này.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.user import Users
from app.repositories import token_repository, user_repository


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


class InvalidResetTokenError(Exception):
    """Link đặt lại mật khẩu sai, đã dùng hoặc hết hạn."""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    """SQLite (khi test) trả datetime không múi giờ → gắn UTC để so sánh được."""
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def forgot_password(db: Session, *, email: str) -> str | None:
    """Tạo link đặt lại (FR-47). Trả token GỐC để gửi email; email không tồn tại → None.

    DB chỉ lưu bản băm SHA-256 của token. Router luôn trả cùng một thông báo.
    """
    user = user_repository.get_by_email(db, email)

    if user is None or not user.is_active:
        return None

    now = _utcnow()

    token_repository.invalidate_unused_reset_tokens(db, user.user_id, now)
    token = generate_token()

    token_repository.create_reset_token(
        db,
        user_id=user.user_id,
        token_hash=hash_token(token),
        expires_at=now + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES),
    )

    db.commit()
    return token  # trả bản GỐC để gửi email; DB chỉ có bản băm


def reset_password(db: Session, *, token: str, new_password: str) -> None:
    """Đặt mật khẩu mới bằng token trong link. Sai / đã dùng / hết hạn → InvalidResetTokenError."""
    record = token_repository.get_reset_token_by_hash(db, hash_token(token))
    now = _utcnow()

    if record is None or record.used_at is not None or _as_utc(record.expires_at) <= now:
        raise InvalidResetTokenError()

    user = user_repository.get_by_id(db, record.user_id)

    if user is None or not user.is_active:
        raise InvalidResetTokenError()

    user.hashed_password = hash_password(new_password)
    record.used_at = now
    token_repository.invalidate_unused_reset_tokens(db, user.user_id, now)  # vô hiệu link khác
    # GĐ6: thu hồi mọi refresh token của user (Q10)
    db.commit()
