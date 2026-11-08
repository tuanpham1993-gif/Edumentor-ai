"""Test GET + PATCH /api/me/skills (module 01 · Tuấn · GĐ4 bước 4.2–4.4, 08/11/2026).

Chạy:  python -m pytest tests/test_me_skills.py -v      (trong thư mục backend)

Dữ liệu ban đầu được thêm THẲNG vào DB test qua `db_session` (hàm give), rồi gọi API.
Test PATCH quan trọng nhất: có 1 lỗi → KHÔNG lưu gì (hồ sơ y nguyên như trước).
"""

import pytest

from app.models.skill import Skills
from app.models.user_skill import UserSkill

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
ME_URL = "/api/me"
SKILLS_URL = "/api/me/skills"
PASSWORD = "Abc@1234"


def register_and_login(client, email, full_name="Người Thử"):
    """Đăng ký + đăng nhập, trả về (headers có token, user_id)."""
    client.post(
        REGISTER_URL,
        json={
            "full_name": full_name,
            "email": email,
            "password": PASSWORD,
            "confirm_password": PASSWORD,
        },
    )
    token = client.post(LOGIN_URL, json={"email": email, "password": PASSWORD}).json()[
        "access_token"
    ]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = client.get(ME_URL, headers=headers).json()["user_id"]
    return headers, user_id


@pytest.fixture()
def skills(db_session):
    """3 kỹ năng trong danh mục (bảng skills của Hòa)."""
    rows = [
        Skills(skill_id=1, skill="SQL", is_active=True),
        Skills(skill_id=2, skill="Python Programming", is_active=True),
        Skills(skill_id=3, skill="Docker", is_active=True),
        Skills(skill_id=4, skill="Kỹ năng đã ẩn", is_active=False),
    ]
    db_session.add_all(rows)
    db_session.commit()
    return rows


def give(db_session, user_id, skill_id, status, source=None):
    """Thêm một kỹ năng vào hồ sơ (thay cho PATCH chưa có)."""
    row = UserSkill(user_id=user_id, skill_id=skill_id, status=status)
    if source:
        row.source = source
    db_session.add(row)
    db_session.commit()


def test_skills_without_token_returns_401(client):
    assert client.get(SKILLS_URL).status_code == 401


def test_skills_empty_profile_returns_empty_list(client, skills):
    headers, _ = register_and_login(client, "a@gmail.com")
    response = client.get(SKILLS_URL, headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_skills_returns_names_sorted_with_default_source(client, db_session, skills):
    headers, user_id = register_and_login(client, "a@gmail.com")
    give(db_session, user_id, 1, "known")  # SQL
    give(db_session, user_id, 2, "learning")  # Python Programming

    data = client.get(SKILLS_URL, headers=headers).json()

    # sắp theo tên: "Python Programming" < "SQL"
    assert [s["skill"] for s in data] == ["Python Programming", "SQL"]
    assert data[0] == {
        "skill_id": 2,
        "skill": "Python Programming",
        "status": "learning",
        "source": "manual",  # S5: mặc định
        "updated_at": data[0]["updated_at"],
    }
    assert data[0]["updated_at"]  # DB tự điền


def test_skills_filter_by_status(client, db_session, skills):
    headers, user_id = register_and_login(client, "a@gmail.com")
    give(db_session, user_id, 1, "known")
    give(db_session, user_id, 2, "learning")
    give(db_session, user_id, 3, "known", source="review")

    known = client.get(SKILLS_URL, params={"status": "known"}, headers=headers).json()
    learning = client.get(
        SKILLS_URL, params={"status": "learning"}, headers=headers
    ).json()

    assert [s["skill"] for s in known] == ["Docker", "SQL"]
    assert all(s["status"] == "known" for s in known)
    assert [s["skill"] for s in learning] == ["Python Programming"]
    assert known[0]["source"] == "review"


def test_skills_invalid_status_returns_422(client, skills):
    headers, _ = register_and_login(client, "a@gmail.com")
    response = client.get(SKILLS_URL, params={"status": "expert"}, headers=headers)
    assert response.status_code == 422


def test_skills_only_own_profile(client, db_session, skills):
    """NFR-06: người A không thấy kỹ năng của người B."""
    headers_a, user_a = register_and_login(client, "a@gmail.com")
    headers_b, user_b = register_and_login(client, "b@gmail.com")
    give(db_session, user_a, 1, "known")
    give(db_session, user_b, 2, "learning")

    data_a = client.get(SKILLS_URL, headers=headers_a).json()
    data_b = client.get(SKILLS_URL, headers=headers_b).json()

    assert [s["skill_id"] for s in data_a] == [1]
    assert [s["skill_id"] for s in data_b] == [2]


# ─────────────── PATCH /api/me/skills (4.3) ───────────────


def snapshot(client, headers):
    """Hồ sơ hiện tại dạng {skill_id: (status, source)} — so trước/sau khi lưu."""
    return {
        s["skill_id"]: (s["status"], s["source"])
        for s in client.get(SKILLS_URL, headers=headers).json()
    }


def patch(client, headers, **body):
    return client.patch(SKILLS_URL, json=body, headers=headers)


def test_patch_without_token_returns_401(client):
    assert client.patch(SKILLS_URL, json={"remove": [1]}).status_code == 401


def test_patch_add_returns_updated_list(client, skills):
    headers, _ = register_and_login(client, "a@gmail.com")
    response = patch(
        client,
        headers,
        add=[{"skill_id": 1, "status": "known"}, {"skill_id": 2, "status": "learning"}],
    )
    assert response.status_code == 200
    # trả về danh sách SAU khi lưu, sắp theo tên, nguồn "manual"
    assert [(s["skill"], s["status"], s["source"]) for s in response.json()] == [
        ("Python Programming", "learning", "manual"),
        ("SQL", "known", "manual"),
    ]


def test_patch_add_update_remove_in_one_save(client, db_session, skills):
    headers, user_id = register_and_login(client, "a@gmail.com")
    give(db_session, user_id, 1, "learning")
    give(db_session, user_id, 2, "known")

    response = patch(
        client,
        headers,
        add=[{"skill_id": 3, "status": "learning"}],
        update=[{"skill_id": 1, "status": "known"}],
        remove=[2],
    )
    assert response.status_code == 200
    assert snapshot(client, headers) == {
        1: ("known", "manual"),
        3: ("learning", "manual"),
    }


def test_patch_user_can_change_and_remove_review_skills(client, db_session, skills):
    """S6 (thầy, 08/11): người dùng được đổi / gỡ cả kỹ năng đạt qua bài ôn tập."""
    headers, user_id = register_and_login(client, "a@gmail.com")
    give(db_session, user_id, 1, "known", source="review")
    give(db_session, user_id, 2, "known", source="review")

    response = patch(
        client, headers, update=[{"skill_id": 1, "status": "learning"}], remove=[2]
    )
    assert response.status_code == 200
    # đổi trạng thái → nguồn chuyển "manual" (người dùng tự chọn)
    assert snapshot(client, headers) == {1: ("learning", "manual")}


def test_patch_update_same_status_keeps_source(client, db_session, skills):
    headers, user_id = register_and_login(client, "a@gmail.com")
    give(db_session, user_id, 1, "known", source="review")
    patch(client, headers, update=[{"skill_id": 1, "status": "known"}])
    assert snapshot(client, headers) == {1: ("known", "review")}


@pytest.mark.parametrize(
    "body",
    [
        {},  # không có thay đổi nào
        {"add": [], "update": [], "remove": []},
        {"add": [{"skill_id": 1, "status": "expert"}]},  # status sai
        {"add": [{"skill_id": 1, "status": "known"}], "remove": [1]},  # 1 kỹ năng 2 lần
        {"remove": [0]},  # id không hợp lệ
    ],
)
def test_patch_invalid_body_returns_422(client, skills, body):
    headers, _ = register_and_login(client, "a@gmail.com")
    assert client.patch(SKILLS_URL, json=body, headers=headers).status_code == 422


def test_patch_add_unknown_or_hidden_skill_returns_422(client, skills):
    """S4: không có trong danh mục (999) hoặc đã ẩn (4) → 422."""
    headers, _ = register_and_login(client, "a@gmail.com")
    for skill_id in (999, 4):
        response = patch(
            client, headers, add=[{"skill_id": skill_id, "status": "known"}]
        )
        assert response.status_code == 422
        assert str(skill_id) in response.json()["detail"]


def test_patch_add_existing_returns_409(client, db_session, skills):
    """S2."""
    headers, user_id = register_and_login(client, "a@gmail.com")
    give(db_session, user_id, 1, "known")
    response = patch(client, headers, add=[{"skill_id": 1, "status": "learning"}])
    assert response.status_code == 409


def test_patch_update_or_remove_missing_returns_404(client, skills):
    """S3."""
    headers, _ = register_and_login(client, "a@gmail.com")
    assert (
        patch(client, headers, update=[{"skill_id": 1, "status": "known"}]).status_code
        == 404
    )
    assert patch(client, headers, remove=[2]).status_code == 404


@pytest.mark.parametrize(
    "bad_part, expected",
    [
        ({"remove": [3]}, 404),  # gỡ kỹ năng chưa có
        ({"update": [{"skill_id": 3, "status": "known"}]}, 404),
        (
            {"add": [{"skill_id": 999, "status": "known"}]},
            422,
        ),  # thêm kỹ năng không tồn tại
    ],
)
def test_patch_one_error_saves_nothing(client, db_session, skills, bad_part, expected):
    """FR-04: 2 thay đổi đúng + 1 sai → lỗi và hồ sơ Y NGUYÊN (không lưu một nửa)."""
    headers, user_id = register_and_login(client, "a@gmail.com")
    give(db_session, user_id, 1, "learning")
    give(db_session, user_id, 2, "known")
    before = snapshot(client, headers)

    body = {"update": [{"skill_id": 1, "status": "known"}], "remove": [2]}
    for key, value in bad_part.items():
        body[key] = body.get(key, []) + value
    response = client.patch(SKILLS_URL, json=body, headers=headers)

    assert response.status_code == expected
    assert snapshot(client, headers) == before


def test_patch_does_not_touch_other_users(client, db_session, skills):
    """NFR-06: user_id luôn lấy từ token — không sửa được hồ sơ người khác."""
    headers_a, user_a = register_and_login(client, "a@gmail.com")
    headers_b, user_b = register_and_login(client, "b@gmail.com")
    give(db_session, user_b, 1, "known")

    # A thử gỡ kỹ năng 1 (chỉ B có) → 404, hồ sơ B không đổi
    assert patch(client, headers_a, remove=[1]).status_code == 404
    assert snapshot(client, headers_b) == {1: ("known", "manual")}
