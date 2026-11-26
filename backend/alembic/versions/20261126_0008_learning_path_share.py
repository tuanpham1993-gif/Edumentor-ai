"""Chia sẻ lộ trình — các cột mới của learning_paths (tính năng của Khôi, nhánh Khoi/ShareNotePath; migration Tuấn viết
khi gộp 26/11/2026).

- learning_paths + is_shared, share_code (duy nhất), shared_at, clone_count, cloned_from_id (→ learning_paths, SET NULL)
- index ix_learning_paths_share_code (duy nhất), ix_learning_paths_student_id

An toàn cho máy ĐÃ chạy script tay `backend/scripts/migrate_learning_path_share.py`: cột / index có rồi thì bỏ qua;
ràng buộc UNIQUE `learning_paths_share_code_key` do script tạo được đổi thành index duy nhất như model.

Revision ID: 0008_learning_path_share
Revises: 0007_generation_job_detail
Create Date: 2026-11-26
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008_learning_path_share"
down_revision: str | Sequence[str] | None = "0007_generation_job_detail"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE = "learning_paths"
SCRIPT_UNIQUE = "learning_paths_share_code_key"  # tên PostgreSQL tự đặt khi script tay tạo UNIQUE
FK_NAME = "learning_paths_cloned_from_id_fkey"
COLUMNS = (
    sa.Column("is_shared", sa.Boolean(), server_default=sa.false(), nullable=False),
    sa.Column("share_code", sa.String(length=50), nullable=True),
    sa.Column("shared_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("clone_count", sa.Integer(), server_default="0", nullable=False),
    sa.Column("cloned_from_id", sa.Integer(), nullable=True),
)


def _state():
    insp = sa.inspect(op.get_bind())
    return (
        {c["name"] for c in insp.get_columns(TABLE)},
        {i["name"] for i in insp.get_indexes(TABLE)},
        {u["name"] for u in insp.get_unique_constraints(TABLE)},
        {f["name"] for f in insp.get_foreign_keys(TABLE)},
    )


def upgrade() -> None:
    columns, indexes, uniques, fks = _state()
    with op.batch_alter_table(TABLE) as t:
        for col in COLUMNS:
            if col.name not in columns:
                t.add_column(col.copy())
        if "cloned_from_id" not in columns and FK_NAME not in fks:
            t.create_foreign_key(FK_NAME, TABLE, ["cloned_from_id"], ["record_id"], ondelete="SET NULL")
        if SCRIPT_UNIQUE in uniques:
            t.drop_constraint(SCRIPT_UNIQUE, type_="unique")
    if "ix_learning_paths_share_code" not in indexes:
        op.create_index("ix_learning_paths_share_code", TABLE, ["share_code"], unique=True)
    if "ix_learning_paths_student_id" not in indexes:
        op.create_index("ix_learning_paths_student_id", TABLE, ["student_id"])


def downgrade() -> None:
    op.drop_index("ix_learning_paths_student_id", table_name=TABLE)
    op.drop_index("ix_learning_paths_share_code", table_name=TABLE)
    # Khóa ngoại tìm theo CỘT: model khai báo không tên → database tạo từ model (SQLite) có khóa ngoại không tên;
    # khi đó bỏ cột trong batch là đủ (SQLite dựng lại bảng không có cột / khóa ngoại đó).
    fk_names = [f["name"] for f in sa.inspect(op.get_bind()).get_foreign_keys(TABLE)
                if f["constrained_columns"] == ["cloned_from_id"] and f["name"]]  # fmt: skip
    with op.batch_alter_table(TABLE) as t:
        for fk in fk_names:
            t.drop_constraint(fk, type_="foreignkey")
        for name in ("cloned_from_id", "clone_count", "shared_at", "share_code", "is_shared"):
            t.drop_column(name)
