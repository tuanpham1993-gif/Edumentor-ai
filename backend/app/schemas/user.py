"""Schema hồ sơ người dùng /api/me* (module 01 · Tuấn · GĐ2–GĐ3, 05–06/11/2026).

- UserMe               : dữ liệu TRẢ RA (response) — không bao giờ có hashed_password.
- UpdateMeRequest      : body PATCH /api/me — chỉ sửa họ tên.
- ChangePasswordRequest: body POST /api/me/change-password.
- MessageResponse      : response chỉ có một thông báo.
"""

import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.security import validate_password


class UserMe(BaseModel):
    """Thông tin hồ sơ trả về (FR-03): họ tên, email, vai trò, ngày tham gia, ảnh đại diện."""

    # from_attributes=True: đọc thẳng từ object SQLAlchemy (Users) → router chỉ cần `return user`.
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    full_name: str
    email: str
    role: str
    avatar_url: str | None = None  # None khi chưa có ảnh (GĐ7 mới làm upload)
    created_at: datetime
    # Thông tin cá nhân thêm (12/11) — bảng user_profiles; chưa nhập → None
    date_of_birth: date | None = None
    gender: Literal["male", "female"] | None = None
    hometown: str | None = None
    phone: str | None = None
    citizen_id_masked: str | None = None  # vd "345*********" — KHÔNG BAO GIỜ trả số CCCD đầy đủ
    # KHÔNG có hashed_password, is_active, updated_at → không bao giờ bị trả ra ngoài.


class UpdateMeRequest(BaseModel):
    """PATCH /me — sửa họ tên + thông tin cá nhân (12/11); email, vai trò chỉ đọc (FR-03).

    Không khai báo email / role → client gửi kèm cũng bị Pydantic bỏ qua.
    Các trường cá nhân: KHÔNG gửi = giữ nguyên; gửi null = xóa; gửi giá trị = cập nhật.
    citizen_id chỉ GHI (12 chữ số) — đọc lại chỉ có bản che citizen_id_masked.
    """

    full_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date | None = None
    gender: Literal["male", "female"] | None = None
    hometown: str | None = Field(default=None, max_length=100)
    phone: str | None = None
    citizen_id: str | None = None

    @field_validator("date_of_birth")
    @classmethod
    def check_birth_date(cls, value: date | None) -> date | None:
        if value is not None and not (date(1900, 1, 1) <= value <= date.today()):
            raise ValueError("Ngày sinh không hợp lệ.")
        return value

    @field_validator("hometown")
    @classmethod
    def clean_hometown(cls, value: str | None) -> str | None:
        value = (value or "").strip()
        return value or None

    @field_validator("phone")
    @classmethod
    def check_phone(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        digits = re.sub(r"[\s.\-()]", "", value)
        if digits.startswith("+84"):
            digits = "0" + digits[3:]
        if not re.fullmatch(r"0\d{9}", digits):
            raise ValueError("Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0.")
        return digits

    @field_validator("citizen_id")
    @classmethod
    def check_citizen_id(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        digits = re.sub(r"\s", "", value)
        if not re.fullmatch(r"\d{12}", digits):
            raise ValueError("Số CCCD phải gồm đúng 12 chữ số.")
        return digits

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str) -> str:
        # Giống RegisterRequest.clean_full_name (schemas/auth.py).
        value = value.strip()
        if not value:
            raise ValueError("Họ tên không được để trống.")
        return value


class ChangePasswordRequest(BaseModel):
    """POST /me/change-password (FR-48) — màn demo ChangePassword: 3 ô."""

    # Không kiểm quy tắc cho mật khẩu HIỆN TẠI (chỉ cần so khớp — lý do giống LoginRequest).
    current_password: str
    new_password: str
    confirm_new_password: str

    @field_validator("new_password")
    @classmethod
    def check_password_policy(cls, value: str) -> str:
        validate_password(value)  # cùng quy tắc với đăng ký và đặt lại mật khẩu
        return value

    @model_validator(mode="after")
    def check_passwords_match(self) -> "ChangePasswordRequest":
        if self.new_password != self.confirm_new_password:
            raise ValueError("Mật khẩu xác nhận không khớp.")
        return self


class MessageResponse(BaseModel):
    message: str
