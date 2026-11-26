"""Chi tiết việc AI soạn câu: lý do câu bị loại theo từng vòng (Tuấn · 26/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md mục 7.7).

- review_generation_jobs + detail (JSON): {"rounds": [{step, kind, need, passed, saved, calls, rejected: {nhóm: số câu},
  examples: [lý do mẫu]}], "chunks_added": n}. Trước đây lý do chỉ ghi log → soạn đề thất bại phải đoán nguyên nhân.

Revision ID: 0007_generation_job_detail
Revises: 0006_generation_jobs
Create Date: 2026-11-26
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_generation_job_detail"
down_revision: str | Sequence[str] | None = "0006_generation_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("review_generation_jobs") as t:
        t.add_column(sa.Column("detail", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("review_generation_jobs") as t:
        t.drop_column("detail")
