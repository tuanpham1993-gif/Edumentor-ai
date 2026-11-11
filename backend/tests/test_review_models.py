"""Test ràng buộc tầng DB của 4 bảng ôn tập (module 09 · Tuấn · GĐ1, 10/11/2026).

Chạy:  python -m pytest tests/test_review_models.py -v      (trong thư mục backend)
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import (
    Courses,
    KnowledgeChunk,
    ReviewAnswer,
    ReviewAttempt,
    ReviewQuestion,
    Skills,
    Users,
)

RUBRIC = [
    {"text": "List thay đổi được", "max_points": 5, "main_keywords": ["sửa"], "sub_keywords": ["list"]},
    {"text": "Tuple không đổi", "max_points": 5, "main_keywords": ["không"], "sub_keywords": ["tuple"]},
]


@pytest.fixture()
def base(db_session):
    """1 người dùng, 1 khóa, 1 kỹ năng, 1 đoạn tri thức."""
    user = Users(full_name="Học viên", email="hv@x.com", hashed_password="$2b$x")
    course = Courses(course_id=312, title="Python Basics")
    skill = Skills(skill_id=400, skill="Iteration", is_active=True)
    db_session.add_all([user, course, skill])
    db_session.flush()
    chunk = KnowledgeChunk(code="312-ITER-K01", skill_id=400, content="Vòng lặp for…")
    db_session.add(chunk)
    db_session.flush()
    return {"user": user, "course": course, "skill": skill, "chunk": chunk}


def mcq(**changes):
    data = {
        "skill_id": 400,
        "type": "mcq",
        "level": "recognize",
        "content": "Từ khóa nào tạo vòng lặp?",
        "options": ["for", "if", "def", "class"],
        "correct_index": 0,
    }
    return ReviewQuestion(**{**data, **changes})


def essay(**changes):
    data = {"skill_id": 400, "type": "essay", "level": "advanced", "content": "Phân biệt…", "rubric": RUBRIC}
    return ReviewQuestion(**{**data, **changes})


def add_and_flush(db_session, obj):
    db_session.add(obj)
    db_session.flush()
    return obj


# ─────────────── review_questions ───────────────


def test_valid_mcq_and_essay(db_session, base):
    q1 = add_and_flush(db_session, mcq(chunk_id=base["chunk"].chunk_id))
    q2 = add_and_flush(db_session, essay())

    assert q1.source == "bank" and q1.is_active is True
    assert q2.question_id != q1.question_id


@pytest.mark.parametrize(
    "bad",
    [
        {"type": "tf"},  # loại lạ
        {"level": "easy"},  # TN mà mức độ của TL
        {"correct_index": 4},  # đáp án ngoài 0..3
        {"options": None},  # TN thiếu lựa chọn
        {"rubric": RUBRIC},  # TN có barem
        {"source": "manual"},  # nguồn lạ
    ],
)
def test_invalid_mcq_rejected(db_session, base, bad):
    with pytest.raises(IntegrityError):
        add_and_flush(db_session, mcq(**bad))


@pytest.mark.parametrize(
    "bad",
    [
        {"level": "recognize"},  # TL mà mức độ của TN
        {"rubric": None},  # TL thiếu barem
        {"correct_index": 0},  # TL có đáp án
    ],
)
def test_invalid_essay_rejected(db_session, base, bad):
    with pytest.raises(IntegrityError):
        add_and_flush(db_session, essay(**bad))


def test_question_code_unique(db_session, base):
    add_and_flush(db_session, mcq(code="312-ITER-TN-01"))

    with pytest.raises(IntegrityError):
        add_and_flush(db_session, mcq(code="312-ITER-TN-01"))


# ─────────────── review_attempts ───────────────


def attempt(base, **changes):
    data = {"user_id": base["user"].user_id, "course_id": 312}
    return ReviewAttempt(**{**data, **changes})


def test_attempt_defaults(db_session, base):
    a = add_and_flush(db_session, attempt(base))

    assert a.status == "in_progress"
    assert a.is_first_pass is False and a.score is None and a.passed is None


def test_only_one_in_progress_per_user_course(db_session, base):
    add_and_flush(db_session, attempt(base))

    with pytest.raises(IntegrityError):
        add_and_flush(db_session, attempt(base))


def test_graded_attempts_do_not_block_new_one(db_session, base):
    add_and_flush(db_session, attempt(base, status="graded", score=5, passed=False))
    add_and_flush(db_session, attempt(base, status="graded", score=7.7, passed=True))

    add_and_flush(db_session, attempt(base))  # vẫn bắt đầu được lượt mới


@pytest.mark.parametrize("bad", [{"status": "done"}, {"score": 10.5}, {"score": -1}])
def test_invalid_attempt_rejected(db_session, base, bad):
    with pytest.raises(IntegrityError):
        add_and_flush(db_session, attempt(base, **bad))


# ─────────────── review_answers ───────────────


def test_answers_ordered_and_cascade_delete(db_session, base):
    q1 = add_and_flush(db_session, mcq())
    q2 = add_and_flush(db_session, essay())
    a = add_and_flush(db_session, attempt(base))
    a.answers.append(ReviewAnswer(position=2, question_id=q2.question_id, max_points=2))
    a.answers.append(
        ReviewAnswer(position=1, question_id=q1.question_id, max_points=0.5, option_order=[2, 0, 3, 1])
    )
    db_session.flush()
    db_session.expire(a)

    assert [x.position for x in a.answers] == [1, 2]
    assert a.answers[0].question.type == "mcq"

    db_session.delete(a)
    db_session.flush()
    assert db_session.query(ReviewAnswer).count() == 0


def test_same_question_twice_in_attempt_rejected(db_session, base):
    q = add_and_flush(db_session, mcq())
    a = add_and_flush(db_session, attempt(base))
    db_session.add_all(
        [
            ReviewAnswer(attempt_id=a.attempt_id, position=1, question_id=q.question_id, max_points=0.5),
            ReviewAnswer(attempt_id=a.attempt_id, position=2, question_id=q.question_id, max_points=0.5),
        ]
    )

    with pytest.raises(IntegrityError):
        db_session.flush()


@pytest.mark.parametrize(
    "bad",
    [{"position": 0}, {"selected_index": 4}, {"points": 0.75}],  # 0.75 > max_points 0.5
)
def test_invalid_answer_rejected(db_session, base, bad):
    q = add_and_flush(db_session, mcq())
    a = add_and_flush(db_session, attempt(base))
    data = {"attempt_id": a.attempt_id, "position": 1, "question_id": q.question_id, "max_points": 0.5}

    with pytest.raises(IntegrityError):
        add_and_flush(db_session, ReviewAnswer(**{**data, **bad}))
