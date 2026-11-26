"""Công cụ soạn đề scripts/bank (27/11/2026): rào chắn xóa lượt thử + kiểm mẫu câu mô tả ý + giới hạn gọi Gemini."""

import json
from datetime import UTC, datetime

import pytest

from app.models import Notification, ReviewAnswer, ReviewAttempt, ReviewQuestion, Skills, Users, UserSkill
from scripts.bank import delete_test_attempt as dta
from scripts.bank.check import template_problems
from scripts.bank.probe_gemini import grade_with_retry, judge

GRADED_AT = datetime(2026, 11, 26, 14, 17, tzinfo=UTC)


def make_attempt(db, *, email="an.0001@example.com", user_id=501, passed=True, first_pass=False, known_by_attempt=True):
    db.add(Users(user_id=user_id, full_name="Học viên thử", email=email, hashed_password="x", role="student"))
    db.add(Skills(skill_id=1108, skill="Messaging Protocols", is_active=True))
    db.flush()
    q = ReviewQuestion(
        skill_id=1108, type="mcq", level="recognize", content="Q?", options=["a", "b", "c", "d"], correct_index=0
    )
    db.add(q)
    db.flush()
    a = ReviewAttempt(user_id=user_id, skill_id=1108, status="graded", score=9, passed=passed, is_first_pass=first_pass)
    db.add(a)
    db.flush()
    db.add(
        ReviewAnswer(
            attempt_id=a.attempt_id, position=1, question_id=q.question_id, selected_index=0, max_points=0.5, points=0.5
        )
    )
    db.add(
        Notification(
            user_id=user_id, type="review_graded", title="Kết quả", source_id=a.attempt_id, created_at=GRADED_AT
        )
    )
    stamp = GRADED_AT if known_by_attempt else datetime(2026, 11, 1, tzinfo=UTC)
    db.add(
        UserSkill(user_id=user_id, skill_id=1108, status="known", source="review", created_at=stamp, updated_at=stamp)
    )
    db.commit()
    return a.attempt_id


def test_refuses_without_local_test_user_list(tmp_path):
    with pytest.raises(dta.Refused, match="test_users.local.json"):
        dta.allowed_user_ids(tmp_path / "test_users.local.json")


@pytest.mark.parametrize(
    ("email", "allowed"),
    [
        ("an.0001@example.com", set()),  # email đúng mẫu nhưng user ID KHÔNG trong danh sách
        ("hoc.vien@gmail.com", {501}),  # user ID trong danh sách nhưng email KHÔNG đúng mẫu (học viên thật)
        ("hoc.vien+hvx@gmail.com", {501}),  # "+hv" không kèm số → không phải bí danh tài khoản thử
    ],
)
def test_refuses_unless_both_conditions_hold(db_session, email, allowed):
    attempt_id = make_attempt(db_session, email=email)
    with pytest.raises(dta.Refused, match="không thuộc tài khoản thử"):
        dta.plan(db_session, attempt_id, allowed)


def test_refuses_attempt_that_completed_a_course(db_session):
    attempt_id = make_attempt(db_session, first_pass=True)
    with pytest.raises(dta.Refused, match="Hoàn thành"):
        dta.plan(db_session, attempt_id, {501})


def test_plan_is_dry_run_and_lists_linked_rows(db_session):
    attempt_id = make_attempt(db_session, email="ten+hv01@gmail.com")
    p = dta.plan(db_session, attempt_id, {501})
    assert dta.counts(p) == {"review_attempts": 1, "review_answers": 1, "notifications": 1, "user_skills": 1}
    assert db_session.get(ReviewAttempt, attempt_id) is not None  # chạy thử không xóa gì


def test_delete_backs_up_first_then_removes_everything(db_session, tmp_path):
    attempt_id = make_attempt(db_session)
    out = tmp_path / "backup.json"
    n = dta.delete(db_session, attempt_id, {501}, out)
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert n == {"review_attempts": 1, "review_answers": 1, "notifications": 1, "user_skills": 1}
    assert len(saved["review_attempts"]) == 1 and len(saved["review_answers"]) == 1
    assert db_session.get(ReviewAttempt, attempt_id) is None
    assert db_session.query(ReviewAnswer).count() == 0 and db_session.query(Notification).count() == 0
    assert db_session.get(UserSkill, (501, 1108)) is None


def test_keeps_known_skill_that_existed_before_the_attempt(db_session, tmp_path):
    attempt_id = make_attempt(db_session, known_by_attempt=False)
    dta.delete(db_session, attempt_id, {501}, tmp_path / "b.json")
    assert db_session.get(UserSkill, (501, 1108)) is not None


def test_no_delete_when_backup_cannot_be_written(db_session, tmp_path, monkeypatch):
    attempt_id = make_attempt(db_session)

    def broken(*_a, **_k):
        raise OSError("đĩa đầy")

    monkeypatch.setattr(dta, "write_json", broken)
    with pytest.raises(OSError):
        dta.delete(db_session, attempt_id, {501}, tmp_path / "b.json")
    assert db_session.get(ReviewAttempt, attempt_id) is not None


@pytest.mark.parametrize(
    ("text", "problem"),
    [
        ("Non-confirmable messages save resources (any one of: energy, bandwidth, fewer messages).", None),
        ("Non-confirmable messages save resources (any one of: energy and bandwidth).", "'and'"),
        ("QoS 0 (both needed: at most once; the message may be lost).", None),
        ("QoS 0 (both needed: at most once).", "≥ 2 phần"),
        ("Non-confirmable messages save energy and bandwidth.", "ngoài mẫu"),
        ("The sensor and the bulb are mapped to the perception layer (both needed: sensor; bulb).", "ngoài mẫu"),
        ("Perception layer mapping (both needed: the motion sensor; the smart bulb or relay).", None),
        ("CoAP runs over unreliable UDP", None),
    ],
)
def test_rubric_text_templates(text, problem):
    found = template_problems("X-TL-01", 1, text)
    assert (found == []) if problem is None else (len(found) == 1 and problem in found[0])


def test_gemini_retry_waits_then_succeeds():
    from app.ai.review.base import AIUnavailableError

    calls, waits = [], []

    class FlakyAI:
        def grade_essay_detailed(self, question, answer):
            calls.append(1)
            if len(calls) < 3:
                raise AIUnavailableError("Gemini trả HTTP 429 RESOURCE_EXHAUSTED")
            return "ok"

    assert grade_with_retry(FlakyAI(), {}, "x", sleep=waits.append) == "ok"
    assert waits == [20, 40]


def test_judge_rules():
    assert judge({"both": True, "variant": "A", "gemini": 0, "keyword": 5}) == "OK"  # ý both nêu thiếu → Gemini none
    assert judge({"both": True, "variant": "A", "gemini": 5, "keyword": 5}) == "LỆCH"
    assert judge({"both": False, "variant": "A", "gemini": 0, "keyword": 3}) == "LỆCH"
    assert judge({"both": False, "variant": "B", "gemini": 2, "keyword": 2}) == "OK"
