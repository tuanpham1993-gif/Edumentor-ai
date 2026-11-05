import re
 
import bcrypt
 
# bcrypt chỉ xử lý tối đa 72 byte; bcrypt 5.0 sẽ báo lỗi nếu dài hơn.
MAX_PASSWORD_BYTES = 72
MIN_PASSWORD_LENGTH = 8
 
 
def hash_password(plain_password: str) -> str:
    """Băm mật khẩu để lưu vào DB."""
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")
 
 
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu người dùng nhập có khớp bản băm không."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        # Bản băm trong DB hỏng/sai định dạng, hoặc mật khẩu nhập quá 72 byte
        return False
 
 
def validate_password(password: str) -> None:
    """Kiểm tra quy tắc mật khẩu (màn demo ChangePassword/ResetPassword).
    Hợp lệ → không trả gì. Không hợp lệ → raise ValueError("lý do").
    Dùng chung cho đăng ký, đặt lại và đổi mật khẩu (FR-48).
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Mật khẩu phải có tối thiểu {MIN_PASSWORD_LENGTH} ký tự.")
 
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise ValueError(f"Mật khẩu quá dài (tối đa {MAX_PASSWORD_BYTES} byte).")
 
    if not re.search(r"[A-Z]", password):
        raise ValueError("Mật khẩu phải có ít nhất 1 chữ hoa.")
 
    if not re.search(r"[a-z]", password):
        raise ValueError("Mật khẩu phải có ít nhất 1 chữ thường.")
 
    if not re.search(r"[0-9]", password):
        raise ValueError("Mật khẩu phải có ít nhất 1 chữ số.")
 
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Mật khẩu phải có ít nhất 1 ký tự đặc biệt.")
 