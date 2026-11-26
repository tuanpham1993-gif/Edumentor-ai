"""Kho đoạn tri thức — nguồn gốc đoạn (Tuấn · G3a, 24/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md mục 7.1).

knowledge_chunks (bảng của module 09) thêm: source manual / ai / admin (+ CHECK), source_course_ids, model,
prompt_version, updated_by (FK users SET NULL), updated_at. Đoạn có sẵn (nhóm soạn) tự nhận source = 'manual'.

Revision ID: 0004_knowledge_source
Revises: 0003_skill_scopes
Create Date: 2026-11-24
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_knowledge_source"
down_revision: str | Sequence[str] | None = "0003_skill_scopes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("knowledge_chunks") as t:
        t.add_column(sa.Column("source", sa.String(length=10), server_default="manual", nullable=False))
        t.add_column(sa.Column("source_course_ids", sa.JSON(none_as_null=True), nullable=True))
        t.add_column(sa.Column("model", sa.String(length=100), nullable=True))
        t.add_column(sa.Column("prompt_version", sa.String(length=30), nullable=True))
        t.add_column(sa.Column("updated_by", sa.Integer(), nullable=True))
        t.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
        t.create_foreign_key(
            "knowledge_chunks_updated_by_fkey", "users", ["updated_by"], ["user_id"], ondelete="SET NULL"
        )
        t.create_check_constraint("ck_knowledge_chunks_source", "source IN ('manual', 'ai', 'admin')")


def downgrade() -> None:
    with op.batch_alter_table("knowledge_chunks") as t:
        t.drop_constraint("ck_knowledge_chunks_source", type_="check")
        if op.get_bind().dialect.name != "sqlite":  # SQLite không lưu tên FK; dựng lại bảng thì FK đi cùng cột
            t.drop_constraint("knowledge_chunks_updated_by_fkey", type_="foreignkey")
        for column in ("updated_at", "updated_by", "prompt_version", "model", "source_course_ids", "source"):
            t.drop_column(column)
