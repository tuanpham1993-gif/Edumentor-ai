"""Việc AI soạn câu ở nền + nguồn câu (Tuấn · G3d, 25/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md D9, D24, D26, mục 7.5).

- Bảng mới review_generation_jobs (mỗi kỹ năng tối đa MỘT việc đang chờ / chạy — index duy nhất có điều kiện).
- review_question_meta + origin ('on_demand' | 'nightly').

Revision ID: 0006_generation_jobs
Revises: 0005_question_reports
Create Date: 2026-11-25
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_generation_jobs"
down_revision: str | Sequence[str] | None = "0005_question_reports"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ACTIVE = sa.text("status IN ('queued', 'running')")


def upgrade() -> None:
    op.create_table(
        "review_generation_jobs",
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=10), server_default="queued", nullable=False),
        sa.Column("step", sa.Integer(), server_default="0", nullable=False),
        sa.Column("requested_by", sa.Integer(), nullable=True),
        sa.Column("error", sa.String(length=500), nullable=True),
        sa.Column("saved", sa.Integer(), server_default="0", nullable=False),
        sa.Column("calls", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("kind IN ('exam', 'topup', 'nightly')", name="ck_review_generation_jobs_kind"),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'done', 'failed')", name="ck_review_generation_jobs_status"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.skill_id"], ondelete="CASCADE", name="review_generation_jobs_skill_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["requested_by"], ["users.user_id"], ondelete="SET NULL", name="review_generation_jobs_requested_by_fkey"
        ),
        sa.PrimaryKeyConstraint("job_id"),
    )
    op.create_index("ix_review_generation_jobs_skill_id", "review_generation_jobs", ["skill_id"])
    op.create_index(
        "uq_review_generation_jobs_one_active",
        "review_generation_jobs",
        ["skill_id"],
        unique=True,
        postgresql_where=ACTIVE,
        sqlite_where=ACTIVE,
    )
    with op.batch_alter_table("review_question_meta") as t:
        t.add_column(sa.Column("origin", sa.String(length=10), nullable=True))
        t.create_check_constraint(
            "ck_review_question_meta_origin", "origin IS NULL OR origin IN ('on_demand', 'nightly')"
        )


def downgrade() -> None:
    with op.batch_alter_table("review_question_meta") as t:
        t.drop_constraint("ck_review_question_meta_origin", type_="check")
        t.drop_column("origin")
    op.drop_index("uq_review_generation_jobs_one_active", table_name="review_generation_jobs")
    op.drop_index("ix_review_generation_jobs_skill_id", table_name="review_generation_jobs")
    op.drop_table("review_generation_jobs")
