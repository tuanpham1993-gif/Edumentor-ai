"""Schema hồ sơ người dùng /api/me* (module 01 · Tuấn · GĐ2–GĐ3, 05–06/11/2026).

- UserMe               : dữ liệu TRẢ RA (response) — không bao giờ có hashed_password.
- UpdateMeRequest      : body PATCH /api/me — chỉ sửa họ tên.
- ChangePasswordRequest: body POST /api/me/change-password.
- MessageResponse      : response chỉ có một thông báo.
"""

from datetime import datetime

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
    # KHÔNG có hashed_password, is_active, updated_at → không bao giờ bị trả ra ngoài.


class UpdateMeRequest(BaseModel):
    """PATCH /me — chỉ sửa họ tên; email, vai trò chỉ đọc (FR-03).

    Chỉ khai báo full_name → client gửi kèm "email"/"role" cũng bị Pydantic bỏ qua.
    """

    full_name: str = Field(min_length=1, max_length=100)

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
