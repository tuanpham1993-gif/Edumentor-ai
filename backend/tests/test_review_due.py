"""Đến hạn ôn — Q12 guide.md (module 09 · Tuấn · 21/11/2026).

Quy tắc: theo kỹ năng; chỉ kỹ năng Đã biết đã từng ôn đạt; khoảng nhắc 7 → 30 → 90 ngày theo số lần đạt liên tiếp,
lần gần nhất chưa đạt → 7 ngày; quá hạn chỉ nhắc (không hạ Đã biết); chuông ≤ 1 lần / 24 giờ, email ≤ 1 lần / tuần
theo cài đặt "Nhắc ôn tập". Dữ liệu mẫu: khóa 312 (bank_312) — đạt bài khóa = đã ôn mọi kỹ năng của khóa.

Chạy:  python -m pytest tests/test_review_due.py -v      (trong thư mục backend)
"""

# ruff: noqa: F811 — fixture bank_312 import từ test_review_api; pytest truyền qua TÊN tham số

from datetime import UTC, datetime, timedelta

import pytest

from app.core import database
from app.models import EmailPreference, Notification, ReviewAttempt, ReviewDueReminder, UserSkill
from app.services import review_due_service as due
from tests.test_review_api import SKILL_IDS, bank_312, user_of  # noqa: F401 — bank_312 là fixture

NOW = datetime(2026, 12, 1, 9, 0, tzinfo=UTC)
SKILL = SKILL_IDS[0]


def attempt(db, user, days_ago, passed, score=None, now=NOW):
    db.add(
        ReviewAttempt(
            user_id=user.user_id,
            course_id=312,
            status="graded",
            score=score if score is not None else (8 if passed else 3),
            passed=passed,
            submitted_at=now - timedelta(days=days_ago),
        )
    )
    db.flush()


def mark_known(db, user, skill_ids=SKILL_IDS, source="review"):
    for skill_id in skill_ids:
        db.add(UserSkill(user_id=user.user_id, skill_id=skill_id, status="known", source=source))
    db.flush()


@pytest.fixture()
def student(db_session, bank_312):
    return user_of(db_session)


# ─────────────── Tính đến hạn ───────────────


@pytest.mark.parametrize(
    ("history", "interval", "is_due"),
    [
        ([(8, True)], 7, True),  # đạt 1 lần, 8 ngày trước → khoảng 7 ngày → đến hạn
        ([(6, True)], 7, False),  # mới 6 ngày → chưa
        ([(40, True), (10, True)], 30, False),  # đạt 2 lần liên tiếp → 30 ngày
        ([(100, True), (60, True), (31, True)], 90, False),  # 3 lần → 90 ngày
        ([(200, True), (150, True), (100, True), (95, True)], 90, True),  # lần 4 vẫn 90 ngày; 95 ≥ 90 → đến hạn
        ([(40, True), (8, False)], 7, True),  # lần gần nhất chưa đạt → quay về 7 ngày, tính từ lần đó
        ([(40, True), (10, True), (5, False)], 7, False),
    ],
)
def test_interval_grows_with_pass_streak(db_session, student, history, interval, is_due):
    mark_known(db_session, student)
    for days_ago, passed in history:
        attempt(db_session, student, days_ago, passed)

    info = due.due_info(db_session, student.user_id, [SKILL], now=NOW)[SKILL]

    assert info["interval_days"] == interval and info["due"] is is_due
    assert info["due_at"] == NOW - timedelta(days=history[-1][0]) + timedelta(days=interval)
    assert info["last_passed"] is history[-1][1]


def test_only_known_skills_that_were_passed_count(db_session, student):
    mark_known(db_session, student, SKILL_IDS[:1])  # SKILL_IDS[1] chỉ có trong bài ôn, không "Đã biết"
    attempt(db_session, student, 8, False)  # chưa từng đạt → chưa có gì để ôn lại
    assert due.due_info(db_session, student.user_id, now=NOW) == {}

    attempt(db_session, student, 8, True)
    assert set(due.due_info(db_session, student.user_id, now=NOW)) == {SKILL}


def test_self_declared_known_without_review_is_not_due(db_session, student):
    mark_known(db_session, student, source="manual")
    assert due.due_info(db_session, student.user_id, now=NOW) == {}


def test_overdue_does_not_downgrade_known(db_session, student):
    mark_known(db_session, student)
    attempt(db_session, student, 400, True)
    due.run_reminders(db_session, now=NOW)
    statuses = {s.status for s in db_session.query(UserSkill).filter_by(user_id=student.user_id)}
    assert statuses == {"known"}


# ─────────────── Nhắc chuông + email ───────────────


def test_remind_once_bundles_skills_and_never_repeats(db_session, student, capsys):
    mark_known(db_session, student)
    attempt(db_session, student, 8, True)

    first = due.run_reminders(db_session, now=NOW)
    assert first == {"users": 1, "notified": len(SKILL_IDS), "emailed": len(SKILL_IDS)}
    [note] = db_session.query(Notification).filter_by(user_id=student.user_id, type="review_due").all()
    assert note.title == f"Có {len(SKILL_IDS)} kỹ năng đến hạn ôn" and note.link == "/me/courses"
    assert "kỹ năng đến hạn ôn" in capsys.readouterr().out  # SMTP tắt trong test → thư in ra terminal

    again = due.run_reminders(db_session, now=NOW + timedelta(days=2))  # cùng hạn → không nhắc lại
    assert again == {"users": 0, "notified": 0, "emailed": 0}
    assert db_session.query(ReviewDueReminder).count() == len(SKILL_IDS)


def test_bell_at_most_daily_email_at_most_weekly(db_session, student):
    mark_known(db_session, student, SKILL_IDS[:1])
    attempt(db_session, student, 8, True)
    due.run_reminders(db_session, now=NOW)

    # Ôn lại (đạt) → hạn mới sau 30 ngày; tới hạn mới thì nhắc tiếp
    attempt(db_session, student, -1, True)  # 1 ngày sau NOW
    assert due.run_reminders(db_session, now=NOW + timedelta(days=20)) == {"users": 0, "notified": 0, "emailed": 0}
    later = NOW + timedelta(days=32)
    assert due.run_reminders(db_session, now=later) == {"users": 1, "notified": 1, "emailed": 1}
    assert db_session.query(Notification).filter_by(type="review_due").count() == 2


def test_bell_waits_24h_and_email_waits_a_week(db_session, student):
    mark_known(db_session, student, SKILL_IDS[:1])
    attempt(db_session, student, 8, True)
    assert due.run_reminders(db_session, now=NOW)["notified"] == 1

    # Một kỹ năng khác vừa thành "Đã biết" → cũng đến hạn, nhưng vừa nhắc xong
    mark_known(db_session, student, SKILL_IDS[1:2])
    assert due.run_reminders(db_session, now=NOW + timedelta(hours=1)) == {"users": 0, "notified": 0, "emailed": 0}
    # Qua 24 giờ → chuông nhắc kỹ năng mới; email vẫn chờ đủ 1 tuần
    assert due.run_reminders(db_session, now=NOW + timedelta(hours=25)) == {"users": 1, "notified": 1, "emailed": 0}
    assert due.run_reminders(db_session, now=NOW + timedelta(days=7)) == {"users": 1, "notified": 0, "emailed": 1}
    assert db_session.query(Notification).filter_by(type="review_due").count() == 2


def test_email_respects_review_reminder_setting(db_session, student, capsys):
    db_session.add(EmailPreference(user_id=student.user_id, review_reminder=False))
    mark_known(db_session, student)
    attempt(db_session, student, 8, True)

    out = due.run_reminders(db_session, now=NOW)

    assert out["notified"] == len(SKILL_IDS) and out["emailed"] == 0  # chuông vẫn có, email thì không
    assert "đến hạn ôn" not in capsys.readouterr().out


# ─────────────── API + hạ tầng ───────────────


def test_api_returns_due_info(client, db_session, student, student_headers):
    mark_known(db_session, student, SKILL_IDS[:1])
    attempt(db_session, student, 8, True, score=7, now=datetime.now(UTC))  # API dùng giờ thật
    db_session.commit()

    items = client.get(
        "/api/me/review/skills", params={"skill_ids": f"{SKILL},{SKILL_IDS[1]}"}, headers=student_headers
    ).json()["items"]

    first, second = items
    assert first["due"]["due"] is True and first["due"]["last_score"] == 7 and first["due"]["interval_days"] == 7
    assert first["due"]["streak"] == 1 and first["due"]["last_passed"] is True
    assert second["due"] is None  # chưa "Đã biết" → không xét


def test_notification_type_sync_skips_sqlite():
    assert database.sync_notification_types(database.create_engine("sqlite://")) is False


def test_background_job_is_off_by_default():
    # Mặc định tắt (21/11): máy dev cấu hình Gmail không tự gửi email nhắc; bật bằng .env
    assert type(due.settings).model_fields["REVIEW_DUE_JOB_ENABLED"].default is False
    assert due.start_background(lambda: None) is False
