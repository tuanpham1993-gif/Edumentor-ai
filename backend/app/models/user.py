"""Model bảng `users` — tài khoản người dùng (module 01 · Tuấn · GĐ1, 05/11/2026).

Lớp MODEL: mô tả bảng bằng Python; khi server khởi động, `create_all()` đọc model
(phải được import trong `models/__init__.py`) và tự tạo bảng trong PostgreSQL.
"""

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer, String, func

from app.core.database import Base


class Users(Base):  # Kế thừa Base → SQLAlchemy biết đây là một bảng
    __tablename__ = "users"

    # Khóa chính, DB tự tăng 1, 2, 3… Cũng là `sub` trong JWT.
    user_id = Column(Integer, primary_key=True, index=True)

    # ---------- Hồ sơ (FR-03) ----------
    full_name = Column(String(100), nullable=False)  # schema phải khớp max_length=100
    # unique=True: mỗi email chỉ một tài khoản (FR-01) — lưới an toàn cuối cùng ở tầng DB.
    # index=True: tìm theo email khi đăng nhập nhanh hơn.
    email = Column(String(255), nullable=False, unique=True, index=True)
    # default: Python tự điền khi INSERT; server_default: DB tự điền (kể cả khi INSERT bằng SQL tay).
    role = Column(String(20), nullable=False, default="student", server_default="student")
    # nullable=True: người mới đăng ký chưa có ảnh. Chỉ lưu ĐƯỜNG DẪN ảnh, không lưu file ảnh.
    avatar_url = Column(String(500), nullable=True)
    # "Ngày tham gia" — PostgreSQL tự điền giờ hiện tại; timezone=True để không lệch múi giờ.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---------- Đăng nhập ----------
    # KHÔNG lưu mật khẩu gốc — chỉ lưu bản băm bcrypt "$2b$12$..." (NFR-04).
    hashed_password = Column(String(255), nullable=False)
    # Khóa tài khoản mà không cần xóa; get_current_user và login từ chối user is_active=False.
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    # server_default: điền lúc tạo; onupdate: cập nhật mỗi lần sửa qua SQLAlchemy (vd PATCH /me).
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Ràng buộc ở tầng DB: role chỉ được là 'student' hoặc 'admin' (FR-40).
    # Dù code có lỗi, DB vẫn không cho lưu role lạ như 'superuser'.
    __table_args__ = (CheckConstraint("role IN ('student', 'admin')", name="ck_users_role"),)
