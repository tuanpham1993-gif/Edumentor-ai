"""Test thông báo trong app — chuông trên header (module 01 · Tuấn · 11/11/2026).

Chạy:  python -m pytest tests/test_notifications.py -v      (trong thư mục backend)
"""
# ruff: noqa: F811 — fixture bank_312 import từ test_review_api; pytest truyền qua TÊN tham số

from datetime import UTC, datetime, timedelta

import pytest

from app.models import Notification, Users
from app.services import notification_service
from tests.conftest import STUDENT_EMAIL, TEST_PASSWORD, _login_headers
from tests.test_review_api import bank_312, start  # noqa: F401 — bank_312 là fixture
from tests.test_review_submit import (
    answer_essays_with_model_answers,
    answer_mcq,
    submit_url,
)

URL = "/api/me/notifications"


def user_id(db_session, email=STUDENT_EMAIL):
    return db_session.query(Users).filter_by(email=email).one().user_id


def titles(client, headers, **params):
    return [n["title"] for n in client.get(URL, headers=headers, params=params).json()["items"]]


# ─────────────── Sự kiện tạo thông báo ───────────────


def test_register_creates_welcome(client, student_headers):
    body = client.get(URL, headers=student_headers).json()

    assert body["unread_count"] == 1 and body["total"] == 1
    item = body["items"][0]
    assert item["type"] == "welcome" and item["link"] == "/me/skills" and item["is_read"] is False


def test_change_password_creates_security_notice(client, student_headers):
    response = client.post(
        "/api/me/change-password",
        headers=student_headers,
        json={"current_password": TEST_PASSWORD, "new_password": "Moi@12345", "confirm_new_password": "Moi@12345"},
    )
    assert response.status_code == 200

    headers = _login_headers(client, STUDENT_EMAIL, "Moi@12345")
    assert titles(client, headers)[0] == "Mật khẩu của bạn vừa được thay đổi"


def test_wrong_current_password_creates_nothing(client, student_headers):
    client.post(
        "/api/me/change-password",
        headers=student_headers,
        json={"current_password": "Sai@12345", "new_password": "Moi@12345", "confirm_new_password": "Moi@12345"},
    )
    assert client.get(URL, headers=student_headers).json()["total"] == 1  # chỉ có "welcome"


def test_reset_password_creates_security_notice(client, student_headers, db_session):
    from app.services import auth_service

    token = auth_service.forgot_password(db_session, email=STUDENT_EMAIL)
    client.post("/api/auth/reset-password", json={"token": token, "new_password": "Moi@12345", "confirm_new_password": "Moi@12345"})

    headers = _login_headers(client, STUDENT_EMAIL, "Moi@12345")
    assert titles(client, headers)[0] == "Mật khẩu của bạn vừa được đặt lại"


def test_review_pass_creates_result_and_completed(client, bank_312, student_headers, db_session):
    attempt_id = start(client, student_headers)["attempt_id"]
    answer_mcq(client, student_headers, db_session, attempt_id, correct=12)
    answer_essays_with_model_answers(client, student_headers, db_session, attempt_id)
    client.post(submit_url(attempt_id), headers=student_headers)

    items = client.get(URL, headers=student_headers).json()["items"]
    by_type = {n["type"]: n for n in items}
    assert by_type["review_graded"]["title"] == "Kết quả ôn tập: 10/10 — Đạt"
    assert by_type["review_graded"]["link"] == f"/review/{attempt_id}/result"
    assert by_type["course_completed"]["title"].startswith("Chúc mừng! Bạn đã hoàn thành khóa")


def test_review_fail_creates_only_result(client, bank_312, student_headers, db_session):
    attempt_id = start(client, student_headers)["attempt_id"]
    answer_mcq(client, student_headers, db_session, attempt_id, correct=0)
    client.post(submit_url(attempt_id), headers=student_headers)

    types = [n["type"] for n in client.get(URL, headers=student_headers).json()["items"]]
    assert "review_graded" in types and "course_completed" not in types
    assert titles(client, student_headers)[0] == "Kết quả ôn tập: 0/10 — Chưa đạt"


def test_same_source_is_not_duplicated(db_session, student_headers):
    uid = user_id(db_session)
    first = notification_service.notify(db_session, uid, "review_graded", "A", source_id=7)
    second = notification_service.notify(db_session, uid, "review_graded", "A lần 2", source_id=7)

    assert first is not None and second is None
    assert db_session.query(Notification).filter_by(user_id=uid, source_id=7).count() == 1


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [({"type_": "khong_co"}, "chưa khai báo"), ({"link": "https://lua-dao.example"}, "nội bộ")],
)
def test_notify_rejects_unknown_type_and_external_link(db_session, student_headers, kwargs, message):
    args = {"type_": "welcome", "title": "x", **kwargs}
    with pytest.raises(ValueError, match=message):
        notification_service.notify(db_session, user_id(db_session), args.pop("type_"), args.pop("title"), **args)


# ─────────────── Tab Tất cả / Chưa đọc, đánh dấu đã đọc ───────────────


def seed(db_session, n=3):
    uid = user_id(db_session)
    for i in range(n):
        notification_service.notify(db_session, uid, "review_graded", f"Kết quả {i}", source_id=100 + i)
    db_session.commit()
    return uid


def test_tabs_all_and_unread(client, student_headers, db_session):
    seed(db_session)  # + 1 welcome = 4
    first_id = client.get(URL, headers=student_headers).json()["items"][0]["notification_id"]
    client.patch(f"{URL}/{first_id}/read", headers=student_headers)

    all_tab = client.get(URL, headers=student_headers).json()
    unread_tab = client.get(URL, headers=student_headers, params={"unread_only": True}).json()

    assert all_tab["total"] == 4 and all_tab["unread_count"] == 3
    assert unread_tab["total"] == 3 and all(not n["is_read"] for n in unread_tab["items"])
    assert first_id not in [n["notification_id"] for n in unread_tab["items"]]
    assert client.get(f"{URL}/unread-count", headers=student_headers).json() == {"unread_count": 3}


def test_newest_first_and_pagination(client, student_headers, db_session):
    seed(db_session, 5)
    page1 = client.get(URL, headers=student_headers, params={"size": 2}).json()
    page2 = client.get(URL, headers=student_headers, params={"size": 2, "page": 2}).json()

    assert [n["title"] for n in page1["items"]] == ["Kết quả 4", "Kết quả 3"]
    assert [n["title"] for n in page2["items"]] == ["Kết quả 2", "Kết quả 1"]
    assert page1["total"] == 6


def test_mark_all_read(client, student_headers, db_session):
    seed(db_session)
    response = client.post(f"{URL}/read-all", headers=student_headers)

    assert response.json() == {"updated": 4}
    assert client.get(f"{URL}/unread-count", headers=student_headers).json()["unread_count"] == 0


def test_cannot_read_or_mark_other_users_notification(client, student_headers, admin_headers, db_session):
    seed(db_session, 1)
    mine = client.get(URL, headers=student_headers).json()["items"][0]["notification_id"]

    assert client.patch(f"{URL}/{mine}/read", headers=admin_headers).status_code == 404
    assert mine not in [n["notification_id"] for n in client.get(URL, headers=admin_headers).json()["items"]]
    assert client.get(URL).status_code == 401


def test_keeps_at_most_100_and_drops_older_than_90_days(db_session, student_headers):
    uid = user_id(db_session)
    old = Notification(user_id=uid, type="welcome", title="cũ", created_at=datetime.now(UTC) - timedelta(days=91))
    db_session.add(old)
    db_session.flush()
    for i in range(105):
        notification_service.notify(db_session, uid, "review_graded", f"n{i}", source_id=1000 + i)
    db_session.commit()

    rows = db_session.query(Notification).filter_by(user_id=uid).all()
    assert len(rows) == notification_service.KEEP_MAX
    assert "cũ" not in [n.title for n in rows]
