"""Nghiệp vụ hồ sơ người dùng (module 01 · Tuấn · GĐ3 06/11; ảnh đại diện GĐ7 07/11).

Không cần repository ở đây: `user` đã được lấy từ DB trong get_current_user.
Chỉ cần sửa thuộc tính rồi commit — SQLAlchemy tự theo dõi object bị sửa và
tự sinh câu UPDATE users SET ... WHERE user_id = ...
"""

from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    encrypt_pii,
    hash_password,
    pii_fingerprint,
    verify_password,
)
from app.models.user import Users
from app.models.user_profile import UserProfile
from app.repositories import token_repository, user_skill_repository
from app.services import course_gateway, notification_service
from app.utils import files


class WrongCurrentPasswordError(Exception):
    """Mật khẩu hiện tại nhập vào không đúng."""


class SamePasswordError(Exception):
    """Mật khẩu mới trùng mật khẩu hiện tại (08/11)."""


class CitizenIdTakenError(Exception):
    """Số CCCD đã dùng cho tài khoản khác."""


PROFILE_FIELDS = ("date_of_birth", "gender", "hometown", "phone")


def mask_citizen_id(number: str) -> str:
    """Chỉ lộ 3 số đầu: "345678901234" → "345*********" (Tuấn chốt 12/11)."""
    return number[:3] + "*" * (len(number) - 3)


def update_profile(db: Session, user: Users, *, full_name: str, details: dict | None = None) -> Users:
    """Sửa họ tên (FR-03) + thông tin cá nhân (12/11). Email và vai trò không đổi được.

    details: CHỈ các trường người dùng gửi lên (khóa vắng = giữ nguyên; giá trị None = xóa).
      citizen_id: số đầy đủ → lưu bản MÃ HÓA + bản che + dấu vân tay (chặn trùng); None = xóa.
    """
    user.full_name = full_name
    details = details or {}
    if details:
        profile = user.profile or UserProfile(user_id=user.user_id)
        user.profile = profile
        for key in PROFILE_FIELDS:
            if key in details:
                setattr(profile, key, details[key])
        if "citizen_id" in details:
            number = details["citizen_id"]
            profile.citizen_id_encrypted = encrypt_pii(number) if number else None
            profile.citizen_id_masked = mask_citizen_id(number) if number else None
            profile.citizen_id_hash = pii_fingerprint(number) if number else None
    try:
        db.commit()  # SQLAlchemy tự gửi UPDATE / INSERT
    except IntegrityError:
        db.rollback()
        raise CitizenIdTakenError from None
    db.refresh(user)  # đọc lại updated_at mới do DB điền
    return user


def change_password(
    db: Session, user: Users, *, current_password: str, new_password: str
) -> None:
    """Đổi mật khẩu (FR-48). Sai mật khẩu hiện tại → WrongCurrentPasswordError;
    mật khẩu mới trùng mật khẩu cũ → SamePasswordError.

    Lưu ý: access token cũ vẫn dùng được tới khi hết hạn (JWT không thu hồi được);
    đổi mật khẩu thì thu hồi mọi refresh token của user (Q10, GĐ6).
    """
    # Phải nhập đúng mật khẩu hiện tại — chặn người khác dùng máy đang đăng nhập để đổi.
    if not verify_password(current_password, user.hashed_password):
        raise WrongCurrentPasswordError  # nhập sai → không đổi gì cả

    # Mật khẩu mới trùng mật khẩu đang dùng → không đổi (08/11).
    # Đặt SAU bước kiểm mật khẩu hiện tại: người chưa biết mật khẩu không dò được qua lỗi này.
    if verify_password(new_password, user.hashed_password):
        raise SamePasswordError

    user.hashed_password = hash_password(new_password)  # vẫn chỉ lưu bản băm
    # Q10: đổi mật khẩu → đăng xuất mọi nơi (kể cả phiên hiện tại khi access hết hạn)
    token_repository.revoke_all_refresh_tokens(
        db, user.user_id, datetime.now(timezone.utc)
    )
    notification_service.notify(  # chuông: cảnh báo bảo mật (11/11)
        db, user.user_id, "password_changed", "Mật khẩu của bạn vừa được thay đổi",
        body="Nếu không phải bạn thực hiện, hãy đặt lại mật khẩu ngay.", link="/me/password",
    )
    db.commit()


def update_avatar(db: Session, user: Users, *, data: bytes) -> Users:
    """Lưu ảnh mới, cập nhật avatar_url, xóa ảnh cũ (FR-03).

    Lỗi kiểm tra → files.FileTooLargeError / files.UnsupportedImageError (router đổi thành 413 / 415).
    """
    old_url = user.avatar_url
    new_url = files.save_avatar(user.user_id, data)  # lưu file TRƯỚC
    try:
        user.avatar_url = new_url
        db.commit()
    except Exception:
        db.rollback()
        files.delete_avatar(new_url)  # DB lỗi → dọn file vừa lưu, không để rác
        raise
    files.delete_avatar(old_url)  # xóa ảnh cũ SAU KHI lưu DB thành công
    db.refresh(user)
    return user


def summary(db: Session, user: Users) -> dict:
    """GET /api/me/summary — 4 ô thống kê trang Hồ sơ (7.2 · 12/11/2026, Q9).

    - Khóa đang học / đã hoàn thành: bảng user_courses của Khôi, đi qua course_gateway (không đọc thẳng).
    - Kỹ năng đã biết: user_skills 'known' (Tuấn).
    - Lộ trình đang theo: None — learning_paths của Hòa còn dùng `student_id` tạm (id học viên mẫu, nhận từ
      query, không phải users.user_id) → đếm theo user_id sẽ ra số sai. Khi Hòa đổi sang user_id: chỉ sửa dòng này.
    """
    return {
        "courses_in_progress": course_gateway.count_courses(db, user, course_gateway.IN_PROGRESS),
        "courses_completed": course_gateway.count_courses(db, user, course_gateway.COMPLETED),
        "known_skills": len(user_skill_repository.list_by_user(db, user.user_id, "known")),
        "active_paths": None,  # TODO(Hòa): đếm learning_paths 'ongoing' theo user_id
    }
