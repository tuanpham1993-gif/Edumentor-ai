"""Test GĐ3: nộp bài, chấm điểm, Hoàn thành khóa + kỹ năng, email, lịch sử, vết admin (module 09 · Tuấn).

Chạy:  python -m pytest tests/test_review_submit.py -v      (trong thư mục backend)
"""
# ruff: noqa: F811 — fixture bank_312 import từ test_review_api; pytest truyền qua TÊN tham số

import pytest

from app.ai.review import MockAI
from app.ai.review.base import AIUnavailableError
from app.models import ReviewAnswer, ReviewAttempt, UserSkill
from app.services import course_gateway, review_service
from tests.test_review_api import SKILL_IDS, bank_312, start, user_of  # noqa: F401 — bank_312 là fixture

LIST_TUPLE_ANSWER = "List thì sửa được còn tuple thì không sửa được. List dùng ngoặc vuông. Tuple thì dùng ngoặc tròn."


def submit_url(attempt_id):
    return f"/api/review-attempts/{attempt_id}/submit"


def answers_of(db_session, attempt_id):
    return db_session.query(ReviewAnswer).filter_by(attempt_id=attempt_id).order_by(ReviewAnswer.position).all()


def correct_display_index(answer):
    return answer.option_order.index(answer.question.correct_index)


def answer_mcq(client, headers, db_session, attempt_id, *, correct: int):
    """Trả lời ĐÚNG `correct` câu trắc nghiệm đầu tiên, SAI các câu còn lại."""
    payload = []
    for a in answers_of(db_session, attempt_id):
        if a.question.type == "mcq":
            right = correct_display_index(a)
            payload.append({"position": a.position, "selected_index": right if correct > 0 else (right + 1) % 4})
            correct -= 1
    response = client.patch(f"/api/review-attempts/{attempt_id}/answers", headers=headers, json={"answers": payload})
    assert response.status_code == 200, response.text


def answer_essays_with_model_answers(client, headers, db_session, attempt_id):
    payload = [
        {"position": a.position, "text_answer": a.question.explanation.removeprefix("Đáp án mẫu: ")}
        for a in answers_of(db_session, attempt_id)
        if a.question.type == "essay"
    ]
    client.patch(f"/api/review-attempts/{attempt_id}/answers", headers=headers, json={"answers": payload})


def submit(client, headers, attempt_id):
    response = client.post(submit_url(attempt_id), headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


# ─────────────── Chấm điểm ───────────────


def test_all_correct_scores_10_and_completes_course(client, bank_312, student_headers, db_session, capsys):
    attempt_id = start(client, student_headers)["attempt_id"]
    answer_mcq(client, student_headers, db_session, attempt_id, correct=12)
    answer_essays_with_model_answers(client, student_headers, db_session, attempt_id)

    result = submit(client, student_headers, attempt_id)

    assert result["score"] == 10 and result["passed"] is True
    assert result["mcq_score"] == 6 and result["essay_score"] == 4
    assert result["completed_course"] is True and result["status"] == "graded"
    # B1: mọi kỹ năng của khóa thành "Đã biết", nguồn review
    user = user_of(db_session)
    skills = {s.skill_id: s for s in db_session.query(UserSkill).filter_by(user_id=user.user_id)}
    assert set(skills) == set(SKILL_IDS)
    assert all(s.status == "known" and s.source == "review" for s in skills.values())
    # Email kết quả (chế độ dev in ra terminal)
    out = capsys.readouterr().out
    assert "Kết quả ôn tập: ĐẠT (10/10)" in out and "Hoàn thành" in out


def test_blank_submission_scores_0_and_changes_nothing(client, bank_312, student_headers, db_session):
    attempt_id = start(client, student_headers)["attempt_id"]

    result = submit(client, student_headers, attempt_id)

    assert result["score"] == 0 and result["passed"] is False and result["completed_course"] is False
    assert db_session.query(UserSkill).count() == 0
    assert all(q["points"] == 0 for q in result["questions"])


@pytest.mark.parametrize(("correct", "passed"), [(12, True), (11, False)])
def test_pass_threshold_is_6(client, bank_312, student_headers, db_session, correct, passed):
    """TN đúng hết = 6đ (đúng ngưỡng → Đạt); đúng 11 câu = 5,5đ, tự luận bỏ trống → Chưa đạt."""
    attempt_id = start(client, student_headers)["attempt_id"]
    answer_mcq(client, student_headers, db_session, attempt_id, correct=correct)

    result = submit(client, student_headers, attempt_id)

    assert result["score"] == correct * 0.5 and result["passed"] is passed


def test_meeting_example_essay_scores_7_of_10(client, bank_312, student_headers, db_session):
    """Câu nâng cao list/tuple (2đ) với bài làm mẫu → 7/10 × 2 = 1,4đ, bằng chứng từng ý (mục 5 tài liệu họp)."""
    attempt = None
    for _ in range(30):  # đề ngẫu nhiên — làm lại tới khi đề có câu list/tuple
        attempt_id = start(client, student_headers)["attempt_id"]
        target = [a for a in answers_of(db_session, attempt_id) if a.question.code == "312-PY-TL-02"]
        if target:
            attempt = (attempt_id, target[0].position)
            break
        submit(client, student_headers, attempt_id)
    assert attempt, "không ra được câu list/tuple sau 30 lượt"
    attempt_id, position = attempt
    client.patch(f"/api/review-attempts/{attempt_id}/answers", headers=student_headers,
                 json={"answers": [{"position": position, "text_answer": LIST_TUPLE_ANSWER}]})

    result = submit(client, student_headers, attempt_id)

    q = result["questions"][position - 1]
    assert q["points"] == 1.4 and q["max_points"] == 2
    assert [r["result"] for r in q["rubric"]] == ["full", "full", "partial", "none"]
    assert q["rubric"][0]["evidence"] == "List thì sửa được còn tuple thì không sửa được."
    assert q["text_answer"] == LIST_TUPLE_ANSWER and q["explanation"].startswith("Đáp án mẫu")


def test_result_reveals_answers_after_submit(client, bank_312, student_headers, db_session):
    attempt_id = start(client, student_headers)["attempt_id"]
    answer_mcq(client, student_headers, db_session, attempt_id, correct=1)

    result = submit(client, student_headers, attempt_id)

    first = result["questions"][0]
    assert first["is_correct"] is True and first["selected_index"] == first["correct_index"]
    assert first["explanation"] and len(first["options"]) == 4
    second = result["questions"][1]
    assert second["is_correct"] is False and second["selected_index"] != second["correct_index"]


# ─────────────── Hoàn thành khóa: chỉ lần đạt ĐẦU TIÊN (B1, B2, 6b) ───────────────


def pass_once(client, headers, db_session):
    attempt_id = start(client, headers)["attempt_id"]
    answer_mcq(client, headers, db_session, attempt_id, correct=12)
    return submit(client, headers, attempt_id)


def test_removed_skill_comes_back_on_first_pass(client, bank_312, student_headers, db_session):
    """6b: người dùng tự gỡ một kỹ năng của khóa → đạt lần đầu → kỹ năng quay lại "Đã biết"."""
    client.patch("/api/me/skills", headers=student_headers,
                 json={"add": [{"skill_id": SKILL_IDS[0], "status": "learning"}]})
    client.patch("/api/me/skills", headers=student_headers, json={"remove": [SKILL_IDS[0]]})

    pass_once(client, student_headers, db_session)

    row = db_session.query(UserSkill).filter_by(skill_id=SKILL_IDS[0]).one()
    assert row.status == "known" and row.source == "review"


def test_second_pass_only_records_history(client, bank_312, student_headers, db_session):
    """B2: đạt lần 2 (khóa đã Hoàn thành — user_courses thật của Khôi) → không Hoàn thành lại, không cập nhật kỹ năng."""
    first = pass_once(client, student_headers, db_session)
    assert course_gateway.get_enrollment_status(db_session, user_of(db_session).user_id, 312) == course_gateway.COMPLETED
    client.patch("/api/me/skills", headers=student_headers, json={"remove": [SKILL_IDS[0]]})  # tự gỡ sau khi đạt

    second = pass_once(client, student_headers, db_session)

    assert first["completed_course"] is True and second["completed_course"] is False
    assert db_session.query(UserSkill).filter_by(skill_id=SKILL_IDS[0]).count() == 0  # không thêm lại


@pytest.mark.parametrize("status", ["completed", "abandoned", "bookmarked", None])
def test_no_completion_unless_in_progress(client, bank_312, student_headers, db_session, monkeypatch, status):
    attempt_id = start(client, student_headers)["attempt_id"]  # bắt đầu khi đang học
    answer_mcq(client, student_headers, db_session, attempt_id, correct=12)
    monkeypatch.setattr(course_gateway, "get_enrollment_status", lambda *_: status)  # rồi đổi trạng thái

    result = submit(client, student_headers, attempt_id)

    assert result["passed"] is True and result["completed_course"] is False
    assert db_session.query(UserSkill).count() == 0


def test_failure_mid_transaction_saves_nothing(client, bank_312, student_headers, db_session, monkeypatch):
    """FR-43: lỗi khi đánh dấu Hoàn thành → rollback toàn bộ; bài vẫn đang làm, nộp lại được."""
    attempt_id = start(client, student_headers)["attempt_id"]
    answer_mcq(client, student_headers, db_session, attempt_id, correct=12)

    def broken(*_):
        raise RuntimeError("module khóa học lỗi")

    monkeypatch.setattr(course_gateway, "mark_course_completed", broken)
    with pytest.raises(RuntimeError):
        review_service.submit_attempt(db_session, user_of(db_session), attempt_id)

    attempt = db_session.get(ReviewAttempt, attempt_id)
    assert attempt.status == "in_progress" and attempt.score is None
    assert db_session.query(UserSkill).count() == 0
    monkeypatch.undo()
    assert submit(client, student_headers, attempt_id)["completed_course"] is True


# ─────────────── Chấm tự luận khi AI lỗi (A6) ───────────────


class DownGraderAI(MockAI):
    name = "down"

    def grade_essay(self, question, answer):
        raise AIUnavailableError("hết lượt gọi")


class WrongGraderAI(MockAI):
    name = "wrong"

    def grade_essay(self, question, answer):
        return [{"result": "full", "points": 99, "evidence": None} for _ in question["rubric"]]


@pytest.mark.parametrize("ai", [DownGraderAI(), WrongGraderAI()])
def test_essay_falls_back_to_keyword_grading(client, bank_312, student_headers, db_session, ai):
    attempt_id = start(client, student_headers)["attempt_id"]
    answer_essays_with_model_answers(client, student_headers, db_session, attempt_id)

    result = review_service.submit_attempt(db_session, user_of(db_session), attempt_id, ai=ai)

    assert result["essay_score"] == 4  # vẫn chấm đúng bằng từ khóa
    grading = db_session.get(ReviewAttempt, attempt_id).trace["grading"]
    assert grading["ai"] == ai.name and len(grading["keyword_fallback"]) == 3


# ─────────────── Nộp lại, quyền ───────────────


def test_submit_twice_and_ownership(client, bank_312, student_headers, admin_headers, db_session):
    attempt_id = start(client, student_headers)["attempt_id"]

    assert client.post(submit_url(attempt_id), headers=admin_headers).status_code == 404  # bài người khác
    first = submit(client, student_headers, attempt_id)
    again = client.post(submit_url(attempt_id), headers=student_headers)

    assert again.status_code == 409
    assert db_session.get(ReviewAttempt, attempt_id).score == first["score"]  # điểm không đổi
    assert client.post(submit_url(99999), headers=student_headers).status_code == 404
    assert client.post(submit_url(attempt_id)).status_code == 401


# ─────────────── Lịch sử ───────────────


def test_history_list_filters_and_pages(client, bank_312, student_headers, db_session):
    failed = start(client, student_headers)["attempt_id"]
    submit(client, student_headers, failed)
    passed = pass_once(client, student_headers, db_session)["attempt_id"]
    start(client, student_headers)  # lượt đang làm — KHÔNG có trong lịch sử

    all_items = client.get("/api/me/review-history", headers=student_headers).json()
    only_passed = client.get("/api/me/review-history?passed=true", headers=student_headers).json()
    page2 = client.get("/api/me/review-history?size=1&page=2", headers=student_headers).json()
    other_course = client.get("/api/me/review-history?course_id=999", headers=student_headers).json()

    assert all_items["total"] == 2 and [i["attempt_id"] for i in all_items["items"]] == [passed, failed]
    assert all_items["items"][0]["course_title"] == "Python Basics: Selection and Iteration"
    assert all_items["items"][0]["completed_course"] is True
    assert only_passed["total"] == 1 and only_passed["items"][0]["attempt_id"] == passed
    assert page2["total"] == 2 and [i["attempt_id"] for i in page2["items"]] == [failed]
    assert other_course["total"] == 0


def test_history_detail_only_for_submitted_own_attempts(client, bank_312, student_headers, admin_headers, db_session):
    attempt_id = start(client, student_headers)["attempt_id"]
    url = f"/api/me/review-history/{attempt_id}"

    assert client.get(url, headers=student_headers).status_code == 404  # đang làm → chưa xem đáp án được
    submit(client, student_headers, attempt_id)
    detail = client.get(url, headers=student_headers)
    assert detail.status_code == 200 and detail.json()["attempt_id"] == attempt_id
    assert client.get(url, headers=admin_headers).status_code == 404  # lượt của người khác


def test_info_lists_attempts_after_submit(client, bank_312, student_headers, db_session):
    result = pass_once(client, student_headers, db_session)

    info = client.get("/api/courses/312/review", headers=student_headers).json()

    assert info["in_progress_attempt_id"] is None
    assert info["attempts"][0]["attempt_id"] == result["attempt_id"]
    assert info["attempts"][0]["passed"] is True and info["can_start"] is True  # vẫn ôn lại được (B2)


# ─────────────── Vết cho admin (A4) ───────────────


def test_trace_admin_only(client, bank_312, student_headers, admin_headers, db_session):
    attempt_id = start(client, student_headers)["attempt_id"]
    submit(client, student_headers, attempt_id)
    url = f"/api/admin/review-attempts/{attempt_id}/trace"

    assert client.get(url, headers=student_headers).status_code == 403
    response = client.get(url, headers=admin_headers)
    assert response.status_code == 200
    trace = response.json()["trace"]
    assert trace["ai_mode"] == "mock" and len(trace["skills"]) == 5 and trace["grading"]["ai"] == "mock"
    assert client.get("/api/admin/review-attempts/99999/trace", headers=admin_headers).status_code == 404
