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
