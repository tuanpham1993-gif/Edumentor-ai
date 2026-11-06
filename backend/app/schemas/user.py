from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.security import validate_password


class UserMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    full_name: str
    email: str
    role: str
    avatar_url: str | None = None
    created_at: datetime


class UpdateMeRequest(BaseModel):
    """PATCH /me — chỉ sửa họ tên; email, vai trò chỉ đọc (FR-03)."""

    full_name: str = Field(min_length=1, max_length=100)

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Họ tên không được để trống.")
        return value


class ChangePasswordRequest(BaseModel):
    """POST /me/change-password (FR-48)."""

    current_password: str
    new_password: str
    confirm_new_password: str

    @field_validator("new_password")
    @classmethod
    def check_password_policy(cls, value: str) -> str:
        validate_password(value)
        return value

    @model_validator(mode="after")
    def check_passwords_match(self) -> "ChangePasswordRequest":
        if self.new_password != self.confirm_new_password:
            raise ValueError("Mật khẩu xác nhận không khớp.")
        return self


class MessageResponse(BaseModel):
    message: str
