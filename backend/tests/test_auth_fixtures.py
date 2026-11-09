"""Test fixture dùng chung admin_headers / student_headers trong conftest.py (module 01 · Tuấn · 09/11/2026).

Chạy:  python -m pytest tests/test_auth_fixtures.py -v      (trong thư mục backend)
"""

ME_URL = "/api/me"


def test_admin_headers_logs_in_as_admin(client, admin_headers):
    response = client.get(ME_URL, headers=admin_headers)

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_student_headers_logs_in_as_student(client, student_headers):
    response = client.get(ME_URL, headers=student_headers)

    assert response.status_code == 200
    assert response.json()["role"] == "student"


def test_both_fixtures_together_are_different_users(client, admin_headers, student_headers):
    admin = client.get(ME_URL, headers=admin_headers).json()
    student = client.get(ME_URL, headers=student_headers).json()

    assert admin["user_id"] != student["user_id"]
