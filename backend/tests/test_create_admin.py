"""Test tự động: script tạo admin scripts/create_admin.py (module 01 · Tuấn · GĐ8, 07/11/2026).

Chạy:  python -m pytest tests/test_create_admin.py -v      (trong thư mục backend)

- Test hàm create_admin() trực tiếp với db_session.
- Test main() (S1–S4): monkeypatch getpass (giả lập gõ mật khẩu), sys.argv (tham số dòng lệnh)
  và SessionLocal (dùng DB test thay vì PostgreSQL thật).
"""

import sys

import pytest
from pydantic import ValidationError

from app.models.user import Users
from app.services import auth_service
from scripts import create_admin as script

EMAIL = "admin@edumentor.vn"
PASSWORD = "Admin!123"


def run_main(monkeypatch, db_session, passwords, email=EMAIL):
    """Chạy main() như gõ lệnh, lần lượt 'gõ' các mật khẩu trong `passwords`.

    main() dùng chính phiên DB test (db_session) thay cho SessionLocal của PostgreSQL thật.
    """
    answers = iter(passwords)
    monkeypatch.setattr(script.getpass, "getpass", lambda prompt="": next(answers))
    monkeypatch.setattr(
        sys, "argv", ["create_admin", "--email", email, "--full-name", "Quản trị viên"]
    )
    monkeypatch.setattr(script, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(script, "create_tables", lambda: None)
    return script.main()


# ─────────────── Hàm create_admin() ───────────────


def test_create_admin_success(db_session):
    user = script.create_admin(
        db_session, email=EMAIL, full_name="Quản trị viên", password=PASSWORD
    )

    assert user.role == "admin"
    assert user.hashed_password.startswith("$2b$")  # vẫn chỉ lưu bản băm


def test_admin_can_login(client, db_session):
    script.create_admin(
        db_session, email=EMAIL, full_name="Quản trị viên", password=PASSWORD
    )

    response = client.post(
        "/api/auth/login", json={"email": EMAIL, "password": PASSWORD}
    )

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"


def test_duplicate_email_raises(db_session):
    script.create_admin(db_session, email=EMAIL, full_name="A", password=PASSWORD)

    with pytest.raises(auth_service.EmailAlreadyExistsError):
        script.create_admin(db_session, email=EMAIL, full_name="B", password=PASSWORD)


def test_weak_password_raises(db_session):
    with pytest.raises(ValidationError):
        script.create_admin(db_session, email=EMAIL, full_name="A", password="abc")


# ─────────────── Lệnh main() — S1 → S4 ───────────────


def test_main_success_prints_and_returns_0(db_session, monkeypatch, capsys):  # S1
    code = run_main(monkeypatch, db_session, [PASSWORD, PASSWORD])

    assert code == 0
    output = capsys.readouterr().out
    assert "Đã tạo admin #" in output and EMAIL in output
    assert PASSWORD not in output  # không bao giờ in mật khẩu
    assert db_session.query(Users).filter_by(email=EMAIL).one().role == "admin"


def test_main_duplicate_email(db_session, monkeypatch, capsys):  # S2
    run_main(monkeypatch, db_session, [PASSWORD, PASSWORD])

    code = run_main(monkeypatch, db_session, [PASSWORD, PASSWORD])

    assert code == 1
    assert "đã có tài khoản" in capsys.readouterr().out


def test_main_weak_password(db_session, monkeypatch, capsys):  # S3
    code = run_main(monkeypatch, db_session, ["abc", "abc"])

    assert code == 1
    assert "Dữ liệu không hợp lệ" in capsys.readouterr().out


def test_main_confirm_mismatch(db_session, monkeypatch, capsys):  # S4
    code = run_main(monkeypatch, db_session, [PASSWORD, "Khac@123"])

    assert code == 1
    assert "không khớp" in capsys.readouterr().out
