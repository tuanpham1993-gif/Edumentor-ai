"""Model bảng `knowledge_chunks` — đoạn tri thức cho RAG (module 09 · Tuấn · GĐ1, 10/11/2026).

Mỗi dòng = một đoạn tài liệu ngắn về MỘT kỹ năng (nhóm tự soạn — A8).
  - embedding: vector số thực của đoạn, tính sẵn OFFLINE bằng scripts/build_embeddings.py
    (backend chỉ đọc vector và tính cosine — A7, không cài torch).
  - code: mã duy nhất do người soạn đặt (vd "312-ITER-K01") → scripts/seed_review.py chạy lại
    nhiều lần không bị trùng. Đoạn do AI/hệ thống tạo sau này có thể để trống.
Bảng `skills` là của Hòa (models/skill.py), khóa chính `skill_id`.

G3a (24/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md mục 7.1): thêm nguồn gốc đoạn
  - source: 'manual' (nhóm soạn, nạp từ JSON) | 'ai' (AI viết từ mô tả khóa — dùng ngay, D1) | 'admin' (admin thêm / sửa)
  - source_course_ids: các khóa đã dùng làm nguồn khi AI viết; model / prompt_version: để đo lại khi đổi prompt
"""

from sqlalchemy import JSON, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, func

from app.core.database import Base


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    chunk_id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=True)
    # index=True: RAG luôn lọc theo kỹ năng trước rồi mới xếp hạng cosine.
    skill_id = Column(
        Integer,
        ForeignKey("skills.skill_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    # Danh sách số thực, vd [0.012, -0.08, ...]. NULL = chưa chạy build_embeddings.
    embedding = Column(JSON(none_as_null=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # G3a (24/11)
    source = Column(String(10), nullable=False, default="manual", server_default="manual")
    source_course_ids = Column(JSON(none_as_null=True), nullable=True)
    model = Column(String(100), nullable=True)
    prompt_version = Column(String(30), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (CheckConstraint("source IN ('manual', 'ai', 'admin')", name="ck_knowledge_chunks_source"),)
