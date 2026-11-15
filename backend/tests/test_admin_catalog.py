from app.models.skill import Skills
from fastapi.testclient import TestClient

# ==============================================================================
# 1. TEST SUITE: ADMIN COURSES (/api/admin/courses)
# ==============================================================================


def test_create_admin_course_success(client: TestClient, admin_headers):
    """POST /api/admin/courses: Thêm mới khóa học thành công với quyền admin."""
    payload = {
        "title": "Python for Data Science",
        "num_enrolled": 1500,
        "rating": 4.8,
        "num_reviews": 320,
        "instructor": "John Doe",
        "organization": "Coursera",
        "description": "Learn python from scratch with practical data science projects.",
        "modules": "4 modules",
        "level": "beginner",
        "schedule": "Approx. 20 hours",
        "url": "https://coursera.org/learn/python-data-science",
        "image": "https://coursera.org/image.png",
    }
    response = client.post("/api/admin/courses", json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["level"] == "beginner"
    assert data["rating"] == 4.8
    assert "course_id" in data


def test_create_admin_course_duplicate_url(client: TestClient, admin_headers):
    """POST /api/admin/courses: Báo lỗi 409 Conflict khi URL đã tồn tại."""
    payload = {
        "title": "Unique Course",
        "url": "https://coursera.org/learn/unique-url",
    }
    res1 = client.post("/api/admin/courses", json=payload, headers=admin_headers)
    assert res1.status_code == 201

    res2 = client.post("/api/admin/courses", json=payload, headers=admin_headers)
    assert res2.status_code == 409
    assert "đã tồn tại" in res2.json()["detail"]


def test_create_admin_course_invalid_data(client: TestClient, admin_headers):
    """POST /api/admin/courses: Báo lỗi 422 khi dữ liệu không hợp lệ (ví dụ rating > 5 hoặc title rỗng)."""
    # Rating vượt quá 5.0
    payload_invalid_rating = {
        "title": "Bad Rating Course",
        "rating": 6.5,
    }
    res = client.post(
        "/api/admin/courses", json=payload_invalid_rating, headers=admin_headers
    )
    assert res.status_code == 422

    # Title rỗng
    payload_empty_title = {
        "title": "   ",
    }
    res = client.post(
        "/api/admin/courses", json=payload_empty_title, headers=admin_headers
    )
    assert res.status_code == 422


def test_get_admin_courses_list_and_filter(client: TestClient, admin_headers):
    """GET /api/admin/courses: Lấy danh sách có phân trang và lọc theo search/level."""
    client.post(
        "/api/admin/courses",
        json={
            "title": "FastAPI Web Development",
            "level": "intermediate",
            "url": "https://course1.com",
        },
        headers=admin_headers,
    )
    client.post(
        "/api/admin/courses",
        json={
            "title": "Django Backend Mastery",
            "level": "advanced",
            "url": "https://course2.com",
        },
        headers=admin_headers,
    )
    client.post(
        "/api/admin/courses",
        json={
            "title": "React Frontend",
            "level": "beginner",
            "url": "https://course3.com",
        },
        headers=admin_headers,
    )

    # 1. Lấy tất cả phân trang
    res = client.get("/api/admin/courses?page=1&page_size=2", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] >= 3
    assert len(data["items"]) == 2

    # 2. Tìm kiếm theo keyword
    res = client.get("/api/admin/courses?search=FastAPI", headers=admin_headers)
    assert res.status_code == 200
    assert any("FastAPI" in c["title"] for c in res.json()["items"])

    # 3. Lọc theo level
    res = client.get("/api/admin/courses?level=advanced", headers=admin_headers)
    assert res.status_code == 200
    for c in res.json()["items"]:
        assert c["level"] == "advanced"


def test_get_admin_course_detail(client: TestClient, admin_headers):
    """GET /api/admin/courses/{course_id}: Lấy chi tiết khóa học kèm danh sách kỹ năng."""
    # Tạo course & skill
    res_c = client.post(
        "/api/admin/courses",
        json={"title": "Machine Learning", "url": "https://ml.com"},
        headers=admin_headers,
    )
    course_id = res_c.json()["course_id"]

    res_s = client.post(
        "/api/admin/skills",
        json={"skill": "Scikit-Learn"},
        headers=admin_headers,
    )
    skill_id = res_s.json()["skill_id"]

    # Gán quan hệ
    client.post(
        "/api/admin/course-skill-relations",
        json={"course_id": course_id, "skill_id": skill_id},
        headers=admin_headers,
    )

    # Lấy chi tiết
    res = client.get(f"/api/admin/courses/{course_id}", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["course_id"] == course_id
    assert len(data["skills"]) == 1
    assert data["skills"][0]["skill_id"] == skill_id
    assert data["skills"][0]["skill"] == "Scikit-Learn"


def test_get_admin_course_not_found(client: TestClient, admin_headers):
    """GET /api/admin/courses/{course_id}: 404 khi course_id không tồn tại."""
    res = client.get("/api/admin/courses/99999", headers=admin_headers)
    assert res.status_code == 404


def test_update_admin_course(client: TestClient, admin_headers):
    """PATCH /api/admin/courses/{course_id}: Cập nhật khóa học."""
    res = client.post(
        "/api/admin/courses",
        json={"title": "Old Title", "level": "beginner", "url": "https://old.com"},
        headers=admin_headers,
    )
    course_id = res.json()["course_id"]

    # Update title và level
    patch_res = client.patch(
        f"/api/admin/courses/{course_id}",
        json={"title": "New Title", "level": "intermediate"},
        headers=admin_headers,
    )
    assert patch_res.status_code == 200
    updated_data = patch_res.json()
    assert updated_data["title"] == "New Title"
    assert updated_data["level"] == "intermediate"


def test_delete_admin_course(client: TestClient, admin_headers):
    """DELETE /api/admin/courses/{course_id}: Xóa khóa học."""
    res = client.post(
        "/api/admin/courses",
        json={"title": "To Be Deleted", "url": "https://delete.com"},
        headers=admin_headers,
    )
    course_id = res.json()["course_id"]

    del_res = client.delete(f"/api/admin/courses/{course_id}", headers=admin_headers)
    assert del_res.status_code == 200

    # Kiểm tra lại phải là 404
    get_res = client.get(f"/api/admin/courses/{course_id}", headers=admin_headers)
    assert get_res.status_code == 404


# ==============================================================================
# 2. TEST SUITE: ADMIN SKILLS (/api/admin/skills)
# ==============================================================================


def test_create_admin_skill_success(client: TestClient, admin_headers):
    """POST /api/admin/skills: Tạo kỹ năng mới."""
    res = client.post(
        "/api/admin/skills",
        json={"skill": "Docker"},
        headers=admin_headers,
    )
    assert res.status_code == 201
    data = res.json()
    assert data["skill"] == "Docker"
    assert data["is_active"] is True
    assert "skill_id" in data


def test_create_admin_skill_duplicate(client: TestClient, admin_headers):
    """POST /api/admin/skills: Báo lỗi 409 khi kỹ năng bị trùng tên."""
    client.post(
        "/api/admin/skills",
        json={"skill": "Kubernetes"},
        headers=admin_headers,
    )
    res = client.post(
        "/api/admin/skills",
        json={"skill": "Kubernetes"},
        headers=admin_headers,
    )
    assert res.status_code == 409
    assert "đã tồn tại" in res.json()["detail"]


def test_get_admin_skills_list(client: TestClient, admin_headers):
    """GET /api/admin/skills: Lấy danh sách kỹ năng có phân trang & tìm kiếm."""
    client.post(
        "/api/admin/skills",
        json={"skill": "Golang Programming"},
        headers=admin_headers,
    )
    client.post(
        "/api/admin/skills",
        json={"skill": "Rust Programming"},
        headers=admin_headers,
    )

    res = client.get("/api/admin/skills?search=Golang", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert any("Golang" in item["skill"] for item in data["items"])


def test_update_admin_skill(client: TestClient, admin_headers):
    """PATCH /api/admin/skills/{skill_id}: Cập nhật tên hoặc is_active."""
    res = client.post(
        "/api/admin/skills",
        json={"skill": "VueJS"},
        headers=admin_headers,
    )
    skill_id = res.json()["skill_id"]

    patch_res = client.patch(
        f"/api/admin/skills/{skill_id}",
        json={"skill": "Vue.js 3", "is_active": False},
        headers=admin_headers,
    )
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["skill"] == "Vue.js 3"
    assert data["is_active"] is False


def test_delete_admin_skill_safe_deactivation(
    client: TestClient, db_session, admin_headers
):
    """DELETE /api/admin/skills/{skill_id}: Tự động soft-delete (is_active=False) nếu skill đang liên kết."""
    # 1. Tạo skill và gán vào course
    res_s = client.post(
        "/api/admin/skills",
        json={"skill": "SQLAlchemy"},
        headers=admin_headers,
    )
    skill_id = res_s.json()["skill_id"]

    res_c = client.post(
        "/api/admin/courses",
        json={"title": "Python Database", "url": "https://pydb.com"},
        headers=admin_headers,
    )
    course_id = res_c.json()["course_id"]

    client.post(
        "/api/admin/course-skill-relations",
        json={"course_id": course_id, "skill_id": skill_id},
        headers=admin_headers,
    )

    # 2. Xóa skill
    del_res = client.delete(f"/api/admin/skills/{skill_id}", headers=admin_headers)
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["action"] == "deactivated"

    # Kiểm tra trong DB skill vẫn còn nhưng is_active = False
    skill = db_session.get(Skills, skill_id)
    assert skill is not None
    assert skill.is_active is False


def test_delete_admin_skill_physical(client: TestClient, db_session, admin_headers):
    """DELETE /api/admin/skills/{skill_id}: Xóa vật lý khi skill chưa có liên kết nào."""
    res_s = client.post(
        "/api/admin/skills",
        json={"skill": "Unused Skill"},
        headers=admin_headers,
    )
    skill_id = res_s.json()["skill_id"]

    del_res = client.delete(f"/api/admin/skills/{skill_id}", headers=admin_headers)
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["action"] == "deleted"

    # Trong DB không còn bản ghi
    assert db_session.get(Skills, skill_id) is None


# ==============================================================================
# 3. TEST SUITE: COURSE-SKILL RELATIONS (/api/admin/course-skill-relations)
# ==============================================================================


def test_course_skill_relations_crud(client: TestClient, admin_headers):
    """Kiểm thử trọn vẹn luồng GET, POST, DELETE quan hệ Khóa học - Kỹ năng."""
    # Setup
    c_res = client.post(
        "/api/admin/courses",
        json={"title": "Git & GitHub Course", "url": "https://git.com"},
        headers=admin_headers,
    )
    course_id = c_res.json()["course_id"]

    s_res = client.post(
        "/api/admin/skills",
        json={"skill": "Git Version Control"},
        headers=admin_headers,
    )
    skill_id = s_res.json()["skill_id"]

    # 1. POST: Tạo liên kết
    create_res = client.post(
        "/api/admin/course-skill-relations",
        json={"course_id": course_id, "skill_id": skill_id},
        headers=admin_headers,
    )
    assert create_res.status_code == 201
    assert create_res.json()["course_id"] == course_id
    assert create_res.json()["skill_id"] == skill_id

    # 2. POST trùng: Báo lỗi 409
    dup_res = client.post(
        "/api/admin/course-skill-relations",
        json={"course_id": course_id, "skill_id": skill_id},
        headers=admin_headers,
    )
    assert dup_res.status_code == 409

    # 3. GET: Lấy danh sách liên kết
    list_res = client.get(
        f"/api/admin/course-skill-relations?course_id={course_id}",
        headers=admin_headers,
    )
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(
        r["course_id"] == course_id and r["skill_id"] == skill_id
        for r in list_data["items"]
    )
    assert list_data["items"][0]["course_title"] == "Git & GitHub Course"
    assert list_data["items"][0]["skill_name"] == "Git Version Control"

    # 4. DELETE: Xóa liên kết
    del_res = client.delete(
        f"/api/admin/course-skill-relations/{course_id}/{skill_id}",
        headers=admin_headers,
    )
    assert del_res.status_code == 200

    # 5. DELETE lại: Báo lỗi 404
    del_again_res = client.delete(
        f"/api/admin/course-skill-relations/{course_id}/{skill_id}",
        headers=admin_headers,
    )
    assert del_again_res.status_code == 404


# ==============================================================================
# 4. TEST SUITE: RBAC & ADMIN AUTHORIZATION (PHÂN QUYỀN ADMIN)
# ==============================================================================


def test_admin_endpoints_unauthorized_without_token(client: TestClient):
    """Mọi endpoint admin khi không gửi Authorization header đều bị chặn 401 Unauthorized."""
    # Courses
    assert client.get("/api/admin/courses").status_code == 401
    assert client.post("/api/admin/courses", json={"title": "Test"}).status_code == 401
    assert client.get("/api/admin/courses/1").status_code == 401
    assert (
        client.patch("/api/admin/courses/1", json={"title": "Test"}).status_code == 401
    )
    assert client.delete("/api/admin/courses/1").status_code == 401

    # Skills
    assert client.get("/api/admin/skills").status_code == 401
    assert client.post("/api/admin/skills", json={"skill": "Test"}).status_code == 401
    assert (
        client.patch("/api/admin/skills/1", json={"skill": "Test"}).status_code == 401
    )
    assert client.delete("/api/admin/skills/1").status_code == 401

    # Course-Skill Relations
    assert client.get("/api/admin/course-skill-relations").status_code == 401
    assert (
        client.post(
            "/api/admin/course-skill-relations", json={"course_id": 1, "skill_id": 1}
        ).status_code
        == 401
    )
    assert client.delete("/api/admin/course-skill-relations/1/1").status_code == 401


def test_admin_endpoints_forbidden_for_student(client: TestClient, student_headers):
    """Học viên thường (role='student') gọi vào bất kỳ endpoint admin nào đều bị chặn 403 Forbidden."""
    # 1. Courses
    res_get_courses = client.get("/api/admin/courses", headers=student_headers)
    assert res_get_courses.status_code == 403
    assert (
        res_get_courses.json()["detail"] == "Bạn không có quyền thực hiện thao tác này."
    )

    assert (
        client.post(
            "/api/admin/courses", json={"title": "Test"}, headers=student_headers
        ).status_code
        == 403
    )
    assert (
        client.get("/api/admin/courses/1", headers=student_headers).status_code == 403
    )
    assert (
        client.patch(
            "/api/admin/courses/1", json={"title": "Test"}, headers=student_headers
        ).status_code
        == 403
    )
    assert (
        client.delete("/api/admin/courses/1", headers=student_headers).status_code
        == 403
    )

    # 2. Skills
    res_get_skills = client.get("/api/admin/skills", headers=student_headers)
    assert res_get_skills.status_code == 403
    assert (
        res_get_skills.json()["detail"] == "Bạn không có quyền thực hiện thao tác này."
    )

    assert (
        client.post(
            "/api/admin/skills", json={"skill": "Test"}, headers=student_headers
        ).status_code
        == 403
    )
    assert (
        client.patch(
            "/api/admin/skills/1", json={"skill": "Test"}, headers=student_headers
        ).status_code
        == 403
    )
    assert (
        client.delete("/api/admin/skills/1", headers=student_headers).status_code == 403
    )

    # 3. Course-Skill Relations
    res_get_relations = client.get(
        "/api/admin/course-skill-relations", headers=student_headers
    )
    assert res_get_relations.status_code == 403
    assert (
        res_get_relations.json()["detail"]
        == "Bạn không có quyền thực hiện thao tác này."
    )

    assert (
        client.post(
            "/api/admin/course-skill-relations",
            json={"course_id": 1, "skill_id": 1},
            headers=student_headers,
        ).status_code
        == 403
    )
    assert (
        client.delete(
            "/api/admin/course-skill-relations/1/1", headers=student_headers
        ).status_code
        == 403
    )


def test_admin_endpoints_invalid_token(client: TestClient):
    """Gửi Bearer token sai hoặc rác đều trả về 401 Unauthorized."""
    fake_headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
    }
    res = client.get("/api/admin/courses", headers=fake_headers)
    assert res.status_code == 401
    assert res.json()["detail"] == "Phiên đăng nhập không hợp lệ hoặc đã hết hạn."
