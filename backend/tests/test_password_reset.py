"""Test tự động: quên / đặt lại mật khẩu (module 01 · Tuấn · GĐ5, 06/11/2026).

Chạy:  python -m pytest tests/test_password_reset.py -v      (trong thư mục backend)

Fixture `sent_emails` dùng monkeypatch thay hàm gửi email thật bằng hàm ghi lại
(email, token) → test lấy được token như người dùng mở link trong email.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.models.auth_token import PasswordResetToken

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
FORGOT_URL = "/api/auth/forgot-password"
RESET_URL = "/api/auth/reset-password"
PASSWORD = "Abc@1234"
NEW_PASSWORD = "Moi@5678"
EMAIL = "tuan@gmail.com"


@pytest.fixture()
def sent_emails(monkeypatch):
    """Thay hàm gửi email bằng hàm ghi lại (email, token) vào danh sách."""
    sent = []
    monkeypatch.setattr(
        "app.routers.v1.endpoints.auth.send_password_reset_email",
        lambda to, token: sent.append((to, token)),
    )
    return sent


@pytest.fixture()
def registered(client):
    client.post(
        REGISTER_URL,
        json={
            "full_name": "Tuấn",
            "email": EMAIL,
            "password": PASSWORD,
            "confirm_password": PASSWORD,
        },
    )


def forgot(client, email=EMAIL):
    return client.post(FORGOT_URL, json={"email": email})


def reset(client, token, new=NEW_PASSWORD, confirm=None):
    return client.post(
        RESET_URL,
        json={
            "token": token,
            "new_password": new,
            "confirm_new_password": confirm or new,
        },
    )


def login(client, password):
    return client.post(LOGIN_URL, json={"email": EMAIL, "password": password})


# ─────────────── POST /api/auth/forgot-password ───────────────


def test_forgot_unknown_email_same_message_and_no_email(client, sent_emails):
    response = forgot(client, "khong-co@x.com")

    assert response.status_code == 200
    assert sent_emails == []


def test_forgot_known_email_sends_one_email(client, registered, sent_emails):
    response = forgot(client)

    assert response.status_code == 200
    assert len(sent_emails) == 1
    assert sent_emails[0][0] == EMAIL


def test_forgot_same_message_for_known_and_unknown(client, registered, sent_emails):
    known = forgot(client)
    unknown = forgot(client, "khong-co@x.com")

    assert known.status_code == unknown.status_code == 200
    assert known.json() == unknown.json()  # không lộ email nào đã đăng ký


def test_token_stored_as_hash(client, registered, sent_emails, db_session):
    forgot(client)
    token = sent_emails[0][1]

    record = db_session.query(PasswordResetToken).one()
    assert record.token_hash != token  # DB không lưu token gốc
    assert len(record.token_hash) == 64  # SHA-256 dạng hex


# ─────────────── POST /api/auth/reset-password ───────────────


def test_reset_success_then_login_with_new_password(client, registered, sent_emails):
    forgot(client)
    token = sent_emails[0][1]

    response = reset(client, token)

    assert response.status_code == 200
    assert login(client, NEW_PASSWORD).status_code == 200
    assert login(client, PASSWORD).status_code == 401


def test_reset_token_used_twice_returns_400(client, registered, sent_emails):
    forgot(client)
    token = sent_emails[0][1]

    assert reset(client, token).status_code == 200
    assert reset(client, token, new="Khac@9999").status_code == 400  # dùng một lần


def test_reset_invalid_token_returns_400(client, registered):
    response = reset(client, "abc")

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn."
    )


def test_old_link_invalid_after_new_request(client, registered, sent_emails):
    forgot(client)
    forgot(client)
    old_token, new_token = sent_emails[0][1], sent_emails[1][1]

    assert reset(client, old_token).status_code == 400  # link cũ đã bị vô hiệu
    assert reset(client, new_token).status_code == 200


def test_reset_expired_token_returns_400(client, registered, sent_emails, db_session):
    forgot(client)
    token = sent_emails[0][1]
    record = db_session.query(PasswordResetToken).one()
    record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)  # đã hết hạn
    db_session.commit()

    assert reset(client, token).status_code == 400
    assert login(client, PASSWORD).status_code == 200  # mật khẩu không bị đổi


def test_reset_weak_password_returns_422(client, registered, sent_emails):
    forgot(client)
    token = sent_emails[0][1]

    assert reset(client, token, new="abc12345").status_code == 422
    assert (
        reset(client, token, new=NEW_PASSWORD, confirm="Khac@9999").status_code == 422
    )
