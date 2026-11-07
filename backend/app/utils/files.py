"""Lưu / xóa file ảnh đại diện (module 01 · Tuấn · GĐ7, 07/11/2026).

Q8: PNG + JPEG, tối đa 5 MB, lưu backend/uploads/avatars/. Sau này chuyển lên đám mây
thì chỉ viết lại save_avatar / delete_avatar (avatar_url chứa được URL đầy đủ).

Không tin tên file hay content_type từ client: kiểm tra "chữ ký" byte đầu file,
và server tự đặt tên file → chặn file giả dạng ảnh và lỗi path traversal.
"""

import secrets
from pathlib import Path

from app.core.config import settings

AVATAR_SUBDIR = "avatars"
URL_PREFIX = "/uploads"

# Chữ ký (magic bytes) của định dạng được chấp nhận → đuôi file
SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpg",
}


class FileTooLargeError(Exception):
    """File vượt dung lượng cho phép."""


class UnsupportedImageError(Exception):
    """Không phải ảnh PNG / JPEG hợp lệ."""


def avatar_dir() -> Path:
    path = Path(settings.UPLOAD_DIR) / AVATAR_SUBDIR
    path.mkdir(parents=True, exist_ok=True)  # tạo thư mục nếu chưa có
    return path


def detect_image_extension(data: bytes) -> str | None:
    """Trả 'png' / 'jpg' nếu byte đầu khớp chữ ký, ngược lại None."""
    for signature, ext in SIGNATURES.items():
        if data.startswith(signature):
            return ext
    return None


def save_avatar(user_id: int, data: bytes) -> str:
    """Kiểm tra rồi lưu file. Trả avatar_url (vd "/uploads/avatars/7_ab12cd34ef56.png")."""
    if len(data) > settings.AVATAR_MAX_BYTES:
        raise FileTooLargeError
    ext = detect_image_extension(data)
    if ext is None:
        raise UnsupportedImageError

    filename = f"{user_id}_{secrets.token_hex(8)}.{ext}"  # tên do SERVER đặt
    (avatar_dir() / filename).write_bytes(data)
    return f"{URL_PREFIX}/{AVATAR_SUBDIR}/{filename}"


def delete_avatar(avatar_url: str | None) -> None:
    """Xóa file ảnh cũ — CHỈ khi url là ảnh do hệ thống lưu (bắt đầu /uploads/avatars/)."""
    prefix = f"{URL_PREFIX}/{AVATAR_SUBDIR}/"
    if not avatar_url or not avatar_url.startswith(prefix):
        return
    name = Path(avatar_url).name  # chỉ lấy tên file, bỏ mọi thư mục → an toàn
    (avatar_dir() / name).unlink(missing_ok=True)
