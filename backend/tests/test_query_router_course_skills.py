from app.ai.query_router import route_query
from app.services.sql_retrieval import retrieve_for_query
from app.models.course import Courses
from app.models.course_skill import CourseSkill
from app.models.skill import Skills


COURSE_TITLE = "Building Your Audience for Music Professionals Specialization"


def test_skill_queries_about_a_course_route_to_that_course():
    questions = [
        f"Cho tôi biết những skill trong hệ thống khóa {COURSE_TITLE}",
        f"Cho tôi biết những skill liên quan khóa học {COURSE_TITLE}",
    ]

    for question in questions:
        result = route_query(question)

        assert result["intent"] == "course_question"
        assert result["entity_type"] == "course"
        assert result["entity_name"] == COURSE_TITLE


def test_strategy_queries_exclude_question_tail_from_skill_name():
    questions = [
        "Cho tôi biết trong hệ thống có kỹ năng nào liên quan đến strategy hay không",
        "Cho tôi biết kỹ năng nào liên quan đến strategy có gì hay không",
    ]

    for question in questions:
        result = route_query(question)

        assert result["intent"] == "skill_search"
        assert result["entity_name"] == "strategy"


def test_course_skill_query_returns_at_most_five_active_skills(db_session):
    course = Courses(course_id=1, title=COURSE_TITLE)
    skills = [
        Skills(skill_id=index, skill=f"Skill {index}", is_active=True)
        for index in range(1, 7)
    ]
    inactive_skill = Skills(skill_id=7, skill="Inactive skill", is_active=False)

    db_session.add_all([course, *skills, inactive_skill])
    db_session.flush()
    db_session.add_all(
        [
            CourseSkill(course_id=course.course_id, skill_id=skill.skill_id)
            for skill in [*skills, inactive_skill]
        ]
    )
    db_session.commit()

    route_result = route_query(
        f"Cho tôi biết những skill trong hệ thống khóa {COURSE_TITLE}"
    )
    result = retrieve_for_query(db_session, route_result)

    assert result["found"] is True
    assert [skill["skill"] for skill in result["skills"]] == [
        "Skill 1",
        "Skill 2",
        "Skill 3",
        "Skill 4",
        "Skill 5",
    ]
