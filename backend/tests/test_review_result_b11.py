"""Test B11 — API kết quả trả thêm lý do từng ý, nhận xét chung, chấm bởi AI / từ khóa, "đang xem lại"
(module 09 · Tuấn · 16/11/2026). Không gọi Gemini (AI giả).

Chạy:  python -m pytest tests/test_review_result_b11.py -v      (trong thư mục backend)
"""

# ruff: noqa: F811 — fixture import từ test_review_api; pytest truyền qua TÊN tham số

from app.ai.review import MockAI
from app.ai.review.base import AIUnavailableError, EssayGrade
from app.models import ReviewAnswer, ReviewAttempt
from app.services import review_service
from tests.test_review_api import bank_312, start, user_of  # noqa: F401 — fixture


def essays_of(db_session, attempt_id):
    return [
        a
        for a in db_session.query(ReviewAnswer).filter_by(attempt_id=attempt_id).order_by(ReviewAnswer.position)
        if a.question.type == "essay"
    ]


def answer_with_model_answer(client, headers, db_session, attempt_id, essay):
    text = essay.question.explanation.split(":", 1)[-1].strip()
    client.patch(f"/api/review-attempts/{attempt_id}/answers", headers=headers,
                 json={"answers": [{"position": essay.position, "text_answer": text}]})  # fmt: skip
    return text


class ExplainingAI(MockAI):
    """Giống AI thật: chấm bằng từ khóa nhưng trả kèm lý do từng ý + nhận xét chung."""

    name = "gemini"

    def grade_essay_detailed(self, question, answer):
        items = [{**r, "reason": f"Lý do ý {i}"} for i, r in enumerate(self.grade_essay(question, answer), start=1)]
        return EssayGrade(items=items, feedback="Bài làm tốt, nêu đủ ý.", prompt_version="grade-en-v2")


class DownAI(MockAI):
    name = "gemini"

    def grade_essay(self, question, answer):
        raise AIUnavailableError("hết lượt")


def result_question(result, position):
    return next(q for q in result["questions"] if q["position"] == position)


def test_ai_graded_essay_returns_reason_feedback_and_ai_label(client, bank_312, student_headers, db_session):
    attempt_id = start(client, student_headers)["attempt_id"]
    essay = essays_of(db_session, attempt_id)[0]
    answer_with_model_answer(client, student_headers, db_session, attempt_id, essay)

    result = review_service.submit_attempt(db_session, user_of(db_session), attempt_id, ai=ExplainingAI())
    q = result_question(result, essay.position)

    assert q["graded_by"] == "ai" and q["needs_review"] is False
    assert q["feedback"] == "Bài làm tốt, nêu đủ ý."
    assert [r["reason"] for r in q["rubric"]] == [f"Lý do ý {i}" for i in range(1, len(q["rubric"]) + 1)]


def test_mock_mode_is_labelled_keyword_not_ai(client, bank_312, student_headers, db_session):
    """AI_MODE=mock thực chất chấm từ khóa → không được ghi "Chấm bởi AI" với người học."""
    attempt_id = start(client, student_headers)["attempt_id"]
    essay = essays_of(db_session, attempt_id)[0]
    answer_with_model_answer(client, student_headers, db_session, attempt_id, essay)

    result = review_service.submit_attempt(db_session, user_of(db_session), attempt_id, ai=MockAI())
    q = result_question(result, essay.position)
    assert q["graded_by"] == "keyword" and q["feedback"] is None


def test_ai_failure_falls_back_and_is_labelled_keyword(client, bank_312, student_headers, db_session):
    attempt_id = start(client, student_headers)["attempt_id"]
    essay = essays_of(db_session, attempt_id)[0]
    answer_with_model_answer(client, student_headers, db_session, attempt_id, essay)

    result = review_service.submit_attempt(db_session, user_of(db_session), attempt_id, ai=DownAI())
    assert result_question(result, essay.position)["graded_by"] == "keyword"


def test_blank_essay_and_mcq_have_no_grading_label(client, bank_312, student_headers, db_session):
    attempt_id = start(client, student_headers)["attempt_id"]
    result = review_service.submit_attempt(db_session, user_of(db_session), attempt_id, ai=ExplainingAI())
    for q in result["questions"]:
        assert q["graded_by"] is None and q["needs_review"] is False and q["feedback"] is None


def test_needs_review_flag_reaches_the_result(client, bank_312, student_headers, db_session):
    """Điểm AI lệch chấm từ khóa > 3 sau khi chấm lại (B8) → kết quả báo "đang xem lại"."""

    class StingyAI(MockAI):
        name = "gemini"

        def grade_essay(self, question, answer):  # luôn chấm 0 → lệch xa chấm từ khóa (đáp án mẫu được 10)
            return [{"result": "none", "points": 0.0, "evidence": None} for _ in question["rubric"]]

    attempt_id = start(client, student_headers)["attempt_id"]
    essay = essays_of(db_session, attempt_id)[0]
    answer_with_model_answer(client, student_headers, db_session, attempt_id, essay)

    result = review_service.submit_attempt(db_session, user_of(db_session), attempt_id, ai=StingyAI())
    q = result_question(result, essay.position)
    assert q["needs_review"] is True and q["graded_by"] == "ai" and q["points"] == 0


def test_old_attempt_without_pipeline_trace_still_renders(client, bank_312, student_headers, db_session):
    """Lượt chấm trước B6 (trace không có essays / keyword_fallback) → giá trị mặc định, không lỗi."""
    attempt_id = start(client, student_headers)["attempt_id"]
    essay = essays_of(db_session, attempt_id)[0]
    answer_with_model_answer(client, student_headers, db_session, attempt_id, essay)
    review_service.submit_attempt(db_session, user_of(db_session), attempt_id, ai=MockAI())

    attempt = db_session.get(ReviewAttempt, attempt_id)
    attempt.trace = {**attempt.trace, "grading": {"ai": "gemini"}}  # dạng cũ: chỉ có tên AI
    db_session.commit()

    response = client.get(f"/api/me/review-history/{attempt_id}", headers=student_headers)
    assert response.status_code == 200, response.text
    q = result_question(response.json(), essay.position)
    assert q["graded_by"] == "ai" and q["needs_review"] is False and q["feedback"] is None


def test_api_response_contains_new_fields(client, bank_312, student_headers, db_session):
    attempt_id = start(client, student_headers)["attempt_id"]
    essay = essays_of(db_session, attempt_id)[0]
    answer_with_model_answer(client, student_headers, db_session, attempt_id, essay)
    review_service.submit_attempt(db_session, user_of(db_session), attempt_id, ai=ExplainingAI())

    response = client.get(f"/api/me/review-history/{attempt_id}", headers=student_headers)
    q = result_question(response.json(), essay.position)
    assert {"graded_by", "needs_review", "feedback"} <= set(q) and "reason" in q["rubric"][0]
    assert q["feedback"] == "Bài làm tốt, nêu đủ ý."
