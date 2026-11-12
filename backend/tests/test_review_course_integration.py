"""Test chung Ôn tập (09 · Tuấn) × Theo dõi khóa học (Khôi) — T1–T9 (12/11/2026).

Đi qua API THẬT của cả hai module (không monkeypatch course_gateway):
    Khôi: POST /api/me/bookmarks · POST /api/courses/{id}/join · DELETE /api/me/courses/{id}
          GET /api/me/courses/{id}/status
    Tuấn: GET /api/courses/{id}/review · POST …/review-attempts · POST /api/review-attempts/{id}/submit
          GET /api/me/skills
Danh sách T1–T9: BA-nhom/Gui-Khoi-On-tap-09-va-Khoa-hoc.md.

Chạy:  python -m pytest tests/test_review_course_integration.py -v      (trong thư mục backend)
"""
# ruff: noqa: F811 — fixture bank_312 import từ test_review_api; pytest truyền qua TÊN tham số

import pytest

from app.models import UserCourse
from app.models.course import Courses
from app.models.course_skill import CourseSkill
from tests.test_review_api import INFO_URL, SKILL_IDS, START_URL, bank_312, user_of  # noqa: F401
from tests.test_review_submit import answer_mcq, submit_url

COURSE = 312


@pytest.fixture()
def fresh(bank_312, db_session):
    """Ngân hàng khóa 312 như bank_312 nhưng học viên CHƯA tham gia khóa nào (bỏ dòng user_courses mẫu)."""
    db_session.query(UserCourse).delete()
    db_session.commit()


def join(client, headers, course_id=COURSE):
    response = client.post(f"/api/courses/{course_id}/join", headers=headers)
    assert response.status_code == 200, response.text


def course_status(client, headers, course_id=COURSE):
    return client.get(f"/api/me/courses/{course_id}/status", headers=headers).json()["status"]


def my_skills(client, headers):
    return {s["skill_id"]: s["status"] for s in client.get("/api/me/skills", headers=headers).json()}


def take_review(client, headers, db_session, *, correct=12):
    """Làm 1 lượt: đúng `correct` câu trắc nghiệm (12 = 6đ = vừa đạt), tự luận bỏ trống → nộp."""
    attempt_id = client.post(START_URL, headers=headers).json()["attempt_id"]
    answer_mcq(client, headers, db_session, attempt_id, correct=correct)
    response = client.post(submit_url(attempt_id), headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


# ─────────────── Chưa tham gia → không được ôn ───────────────


def test_t1_not_joined_cannot_review(client, fresh, student_headers):
    info = client.get(INFO_URL, headers=student_headers).json()
    assert info["can_start"] is False and info["blocked"]["code"] == "not_enrolled"
    assert client.post(START_URL, headers=student_headers).status_code == 403


def test_t2_bookmark_only_is_like_not_joined(client, fresh, student_headers):
    response = client.post("/api/me/bookmarks", headers=student_headers, json={"course_id": COURSE})
    assert response.status_code == 201, response.text

    info = client.get(INFO_URL, headers=student_headers).json()
    assert info["blocked"]["code"] == "not_enrolled"
    assert client.post(START_URL, headers=student_headers).status_code == 403


# ─────────────── Tham gia → ôn tập → Hoàn thành ───────────────


def test_t3_join_adds_course_skills_as_learning(client, fresh, student_headers):
    join(client, student_headers)

    assert my_skills(client, student_headers) == {s: "learning" for s in SKILL_IDS}
    assert client.get(INFO_URL, headers=student_headers).json()["can_start"] is True


def test_t4_pass_completes_course_and_skills_known(client, fresh, student_headers, db_session):
    join(client, student_headers)

    result = take_review(client, student_headers, db_session)

    assert result["passed"] is True and result["completed_course"] is True
    assert course_status(client, student_headers) == "completed"  # bảng user_courses của Khôi
    row = db_session.query(UserCourse).filter_by(course_id=COURSE).one()
    assert row.completed_at is not None
    assert my_skills(client, student_headers) == {s: "known" for s in SKILL_IDS}


def test_t5_review_completed_course_again_only_adds_history(client, fresh, student_headers, db_session):
    join(client, student_headers)
    take_review(client, student_headers, db_session)

    again = take_review(client, student_headers, db_session)

    assert again["passed"] is True and again["completed_course"] is False  # B2
    assert course_status(client, student_headers) == "completed"
    assert my_skills(client, student_headers) == {s: "known" for s in SKILL_IDS}
    assert client.get("/api/me/review-history", headers=student_headers).json()["total"] == 2


def test_t6_cannot_abandon_completed_course(client, fresh, student_headers, db_session):
    join(client, student_headers)
    take_review(client, student_headers, db_session)

    assert client.delete(f"/api/me/courses/{COURSE}", headers=student_headers).status_code == 409
    assert course_status(client, student_headers) == "completed"


# ─────────────── Bỏ khóa ───────────────


def test_t7_abandon_removes_learning_skills_except_shared(client, fresh, student_headers, db_session):
    shared = SKILL_IDS[0]
    db_session.add(Courses(course_id=313, title="Khóa khác dùng chung 1 kỹ năng"))
    db_session.flush()
    db_session.add(CourseSkill(course_id=313, skill_id=shared))
    db_session.commit()
    join(client, student_headers)
    join(client, student_headers, 313)

    assert client.delete(f"/api/me/courses/{COURSE}", headers=student_headers).status_code == 200

    assert my_skills(client, student_headers) == {shared: "learning"}  # khóa 313 vẫn đang học kỹ năng này
    assert client.get(INFO_URL, headers=student_headers).json()["blocked"]["code"] == "abandoned"


def test_t8_abandon_while_attempt_open_still_grades_but_not_complete(client, fresh, student_headers, db_session):
    join(client, student_headers)
    attempt_id = client.post(START_URL, headers=student_headers).json()["attempt_id"]
    answer_mcq(client, student_headers, db_session, attempt_id, correct=12)
    assert client.delete(f"/api/me/courses/{COURSE}", headers=student_headers).status_code == 200

    response = client.post(submit_url(attempt_id), headers=student_headers)

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["passed"] is True and result["completed_course"] is False  # có lịch sử, KHÔNG Hoàn thành
    assert course_status(client, student_headers) == "abandoned"
    assert "known" not in my_skills(client, student_headers).values()


def test_t9_rejoin_then_pass_completes(client, fresh, student_headers, db_session):
    join(client, student_headers)
    assert client.delete(f"/api/me/courses/{COURSE}", headers=student_headers).status_code == 200
    join(client, student_headers)

    result = take_review(client, student_headers, db_session)

    assert result["completed_course"] is True
    assert course_status(client, student_headers) == "completed"


# ─────────────── L1: bỏ khóa đúng lúc đang chấm (12/11) ───────────────


def test_l1_abandon_during_grading_cancels_submit_then_resubmit_works(
    client, fresh, student_headers, db_session, monkeypatch
):
    """Lúc nộp, khóa còn 'ongoing' (đã kiểm) nhưng ngay trước khi chuyển Hoàn thành thì người học bỏ khóa.
    Hàm của Khôi im lặng → cổng đọc lại thấy chưa 'completed' → hủy cả lần nộp (409), bài vẫn đang làm,
    không có kỹ năng "Đã biết". Nộp lại → chấm bình thường, KHÔNG Hoàn thành (khóa đã bỏ)."""
    from app.services import course_tracking_service

    join(client, student_headers)
    attempt_id = client.post(START_URL, headers=student_headers).json()["attempt_id"]
    answer_mcq(client, student_headers, db_session, attempt_id, correct=12)
    real_mark = course_tracking_service.mark_course_completed_in_tx

    def abandon_just_before(db, user_id, course_id):
        row = db.query(UserCourse).filter_by(user_id=user_id, course_id=course_id).one()
        row.status = "abandoned"  # như request "Bỏ khóa" chen vào đúng lúc
        db.flush()
        real_mark(db, user_id, course_id)  # hàm thật của Khôi: không 'ongoing' → im lặng

    monkeypatch.setattr(course_tracking_service, "mark_course_completed_in_tx", abandon_just_before)

    response = client.post(submit_url(attempt_id), headers=student_headers)

    assert response.status_code == 409 and "nộp lại" in response.json()["detail"]
    db_session.expire_all()
    assert client.get(f"/api/review-attempts/{attempt_id}", headers=student_headers).json()["status"] == "in_progress"
    assert "known" not in my_skills(client, student_headers).values()

    monkeypatch.undo()
    db_session.query(UserCourse).filter_by(course_id=COURSE).update({"status": "abandoned"})
    db_session.commit()
    result = client.post(submit_url(attempt_id), headers=student_headers).json()
    assert result["passed"] is True and result["completed_course"] is False
