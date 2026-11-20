"""Ôn tập trên đồ thị lộ trình — GET /api/me/review/skills (module 09 · Tuấn · 20/11/2026).

Mỗi kỹ năng → các khóa người học đã tham gia có dạy kỹ năng đó và ôn tập được, kèm lần làm gần nhất.
Dữ liệu mẫu (bank_312): khóa 312 có đủ đề; khóa 999 dùng chung kỹ năng SKILL_IDS[0] nhưng CHƯA có đề.

Chạy:  python -m pytest tests/test_review_skills.py -v      (trong thư mục backend)
"""

# ruff: noqa: F811 — fixture bank_312 import từ test_review_api; pytest truyền qua TÊN tham số

from app.models import UserCourse
from tests.test_review_api import SKILL_IDS, bank_312, start, user_of  # noqa: F401 — bank_312 là fixture
from tests.test_review_submit import submit

URL = "/api/me/review/skills"


def get(client, headers, ids):
    response = client.get(URL, params={"skill_ids": ",".join(str(i) for i in ids)}, headers=headers)
    assert response.status_code == 200, response.text
    return {item["skill_id"]: item["courses"] for item in response.json()["items"]}


def test_lists_only_reviewable_enrolled_courses(client, bank_312, student_headers):
    shared = SKILL_IDS[0]  # khóa 312 (có đề) và 999 (chưa có đề) cùng dạy
    body = get(client, student_headers, [shared, 99001, 424242, shared])

    assert list(body) == [shared, 99001, 424242]  # đúng thứ tự gửi, bỏ trùng
    [course] = body[shared]
    assert course == {
        "course_id": 312,
        "course_title": "Python Basics: Selection and Iteration",
        "enrollment": "ongoing",
        "in_progress_attempt_id": None,
        "last_attempt": None,
    }
    assert body[99001] == [] and body[424242] == []  # 999 chưa có đề; kỹ năng lạ → rỗng (không hiện huy hiệu)


def test_shows_in_progress_then_last_attempt(client, bank_312, student_headers):
    attempt_id = start(client, student_headers)["attempt_id"]
    [course] = get(client, student_headers, [SKILL_IDS[1]])[SKILL_IDS[1]]
    assert course["in_progress_attempt_id"] == attempt_id and course["last_attempt"] is None

    submit(client, student_headers, attempt_id)
    [course] = get(client, student_headers, [SKILL_IDS[1]])[SKILL_IDS[1]]
    assert course["in_progress_attempt_id"] is None
    last = course["last_attempt"]
    assert (
        last["attempt_id"] == attempt_id
        and last["status"] == "graded"
        and last["score"] == 0
        and last["passed"] is False
    )


def test_abandoned_or_bookmarked_courses_are_hidden(client, bank_312, student_headers, db_session):
    row = db_session.query(UserCourse).filter_by(user_id=user_of(db_session).user_id, course_id=312).one()
    for status in ("abandoned", "bookmarked"):
        row.status = status
        db_session.commit()
        assert get(client, student_headers, SKILL_IDS)[SKILL_IDS[0]] == []


def test_each_user_sees_only_own_courses(client, bank_312, student_headers, admin_headers):
    start(client, student_headers)
    assert get(client, admin_headers, SKILL_IDS)[SKILL_IDS[0]] == []  # admin chưa tham gia khóa nào


def test_requires_login_and_valid_ids(client, bank_312, student_headers):
    assert client.get(URL, params={"skill_ids": "1"}).status_code == 401
    assert client.get(URL, params={"skill_ids": "1,abc"}, headers=student_headers).status_code == 422
    assert client.get(URL, headers=student_headers).status_code == 422
    too_many = ",".join(str(i) for i in range(101))
    assert client.get(URL, params={"skill_ids": too_many}, headers=student_headers).status_code == 422
    assert client.get(URL, params={"skill_ids": ""}, headers=student_headers).json() == {"items": []}
