"""Bảo mật dùng chung: băm mật khẩu, quy tắc mật khẩu, JWT (module 01 · Tuấn · GĐ1, 05/11/2026).

- Phần 1 — Mật khẩu: hash_password, verify_password, validate_password.
- Phần 2 — JWT access token: create_access_token, decode_access_token.
- Phần 3 — Token ngẫu nhiên (GĐ5–GĐ6): generate_token, hash_token.

Không phụ thuộc HTTP hay DB → dùng được ở mọi nơi (service, script, test).
"""

import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

# bcrypt chỉ xử lý tối đa 72 byte; bcrypt 5.0 sẽ báo lỗi nếu dài hơn.
MAX_PASSWORD_BYTES = 72
MIN_PASSWORD_LENGTH = 8


# =====================================================================
# PHẦN 1 — MẬT KHẨU
# Băm là MỘT CHIỀU: từ bản băm không tính ngược ra mật khẩu.
# "Salt" ngẫu nhiên được trộn vào → cùng mật khẩu nhưng mỗi lần băm ra chuỗi khác;
# salt được lưu ngay trong chuỗi băm nên checkpw vẫn so được.
# =====================================================================


def hash_password(plain_password: str) -> str:
    """Băm mật khẩu để lưu vào DB."""
    password_bytes = plain_password.encode(
        "utf-8"
    )  # bcrypt làm việc với bytes, không phải str
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")  # bytes → str để lưu vào cột String


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu người dùng nhập có khớp bản băm không."""
    try:
        # checkpw lấy salt trong bản băm, băm lại mật khẩu nhập vào rồi so sánh.
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        # Bản băm trong DB hỏng/sai định dạng, hoặc mật khẩu nhập quá 72 byte
        # → coi như sai mật khẩu (401) thay vì làm server lỗi 500.
        return False


def validate_password(password: str) -> None:
    """Kiểm tra quy tắc mật khẩu (màn demo ChangePassword/ResetPassword).
    Hợp lệ → không trả gì. Không hợp lệ → raise ValueError("lý do").
    Dùng chung cho đăng ký, đặt lại và đổi mật khẩu (FR-48).

    Dùng ValueError vì khi gọi trong validator của Pydantic, ValueError
    tự thành lỗi 422 kèm thông báo — không cần viết thêm code xử lý.
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Mật khẩu phải có tối thiểu {MIN_PASSWORD_LENGTH} ký tự.")

    # Đếm BYTE chứ không đếm ký tự: chữ có dấu như "ệ" chiếm 3 byte.
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise ValueError(f"Mật khẩu quá dài (tối đa {MAX_PASSWORD_BYTES} byte).")

    # re.search trả None khi KHÔNG tìm thấy → `not` để bắt trường hợp thiếu.
    if not re.search(r"[A-Z]", password):
        raise ValueError("Mật khẩu phải có ít nhất 1 chữ hoa.")

    if not re.search(r"[a-z]", password):
        raise ValueError("Mật khẩu phải có ít nhất 1 chữ thường.")

    if not re.search(r"[0-9]", password):
        raise ValueError("Mật khẩu phải có ít nhất 1 chữ số.")

    # Ký tự đặc biệt = bất kỳ ký tự nào KHÔNG phải chữ cái tiếng Anh / số
    # (lưu ý: dấu cách và chữ có dấu cũng được tính — câu hỏi Q1 còn mở).
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Mật khẩu phải có ít nhất 1 ký tự đặc biệt.")


# =====================================================================
# PHẦN 2 — JWT ACCESS TOKEN ("vé thông hành")
# JWT = header.payload.chữ_ký. Chữ ký tạo bằng SECRET_KEY (chỉ server biết)
# → ai sửa payload thì chữ ký không khớp → bị từ chối. Server không cần lưu token.
# Payload KHÔNG mã hóa (ai cũng đọc được) → chỉ đặt user_id, không đặt bí mật.
# =====================================================================


def create_access_token(user_id: int) -> str:
    """Tạo access token (JWT) sau khi đăng nhập thành công."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),  # "subject": vé của ai — PyJWT bắt buộc là chuỗi
        "iat": now,  # "issued at": phát lúc nào
        # "expiration": hết hạn sau ACCESS_TOKEN_EXPIRE_MINUTES (đọc từ .env, không ghi cứng)
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Đọc token. Hợp lệ → trả user_id (int). Giả / hết hạn / hỏng → None."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            # Chỉ chấp nhận đúng thuật toán HS256 → chặn kiểu tấn công gửi token "alg: none".
            algorithms=[settings.ALGORITHM],
        )
        return int(payload["sub"])
    # InvalidTokenError: chữ ký sai, token hỏng, hết hạn (ExpiredSignatureError là lớp con)
    # KeyError: thiếu "sub" · ValueError: "sub" không phải số
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None


# =====================================================================
# PHẦN 3 — TOKEN NGẪU NHIÊN (reset mật khẩu, refresh token)
# =====================================================================


def generate_token() -> str:
    """Chuỗi ngẫu nhiên an toàn (~43 ký tự) — gửi cho người dùng, KHÔNG lưu bản gốc."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Bản băm SHA-256 (hex) — lưu vào DB và dùng để tìm token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
