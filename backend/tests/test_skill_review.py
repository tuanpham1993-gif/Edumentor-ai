"""G2c — ráp đề ôn tập theo KỸ NĂNG (module 09 · Tuấn · 22/11/2026 — app/services/skill_review_service.py).

Chạy:  python -m pytest tests/test_skill_review.py -v      (trong thư mục backend)
"""

import random

import pytest

from app.ai.review import MockAI
from app.core.config import settings
from app.core.seed_data import seed_review
from app.models import LearningPath, LearningPathNode, ReviewAttempt, ReviewQuestion, Skills, Users
from app.services import review_service, skill_search_service
from app.services import skill_review_service as svc

NODE_SKILL = 50  # node lộ trình "Python Programming" — KHÔNG có câu
BANK_SKILL = 51  # tên trùng "python programming" — giữ ngân hàng câu
EMPTY_SKILL = 52  # "Docker" — chưa có câu
_BANK = seed_review.load_bank(seed_review.DEFAULT_FILE)["questions"]
RUBRIC = {lv: next(q["rubric"] for q in _BANK if q["level"] == lv) for lv in ("easy", "advanced")}  # barem thật


def _mcq(skill_id, level, i):
    return ReviewQuestion(skill_id=skill_id, type="mcq", level=level, content=f"{level} câu {i}?",
                          options=["A", "B", "C", "D"], correct_index=i % 4, is_active=True)  # fmt: skip


def _essay(skill_id, level, i):
    return ReviewQuestion(skill_id=skill_id, type="essay", level=level, content=f"Tự luận {level} {i}?",
                          rubric=RUBRIC[level], is_active=True)  # fmt: skip


def _user(db, email):
    user = Users(email=email, full_name="HV", hashed_password="x")
    db.add(user)
    db.flush()
    return user


@pytest.fixture()
def world(db_session):
    db = db_session
    db.add_all([Skills(skill_id=NODE_SKILL, skill="Python Programming", is_active=True),
                Skills(skill_id=BANK_SKILL, skill="python programming", is_active=True),
                Skills(skill_id=EMPTY_SKILL, skill="Docker", is_active=True),
                Skills(skill_id=53, skill="Ngừng dùng", is_active=False)])  # fmt: skip
    db.flush()
    for i in range(8):
        db.add_all([_mcq(BANK_SKILL, "recognize", i), _mcq(BANK_SKILL, "understand", i)])
    for i in range(3):
        db.add_all([_essay(BANK_SKILL, "easy", i), _essay(BANK_SKILL, "advanced", i)])
    db.add(_mcq(EMPTY_SKILL, "recognize", 0))  # 1 câu — không đủ khung
    user, other = _user(db, "hv1@test.vn"), _user(db, "hv2@test.vn")
    mine = LearningPath(student_id=user.user_id, original_query="học python", goal_type="career", status="ongoing")
    theirs = LearningPath(student_id=other.user_id, original_query="x", goal_type="career", status="ongoing")
    db.add_all([mine, theirs])
    db.flush()
    node = {"skill_id": NODE_SKILL, "is_target": True, "added_by": "system", "is_required": True, "display_order": 1}
    db.add_all([LearningPathNode(path_id=mine.record_id, **node), LearningPathNode(path_id=theirs.record_id, **node)])
    db.commit()
    skill_search_service._state.update(index=None, built=0.0, signature=None)
    yield {"db": db, "user": user, "other": other, "path": mine.record_id, "their_path": theirs.record_id}
    skill_search_service._state.update(index=None, built=0.0, signature=None)


def start(w, skill_id=NODE_SKILL, path_id=None, user=None, seed=1):
    return svc.start_skill_attempt(w["db"], user or w["user"], skill_id, path_id, rng=random.Random(seed), ai=MockAI())


# ─────────────── Mức sẵn sàng ───────────────


def test_readiness_uses_duplicate_name_that_holds_the_bank(world):
    info = svc.skill_readiness(world["db"], NODE_SKILL)
    assert info.bank_skill_id == BANK_SKILL and info.ready
    assert svc.skill_readiness(world["db"], EMPTY_SKILL).ready is False


def test_unknown_or_inactive_skill(world):
    for skill_id in (9999, 53):
        with pytest.raises(svc.SkillNotFoundError):
            svc.skill_readiness(world["db"], skill_id)


# ─────────────── Ráp đề ───────────────


def test_exam_has_15_questions_of_one_skill_in_the_standard_structure(world):
    view = start(world, path_id=world["path"])
    assert view["total_questions"] == 15 and view["resumed"] is False
    assert view["skill_id"] == NODE_SKILL and view["skill_name"] == "Python Programming"
    assert view["course_id"] is None and view["course_title"] == "" and view["path_id"] == world["path"]
    levels = [q["level"] for q in view["questions"]]
    assert {lv: levels.count(lv) for lv in set(levels)} == {"recognize": 6, "understand": 6, "easy": 2, "advanced": 1}
    assert {q["skill_id"] for q in view["questions"]} == {BANK_SKILL}

    attempt = world["db"].get(ReviewAttempt, view["attempt_id"])
    assert attempt.course_id is None and attempt.skill_id == NODE_SKILL
    assert attempt.trace["mode"] == "skill" and attempt.trace["bank_skill_id"] == BANK_SKILL


def test_second_start_resumes_the_unfinished_attempt(world):
    first = start(world)
    again = start(world, seed=2)
    assert again["attempt_id"] == first["attempt_id"] and again["resumed"] is True


def test_skill_without_enough_questions_is_blocked(world):
    with pytest.raises(svc.SkillBankMissingError) as err:
        start(world, skill_id=EMPTY_SKILL)
    assert err.value.message == "Chưa có đề ôn tập cho kỹ năng này."


def test_path_must_belong_to_the_learner_and_contain_the_skill(world):
    with pytest.raises(svc.PathNotFoundError):
        start(world, path_id=world["their_path"])  # lộ trình của người khác
    with pytest.raises(svc.PathNotFoundError):
        start(world, skill_id=BANK_SKILL, path_id=world["path"])  # lộ trình không có node này
    assert world["db"].query(ReviewAttempt).count() == 0


def test_unfinished_limit_counts_course_and_skill_attempts(world, monkeypatch):
    monkeypatch.setattr(settings, "REVIEW_MAX_UNFINISHED", 1)
    start(world)
    with pytest.raises(review_service.ReviewBlockedError) as err:
        start(world, skill_id=BANK_SKILL)
    assert err.value.code == "too_many_unfinished"


def test_next_attempt_avoids_questions_of_the_previous_one_when_possible(world):
    db = world["db"]
    first = start(world)
    attempt = db.get(ReviewAttempt, first["attempt_id"])
    attempt.status = "graded"  # giả lập đã nộp + chấm
    db.commit()
    prev = {a.question_id for a in attempt.answers}
    second = start(world, seed=2)
    ids = {a.question_id for a in db.get(ReviewAttempt, second["attempt_id"]).answers}
    mcq_prev = {q for q in prev if db.get(ReviewQuestion, q).type == "mcq"}
    # mỗi mức TN có 8 câu, đề cần 6, lượt trước đã dùng 6 → chỉ còn 2 câu mới → buộc lặp 4 / mức = 8 (tối thiểu)
    assert len(ids & mcq_prev) == 8


# ─────────────── G2d · API + trọn luồng ───────────────

STUDENT = "student.test@edumentor.vn"


@pytest.fixture()
def api_world(world, student_headers):
    db = world["db"]
    student = db.query(Users).filter_by(email=STUDENT).one()
    path = LearningPath(student_id=student.user_id, original_query="python", goal_type="career", status="ongoing")
    db.add(path)
    db.flush()
    db.add(LearningPathNode(path_id=path.record_id, skill_id=NODE_SKILL, is_target=True, added_by="system",
                            is_required=True, display_order=1))  # fmt: skip
    db.commit()
    return {**world, "student": student, "student_path": path.record_id}


def _answer_all_mcq_correctly(db, attempt_id):
    from app.models import ReviewAnswer

    for a in db.query(ReviewAnswer).filter_by(attempt_id=attempt_id):
        if a.question.type == "mcq":
            a.selected_index = a.option_order.index(a.question.correct_index)
    db.commit()


def test_api_info_start_submit_result_history(client, api_world, student_headers):
    db, path = api_world["db"], api_world["student_path"]
    info = client.get(f"/api/skills/{NODE_SKILL}/review", headers=student_headers).json()
    assert info["can_start"] is True and info["skill"] == "Python Programming" and info["attempts"] == []

    started = client.post(f"/api/skills/{NODE_SKILL}/review-attempts", params={"path": path}, headers=student_headers)
    assert started.status_code == 200, started.text
    body = started.json()
    assert body["course_id"] is None and body["skill_id"] == NODE_SKILL and body["path_id"] == path
    assert body["skill_name"] == "Python Programming" and body["total_questions"] == 15
    attempt_id = body["attempt_id"]
    assert client.get(f"/api/review-attempts/{attempt_id}", headers=student_headers).status_code == 200

    _answer_all_mcq_correctly(db, attempt_id)  # 12 × 0,5 = 6,0 = ngưỡng đạt
    result = client.post(f"/api/review-attempts/{attempt_id}/submit", headers=student_headers)
    assert result.status_code == 200, result.text
    result = result.json()
    assert result["passed"] is True and result["skill_known"] is True and result["completed_course"] is False
    assert result["course_id"] is None and result["skill_name"] == "Python Programming"

    # chỉ kỹ năng của node thành "Đã biết" (không đụng khóa, không đụng kỹ năng giữ ngân hàng)
    from app.models import Notification, UserSkill

    known = {s.skill_id for s in db.query(UserSkill).filter_by(user_id=api_world["student"].user_id)}
    assert known == {NODE_SKILL}
    note = db.query(Notification).filter_by(user_id=api_world["student"].user_id, type="review_graded").one()
    assert note.body == "Kỹ năng: Python Programming"

    history = client.get("/api/me/review-history", headers=student_headers).json()
    assert history["total"] == 1 and history["items"][0]["skill_id"] == NODE_SKILL
    assert history["items"][0]["course_id"] is None
    detail = client.get(f"/api/me/review-history/{attempt_id}", headers=student_headers)
    assert detail.status_code == 200 and detail.json()["skill_known"] is True

    info = client.get(f"/api/skills/{NODE_SKILL}/review", headers=student_headers).json()
    assert [a["attempt_id"] for a in info["attempts"]] == [attempt_id]

    # huy hiệu trên node: phần "ôn thẳng theo kỹ năng" + "Đến hạn ôn" tính cả lượt theo kỹ năng
    badge = client.get("/api/me/review/skills", params={"skill_ids": str(NODE_SKILL)}, headers=student_headers).json()
    item = badge["items"][0]
    assert item["skill"]["ready"] is True and item["skill"]["last_attempt"]["attempt_id"] == attempt_id
    assert item["due"] is not None and item["due"]["last_passed"] is True


def test_api_errors(client, api_world, student_headers):
    url = "/api/skills/{}/review-attempts"
    assert client.post(url.format(NODE_SKILL)).status_code == 401
    assert client.get("/api/skills/9999/review", headers=student_headers).status_code == 404
    assert client.post(url.format(9999), headers=student_headers).status_code == 404
    other_path = client.post(url.format(NODE_SKILL), params={"path": api_world["path"]}, headers=student_headers)
    assert other_path.status_code == 404  # lộ trình của người khác
    empty = client.post(url.format(EMPTY_SKILL), headers=student_headers)
    assert empty.status_code == 409 and empty.json()["detail"] == "Chưa có đề ôn tập cho kỹ năng này."
    info = client.get(f"/api/skills/{EMPTY_SKILL}/review", headers=student_headers).json()
    assert info["can_start"] is False and info["blocked"]["code"] == "no_question_bank"


def test_other_user_cannot_open_skill_attempt(client, api_world, student_headers):
    view = start(api_world, user=api_world["other"])
    assert client.get(f"/api/review-attempts/{view['attempt_id']}", headers=student_headers).status_code == 404


def test_failed_skill_attempt_does_not_mark_known(api_world):
    from app.models import UserSkill

    db = api_world["db"]
    view = start(api_world)
    review_service.submit_attempt(db, api_world["user"], view["attempt_id"], ai=MockAI())  # bỏ trống → 0 điểm
    assert db.get(ReviewAttempt, view["attempt_id"]).passed is False
    assert db.query(UserSkill).filter_by(user_id=api_world["user"].user_id).count() == 0
