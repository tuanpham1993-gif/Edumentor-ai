"""Schema tài khoản (module 01 · Tuấn): đăng ký, đăng nhập (GĐ2, 05/11); quên / đặt lại mật khẩu (GĐ5, 06/11).

Lớp SCHEMA = "người gác cổng": khai báo dữ liệu vào phải trông như thế nào.
Sai → FastAPI tự trả 422 kèm lý do, code phía sau KHÔNG chạy.
  - @field_validator("x"): kiểm tra MỘT trường.
  - @model_validator(mode="after"): kiểm tra NHIỀU trường cùng lúc (chạy sau khi từng trường đã qua).
  - Trong validator, raise ValueError("...") → thành lỗi 422.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.core.security import validate_password
from app.schemas.user import UserMe


class RegisterRequest(BaseModel):
    """Body của POST /api/auth/register (màn demo Register: 4 ô).

    KHÔNG có trường `role` → client gửi kèm "role": "admin" cũng bị bỏ qua (luôn tạo student).
    """

    full_name: str = Field(min_length=1, max_length=100)  # khớp String(100) trong model
    email: EmailStr  # Pydantic tự kiểm tra dạng email
    password: str
    confirm_password: str  # chỉ để so khớp, KHÔNG lưu và không truyền xuống service

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str) -> str:
        value = value.strip()  # "  Phạm Tuấn  " → "Phạm Tuấn"
        if not value:
            raise ValueError("Họ tên không được để trống.")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        # Chữ thường để "Tuan@Gmail.com" và "tuan@gmail.com" không thành 2 tài khoản.
        return value.lower()

    @field_validator("password")
    @classmethod
    def check_password_policy(cls, value: str) -> str:
        validate_password(value)  # dùng chung quy tắc ở core/security.py
        return value

    @model_validator(mode="after")
    def check_passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Mật khẩu xác nhận không khớp.")
        return self


class LoginRequest(BaseModel):
    """Body của POST /api/auth/login.

    KHÔNG kiểm tra quy tắc mật khẩu ở đây: đăng nhập chỉ cần SO KHỚP;
    kiểm quy tắc sẽ khóa người dùng cũ khi nhóm đổi quy tắc và làm lộ quy tắc cho kẻ dò.
    """

    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()  # phải chuẩn hóa giống lúc đăng ký


class TokenResponse(BaseModel):
    """Response đăng nhập: token + thông tin user (có `role` để frontend biết student/admin)."""

    access_token: str
    token_type: str = "bearer"
    user: UserMe  # nhận thẳng object Users nhờ from_attributes=True trong UserMe

class ForgotPasswordRequest(BaseModel):
    """Body của POST /api/auth/forgot-password (GĐ5)."""

    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class ResetPasswordRequest(BaseModel):
    """Body của POST /api/auth/reset-password (GĐ5) — token lấy từ link trong email."""

    token: str = Field(min_length=1)
    new_password: str
    confirm_new_password: str

    @field_validator("new_password")
    @classmethod
    def check_password_policy(cls, value: str) -> str:
        validate_password(value)
        return value

    @model_validator(mode="after")
    def check_passwords_match(self) -> "ResetPasswordRequest":
        if self.new_password != self.confirm_new_password:
            raise ValueError("Mật khẩu xác nhận không khớp.")
        return self
