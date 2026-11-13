"""Test GĐ7 bước 7.3 — API quản trị ngân hàng câu hỏi ôn tập (module 09 · Tuấn · 13/11/2026).

Chạy:  python -m pytest tests/test_review_admin.py -v      (trong thư mục backend)
Quy tắc phiên bản / sửa nhỏ / xóa đã test kỹ ở test_review_bank.py — ở đây kiểm API: quyền, mã HTTP, dữ liệu trả về.
"""

# ruff: noqa: F811 — fixture import từ file test khác; pytest truyền qua TÊN tham số

import pytest

from app.models import ReviewQuestion, ReviewQuestionMeta
from app.services import review_bank_service as bank_service
from scripts import seed_review as script
from tests.test_review_bank import by_code, use_in_attempt
from tests.test_seed_review import bank, course_312  # noqa: F401 — fixture

URL = "/api/admin/review/questions"


@pytest.fixture()
def seeded(db_session, course_312, bank):
    script.seed_bank(db_session, bank)
    db_session.commit()
    return bank


def mcq_body(db_session, **change) -> dict:
    q = by_code(db_session, "312-PY-TN-01")
    return {
        "skill_id": q.skill_id,
        "chunk_id": q.chunk_id,
        "type": "mcq",
        "level": "recognize",
        "content": "What does print() do?",
        "options": ["Shows output", "Reads input", "Loops", "Stops program"],
        "correct_index": 0,
        "explanation": "print writes to the screen.",
        **change,
    }


def essay_body(db_session, **change) -> dict:
    """Câu tự luận DỄ hợp lệ: 3 ý (2–3 ý), tổng 10 điểm."""
    q = by_code(db_session, "312-PY-TN-01")
    return {
        "skill_id": q.skill_id,
        "chunk_id": q.chunk_id,
        "type": "essay",
        "level": "easy",
        "content": "Explain what print() and input() do.",
        "rubric": [
            {"text": "print shows output", "max_points": 4, "main_keywords": ["print", "output"]},
            {"text": "input reads text from the user", "max_points": 3, "main_keywords": ["input", "user"]},
            {"text": "input returns a string", "max_points": 3, "main_keywords": ["string"]},
        ],
        "explanation": "print writes, input reads a string.",
        **change,
    }


def items(response) -> list[dict]:
    assert response.status_code == 200, response.text
    return response.json()["items"]


# ─────────────── quyền ───────────────


@pytest.mark.parametrize(
    "method, path",
    [
        ("get", ""),
        ("get", "/1"),
        ("post", ""),
        ("patch", "/1"),
        ("post", "/1/activate"),
        ("post", "/1/deactivate"),
        ("delete", "/1"),
        ("post", "/1/approve"),
        ("get", "/1/suggested-code"),
        ("post", "/1/reject"),
    ],
)
def test_requires_admin(client, seeded, student_headers, method, path):
    assert getattr(client, method)(URL + path).status_code == 401
    assert getattr(client, method)(URL + path, headers=student_headers).status_code == 403


# ─────────────── danh sách / chi tiết ───────────────


def test_list_paginates_and_filters(client, seeded, admin_headers):
    response = client.get(URL, params={"size": 10}, headers=admin_headers)
    assert response.status_code == 200
    page = response.json()
    assert page["total"] == 100 and len(page["items"]) == 10
    item = page["items"][0]
    assert item["version"] == 1 and item["used_count"] == 0 and item["review_status"] == "approved"
    assert item["skill_name"]

    essays = client.get(URL, params={"type": "essay", "size": 100}, headers=admin_headers).json()
    assert essays["total"] == 30 and all(i["type"] == "essay" for i in essays["items"])

    found = client.get(URL, params={"q": "312-py-tn-01"}, headers=admin_headers).json()
    assert [i["code"] for i in found["items"]] == ["312-PY-TN-01"]

    by_course = client.get(URL, params={"course_id": 312, "size": 1}, headers=admin_headers).json()
    assert by_course["total"] == 100
    assert client.get(URL, params={"course_id": 99999}, headers=admin_headers).json()["total"] == 0


def test_list_hides_old_versions_by_default(client, seeded, admin_headers, db_session):
    q = by_code(db_session, "312-PY-TN-01")
    use_in_attempt(db_session, q)
    db_session.commit()
    client.patch(f"{URL}/{q.question_id}", json={"correct_index": 2}, headers=admin_headers)

    latest = client.get(URL, params={"q": "312-PY-TN-01"}, headers=admin_headers).json()
    assert [(i["code"], i["version"]) for i in latest["items"]] == [("312-PY-TN-01", 2)]
    every = client.get(URL, params={"q": "312-PY-TN-01", "latest_only": False}, headers=admin_headers).json()
    # used_count đếm bằng subquery GROUP BY: bản cũ có 1 bài làm, bản mới chưa có
    assert {i["code"]: (i["version"], i["used_count"]) for i in every["items"]} == {
        "312-PY-TN-01": (2, 0),
        "312-PY-TN-01~v1": (1, 1),
    }


def test_question_without_meta_is_treated_as_v1(client, seeded, admin_headers, db_session):
    """Câu nạp trước 13/11 (DB thật) chưa có dòng meta → OUTER JOIN + COALESCE: v1, họ = chính nó, đã duyệt."""
    q = by_code(db_session, "312-PY-TN-01")
    db_session.delete(db_session.get(ReviewQuestionMeta, q.question_id))
    db_session.commit()

    listed = items(client.get(URL, params={"q": "312-PY-TN-01"}, headers=admin_headers))  # latest_only mặc định
    assert [(i["question_id"], i["version"], i["family_id"], i["review_status"]) for i in listed] == [
        (q.question_id, 1, q.question_id, "approved")
    ]
    approved = client.get(URL, params={"review_status": "approved", "size": 1}, headers=admin_headers).json()
    assert approved["total"] == 100

    detail = client.get(f"{URL}/{q.question_id}", headers=admin_headers).json()
    assert (detail["version"], detail["family_id"]) == (1, q.question_id)
    db_session.expire_all()
    meta = db_session.get(ReviewQuestionMeta, q.question_id)  # xem chi tiết → meta được tạo và lưu
    assert meta is not None
    assert (meta.family_id, meta.version, meta.review_status) == (q.question_id, 1, "approved")


def test_list_filters(client, seeded, admin_headers, db_session):
    def total(**params):
        response = client.get(URL, params={**params, "size": 1}, headers=admin_headers)
        assert response.status_code == 200, response.text
        return response.json()["total"]

    py = by_code(db_session, "312-PY-TN-01")
    assert total(skill_id=py.skill_id) == 20
    assert total(course_id=312, skill_id=py.skill_id) == 20
    assert total(course_id=312, skill_id=123456) == 0  # kỹ năng không thuộc khóa → giao rỗng
    assert total(course_id=99999, skill_id=py.skill_id) == 0
    assert total(level="recognize") == 35  # 7 câu NB × 5 kỹ năng
    assert total(level="advanced") == 12
    assert total(source="bank") == 100
    assert total(source="ai") == 0

    client.post(f"{URL}/{py.question_id}/deactivate", headers=admin_headers)
    assert total(is_active=False) == 1
    assert total(is_active=True) == 99


def test_list_search_content(client, seeded, admin_headers, db_session):
    q = by_code(db_session, "312-PY-TN-04")
    fragment = q.content[3:25].upper()  # tìm không phân biệt hoa thường
    codes = [i["code"] for i in items(client.get(URL, params={"q": fragment}, headers=admin_headers))]
    assert q.code in codes
    assert items(client.get(URL, params={"q": "100%"}, headers=admin_headers)) == []  # % không phải ký tự đại diện


def test_list_newest_first(client, seeded, admin_headers, db_session):
    created = client.post(URL, json=mcq_body(db_session, code="PY-TN-15"), headers=admin_headers).json()
    assert items(client.get(URL, headers=admin_headers))[0]["question_id"] == created["question_id"]


@pytest.mark.parametrize(
    "params",
    [{"size": 0}, {"size": 101}, {"page": 0}, {"source": "xyz"}, {"type": "abc"}, {"review_status": "ok"}],
)
def test_list_invalid_params_is_422(client, seeded, admin_headers, params):
    assert client.get(URL, params=params, headers=admin_headers).status_code == 422


def test_detail_has_answer_and_versions(client, seeded, admin_headers, db_session):
    q = by_code(db_session, "312-PY-TL-02")
    response = client.get(f"{URL}/{q.question_id}", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["rubric"] and body["options"] is None
    assert [v["version"] for v in body["versions"]] == [1]
    assert client.get(f"{URL}/999999", headers=admin_headers).status_code == 404


# ─────────────── thêm ───────────────


def test_create_question(client, seeded, admin_headers, db_session):
    response = client.post(URL, json=mcq_body(db_session, code="PY-TN-15"), headers=admin_headers)
    assert response.status_code == 201, response.text
    body = response.json()
    assert (body["code"], body["version"], body["is_active"], body["source"]) == (
        "PY-TN-15",
        1,
        True,
        "bank",
    )


@pytest.mark.parametrize(
    "change, code",
    [
        ({"correct_index": 9}, 422),  # validator
        ({"options": ["a", "b"]}, 422),
        ({"code": "312-PY-TN-01"}, 409),  # mã trùng
        ({"skill_id": 123456}, 400),  # kỹ năng không tồn tại
        ({"chunk_id": 999999}, 400),  # đoạn tri thức không tồn tại
    ],
)
def test_create_invalid(client, seeded, admin_headers, db_session, change, code):
    response = client.post(URL, json=mcq_body(db_session, **change), headers=admin_headers)
    assert response.status_code == code, response.text
    if code == 422:  # lỗi từ validator ngân hàng (không phải lỗi kiểu dữ liệu của Pydantic)
        assert response.json()["detail"]["errors"]


def test_create_essay(client, seeded, admin_headers, db_session):
    response = client.post(URL, json=essay_body(db_session), headers=admin_headers)
    assert response.status_code == 201, response.text
    body = response.json()
    assert (body["type"], body["level"], body["options"], body["correct_index"]) == ("essay", "easy", None, None)
    points = [item["max_points"] for item in body["rubric"]]
    assert points == [4, 3, 3]
    assert all(type(p) is int for p in points)  # gửi 4 → giữ 4, không thành 4.0
    assert body["rubric"][2]["sub_keywords"] == []  # mặc định của RubricItem


def test_create_essay_invalid(client, seeded, admin_headers, db_session):
    rubric = essay_body(db_session)["rubric"]
    nine = [{**rubric[0], "max_points": 3}, *rubric[1:]]  # tổng 9
    four_items = [{**r, "max_points": 2.5} for r in [*rubric, rubric[0]]]  # câu dễ chỉ 2–3 ý
    for bad in (nine, four_items):
        response = client.post(URL, json=essay_body(db_session, rubric=bad), headers=admin_headers)
        assert response.status_code == 422, response.text
        assert response.json()["detail"]["errors"]


def test_create_chunk_of_other_skill_is_400(client, seeded, admin_headers, db_session):
    other = by_code(db_session, "312-VAR-TL-01")
    response = client.post(URL, json=mcq_body(db_session, chunk_id=other.chunk_id), headers=admin_headers)
    assert response.status_code == 400 and "không thuộc kỹ năng" in response.json()["detail"]


# ─────────────── sửa ───────────────


def test_edit_unused_in_place(client, seeded, admin_headers, db_session):
    q = by_code(db_session, "312-PY-TN-01")
    response = client.patch(f"{URL}/{q.question_id}", json={"correct_index": 2}, headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["versioned"] is False and body["changed"] == ["correct_index"]
    assert body["question"]["question_id"] == q.question_id and body["question"]["correct_index"] == 2


def test_edit_used_creates_version(client, seeded, admin_headers, db_session):
    q = by_code(db_session, "312-PY-TN-01")
    old_id = q.question_id
    use_in_attempt(db_session, q)
    db_session.commit()

    response = client.patch(
        f"{URL}/{old_id}",
        json={"correct_index": 2, "note": "sửa đáp án"},
        headers=admin_headers,
    )
    body = response.json()
    assert response.status_code == 200 and body["versioned"] is True
    new = body["question"]
    assert new["question_id"] != old_id and new["version"] == 2 and new["code"] == "312-PY-TN-01"
    assert new["change_note"] == "sửa đáp án"
    assert [v["version"] for v in new["versions"]] == [2, 1]

    old = client.get(f"{URL}/{old_id}", headers=admin_headers).json()
    assert old["code"] == "312-PY-TN-01~v1" and old["is_active"] is False and old["used_count"] == 1


def test_edit_no_change(client, seeded, admin_headers, db_session):
    q = by_code(db_session, "312-PY-TN-01")
    body = client.patch(f"{URL}/{q.question_id}", json={"content": q.content}, headers=admin_headers).json()
    assert body["versioned"] is False and body["changed"] == []


def test_minor_edit_rules(client, seeded, admin_headers, db_session):
    q = by_code(db_session, "312-PY-TN-01")
    use_in_attempt(db_session, q)
    db_session.commit()
    url = f"{URL}/{q.question_id}"

    ok = client.patch(
        url,
        json={"explanation": "Giải thích mới.", "minor": True},
        headers=admin_headers,
    )
    assert ok.status_code == 200 and ok.json()["versioned"] is False

    wrong = client.patch(url, json={"correct_index": 3, "minor": True}, headers=admin_headers)
    assert wrong.status_code == 409


def test_edit_invalid_is_422_and_rolled_back(client, seeded, admin_headers, db_session):
    q = by_code(db_session, "312-PY-TN-01")
    response = client.patch(
        f"{URL}/{q.question_id}",
        json={"options": ["a", "a", "b", "c"]},
        headers=admin_headers,
    )
    assert response.status_code == 422
    db_session.expire_all()
    assert len(set(by_code(db_session, "312-PY-TN-01").options)) == 4


def test_edit_bad_references_is_400(client, seeded, admin_headers, db_session):
    q = by_code(db_session, "312-PY-TN-01")
    other_chunk = by_code(db_session, "312-VAR-TL-01").chunk_id
    url = f"{URL}/{q.question_id}"
    assert client.patch(url, json={"skill_id": 123456}, headers=admin_headers).status_code == 400
    response = client.patch(url, json={"chunk_id": other_chunk}, headers=admin_headers)
    assert response.status_code == 400
    assert "không thuộc kỹ năng" in response.json()["detail"]


def test_cannot_change_type(client, seeded, admin_headers, db_session):
    q = by_code(db_session, "312-PY-TN-01")
    body = client.patch(f"{URL}/{q.question_id}", json={"type": "essay"}, headers=admin_headers).json()
    assert body["changed"] == []  # "type" không có trong QuestionUpdate → bỏ qua


# ─────────────── bật / tắt / xóa ───────────────


def test_deactivate_activate(client, seeded, admin_headers, db_session):
    qid = by_code(db_session, "312-PY-TN-01").question_id
    assert client.post(f"{URL}/{qid}/deactivate", headers=admin_headers).json()["is_active"] is False
    assert client.post(f"{URL}/{qid}/activate", headers=admin_headers).json()["is_active"] is True


def test_cannot_activate_old_version(client, seeded, admin_headers, db_session):
    q = by_code(db_session, "312-PY-TN-01")
    old_id = q.question_id
    use_in_attempt(db_session, q)
    db_session.commit()
    client.patch(f"{URL}/{old_id}", json={"correct_index": 2}, headers=admin_headers)
    assert client.post(f"{URL}/{old_id}/activate", headers=admin_headers).status_code == 409


def test_delete_unused_and_used(client, seeded, admin_headers, db_session):
    unused = by_code(db_session, "312-PY-TN-02").question_id
    used_q = by_code(db_session, "312-PY-TN-01")
    use_in_attempt(db_session, used_q)
    db_session.commit()

    assert client.delete(f"{URL}/{unused}", headers=admin_headers).json() == {"result": "deleted"}
    assert client.get(f"{URL}/{unused}", headers=admin_headers).status_code == 404
    db_session.expire_all()
    assert db_session.get(ReviewQuestionMeta, unused) is None  # meta xóa theo, không mồ côi
    assert client.delete(f"{URL}/{used_q.question_id}", headers=admin_headers).json() == {"result": "deactivated"}
    assert client.delete(f"{URL}/999999", headers=admin_headers).status_code == 404


# ─────────────── duyệt câu AI soạn ───────────────


@pytest.fixture()
def pending(db_session, seeded) -> ReviewQuestion:
    q = bank_service.create_question(db_session, mcq_body(db_session), source="ai", review_status="pending")
    db_session.commit()
    return q


def test_pending_listed_and_cannot_be_activated(client, pending, admin_headers):
    listed = client.get(URL, params={"review_status": "pending"}, headers=admin_headers).json()
    assert [i["question_id"] for i in listed["items"]] == [pending.question_id]
    assert client.post(f"{URL}/{pending.question_id}/activate", headers=admin_headers).status_code == 409


def test_approve_gives_code_and_activates(client, pending, admin_headers):
    response = client.post(
        f"{URL}/{pending.question_id}/approve",
        json={"code": "PY-TN-16"},
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert (body["code"], body["review_status"], body["is_active"]) == (
        "PY-TN-16",
        "approved",
        True,
    )
    # duyệt lần 2 → 409
    again = client.post(f"{URL}/{pending.question_id}/approve", json={"code": "PY-TN-17"}, headers=admin_headers)
    assert again.status_code == 409


@pytest.mark.parametrize("body", [None, {}, {"code": ""}, {"code": "   "}])
def test_approve_requires_code(client, pending, admin_headers, body):
    """Tuấn chốt 13/11: duyệt BẮT BUỘC nhập mã (chưa kịp nhập → cứ để Chờ duyệt)."""
    response = client.post(f"{URL}/{pending.question_id}/approve", json=body, headers=admin_headers)
    assert response.status_code == 422
    detail = client.get(f"{URL}/{pending.question_id}", headers=admin_headers).json()
    assert (detail["review_status"], detail["is_active"]) == ("pending", False)


def test_suggested_code_follows_skill_codes(client, pending, admin_headers, db_session):
    """Kỹ năng PY đã có 312-PY-TN-01..14 → gợi ý "PY-TN-15" (bỏ tiền tố khóa — QT9); duyệt xong → câu sau "PY-TN-16"."""
    url = f"{URL}/{pending.question_id}/suggested-code"
    assert client.get(url, headers=admin_headers).json() == {"code": "PY-TN-15"}
    client.post(f"{URL}/{pending.question_id}/approve", json={"code": "PY-TN-15"}, headers=admin_headers)

    data = {**mcq_body(db_session), "content": "Another AI question?"}
    second = bank_service.create_question(db_session, data, source="ai", review_status="pending")
    db_session.commit()
    assert client.get(f"{URL}/{second.question_id}/suggested-code", headers=admin_headers).json() == {
        "code": "PY-TN-16"
    }


def test_suggested_code_essay_uses_tl(client, seeded, admin_headers, db_session):
    q = by_code(db_session, "312-PY-TL-02")
    # PY đã có 312-PY-TL-01..06 → tự luận tiếp theo là 07 (đếm riêng với trắc nghiệm TN-01..14)
    assert client.get(f"{URL}/{q.question_id}/suggested-code", headers=admin_headers).json() == {"code": "PY-TL-07"}


def test_suggested_code_none_when_skill_has_no_codes(client, seeded, admin_headers, db_session):
    data = {**mcq_body(db_session), "chunk_id": None}
    q = bank_service.create_question(db_session, data, source="ai", review_status="pending")
    db_session.commit()
    db_session.query(ReviewQuestion).filter(
        ReviewQuestion.skill_id == q.skill_id, ReviewQuestion.question_id != q.question_id
    ).update({"code": None})
    db_session.commit()
    assert client.get(f"{URL}/{q.question_id}/suggested-code", headers=admin_headers).json() == {"code": None}
    assert client.get(f"{URL}/999999/suggested-code", headers=admin_headers).status_code == 404


def test_approve_duplicate_code_is_409(client, pending, admin_headers):
    response = client.post(
        f"{URL}/{pending.question_id}/approve",
        json={"code": "312-PY-TN-01"},
        headers=admin_headers,
    )
    assert response.status_code == 409
    detail = client.get(f"{URL}/{pending.question_id}", headers=admin_headers).json()
    assert detail["review_status"] == "pending"  # rollback — không duyệt nửa vời


def test_reject_hides_question(client, pending, admin_headers):
    body = client.post(f"{URL}/{pending.question_id}/reject", headers=admin_headers).json()
    assert (body["review_status"], body["is_active"]) == ("rejected", False)
    assert client.post(f"{URL}/{pending.question_id}/reject", headers=admin_headers).status_code == 409
    # câu bị từ chối không bật được bằng công tắc, cũng không duyệt lại được
    assert client.post(f"{URL}/{pending.question_id}/activate", headers=admin_headers).status_code == 409
    approve = client.post(f"{URL}/{pending.question_id}/approve", json={"code": "PY-TN-15"}, headers=admin_headers)
    assert approve.status_code == 409
    rejected = client.get(URL, params={"review_status": "rejected"}, headers=admin_headers).json()
    assert [i["question_id"] for i in rejected["items"]] == [pending.question_id]
