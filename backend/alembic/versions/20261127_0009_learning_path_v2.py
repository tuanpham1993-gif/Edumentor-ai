"""Lộ trình AI v2 — 4 bảng mới (tính năng của Hòa, nhánh Hoa-update; migration Tuấn viết khi gộp 27/11/2026).

- certifications, technical_domains: danh sách chọn cho form "Tạo lộ trình" (learning_path2)
- learner_profiles: ảnh chụp hồ sơ người học của mỗi lộ trình AI v2 (1–1 với learning_paths)
- learning_path_graphs: đồ thị AI sinh ra khi người học xác nhận lộ trình (1–1 với learning_paths, learner_profiles)

An toàn cho máy ĐÃ chạy server nhánh Hoa-update (create_all đã tạo bảng): bảng có rồi thì bỏ qua.

Revision ID: 0009_learning_path_v2
Revises: 0008_learning_path_share
Create Date: 2026-11-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009_learning_path_v2"
down_revision: str | Sequence[str] | None = "0008_learning_path_share"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CAREER_LEVELS = ("beginner", "intern", "fresher", "junior", "middle", "senior",
                 "lead", "architect", "manager", "career_switcher", "student")


def _in(col: str, values: tuple[str, ...]) -> str:
    return f"{col} IN (" + ", ".join(f"'{v}'" for v in values) + ")"


def _created_at() -> sa.Column:
    return sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)


def upgrade() -> None:
    have = set(sa.inspect(op.get_bind()).get_table_names())

    if "certifications" not in have:
        op.create_table(
            "certifications",
            sa.Column("cert_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("issuer", sa.String(length=100), nullable=True),
            sa.Column("aliases", sa.JSON(), nullable=False),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
            sa.PrimaryKeyConstraint("cert_id"),
            sa.UniqueConstraint("name"),
        )

    if "technical_domains" not in have:
        op.create_table(
            "technical_domains",
            sa.Column("domain_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
            sa.PrimaryKeyConstraint("domain_id"),
            sa.UniqueConstraint("name"),
        )

    if "learner_profiles" not in have:
        op.create_table(
            "learner_profiles",
            sa.Column("profile_id", sa.Integer(), nullable=False),
            sa.Column("path_id", sa.Integer(), nullable=False),
            sa.Column("original_query", sa.Text(), nullable=False),
            sa.Column("goal_type", sa.String(length=20), nullable=False),
            sa.Column("target_role_raw", sa.String(length=255), nullable=True),
            sa.Column("role_id", sa.Integer(), nullable=True),
            sa.Column("role_name", sa.String(length=150), nullable=True),
            sa.Column("target_technologies", sa.JSON(), nullable=False),
            sa.Column("career_level", sa.String(length=30), nullable=True),
            sa.Column("current_job_title", sa.String(length=255), nullable=True),
            sa.Column("industry", sa.String(length=255), nullable=True),
            sa.Column("relevant_it_work_experience", sa.String(length=50), nullable=True),
            sa.Column("technical_domains", sa.JSON(), nullable=False),
            sa.Column("certifications", sa.JSON(), nullable=False),
            sa.Column("previous_job_roles", sa.JSON(), nullable=False),
            sa.Column("skill_profiles", sa.JSON(), nullable=False),
            sa.Column("practical_experiences", sa.JSON(), nullable=False),
            sa.Column("study_time_value", sa.Float(), nullable=True),
            sa.Column("study_time_unit", sa.String(length=10), nullable=True),
            sa.Column("study_time_period", sa.String(length=10), nullable=True),
            sa.Column("deadline_type", sa.String(length=20), nullable=True),
            sa.Column("deadline_target_date", sa.Date(), nullable=True),
            sa.Column("deadline_duration_value", sa.Float(), nullable=True),
            sa.Column("deadline_duration_unit", sa.String(length=10), nullable=True),
            _created_at(),
            sa.CheckConstraint("goal_type IN ('career', 'project')", name="ck_learner_profiles_goal_type"),
            sa.CheckConstraint("career_level IS NULL OR " + _in("career_level", CAREER_LEVELS),
                               name="ck_learner_profiles_career_level"),
            sa.CheckConstraint(
                "(study_time_value IS NULL AND study_time_unit IS NULL AND study_time_period IS NULL) OR "
                "(study_time_value > 0 AND study_time_unit IN ('hours', 'minutes') "
                "AND study_time_period IN ('per_day', 'per_week'))",
                name="ck_learner_profiles_study_time",
            ),
            sa.CheckConstraint(
                "(deadline_type IS NULL AND deadline_target_date IS NULL "
                " AND deadline_duration_value IS NULL AND deadline_duration_unit IS NULL) OR "
                "(deadline_type = 'fixed_date' AND deadline_target_date IS NOT NULL "
                " AND deadline_duration_value IS NULL AND deadline_duration_unit IS NULL) OR "
                "(deadline_type = 'relative_duration' AND deadline_target_date IS NULL "
                " AND deadline_duration_value > 0 "
                " AND deadline_duration_unit IN ('days', 'weeks', 'months', 'years'))",
                name="ck_learner_profiles_deadline",
            ),
            sa.ForeignKeyConstraint(["path_id"], ["learning_paths.record_id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("profile_id"),
            sa.UniqueConstraint("path_id"),
        )
        op.create_index("ix_learner_profiles_role_id", "learner_profiles", ["role_id"])

    if "learning_path_graphs" not in have:
        op.create_table(
            "learning_path_graphs",
            sa.Column("graph_id", sa.Integer(), nullable=False),
            sa.Column("path_id", sa.Integer(), nullable=False),
            sa.Column("profile_id", sa.Integer(), nullable=False),
            sa.Column("role_id", sa.Integer(), nullable=True),
            sa.Column("targets", sa.JSON(), nullable=False),
            sa.Column("node_states", sa.JSON(), nullable=False),
            sa.Column("layer", sa.JSON(), nullable=False),
            sa.Column("retrieval_status", sa.String(length=20), nullable=False),
            sa.Column("warnings", sa.JSON(), nullable=False),
            sa.Column("generator_version", sa.String(length=30), nullable=False),
            _created_at(),
            sa.ForeignKeyConstraint(["path_id"], ["learning_paths.record_id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["profile_id"], ["learner_profiles.profile_id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("graph_id"),
            sa.UniqueConstraint("path_id"),
            sa.UniqueConstraint("profile_id"),
        )


def downgrade() -> None:
    op.drop_table("learning_path_graphs")
    op.drop_index("ix_learner_profiles_role_id", table_name="learner_profiles")
    op.drop_table("learner_profiles")
    op.drop_table("technical_domains")
    op.drop_table("certifications")
