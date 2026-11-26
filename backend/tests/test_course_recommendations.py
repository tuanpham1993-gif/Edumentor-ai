import pytest

from app.core.security import create_access_token, hash_password
from app.models.course import Courses
from app.models.course_skill import CourseSkill
from app.models.skill import Skills
from app.models.user import Users
from app.models.user_course import UserCourse
from app.models.user_skill import UserSkill


@pytest.fixture
def course_rec_dataset(db_session):
    student = Users(
        email="rec_student@edumentor.vn",
        full_name="Rec Student",
        hashed_password=hash_password("Pass@1234"),
        role="student",
        is_active=True,
    )
    db_session.add(student)
    db_session.flush()

    skill_py = Skills(skill_id=8101, skill="Python", is_active=True)
    skill_rust = Skills(skill_id=8102, skill="Rust", is_active=True)
    skill_extra = Skills(skill_id=8103, skill="Data Science", is_active=True)
    db_session.add_all([skill_py, skill_rust, skill_extra])
    db_session.flush()

    # Khóa học 1: 5.0 sao nhưng chỉ có 1 review, không chuyên sâu (tên không có Python)
    c1 = Courses(
        course_id=8201,
        title="General Programming Basics",
        rating=5.0,
        num_reviews=1,
        num_enrolled=10,
        level="beginner",
        organization="TinyOrg",
        url="https://example.com/c1",
    )
    # Khóa học 2: 4.8 sao, 2000 reviews, tên chứa "Python" -> phải đứng đầu!
    c2 = Courses(
        course_id=8202,
        title="Python Fundamentals for Beginners",
        rating=4.8,
        num_reviews=2000,
        num_enrolled=50000,
        level="beginner",
        organization="Coursera",
        url="https://example.com/c2",
    )
    # Khóa học 3: Intermediate Python
    c3 = Courses(
        course_id=8203,
        title="Advanced Python Architecture",
        rating=4.7,
        num_reviews=500,
        num_enrolled=12000,
        level="intermediate",
        organization="edX",
        url="https://example.com/c3",
    )
    # Khóa học 4: Chưa liên kết bảng course_skill nhưng tiêu đề chứa Rust (dùng cho keyword fallback)
    c4 = Courses(
        course_id=8204,
        title="Rust Systems Programming",
        rating=4.9,
        num_reviews=300,
        num_enrolled=4000,
        level="intermediate",
        organization="Udemy",
        url="https://example.com/c4",
    )
    db_session.add_all([c1, c2, c3, c4])
    db_session.flush()

    db_session.add_all([
        CourseSkill(course_id=8201, skill_id=8101),
        CourseSkill(course_id=8201, skill_id=8103),
        CourseSkill(course_id=8202, skill_id=8101),
        CourseSkill(course_id=8203, skill_id=8101),
    ])

    db_session.add(
        UserSkill(user_id=student.user_id, skill_id=8101, status="learning", source="course")
    )
    db_session.add(
        UserCourse(user_id=student.user_id, course_id=8202, status="bookmarked")
    )
    db_session.commit()

    return {
        "token": create_access_token(student.user_id),
        "skill_py": skill_py.skill_id,
        "skill_rust": skill_rust.skill_id,
    }


def test_recommend_courses_ranking_and_user_context(client, course_rec_dataset):
    headers = {"Authorization": f"Bearer {course_rec_dataset['token']}"}
    res = client.get(
        f"/api/courses/recommendations?skill_id={course_rec_dataset['skill_py']}",
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()

    assert body["skill_name"] == "Python"
    assert body["user_skill_status"] == "learning"
    assert body["total"] == 3

    items = body["items"]
    # Khóa học khớp tiêu đề Python + uy tín cao phải xếp trên khóa 5.0 sao ít review
    assert items[0]["course_id"] == 8202
    assert items[0]["match_type"] == "direct"
    assert items[0]["is_bookmarked"] is True
    assert items[0]["user_status"] == "bookmarked"
    assert items[-1]["course_id"] == 8201


def test_recommend_courses_level_filter_and_guest(client, course_rec_dataset):
    res = client.get(
        f"/api/courses/recommendations?skill_id={course_rec_dataset['skill_py']}&level=intermediate"
    )
    assert res.status_code == 200
    body = res.json()
    assert body["user_skill_status"] is None
    assert body["total"] == 1
    assert body["items"][0]["course_id"] == 8203
    assert body["items"][0]["is_bookmarked"] is False


def test_recommend_courses_keyword_fallback(client, course_rec_dataset):
    res = client.get(
        f"/api/courses/recommendations?skill_id={course_rec_dataset['skill_rust']}"
    )
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 1
    assert body["items"][0]["course_id"] == 8204
    assert body["items"][0]["match_type"] == "keyword_fallback"


def test_recommend_courses_skill_not_found(client, course_rec_dataset):
    res = client.get("/api/courses/recommendations?skill_id=999999")
    assert res.status_code == 404
