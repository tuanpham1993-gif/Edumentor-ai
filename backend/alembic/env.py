"""Môi trường chạy Alembic (Tuấn · G2a, 22/11/2026).

- Địa chỉ DB: DATABASE_URL (app.core.config) — không ghi trong alembic.ini.
- target_metadata = Base.metadata (nạp toàn bộ model qua `import app.models`) → `--autogenerate` so model với DB.
- Gọi từ code (app/core/migrations.py, test) thì truyền sẵn kết nối qua config.attributes["connection"].
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

import app.models  # noqa: F401 — đăng ký mọi bảng vào Base.metadata
from alembic import context
from app.core.config import settings
from app.core.database import Base

config = context.config
if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url") or settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _run(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=connection.dialect.name == "sqlite",  # SQLite (test) không ALTER cột được → batch
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connection = config.attributes.get("connection")
    if connection is not None:
        _run(connection)
        return
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url") or settings.DATABASE_URL
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as conn:
        _run(conn)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
