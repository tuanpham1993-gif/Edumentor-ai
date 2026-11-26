import pytest

from app.core.security import create_access_token, hash_password
from app.models.learning_path import LearningPath, LearningPathEdge, LearningPathNode
from app.models.skill import Skills
from app.models.user import Users
from app.models.user_skill import UserSkill


@pytest.fixture
def admin_user_paths_dataset(db_session):
    """Tạo dataset thử nghiệm gồm admin, 2 học viên, 1 lộ trình mồ côi và user_skills."""
    admin = Users(
        email="admin_test@edumentor.vn",
        full_name="Quan Tri Vien",
        hashed_password=hash_password("Admin@1234"),
        role="admin",
        is_active=True,
    )
    student1 = Users(
        email="student1@edumentor.vn",
        full_name="Nguyen Van A",
        hashed_password=hash_password("Pass@1234"),
        role="student",
        is_active=True,
    )
    student2 = Users(
        email="student2@edumentor.vn",
        full_name="Tran Thi B",
        hashed_password=hash_password("Pass@1234"),
        role="student",
        is_active=True,
    )
    db_session.add_all([admin, student1, student2])
    db_session.flush()

    skill_py = Skills(skill_id=9001, skill="Python", is_active=True)
    skill_sql = Skills(skill_id=9002, skill="SQL", is_active=True)
    skill_fastapi = Skills(skill_id=9003, skill="FastAPI", is_active=True)
    db_session.add_all([skill_py, skill_sql, skill_fastapi])
    db_session.flush()

    # Lộ trình 1 của student1 (ongoing, shared)
    path1 = LearningPath(
        student_id=student1.user_id,
        original_query="Backend Python Developer",
        goal_type="career",
        status="ongoing",
        is_shared=True,
        share_code="SHARE_PY_1",
        clone_count=1,
    )
    # Lộ trình 2 của student1 (completed)
    path2 = LearningPath(
        student_id=student1.user_id,
        original_query="SQL Mastery",
        goal_type="project",
        status="completed",
    )
    # Lộ trình của student2 (cùng mục tiêu Backend Python Developer)
    path3 = LearningPath(
        student_id=student2.user_id,
        original_query="  backend python developer ",
        goal_type="career",
        status="abandoned",
    )
    # Lộ trình mồ côi (student_id không có trong bảng users) -> phải bị bỏ qua khi tổng hợp
    orphan_path = LearningPath(
        student_id=999999,
        original_query="Orphan Synthetic Path",
        goal_type="career",
        status="ongoing",
    )
    db_session.add_all([path1, path2, path3, orphan_path])
    db_session.flush()

    # Nodes & edges cho path1
    db_session.add_all([
        LearningPathNode(
            path_id=path1.record_id,
            skill_id=skill_py.skill_id,
            node_role="prerequisite",
            is_target=False,
            added_by="system",
            is_required=True,
            display_order=1000,
        ),
        LearningPathNode(
            path_id=path1.record_id,
            skill_id=skill_sql.skill_id,
            node_role="prerequisite",
            is_target=False,
            added_by="system",
            is_required=True,
            display_order=2000,
        ),
        LearningPathNode(
            path_id=path1.record_id,
            skill_id=skill_fastapi.skill_id,
            node_role="extension",
            is_target=True,
            added_by="system",
            is_required=True,
            display_order=3000,
        ),
        LearningPathEdge(
            path_id=path1.record_id,
            from_skill_id=skill_py.skill_id,
            to_skill_id=skill_fastapi.skill_id,
            relation_type="prerequisite",
        ),
    ])

    # Kỹ năng của student1: Python=known, FastAPI=learning, SQL chưa học
    db_session.add_all([
        UserSkill(user_id=student1.user_id, skill_id=skill_py.skill_id, status="known", source="review"),
        UserSkill(user_id=student1.user_id, skill_id=skill_fastapi.skill_id, status="learning", source="course"),
    ])
    db_session.commit()

    return {
        "admin": admin,
        "student1": student1,
        "student2": student2,
        "admin_token": create_access_token(admin.user_id),
        "student_token": create_access_token(student1.user_id),
        "path1": path1,
    }


def test_admin_user_paths_requires_admin(client, admin_user_paths_dataset):
    # Guest -> 401
    res_guest = client.get("/api/admin/user-paths/overview")
    assert res_guest.status_code == 401

    # Student -> 403
    student_headers = {"Authorization": f"Bearer {admin_user_paths_dataset['student_token']}"}
    res_student = client.get("/api/admin/user-paths/overview", headers=student_headers)
    assert res_student.status_code == 403


def test_admin_user_paths_overview(client, admin_user_paths_dataset):
    headers = {"Authorization": f"Bearer {admin_user_paths_dataset['admin_token']}"}
    res = client.get("/api/admin/user-paths/overview", headers=headers)
    assert res.status_code == 200
    body = res.json()

    stats = body["stats"]
    assert stats["total_users"] == 3
    assert stats["users_with_paths"] == 2
    # Chỉ tính 3 lộ trình thuộc user thật (bỏ qua orphan_path)
    assert stats["total_paths"] == 3
    assert stats["ongoing_paths"] == 1
    assert stats["completed_paths"] == 1
    assert stats["abandoned_paths"] == 1
    assert stats["shared_paths"] == 1

    goals = body["popular_goals"]
    assert len(goals) == 2
    assert goals[0]["user_count"] == 2
    assert goals[0]["path_count"] == 2
    assert "backend python developer" in goals[0]["title"].lower()


def test_admin_user_paths_list_users_and_filters(client, admin_user_paths_dataset):
    headers = {"Authorization": f"Bearer {admin_user_paths_dataset['admin_token']}"}

    # 1. Lấy toàn bộ
    res = client.get("/api/admin/user-paths/users", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    # Student1 đứng đầu (2 paths)
    first = data["items"][0]
    assert first["email"] == "student1@edumentor.vn"
    assert first["total_paths"] == 2
    assert first["ongoing_paths"] == 1
    assert first["completed_paths"] == 1
    assert first["shared_paths"] == 1
    assert first["known_skills_count"] == 1
    assert first["learning_skills_count"] == 1

    # 2. Tìm theo email
    res_search = client.get("/api/admin/user-paths/users?search=student2&search_by=user", headers=headers)
    assert res_search.status_code == 200
    assert res_search.json()["total"] == 1
    assert res_search.json()["items"][0]["email"] == "student2@edumentor.vn"

    # 3. Tìm theo mục tiêu
    res_goal_search = client.get("/api/admin/user-paths/users?search=SQL&search_by=goal", headers=headers)
    assert res_goal_search.status_code == 200
    assert res_goal_search.json()["total"] == 1
    assert res_goal_search.json()["items"][0]["email"] == "student1@edumentor.vn"

    # 4. Lọc theo chip popular goal
    res_chip = client.get(
        "/api/admin/user-paths/users",
        params={"goal": "Backend Python Developer"},
        headers=headers,
    )
    assert res_chip.status_code == 200
    assert res_chip.json()["total"] == 2


def test_admin_user_paths_detail(client, admin_user_paths_dataset):
    headers = {"Authorization": f"Bearer {admin_user_paths_dataset['admin_token']}"}
    student1_id = admin_user_paths_dataset["student1"].user_id

    res = client.get(f"/api/admin/user-paths/users/{student1_id}", headers=headers)
    assert res.status_code == 200
    detail = res.json()

    assert detail["user"]["email"] == "student1@edumentor.vn"
    assert detail["status_counts"] == {"all": 2, "ongoing": 1, "completed": 1, "abandoned": 0}
    assert len(detail["paths"]) == 2

    # path2 record_id lớn hơn nên nằm trước, lấy path1 theo original_query
    path1_dto = next(p for p in detail["paths"] if p["original_query"] == "Backend Python Developer")
    assert path1_dto["progress_known"] == 1
    assert path1_dto["progress_learning"] == 1
    assert path1_dto["progress_total"] == 3
    assert path1_dto["target_skills"] == ["FastAPI"]

    node_status_by_name = {n["skill_name"]: n["user_skill_status"] for n in path1_dto["nodes"]}
    assert node_status_by_name == {
        "Python": "known",
        "SQL": "unlearned",
        "FastAPI": "learning",
    }

    # Non-existent user -> 404
    res_404 = client.get("/api/admin/user-paths/users/888888", headers=headers)
    assert res_404.status_code == 404
