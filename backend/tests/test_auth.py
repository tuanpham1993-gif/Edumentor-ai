"""Test tự động: đăng ký, đăng nhập, GET /me (module 01 · Tuấn · GĐ2, 05/11/2026).

Chạy:  python -m pytest tests/test_auth.py -v      (trong thư mục backend)

Fixture `client` và `db_session` lấy từ tests/conftest.py: mỗi test có một DB SQLite
mới tinh trong RAM → các test không ảnh hưởng nhau và không đụng PostgreSQL thật.
Mỗi test bắt đầu với DB rỗng → test đăng nhập phải tự register() trước.
Mẫu mỗi test: Chuẩn bị → Thực hiện → Kiểm tra (assert).
"""

from app.models.user import Users

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
ME_URL = "/api/me"

VALID_USER = {
    "full_name": "Phạm Tuấn",
    "email": "tuan@gmail.com",
    "password": "Abc@1234",
    "confirm_password": "Abc@1234",
}


def register(client, **changes):
    """Gọi API đăng ký với VALID_USER, cho phép đổi vài trường.
    Ví dụ: register(client, email="khac@x.com")"""
    return client.post(REGISTER_URL, json={**VALID_USER, **changes})


def login(client, email=VALID_USER["email"], password=VALID_USER["password"]):
    return client.post(LOGIN_URL, json={"email": email, "password": password})


# ─────────────── ĐĂNG KÝ ───────────────


def test_register_success(client):
    response = register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "tuan@gmail.com"
    assert body["full_name"] == "Phạm Tuấn"
    assert body["role"] == "student"
    assert "hashed_password" not in body
    assert "password" not in body


def test_register_duplicate_email_returns_409(client):
    first = register(client)
    second = register(client)

    assert first.status_code == 201
    assert second.status_code == 409


def test_register_duplicate_email_different_case_returns_409(client):
    register(client)
    response = register(client, email="TUAN@Gmail.com")

    assert response.status_code == 409


def test_register_weak_password_returns_422(client):
    response = register(client, password="abc12345", confirm_password="abc12345")

    assert response.status_code == 422


def test_register_password_mismatch_returns_422(client):
    response = register(client, confirm_password="Khac@1234")

    assert response.status_code == 422


def test_register_ignores_role_from_client(client):
    response = register(client, role="admin")

    assert response.status_code == 201
    assert response.json()["role"] == "student"


def test_password_is_hashed_in_database(client, db_session):
    register(client)

    user = db_session.query(Users).filter_by(email="tuan@gmail.com").one()
    assert user.hashed_password != "Abc@1234"
    assert user.hashed_password.startswith("$2b$")


# ─────────────── ĐĂNG NHẬP ───────────────


def test_login_success_returns_token_and_user(client):
    register(client)
    response = login(client)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "tuan@gmail.com"


def test_login_email_case_insensitive(client):
    register(client)
    response = login(client, email="TUAN@GMAIL.COM")

    assert response.status_code == 200


def test_login_wrong_password_returns_401(client):
    register(client)
    response = login(client, password="Sai@1234")

    assert response.status_code == 401


def test_login_unknown_email_returns_same_message(client):
    register(client)
    wrong_pw = login(client, password="Sai@1234")
    unknown = login(client, email="khong-co@x.com")

    assert wrong_pw.status_code == 401
    assert unknown.status_code == 401
    assert wrong_pw.json()["detail"] == unknown.json()["detail"]


# ─────────────── /me ───────────────


def test_me_with_valid_token_returns_profile(client):
    register(client)
    token = login(client).json()["access_token"]

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "tuan@gmail.com"


def test_me_without_token_returns_401(client):
    response = client.get(ME_URL)

    assert response.status_code == 401
