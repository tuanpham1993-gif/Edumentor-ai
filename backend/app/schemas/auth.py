from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
 
from app.core.security import validate_password
from app.schemas.user import UserMe
 
 
class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str
    confirm_password: str
 
    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Họ tên không được để trống.")
        return value
 
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()
 
    @field_validator("password")
    @classmethod
    def check_password_policy(cls, value: str) -> str:
        validate_password(value)
        return value
 
    @model_validator(mode="after")
    def check_passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Mật khẩu xác nhận không khớp.")
        return self
 
 
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
 
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()
 
 
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserMe
 