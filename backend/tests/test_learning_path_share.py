import pytest

from app.core.security import create_access_token, hash_password
from app.models.learning_path import LearningPath, LearningPathEdge, LearningPathNode
from app.models.skill import Skills
from app.models.user import Users


@pytest.fixture
def two_students_with_path(db_session):
    """Tạo 2 học viên và 1 lộ trình học tập thuộc học viên 1."""
    # 1. Tạo 2 học viên
    user1 = Users(
        email="owner@edumentor.vn",
        full_name="Le Van Owner",
        hashed_password=hash_password("Pass@1234"),
        role="student",
        is_active=True,
    )
    user2 = Users(
        email="cloner@edumentor.vn",
        full_name="Tran Thi Cloner",
        hashed_password=hash_password("Pass@1234"),
        role="student",
        is_active=True,
    )
    db_session.add_all([user1, user2])
    db_session.flush()

    token1 = create_access_token(user1.user_id)
    token2 = create_access_token(user2.user_id)

    # 2. Tạo kỹ năng
    skill1 = Skills(skill_id=201, skill="ReactJS", is_active=True)
    skill2 = Skills(skill_id=202, skill="Redux Toolkit", is_active=True)
    db_session.add_all([skill1, skill2])
    db_session.flush()

    # 3. Tạo lộ trình cho user1
    path = LearningPath(
        student_id=user1.user_id,
        original_query="Học Frontend React Chuyên Sâu",
        goal_type="career",
        status="ongoing",
    )
    db_session.add(path)
    db_session.flush()

    # 4. Thêm node & edge
    node1 = LearningPathNode(
        path_id=path.record_id,
        skill_id=skill1.skill_id,
        node_role="prerequisite",
        is_target=False,
        added_by="system",
        is_required=True,
        display_order=1,
    )
    node2 = LearningPathNode(
        path_id=path.record_id,
        skill_id=skill2.skill_id,
        node_role="extension",
        is_target=True,
        added_by="system",
        is_required=True,
        display_order=2,
    )
    edge = LearningPathEdge(
        path_id=path.record_id,
        from_skill_id=skill1.skill_id,
        to_skill_id=skill2.skill_id,
        relation_type="prerequisite",
    )
    db_session.add_all([node1, node2, edge])
    db_session.commit()

    return {
        "user1": user1,
        "user2": user2,
        "token1": token1,
        "token2": token2,
        "path": path,
        "skill1": skill1,
        "skill2": skill2,
    }


def test_enable_and_disable_share(client, two_students_with_path):
    data = two_students_with_path
    path_id = data["path"].record_id
    headers1 = {"Authorization": f"Bearer {data['token1']}"}
    headers2 = {"Authorization": f"Bearer {data['token2']}"}

    # User 2 không thể bật share lộ trình của User 1
    res = client.post(f"/api/learning-paths/{path_id}/share", headers=headers2)
    assert res.status_code == 400

    # User 1 bật share thành công
    res = client.post(f"/api/learning-paths/{path_id}/share", headers=headers1)
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["is_shared"] is True
    assert res_data["share_code"] is not None
    assert "/shared/learning-paths/" in res_data["share_url"]

    # User 1 tắt share
    res_del = client.delete(f"/api/learning-paths/{path_id}/share", headers=headers1)
    assert res_del.status_code == 200
    assert res_del.json()["is_shared"] is False


def test_view_shared_path(client, two_students_with_path):
    data = two_students_with_path
    path_id = data["path"].record_id
    headers1 = {"Authorization": f"Bearer {data['token1']}"}
    headers2 = {"Authorization": f"Bearer {data['token2']}"}

    # Bật share
    share_res = client.post(f"/api/learning-paths/{path_id}/share", headers=headers1)
    share_code = share_res.json()["share_code"]

    # 1. Khách vãng lai (không token) xem lộ trình
    res_guest = client.get(f"/api/learning-paths/shared/{share_code}")
    assert res_guest.status_code == 200
    guest_data = res_guest.json()
    assert guest_data["original_query"] == "Học Frontend React Chuyên Sâu"
    assert guest_data["is_owner"] is False
    assert guest_data["author"]["full_name"] == "Le Van Owner"
    assert len(guest_data["nodes"]) == 2
    assert len(guest_data["edges"]) == 1

    # 2. Học viên khác (User 2) xem lộ trình
    res_user2 = client.get(f"/api/learning-paths/shared/{share_code}", headers=headers2)
    assert res_user2.status_code == 200
    assert res_user2.json()["is_owner"] is False

    # 3. Chính chủ sở hữu (User 1) xem lộ trình
    res_owner = client.get(f"/api/learning-paths/shared/{share_code}", headers=headers1)
    assert res_owner.status_code == 200
    assert res_owner.json()["is_owner"] is True


def test_clone_shared_path_success(client, two_students_with_path):
    data = two_students_with_path
    path_id = data["path"].record_id
    headers1 = {"Authorization": f"Bearer {data['token1']}"}
    headers2 = {"Authorization": f"Bearer {data['token2']}"}

    # Bật share
    share_res = client.post(f"/api/learning-paths/{path_id}/share", headers=headers1)
    share_code = share_res.json()["share_code"]

    # User 2 clone lộ trình của User 1
    clone_res = client.post(f"/api/learning-paths/shared/{share_code}/clone", headers=headers2)
    assert clone_res.status_code == 201
    clone_data = clone_res.json()
    assert "Đã sao chép lộ trình thành công" in clone_data["message"]
    new_path = clone_data["learning_path"]
    assert new_path["student_id"] == data["user2"].user_id
    assert new_path["original_query"] == data["path"].original_query
    assert new_path["cloned_from_id"] == path_id
    assert len(new_path["nodes"]) == 2
    assert len(new_path["edges"]) == 1

    # Kiểm tra clone_count của lộ trình gốc tăng lên 1
    check_orig = client.get(f"/api/learning-paths/shared/{share_code}")
    assert check_orig.json()["clone_count"] == 1


def test_prevent_self_cloning(client, two_students_with_path):
    """Ràng buộc an toàn: Không cho phép tự clone lộ trình của chính mình."""
    data = two_students_with_path
    path_id = data["path"].record_id
    headers1 = {"Authorization": f"Bearer {data['token1']}"}

    # Bật share
    share_res = client.post(f"/api/learning-paths/{path_id}/share", headers=headers1)
    share_code = share_res.json()["share_code"]

    # Chính User 1 cố gắng clone lộ trình của mình -> Bị từ chối kèm thông báo rõ ràng
    self_clone_res = client.post(f"/api/learning-paths/shared/{share_code}/clone", headers=headers1)
    assert self_clone_res.status_code == 400
    assert "Đây là lộ trình của bạn" in self_clone_res.json()["detail"]
