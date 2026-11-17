"""Test T1 — AI chấm quá lâu → "Đang chấm", chấm nốt ở nền (module 09 · Tuấn · 12/11/2026).

    - Tự luận gửi AI SONG SONG (3 câu ≈ thời gian 1 câu).
    - Quá REVIEW_GRADING_TIMEOUT → POST submit trả 202, status "grading", chưa có điểm / đáp án.
    - Nền chờ AI tới REVIEW_GRADING_MAX_WAIT → có điểm + chuông + email; câu AI chưa xong → chấm từ khóa.
    - Luồng nền mất (server khởi động lại) → mở trang lịch sử / kết quả tự chấm lại bằng từ khóa.

Chạy:  python -m pytest tests/test_review_grading_timeout.py -v      (trong thư mục backend)
"""
# ruff: noqa: F811 — fixture bank_312 import từ test_review_api; pytest truyền qua TÊN tham số

import threading
import time
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import sessionmaker

from app.ai.review import MockAI
from app.core import database
from app.core.config import settings
from app.models import ReviewAttempt
from app.models.notification import Notification
from app.services import review_service
from tests.test_review_api import bank_312, start, user_of  # noqa: F401 — bank_312 là fixture
from tests.test_review_submit import answer_essays_with_model_answers, answer_mcq, submit_url


class SlowAI(MockAI):
    """Chấm như mock nhưng chờ `release` (hoặc `delay` giây) trước khi trả — giả Gemini chậm."""

    name = "slow"

    def __init__(self, *, delay: float | None = None):
        self.release = threading.Event()
        self.delay = delay

    def grade_essay(self, question, answer):
        if self.delay is not None:
            time.sleep(self.delay)
        else:
            self.release.wait(timeout=5)
        return super().grade_essay(question, answer)


@pytest.fixture()
def short_wait(monkeypatch, db_session):
    """Chờ đồng bộ 0,2 giây; nền chờ tối đa 3 giây. Phiên DB nền mở trên CÙNG DB test (SQLite trong RAM)."""
    monkeypatch.setattr(settings, "REVIEW_GRADING_TIMEOUT", 0.2)
    monkeypatch.setattr(settings, "REVIEW_GRADING_MAX_WAIT", 3)
    monkeypatch.setattr(database, "SessionLocal", sessionmaker(bind=db_session.get_bind()))


def prepared_attempt(client, headers, db_session):
    attempt_id = start(client, headers)["attempt_id"]
    answer_mcq(client, headers, db_session, attempt_id, correct=12)
    answer_essays_with_model_answers(client, headers, db_session, attempt_id)
    return attempt_id


def detail(client, headers, attempt_id):
    response = client.get(f"/api/me/review-history/{attempt_id}", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


# ─────────────── Song song ───────────────


def test_essays_are_graded_in_parallel(client, bank_312, student_headers, db_session):
    attempt_id = prepared_attempt(client, student_headers, db_session)
    ai = SlowAI(delay=0.4)

    began = time.monotonic()
    result = review_service.submit_attempt(db_session, user_of(db_session), attempt_id, ai=ai)
    elapsed = time.monotonic() - began

    assert result["status"] == "graded" and result["score"] == 10
    assert elapsed < 1.0  # lần lượt sẽ mất ≥ 1,2 giây (3 câu × 0,4)


# ─────────────── Quá 20 giây → "Đang chấm" ───────────────


def test_slow_ai_returns_202_then_finishes_in_background(
    client, bank_312, student_headers, db_session, short_wait, monkeypatch, capsys
):
    attempt_id = prepared_attempt(client, student_headers, db_session)
    ai = SlowAI()
    monkeypatch.setattr(review_service, "get_review_ai", lambda: ai)
    threading.Timer(0.6, ai.release.set).start()  # AI trả lời sau 0,6 giây (> 0,2 giây chờ đồng bộ)

    response = client.post(submit_url(attempt_id), headers=student_headers)

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "grading" and body["score"] is None and body["passed"] is None
    assert body["questions"] == []  # chưa có điểm → chưa lộ đáp án
    # TestClient chạy xong tác vụ nền rồi mới trả → lúc này đã chấm xong BẰNG AI (không phải từ khóa)
    result = detail(client, student_headers, attempt_id)
    assert result["status"] == "graded" and result["score"] == 10 and result["completed_course"] is True
    db_session.expire_all()
    attempt = db_session.get(ReviewAttempt, attempt_id)
    assert attempt.trace["grading"]["ai"] == "slow" and attempt.trace["grading"]["keyword_fallback"] == []
    assert db_session.query(Notification).filter_by(type="review_graded").count() == 1
    assert "Kết quả ôn tập: ĐẠT (10/10)" in capsys.readouterr().out  # email gửi từ luồng nền


def test_ai_never_answers_falls_back_to_keywords_after_max_wait(
    client, bank_312, student_headers, db_session, short_wait, monkeypatch
):
    monkeypatch.setattr(settings, "REVIEW_GRADING_MAX_WAIT", 0.5)
    attempt_id = prepared_attempt(client, student_headers, db_session)
    ai = SlowAI()  # không bao giờ được release trong thời gian chờ
    monkeypatch.setattr(review_service, "get_review_ai", lambda: ai)

    response = client.post(submit_url(attempt_id), headers=student_headers)
    ai.release.set()  # dọn luồng

    assert response.status_code == 202
    result = detail(client, student_headers, attempt_id)
    assert result["status"] == "graded" and result["essay_score"] == 4  # từ khóa vẫn chấm đúng đáp án mẫu
    db_session.expire_all()
    fallbacks = db_session.get(ReviewAttempt, attempt_id).trace["grading"]["keyword_fallback"]
    assert len(fallbacks) == 3 and all("quá thời gian" in f["error"] for f in fallbacks)


def test_grading_attempt_is_locked_and_hides_answers(client, bank_312, student_headers, db_session, short_wait):
    attempt_id = prepared_attempt(client, student_headers, db_session)
    ai = SlowAI()
    jobs = []

    result = review_service.submit_attempt(db_session, user_of(db_session), attempt_id, ai=ai, schedule=jobs.append)

    assert result["status"] == "grading" and len(jobs) == 1
    # Đang chấm: không sửa câu trả lời, không nộp lại; xem chi tiết chỉ thấy "đang chấm"
    patch = client.patch(
        f"/api/review-attempts/{attempt_id}/answers",
        headers=student_headers,
        json={"answers": [{"position": 1, "selected_index": 0}]},
    )
    assert patch.status_code == 409
    assert client.post(submit_url(attempt_id), headers=student_headers).status_code == 409
    shown = detail(client, student_headers, attempt_id)
    assert shown["status"] == "grading" and shown["questions"] == [] and shown["score"] is None
    history = client.get("/api/me/review-history", headers=student_headers).json()
    assert history["items"][0]["status"] == "grading"

    ai.release.set()
    jobs[0]()  # tác vụ nền chạy

    assert detail(client, student_headers, attempt_id)["score"] == 10
    jobs[0]()  # chạy lại lần nữa (vd trùng) → không chấm 2 lần
    assert db_session.query(Notification).filter_by(type="review_graded").count() == 1


# ─────────────── Luồng nền mất ───────────────


def test_stuck_grading_attempt_is_recovered_with_keywords(client, bank_312, student_headers, db_session):
    attempt_id = prepared_attempt(client, student_headers, db_session)
    attempt = db_session.get(ReviewAttempt, attempt_id)
    attempt.status = "grading"  # như server tắt giữa lúc chấm nền
    attempt.submitted_at = datetime.now(UTC) - timedelta(seconds=settings.REVIEW_GRADING_MAX_WAIT + 120)
    db_session.commit()

    result = detail(client, student_headers, attempt_id)

    assert result["status"] == "graded" and result["score"] == 10
    assert db_session.query(Notification).filter_by(type="review_graded").count() == 1


def test_recent_grading_attempt_is_not_recovered_early(client, bank_312, student_headers, db_session):
    attempt_id = prepared_attempt(client, student_headers, db_session)
    attempt = db_session.get(ReviewAttempt, attempt_id)
    attempt.status = "grading"
    attempt.submitted_at = datetime.now(UTC) - timedelta(seconds=5)  # luồng nền có thể vẫn đang chạy
    db_session.commit()

    assert detail(client, student_headers, attempt_id)["status"] == "grading"
