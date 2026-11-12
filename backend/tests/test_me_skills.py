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


# ─────────────── GET /api/me/skills/suggestions (FĐ6) ───────────────

SUGGEST_URL = "/api/me/skills/suggestions"


@pytest.fixture()
def catalog(db_session, skills):
    """Thêm quan hệ + số khóa học cho 4 kỹ năng mẫu (1 SQL, 2 Python, 3 Docker, 4 ẩn) + 5 Pandas, 6 R."""
    from app.models.course_skill import CourseSkill
    from app.models.skill_relation import SkillRelation

    db_session.add_all(
        [
            Skills(skill_id=5, skill="Pandas", is_active=True),
            Skills(skill_id=6, skill="R Programming", is_active=True),
            # Python là nền của Pandas (next); Python "related" với R; Python → kỹ năng ẩn (bỏ qua)
            SkillRelation(from_skill_id=2, to_skill_id=5, relation_type="prerequisite"),
            SkillRelation(from_skill_id=6, to_skill_id=2, relation_type="related"),
            SkillRelation(from_skill_id=2, to_skill_id=4, relation_type="extension"),
        ]
    )
    # số khóa học: SQL 3, Docker 2, Pandas 1, kỹ năng ẩn 9 (không được gợi ý)
    for course_id, skill_id in [(1, 1), (2, 1), (3, 1), (1, 3), (2, 3), (1, 5)] + [
        (i, 4) for i in range(10, 19)
    ]:
        db_session.add(CourseSkill(course_id=course_id, skill_id=skill_id))
    db_session.commit()


def test_suggestions_without_token_returns_401(client):
    assert client.get(SUGGEST_URL).status_code == 401


def test_suggestions_empty_profile_returns_popular(client, catalog):
    headers, _ = register_and_login(client, "a@gmail.com")
    data = client.get(SUGGEST_URL, headers=headers).json()
    assert [(s["skill"], s["reason"], s["course_count"]) for s in data] == [
        ("SQL", "popular", 3),
        ("Docker", "popular", 2),
        ("Pandas", "popular", 1),
    ]  # kỹ năng ẩn (9 khóa) không xuất hiện


def test_suggestions_next_and_related_come_first(client, db_session, catalog):
    headers, user_id = register_and_login(client, "a@gmail.com")
    give(db_session, user_id, 2, "known")  # có Python
    data = client.get(SUGGEST_URL, headers=headers).json()

    assert [(s["skill"], s["reason"], s["via"]) for s in data[:2]] == [
        ("Pandas", "next", "Python Programming"),
        ("R Programming", "related", "Python Programming"),
    ]
    rest = [s["skill"] for s in data[2:]]
    assert rest == ["SQL", "Docker"]  # phổ biến, bỏ Pandas (đã gợi ý) và Python (đã có)
    assert all(s["skill_id"] != 2 for s in data)


def test_suggestions_respect_limit(client, catalog):
    headers, _ = register_and_login(client, "a@gmail.com")
    assert (
        len(client.get(SUGGEST_URL, params={"limit": 2}, headers=headers).json()) == 2
    )
    assert (
        client.get(SUGGEST_URL, params={"limit": 0}, headers=headers).status_code == 422
    )


# ─────────────── Khám phá kỹ năng theo danh mục (FĐ6) ───────────────

CATALOG_URL = "/api/me/skills/catalog"


def test_categorize_examples():
    from app.utils.skill_categories import categorize

    assert categorize("Python Programming") == "programming"
    assert (
        categorize("Computer Programming") == "programming"
    )  # không nhầm "r programming"
    assert categorize("SQL") == "database"
    assert categorize("Jquery") == "web"  # không nhầm "query"
    assert (
        categorize("Web Application Security") == "security"
    )  # An ninh mạng ưu tiên hơn Web
    assert categorize("Design Patterns") == "programming"
    assert categorize("Machine Learning") == "ai"
    assert categorize("Photovoltaics") == "science"
    assert categorize("Zzz không khớp gì") == "other"


def test_catalog_requires_login(client):
    assert client.get(CATALOG_URL).status_code == 401
    assert client.get(CATALOG_URL + "/categories").status_code == 401


def test_catalog_categories_count_active_skills(client, catalog):
    headers, _ = register_and_login(client, "a@gmail.com")
    data = client.get(CATALOG_URL + "/categories", headers=headers).json()
    counts = {c["key"]: c["count"] for c in data}
    assert data[-1]["key"] == "other"  # "Khác" luôn ở cuối
    # SQL → database · Python, R → programming / data · Docker → cloud · Pandas → data; kỹ năng ẩn không tính
    assert sum(counts.values()) == 5
    assert counts["database"] == 1 and counts["cloud"] == 1


def test_catalog_popular_sort_paging_and_my_status(client, db_session, catalog):
    headers, user_id = register_and_login(client, "a@gmail.com")
    give(db_session, user_id, 3, "learning")  # Docker đã có
    page1 = client.get(CATALOG_URL, params={"size": 2}, headers=headers).json()
    assert page1["total"] == 5 and page1["page"] == 1
    assert [(i["skill"], i["course_count"]) for i in page1["items"]] == [
        ("SQL", 3),
        ("Docker", 2),
    ]
    assert page1["items"][1]["my_status"] == "learning"
    assert page1["items"][0]["my_status"] is None
    page3 = client.get(
        CATALOG_URL, params={"size": 2, "page": 3}, headers=headers
    ).json()
    assert len(page3["items"]) == 1


def test_catalog_filter_search_and_name_sort(client, catalog):
    headers, _ = register_and_login(client, "a@gmail.com")
    data = client.get(CATALOG_URL, params={"category": "cloud"}, headers=headers).json()
    assert [i["skill"] for i in data["items"]] == ["Docker"]
    data = client.get(
        CATALOG_URL, params={"q": "pro", "sort": "name"}, headers=headers
    ).json()
    assert [i["skill"] for i in data["items"]] == [
        "Python Programming",
        "R Programming",
    ]
    assert (
        client.get(CATALOG_URL, params={"category": "xyz"}, headers=headers).status_code
        == 422
    )


# ─────────────── Hàm cho module khác gọi: khóa học / ôn tập (08/11) ───────────────


def profile_of(db_session, user_id):
    rows = db_session.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    return {r.skill_id: (r.status, r.source) for r in rows}


@pytest.fixture()
def user_id(client, skills):
    _, uid = register_and_login(client, "a@gmail.com")
    return uid


def test_join_course_adds_learning_keeps_known(db_session, user_id):
    from app.services import user_skill_service as svc

    give(db_session, user_id, 1, "known")  # SQL đã biết
    svc.add_learning_from_course(db_session, user_id, [1, 2, 3])
    db_session.commit()
    assert profile_of(db_session, user_id) == {
        1: ("known", "manual"),  # giữ nguyên
        2: ("learning", "course"),
        3: ("learning", "course"),
    }


def test_abandon_course_removes_only_course_learning(db_session, user_id):
    from app.services import user_skill_service as svc

    give(db_session, user_id, 1, "learning")  # tự thêm (manual) → không gỡ
    svc.add_learning_from_course(db_session, user_id, [2, 3])
    db_session.commit()
    # Docker (3) còn được một khóa khác đang học dạy → giữ
    svc.remove_learning_from_course(db_session, user_id, [1, 2, 3], keep_skill_ids=[3])
    db_session.commit()
    assert profile_of(db_session, user_id) == {
        1: ("learning", "manual"),
        3: ("learning", "course"),
    }


def test_abandon_then_rejoin_adds_back(db_session, user_id):
    from app.services import user_skill_service as svc

    svc.add_learning_from_course(db_session, user_id, [2])
    svc.remove_learning_from_course(db_session, user_id, [2])
    db_session.commit()
    assert profile_of(db_session, user_id) == {}
    svc.add_learning_from_course(db_session, user_id, [2])
    db_session.commit()
    assert profile_of(db_session, user_id) == {2: ("learning", "course")}


def test_abandon_does_not_remove_known(db_session, user_id):
    from app.services import user_skill_service as svc

    svc.add_learning_from_course(db_session, user_id, [2])
    svc.mark_known(db_session, user_id, [2], source="course")  # đã hoàn thành → known
    svc.remove_learning_from_course(db_session, user_id, [2])
    db_session.commit()
    assert profile_of(db_session, user_id) == {2: ("known", "course")}


def test_mark_known_course_and_review(db_session, user_id):
    from app.services import user_skill_service as svc

    give(db_session, user_id, 1, "learning")
    svc.add_learning_from_course(db_session, user_id, [2])
    svc.mark_known(
        db_session, user_id, [1, 2, 3], source="course"
    )  # S8 hoàn thành khóa
    db_session.commit()
    assert profile_of(db_session, user_id) == {
        1: ("known", "course"),
        2: ("known", "course"),
        3: ("known", "course"),
    }
    svc.mark_known(
        db_session, user_id, [2], source="review"
    )  # T13 đạt ôn tập → xác nhận
    svc.mark_known(db_session, user_id, [2], source="course")  # không ghi đè review
    db_session.commit()
    assert profile_of(db_session, user_id)[2] == ("known", "review")
    with pytest.raises(ValueError):
        svc.mark_known(db_session, user_id, [1], source="manual")
