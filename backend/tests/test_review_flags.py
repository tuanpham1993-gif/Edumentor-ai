"""Test "Bài cần xem lại" — admin xem và chấm lại câu tự luận bị gắn cờ (module 09 · Tuấn · 17/11/2026).

Chạy:  python -m pytest tests/test_review_flags.py -v      (trong thư mục backend)
"""

# ruff: noqa: F811 — fixture import từ test_review_api; pytest truyền qua TÊN tham số

from app.models import Notification, ReviewAttempt, UserCourse, UserSkill
from app.services import notification_service
from tests.test_review_api import SKILL_IDS, bank_312, start, user_of  # noqa: F401 — bank_312 là fixture
from tests.test_review_submit import answer_mcq, answers_of, submit

FLAGS_URL = "/api/admin/review/flags"


def resolve_url(attempt_id, position):
    return f"{FLAGS_URL}/{attempt_id}/{position}/resolve"


def essays(db_session, attempt_id):
    return [a for a in answers_of(db_session, attempt_id) if a.question.type == "essay"]


def answer_essays(client, headers, db_session, attempt_id, text="I am not sure about this question."):
    payload = [{"position": a.position, "text_answer": text} for a in essays(db_session, attempt_id)]
    client.patch(f"/api/review-attempts/{attempt_id}/answers", headers=headers, json={"answers": payload})


def graded_attempt(client, headers, db_session, *, mcq_correct):
    """Lượt đã chấm: `mcq_correct` câu trắc nghiệm đúng (0,5 điểm / câu), tự luận viết lạc đề (0 điểm)."""
    attempt_id = start(client, headers)["attempt_id"]
    answer_mcq(client, headers, db_session, attempt_id, correct=mcq_correct)
    answer_essays(client, headers, db_session, attempt_id)
    submit(client, headers, attempt_id)
    db_session.expire_all()
    return attempt_id


def mark_needs_review(db_session, attempt_id, position):
    """Giả lập khối 6 (đối chiếu) gắn cờ needs_review cho một câu."""
    attempt = db_session.get(ReviewAttempt, attempt_id)
    trace = dict(attempt.trace)
    grading = dict(trace["grading"])
    grading["essays"] = [
        {**e, "needs_review": e["position"] == position, "flags": ["needs_review"] if e["position"] == position else []}
        for e in grading["essays"]
    ]
    grading["needs_review"] = [position]
    trace["grading"] = grading
    attempt.trace = trace
    db_session.commit()


# ─────────────── Danh sách ───────────────


def test_unflagged_attempt_is_not_listed(client, bank_312, student_headers, admin_headers, db_session):
    graded_attempt(client, student_headers, db_session, mcq_correct=0)  # 0 điểm: xa ngưỡng, chấm từ khóa (mock)
    page = client.get(FLAGS_URL, headers=admin_headers).json()
    assert page["items"] == [] and page["open_total"] == 0


def test_needs_review_essay_is_listed_with_details(client, bank_312, student_headers, admin_headers, db_session):
    attempt_id = graded_attempt(client, student_headers, db_session, mcq_correct=0)
    essay = essays(db_session, attempt_id)[0]
    mark_needs_review(db_session, attempt_id, essay.position)

    page = client.get(FLAGS_URL, headers=admin_headers).json()

    assert page["open_total"] == 1 and page["reason_counts"]["needs_review"] == 1
    item = page["items"][0]
    assert (item["attempt_id"], item["position"]) == (attempt_id, essay.position)
    assert item["reasons"] == ["needs_review"] and item["review"] is None
    assert item["user_email"] == "student.test@edumentor.vn" and item["course_title"]
    assert item["text_answer"] and len(item["rubric"]) == len(essay.question.rubric)


def test_near_pass_attempt_flags_every_answered_essay(client, bank_312, student_headers, admin_headers, db_session):
    attempt_id = graded_attempt(client, student_headers, db_session, mcq_correct=11)  # 5,5 điểm — sát ngưỡng 6
    page = client.get(FLAGS_URL, params={"reason": "near_pass"}, headers=admin_headers).json()
    assert page["total"] == 3
    assert {i["position"] for i in page["items"]} == {a.position for a in essays(db_session, attempt_id)}
    assert all(i["attempt_score"] == 5.5 for i in page["items"])


def test_flags_admin_only(client, bank_312, student_headers):
    assert client.get(FLAGS_URL).status_code == 401
    assert client.get(FLAGS_URL, headers=student_headers).status_code == 403
    assert client.post(resolve_url(1, 13), headers=student_headers, json={"labels": ["full"]}).status_code == 403


# ─────────────── Chấm lại ───────────────


def test_resolve_recomputes_points_and_moves_to_resolved(client, bank_312, student_headers, admin_headers, db_session):
    attempt_id = graded_attempt(client, student_headers, db_session, mcq_correct=0)
    essay = essays(db_session, attempt_id)[0]
    mark_needs_review(db_session, attempt_id, essay.position)
    rubric = essay.question.rubric
    labels = ["full"] + ["none"] * (len(rubric) - 1)

    response = client.post(
        resolve_url(attempt_id, essay.position), headers=admin_headers, json={"labels": labels, "note": "Ý 1 đúng"}
    )

    assert response.status_code == 200, response.text
    body = response.json()
    expected = round(rubric[0]["max_points"] / 10 * float(essay.max_points), 2)
    assert body["item"]["points"] == expected and body["score_changed"] is True
    assert body["item"]["rubric"][0]["result"] == "full"
    assert body["item"]["rubric"][0]["reason"].startswith("Giáo viên chấm lại")
    review = body["item"]["review"]
    assert review["after"] == labels and review["note"] == "Ý 1 đúng" and review["score_after"] == expected
    # Lượt + trace: điểm tổng mới, hết cờ needs_review
    db_session.expire_all()
    attempt = db_session.get(ReviewAttempt, attempt_id)
    assert float(attempt.score) == expected and attempt.trace["grading"]["needs_review"] == []
    # Danh sách: không còn ở "chờ", có ở "đã xem lại"
    assert client.get(FLAGS_URL, headers=admin_headers).json()["open_total"] == 0
    resolved = client.get(FLAGS_URL, params={"status": "resolved"}, headers=admin_headers).json()
    assert resolved["total"] == 1 and resolved["items"][0]["review"]["by_name"]
    # Học viên: câu này "đã được xem lại", không còn "đang xem lại"
    result = client.get(f"/api/me/review-history/{attempt_id}", headers=student_headers).json()
    q = next(q for q in result["questions"] if q["position"] == essay.position)
    assert q["reviewed"] is True and q["needs_review"] is False and q["points"] == expected


def test_resolve_to_pass_completes_course_notifies_and_emails(
    client, bank_312, student_headers, admin_headers, db_session, capsys
):
    attempt_id = graded_attempt(client, student_headers, db_session, mcq_correct=11)  # 5,5 → chưa đạt
    student = user_of(db_session)
    assert db_session.query(UserCourse).filter_by(user_id=student.user_id, course_id=312).one().status == "ongoing"
    advanced = next(a for a in essays(db_session, attempt_id) if a.question.level == "advanced")  # câu 2 điểm
    capsys.readouterr()

    labels = ["full"] * len(advanced.question.rubric)
    body = client.post(
        resolve_url(attempt_id, advanced.position), headers=admin_headers, json={"labels": labels}
    ).json()

    assert body["passed_changed"] is True and body["completed_course"] is True
    assert body["item"]["attempt_score"] == 7.5 and body["item"]["attempt_passed"] is True
    db_session.expire_all()
    assert db_session.query(UserCourse).filter_by(user_id=student.user_id, course_id=312).one().status == "completed"
    known = db_session.query(UserSkill).filter_by(user_id=student.user_id, status="known").all()
    assert {s.skill_id for s in known} == set(SKILL_IDS)
    # Chuông kết quả cũ được CẬP NHẬT (không tạo trùng), đặt lại chưa đọc + chuông "hoàn thành khóa"
    graded = db_session.query(Notification).filter_by(user_id=student.user_id, type="review_graded").all()
    assert len(graded) == 1 and graded[0].is_read is False and "7.5/10 — Đạt" in graded[0].title
    assert db_session.query(Notification).filter_by(user_id=student.user_id, type="course_completed").count() == 1
    # Email kết quả, cùng mẫu khi nộp bài
    assert "Kết quả ôn tập: ĐẠT (7.5/10)" in capsys.readouterr().out


def test_resolve_without_change_keeps_score_and_sends_nothing(
    client, bank_312, student_headers, admin_headers, db_session, capsys
):
    attempt_id = graded_attempt(client, student_headers, db_session, mcq_correct=11)
    essay = essays(db_session, attempt_id)[0]
    before = [r["result"] for r in essay.rubric_result]
    capsys.readouterr()

    body = client.post(resolve_url(attempt_id, essay.position), headers=admin_headers, json={"labels": before}).json()

    assert body["score_changed"] is False and body["passed_changed"] is False
    assert body["item"]["review"]["before"] == before  # vẫn ghi là đã xem lại (xác nhận AI chấm đúng)
    assert "Kết quả ôn tập" not in capsys.readouterr().out


def test_resolve_errors(client, bank_312, student_headers, admin_headers, db_session):
    attempt_id = graded_attempt(client, student_headers, db_session, mcq_correct=0)
    essay = essays(db_session, attempt_id)[0]
    mcq = next(a for a in answers_of(db_session, attempt_id) if a.question.type == "mcq")
    n = len(essay.question.rubric)

    assert client.post(resolve_url(attempt_id, mcq.position), headers=admin_headers,
                       json={"labels": ["full"]}).status_code == 404  # fmt: skip
    assert client.post(resolve_url(999999, 1), headers=admin_headers, json={"labels": ["full"]}).status_code == 404
    wrong_count = client.post(resolve_url(attempt_id, essay.position), headers=admin_headers,
                              json={"labels": ["full"] * (n + 1)})  # fmt: skip
    assert wrong_count.status_code == 422
    bad_label = client.post(resolve_url(attempt_id, essay.position), headers=admin_headers,
                            json={"labels": ["partial"] * n})  # fmt: skip
    assert bad_label.status_code == 422

    in_progress = start(client, student_headers)["attempt_id"]
    position = essays(db_session, in_progress)[0].position
    client.patch(f"/api/review-attempts/{in_progress}/answers", headers=student_headers,
                 json={"answers": [{"position": position, "text_answer": "abc"}]})  # fmt: skip
    assert client.post(resolve_url(in_progress, position), headers=admin_headers,
                       json={"labels": ["full"] * len(essays(db_session, in_progress)[0].question.rubric)}
                       ).status_code == 409  # fmt: skip


# ─────────────── Chuông: renotify ───────────────


def test_renotify_updates_existing_notification(db_session, student_headers):
    student = user_of(db_session)
    first = notification_service.notify(db_session, student.user_id, "review_graded", "Cũ", source_id=7)
    first.is_read = True
    db_session.commit()

    again = notification_service.renotify(db_session, student.user_id, "review_graded", "Mới", source_id=7)
    db_session.commit()

    assert again.notification_id == first.notification_id
    assert again.title == "Mới" and again.is_read is False and again.read_at is None
    rows = db_session.query(Notification).filter_by(user_id=student.user_id, type="review_graded").count()
    assert rows == 1
