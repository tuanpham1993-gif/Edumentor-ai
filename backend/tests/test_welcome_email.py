"""Test email chào mừng khi đăng ký (module 01 · Tuấn · 12/11/2026). Không gửi thật (conftest chặn SMTP)."""

from app.core import email as email_module
from app.routers.v1.endpoints import auth as auth_router

BODY = {"full_name": "Người Mới", "email": "Moi@Example.com", "password": "Test@1234", "confirm_password": "Test@1234"}


def test_register_sends_welcome_email_to_the_new_address(client, monkeypatch):
    sent = []
    monkeypatch.setattr(auth_router, "send_welcome_email", lambda to, name: sent.append((to, name)))

    response = client.post("/api/auth/register", json=BODY)

    assert response.status_code == 201
    assert sent == [("moi@example.com", "Người Mới")]  # đúng email vừa đăng ký (đã chuẩn hóa chữ thường)


def test_no_email_when_register_fails(client, monkeypatch):
    sent = []
    monkeypatch.setattr(auth_router, "send_welcome_email", lambda to, name: sent.append(to))
    client.post("/api/auth/register", json=BODY)
    sent.clear()

    assert client.post("/api/auth/register", json=BODY).status_code == 409  # email trùng
    assert client.post("/api/auth/register", json={**BODY, "email": "x@y.com", "password": "yeu"}).status_code == 422
    assert sent == []


def test_welcome_email_content(monkeypatch):
    captured = {}
    monkeypatch.setattr(email_module, "send_email", lambda to, subject, body: captured.update(to=to, subject=subject, body=body))

    email_module.send_welcome_email("an@gmail.com", "Nguyễn An")

    assert captured["to"] == "an@gmail.com"
    assert captured["subject"] == "Chào mừng bạn đến với EduMentor AI"
    assert "Xin chào Nguyễn An" in captured["body"] and "an@gmail.com" in captured["body"]
    assert "/login" in captured["body"]


def test_tests_never_send_real_email(client):
    from app.core.config import settings

    assert settings.SMTP_HOST == "" and not email_module._smtp_configured()
