import pytest
from app.models.course import Courses
from app.models.skill import Skills
from app.models.course_skill import CourseSkill


@pytest.fixture
def sample_data(db_session):
    skill_python = Skills(skill_id=1, skill="Python Programming", is_active=True)
    skill_ml = Skills(skill_id=2, skill="Machine Learning", is_active=True)
    skill_react = Skills(skill_id=3, skill="React", is_active=True)
    db_session.add_all([skill_python, skill_ml, skill_react])
    db_session.commit()

    course1 = Courses(
        course_id=1,
        title="Python for Beginners",
        instructor="Guido",
        organization="Python Org",
        description="Introduction to Python programming language",
        level="beginner",
        rating=4.8,
        num_reviews=1200,
        num_enrolled=5000,
        modules="4 modules",
        schedule="Flexible schedule",
        url="https://coursera.org/python-beginner",
        image="https://example.com/python.png",
    )
    course2 = Courses(
        course_id=2,
        title="Advanced Machine Learning",
        instructor="Andrew Ng",
        organization="Deeplearning.AI",
        description="Master advanced ML algorithms",
        level="advanced",
        rating=4.9,
        num_reviews=3500,
        num_enrolled=15000,
        modules="6 modules",
        schedule="Approx. 3 months",
        url="https://coursera.org/adv-ml",
        image="https://example.com/ml.png",
    )
    course3 = Courses(
        course_id=3,
        title="Fullstack React & Python",
        instructor="John Doe",
        organization="Meta",
        description="Build fullstack apps using React and Python backend",
        level="intermediate",
        rating=4.5,
        num_reviews=800,
        num_enrolled=3000,
        modules="5 modules",
        schedule="Self-paced",
        url="https://coursera.org/react-python",
        image="https://example.com/react-python.png",
    )

    db_session.add_all([course1, course2, course3])
    db_session.commit()

    # Thêm quan hệ course - skill
    cs1 = CourseSkill(course_id=1, skill_id=1)
    cs2 = CourseSkill(course_id=2, skill_id=2)
    cs3_1 = CourseSkill(course_id=3, skill_id=1)
    cs3_2 = CourseSkill(course_id=3, skill_id=3)
    db_session.add_all([cs1, cs2, cs3_1, cs3_2])
    db_session.commit()


def test_get_courses_list_all(client, sample_data):
    response = client.get("/api/courses")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["data"]) == 3
    assert data["page"] == 1
    assert data["page_size"] == 10

def test_get_courses_pagination(client, sample_data):
    response = client.get("/api/courses?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["data"]) == 2

    response_p2 = client.get("/api/courses?page=2&page_size=2")
    assert response_p2.status_code == 200
    data_p2 = response_p2.json()
    assert len(data_p2["data"]) == 1


def test_get_courses_search_keyword(client, sample_data):
    response = client.get("/api/courses?search=Andrew")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["course_id"] == 2


def test_get_courses_filter_by_level(client, sample_data):
    response = client.get("/api/courses?level=beginner")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["level"] == "beginner"


def test_get_courses_filter_by_skill_id(client, sample_data):
    # skill_id = 1 (Python) -> có trong course 1 và course 3
    response = client.get("/api/courses?skill_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    ids = [item["course_id"] for item in data["data"]]
    assert 1 in ids and 3 in ids


def test_get_courses_sort_by_rating(client, sample_data):
    response = client.get("/api/courses?sort_by=rating")
    assert response.status_code == 200
    data = response.json()
    # Rating: 4.9 (course 2) > 4.8 (course 1) > 4.5 (course 3)
    assert data["data"][0]["course_id"] == 2
    assert data["data"][1]["course_id"] == 1
    assert data["data"][2]["course_id"] == 3


def test_get_courses_sort_by_num_reviews(client, sample_data):
    response = client.get("/api/courses?sort_by=num_reviews")
    assert response.status_code == 200
    data = response.json()
    # Reviews: 3500 (course 2) > 1200 (course 1) > 800 (course 3)
    assert data["data"][0]["course_id"] == 2
    assert data["data"][1]["course_id"] == 1
    assert data["data"][2]["course_id"] == 3


def test_get_course_detail_success(client, sample_data):
    response = client.get("/api/courses/1")
    assert response.status_code == 200
    data = response.json()
    assert data["course_id"] == 1
    assert data["title"] == "Python for Beginners"
    assert "skills_info" in data
    assert len(data["skills_info"]) == 1
    assert data["skills_info"][0]["skill"] == "Python Programming"


def test_get_course_detail_not_found(client, sample_data):
    response = client.get("/api/courses/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found."


def test_get_course_skills_success(client, sample_data):
    response = client.get("/api/courses/3/skills")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    skill_names = [s["skill"] for s in data]
    assert "Python Programming" in skill_names
    assert "React" in skill_names


def test_get_course_skills_not_found(client, sample_data):
    response = client.get("/api/courses/99999/skills")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found."

