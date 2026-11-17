"""Test B2 — ngân hàng tiếng Anh + chuyển từ bản tiếng Việt (module 09 · Tuấn · 14/11/2026).

Chạy:  python -m pytest tests/test_seed_review_en.py -v      (trong thư mục backend)
"""

# ruff: noqa: F811 — fixture import từ test_seed_review; pytest truyền qua TÊN tham số

import copy
from pathlib import Path

from app.models import (
    KnowledgeChunk,
    ReviewAnswer,
    ReviewAttempt,
    ReviewQuestion,
    Users,
)
from scripts import seed_review as script
from tests.test_seed_review import bank, course_312  # noqa: F401 — fixture

EN = script.load_bank(Path(__file__).parents[1] / "data/review/course_312_en.json")


def test_english_bank_is_valid_and_complete():
    assert script.validate_bank(EN) == []
    questions = EN["questions"]
    assert len(questions) == 100 and len(EN["chunks"]) == 15
    assert sum(q["type"] == "essay" for q in questions) == 30
    assert all(not q["code"].startswith("312-") for q in questions)  # QT9: mã theo kỹ năng, bỏ tiền tố khóa


def test_english_bank_mirrors_vietnamese(bank):
    """Dịch giữ nguyên đáp án, mức, đoạn tri thức, điểm từng ý."""
    vi = {q["code"].removeprefix("312-"): q for q in bank["questions"]}
    for q in EN["questions"]:
        src = vi[q["code"]]
        assert (q["type"], q["level"], q.get("correct_index")) == (src["type"], src["level"], src.get("correct_index"))
        assert q["chunk"] == src["chunk"].removeprefix("312-")
        if q["type"] == "essay":
            assert [r["max_points"] for r in q["rubric"]] == [r["max_points"] for r in src["rubric"]]


def test_switch_to_english_keeps_history(db_session, course_312, bank):
    """Nạp tiếng Việt → có bài làm → nạp tiếng Anh + --retire: câu VN tắt (không xóa), đoạn VN bị xóa,
    bài làm cũ vẫn trỏ đúng câu cũ; chỉ còn 100 câu tiếng Anh đang bật."""
    script.seed_bank(db_session, bank)
    db_session.commit()
    old = db_session.query(ReviewQuestion).filter_by(code="312-PY-TN-01").one()
    user = Users(full_name="Học viên", email="hv@example.com", hashed_password="x", role="student")
    db_session.add(user)
    db_session.flush()
    attempt = ReviewAttempt(user_id=user.user_id, course_id=312, status="graded")
    db_session.add(attempt)
    db_session.flush()
    db_session.add(ReviewAnswer(attempt_id=attempt.attempt_id, position=1, question_id=old.question_id, max_points=0.5))
    db_session.commit()

    script.seed_bank(db_session, copy.deepcopy(EN))
    counts = script.retire_bank(db_session, bank)
    db_session.commit()

    assert counts == {"questions_deactivated": 100, "chunks_deleted": 15}
    active = db_session.query(ReviewQuestion).filter_by(is_active=True).all()
    assert len(active) == 100 and all(not q.code.startswith("312-") for q in active)
    assert {c.code for c in db_session.query(KnowledgeChunk)} == {c["code"] for c in EN["chunks"]}
    db_session.expire_all()
    kept = db_session.get(ReviewQuestion, old.question_id)
    assert kept is not None and kept.is_active is False and kept.chunk_id is None
    assert db_session.query(ReviewAnswer).filter_by(question_id=old.question_id).count() == 1


def test_retire_twice_is_harmless(db_session, course_312, bank):
    script.seed_bank(db_session, bank)
    script.seed_bank(db_session, copy.deepcopy(EN))
    script.retire_bank(db_session, bank)
    db_session.commit()
    assert script.retire_bank(db_session, bank) == {"questions_deactivated": 0, "chunks_deleted": 0}
