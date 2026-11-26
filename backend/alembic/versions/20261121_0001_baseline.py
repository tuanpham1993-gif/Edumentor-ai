"""Bản mốc: 24 bảng đúng như create_all tạo ở mọi máy ngày 21/11/2026 (Tuấn · G2a).

Sinh bằng `alembic revision --autogenerate` trên database trống; database thật (máy Tuấn) so với model: 0 khác biệt.
- Database đã có bảng nhưng chưa có Alembic → app/core/migrations.py tự `stamp` bản này (không chạy upgrade()).
- Database trống → create_all + `stamp head`. upgrade() ở đây chỉ dùng khi tự chạy `alembic upgrade head` trên DB trống.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-11-21 22:18:50
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = '0001_baseline'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('courses',
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('num_enrolled', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('num_reviews', sa.Integer(), nullable=True),
    sa.Column('instructor', sa.String(length=255), nullable=True),
    sa.Column('organization', sa.String(length=255), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('modules', sa.String(length=100), nullable=True),
    sa.Column('level', sa.String(length=20), nullable=True),
    sa.Column('schedule', sa.String(length=255), nullable=True),
    sa.Column('url', sa.String(length=500), nullable=True),
    sa.Column('image', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('rating >= 0 AND rating <= 5', name='ck_course_rating_range'),
    sa.PrimaryKeyConstraint('course_id')
    )
    op.create_index(op.f('ix_courses_course_id'), 'courses', ['course_id'], unique=False)
    op.create_table('learning_paths',
    sa.Column('record_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('original_query', sa.Text(), nullable=False),
    sa.Column('goal_type', sa.String(length=20), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.CheckConstraint("goal_type IN ('career', 'project', 'template')", name='ck_learning_path_goal_type'),
    sa.CheckConstraint("status IN ('completed', 'ongoing', 'abandoned')", name='ck_learning_path_status'),
    sa.PrimaryKeyConstraint('record_id')
    )
    op.create_index(op.f('ix_learning_paths_record_id'), 'learning_paths', ['record_id'], unique=False)
    op.create_table('skills',
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('skill', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('skill_id')
    )
    op.create_index(op.f('ix_skills_skill_id'), 'skills', ['skill_id'], unique=False)
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=20), server_default='student', nullable=False),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.CheckConstraint("role IN ('student', 'admin')", name='ck_users_role'),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_table('chat_session',
    sa.Column('session_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('session_type', sa.String(length=15), server_default='tutor', nullable=False),
    sa.Column('topic', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=10), server_default='active', nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.CheckConstraint("session_type IN ('tutor', 'learning_path')", name='ck_chat_session_type'),
    sa.CheckConstraint("status IN ('active', 'archived')", name='ck_chat_session_status'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('session_id')
    )
    op.create_table('course_skill',
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], ),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.skill_id'], ),
    sa.PrimaryKeyConstraint('course_id', 'skill_id')
    )
    op.create_table('email_preferences',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('review_reminder', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('course_suggestions', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('feedback_replies', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('feedback',
    sa.Column('feedback_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('target_type', sa.String(length=10), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.Column('skill_id', sa.Integer(), nullable=True),
    sa.Column('feedback_type', sa.String(length=100), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('image_url', sa.String(length=500), nullable=True),
    sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
    sa.Column('admin_response', sa.Text(), nullable=True),
    sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("\n            (\n                target_type = 'course'\n                AND course_id IS NOT NULL\n                AND skill_id IS NULL\n            )\n            OR\n            (\n                target_type = 'skill'\n                AND course_id IS NULL\n                AND skill_id IS NOT NULL\n            )\n            OR\n            (\n                target_type IN ('system', 'other')\n                AND course_id IS NULL\n                AND skill_id IS NULL\n            )\n            ", name='ck_feedback_target'),
    sa.CheckConstraint("status IN ('pending', 'in_review', 'resolved', 'rejected')", name='ck_feedback_status'),
    sa.CheckConstraint("target_type <> 'other' OR title IS NOT NULL", name='ck_feedback_other_title'),
    sa.CheckConstraint("target_type IN ('course', 'skill', 'system', 'other')", name='ck_feedback_target_type'),
    sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.skill_id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('feedback_id')
    )
    op.create_index(op.f('ix_feedback_feedback_id'), 'feedback', ['feedback_id'], unique=False)
    op.create_table('knowledge_chunks',
    sa.Column('chunk_id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=True),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('embedding', sa.JSON(none_as_null=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.skill_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('chunk_id'),
    sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_knowledge_chunks_skill_id'), 'knowledge_chunks', ['skill_id'], unique=False)
    op.create_table('learning_path_edges',
    sa.Column('path_id', sa.Integer(), nullable=False),
    sa.Column('from_skill_id', sa.Integer(), nullable=False),
    sa.Column('to_skill_id', sa.Integer(), nullable=False),
    sa.Column('relation_type', sa.String(length=20), nullable=False),
    sa.CheckConstraint("relation_type IN ('prerequisite', 'related', 'extension')", name='ck_learning_path_edge_relation_type'),
    sa.CheckConstraint('from_skill_id != to_skill_id', name='ck_learning_path_edge_different_skills'),
    sa.ForeignKeyConstraint(['from_skill_id'], ['skills.skill_id'], ),
    sa.ForeignKeyConstraint(['path_id'], ['learning_paths.record_id'], ),
    sa.ForeignKeyConstraint(['to_skill_id'], ['skills.skill_id'], ),
    sa.PrimaryKeyConstraint('path_id', 'from_skill_id', 'to_skill_id')
    )
    op.create_table('learning_path_nodes',
    sa.Column('path_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('node_role', sa.String(length=30), nullable=True),
    sa.Column('is_target', sa.Boolean(), nullable=False),
    sa.Column('added_by', sa.String(length=20), nullable=False),
    sa.Column('is_required', sa.Boolean(), nullable=False),
    sa.Column('display_order', sa.Integer(), nullable=False),
    sa.CheckConstraint("added_by IN ('system', 'user')", name='ck_learning_path_node_added_by'),
    sa.CheckConstraint('is_required IN (TRUE, FALSE)', name='ck_learning_path_node_is_required'),
    sa.CheckConstraint('is_target IN (TRUE, FALSE)', name='ck_learning_path_node_is_target'),
    sa.ForeignKeyConstraint(['path_id'], ['learning_paths.record_id'], ),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.skill_id'], ),
    sa.PrimaryKeyConstraint('path_id', 'skill_id')
    )
    op.create_table('notifications',
    sa.Column('notification_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=40), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('link', sa.String(length=500), nullable=True),
    sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.CheckConstraint("link IS NULL OR link LIKE '/%%'", name='ck_notifications_link_internal'),
    sa.CheckConstraint("type IN ('review_graded', 'course_completed', 'password_changed', 'welcome', 'review_due')", name='ck_notifications_type'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('notification_id')
    )
    op.create_index('ix_notifications_user_read_created', 'notifications', ['user_id', 'is_read', 'created_at'], unique=False)
    op.create_index('uq_notifications_source', 'notifications', ['user_id', 'type', 'source_id'], unique=True, postgresql_where=sa.text('source_id IS NOT NULL'), sqlite_where=sa.text('source_id IS NOT NULL'))
    op.create_table('password_reset_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_password_reset_tokens_id'), 'password_reset_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_password_reset_tokens_token_hash'), 'password_reset_tokens', ['token_hash'], unique=True)
    op.create_index(op.f('ix_password_reset_tokens_user_id'), 'password_reset_tokens', ['user_id'], unique=False)
    op.create_table('refresh_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=True)
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)
    op.create_table('review_attempts',
    sa.Column('attempt_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), server_default='in_progress', nullable=False),
    sa.Column('score', sa.Numeric(precision=4, scale=2), nullable=True),
    sa.Column('passed', sa.Boolean(), nullable=True),
    sa.Column('is_first_pass', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('trace', sa.JSON(none_as_null=True), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("status IN ('in_progress', 'grading', 'graded')", name='ck_review_attempts_status'),
    sa.CheckConstraint('score IS NULL OR (score >= 0 AND score <= 10)', name='ck_review_attempts_score'),
    sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('attempt_id')
    )
    op.create_index(op.f('ix_review_attempts_course_id'), 'review_attempts', ['course_id'], unique=False)
    op.create_index(op.f('ix_review_attempts_user_id'), 'review_attempts', ['user_id'], unique=False)
    op.create_index('uq_review_attempts_one_in_progress', 'review_attempts', ['user_id', 'course_id'], unique=True, postgresql_where=sa.text("status = 'in_progress'"), sqlite_where=sa.text("status = 'in_progress'"))
    op.create_table('review_due_reminders',
    sa.Column('reminder_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('due_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('notified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('emailed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.skill_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('reminder_id'),
    sa.UniqueConstraint('user_id', 'skill_id', 'due_at', name='uq_review_due_reminders')
    )
    op.create_index(op.f('ix_review_due_reminders_user_id'), 'review_due_reminders', ['user_id'], unique=False)
    op.create_table('skill_relation',
    sa.Column('from_skill_id', sa.Integer(), nullable=False),
    sa.Column('to_skill_id', sa.Integer(), nullable=False),
    sa.Column('relation_type', sa.String(length=20), nullable=False),
    sa.CheckConstraint("relation_type IN ('prerequisite', 'related', 'extension')", name='ck_skill_relation_type'),
    sa.CheckConstraint('from_skill_id != to_skill_id', name='ck_skill_relation_different_skills'),
    sa.ForeignKeyConstraint(['from_skill_id'], ['skills.skill_id'], ),
    sa.ForeignKeyConstraint(['to_skill_id'], ['skills.skill_id'], ),
    sa.PrimaryKeyConstraint('from_skill_id', 'to_skill_id')
    )
    op.create_table('user_courses',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('joined_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('bookmarked', 'ongoing', 'completed', 'abandoned')", name='ck_user_courses_status'),
    sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'course_id')
    )
    op.create_index(op.f('ix_user_courses_course_id'), 'user_courses', ['course_id'], unique=False)
    op.create_index('ix_user_courses_user_status_updated', 'user_courses', ['user_id', 'status', 'updated_at'], unique=False)
    op.create_table('user_profiles',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('gender', sa.String(length=10), nullable=True),
    sa.Column('hometown', sa.String(length=100), nullable=True),
    sa.Column('phone', sa.String(length=15), nullable=True),
    sa.Column('citizen_id_encrypted', sa.Text(), nullable=True),
    sa.Column('citizen_id_masked', sa.String(length=12), nullable=True),
    sa.Column('citizen_id_hash', sa.String(length=64), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("gender IS NULL OR gender IN ('male', 'female')", name='ck_user_profiles_gender'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('citizen_id_hash')
    )
    op.create_table('user_skills',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('source', sa.String(length=20), server_default='manual', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("source IN ('manual', 'course', 'review')", name='ck_user_skills_source'),
    sa.CheckConstraint("status IN ('known', 'learning')", name='ck_user_skills_status'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.skill_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'skill_id')
    )
    op.create_index(op.f('ix_user_skills_skill_id'), 'user_skills', ['skill_id'], unique=False)
    op.create_table('chat_message',
    sa.Column('message_id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('session_id', sa.UUID(), nullable=False),
    sa.Column('role', sa.String(length=10), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.CheckConstraint("role IN ('user', 'assistant')", name='ck_chat_message_role'),
    sa.ForeignKeyConstraint(['session_id'], ['chat_session.session_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('message_id')
    )
    op.create_table('review_questions',
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=True),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('chunk_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=10), nullable=False),
    sa.Column('level', sa.String(length=20), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('options', sa.JSON(none_as_null=True), nullable=True),
    sa.Column('correct_index', sa.Integer(), nullable=True),
    sa.Column('rubric', sa.JSON(none_as_null=True), nullable=True),
    sa.Column('explanation', sa.Text(), nullable=True),
    sa.Column('source', sa.String(length=10), server_default='bank', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("(type = 'mcq' AND level IN ('recognize', 'understand')) OR (type = 'essay' AND level IN ('easy', 'advanced'))", name='ck_review_questions_level'),
    sa.CheckConstraint("(type = 'mcq' AND options IS NOT NULL AND correct_index BETWEEN 0 AND 3 AND rubric IS NULL) OR (type = 'essay' AND rubric IS NOT NULL AND options IS NULL AND correct_index IS NULL)", name='ck_review_questions_shape'),
    sa.CheckConstraint("source IN ('bank', 'ai')", name='ck_review_questions_source'),
    sa.CheckConstraint("type IN ('mcq', 'essay')", name='ck_review_questions_type'),
    sa.ForeignKeyConstraint(['chunk_id'], ['knowledge_chunks.chunk_id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.skill_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('question_id'),
    sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_review_questions_chunk_id'), 'review_questions', ['chunk_id'], unique=False)
    op.create_index(op.f('ix_review_questions_skill_id'), 'review_questions', ['skill_id'], unique=False)
    op.create_table('review_answers',
    sa.Column('attempt_id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('option_order', sa.JSON(none_as_null=True), nullable=True),
    sa.Column('selected_index', sa.Integer(), nullable=True),
    sa.Column('text_answer', sa.Text(), nullable=True),
    sa.Column('max_points', sa.Numeric(precision=3, scale=1), nullable=False),
    sa.Column('points', sa.Numeric(precision=4, scale=2), nullable=True),
    sa.Column('rubric_result', sa.JSON(none_as_null=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('points IS NULL OR (points >= 0 AND points <= max_points)', name='ck_review_answers_points'),
    sa.CheckConstraint('position >= 1', name='ck_review_answers_position'),
    sa.CheckConstraint('selected_index IS NULL OR selected_index BETWEEN 0 AND 3', name='ck_review_answers_selected'),
    sa.ForeignKeyConstraint(['attempt_id'], ['review_attempts.attempt_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['question_id'], ['review_questions.question_id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('attempt_id', 'position', name='pk_review_answers'),
    sa.UniqueConstraint('attempt_id', 'question_id', name='uq_review_answers_question')
    )
    op.create_index(op.f('ix_review_answers_question_id'), 'review_answers', ['question_id'], unique=False)
    op.create_table('review_question_meta',
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('family_id', sa.Integer(), nullable=False),
    sa.Column('version', sa.Integer(), server_default='1', nullable=False),
    sa.Column('exclusion_group', sa.String(length=50), nullable=True),
    sa.Column('review_status', sa.String(length=10), server_default='approved', nullable=False),
    sa.Column('reviewed_by', sa.Integer(), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('change_note', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("review_status IN ('pending', 'approved', 'rejected')", name='ck_review_question_meta_status'),
    sa.CheckConstraint('version >= 1', name='ck_review_question_meta_version'),
    sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['question_id'], ['review_questions.question_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reviewed_by'], ['users.user_id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('question_id'),
    sa.UniqueConstraint('family_id', 'version', name='uq_review_question_meta_family_version')
    )
    op.create_index(op.f('ix_review_question_meta_exclusion_group'), 'review_question_meta', ['exclusion_group'], unique=False)
    op.create_index(op.f('ix_review_question_meta_family_id'), 'review_question_meta', ['family_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_review_question_meta_family_id'), table_name='review_question_meta')
    op.drop_index(op.f('ix_review_question_meta_exclusion_group'), table_name='review_question_meta')
    op.drop_table('review_question_meta')
    op.drop_index(op.f('ix_review_answers_question_id'), table_name='review_answers')
    op.drop_table('review_answers')
    op.drop_index(op.f('ix_review_questions_skill_id'), table_name='review_questions')
    op.drop_index(op.f('ix_review_questions_chunk_id'), table_name='review_questions')
    op.drop_table('review_questions')
    op.drop_table('chat_message')
    op.drop_index(op.f('ix_user_skills_skill_id'), table_name='user_skills')
    op.drop_table('user_skills')
    op.drop_table('user_profiles')
    op.drop_index('ix_user_courses_user_status_updated', table_name='user_courses')
    op.drop_index(op.f('ix_user_courses_course_id'), table_name='user_courses')
    op.drop_table('user_courses')
    op.drop_table('skill_relation')
    op.drop_index(op.f('ix_review_due_reminders_user_id'), table_name='review_due_reminders')
    op.drop_table('review_due_reminders')
    op.drop_index('uq_review_attempts_one_in_progress', table_name='review_attempts', postgresql_where=sa.text("status = 'in_progress'"), sqlite_where=sa.text("status = 'in_progress'"))
    op.drop_index(op.f('ix_review_attempts_user_id'), table_name='review_attempts')
    op.drop_index(op.f('ix_review_attempts_course_id'), table_name='review_attempts')
    op.drop_table('review_attempts')
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    op.drop_index(op.f('ix_password_reset_tokens_user_id'), table_name='password_reset_tokens')
    op.drop_index(op.f('ix_password_reset_tokens_token_hash'), table_name='password_reset_tokens')
    op.drop_index(op.f('ix_password_reset_tokens_id'), table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_index('uq_notifications_source', table_name='notifications', postgresql_where=sa.text('source_id IS NOT NULL'), sqlite_where=sa.text('source_id IS NOT NULL'))
    op.drop_index('ix_notifications_user_read_created', table_name='notifications')
    op.drop_table('notifications')
    op.drop_table('learning_path_nodes')
    op.drop_table('learning_path_edges')
    op.drop_index(op.f('ix_knowledge_chunks_skill_id'), table_name='knowledge_chunks')
    op.drop_table('knowledge_chunks')
    op.drop_index(op.f('ix_feedback_feedback_id'), table_name='feedback')
    op.drop_table('feedback')
    op.drop_table('email_preferences')
    op.drop_table('course_skill')
    op.drop_table('chat_session')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_skills_skill_id'), table_name='skills')
    op.drop_table('skills')
    op.drop_index(op.f('ix_learning_paths_record_id'), table_name='learning_paths')
    op.drop_table('learning_paths')
    op.drop_index(op.f('ix_courses_course_id'), table_name='courses')
    op.drop_table('courses')
