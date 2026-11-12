
def test_get_learning_path_node_detail_success(client, sample_learning_path):
    path_id = sample_learning_path["path_id"]
    skill_id = sample_learning_path["python_skill_id"]
    fastapi_skill_id = sample_learning_path["fastapi_skill_id"]

    response = client.get(f"/api/learning-paths-nodes/{path_id}/nodes/{skill_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["path_id"] == path_id
    assert data["skill_id"] == skill_id
    assert data["node_role"] == "prerequisite"
    assert data["is_target"] is False

    # Check the nested skill relationship.
    assert data["skill"]["skill_id"] == skill_id
    assert data["skill"]["skill"] == "Python"
    print(data)

    response = client.get(f"/api/learning-paths-nodes/{path_id}/nodes/{fastapi_skill_id}")
    data = response.json()
    assert data["path_id"] == path_id
    assert data["skill_id"] == fastapi_skill_id
    assert data["node_role"] == "prerequisite"
    assert data["is_target"] is False
    print("================================")
    # Check the nested skill relationship.
    assert data["skill"]["skill_id"] == fastapi_skill_id
    assert data["skill"]["skill"] == "FastAPI"
    print(data)

def test_get_learning_path_node_detail_not_found(client, sample_learning_path):
    path_id = sample_learning_path["path_id"]
    nonexistent_skill_id = 999
    response = client.get(f"/api/learning-paths-nodes/{path_id}/nodes/{nonexistent_skill_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Learning path node not found."
