"""Test GĐ7 bước 7.4 — mức sẵn sàng ôn tập của khóa (module 09 · Tuấn · 16/11/2026).

Chạy:  python -m pytest tests/test_review_readiness.py -v      (trong thư mục backend)
"""

# ruff: noqa: F811 — fixture import từ file test khác; pytest truyền qua TÊN tham số

from sqlalchemy import select

from app.models import ReviewQuestion
from app.models.course import Courses
from app.services import review_bank_service as bank_service
from tests.test_review_admin import seeded  # noqa: F401 — fixture
from tests.test_seed_review import bank, course_312  # noqa: F401 — fixture

URL = "/api/admin/review/readiness"


def get(client, headers, **params) -> dict:
    response = client.get(URL, params=params, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def course(data: dict, course_id: int = 312) -> dict:
    return next(c for c in data["courses"] if c["course_id"] == course_id)


def test_requires_admin(client, seeded, student_headers):
    assert client.get(URL).status_code == 401
    assert client.get(URL, headers=student_headers).status_code == 403


def test_full_bank_is_ready(client, seeded, admin_headers):
    assert course(get(client, admin_headers))["skills"] == []  # danh sách mọi khóa: chỉ tóm tắt
    data = get(client, admin_headers, course_id=312)
    assert data["target_per_skill"] == 20
    assert data["structure"] == {"recognize": 6, "understand": 6, "easy": 2, "advanced": 1}
    c = course(data)
    assert c["ready"] is True and c["missing"] == []
    assert (c["skill_count"], c["active"], c["mcq"], c["essay"], c["target"]) == (5, 100, 70, 30, 100)
    skill = c["skills"][0]
    assert skill["active"] == 20 and skill["mcq"] == 14 and skill["missing"] == []
    assert sum(skill["by_level"].values()) == 20


def test_course_without_questions_is_counted_not_listed(client, seeded, admin_headers, db_session):
    before = get(client, admin_headers)["courses_without_questions"]
    db_session.add(Courses(course_id=9001, title="Khóa trống"))
    db_session.commit()
    data = get(client, admin_headers)
    assert data["courses_without_questions"] == before + 1
    assert 9001 not in [c["course_id"] for c in data["courses"]]

    one = get(client, admin_headers, course_id=9001)  # vẫn xem riêng được → chưa ôn được
    assert one["courses"][0]["ready"] is False and one["courses"][0]["missing"][0] == "Khóa chưa gắn kỹ năng nào"


def test_skill_without_mcq_blocks_course(client, seeded, admin_headers, db_session):
    """Tắt mọi câu TN của 1 kỹ năng → khóa không ôn được (giống học viên bị chặn no_question_bank)."""
    skill_id = course(get(client, admin_headers, course_id=312))["skills"][0]["skill_id"]
    for q in db_session.scalars(
        select(ReviewQuestion).where(ReviewQuestion.skill_id == skill_id, ReviewQuestion.type == "mcq")
    ):
        q.is_active = False
    db_session.commit()

    c = course(get(client, admin_headers, course_id=312))
    assert c["ready"] is False
    assert c["missing"] == [f"Kỹ năng «skill {skill_id}» chưa có câu trắc nghiệm"]
    skill = next(s for s in c["skills"] if s["skill_id"] == skill_id)
    assert skill["mcq"] == 0 and "trắc nghiệm nhận biết" in skill["missing"]
    assert c["active"] == 86  # câu tắt không tính


def test_missing_level_named(client, seeded, admin_headers, db_session):
    """Tắt hết tự luận nâng cao → thiếu đúng mức đó."""
    for q in db_session.scalars(select(ReviewQuestion).where(ReviewQuestion.level == "advanced")):
        q.is_active = False
    db_session.commit()
    c = course(get(client, admin_headers))
    assert c["ready"] is False and c["missing"] == ["Thiếu tự luận nâng cao: có 0/1 câu"]


def test_pending_counted_separately(client, seeded, admin_headers, db_session):
    skill_id = course(get(client, admin_headers, course_id=312))["skills"][0]["skill_id"]
    bank_service.create_question(
        db_session,
        {
            "skill_id": skill_id,
            "type": "mcq",
            "level": "recognize",
            "content": "Which function shows text on the screen?",
            "options": ["print()", "input()", "len()", "int()"],
            "correct_index": 0,
            "explanation": "print() writes to the screen.",
        },
        source="ai",
        review_status="pending",
    )
    db_session.commit()
    c = course(get(client, admin_headers, course_id=312))
    skill = next(s for s in c["skills"] if s["skill_id"] == skill_id)
    assert (skill["pending"], skill["active"]) == (1, 20)  # chờ duyệt không vào đề
    assert (c["pending"], c["active"]) == (1, 100)


def test_unknown_course_404(client, seeded, admin_headers):
    assert client.get(URL, params={"course_id": 99999}, headers=admin_headers).status_code == 404
