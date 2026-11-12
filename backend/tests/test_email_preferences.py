"""Test tùy chọn nhận email (module 01 · Tuấn · 11/11/2026)."""

import pytest

from app.models import Users
from app.services import email_preference_service
from tests.conftest import STUDENT_EMAIL

URL = "/api/me/email-preferences"
DEFAULTS = {"review_reminder": True, "course_suggestions": False, "feedback_replies": True}


def test_defaults_when_never_saved(client, student_headers):
    assert client.get(URL, headers=student_headers).json() == DEFAULTS


def test_patch_part_keeps_the_rest(client, student_headers):
    body = client.patch(URL, headers=student_headers, json={"course_suggestions": True}).json()

    assert body == {**DEFAULTS, "course_suggestions": True}
    assert client.get(URL, headers=student_headers).json() == body
    body = client.patch(URL, headers=student_headers, json={"review_reminder": False}).json()
    assert body == {"review_reminder": False, "course_suggestions": True, "feedback_replies": True}


def test_unknown_key_rejected_and_login_required(client, student_headers):
    assert client.patch(URL, headers=student_headers, json={"hack": True}).status_code == 422
    assert client.get(URL).status_code == 401


def test_each_user_has_own_preferences(client, student_headers, admin_headers):
    client.patch(URL, headers=student_headers, json={"feedback_replies": False})
    assert client.get(URL, headers=admin_headers).json() == DEFAULTS


def test_wants_email_for_senders(client, student_headers, db_session):
    uid = db_session.query(Users).filter_by(email=STUDENT_EMAIL).one().user_id
    assert email_preference_service.wants_email(db_session, uid, "course_suggestions") is False
    client.patch(URL, headers=student_headers, json={"course_suggestions": True})
    db_session.expire_all()
    assert email_preference_service.wants_email(db_session, uid, "course_suggestions") is True
    with pytest.raises(ValueError):
        email_preference_service.wants_email(db_session, uid, "khong_co")
