"""Test script tạo học viên mẫu scripts/seed_students.py (13/11/2026).

Chạy:  python -m pytest tests/test_seed_students.py -v      (trong thư mục backend)
"""

import pytest

from app.core.security import verify_password
from app.models.user import Users
from scripts import seed_students as script

PASSWORD = "HocVien@123"


def test_generate_1500_unique_emails():
    students = script.generate_students(1500)
    emails = [s["email"] for s in students]
    assert len(students) == 1500
    assert len(set(emails)) == 1500  # không trùng
    assert all(e.endswith("@example.com") and e.isascii() for e in emails)
    assert emails[0].endswith(".0001@example.com")
    assert emails[-1].endswith(".1500@example.com")


def test_generate_is_deterministic():
    assert script.generate_students(50) == script.generate_students(50)


def test_to_ascii_slug_removes_accents():
    assert script.to_ascii_slug("Nguyễn Văn Đạt") == "nguyenvandat"


def test_seed_creates_students_with_profile(db_session):
    students = script.generate_students(30)
    created, skipped = script.seed_students(db_session, students, PASSWORD)
    assert (created, skipped) == (30, 0)

    users = db_session.query(Users).all()
    assert len(users) == 30
    assert all(u.role == "student" and u.is_active for u in users)
    assert verify_password(PASSWORD, users[0].hashed_password)
    assert users[0].profile is not None and users[0].hometown


def test_seed_is_idempotent(db_session):
    script.seed_students(db_session, script.generate_students(20), PASSWORD)
    # chạy lại với số lớn hơn: chỉ thêm phần còn thiếu
    created, skipped = script.seed_students(db_session, script.generate_students(25), PASSWORD)
    assert (created, skipped) == (5, 20)
    assert db_session.query(Users).count() == 25


def test_seed_rejects_weak_password(db_session):
    with pytest.raises(ValueError):
        script.seed_students(db_session, script.generate_students(1), "yeu")
    assert db_session.query(Users).count() == 0
