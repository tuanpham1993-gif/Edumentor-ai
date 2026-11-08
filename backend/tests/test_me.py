"""Test tự động: PATCH /me, đổi mật khẩu (module 01 · Tuấn · GĐ3, 06/11/2026).

Chạy:  python -m pytest tests/test_me.py -v      (trong thư mục backend)

Fixture tự viết `auth_headers`: đăng ký + đăng nhập sẵn, trả về header có token.
Test nào cần đăng nhập chỉ việc thêm tham số `auth_headers` — không lặp 3 bước.
Ngoài kiểm tra mã HTTP, có test kiểm tra DỮ LIỆU: tên mới đã lưu (GET lại),
nhập sai mật khẩu hiện tại thì mật khẩu cũ vẫn dùng được (không đổi gì).
"""

import pytest

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
ME_URL = "/api/me"
CHANGE_PW_URL = "/api/me/change-password"

PASSWORD = "Abc@1234"
VALID_USER = {
    "full_name": "Phạm Tuấn",
    "email": "tuan@gmail.com",
    "password": PASSWORD,
    "confirm_password": PASSWORD,
}


@pytest.fixture()
def auth_headers(client):
    """Đăng ký + đăng nhập VALID_USER, trả về header có token."""
    client.post(REGISTER_URL, json=VALID_USER)
    response = client.post(
        LOGIN_URL, json={"email": VALID_USER["email"], "password": PASSWORD}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def change_password(client, headers, current, new, confirm=None):
    """Gọi API đổi mật khẩu. confirm mặc định = new."""
    return client.post(
        CHANGE_PW_URL,
        json={
            "current_password": current,
            "new_password": new,
            "confirm_new_password": new if confirm is None else confirm,
        },
        headers=headers,
    )


def login(client, password):
    """Đăng nhập VALID_USER với mật khẩu cho trước."""
    return client.post(
        LOGIN_URL, json={"email": VALID_USER["email"], "password": password}
    )


# ─────────────── PATCH /api/me ───────────────


def test_update_full_name_success(client, auth_headers):
    response = client.patch(
        ME_URL, json={"full_name": "  Tuấn Tài  "}, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Tuấn Tài"


def test_update_full_name_is_saved(client, auth_headers):
    client.patch(ME_URL, json={"full_name": "Tên Mới"}, headers=auth_headers)

    response = client.get(ME_URL, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["full_name"] == "Tên Mới"


def test_update_cannot_change_email_or_role(client, auth_headers):
    response = client.patch(
        ME_URL,
        json={"full_name": "X", "email": "hack@x.com", "role": "admin"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    me = client.get(ME_URL, headers=auth_headers).json()
    assert me["email"] == "tuan@gmail.com"
    assert me["role"] == "student"


def test_update_blank_full_name_returns_422(client, auth_headers):
    response = client.patch(ME_URL, json={"full_name": "   "}, headers=auth_headers)

    assert response.status_code == 422


def test_update_full_name_too_long_returns_422(client, auth_headers):
    response = client.patch(ME_URL, json={"full_name": "A" * 101}, headers=auth_headers)

    assert response.status_code == 422


def test_update_without_token_returns_401(client):
    response = client.patch(ME_URL, json={"full_name": "Tên Mới"})

    assert response.status_code == 401


# ─────────────── POST /api/me/change-password ───────────────


def test_change_password_success(client, auth_headers):
    response = change_password(client, auth_headers, current=PASSWORD, new="Moi@5678")

    assert response.status_code == 200
    assert response.json()["message"] == "Đổi mật khẩu thành công."


def test_change_password_then_old_fails_new_works(client, auth_headers):
    change_password(client, auth_headers, current=PASSWORD, new="Moi@5678")

    assert login(client, PASSWORD).status_code == 401
    assert login(client, "Moi@5678").status_code == 200


def test_change_password_wrong_current_returns_400(client, auth_headers):
    response = change_password(client, auth_headers, current="Sai@0000", new="Moi@5678")

    assert response.status_code == 400
    assert response.json()["detail"] == "Mật khẩu hiện tại không đúng."


def test_change_password_wrong_current_keeps_old_password(client, auth_headers):
    change_password(client, auth_headers, current="Sai@0000", new="Moi@5678")

    assert login(client, PASSWORD).status_code == 200


def test_change_password_same_as_current_returns_400(client, auth_headers):
    response = change_password(client, auth_headers, current=PASSWORD, new=PASSWORD)
    assert response.status_code == 400
    assert response.json()["detail"] == "Mật khẩu này đã được sử dụng."


def test_change_password_same_as_current_keeps_sessions(client, auth_headers):
    # Bị từ chối → không đổi gì, phiên không bị thu hồi: vẫn đăng nhập được bằng mật khẩu cũ
    change_password(client, auth_headers, current=PASSWORD, new=PASSWORD)
    assert login(client, PASSWORD).status_code == 200


def test_change_password_weak_new_returns_422(client, auth_headers):
    response = change_password(client, auth_headers, current=PASSWORD, new="abc12345")

    assert response.status_code == 422


def test_change_password_mismatch_returns_422(client, auth_headers):
    response = change_password(
        client, auth_headers, current=PASSWORD, new="Moi@5678", confirm="Moi@9999"
    )

    assert response.status_code == 422


def test_change_password_without_token_returns_401(client):
    response = change_password(client, {}, current=PASSWORD, new="Moi@5678")

    assert response.status_code == 401
