"""Model bảng `review_generation_jobs` — việc AI soạn câu ôn theo kỹ năng chạy ở nền (module 09 · Tuấn · G3d, 25/11/2026).

Docs: docs/Review-AI-Tu-Soan-On-Tap.md D9, D24, D25, mục 7.5.
  - Một dòng = một lần soạn cho MỘT kỹ năng (kỹ năng giữ ngân hàng câu — `skill_id`).
  - kind: 'exam' (học viên bấm ôn mà thiếu câu → soạn đủ 1 đề) | 'topup' (bổ sung tới ~30 câu, G3d-3) |
          'nightly' (soạn sẵn ban đêm, G3d-3).
  - status: 'queued' → 'running' → 'done' | 'failed'. step 1..4 (đoạn tài liệu → trắc nghiệm → tự luận → lưu) cho màn
    "Đang soạn đề… bước x/4".
  - D9: MỖI kỹ năng chỉ một việc đang chờ / chạy (index duy nhất có điều kiện) → nhiều người bấm cùng lúc chỉ soạn 1 lần.
"""

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, func, text

from app.core.database import Base

KINDS = ("exam", "topup", "nightly")
STATUSES = ("queued", "running", "done", "failed")


class ReviewGenerationJob(Base):
    __tablename__ = "review_generation_jobs"

    job_id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.skill_id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String(10), nullable=False)
    status = Column(String(10), nullable=False, default="queued", server_default="queued")
    step = Column(Integer, nullable=False, default=0, server_default="0")
    requested_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    error = Column(String(500), nullable=True)
    saved = Column(Integer, nullable=False, default=0, server_default="0")  # số câu đã lưu vào ngân hàng
    calls = Column(Integer, nullable=False, default=0, server_default="0")  # số lần gọi Gemini (soạn + giải mù)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("kind IN ('exam', 'topup', 'nightly')", name="ck_review_generation_jobs_kind"),
        CheckConstraint("status IN ('queued', 'running', 'done', 'failed')", name="ck_review_generation_jobs_status"),
        Index(
            "uq_review_generation_jobs_one_active",
            "skill_id",
            unique=True,
            postgresql_where=text("status IN ('queued', 'running')"),
            sqlite_where=text("status IN ('queued', 'running')"),
        ),
    )
