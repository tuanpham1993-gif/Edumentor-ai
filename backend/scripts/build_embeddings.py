"""Tính vector embedding cho đoạn tri thức ôn tập — chạy TAY trên máy (module 09 · Tuấn · GĐ2, 09/11/2026).

Chạy (trong thư mục backend):
    python -m scripts.build_embeddings          # chỉ các đoạn CHƯA có vector (sau khi seed thêm / sửa đoạn)
    python -m scripts.build_embeddings --all    # tính lại TẤT CẢ (sau khi đổi REVIEW_EMBEDDING_MODEL)

- Mô hình: settings.REVIEW_EMBEDDING_MODEL (đa ngôn ngữ — tài liệu viết tiếng Việt). Lần đầu tự tải
  về máy (~470 MB, lưu cache Hugging Face); những lần sau và lúc server chạy dùng bản đã tải.
- Vector được chuẩn hóa (độ dài 1) → cosine = tích vô hướng. Lưu vào knowledge_chunks.embedding.
- Vì sao tính sẵn: server chỉ đọc vector + tính cosine, không phải mã hóa lại tài liệu mỗi lần ra đề (A7).
"""

import argparse
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, create_tables
from app.models.knowledge_chunk import KnowledgeChunk


def chunk_text(chunk: KnowledgeChunk) -> str:
    """Tiêu đề + nội dung (tiêu đề giúp đoạn ngắn vẫn mang đủ nghĩa)."""
    return f"{chunk.title}\n{chunk.content}" if chunk.title else chunk.content


def build(db: Session, encode, *, rebuild_all: bool = False) -> int:
    """encode(list[str]) -> list[list[float]]. Trả số đoạn đã ghi vector (chỉ flush — main() commit)."""
    query = select(KnowledgeChunk).order_by(KnowledgeChunk.chunk_id)
    if not rebuild_all:
        query = query.where(KnowledgeChunk.embedding.is_(None))
    chunks = list(db.scalars(query))
    if not chunks:
        return 0
    vectors = encode([chunk_text(c) for c in chunks])
    for chunk, vector in zip(chunks, vectors, strict=True):
        chunk.embedding = [round(float(x), 6) for x in vector]
    db.flush()
    return len(chunks)


def main() -> int:
    parser = argparse.ArgumentParser(description="Tính embedding cho đoạn tri thức ôn tập")
    parser.add_argument("--all", action="store_true", help="tính lại tất cả đoạn")
    args = parser.parse_args()

    from sentence_transformers import (
        SentenceTransformer,  # nặng → chỉ nạp khi chạy script
    )

    print(f"Nạp mô hình {settings.REVIEW_EMBEDDING_MODEL} (lần đầu sẽ tải về, ~470 MB)…")
    model = SentenceTransformer(settings.REVIEW_EMBEDDING_MODEL)

    def encode(texts):
        return model.encode(texts, normalize_embeddings=True, show_progress_bar=True).tolist()

    create_tables()
    db = SessionLocal()
    try:
        count = build(db, encode, rebuild_all=args.all)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    print(f"Đã ghi vector cho {count} đoạn tri thức.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
