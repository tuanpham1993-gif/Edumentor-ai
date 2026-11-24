"""Phạm vi ôn tập theo kỹ năng — bảng review_skill_scopes (Tuấn · G3.0, 24/11/2026).

Mỗi kỹ năng một nhãn open / closed / unsure: AI có được tự soạn câu ôn tập cho kỹ năng đó không (docs/guide.md Q8).
Chỉ TẠO BẢNG MỚI, không đụng bảng có sẵn. Tên FK để PostgreSQL tự đặt (<bảng>_<cột>_fkey) — giống create_all.

Revision ID: 0003_skill_scopes
Revises: 0002_skill_review
Create Date: 2026-11-24
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# Ghi cứng (không import từ model): migration là ảnh chụp lúc viết, model đổi sau này thì viết migration mới.
LABELS = ("open", "closed", "unsure")
CATEGORIES = ("programming", "software_tools", "data_bi", "infra_security", "software_process", "math_science",
              "business_domain", "soft_skill", "specialized_domain", "other")  # fmt: skip
SOURCES = ("ai", "admin")

revision: str = "0003_skill_scopes"
down_revision: str | Sequence[str] | None = "0002_skill_review"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _in(column: str, values: tuple[str, ...]) -> str:
    return f"{column} IN ({', '.join(repr(v) for v in values)})"


def upgrade() -> None:
    op.create_table(
        "review_skill_scopes",
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=10), nullable=False),
        sa.Column("category", sa.String(length=30), server_default="other", nullable=False),
        sa.Column("reason", sa.String(length=200), nullable=True),
        sa.Column("source", sa.String(length=10), server_default="ai", nullable=False),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("prompt_version", sa.String(length=30), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(_in("label", LABELS), name="ck_review_skill_scopes_label"),
        sa.CheckConstraint(_in("category", CATEGORIES), name="ck_review_skill_scopes_category"),
        sa.CheckConstraint(_in("source", SOURCES), name="ck_review_skill_scopes_source"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.skill_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.user_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("skill_id"),
    )


def downgrade() -> None:
    op.drop_table("review_skill_scopes")
