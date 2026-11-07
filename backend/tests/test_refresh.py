"""Test tự động: làm mới token / đăng xuất (module 01 · Tuấn · GĐ6).

Chạy:  python -m pytest tests/test_refresh.py -v      (trong thư mục backend)

Fixture `tokens` đăng ký + đăng nhập rồi trả (access_token, refresh_token)
→ test dùng refresh token như frontend lưu sau khi đăng nhập.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.models.auth_token import RefreshToken
from app.models.user import Users

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
REFRESH_URL = "/api/auth/refresh"
LOGOUT_URL = "/api/auth/logout"
ME_URL = "/api/me"
CHANGE_PW_URL = "/api/me/change-password"
PASSWORD = "Abc@1234"
NEW_PASSWORD = "Moi@5678"
EMAIL = "tuan@gmail.com"
EXPIRED_MESSAGE = "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại."


@pytest.fixture()
def tokens(client):
    """Đăng ký + đăng nhập, trả về (access_token, refresh_token)."""
    client.post(
        REGISTER_URL,
        json={"full_name": "Tuấn", "email": EMAIL, "password": PASSWORD, "confirm_password": PASSWORD},
    )
    body = login(client).json()
    return body["access_token"], body["refresh_token"]


def login(client, password=PASSWORD):
    return client.post(LOGIN_URL, json={"email": EMAIL, "password": password})


def refresh(client, refresh_token):
    return client.post(REFRESH_URL, json={"refresh_token": refresh_token})


def logout(client, refresh_token):
    return client.post(LOGOUT_URL, json={"refresh_token": refresh_token})


def bearer(access_token):
    return {"Authorization": f"Bearer {access_token}"}


# ─────────────── Đăng nhập trả refresh token ───────────────


def test_login_returns_refresh_token(tokens):
    _, refresh_token = tokens

    assert isinstance(refresh_token, str)
    assert len(refresh_token) >= 40  # token_urlsafe(32) ≈ 43 ký tự


def test_refresh_token_stored_as_hash(tokens, db_session):
    _, refresh_token = tokens

    record = db_session.query(RefreshToken).one()
    assert record.token_hash != refresh_token  # DB không lưu token gốc
    assert len(record.token_hash) == 64  # SHA-256 dạng hex
    assert record.revoked_at is None  # còn hiệu lực


# ─────────────── POST /api/auth/refresh ───────────────


def test_refresh_success_returns_new_pair(client, tokens):
    _, refresh_token = tokens

    response = refresh(client, refresh_token)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["refresh_token"] != refresh_token  # xoay vòng: luôn cấp token mới


def test_new_access_token_works(client, tokens):
    _, refresh_token = tokens
    new_access = refresh(client, refresh_token).json()["access_token"]

    response = client.get(ME_URL, headers=bearer(new_access))

    assert response.status_code == 200
    assert response.json()["email"] == EMAIL


def test_new_refresh_token_can_refresh_again(client, tokens):
    _, refresh_token = tokens
    new_refresh = refresh(client, refresh_token).json()["refresh_token"]

    assert refresh(client, new_refresh).status_code == 200


def test_old_refresh_token_used_twice_returns_401(client, tokens):
    _, refresh_token = tokens

    assert refresh(client, refresh_token).status_code == 200
    response = refresh(client, refresh_token)  # token cũ đã bị thu hồi khi xoay vòng

    assert response.status_code == 401
    assert response.json()["detail"] == EXPIRED_MESSAGE


def test_reuse_old_token_revokes_all_sessions(client, tokens):
    """Token cũ bị gửi lại → nghi bị đánh cắp → thu hồi luôn token mới."""
    _, refresh_token = tokens
    new_refresh = refresh(client, refresh_token).json()["refresh_token"]

    refresh(client, refresh_token)  # kẻ gian dùng lại token cũ

    assert refresh(client, new_refresh).status_code == 401


def test_refresh_invalid_token_returns_401(client, tokens):
    response = refresh(client, "abc")

    assert response.status_code == 401
    assert response.json()["detail"] == EXPIRED_MESSAGE


def test_refresh_empty_token_returns_422(client):
    assert refresh(client, "").status_code == 422


def test_refresh_expired_token_returns_401(client, tokens, db_session):
    _, refresh_token = tokens
    record = db_session.query(RefreshToken).one()
    record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)  # đã hết hạn
    db_session.commit()

    assert refresh(client, refresh_token).status_code == 401


def test_refresh_locked_user_returns_401(client, tokens, db_session):
    _, refresh_token = tokens
    user = db_session.query(Users).one()
    user.is_active = False  # admin khóa tài khoản
    db_session.commit()

    assert refresh(client, refresh_token).status_code == 401


# ─────────────── POST /api/auth/logout ───────────────


def test_logout_success_then_refresh_fails(client, tokens):
    _, refresh_token = tokens

    response = logout(client, refresh_token)

    assert response.status_code == 200
    assert response.json()["message"] == "Đã đăng xuất."
    assert refresh(client, refresh_token).status_code == 401


def test_logout_invalid_token_still_200(client):
    assert logout(client, "abc").status_code == 200  # không báo lỗi, frontend cứ xóa token


def test_logout_twice_still_200(client, tokens):
    _, refresh_token = tokens

    assert logout(client, refresh_token).status_code == 200
    assert logout(client, refresh_token).status_code == 200


def test_logout_only_affects_that_device(client, tokens):
    """Đăng nhập 2 thiết bị, đăng xuất máy 1 → máy 2 vẫn refresh được."""
    _, refresh_device_1 = tokens
    refresh_device_2 = login(client).json()["refresh_token"]

    logout(client, refresh_device_1)

    assert refresh(client, refresh_device_2).status_code == 200


# ─────────────── Đổi mật khẩu → đăng xuất mọi nơi ───────────────


def test_change_password_revokes_refresh_tokens(client, tokens):
    access_token, refresh_token = tokens
    client.post(
        CHANGE_PW_URL,
        json={"current_password": PASSWORD, "new_password": NEW_PASSWORD, "confirm_new_password": NEW_PASSWORD},
        headers=bearer(access_token),
    )

    assert refresh(client, refresh_token).status_code == 401


def test_reset_password_revokes_refresh_tokens(client, tokens, monkeypatch):
    """Đặt lại mật khẩu qua email → mọi refresh token cũ bị thu hồi (Q10)."""
    _, refresh_token = tokens
    sent = []
    monkeypatch.setattr(
        "app.routers.v1.endpoints.auth.send_password_reset_email",
        lambda to, token: sent.append(token),
    )
    client.post("/api/auth/forgot-password", json={"email": EMAIL})
    client.post(
        "/api/auth/reset-password",
        json={"token": sent[0], "new_password": NEW_PASSWORD, "confirm_new_password": NEW_PASSWORD},
    )

    assert refresh(client, refresh_token).status_code == 401
