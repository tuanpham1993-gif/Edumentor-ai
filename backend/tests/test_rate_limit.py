"""Test giới hạn tần suất đăng nhập / đăng ký / quên & đặt lại mật khẩu (module 01 · Tuấn · 19/11/2026).

Chạy:  python -m pytest tests/test_rate_limit.py -v      (trong thư mục backend)
"""

import pytest

from app.core import rate_limit as rl
from app.core.config import settings
from tests.conftest import TEST_PASSWORD

LOGIN = "/api/auth/login"
EMAIL = "student.test@edumentor.vn"


def login(client, password, email=EMAIL, ip=None):
    headers = {"X-Real-IP": ip} if ip else {}
    return client.post(LOGIN, json={"email": email, "password": password}, headers=headers)


# ─────────────── Bộ đếm cửa sổ trượt ───────────────


def test_sliding_window_counts_and_expires():
    now = [0.0]
    limiter = rl.RateLimiter(limit=3, window=60, clock=lambda: now[0])
    for _ in range(3):
        assert limiter.retry_after("k") == 0
        limiter.hit("k")
    assert limiter.retry_after("k") == 60  # lần đầu ở t=0 → chờ tới t=60
    now[0] = 30
    assert limiter.retry_after("k") == 30
    now[0] = 60.01
    assert limiter.retry_after("k") == 0  # lần cũ nhất ra khỏi cửa sổ
    assert limiter.retry_after("other") == 0  # mỗi khóa đếm riêng


def test_reset_clears_one_key():
    limiter = rl.RateLimiter(limit=1, window=60)
    limiter.hit("a")
    limiter.hit("b")
    limiter.reset("a")
    assert limiter.retry_after("a") == 0 and limiter.retry_after("b") > 0


# ─────────────── Đăng nhập ───────────────


def test_five_wrong_passwords_lock_the_email(client, student_headers):
    for _ in range(5):
        assert login(client, "Wrong@123").status_code == 401
    locked = login(client, TEST_PASSWORD)  # đúng mật khẩu nhưng email đang bị khóa tạm
    assert locked.status_code == 429
    assert "thử lại sau 15 phút" in locked.json()["detail"]
    assert 0 < int(locked.headers["Retry-After"]) <= 15 * 60


def test_correct_login_resets_failures(client, student_headers):
    for _ in range(4):
        assert login(client, "Wrong@123").status_code == 401
    assert login(client, TEST_PASSWORD).status_code == 200
    for _ in range(4):  # bộ đếm đã về 0 → lại được sai 4 lần mà chưa bị khóa
        assert login(client, "Wrong@123").status_code == 401
    assert login(client, TEST_PASSWORD).status_code == 200


def test_lock_is_per_email_and_case_insensitive(client, student_headers):
    for _ in range(5):
        login(client, "Wrong@123", email="Student.Test@EduMentor.vn")
    assert login(client, TEST_PASSWORD).status_code == 429  # cùng email, khác hoa thường
    assert login(client, "Wrong@123", email="someone.else@edumentor.vn").status_code == 401  # email khác vẫn thử được


def test_unknown_email_is_counted_the_same(client):
    """Email chưa đăng ký cũng bị khóa sau 5 lần → không dò được email nào tồn tại qua mã 429."""
    for _ in range(5):
        assert login(client, "Wrong@123", email="ghost@edumentor.vn").status_code == 401
    assert login(client, "Wrong@123", email="ghost@edumentor.vn").status_code == 429


def test_one_ip_trying_many_accounts_is_limited(client):
    for i in range(30):
        assert login(client, "Wrong@123", email=f"user{i}@edumentor.vn", ip="10.0.0.9").status_code == 401
    assert login(client, "Wrong@123", email="user99@edumentor.vn", ip="10.0.0.9").status_code == 429
    assert login(client, "Wrong@123", email="user99@edumentor.vn", ip="10.0.0.10").status_code == 401  # IP khác


def test_disabled_by_setting(client, student_headers, monkeypatch):
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", False)
    for _ in range(7):
        login(client, "Wrong@123")
    assert login(client, TEST_PASSWORD).status_code == 200


# ─────────────── Quên / đặt lại mật khẩu, đăng ký ───────────────


def test_forgot_password_limited_per_email(client, student_headers):
    for _ in range(3):
        assert client.post("/api/auth/forgot-password", json={"email": EMAIL}).status_code == 200
    assert client.post("/api/auth/forgot-password", json={"email": EMAIL}).status_code == 429
    assert client.post("/api/auth/forgot-password", json={"email": "other@edumentor.vn"}).status_code == 200


def test_reset_password_limited_per_ip(client):
    body = {"token": "khong-hop-le", "new_password": "Abc@12345", "confirm_new_password": "Abc@12345"}
    for _ in range(10):
        assert client.post("/api/auth/reset-password", json=body).status_code == 400
    assert client.post("/api/auth/reset-password", json=body).status_code == 429


@pytest.mark.parametrize("n", [5])
def test_register_limited_per_ip(client, n):
    def register(i):
        return client.post("/api/auth/register", json={
            "full_name": "Người Thử", "email": f"new{i}@edumentor.vn",
            "password": "Abc@12345", "confirm_password": "Abc@12345"})  # fmt: skip

    for i in range(n):
        assert register(i).status_code == 201
    assert register(n).status_code == 429
