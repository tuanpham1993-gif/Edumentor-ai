"""Tạo tài khoản ADMIN (module 01 · Tuấn · GĐ8, 07/11/2026).

Đăng ký qua API luôn tạo student (FR-40) → admin chỉ tạo bằng script này, chạy trên máy server.

Chạy (trong thư mục backend):
    python -m scripts.create_admin --email admin@edumentor.vn --full-name "Quản trị viên"
Mật khẩu được hỏi bằng getpass (không hiện khi gõ, không lưu vào lịch sử lệnh).
"""

import argparse
import getpass
import sys

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, create_tables
from app.models.user import Users
from app.schemas.auth import RegisterRequest
from app.services import auth_service


def create_admin(db: Session, *, email: str, full_name: str, password: str) -> Users:
    """Tạo admin. Dữ liệu sai → ValidationError; email đã có → EmailAlreadyExistsError.

    Dùng lại schema đăng ký (kiểm email, họ tên, quy tắc mật khẩu) và auth_service.register
    (kiểm trùng email, băm mật khẩu) — service không biết HTTP nên script gọi lại được.
    """
    data = RegisterRequest(
        full_name=full_name, email=email, password=password, confirm_password=password
    )
    user = auth_service.register(
        db, email=data.email, full_name=data.full_name, password=data.password
    )
    user.role = "admin"  # điểm khác duy nhất so với đăng ký thường
    db.commit()
    db.refresh(user)
    return user


def main() -> int:
    parser = argparse.ArgumentParser(description="Tạo tài khoản admin EduMentor AI")
    parser.add_argument("--email", required=True)
    parser.add_argument("--full-name", required=True)
    args = parser.parse_args()

    password = getpass.getpass("Mật khẩu admin: ")
    confirm = getpass.getpass("Nhập lại mật khẩu: ")
    if confirm != password:
        print("Mật khẩu xác nhận không khớp.")
        return 1

    create_tables()  # phòng khi chạy script trước lần đầu khởi động server
    db = SessionLocal()
    try:
        user = create_admin(
            db, email=args.email, full_name=args.full_name, password=password
        )
    except ValidationError as error:
        print("Dữ liệu không hợp lệ:")
        for e in error.errors():
            print("-", e["msg"].removeprefix("Value error, "))
        return 1
    except auth_service.EmailAlreadyExistsError:
        print(f"Email {args.email} đã có tài khoản.")
        return 1
    finally:
        db.close()

    print(f"Đã tạo admin #{user.user_id}: {user.email}")  # KHÔNG in mật khẩu
    return 0


if __name__ == "__main__":
    sys.exit(main())
