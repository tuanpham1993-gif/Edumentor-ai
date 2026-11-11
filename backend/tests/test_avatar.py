"""Test tự động: đổi ảnh đại diện POST /api/me/avatar (module 01 · Tuấn · GĐ7, 07/11/2026).

Chạy:  python -m pytest tests/test_avatar.py -v      (trong thư mục backend)

Không cần ảnh thật: chỉ cần byte giả có đúng "chữ ký" PNG / JPEG.
Fixture `upload_dir` (autouse) đổi UPLOAD_DIR sang thư mục tạm của pytest
→ test không ghi file vào backend/uploads/ thật, và tự dọn sau mỗi test.
"""

import pytest

from app.core.config import settings

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100  # "ảnh PNG" giả: đúng chữ ký
JPEG = b"\xff\xd8\xff" + b"0" * 100
AVATAR_URL = "/api/me/avatar"
ME_URL = "/api/me"
PASSWORD = "Abc@1234"
EMAIL = "tuan@gmail.com"


@pytest.fixture(autouse=True)
def upload_dir(tmp_path, monkeypatch):
    """Mọi test trong file này lưu ảnh vào thư mục tạm (tự xóa sau test)."""
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture()
def auth_headers(client):
    """Đăng ký + đăng nhập, trả về header có access token."""
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Tuấn",
            "email": EMAIL,
            "password": PASSWORD,
            "confirm_password": PASSWORD,
        },
    )
    token = client.post(
        "/api/auth/login", json={"email": EMAIL, "password": PASSWORD}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def upload(client, headers, data, filename="a.png", content_type="image/png"):
    return client.post(
        AVATAR_URL, files={"file": (filename, data, content_type)}, headers=headers
    )


def saved_files(upload_dir):
    folder = upload_dir / "avatars"
    return sorted(folder.iterdir()) if folder.exists() else []


# ─────────────── Upload thành công ───────────────


def test_upload_png_success(client, auth_headers, upload_dir):
    response = upload(client, auth_headers, PNG)

    assert response.status_code == 200
    avatar_url = response.json()["avatar_url"]
    assert avatar_url.startswith("/uploads/avatars/")
    assert avatar_url.endswith(".png")
    files = saved_files(upload_dir)
    assert (
        len(files) == 1 and files[0].read_bytes() == PNG
    )  # file có thật, đúng nội dung


def test_upload_jpeg_success(client, auth_headers):
    response = upload(
        client, auth_headers, JPEG, filename="a.jpg", content_type="image/jpeg"
    )

    assert response.status_code == 200
    assert response.json()["avatar_url"].endswith(".jpg")


def test_avatar_saved_in_profile(client, auth_headers):
    avatar_url = upload(client, auth_headers, PNG).json()["avatar_url"]

    assert client.get(ME_URL, headers=auth_headers).json()["avatar_url"] == avatar_url


def test_new_avatar_deletes_old_file(client, auth_headers, upload_dir):
    upload(client, auth_headers, PNG)
    new_url = upload(
        client, auth_headers, JPEG, filename="b.jpg", content_type="image/jpeg"
    ).json()["avatar_url"]

    files = saved_files(upload_dir)
    assert len(files) == 1  # ảnh cũ đã bị xóa
    assert new_url.endswith(files[0].name)


# ─────────────── Bảo mật ───────────────


def test_filename_from_client_is_ignored(client, auth_headers):
    response = upload(client, auth_headers, PNG, filename="../../evil.png")

    assert response.status_code == 200
    avatar_url = response.json()["avatar_url"]
    assert "evil" not in avatar_url and ".." not in avatar_url  # server tự đặt tên


def test_fake_image_returns_415(client, auth_headers, upload_dir):
    """File chữ đổi đuôi .png + content_type image/png vẫn bị chặn nhờ kiểm tra chữ ký."""
    response = upload(client, auth_headers, b"hello, toi khong phai anh")

    assert response.status_code == 415
    assert response.json()["detail"] == "Chỉ chấp nhận ảnh PNG hoặc JPEG."
    assert saved_files(upload_dir) == []  # không lưu gì


def test_empty_file_returns_415(client, auth_headers):
    assert upload(client, auth_headers, b"").status_code == 415


def test_too_large_returns_413(client, auth_headers, upload_dir):
    data = PNG + b"0" * settings.AVATAR_MAX_BYTES  # luôn lớn hơn giới hạn
    response = upload(client, auth_headers, data)

    assert response.status_code == 413
    assert (
        response.json()["detail"]
        == f"Ảnh vượt quá {settings.AVATAR_MAX_BYTES // (1024 * 1024)} MB."
    )
    assert saved_files(upload_dir) == []


def test_upload_without_token_returns_401(client):
    assert upload(client, {}, PNG).status_code == 401
