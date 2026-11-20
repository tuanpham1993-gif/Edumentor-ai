"""Test API ôn tập GĐ2: thông tin, bắt đầu / làm tiếp, xem đề, lưu câu trả lời (module 09 · Tuấn · 09/11/2026).

Dùng ngân hàng THẬT của khóa 312 (bản tiếng Việt, data/review/archive/course_312.json) nạp vào DB test.
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
    ReviewQuestionMeta,
    Skills,
    UserCourse,
    Users,
)
from app.services import course_gateway, review_service
from scripts import seed_review

BANK = seed_review.load_bank(seed_review.VI_ARCHIVE_FILE)  # bản tiếng Việt (lưu trữ 21/11) — 10 file test dùng chung
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
    """7.5c (QT6-A, 16/11): câu AI soạn mới vào ngân hàng ở trạng thái CHỜ DUYỆT (tắt), KHÔNG vào đề."""
    client.get(INFO_URL, headers=student_headers)
    before = db_session.query(ReviewQuestion).count()

    body = review_service.start_attempt(
        db_session, user_of(db_session), 312, rng=random.Random(2), ai=NewQuestionAI()
    )

    ai_rows = db_session.query(ReviewQuestion).filter_by(source="ai").all()
    assert len(ai_rows) == 15 and db_session.query(ReviewQuestion).count() == before + 15
    assert all(not q.is_active for q in ai_rows)
    statuses = {m.review_status for m in db_session.query(ReviewQuestionMeta).filter(
        ReviewQuestionMeta.question_id.in_([q.question_id for q in ai_rows]))}  # fmt: skip
    assert statuses == {"pending"}
    exam_ids = {a.question_id for a in db_session.query(ReviewAnswer).filter_by(attempt_id=body["attempt_id"])}
    assert len(exam_ids) == 15 and not exam_ids & {q.question_id for q in ai_rows}  # đề chỉ có câu đã duyệt


def test_new_ai_questions_are_recorded_in_trace(client, bank_312, student_headers, db_session):
    """7.5c: trace ghi số câu AI đã gửi chờ duyệt + đề lấy từ ngân hàng (fallback) cho từng kỹ năng."""
    client.get(INFO_URL, headers=student_headers)
    body = review_service.start_attempt(
        db_session, user_of(db_session), 312, rng=random.Random(2), ai=NewQuestionAI()
    )
    trace = db_session.get(ReviewAttempt, body["attempt_id"]).trace
    assert sum(s["ai_new_pending"] for s in trace["skills"]) == 15
    assert all(s["fallback"] is True for s in trace["skills"])


def test_pending_questions_count_towards_bank_target(client, bank_312, student_headers, db_session):
    """7.5c: câu chờ duyệt tính vào ngưỡng 'đủ câu' → lượt sau AI được báo đã có câu chờ duyệt."""
    from app.repositories import review_repository

    client.get(INFO_URL, headers=student_headers)
    user = user_of(db_session)
    assert all(review_repository.pending_count(db_session, s) == 0 for s in SKILL_IDS)
    first = review_service.start_attempt(db_session, user, 312, rng=random.Random(2), ai=NewQuestionAI())
    saved = {s: db_session.query(ReviewQuestion).filter_by(source="ai", skill_id=s).count() for s in SKILL_IDS}
    assert sum(saved.values()) == 15
    assert all(review_repository.pending_count(db_session, s) == n for s, n in saved.items())

    review_service.submit_attempt(db_session, user, first["attempt_id"], ai=MockAI())  # nộp → được bắt đầu lượt mới
    seen = {}

    class Spy(NewQuestionAI):
        def generate_questions(self, request, rng):
            seen[request.skill_id] = request.pending_count
            return super().generate_questions(request, rng)

    review_service.start_attempt(db_session, user, 312, rng=random.Random(3), ai=Spy())
    assert seen and all(seen[s] == saved[s] for s in seen)  # AI được báo đúng số câu đang chờ duyệt


def test_next_attempt_avoids_new_versions_of_previous_questions(client, bank_312, student_headers, db_session):
    """7.5a (16/11): lượt 1 làm câu v1 → admin sửa thành v2 (câu đã có bài làm → phiên bản mới) → lượt 2 không ra v2."""
    from app.services import review_bank_service

    client.get(INFO_URL, headers=student_headers)
    user = user_of(db_session)
    first = review_service.start_attempt(db_session, user, 312, rng=random.Random(5), ai=MockAI())
    review_service.submit_attempt(db_session, user, first["attempt_id"], ai=MockAI())

    used = [a.question for a in db_session.query(ReviewAnswer).filter_by(attempt_id=first["attempt_id"])]
    v2_ids = set()
    for q in used:
        result = review_bank_service.update_question(db_session, q, {"content": q.content + " (v2)"}, note="test 7.5a")
        assert result.versioned  # câu đã có bài làm → tạo phiên bản mới, bản cũ tắt
        v2_ids.add(result.question.question_id)
    db_session.commit()

    second = review_service.start_attempt(db_session, user, 312, rng=random.Random(6), ai=MockAI())
    second_ids = {a.question_id for a in db_session.query(ReviewAnswer).filter_by(attempt_id=second["attempt_id"])}
    assert len(second_ids) == 15 and not second_ids & v2_ids
    trace = db_session.get(ReviewAttempt, second["attempt_id"]).trace
    assert v2_ids <= set(trace["avoided_question_ids"])  # trace ghi cả v1 lẫn v2


def test_family_questions_covers_all_versions_and_questions_without_meta(bank_312, db_session):
    """7.5a: họ = family_id; câu nạp trước 13/11 chưa có meta là họ của chính nó."""
    from app.repositories import review_repository
    from app.services import review_bank_service

    questions = db_session.query(ReviewQuestion).order_by(ReviewQuestion.question_id).limit(2).all()
    plain, edited = questions
    db_session.query(ReviewQuestionMeta).filter_by(question_id=plain.question_id).delete()  # giả lập câu chưa có meta
    db_session.add(ReviewAttempt(user_id=user_of(db_session).user_id, course_id=312, status="graded"))
    db_session.flush()
    attempt = db_session.query(ReviewAttempt).one()
    db_session.add(ReviewAnswer(attempt_id=attempt.attempt_id, position=1, question_id=edited.question_id,
                                max_points=0.5))  # fmt: skip
    db_session.flush()
    v2 = review_bank_service.update_question(db_session, edited, {"content": edited.content + " v2"}).question

    assert {q.question_id for q in review_repository.family_questions(db_session, [plain.question_id])} == {
        plain.question_id
    }
    assert {q.question_id for q in review_repository.family_questions(db_session, [edited.question_id])} == {
        edited.question_id,
        v2.question_id,
    }
    assert review_repository.family_questions(db_session, []) == []


def test_real_ai_does_not_generate_when_active_plus_pending_reach_target(monkeypatch):
    """7.5c: kỹ năng có 15 câu đang bật + 5 câu chờ duyệt (= ngưỡng 20) → Gemini KHÔNG soạn thêm, bốc ngân hàng."""
    import httpx

    from app.ai.review.base import GenerationRequest
    from app.ai.review.real_ai import RealAI
    from app.core.config import settings

    monkeypatch.setattr(settings, "REVIEW_BANK_TARGET_PER_SKILL", 20)
    for name, value in (("LLM_API_KEY", "test-key"), ("LLM_MODEL", "gemini-test"), ("REVIEW_LLM_API_KEY", ""),
                        ("REVIEW_LLM_MODEL", "")):  # fmt: skip
        monkeypatch.setattr(settings, name, value)  # không phụ thuộc .env trên máy
    calls = []
    transport = httpx.MockTransport(lambda request: calls.append(request) or httpx.Response(400))
    candidates = [
        {"question_id": i, "chunk_id": None, "type": "mcq", "level": "recognize", "content": f"Q{i}",
         "options": ["a", "b", "c", "d"], "correct_index": 0, "explanation": ""}
        for i in range(15)
    ]  # fmt: skip
    request = GenerationRequest(course_title="Python", skill_id=1, skill_name="Python", need={"recognize": 2},
                                candidates=candidates, pending_count=5)  # fmt: skip
    picked = RealAI(transport=transport).generate_questions(request, random.Random(0))
    assert calls == [] and len(picked) == 2 and all("question_id" in q for q in picked)
    request.pending_count = 4  # 15 + 4 < 20 → mới gọi Gemini (ở đây trả 400 → lỗi, đúng là đã gọi)
    with pytest.raises(AIUnavailableError):
        RealAI(transport=transport).generate_questions(request, random.Random(0))
    assert len(calls) == 1


def test_invalid_ai_question_is_skipped_without_breaking_attempt(
    client, bank_312, student_headers, db_session, monkeypatch
):
    """7.5c: một câu AI không lưu được (lỗi kiểm tra) chỉ bị bỏ qua; học viên vẫn bắt đầu làm bài với 15 câu."""
    from app.services import review_bank_service

    real = review_bank_service.create_question
    calls = []

    def flaky(db, data, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise review_bank_service.QuestionInvalidError(["giả lập lỗi"])
        return real(db, data, **kwargs)

    monkeypatch.setattr(review_bank_service, "create_question", flaky)
    client.get(INFO_URL, headers=student_headers)
    body = review_service.start_attempt(
        db_session, user_of(db_session), 312, rng=random.Random(2), ai=NewQuestionAI()
    )
    assert len(body["questions"]) == 15
    assert db_session.query(ReviewQuestion).filter_by(source="ai").count() == 14


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
