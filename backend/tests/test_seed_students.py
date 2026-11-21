"""Test script tạo học viên mẫu app/core/seed_data/seed_students.py (13/11/2026).

Chạy:  python -m pytest tests/test_seed_students.py -v      (trong thư mục backend)
"""

import pytest

from app.core.security import verify_password
from app.models.user import Users
from app.core.seed_data import seed_students as script

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


# ─────────────── 16/11: N tài khoản thật (địa chỉ cộng) + mật khẩu riêng ───────────────
# Dùng email GIẢ "demo@gmail.com" — email / mật khẩu thật chỉ truyền qua dòng lệnh, không vào repo.


def test_real_accounts_use_plus_addresses_and_own_passwords():
    base = script.generate_students(15)
    students = script.apply_real_accounts(base, "Demo@Gmail.com", 10, "Demo{n:03d}@")
    assert [s["email"] for s in students[:3]] == ["demo+hv01@gmail.com", "demo+hv02@gmail.com", "demo+hv03@gmail.com"]
    assert students[9]["email"] == "demo+hv10@gmail.com" and students[9]["password"] == "Demo010@"
    assert [s["full_name"] for s in students] == [s["full_name"] for s in base]  # họ tên, hồ sơ giữ nguyên
    assert students[10] == base[10] and "password" not in students[10]  # từ người thứ 11: tài khoản ảo như cũ
    assert "password" not in base[0]  # không sửa danh sách gốc


@pytest.mark.parametrize(
    "email, count, fmt",
    [("khong-co-a-cong", 10, "Demo{n:03d}@"), ("a+b@gmail.com", 10, "Demo{n:03d}@"), ("demo@gmail.com", 0, "Demo{n:03d}@"),
     ("demo@gmail.com", 99, "Demo{n:03d}@"), ("demo@gmail.com", 10, "yeu{n}")],
)  # fmt: skip
def test_real_accounts_reject_bad_input(email, count, fmt):
    with pytest.raises(ValueError):
        script.apply_real_accounts(script.generate_students(15), email, count, fmt)


def test_seed_real_accounts_login_with_own_password(db_session):
    students = script.apply_real_accounts(script.generate_students(12), "demo@gmail.com", 10, "Demo{n:03d}@")
    created, _ = script.seed_students(db_session, students, PASSWORD)
    assert created == 12
    real = db_session.query(Users).filter_by(email="demo+hv07@gmail.com").one()
    assert verify_password("Demo007@", real.hashed_password) and not verify_password(PASSWORD, real.hashed_password)
    fake = db_session.query(Users).filter_by(email=students[11]["email"]).one()
    assert verify_password(PASSWORD, fake.hashed_password)


def test_credentials_file_lists_every_account_with_its_password(tmp_path):
    import csv

    students = script.apply_real_accounts(script.generate_students(12), "demo@gmail.com", 10, "Demo{n:03d}@")
    path = tmp_path / "dang_nhap.csv"
    script.write_credentials(path, students, PASSWORD)
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    assert len(rows) == 12 and rows[0]["email"] == "demo+hv01@gmail.com" and rows[0]["password"] == "Demo001@"
    assert rows[11]["password"] == PASSWORD and rows[11]["loai"].startswith("ao")
