import pytest
from fastapi.testclient import TestClient
from app.models.course import Courses
from app.models.skill import Skills
from app.models.course_skill import CourseSkill


# ==============================================================================
# 1. TEST SUITE: ADMIN COURSES (/api/admin/courses)
# ==============================================================================

def test_create_admin_course_success(client: TestClient):
    """POST /api/admin/courses: Thêm mới khóa học thành công."""
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
        "image": "https://coursera.org/image.png"
    }
    response = client.post("/api/admin/courses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["level"] == "beginner"
    assert data["rating"] == 4.8
    assert "course_id" in data


def test_create_admin_course_duplicate_url(client: TestClient):
    """POST /api/admin/courses: Báo lỗi 409 Conflict khi URL đã tồn tại."""
    payload = {
        "title": "Unique Course",
        "url": "https://coursera.org/learn/unique-url"
    }
    res1 = client.post("/api/admin/courses", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/admin/courses", json=payload)
    assert res2.status_code == 409
    assert "đã tồn tại" in res2.json()["detail"]


def test_create_admin_course_invalid_data(client: TestClient):
    """POST /api/admin/courses: Báo lỗi 422 khi dữ liệu không hợp lệ (ví dụ rating > 5 hoặc title rỗng)."""
    # Rating vượt quá 5.0
    payload_invalid_rating = {
        "title": "Bad Rating Course",
        "rating": 6.5
    }
    res = client.post("/api/admin/courses", json=payload_invalid_rating)
    assert res.status_code == 422

    # Title rỗng
    payload_empty_title = {
        "title": "   "
    }
    res = client.post("/api/admin/courses", json=payload_empty_title)
    assert res.status_code == 422


def test_get_admin_courses_list_and_filter(client: TestClient):
    """GET /api/admin/courses: Lấy danh sách có phân trang và lọc theo search/level."""
    client.post("/api/admin/courses", json={"title": "FastAPI Web Development", "level": "intermediate", "url": "https://course1.com"})
    client.post("/api/admin/courses", json={"title": "Django Backend Mastery", "level": "advanced", "url": "https://course2.com"})
    client.post("/api/admin/courses", json={"title": "React Frontend", "level": "beginner", "url": "https://course3.com"})

    # 1. Lấy tất cả phân trang
    res = client.get("/api/admin/courses?page=1&page_size=2")
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] >= 3
    assert len(data["items"]) == 2

    # 2. Tìm kiếm theo keyword
    res = client.get("/api/admin/courses?search=FastAPI")
    assert res.status_code == 200
    assert any("FastAPI" in c["title"] for c in res.json()["items"])

    # 3. Lọc theo level
    res = client.get("/api/admin/courses?level=advanced")
    assert res.status_code == 200
    for c in res.json()["items"]:
        assert c["level"] == "advanced"


def test_get_admin_course_detail(client: TestClient, db_session):
    """GET /api/admin/courses/{course_id}: Lấy chi tiết khóa học kèm danh sách kỹ năng."""
    # Tạo course & skill
    res_c = client.post("/api/admin/courses", json={"title": "Machine Learning", "url": "https://ml.com"})
    course_id = res_c.json()["course_id"]

    res_s = client.post("/api/admin/skills", json={"skill": "Scikit-Learn"})
    skill_id = res_s.json()["skill_id"]

    # Gán quan hệ
    client.post("/api/admin/course-skill-relations", json={"course_id": course_id, "skill_id": skill_id})

    # Lấy chi tiết
    res = client.get(f"/api/admin/courses/{course_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["course_id"] == course_id
    assert len(data["skills"]) == 1
    assert data["skills"][0]["skill_id"] == skill_id
    assert data["skills"][0]["skill"] == "Scikit-Learn"


def test_get_admin_course_not_found(client: TestClient):
    """GET /api/admin/courses/{course_id}: 404 khi course_id không tồn tại."""
    res = client.get("/api/admin/courses/99999")
    assert res.status_code == 404


def test_update_admin_course(client: TestClient):
    """PATCH /api/admin/courses/{course_id}: Cập nhật khóa học."""
    res = client.post("/api/admin/courses", json={"title": "Old Title", "level": "beginner", "url": "https://old.com"})
    course_id = res.json()["course_id"]

    # Update title và level
    patch_res = client.patch(f"/api/admin/courses/{course_id}", json={"title": "New Title", "level": "intermediate"})
    assert patch_res.status_code == 200
    updated_data = patch_res.json()
    assert updated_data["title"] == "New Title"
    assert updated_data["level"] == "intermediate"


def test_delete_admin_course(client: TestClient):
    """DELETE /api/admin/courses/{course_id}: Xóa khóa học."""
    res = client.post("/api/admin/courses", json={"title": "To Be Deleted", "url": "https://delete.com"})
    course_id = res.json()["course_id"]

    del_res = client.delete(f"/api/admin/courses/{course_id}")
    assert del_res.status_code == 200

    # Kiểm tra lại phải là 404
    get_res = client.get(f"/api/admin/courses/{course_id}")
    assert get_res.status_code == 404


# ==============================================================================
# 2. TEST SUITE: ADMIN SKILLS (/api/admin/skills)
# ==============================================================================

def test_create_admin_skill_success(client: TestClient):
    """POST /api/admin/skills: Tạo kỹ năng mới."""
    res = client.post("/api/admin/skills", json={"skill": "Docker"})
    assert res.status_code == 201
    data = res.json()
    assert data["skill"] == "Docker"
    assert data["is_active"] is True
    assert "skill_id" in data


def test_create_admin_skill_duplicate(client: TestClient):
    """POST /api/admin/skills: Báo lỗi 409 khi kỹ năng bị trùng tên."""
    client.post("/api/admin/skills", json={"skill": "Kubernetes"})
    res = client.post("/api/admin/skills", json={"skill": "Kubernetes"})
    assert res.status_code == 409
    assert "đã tồn tại" in res.json()["detail"]


def test_get_admin_skills_list(client: TestClient):
    """GET /api/admin/skills: Lấy danh sách kỹ năng có phân trang & tìm kiếm."""
    client.post("/api/admin/skills", json={"skill": "Golang Programming"})
    client.post("/api/admin/skills", json={"skill": "Rust Programming"})

    res = client.get("/api/admin/skills?search=Golang")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert any("Golang" in item["skill"] for item in data["items"])


def test_update_admin_skill(client: TestClient):
    """PATCH /api/admin/skills/{skill_id}: Cập nhật tên hoặc is_active."""
    res = client.post("/api/admin/skills", json={"skill": "VueJS"})
    skill_id = res.json()["skill_id"]

    patch_res = client.patch(f"/api/admin/skills/{skill_id}", json={"skill": "Vue.js 3", "is_active": False})
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["skill"] == "Vue.js 3"
    assert data["is_active"] is False


def test_delete_admin_skill_safe_deactivation(client: TestClient, db_session):
    """DELETE /api/admin/skills/{skill_id}: Tự động soft-delete (is_active=False) nếu skill đang liên kết."""
    # 1. Tạo skill và gán vào course
    res_s = client.post("/api/admin/skills", json={"skill": "SQLAlchemy"})
    skill_id = res_s.json()["skill_id"]

    res_c = client.post("/api/admin/courses", json={"title": "Python Database", "url": "https://pydb.com"})
    course_id = res_c.json()["course_id"]

    client.post("/api/admin/course-skill-relations", json={"course_id": course_id, "skill_id": skill_id})

    # 2. Xóa skill
    del_res = client.delete(f"/api/admin/skills/{skill_id}")
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["action"] == "deactivated"

    # Kiểm tra trong DB skill vẫn còn nhưng is_active = False
    skill = db_session.get(Skills, skill_id)
    assert skill is not None
    assert skill.is_active is False


def test_delete_admin_skill_physical(client: TestClient, db_session):
    """DELETE /api/admin/skills/{skill_id}: Xóa vật lý khi skill chưa có liên kết nào."""
    res_s = client.post("/api/admin/skills", json={"skill": "Unused Skill"})
    skill_id = res_s.json()["skill_id"]

    del_res = client.delete(f"/api/admin/skills/{skill_id}")
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["action"] == "deleted"

    # Trong DB không còn bản ghi
    assert db_session.get(Skills, skill_id) is None


# ==============================================================================
# 3. TEST SUITE: COURSE-SKILL RELATIONS (/api/admin/course-skill-relations)
# ==============================================================================

def test_course_skill_relations_crud(client: TestClient):
    """Kiểm thử trọn vẹn luồng GET, POST, DELETE quan hệ Khóa học - Kỹ năng."""
    # Setup
    c_res = client.post("/api/admin/courses", json={"title": "Git & GitHub Course", "url": "https://git.com"})
    course_id = c_res.json()["course_id"]

    s_res = client.post("/api/admin/skills", json={"skill": "Git Version Control"})
    skill_id = s_res.json()["skill_id"]

    # 1. POST: Tạo liên kết
    create_res = client.post("/api/admin/course-skill-relations", json={"course_id": course_id, "skill_id": skill_id})
    assert create_res.status_code == 201
    assert create_res.json()["course_id"] == course_id
    assert create_res.json()["skill_id"] == skill_id

    # 2. POST trùng: Báo lỗi 409
    dup_res = client.post("/api/admin/course-skill-relations", json={"course_id": course_id, "skill_id": skill_id})
    assert dup_res.status_code == 409

    # 3. GET: Lấy danh sách liên kết
    list_res = client.get(f"/api/admin/course-skill-relations?course_id={course_id}")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(r["course_id"] == course_id and r["skill_id"] == skill_id for r in list_data["items"])
    assert list_data["items"][0]["course_title"] == "Git & GitHub Course"
    assert list_data["items"][0]["skill_name"] == "Git Version Control"

    # 4. DELETE: Xóa liên kết
    del_res = client.delete(f"/api/admin/course-skill-relations/{course_id}/{skill_id}")
    assert del_res.status_code == 200

    # 5. DELETE lại: Báo lỗi 404
    del_again_res = client.delete(f"/api/admin/course-skill-relations/{course_id}/{skill_id}")
    assert del_again_res.status_code == 404

