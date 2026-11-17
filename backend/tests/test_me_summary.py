"""Test GET /api/me/summary — 4 ô thống kê trang Hồ sơ (module 01 · Tuấn · 7.2, 12/11/2026).

Chạy:  python -m pytest tests/test_me_summary.py -v      (trong thư mục backend)
"""

from app.models import UserCourse, UserSkill
from app.models.course import Courses
from app.models.skill import Skills
from app.models.user import Users

URL = "/api/me/summary"


def student(db_session, email="student.test@edumentor.vn"):
    return db_session.query(Users).filter_by(email=email).one()


def test_requires_login(client):
    assert client.get(URL).status_code == 401


def test_new_user_all_zero(client, student_headers):
    assert client.get(URL, headers=student_headers).json() == {
        "courses_in_progress": 0,
        "courses_completed": 0,
        "known_skills": 0,
        "active_paths": None,  # chờ lộ trình của Hòa dùng users.user_id
    }


def test_counts_only_my_rows_by_status(client, db_session, student_headers, admin_headers):
    me = student(db_session)
    admin = student(db_session, "admin.test@edumentor.vn")
    db_session.add_all([Courses(course_id=c, title=f"Khóa {c}") for c in range(1, 7)])
    db_session.add_all([Skills(skill_id=s, skill=f"Kỹ năng {s}", is_active=True) for s in (1, 2, 3)])
    db_session.flush()
    db_session.add_all(
        [
            UserCourse(user_id=me.user_id, course_id=1, status="ongoing"),
            UserCourse(user_id=me.user_id, course_id=2, status="ongoing"),
            UserCourse(user_id=me.user_id, course_id=3, status="completed"),
            UserCourse(user_id=me.user_id, course_id=4, status="bookmarked"),  # không tính
            UserCourse(user_id=me.user_id, course_id=5, status="abandoned"),  # không tính
            UserCourse(user_id=admin.user_id, course_id=6, status="ongoing"),  # của người khác
            UserSkill(user_id=me.user_id, skill_id=1, status="known", source="manual"),
            UserSkill(user_id=me.user_id, skill_id=2, status="known", source="review"),
            UserSkill(user_id=me.user_id, skill_id=3, status="learning", source="course"),  # không tính
            UserSkill(user_id=admin.user_id, skill_id=3, status="known", source="manual"),  # của người khác
        ]
    )
    db_session.commit()

    body = client.get(URL, headers=student_headers).json()

    assert body == {"courses_in_progress": 2, "courses_completed": 1, "known_skills": 2, "active_paths": None}
