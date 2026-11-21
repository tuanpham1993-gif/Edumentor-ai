"""G2a — Alembic tự chạy lúc khởi động (module 09 · Tuấn · 22/11/2026 — app/core/migrations.py).

Mỗi test dùng một file SQLite riêng. Chạy:  python -m pytest tests/test_migrations.py -v
"""

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

import app.models  # noqa: F401
from alembic import command
from app.core import migrations
from app.core.database import Base


@pytest.fixture()
def engine(tmp_path):
    eng = create_engine(f"sqlite:///{tmp_path / 'db.sqlite'}")
    yield eng
    eng.dispose()


def head() -> str:
    with create_engine("sqlite://").connect() as conn:
        return ScriptDirectory.from_config(migrations._config(conn)).get_current_head()


def test_fresh_database_is_created_and_stamped_head(engine):
    assert migrations.run_migrations(engine) == "fresh"
    assert migrations.current_revision(engine) == head()
    assert {"users", "review_attempts", "skills"} <= set(inspect(engine).get_table_names())


def test_existing_database_without_alembic_is_stamped_baseline_then_upgraded(engine):
    # Máy cả nhóm ngày 21/11: 24 bảng (= bản mốc) do create_all tạo, CHƯA có bảng alembic_version
    with engine.begin() as conn:
        command.upgrade(migrations._config(conn), migrations.BASELINE)
        conn.execute(text("DROP TABLE alembic_version"))
    assert "skill_id" not in {c["name"] for c in inspect(engine).get_columns("review_attempts")}

    assert migrations.run_migrations(engine) == "baseline"
    assert migrations.current_revision(engine) == head()
    assert {"skill_id", "path_id"} <= {c["name"] for c in inspect(engine).get_columns("review_attempts")}


def test_running_again_is_safe(engine):
    migrations.run_migrations(engine)
    assert migrations.run_migrations(engine) == "upgrade"
    assert migrations.current_revision(engine) == head()


def test_migrations_from_empty_match_models(engine):
    """Chặn quên migration: chạy toàn bộ migration trên DB trống phải ra đúng bảng / cột / index / khóa của model.
    Không so KIỂU cột: SQLite không có UUID (đọc ra NUMERIC) → nhiễu; kiểu đã kiểm trên PostgreSQL (0 khác biệt)."""
    with engine.begin() as conn:
        command.upgrade(migrations._config(conn), "head")
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn, opts={"compare_type": False}), Base.metadata)
    assert diff == []


# ─────────────── G2b · D1–D7 ───────────────


def _seed(conn):
    conn.execute(text("PRAGMA foreign_keys=ON"))
    conn.execute(text("INSERT INTO users (user_id, email, full_name, hashed_password) VALUES (1, 'a@x.vn', 'A', 'x')"))
    conn.execute(text("INSERT INTO courses (course_id, title) VALUES (10, 'Khóa')"))
    conn.execute(text("INSERT INTO skills (skill_id, skill, is_active) VALUES (20, 'Python', 1)"))


def _attempt(conn, course_id, skill_id, status="in_progress"):
    conn.execute(
        text("INSERT INTO review_attempts (user_id, course_id, skill_id, status) VALUES (1, :c, :s, :st)"),
        {"c": course_id, "s": skill_id, "st": status},
    )


def test_attempt_belongs_to_exactly_one_of_course_or_skill(engine):
    from sqlalchemy.exc import IntegrityError

    migrations.run_migrations(engine)
    with engine.begin() as conn:
        _seed(conn)
        _attempt(conn, 10, None)  # theo khóa
        _attempt(conn, None, 20)  # theo kỹ năng
    for course_id, skill_id in ((10, 20), (None, None)):
        with pytest.raises(IntegrityError), engine.begin() as conn:
            _attempt(conn, course_id, skill_id, status="graded")


def test_one_in_progress_attempt_per_user_and_skill(engine):
    from sqlalchemy.exc import IntegrityError

    migrations.run_migrations(engine)
    with engine.begin() as conn:
        _seed(conn)
        _attempt(conn, None, 20)
        _attempt(conn, None, 20, status="graded")  # lượt đã chấm không tính
    with pytest.raises(IntegrityError), engine.begin() as conn:
        _attempt(conn, None, 20)


def test_auto_approved_status_is_allowed(engine):
    from sqlalchemy.exc import IntegrityError

    migrations.run_migrations(engine)
    insert_q = text(
        "INSERT INTO review_questions (question_id, skill_id, type, level, content, options, correct_index, source,"
        " is_active) VALUES (:q, 20, 'mcq', 'recognize', 'Q', '[\"a\",\"b\",\"c\",\"d\"]', 0, 'ai', 1)"
    )
    insert_meta = text(
        "INSERT INTO review_question_meta (question_id, family_id, review_status, ai_check) VALUES (:q, :q, :st, :c)"
    )
    with engine.begin() as conn:
        _seed(conn)
        conn.execute(insert_q, {"q": 1})
        conn.execute(insert_meta, {"q": 1, "st": "auto_approved", "c": '{"passed": true}'})
    with pytest.raises(IntegrityError), engine.begin() as conn:
        conn.execute(insert_q, {"q": 2})
        conn.execute(insert_meta, {"q": 2, "st": "lung_tung", "c": None})


def test_downgrade_then_upgrade_again(engine):
    migrations.run_migrations(engine)
    with engine.begin() as conn:
        command.downgrade(migrations._config(conn), migrations.BASELINE)
    assert "skill_id" not in {c["name"] for c in inspect(engine).get_columns("review_attempts")}
    with engine.begin() as conn:
        command.upgrade(migrations._config(conn), "head")
    assert migrations.current_revision(engine) == head()
