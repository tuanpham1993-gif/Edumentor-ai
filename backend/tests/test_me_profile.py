"""Test thông tin cá nhân thêm trên PATCH /api/me (module 01 · Tuấn · 12/11/2026).

Ngày sinh, giới tính, quê quán, số điện thoại, CCCD (mã hóa, chỉ trả bản che).
"""

import pytest

from app.core.security import decrypt_pii
from app.models import UserProfile, Users
from tests.conftest import STUDENT_EMAIL

URL = "/api/me"
CCCD = "345678901234"


def patch(client, headers, **body):
    return client.patch(URL, headers=headers, json={"full_name": "Student Test", **body})


def test_new_user_has_empty_details(client, student_headers):
    me = client.get(URL, headers=student_headers).json()
    for key in ("date_of_birth", "gender", "hometown", "phone", "citizen_id_masked"):
        assert me[key] is None
    assert "citizen_id" not in me


def test_save_all_details(client, student_headers):
    response = patch(
        client, student_headers,
        date_of_birth="2004-05-17", gender="male", hometown="  Đồng Nai  ", phone="0912 345 678", citizen_id=CCCD,
    )
    assert response.status_code == 200, response.text
    me = response.json()
    assert me["date_of_birth"] == "2004-05-17" and me["gender"] == "male"
    assert me["hometown"] == "Đồng Nai" and me["phone"] == "0912345678"
    assert me["citizen_id_masked"] == "345*********"
    assert CCCD not in response.text  # không lộ số đầy đủ ở bất kỳ đâu trong response
    assert client.get(URL, headers=student_headers).json() == me


def test_citizen_id_is_encrypted_in_db(client, student_headers, db_session):
    patch(client, student_headers, citizen_id=CCCD)
    user = db_session.query(Users).filter_by(email=STUDENT_EMAIL).one()
    row = db_session.get(UserProfile, user.user_id)

    assert CCCD not in (row.citizen_id_encrypted or "")  # không lưu dạng chữ thường
    assert decrypt_pii(row.citizen_id_encrypted) == CCCD  # giải mã được bằng khóa server
    assert len(row.citizen_id_hash) == 64 and CCCD not in row.citizen_id_hash


def test_omitted_fields_kept_null_clears(client, student_headers):
    patch(client, student_headers, hometown="Huế", phone="0912345678", citizen_id=CCCD)
    me = patch(client, student_headers, phone=None).json()  # chỉ xóa SĐT

    assert me["phone"] is None and me["hometown"] == "Huế" and me["citizen_id_masked"] == "345*********"
    assert patch(client, student_headers, citizen_id=None).json()["citizen_id_masked"] is None


def test_phone_plus84_is_normalized(client, student_headers):
    assert patch(client, student_headers, phone="+84 912 345 678").json()["phone"] == "0912345678"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("phone", "12345", "10 chữ số"),
        ("phone", "1912345678", "bắt đầu bằng 0"),
        ("citizen_id", "34567890123", "12 chữ số"),
        ("citizen_id", "34567890123a", "12 chữ số"),
        ("date_of_birth", "2999-01-01", "Ngày sinh"),
        ("gender", "khac", None),
        ("hometown", "x" * 101, None),
    ],
)
def test_invalid_values_rejected(client, student_headers, field, value, message):
    response = patch(client, student_headers, **{field: value})
    assert response.status_code == 422
    if message:
        assert message in response.text


def test_same_citizen_id_cannot_be_used_twice(client, student_headers, admin_headers):
    assert patch(client, student_headers, citizen_id=CCCD).status_code == 200
    response = client.patch(URL, headers=admin_headers, json={"full_name": "Admin Test", "citizen_id": CCCD})

    assert response.status_code == 409
    assert response.json()["detail"] == "Số CCCD này đã được dùng cho một tài khoản khác."
    assert client.get(URL, headers=admin_headers).json()["citizen_id_masked"] is None


def test_cannot_change_email_or_role(client, student_headers):
    me = client.patch(URL, headers=student_headers, json={"full_name": "X", "email": "a@b.c", "role": "admin"}).json()
    assert me["email"] == STUDENT_EMAIL and me["role"] == "student"
