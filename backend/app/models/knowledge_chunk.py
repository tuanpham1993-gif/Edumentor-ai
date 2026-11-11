"""Model bảng `knowledge_chunks` — đoạn tri thức cho RAG (module 09 · Tuấn · GĐ1, 10/11/2026).

Mỗi dòng = một đoạn tài liệu ngắn về MỘT kỹ năng (nhóm tự soạn — A8).
  - embedding: vector số thực của đoạn, tính sẵn OFFLINE bằng scripts/build_embeddings.py
    (backend chỉ đọc vector và tính cosine — A7, không cài torch).
  - code: mã duy nhất do người soạn đặt (vd "312-ITER-K01") → scripts/seed_review.py chạy lại
    nhiều lần không bị trùng. Đoạn do AI/hệ thống tạo sau này có thể để trống.
Bảng `skills` là của Hòa (models/skill.py), khóa chính `skill_id`.
"""

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, func

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
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
