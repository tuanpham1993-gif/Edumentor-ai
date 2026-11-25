"""Mentor duyệt câu ôn tập AI soạn (Tuấn · G3f, 25/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md D19–D23).

- users: CHECK vai trò thêm 'mentor' (D22 — admin gán vai trò cho tài khoản có sẵn).
- Bảng mới review_question_reports: mentor phản ánh lỗi câu (mỗi câu tối đa MỘT phản ánh đang mở).
- review_question_meta + disabled_reason ('mentor_report'), mentor_status ('passed' | 'reported'), mentor_by, mentor_at.
- notifications: CHECK loại thông báo thêm 'review_report' (chuông báo mentor khi admin xử lý phản ánh).
  (sync_notification_types lúc khởi động cũng tự làm việc này; migration ghi lại để DB chỉ dùng Alembic vẫn đúng.)

Revision ID: 0005_question_reports
Revises: 0004_knowledge_source
Create Date: 2026-11-24 (viết lại 25/11 theo mô hình mentor — bản 24/11 chưa commit)
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_question_reports"
down_revision: str | Sequence[str] | None = "0004_knowledge_source"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OLD_TYPES = ("review_graded", "course_completed", "password_changed", "welcome", "review_due")
NEW_TYPES = (*OLD_TYPES, "review_report")
OLD_ROLES = ("student", "admin")
NEW_ROLES = ("student", "mentor", "admin")


def _in(column: str, values: tuple[str, ...]) -> str:
    return f"{column} IN (" + ", ".join(f"'{v}'" for v in values) + ")"


def upgrade() -> None:
    with op.batch_alter_table("users") as t:
        t.drop_constraint("ck_users_role", type_="check")
        t.create_check_constraint("ck_users_role", _in("role", NEW_ROLES))

    op.create_table(
        "review_question_reports",
        sa.Column("report_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=20), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=10), server_default="open", nullable=False),
        sa.Column("admin_note", sa.String(length=500), nullable=True),
        sa.Column("resolved_by", sa.Integer(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "reason IN ('wrong_answer', 'ambiguous', 'wrong_knowledge', 'bad_rubric', 'other')",
            name="ck_review_question_reports_reason",
        ),
        sa.CheckConstraint("status IN ('open', 'resolved', 'dismissed')", name="ck_review_question_reports_status"),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["review_questions.question_id"],
            ondelete="CASCADE",
            name="review_question_reports_question_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.user_id"], ondelete="CASCADE", name="review_question_reports_user_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["resolved_by"], ["users.user_id"], ondelete="SET NULL", name="review_question_reports_resolved_by_fkey"
        ),
        sa.PrimaryKeyConstraint("report_id"),
    )
    op.create_index("ix_review_question_reports_question_id", "review_question_reports", ["question_id"])
    op.create_index("ix_review_question_reports_user_id", "review_question_reports", ["user_id"])
    op.create_index(
        "uq_review_question_reports_one_open",
        "review_question_reports",
        ["question_id"],
        unique=True,
        postgresql_where=sa.text("status = 'open'"),
        sqlite_where=sa.text("status = 'open'"),
    )

    with op.batch_alter_table("review_question_meta") as t:
        t.add_column(sa.Column("disabled_reason", sa.String(length=20), nullable=True))
        t.add_column(sa.Column("mentor_status", sa.String(length=10), nullable=True))
        t.add_column(sa.Column("mentor_by", sa.Integer(), nullable=True))
        t.add_column(sa.Column("mentor_at", sa.DateTime(timezone=True), nullable=True))
        t.create_foreign_key(
            "review_question_meta_mentor_by_fkey", "users", ["mentor_by"], ["user_id"], ondelete="SET NULL"
        )
        t.create_check_constraint(
            "ck_review_question_meta_mentor_status", "mentor_status IS NULL OR mentor_status IN ('passed', 'reported')"
        )

    with op.batch_alter_table("notifications") as t:
        t.drop_constraint("ck_notifications_type", type_="check")
        t.create_check_constraint("ck_notifications_type", _in("type", NEW_TYPES))


def downgrade() -> None:
    op.execute("DELETE FROM notifications WHERE type = 'review_report'")
    with op.batch_alter_table("notifications") as t:
        t.drop_constraint("ck_notifications_type", type_="check")
        t.create_check_constraint("ck_notifications_type", _in("type", OLD_TYPES))

    is_sqlite = op.get_bind().dialect.name == "sqlite"
    with op.batch_alter_table("review_question_meta") as t:
        t.drop_constraint("ck_review_question_meta_mentor_status", type_="check")
        if not is_sqlite:  # SQLite không lưu tên FK — batch dựng lại bảng là đủ
            t.drop_constraint("review_question_meta_mentor_by_fkey", type_="foreignkey")
        t.drop_column("mentor_at")
        t.drop_column("mentor_by")
        t.drop_column("mentor_status")
        t.drop_column("disabled_reason")

    op.drop_index("uq_review_question_reports_one_open", table_name="review_question_reports")
    op.drop_index("ix_review_question_reports_user_id", table_name="review_question_reports")
    op.drop_index("ix_review_question_reports_question_id", table_name="review_question_reports")
    op.drop_table("review_question_reports")

    op.execute("UPDATE users SET role = 'student' WHERE role = 'mentor'")
    with op.batch_alter_table("users") as t:
        t.drop_constraint("ck_users_role", type_="check")
        t.create_check_constraint("ck_users_role", _in("role", OLD_ROLES))
