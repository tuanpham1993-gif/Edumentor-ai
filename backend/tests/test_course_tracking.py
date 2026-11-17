"""Test module Lưu khóa học và Theo dõi trạng thái (`user_courses`).

Bao phủ 8 endpoint + tích hợp kỹ năng hồ sơ (D05, S7) + cổng nối module 09 (`course_gateway.py`):
  - POST   /api/me/bookmarks
  - GET    /api/me/bookmarks
  - DELETE /api/me/bookmarks/{course_id}
  - POST   /api/courses/{course_id}/join
  - GET    /api/me/courses
  - GET    /api/me/courses/{course_id}/status
  - PATCH  /api/me/courses/{course_id}/status
  - DELETE /api/me/courses/{course_id}
"""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import (
    Courses,
    CourseSkill,
    ReviewAnswer,
    ReviewAttempt,
    Skills,
    UserCourse,
    Users,
    UserSkill,
)
from app.services import (
    course_gateway,
    course_tracking_service,
    review_service,
    user_skill_service,
)
from scripts import seed_review

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
ME_URL = "/api/me"
BOOKMARKS_URL = "/api/me/bookmarks"
MY_COURSES_URL = "/api/me/courses"
PASSWORD = "Abc@1234"


def register_and_login(client, email: str, full_name: str = "Học Viên"):
    res = client.post(
        REGISTER_URL,
        json={
            "full_name": full_name,
            "email": email,
            "password": PASSWORD,
            "confirm_password": PASSWORD,
        },
    )
    assert res.status_code == 201, res.text
    token = client.post(LOGIN_URL, json={"email": email, "password": PASSWORD}).json()[
        "access_token"
    ]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = client.get(ME_URL, headers=headers).json()["user_id"]
    return headers, user_id


def skill_profile(db_session, user_id: int) -> dict[int, tuple[str, str]]:
    rows = db_session.query(UserSkill).filter_by(user_id=user_id).all()
    return {row.skill_id: (row.status, row.source) for row in rows}


@pytest.fixture()
def catalog(db_session):
    """Tạo 4 kỹ năng (1 kỹ năng ẩn) và 4 khóa học (bao gồm khóa url=None)."""
    skills = [
        Skills(skill_id=1, skill="Python", is_active=True),
        Skills(skill_id=2, skill="SQL", is_active=True),
        Skills(skill_id=3, skill="Docker", is_active=True),
        Skills(skill_id=4, skill="Legacy Tool", is_active=False),
    ]
    courses = [
        Courses(
            course_id=1,
            title="Python & SQL Foundation",
            instructor="Guido",
            organization="Coursera",
            level="beginner",
            rating=4.8,
            num_reviews=100,
            url="https://coursera.org/python-sql",
            image="https://example.com/1.png",
        ),
        Courses(
            course_id=2,
            title="SQL & Docker Practical",
            instructor="Ada",
            organization="edX",
            level="intermediate",
            rating=4.7,
            num_reviews=50,
            url="https://edx.org/sql-docker",
        ),
        Courses(
            course_id=3,
            title="Course Without External URL",
            instructor="Linus",
            organization="EduMentor",
            level="beginner",
            url=None,
        ),
        Courses(
            course_id=4,
            title="Extra Catalog Course",
            instructor="Grace",
            organization="Coursera",
            level="advanced",
            url="https://coursera.org/extra",
        ),
    ]
    db_session.add_all(skills + courses)
    db_session.flush()
    db_session.add_all(
        [
            CourseSkill(course_id=1, skill_id=1),
            CourseSkill(course_id=1, skill_id=2),
            CourseSkill(course_id=1, skill_id=4),  # kỹ năng đã tắt -> không tự thêm
            CourseSkill(course_id=2, skill_id=2),
            CourseSkill(course_id=2, skill_id=3),
            CourseSkill(course_id=3, skill_id=1),
        ]
    )
    db_session.commit()


# ─────────────── Ràng buộc tầng Model / DB ───────────────


def test_user_course_model_constraints(db_session, catalog, client):
    _, user_id = register_and_login(client, "model@test.vn")

    with pytest.raises(IntegrityError):
        db_session.add(UserCourse(user_id=user_id, course_id=1, status="paused"))
        db_session.flush()
    db_session.rollback()

    db_session.add(UserCourse(user_id=user_id, course_id=1, status="bookmarked"))
    db_session.flush()

    with pytest.raises(IntegrityError):
        db_session.add(UserCourse(user_id=user_id, course_id=1, status="ongoing"))
        db_session.flush()
    db_session.rollback()


# ─────────────── Xác thực (401) ───────────────


def test_all_endpoints_require_authentication(client):
    assert client.post(BOOKMARKS_URL, json={"course_id": 1}).status_code == 401
    assert client.get(BOOKMARKS_URL).status_code == 401
    assert client.delete(f"{BOOKMARKS_URL}/1").status_code == 401
    assert client.post("/api/courses/1/join").status_code == 401
    assert client.get(MY_COURSES_URL).status_code == 401
    assert client.get(f"{MY_COURSES_URL}/1/status").status_code == 401
    assert (
        client.patch(
            f"{MY_COURSES_URL}/1/status", json={"status": "ongoing"}
        ).status_code
        == 401
    )
    assert client.delete(f"{MY_COURSES_URL}/1").status_code == 401


# ─────────────── Bookmark CRUD ───────────────


def test_bookmark_create_list_and_hard_delete(client, db_session, catalog):
    headers_a, user_a = register_and_login(client, "a@test.vn")
    headers_b, _ = register_and_login(client, "b@test.vn")

    created = client.post(BOOKMARKS_URL, json={"course_id": 1}, headers=headers_a)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["course_id"] == 1
    assert body["title"] == "Python & SQL Foundation"
    assert body["status"] == "bookmarked"
    assert body["joined_at"] is None
    assert body["completed_at"] is None
    assert len(body["skills_info"]) == 3

    # Trùng bookmark -> 409
    dup = client.post(BOOKMARKS_URL, json={"course_id": 1}, headers=headers_a)
    assert dup.status_code == 409

    # Người khác không thấy bookmark của A
    assert client.get(BOOKMARKS_URL, headers=headers_b).json()["total"] == 0

    # Phân trang bookmark
    assert (
        client.post(BOOKMARKS_URL, json={"course_id": 2}, headers=headers_a).status_code
        == 201
    )
    page1 = client.get(
        BOOKMARKS_URL, params={"page": 1, "page_size": 1}, headers=headers_a
    ).json()
    assert page1["total"] == 2
    assert len(page1["items"]) == 1

    # Xóa bookmark -> hard delete, KHÔNG tạo abandoned, KHÔNG đụng kỹ năng
    deleted = client.delete(f"{BOOKMARKS_URL}/1", headers=headers_a)
    assert deleted.status_code == 200
    assert (
        db_session.query(UserCourse)
        .filter_by(user_id=user_a, course_id=1)
        .one_or_none()
        is None
    )
    assert skill_profile(db_session, user_a) == {}

    # Xóa lại -> 404
    assert client.delete(f"{BOOKMARKS_URL}/1", headers=headers_a).status_code == 404


def test_bookmark_not_found_and_validation(client, catalog):
    headers, _ = register_and_login(client, "bm@test.vn")
    assert (
        client.post(
            BOOKMARKS_URL, json={"course_id": 99999}, headers=headers
        ).status_code
        == 404
    )
    assert (
        client.post(BOOKMARKS_URL, json={"course_id": 0}, headers=headers).status_code
        == 422
    )
    assert client.delete(f"{BOOKMARKS_URL}/99999", headers=headers).status_code == 404


def test_bookmark_conflicts_when_ongoing_or_completed(client, db_session, catalog):
    headers, user_id = register_and_login(client, "bm_conflict@test.vn")

    # Đang ongoing -> cả POST bookmark và DELETE bookmark đều 409
    assert client.post("/api/courses/1/join", headers=headers).status_code == 200
    assert (
        client.post(BOOKMARKS_URL, json={"course_id": 1}, headers=headers).status_code
        == 409
    )
    assert client.delete(f"{BOOKMARKS_URL}/1", headers=headers).status_code == 409
    assert db_session.get(UserCourse, (user_id, 1)).status == "ongoing"

    # Đã completed -> cả POST bookmark và DELETE bookmark đều 409
    row = db_session.get(UserCourse, (user_id, 1))
    row.status = "completed"
    row.completed_at = datetime.now(UTC)
    db_session.commit()

    assert (
        client.post(BOOKMARKS_URL, json={"course_id": 1}, headers=headers).status_code
        == 409
    )
    assert client.delete(f"{BOOKMARKS_URL}/1", headers=headers).status_code == 409
    assert db_session.get(UserCourse, (user_id, 1)).status == "completed"


def test_rebookmark_from_abandoned(client, db_session, catalog):
    headers, user_id = register_and_login(client, "rebm@test.vn")
    assert client.post("/api/courses/1/join", headers=headers).status_code == 200
    assert client.delete(f"{MY_COURSES_URL}/1", headers=headers).status_code == 200
    assert db_session.get(UserCourse, (user_id, 1)).status == "abandoned"

    # Lưu lại từ trạng thái abandoned -> chuyển về bookmarked
    res = client.post(BOOKMARKS_URL, json={"course_id": 1}, headers=headers)
    assert res.status_code == 201
    assert res.json()["status"] == "bookmarked"
    assert res.json()["joined_at"] is None


# ─────────────── POST /api/courses/{course_id}/join ───────────────


def test_join_from_scratch_adds_active_skills_and_preserves_known(
    client, db_session, catalog
):
    headers, user_id = register_and_login(client, "join@test.vn")
    # Kỹ năng 2 (SQL) người dùng đã biết từ trước -> phải giữ nguyên known/manual
    db_session.add(
        UserSkill(user_id=user_id, skill_id=2, status="known", source="manual")
    )
    db_session.commit()

    res = client.post("/api/courses/1/join", headers=headers)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["course_id"] == 1
    assert body["status"] == "ongoing"
    assert body["url"] == "https://coursera.org/python-sql"
    assert body["joined_at"] is not None

    # Chỉ thêm skill_id=1 (active), giữ skill_id=2 (known/manual), bỏ qua skill_id=4 (inactive)
    assert skill_profile(db_session, user_id) == {
        1: ("learning", "course"),
        2: ("known", "manual"),
    }


def test_join_idempotent_on_ongoing_and_completed(client, db_session, catalog):
    headers, user_id = register_and_login(client, "join_idem@test.vn")

    # Join lần 1
    first = client.post("/api/courses/1/join", headers=headers).json()
    # Hạ joined_at xuống quá khứ để kiểm tra join lần 2 không ghi đè joined_at
    row = db_session.get(UserCourse, (user_id, 1))
    old_joined = datetime.now(UTC) - timedelta(days=5)
    row.joined_at = old_joined
    db_session.commit()
    first_check = client.get(f"{MY_COURSES_URL}/1/status", headers=headers).json()

    # Join lần 2 khi đang ongoing -> 200, giữ nguyên status và joined_at
    second = client.post("/api/courses/1/join", headers=headers)
    assert second.status_code == 200
    assert second.json()["status"] == "ongoing"
    assert second.json()["joined_at"] == first_check["joined_at"]
    assert second.json()["url"] == first["url"]

    # Chuyển sang completed -> join lần 3 vẫn 200, KHÔNG hạ xuống ongoing
    row = db_session.get(UserCourse, (user_id, 1))
    row.status = "completed"
    row.completed_at = datetime.now(UTC)
    db_session.commit()

    third = client.post("/api/courses/1/join", headers=headers)
    assert third.status_code == 200
    assert third.json()["status"] == "completed"
    assert third.json()["url"] == "https://coursera.org/python-sql"
    assert third.json()["joined_at"] == first_check["joined_at"]
    assert db_session.get(UserCourse, (user_id, 1)).status == "completed"


def test_join_when_course_url_is_none(client, db_session, catalog):
    headers, user_id = register_and_login(client, "nourl@test.vn")
    res = client.post("/api/courses/3/join", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "ongoing"
    assert res.json()["url"] is None
    assert skill_profile(db_session, user_id) == {1: ("learning", "course")}


def test_join_from_bookmarked_and_unknown_course(client, db_session, catalog):
    headers, user_id = register_and_login(client, "join_bm@test.vn")
    assert client.post("/api/courses/99999/join", headers=headers).status_code == 404

    assert (
        client.post(BOOKMARKS_URL, json={"course_id": 1}, headers=headers).status_code
        == 201
    )
    res = client.post("/api/courses/1/join", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "ongoing"
    assert skill_profile(db_session, user_id) == {
        1: ("learning", "course"),
        2: ("learning", "course"),
    }


# ─────────────── GET /api/me/courses & /status ───────────────


def test_get_course_status_and_list_filters(client, db_session, catalog):
    headers, user_id = register_and_login(client, "list@test.vn")

    # Chưa theo dõi
    st = client.get(f"{MY_COURSES_URL}/1/status", headers=headers)
    assert st.status_code == 200
    assert st.json() == {
        "course_id": 1,
        "status": None,
        "is_bookmarked": False,
        "joined_at": None,
        "completed_at": None,
        "updated_at": None,
    }
    assert (
        client.get(f"{MY_COURSES_URL}/99999/status", headers=headers).status_code == 404
    )

    # Tạo đủ 4 trạng thái:
    # course 1: bookmarked, course 2: ongoing, course 3: completed, course 4: abandoned
    client.post(BOOKMARKS_URL, json={"course_id": 1}, headers=headers)
    client.post("/api/courses/2/join", headers=headers)
    client.post("/api/courses/3/join", headers=headers)
    client.post("/api/courses/4/join", headers=headers)
    client.delete(f"{MY_COURSES_URL}/4", headers=headers)
    row3 = db_session.get(UserCourse, (user_id, 3))
    row3.status = "completed"
    row3.completed_at = datetime.now(UTC)
    db_session.commit()

    # Kiểm tra /status khi bookmarked
    assert (
        client.get(f"{MY_COURSES_URL}/1/status", headers=headers).json()[
            "is_bookmarked"
        ]
        is True
    )
    assert (
        client.get(f"{MY_COURSES_URL}/2/status", headers=headers).json()[
            "is_bookmarked"
        ]
        is False
    )

    # GET /api/me/courses mặc định loại trừ abandoned
    default_list = client.get(MY_COURSES_URL, headers=headers).json()
    assert default_list["total"] == 3
    assert {item["course_id"] for item in default_list["items"]} == {1, 2, 3}

    # Lọc từng trạng thái
    for status_name, expected_id in [
        ("bookmarked", 1),
        ("ongoing", 2),
        ("completed", 3),
        ("abandoned", 4),
    ]:
        filtered = client.get(
            MY_COURSES_URL, params={"status": status_name}, headers=headers
        )
        assert filtered.status_code == 200
        data = filtered.json()
        assert data["total"] == 1
        assert [i["course_id"] for i in data["items"]] == [expected_id]

    assert (
        client.get(
            MY_COURSES_URL, params={"status": "invalid"}, headers=headers
        ).status_code
        == 422
    )


# ─────────────── PATCH /status & DELETE /api/me/courses/{course_id} ───────────────


def test_patch_status_transitions_and_guards(client, db_session, catalog):
    headers, user_id = register_and_login(client, "patch@test.vn")

    # Chưa theo dõi -> 404; khóa không tồn tại -> 404
    assert (
        client.patch(
            f"{MY_COURSES_URL}/99999/status",
            json={"status": "ongoing"},
            headers=headers,
        ).status_code
        == 404
    )
    assert (
        client.patch(
            f"{MY_COURSES_URL}/1/status",
            json={"status": "ongoing"},
            headers=headers,
        ).status_code
        == 404
    )

    # Luôn chặn gửi completed thủ công (422)
    client.post(BOOKMARKS_URL, json={"course_id": 1}, headers=headers)
    assert (
        client.patch(
            f"{MY_COURSES_URL}/1/status",
            json={"status": "completed"},
            headers=headers,
        ).status_code
        == 422
    )

    # bookmarked -> abandoned không hợp lệ (409); bookmarked -> bookmarked -> 409
    assert (
        client.patch(
            f"{MY_COURSES_URL}/1/status",
            json={"status": "abandoned"},
            headers=headers,
        ).status_code
        == 409
    )
    assert (
        client.patch(
            f"{MY_COURSES_URL}/1/status",
            json={"status": "bookmarked"},
            headers=headers,
        ).status_code
        == 409
    )

    # bookmarked -> ongoing (hợp lệ, gọi add_learning_from_course)
    to_ongoing = client.patch(
        f"{MY_COURSES_URL}/1/status", json={"status": "ongoing"}, headers=headers
    )
    assert to_ongoing.status_code == 200
    assert to_ongoing.json()["status"] == "ongoing"
    assert to_ongoing.json()["joined_at"] is not None
    assert skill_profile(db_session, user_id) == {
        1: ("learning", "course"),
        2: ("learning", "course"),
    }

    # ongoing -> bookmarked không hợp lệ (409); ongoing -> ongoing -> 409
    assert (
        client.patch(
            f"{MY_COURSES_URL}/1/status",
            json={"status": "bookmarked"},
            headers=headers,
        ).status_code
        == 409
    )
    assert (
        client.patch(
            f"{MY_COURSES_URL}/1/status",
            json={"status": "ongoing"},
            headers=headers,
        ).status_code
        == 409
    )

    # ongoing -> abandoned (gỡ learning course, giữ skill của khóa đang học khác)
    client.post("/api/courses/2/join", headers=headers)  # học thêm khóa 2 (SQL, Docker)
    to_abandoned = client.patch(
        f"{MY_COURSES_URL}/1/status", json={"status": "abandoned"}, headers=headers
    )
    assert to_abandoned.status_code == 200
    assert to_abandoned.json()["status"] == "abandoned"
    # Skill 1 (chỉ ở khóa 1) bị gỡ; skill 2 (dùng chung khóa 2 ongoing) & 3 (khóa 2) được giữ
    assert skill_profile(db_session, user_id) == {
        2: ("learning", "course"),
        3: ("learning", "course"),
    }

    # abandoned -> bookmarked không hợp lệ qua PATCH (409)
    assert (
        client.patch(
            f"{MY_COURSES_URL}/1/status",
            json={"status": "bookmarked"},
            headers=headers,
        ).status_code
        == 409
    )

    # abandoned -> ongoing (học lại -> thêm lại skill 1)
    rejoin = client.patch(
        f"{MY_COURSES_URL}/1/status", json={"status": "ongoing"}, headers=headers
    )
    assert rejoin.status_code == 200
    assert rejoin.json()["status"] == "ongoing"
    assert skill_profile(db_session, user_id) == {
        1: ("learning", "course"),
        2: ("learning", "course"),
        3: ("learning", "course"),
    }

    # Nếu đang completed -> chặn mọi thao tác đổi trạng thái thủ công (409)
    row = db_session.get(UserCourse, (user_id, 1))
    row.status = "completed"
    row.completed_at = datetime.now(UTC)
    db_session.commit()
    for target in ("ongoing", "abandoned", "bookmarked"):
        assert (
            client.patch(
                f"{MY_COURSES_URL}/1/status",
                json={"status": target},
                headers=headers,
            ).status_code
            == 409
        )


def test_delete_my_course_abandon_and_skill_cleanup(client, db_session, catalog):
    headers, user_id = register_and_login(client, "abandon@test.vn")

    # Khóa không tồn tại hoặc chưa theo dõi -> 404
    assert client.delete(f"{MY_COURSES_URL}/99999", headers=headers).status_code == 404
    assert client.delete(f"{MY_COURSES_URL}/1", headers=headers).status_code == 404

    # Đang bookmarked -> 409 (hướng dẫn dùng xóa bookmark)
    client.post(BOOKMARKS_URL, json={"course_id": 1}, headers=headers)
    bm_res = client.delete(f"{MY_COURSES_URL}/1", headers=headers)
    assert bm_res.status_code == 409

    # Tham gia khóa 1 (1 Python, 2 SQL) và khóa 2 (2 SQL, 3 Docker)
    client.post("/api/courses/1/join", headers=headers)
    client.post("/api/courses/2/join", headers=headers)

    # Bỏ khóa 1 -> status thành abandoned, giữ skill 2 (vì khóa 2 đang ongoing), gỡ skill 1
    res = client.delete(f"{MY_COURSES_URL}/1", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "abandoned"
    assert db_session.get(UserCourse, (user_id, 1)).status == "abandoned"
    assert skill_profile(db_session, user_id) == {
        2: ("learning", "course"),
        3: ("learning", "course"),
    }

    # Bỏ lại khóa đã abandoned -> 409
    assert client.delete(f"{MY_COURSES_URL}/1", headers=headers).status_code == 409

    # Đang completed -> 409
    row2 = db_session.get(UserCourse, (user_id, 2))
    row2.status = "completed"
    row2.completed_at = datetime.now(UTC)
    db_session.commit()
    assert client.delete(f"{MY_COURSES_URL}/2", headers=headers).status_code == 409


def test_abandon_rollback_when_skill_cleanup_fails(
    client, db_session, catalog, monkeypatch
):
    headers, user_id = register_and_login(client, "rollback@test.vn")
    client.post("/api/courses/1/join", headers=headers)

    def broken_remove(*args, **kwargs):
        raise RuntimeError("skill service lỗi")

    monkeypatch.setattr(
        user_skill_service, "remove_learning_from_course", broken_remove
    )
    with pytest.raises(RuntimeError):
        review_user = db_session.get(Users, user_id)
        course_tracking_service.abandon_course(db_session, review_user, 1)

    assert db_session.get(UserCourse, (user_id, 1)).status == "ongoing"


# ─────────────── Tích hợp course_gateway với Module 09 (Ôn tập) ───────────────


@pytest.fixture()
def bank_312_untracked(db_session):
    bank = seed_review.load_bank(seed_review.DEFAULT_FILE)
    skill_ids = sorted(bank["skills"].values())
    db_session.add(
        Courses(
            course_id=312,
            title="Python Basics: Selection and Iteration",
            url="https://coursera.org/learn/python-basics",
        )
    )
    for skill_id in skill_ids:
        db_session.add(
            Skills(skill_id=skill_id, skill=f"Kỹ năng {skill_id}", is_active=True)
        )
    db_session.flush()
    for skill_id in skill_ids:
        db_session.add(CourseSkill(course_id=312, skill_id=skill_id))
    seed_review.seed_bank(db_session, bank)
    db_session.commit()
    return skill_ids


def test_gateway_end_to_end_with_review_module(client, db_session, bank_312_untracked):
    headers, user_id = register_and_login(client, "gw@test.vn")

    # 1. Chưa tham gia -> gateway trả None -> module 09 chặn not_enrolled (403)
    assert course_gateway.get_enrollment_status(db_session, user_id, 312) is None
    info = client.get("/api/courses/312/review", headers=headers).json()
    assert info["can_start"] is False
    assert info["blocked"]["code"] == "not_enrolled"
    assert (
        client.post("/api/courses/312/review-attempts", headers=headers).status_code
        == 403
    )

    # 2. Đã bookmark nhưng chưa join -> vẫn chưa thể ôn tập (gateway trả None)
    assert (
        client.post(BOOKMARKS_URL, json={"course_id": 312}, headers=headers).status_code
        == 201
    )
    assert course_gateway.get_enrollment_status(db_session, user_id, 312) is None
    assert (
        client.post("/api/courses/312/review-attempts", headers=headers).status_code
        == 403
    )

    # 3. Join khóa -> ongoing -> gateway ánh xạ IN_PROGRESS -> bắt đầu ôn tập được
    assert client.post("/api/courses/312/join", headers=headers).status_code == 200
    assert (
        course_gateway.get_enrollment_status(db_session, user_id, 312)
        == course_gateway.IN_PROGRESS
    )
    attempt = client.post("/api/courses/312/review-attempts", headers=headers)
    assert attempt.status_code == 200
    attempt_id = attempt.json()["attempt_id"]

    # Trả lời đúng 12 câu trắc nghiệm (= 6.0 điểm -> đạt ngưỡng)
    answers = (
        db_session.query(ReviewAnswer)
        .filter_by(attempt_id=attempt_id)
        .order_by(ReviewAnswer.position)
        .all()
    )
    mcq_payload = [
        {
            "position": ans.position,
            "selected_index": ans.option_order.index(ans.question.correct_index),
        }
        for ans in answers
        if ans.question.type == "mcq"
    ]
    assert (
        client.patch(
            f"/api/review-attempts/{attempt_id}/answers",
            json={"answers": mcq_payload},
            headers=headers,
        ).status_code
        == 200
    )

    submitted = client.post(
        f"/api/review-attempts/{attempt_id}/submit", headers=headers
    )
    assert submitted.status_code == 200
    assert submitted.json()["passed"] is True
    assert submitted.json()["completed_course"] is True

    # 4. Gateway đã chuyển UserCourse -> completed & đặt completed_at trong cùng transaction
    db_session.expire_all()
    uc = db_session.get(UserCourse, (user_id, 312))
    assert uc.status == "completed"
    assert uc.completed_at is not None
    assert (
        course_gateway.get_enrollment_status(db_session, user_id, 312)
        == course_gateway.COMPLETED
    )
    # Các kỹ năng của khóa được nâng lên known (source="review")
    profile = skill_profile(db_session, user_id)
    assert all(profile[sid] == ("known", "review") for sid in bank_312_untracked)


def test_gateway_abandoned_blocks_review_and_rejoin_unlocks(
    client, db_session, bank_312_untracked
):
    headers, user_id = register_and_login(client, "gw_ab@test.vn")
    client.post("/api/courses/312/join", headers=headers)
    client.delete(f"{MY_COURSES_URL}/312", headers=headers)

    assert (
        course_gateway.get_enrollment_status(db_session, user_id, 312)
        == course_gateway.ABANDONED
    )
    info = client.get("/api/courses/312/review", headers=headers).json()
    assert info["can_start"] is False
    assert info["blocked"]["code"] == "abandoned"
    assert (
        client.post("/api/courses/312/review-attempts", headers=headers).status_code
        == 403
    )

    # Tham gia lại -> mở khóa ôn tập
    client.post("/api/courses/312/join", headers=headers)
    assert (
        client.post("/api/courses/312/review-attempts", headers=headers).status_code
        == 200
    )


def test_gateway_mark_completed_rolls_back_with_review_transaction(
    client, db_session, bank_312_untracked, monkeypatch
):
    """mark_course_completed chỉ flush(): nếu submit lỗi sau bước này thì UserCourse phải rollback."""
    headers, user_id = register_and_login(client, "gw_rb@test.vn")
    client.post("/api/courses/312/join", headers=headers)
    attempt_id = client.post(
        "/api/courses/312/review-attempts", headers=headers
    ).json()["attempt_id"]

    answers = (
        db_session.query(ReviewAnswer)
        .filter_by(attempt_id=attempt_id)
        .order_by(ReviewAnswer.position)
        .all()
    )
    mcq_payload = [
        {
            "position": ans.position,
            "selected_index": ans.option_order.index(ans.question.correct_index),
        }
        for ans in answers
        if ans.question.type == "mcq"
    ]
    client.patch(
        f"/api/review-attempts/{attempt_id}/answers",
        json={"answers": mcq_payload},
        headers=headers,
    )

    def broken_mark_known(*args, **kwargs):
        raise RuntimeError("lỗi cập nhật user_skills")

    monkeypatch.setattr(user_skill_service, "mark_known", broken_mark_known)
    user = db_session.get(Users, user_id)
    with pytest.raises(RuntimeError):
        review_service.submit_attempt(db_session, user, attempt_id)

    db_session.expire_all()
    uc = db_session.get(UserCourse, (user_id, 312))
    attempt = db_session.get(ReviewAttempt, attempt_id)
    assert uc.status == "ongoing"
    assert uc.completed_at is None
    assert attempt.status == "in_progress"
