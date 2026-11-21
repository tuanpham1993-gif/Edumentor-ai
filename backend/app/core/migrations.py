"""Tự cập nhật cấu trúc database lúc backend khởi động (Tuấn · G2a, 22/11/2026 — docs/guide.md Q7, cách A).

Cả nhóm và Docker KHÔNG phải gõ lệnh alembic. Mỗi lần khởi động xét trạng thái database:

  có bảng alembic_version              → upgrade head (chạy migration còn thiếu)
  trống (chưa có bảng users)           → create_all + stamp head (model đã là bản mới nhất)
  có bảng nhưng chưa có Alembic        → stamp 0001_baseline (24 bảng 21/11) rồi upgrade head
  sau cùng, mọi trường hợp             → create_all: bảng MỚI của thành viên chưa viết migration vẫn được tạo như cũ

Thay đổi bảng CÓ SẴN (thêm / sửa cột, index, CHECK) phải viết migration trong alembic/versions — create_all không
sửa bảng đã có. Chạy lại nhiều lần vẫn an toàn.
"""

import logging
from pathlib import Path

from alembic.config import Config
from sqlalchemy import inspect, text

from alembic import command

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
BASELINE = "0001_baseline"
MARKER_TABLE = "users"  # có bảng này = database đã được create_all trước khi dùng Alembic
LOCK_ID = 2026_0911  # khóa PostgreSQL: hai tiến trình khởi động cùng lúc không migrate chồng nhau


def _config(conn) -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    cfg.attributes["connection"] = conn
    cfg.attributes["configure_logger"] = False  # giữ cấu hình log của ứng dụng
    return cfg


def run_migrations(bind) -> str:
    """Trả việc đã làm: "upgrade" | "fresh" | "baseline". Lỗi thì ném ra (người gọi quyết định)."""
    import app.models  # noqa: F401 — đăng ký mọi bảng
    from app.core.database import Base

    with bind.begin() as conn:
        if conn.dialect.name == "postgresql":
            conn.execute(text("SELECT pg_advisory_xact_lock(:id)"), {"id": LOCK_ID})
        tables = set(inspect(conn).get_table_names())
        cfg = _config(conn)
        if "alembic_version" in tables:
            command.upgrade(cfg, "head")
            action = "upgrade"
        elif MARKER_TABLE not in tables:
            Base.metadata.create_all(conn)
            command.stamp(cfg, "head")
            action = "fresh"
        else:
            command.stamp(cfg, BASELINE)
            command.upgrade(cfg, "head")
            action = "baseline"
        Base.metadata.create_all(conn)
    return action


def current_revision(bind) -> str | None:
    from alembic.migration import MigrationContext

    with bind.connect() as conn:
        return MigrationContext.configure(conn).get_current_revision()
