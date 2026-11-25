"""G3f — mentor duyệt câu ôn tập AI soạn, admin xử lý phản ánh, gán mentor (module 09 · Tuấn · 25/11/2026).

Docs: docs/Review-AI-Tu-Soan-On-Tap.md D19–D23. Chạy:  python -m pytest tests/test_mentor_review.py -v
"""

import pytest

from app.models import (
    KnowledgeChunk,
    Notification,
    ReviewAnswer,
    ReviewAttempt,
    ReviewQuestion,
    ReviewQuestionMeta,
    ReviewQuestionReport,
    Skills,
    Users,
)
from app.services import review_report_service as svc

SKILL = 70
STUDENT = "student.test@edumentor.vn"


def _q(db, qid, *, ai: bool, type_="mcq", chunk_id=None):
    mcq = type_ == "mcq"
    db.add(ReviewQuestion(question_id=qid, skill_id=SKILL, chunk_id=chunk_id, type=type_,
                          level="recognize" if mcq else "easy", content=f"Câu {qid}?",
                          options=["A", "B", "C", "D"] if mcq else None, correct_index=0 if mcq else None,
                          rubric=None if mcq else [{"point": "Ý 1", "keywords": ["a"], "weight": 1}],
                          is_active=True, source="ai" if ai else "bank"))  # fmt: skip
    db.flush()
    db.add(ReviewQuestionMeta(question_id=qid, family_id=qid, review_status="auto_approved" if ai else "approved"))


def _user(db, email, role="student"):
    user = Users(email=email, full_name=email.split("@")[0], hashed_password="x", role=role)
    db.add(user)
    db.flush()
    return user


@pytest.fixture()
def rdb(db_session):
    db = db_session
    db.add(Skills(skill_id=SKILL, skill="Docker", is_active=True))
    db.add(KnowledgeChunk(chunk_id=5, skill_id=SKILL, title="Dockerfile", content="RUN, COPY, ADD tạo layer."))
    db.flush()
    _q(db, 1, ai=True, chunk_id=5)  # câu AI soạn, tự duyệt
    _q(db, 2, ai=False)  # câu soạn tay
    _q(db, 3, ai=True, type_="essay")
    mentor = _user(db, "lan@test.vn", "mentor")
    admin = _user(db, "boss@test.vn", "admin")
    db.commit()
    return {"db": db, "mentor": mentor, "admin": admin}


def _code(fn, *args):
    with pytest.raises(svc.ReportError) as err:
        fn(*args)
    return err.value.code


# ─────────────── Mentor ───────────────


def test_queue_only_ai_questions_with_chunk(rdb):
    page = svc.mentor_queue(rdb["db"])
    assert [i["question_id"] for i in page["items"]] == [1, 3]  # câu soạn tay (2) không vào hàng chờ (D21)
    assert page["counts"] == {"pending": 2, "passed": 0, "reported": 0}
    assert page["items"][0]["chunk"]["content"].startswith("RUN")


def test_queue_puts_popular_skill_first(rdb):
    db = rdb["db"]
    db.add(Skills(skill_id=71, skill="Git", is_active=True))
    db.flush()
    db.add(ReviewQuestion(question_id=9, skill_id=71, type="mcq", level="recognize", content="Git?",
                          options=["A", "B", "C", "D"], correct_index=0, source="ai"))  # fmt: skip
    db.flush()
    db.add(ReviewQuestionMeta(question_id=9, family_id=9, review_status="auto_approved"))
    db.add(ReviewAttempt(user_id=rdb["mentor"].user_id, skill_id=71, status="graded"))  # Git có người ôn
    db.commit()
    assert [i["question_id"] for i in svc.mentor_queue(db)["items"]] == [9, 1, 3]


def test_pass(rdb):
    db, mentor = rdb["db"], rdb["mentor"]
    assert svc.mark_passed(db, mentor, 1)["mentor_status"] == "passed"
    meta = db.get(ReviewQuestionMeta, 1)
    assert meta.mentor_by == mentor.user_id and meta.mentor_at is not None
    assert _code(svc.mark_passed, db, mentor, 1) == "conflict"  # Đạt rồi
    page = svc.mentor_queue(db, status="passed")
    assert page["items"][0]["mentor_name"] == "lan" and page["counts"]["pending"] == 1


def test_manual_question_rejected(rdb):
    assert _code(svc.mark_passed, rdb["db"], rdb["mentor"], 2) == "not_ai"
    assert _code(svc.report, rdb["db"], rdb["mentor"], 2, "wrong_answer", None) == "not_ai"


def test_report_disables_immediately(rdb):
    db, mentor = rdb["db"], rdb["mentor"]
    out = svc.report(db, mentor, 1, "wrong_knowledge", "  chỉ RUN/COPY/ADD  ")
    assert out == {"question_id": 1, "mentor_status": "reported", "is_active": False}
    assert db.get(ReviewQuestion, 1).is_active is False
    assert db.get(ReviewQuestionMeta, 1).disabled_reason == "mentor_report"
    assert db.query(ReviewQuestionReport).one().note == "chỉ RUN/COPY/ADD"
    assert _code(svc.report, db, mentor, 1, "ambiguous", None) == "conflict"  # đang chờ admin
    assert _code(svc.mark_passed, db, mentor, 1) == "conflict"
    item = svc.mentor_queue(db, status="reported")["items"][0]
    assert item["report"] == {"reason": "wrong_knowledge", "note": "chỉ RUN/COPY/ADD"}


def test_passed_question_can_still_be_reported(rdb):
    db, mentor = rdb["db"], rdb["mentor"]
    svc.mark_passed(db, mentor, 1)
    assert svc.report(db, mentor, 1, "wrong_answer", None)["mentor_status"] == "reported"


def test_report_validation(rdb):
    db, mentor = rdb["db"], rdb["mentor"]
    assert _code(svc.report, db, mentor, 1, "bad_rubric", None) == "invalid"  # chỉ tự luận
    assert _code(svc.report, db, mentor, 1, "other", "  ") == "invalid"  # 'Khác' phải ghi chú
    assert svc.report(db, mentor, 3, "bad_rubric", None)["is_active"] is False


# ─────────────── Admin xử lý ───────────────


def test_dismiss_reenables_and_passes_and_notifies(rdb):
    db, admin = rdb["db"], rdb["admin"]
    svc.report(db, rdb["mentor"], 1, "wrong_answer", None)
    out = svc.resolve(db, admin, 1, "dismiss", "Đáp án đúng")
    assert out == {"question_id": 1, "closed": 1, "is_active": True}
    meta = db.get(ReviewQuestionMeta, 1)
    assert (meta.mentor_status, meta.mentor_by, meta.disabled_reason) == ("passed", admin.user_id, None)
    assert db.query(ReviewQuestionReport).one().status == "dismissed"
    note = db.query(Notification).filter_by(type="review_report").one()
    assert note.user_id == rdb["mentor"].user_id and "bật lại" in note.title


def test_keep_disabled(rdb):
    db = rdb["db"]
    svc.report(db, rdb["mentor"], 1, "wrong_answer", None)
    out = svc.resolve(db, rdb["admin"], 1, "keep_disabled")
    assert out["is_active"] is False
    meta = db.get(ReviewQuestionMeta, 1)
    assert meta.mentor_status == "reported" and meta.disabled_reason is None
    assert db.query(ReviewQuestionReport).one().status == "resolved"
    # câu đã xử lý → mentor phản ánh lại được khi câu bật lại sau này (không còn phản ánh đang mở)
    assert svc.open_count(db) == 0


def test_resolve_without_open_report(rdb):
    assert _code(svc.resolve, rdb["db"], rdb["admin"], 1, "dismiss") == "not_found"
    assert _code(svc.resolve, rdb["db"], rdb["admin"], 999, "dismiss") == "not_found"


def test_list_groups_history(rdb):
    db = rdb["db"]
    svc.report(db, rdb["mentor"], 1, "wrong_answer", None)
    svc.resolve(db, rdb["admin"], 1, "dismiss")
    svc.report(db, rdb["mentor"], 1, "ambiguous", None)  # phản ánh lại sau khi admin bác
    page = svc.list_page(db, status="all")
    assert page["total"] == 1 and page["open_total"] == 1
    item = page["items"][0]
    assert [r["status"] for r in item["reports"]] == ["open", "dismissed"]
    assert item["question"]["disabled_by_report"] is True
    assert svc.list_page(db, reason="wrong_answer")["total"] == 0  # chỉ tính phản ánh đang mở


# ─────────────── Tài khoản mentor (D22) ───────────────


def test_add_and_remove_mentor(rdb):
    db = rdb["db"]
    _user(db, "Hoc.Vien@test.vn")
    db.commit()
    out = svc.add_mentor(db, " hoc.vien@TEST.vn ")
    assert out["email"] == "Hoc.Vien@test.vn"
    assert _code(svc.add_mentor, db, "hoc.vien@test.vn") == "conflict"
    assert _code(svc.add_mentor, db, "boss@test.vn") == "conflict"  # không đổi admin
    assert _code(svc.add_mentor, db, "khong.co@test.vn") == "not_found"
    assert {m["email"] for m in svc.list_mentors(db)} == {"lan@test.vn", "Hoc.Vien@test.vn"}
    svc.remove_mentor(db, out["user_id"])
    assert db.get(Users, out["user_id"]).role == "student"
    assert _code(svc.remove_mentor, db, rdb["admin"].user_id) == "not_found"


# ─────────────── API + phân quyền ───────────────


@pytest.fixture()
def mentor_headers(client, rdb, student_headers):
    """Học viên đăng ký qua API rồi được gán mentor (vai trò đọc từ DB → token cũ dùng được ngay)."""
    rdb["db"].query(Users).filter_by(email=STUDENT).one().role = "mentor"
    rdb["db"].commit()
    return student_headers


MENTOR_CALLS = [
    ("get", "/api/mentor/review-questions"),
    ("post", "/api/mentor/review-questions/1/pass"),
    ("post", "/api/mentor/review-questions/1/report"),
]


@pytest.mark.parametrize(("method", "url"), MENTOR_CALLS)
def test_mentor_api_blocks_guest_and_student(client, rdb, student_headers, method, url):
    body = {"json": {"reason": "wrong_answer"}} if method == "post" else {}
    assert getattr(client, method)(url, **body).status_code == 401
    assert getattr(client, method)(url, headers=student_headers, **body).status_code == 403


def test_mentor_call_list_covers_every_route():
    from app.routers.v1.endpoints import mentor_review

    paths = {"/api/mentor" + r.path.replace("{question_id}", "1") for r in mentor_review.router.routes}
    assert paths <= {url for _, url in MENTOR_CALLS}


def test_api_mentor_flow(client, rdb, mentor_headers, admin_headers):
    r = client.get("/api/mentor/review-questions", headers=mentor_headers)
    assert r.status_code == 200 and r.json()["counts"]["pending"] == 2
    assert client.post("/api/mentor/review-questions/2/pass", headers=mentor_headers).status_code == 409
    assert (
        client.post("/api/mentor/review-questions/3/pass", headers=mentor_headers).json()["mentor_status"] == "passed"
    )
    r = client.post("/api/mentor/review-questions/1/report", json={"reason": "lung_tung"}, headers=mentor_headers)
    assert r.status_code == 422
    r = client.post("/api/mentor/review-questions/1/report", json={"reason": "wrong_answer"}, headers=mentor_headers)
    assert r.status_code == 200 and r.json()["is_active"] is False
    # admin cũng vào được trang mentor (để kiểm tra)
    assert client.get("/api/mentor/review-questions", headers=admin_headers).status_code == 200

    assert client.get("/api/admin/review/reports/count", headers=admin_headers).json() == {"open_total": 1}
    item = client.get("/api/admin/review/reports", headers=admin_headers).json()["items"][0]
    assert item["question"]["disabled_by_report"] is True and item["reports"][0]["user_name"] == "Student Test"
    r = client.post("/api/admin/review/reports/1/resolve", json={"action": "dismiss"}, headers=admin_headers)
    assert r.status_code == 200 and r.json()["is_active"] is True
    detail = client.get("/api/admin/review/questions/1", headers=admin_headers).json()
    assert detail["mentor_status"] == "passed"


def test_api_admin_mentors(client, rdb, student_headers, admin_headers):
    r = client.post("/api/admin/review/mentors", json={"email": STUDENT}, headers=admin_headers)
    assert r.status_code == 201, r.text
    assert client.get("/api/mentor/review-questions", headers=student_headers).status_code == 200  # có hiệu lực ngay
    assert client.post("/api/admin/review/mentors", json={"email": STUDENT}, headers=admin_headers).status_code == 409
    mentors = client.get("/api/admin/review/mentors", headers=admin_headers).json()
    assert {m["email"] for m in mentors} == {"lan@test.vn", STUDENT}
    user_id = r.json()["user_id"]
    assert client.delete(f"/api/admin/review/mentors/{user_id}", headers=admin_headers).status_code == 204
    assert client.get("/api/mentor/review-questions", headers=student_headers).status_code == 403


def test_admin_edit_closes_report_reenables_and_passes(client, rdb, admin_headers):
    db = rdb["db"]
    svc.report(db, rdb["mentor"], 1, "wrong_answer", None)
    db.add(ReviewAttempt(user_id=rdb["mentor"].user_id, skill_id=SKILL, status="graded"))
    db.flush()
    attempt = db.query(ReviewAttempt).one()
    db.add(
        ReviewAnswer(
            attempt_id=attempt.attempt_id,
            position=1,
            question_id=1,
            option_order=[0, 1, 2, 3],
            selected_index=0,
            max_points=0.5,
            points=0.5,
        )
    )  # fmt: skip — câu đã dùng → sửa tạo phiên bản mới
    db.commit()
    r = client.patch("/api/admin/review/questions/1", json={"content": "Chỉ thị nào tạo layer mới?"},
                     headers=admin_headers)  # fmt: skip
    assert r.status_code == 200, r.text
    new_id = r.json()["question"]["question_id"]
    assert new_id != 1
    db.expire_all()
    assert db.query(ReviewQuestionReport).one().status == "resolved"
    new_q, new_meta = db.get(ReviewQuestion, new_id), db.get(ReviewQuestionMeta, new_id)
    assert new_q.is_active is True and new_meta.mentor_status == "passed"
    assert db.get(ReviewQuestion, 1).is_active is False  # bản cũ vẫn tắt
    assert db.query(Notification).filter_by(type="review_report").count() == 1
