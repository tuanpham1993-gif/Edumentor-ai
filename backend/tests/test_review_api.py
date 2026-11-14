"""Test API ôn tập GĐ2: thông tin, bắt đầu / làm tiếp, xem đề, lưu câu trả lời (module 09 · Tuấn · 09/11/2026).

Dùng ngân hàng THẬT của khóa 312 (data/review/course_312.json) nạp vào DB test bằng scripts/seed_review.
Chạy:  python -m pytest tests/test_review_api.py -v      (trong thư mục backend)
"""

import random

import pytest

from app.ai.review import MockAI
from app.ai.review.base import AIUnavailableError, ReviewAI
from app.models import (
    Courses,
    CourseSkill,
    KnowledgeChunk,
    ReviewAnswer,
    ReviewAttempt,
    ReviewQuestion,
    Skills,
    UserCourse,
    Users,
)
from app.services import course_gateway, review_service
from scripts import seed_review

BANK = seed_review.load_bank(seed_review.DEFAULT_FILE)
SKILL_IDS = sorted(BANK["skills"].values())
INFO_URL = "/api/courses/312/review"
START_URL = "/api/courses/312/review-attempts"
SECRET_FIELDS = (
    "correct_index",
    "rubric",
    "explanation",
    "question_id",
    "option_order",
)


@pytest.fixture()
def bank_312(db_session, student_headers):
    db_session.add(
        Courses(course_id=312, title="Python Basics: Selection and Iteration")
    )
    db_session.add(Courses(course_id=999, title="Khóa chưa có ngân hàng"))
    for skill_id in SKILL_IDS:
        db_session.add(Skills(skill_id=skill_id, skill=f"Kỹ năng {skill_id}", is_active=True))
    db_session.add(Skills(skill_id=99001, skill="Kỹ năng chưa có câu hỏi", is_active=True))
    db_session.flush()
    for skill_id in SKILL_IDS:
        db_session.add(CourseSkill(course_id=312, skill_id=skill_id))
    # Khóa 999: 1 kỹ năng CÓ câu hỏi (dùng chung với 312) + 1 kỹ năng CHƯA có → vẫn "chưa có đề" (A1, sửa 11/11)
    db_session.add(CourseSkill(course_id=999, skill_id=SKILL_IDS[0]))
    db_session.add(CourseSkill(course_id=999, skill_id=99001))
    seed_review.seed_bank(db_session, BANK)
    student = user_of(db_session)
    db_session.add_all(
        [
            UserCourse(user_id=student.user_id, course_id=312, status="ongoing"),
            UserCourse(user_id=student.user_id, course_id=999, status="ongoing"),
        ]
    )
    db_session.commit()


def start(client, headers):
    response = client.post(START_URL, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def user_of(db_session, email="student.test@edumentor.vn"):
    return db_session.query(Users).filter_by(email=email).one()


# ─────────────── GET /courses/{id}/review ───────────────


def test_info_can_start(client, bank_312, student_headers):
    body = client.get(INFO_URL, headers=student_headers).json()

    assert body["can_start"] is True and body["blocked"] is None
    assert [s["skill_id"] for s in body["skills"]] == SKILL_IDS
    assert body["structure"] == {
        "recognize": 6,
        "understand": 6,
        "easy": 2,
        "advanced": 1,
        "total_questions": 15,
        "max_score": 10.0,
    }
    assert body["pass_score"] == 6.0
    assert body["in_progress_attempt_id"] is None and body["attempts"] == []


def test_info_course_without_bank(client, bank_312, student_headers):
    body = client.get("/api/courses/999/review", headers=student_headers).json()

    assert body["can_start"] is False
    assert body["blocked"] == {
        "code": "no_question_bank",
        "message": "Chưa có đề ôn tập cho khóa học này.",
    }


@pytest.mark.parametrize(
    ("status", "code"),
    # 'bookmarked' (bảng student_courses của Khôi): mới lưu khóa, chưa đăng ký → như chưa tham gia
    [(None, "not_enrolled"), ("bookmarked", "not_enrolled"), ("abandoned", "abandoned")],
)
def test_info_and_start_blocked_by_enrollment(client, bank_312, student_headers, monkeypatch, status, code):
    monkeypatch.setattr(course_gateway, "get_enrollment_status", lambda *_: status)

    info = client.get(INFO_URL, headers=student_headers).json()
    started = client.post(START_URL, headers=student_headers)

    assert info["can_start"] is False and info["blocked"]["code"] == code
    assert started.status_code == 403
    assert started.json()["detail"] == review_service.BLOCK_MESSAGES[code]


def test_completed_course_can_review_again(
    client, bank_312, student_headers, monkeypatch
):
    monkeypatch.setattr(course_gateway, "get_enrollment_status", lambda *_: "completed")
    assert (
        client.get(INFO_URL, headers=student_headers).json()["can_start"] is True
    )  # B2


def test_unknown_course_and_no_token(client, bank_312, student_headers):
    assert (
        client.get("/api/courses/12345/review", headers=student_headers).status_code
        == 404
    )
    assert (
        client.post(
            "/api/courses/12345/review-attempts", headers=student_headers
        ).status_code
        == 404
    )
    assert client.get(INFO_URL).status_code == 401
    assert client.post(START_URL).status_code == 401


def test_start_without_bank_is_409(client, bank_312, student_headers):
    response = client.post("/api/courses/999/review-attempts", headers=student_headers)
    assert response.status_code == 409


# ─────────────── POST /courses/{id}/review-attempts ───────────────


def test_start_builds_exam_matching_structure(client, bank_312, student_headers):
    body = start(client, student_headers)
    questions = body["questions"]

    assert body["resumed"] is False and body["status"] == "in_progress"
    assert body["total_questions"] == 15 and body["answered"] == 0
    assert [q["position"] for q in questions] == list(range(1, 16))
    assert [q["level"] for q in questions[12:]] == ["easy", "easy", "advanced"]
    assert (
        sorted(q["level"] for q in questions[:12])
        == ["recognize"] * 6 + ["understand"] * 6
    )
    assert {q["skill_id"] for q in questions[:12]} == set(
        SKILL_IDS
    )  # mỗi kỹ năng ≥ 1 câu TN
    assert len({q["skill_id"] for q in questions[12:]}) == 3  # 3 câu TL — 3 kỹ năng
    assert sum(q["max_points"] for q in questions) == 10
    for q in questions:
        assert not set(SECRET_FIELDS) & q.keys()  # KHÔNG lộ đáp án / barem
        assert (
            (len(q["options"]) == 4) if q["type"] == "mcq" else (q["options"] is None)
        )


def test_options_are_shuffled_but_consistent(
    client, bank_312, student_headers, db_session
):
    body = start(client, student_headers)
    answers = (
        db_session.query(ReviewAnswer).filter_by(attempt_id=body["attempt_id"]).all()
    )

    for a in answers:
        shown = body["questions"][a.position - 1]["options"]
        if a.question.type == "mcq":
            assert shown == [a.question.options[i] for i in a.option_order]


def test_start_twice_resumes_same_attempt(client, bank_312, student_headers):
    first = start(client, student_headers)
    second = start(client, student_headers)

    assert second["resumed"] is True and second["attempt_id"] == first["attempt_id"]
    assert second["questions"] == first["questions"]
    info = client.get(INFO_URL, headers=student_headers).json()
    assert (
        info["in_progress_attempt_id"] == first["attempt_id"]
        and len(info["attempts"]) == 1
    )


def test_trace_records_rag_and_prompt(client, bank_312, student_headers, db_session):
    body = start(client, student_headers)
    trace = db_session.get(ReviewAttempt, body["attempt_id"]).trace

    assert trace["ai_mode"] == "mock" and trace["ai"] == "mock"
    assert "You are a teacher" in trace["system_prompt"]
    assert sorted(s["skill_id"] for s in trace["skills"]) == SKILL_IDS
    for s in trace["skills"]:
        assert s["chunks"] and "CONTEXT" in s["prompt"]
        assert s["fallback"] is False and s["retries"] == 0


def test_new_attempt_avoids_previous_questions(
    client, bank_312, student_headers, db_session
):
    first = start(client, student_headers)
    attempt = db_session.get(ReviewAttempt, first["attempt_id"])
    attempt.status, attempt.score, attempt.passed = (
        "graded",
        4,
        False,
    )  # giả lập đã nộp (GĐ3)
    db_session.commit()
    previous = {a.question_id for a in attempt.answers}

    second = start(client, student_headers)
    current = {
        a.question_id
        for a in db_session.get(ReviewAttempt, second["attempt_id"]).answers
    }

    assert second["attempt_id"] != first["attempt_id"]
    overlap = previous & current
    # Ngân hàng 40 câu, mỗi đề 15: tự luận (6 dễ, 4 nâng cao) không lặp; trắc nghiệm lặp rất ít
    essays = {
        q.question_id for q in db_session.query(ReviewQuestion).filter_by(type="essay")
    }
    assert not overlap & essays
    assert len(overlap) <= 3


# ─────────────── Sinh đề: sinh lại + ngân hàng dự phòng (A6) ───────────────


class FakeAI(ReviewAI):
    """AI giả trong test: chấm tự luận giống mock (từ khóa); lớp con chỉ đổi cách sinh đề."""

    def grade_essay(self, question, answer):
        return MockAI().grade_essay(question, answer)


class BrokenAI(FakeAI):
    name = "broken"

    def __init__(self):
        self.calls = 0

    def generate_questions(self, request, rng):
        self.calls += 1
        return [{"type": "mcq", "content": "thiếu lựa chọn"}]


class DownAI(FakeAI):
    name = "down"

    def generate_questions(self, request, rng):
        raise AIUnavailableError("hết lượt gọi")


@pytest.mark.parametrize("ai_class", [BrokenAI, DownAI])
def test_fallback_bank_when_ai_fails(
    client, bank_312, student_headers, db_session, ai_class
):
    client.get(INFO_URL, headers=student_headers)  # đảm bảo user đã tạo
    ai = ai_class()

    body = review_service.start_attempt(
        db_session, user_of(db_session), 312, rng=random.Random(1), ai=ai
    )

    assert body["total_questions"] == 15
    trace = db_session.get(ReviewAttempt, body["attempt_id"]).trace
    assert all(s["fallback"] is True for s in trace["skills"])
    if ai_class is BrokenAI:
        assert ai.calls == 5 * 3  # 5 kỹ năng × (1 lần + 2 lần sinh lại)
        assert all(s["retries"] == 3 and len(s["errors"]) == 3 for s in trace["skills"])
    else:
        assert all("hết lượt gọi" in s["errors"][0] for s in trace["skills"])


class NewQuestionAI(FakeAI):
    """Giả lập AI thật (giai đoạn 2): trả câu MỚI chưa có trong ngân hàng."""

    name = "new"

    def generate_questions(self, request, rng):
        out = []
        for level, n in request.need.items():
            for i in range(n):
                if level in ("recognize", "understand"):
                    out.append(
                        {
                            "type": "mcq",
                            "level": level,
                            "content": f"AI {request.skill_id} {level} {i}?",
                            "options": ["a", "b", "c", "d"],
                            "correct_index": 1,
                        }
                    )
                else:
                    size = 2 if level == "easy" else 4
                    out.append(
                        {
                            "type": "essay",
                            "level": level,
                            "content": f"AI {request.skill_id} {level} {i}?",
                            "rubric": [
                                {
                                    "text": f"ý {k}",
                                    "max_points": 10 / size,
                                    "main_keywords": ["x"],
                                    "sub_keywords": [],
                                }
                                for k in range(size)
                            ],
                        }
                    )
        return out


def test_new_ai_questions_saved_to_bank(client, bank_312, student_headers, db_session):
    client.get(INFO_URL, headers=student_headers)
    before = db_session.query(ReviewQuestion).count()

    review_service.start_attempt(
        db_session, user_of(db_session), 312, rng=random.Random(2), ai=NewQuestionAI()
    )

    ai_rows = db_session.query(ReviewQuestion).filter_by(source="ai").all()
    assert (
        len(ai_rows) == 15 and db_session.query(ReviewQuestion).count() == before + 15
    )


def test_rag_scores_in_trace_when_embeddings_exist(
    client, bank_312, student_headers, db_session
):
    for c in db_session.query(KnowledgeChunk):
        c.embedding = [1.0, float(c.chunk_id)]
    db_session.commit()
    client.get(INFO_URL, headers=student_headers)

    body = review_service.start_attempt(
        db_session,
        user_of(db_session),
        312,
        rng=random.Random(3),
        embedder=lambda _: [1.0, 0.0],
    )

    trace = db_session.get(ReviewAttempt, body["attempt_id"]).trace
    for s in trace["skills"]:
        scores = [c["score"] for c in s["chunks"]]
        assert all(x is not None for x in scores) and scores == sorted(
            scores, reverse=True
        )


# ─────────────── GET /review-attempts/{id} ───────────────


def test_get_attempt_owner_only(client, bank_312, student_headers, admin_headers):
    attempt_id = start(client, student_headers)["attempt_id"]
    url = f"/api/review-attempts/{attempt_id}"

    assert client.get(url, headers=student_headers).status_code == 200
    other = client.get(
        url, headers=admin_headers
    )  # người khác (kể cả admin) → 404, không lộ lượt
    assert (
        other.status_code == 404
        and other.json()["detail"] == "Không tìm thấy bài ôn tập."
    )
    assert (
        client.get("/api/review-attempts/99999", headers=student_headers).status_code
        == 404
    )
    assert client.get(url).status_code == 401


# ─────────────── PATCH /review-attempts/{id}/answers ───────────────


def answers_url(attempt_id):
    return f"/api/review-attempts/{attempt_id}/answers"


def test_save_answers_and_resume(client, bank_312, student_headers):
    attempt_id = start(client, student_headers)["attempt_id"]

    saved = client.patch(
        answers_url(attempt_id),
        headers=student_headers,
        json={
            "answers": [
                {"position": 1, "selected_index": 2},
                {
                    "position": 13,
                    "text_answer": "  List thì sửa được còn tuple thì không.  ",
                },
            ]
        },
    )
    assert saved.status_code == 200, saved.text
    assert saved.json()["answered"] == 2

    resumed = start(client, student_headers)  # Tạm rời rồi vào lại
    assert resumed["resumed"] is True
    assert resumed["questions"][0]["selected_index"] == 2
    assert (
        resumed["questions"][12]["text_answer"]
        == "List thì sửa được còn tuple thì không."
    )


def test_clear_answers(client, bank_312, student_headers):
    attempt_id = start(client, student_headers)["attempt_id"]
    url = answers_url(attempt_id)
    client.patch(
        url,
        headers=student_headers,
        json={
            "answers": [
                {"position": 1, "selected_index": 0},
                {"position": 14, "text_answer": "abc"},
            ]
        },
    )

    body = client.patch(
        url,
        headers=student_headers,
        json={
            "answers": [
                {"position": 1, "selected_index": None},
                {"position": 14, "text_answer": "   "},
            ]
        },
    ).json()

    assert body["answered"] == 0
    assert (
        body["questions"][0]["selected_index"] is None
        and body["questions"][13]["text_answer"] is None
    )


@pytest.mark.parametrize(
    ("payload", "status", "message"),
    [
        ({"answers": [{"position": 1, "text_answer": "x"}]}, 422, "trắc nghiệm"),
        ({"answers": [{"position": 13, "selected_index": 1}]}, 422, "tự luận"),
        (
            {"answers": [{"position": 16, "selected_index": 1}]},
            422,
            "không có trong đề",
        ),
        ({"answers": [{"position": 1, "selected_index": 4}]}, 422, None),
        (
            {
                "answers": [
                    {"position": 1, "selected_index": 0},
                    {"position": 1, "selected_index": 1},
                ]
            },
            422,
            None,
        ),
        ({"answers": []}, 422, None),
    ],
)
def test_save_answers_invalid(
    client, bank_312, student_headers, payload, status, message
):
    attempt_id = start(client, student_headers)["attempt_id"]

    response = client.patch(
        answers_url(attempt_id), headers=student_headers, json=payload
    )

    assert response.status_code == status
    if message:
        assert message in response.json()["detail"]
    # sai thì KHÔNG lưu câu nào
    assert (
        client.get(
            f"/api/review-attempts/{attempt_id}", headers=student_headers
        ).json()["answered"]
        == 0
    )


def test_save_answers_other_user_and_locked(
    client, bank_312, student_headers, admin_headers, db_session
):
    attempt_id = start(client, student_headers)["attempt_id"]
    payload = {"answers": [{"position": 1, "selected_index": 1}]}

    assert (
        client.patch(
            answers_url(attempt_id), headers=admin_headers, json=payload
        ).status_code
        == 404
    )

    db_session.get(ReviewAttempt, attempt_id).status = "graded"
    db_session.commit()
    locked = client.patch(
        answers_url(attempt_id), headers=student_headers, json=payload
    )
    assert locked.status_code == 409
