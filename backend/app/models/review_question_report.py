"""Model bảng `review_question_reports` — mentor phản ánh lỗi câu ôn tập AI soạn (module 09 · Tuấn · G3f, 25/11/2026).

Docs: docs/Review-AI-Tu-Soan-On-Tap.md D19–D23, mục 7.2. Bảng riêng của module 09 (KHÔNG dùng bảng feedback của Tâm).
  - Một dòng = một lần mentor bấm "Phản ánh lỗi" một câu (học viên KHÔNG phản ánh — D19).
  - Mỗi câu chỉ có MỘT phản ánh đang mở (index duy nhất có điều kiện status='open'); câu đã được admin xử lý có thể
    bị phản ánh lại.
  - status: 'open' (chờ admin) | 'resolved' (admin sửa câu / giữ tắt) | 'dismissed' (admin bác → câu bật lại, coi như Đạt).
Mentor phản ánh → câu TẮT NGAY (D20), review_question_meta.disabled_reason = 'mentor_report'.
"""

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, func, text

from app.core.database import Base

REASONS = ("wrong_answer", "ambiguous", "wrong_knowledge", "bad_rubric", "other")
STATUSES = ("open", "resolved", "dismissed")


class ReviewQuestionReport(Base):
    __tablename__ = "review_question_reports"

    report_id = Column(Integer, primary_key=True)
    question_id = Column(
        Integer, ForeignKey("review_questions.question_id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)  # mentor
    reason = Column(String(20), nullable=False)
    note = Column(String(500), nullable=True)
    status = Column(String(10), nullable=False, default="open", server_default="open")
    admin_note = Column(String(500), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "reason IN ('wrong_answer', 'ambiguous', 'wrong_knowledge', 'bad_rubric', 'other')",
            name="ck_review_question_reports_reason",
        ),
        CheckConstraint("status IN ('open', 'resolved', 'dismissed')", name="ck_review_question_reports_status"),
        Index(
            "uq_review_question_reports_one_open",
            "question_id",
            unique=True,
            postgresql_where=text("status = 'open'"),
            sqlite_where=text("status = 'open'"),
        ),
    )
