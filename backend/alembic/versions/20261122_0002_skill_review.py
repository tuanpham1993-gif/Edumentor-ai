"""Ôn tập theo kỹ năng — D1–D7 (Tuấn · G2b, 22/11/2026 — docs/guide.md mục 7.2).

D1  review_attempts      + skill_id  NULL FK→skills (CASCADE)                lượt ôn theo kỹ năng
D2  review_attempts      + path_id   NULL FK→learning_paths.record_id (SET NULL) quay lại đúng node lộ trình
D3  review_attempts      course_id cho phép NULL + CHECK đúng một trong course_id / skill_id
D4  review_attempts      index skill_id; UNIQUE (user_id, skill_id) WHERE in_progress
D5  review_questions     index (skill_id, type, level) WHERE is_active      đếm "đủ câu chưa"
D6  review_question_meta + ai_check JSON NULL                              kết quả cổng kiểm tra
D7  review_question_meta review_status: VARCHAR(10) → (20) + 'auto_approved' trong CHECK

Viết tay (autogenerate không thấy thay đổi CHECK, FK không tên → downgrade lỗi). Tên FK theo kiểu PostgreSQL tự đặt
(<bảng>_<cột>_fkey) để database tạo bằng create_all và database nâng cấp bằng migration giống hệt nhau.
batch_alter_table: PostgreSQL chạy ALTER thường; SQLite (test) tự dựng lại bảng.

Revision ID: 0002_skill_review
Revises: 0001_baseline
Create Date: 2026-11-22
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_skill_review"
down_revision: str | Sequence[str] | None = "0001_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

IN_PROGRESS_SKILL = sa.text("status = 'in_progress' AND skill_id IS NOT NULL")
STATUS_OLD = "review_status IN ('pending', 'approved', 'rejected')"
STATUS_NEW = "review_status IN ('pending', 'approved', 'rejected', 'auto_approved')"


def upgrade() -> None:
    with op.batch_alter_table("review_attempts") as t:
        t.add_column(sa.Column("skill_id", sa.Integer(), nullable=True))  # D1
        t.add_column(sa.Column("path_id", sa.Integer(), nullable=True))  # D2
        t.create_foreign_key("review_attempts_skill_id_fkey", "skills", ["skill_id"], ["skill_id"], ondelete="CASCADE")
        t.create_foreign_key(
            "review_attempts_path_id_fkey", "learning_paths", ["path_id"], ["record_id"], ondelete="SET NULL"
        )
        t.alter_column("course_id", existing_type=sa.Integer(), nullable=True)  # D3
        t.create_check_constraint("ck_review_attempts_target", "(course_id IS NULL) <> (skill_id IS NULL)")
        t.create_index("ix_review_attempts_skill_id", ["skill_id"])  # D4
        t.create_index(
            "uq_review_attempts_one_in_progress_skill",
            ["user_id", "skill_id"],
            unique=True,
            postgresql_where=IN_PROGRESS_SKILL,
            sqlite_where=IN_PROGRESS_SKILL,
        )

    op.create_index(  # D5
        "ix_review_questions_skill_type_level_active",
        "review_questions",
        ["skill_id", "type", "level"],
        postgresql_where=sa.text("is_active"),
        sqlite_where=sa.text("is_active"),
    )

    with op.batch_alter_table("review_question_meta") as t:
        t.add_column(sa.Column("ai_check", sa.JSON(none_as_null=True), nullable=True))  # D6
        t.alter_column(  # D7
            "review_status",
            existing_type=sa.String(10),
            type_=sa.String(20),
            existing_nullable=False,
            existing_server_default="approved",
        )
        t.drop_constraint("ck_review_question_meta_status", type_="check")
        t.create_check_constraint("ck_review_question_meta_status", STATUS_NEW)


def downgrade() -> None:
    """Quay về 0001. MẤT dữ liệu ôn theo kỹ năng: xóa lượt theo kỹ năng, câu 'auto_approved' chuyển 'pending'."""
    op.execute("UPDATE review_question_meta SET review_status = 'pending' WHERE review_status = 'auto_approved'")
    with op.batch_alter_table("review_question_meta") as t:
        t.drop_constraint("ck_review_question_meta_status", type_="check")
        t.create_check_constraint("ck_review_question_meta_status", STATUS_OLD)
        t.alter_column(
            "review_status",
            existing_type=sa.String(20),
            type_=sa.String(10),
            existing_nullable=False,
            existing_server_default="approved",
        )
        t.drop_column("ai_check")

    op.drop_index("ix_review_questions_skill_type_level_active", table_name="review_questions")

    op.execute("DELETE FROM review_attempts WHERE course_id IS NULL")
    with op.batch_alter_table("review_attempts") as t:
        t.drop_index("uq_review_attempts_one_in_progress_skill")
        t.drop_index("ix_review_attempts_skill_id")
        t.drop_constraint("ck_review_attempts_target", type_="check")
        t.alter_column("course_id", existing_type=sa.Integer(), nullable=False)
        if op.get_bind().dialect.name != "sqlite":  # SQLite không lưu tên FK; dựng lại bảng thì FK đi cùng cột
            t.drop_constraint("review_attempts_path_id_fkey", type_="foreignkey")
            t.drop_constraint("review_attempts_skill_id_fkey", type_="foreignkey")
        t.drop_column("path_id")
        t.drop_column("skill_id")
