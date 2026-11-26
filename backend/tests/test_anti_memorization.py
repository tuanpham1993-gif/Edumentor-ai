"""G3e — chống học thuộc đáp án (Tuấn · 25/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md D29, mục 7.6).

P2 tránh câu của 3 lượt nộp gần nhất (lặp thì lặp câu cũ nhất) · P3 lượt chưa Đạt ẩn bài mẫu tự luận ·
P4 bài chép bài mẫu → cờ "cần xem lại", không đổi điểm. Chạy:  python -m pytest tests/test_anti_memorization.py -v
"""

import random

import pytest

from app.ai.review.mock_ai import pick_from_bank
from app.ai.review.pipeline.essay import copied_model_answer
from app.core.config import settings
from app.models import ReviewAttempt
from app.repositories import review_repository as repo
from app.services import review_service
from tests.test_review_api import bank_312, start, user_of  # noqa: F401 — fixture khóa 312 (40 câu)

# ─────────────── P2 ───────────────


def test_pick_from_bank_repeats_oldest_first():
    pool = [{"question_id": i, "level": "recognize"} for i in range(1, 5)]
    avoid = {1: 3, 2: 2, 3: 1}  # câu 1: lượt gần nhất · câu 3: lượt cũ nhất · câu 4: chưa làm
    picked = pick_from_bank(pool, {"recognize": 2}, random.Random(0), avoid_question_ids=avoid)
    assert [q["question_id"] for q in picked] == [4, 3]


def _submit_fake(db, attempt_id):
    attempt = db.get(ReviewAttempt, attempt_id)
    attempt.status, attempt.score, attempt.passed = "graded", 4, False
    db.commit()
    return {a.question_id for a in attempt.answers}


def test_recent_attempts_penalty(client, bank_312, student_headers, db_session):  # noqa: F811
    first = _submit_fake(db_session, start(client, student_headers)["attempt_id"])
    second = _submit_fake(db_session, start(client, student_headers)["attempt_id"])
    user = user_of(db_session)
    recent = repo.recent_submitted_question_ids(db_session, user.user_id, 312, attempts=3)
    assert set(recent) == first | second
    assert all(recent[q] == 3 for q in second)  # lượt gần nhất phạt cao nhất
    assert all(recent[q] == 2 for q in first - second)
    _, avoid = review_service.recent_avoid(db_session, user.user_id, 312)
    assert set(avoid) >= first | second


def test_third_attempt_avoids_first_two(client, bank_312, student_headers, db_session, monkeypatch):  # noqa: F811
    first = _submit_fake(db_session, start(client, student_headers)["attempt_id"])
    second = _submit_fake(db_session, start(client, student_headers)["attempt_id"])
    third = {a.question_id for a in db_session.get(ReviewAttempt, start(client, student_headers)["attempt_id"]).answers}
    # 40 câu, mỗi đề 15 → lượt 3 chỉ được lặp phần thiếu và lặp câu của lượt 1 (cũ hơn) trước lượt 2
    assert len(third & second) <= len(third & first)
    monkeypatch.setattr(settings, "REVIEW_AVOID_LAST_ATTEMPTS", 1)  # cấu hình cũ: chỉ tránh 1 lượt
    _, avoid = review_service.recent_avoid(db_session, user_of(db_session).user_id, 312)
    assert len(avoid) >= 15


# ─────────────── P3 ───────────────


def _graded_attempt(client, headers, db, *, passed):
    attempt_id = start(client, headers)["attempt_id"]
    attempt = db.get(ReviewAttempt, attempt_id)
    attempt.status, attempt.score, attempt.passed = "graded", (8 if passed else 4), passed
    for a in attempt.answers:
        a.points = 0
    db.commit()
    return attempt_id


@pytest.mark.parametrize(
    ("reveal", "passed", "essay_hidden", "mcq_hidden"),
    [("mcq_only", False, True, False), ("mcq_only", True, False, False), ("none", False, True, True),
     ("all", False, False, False)],
)  # fmt: skip
def test_result_hides_answers_until_passed(
    client, bank_312, student_headers, db_session, monkeypatch, reveal, passed, essay_hidden, mcq_hidden  # noqa: F811
):
    monkeypatch.setattr(settings, "REVIEW_REVEAL_ON_FAIL", reveal)
    attempt_id = _graded_attempt(client, student_headers, db_session, passed=passed)
    body = client.get(f"/api/me/review-history/{attempt_id}", headers=student_headers).json()
    essays = [q for q in body["questions"] if q["type"] == "essay"]
    mcqs = [q for q in body["questions"] if q["type"] == "mcq"]
    assert all((q["explanation"] is None) == essay_hidden for q in essays)
    assert all(q["answer_hidden"] == essay_hidden for q in essays)
    assert all((q["correct_index"] is None) == mcq_hidden for q in mcqs)
    assert all(q["rubric"] for q in essays)  # ý barem luôn hiện (biết mình thiếu gì)
    assert body["answers_hidden"] == (essay_hidden or mcq_hidden)


# ─────────────── P4 ───────────────

MODEL = "Model answer: A container shares the host operating system kernel, so it does not boot a full guest system."


def test_copied_model_answer_detected():
    copied = "A container shares the host operating system kernel, so it does not boot a full guest system."
    own = "Containers use the same kernel as the host machine. Virtual machines must start their own OS first."
    assert copied_model_answer(MODEL, copied)
    assert copied_model_answer(MODEL, "Answer: " + copied.upper() + " That is why it is fast.")
    assert not copied_model_answer(MODEL, own)
    assert not copied_model_answer("Model answer: x = 6.", "x = 6.")  # bài mẫu quá ngắn → không xét
    assert not copied_model_answer(None, copied)


def test_copy_flag_does_not_change_score():
    from app.ai.review.mock_ai import MockAI
    from app.ai.review.pipeline.essay import grade_essay

    question = {"content": "Why do containers start fast?", "explanation": MODEL,
                "rubric": [{"text": "share kernel", "max_points": 5, "main_keywords": ["kernel"], "sub_keywords": []},
                           {"text": "no guest OS", "max_points": 5, "main_keywords": ["guest"], "sub_keywords": []}]}  # fmt: skip
    copied = MODEL.removeprefix("Model answer: ")
    flagged = grade_essay(MockAI(), question, copied)
    plain = grade_essay(MockAI(), {**question, "explanation": None}, copied)
    assert "copied_model_answer" in flagged.flags and "copied_model_answer" not in plain.flags
    assert flagged.score_10 == plain.score_10
    assert [r["points"] for r in flagged.results] == [r["points"] for r in plain.results]


def test_flag_reason_listed_for_admin():
    from app.services.review_flag_service import REASONS, reasons_for

    attempt = ReviewAttempt(score=4, trace={"grading": {"ai": "gemini", "essays": [
        {"position": 13, "flags": ["copied_model_answer"]}]}})  # fmt: skip
    assert "copied_model_answer" in REASONS
    assert "copied_model_answer" in reasons_for(attempt, 13)
