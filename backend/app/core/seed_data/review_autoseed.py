"""Tự nạp đề ôn tập khi KHỞI TẠO database lần đầu (module 09 · Tuấn · 21/11/2026 — Hòa đề nghị).

Làm thay 4 lệnh tay khi chạy Docker lần đầu:
    python -m app.core.seed_data.seed_review --file data/review/course_312_en.json   (… và mọi course_*_en.json)
    python -m app.core.seed_data.build_embeddings
Chỉ chạy khi bảng review_questions TRỐNG — đã có đề thì bỏ qua (không đè phần admin đã sửa / xóa). File đề mới thêm
sau này vào database đã có đề → vẫn nạp bằng lệnh tay (backend/data/review/README.md).
Gọi từ init_db() SAU seed_data() của Hòa (cần khóa học + kỹ năng đã có). Lỗi bất kỳ chỉ ghi log, không làm dừng
backend. Embedding tính ở luồng nền (mô hình dùng chung với review_rag_service) → khởi động không chậm.
"""

import logging
import sys
import threading
from pathlib import Path

from sqlalchemy import func, select

from app.core.seed_data import build_embeddings, seed_review
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.review_question import ReviewQuestion

logger = logging.getLogger(__name__)

BANK_DIR = seed_review.BACKEND_DIR / "data" / "review"


def bank_files(bank_dir: Path = BANK_DIR) -> list[Path]:
    """Mọi ngân hàng đang dùng (course_*_en.json), không lấy thư mục archive/."""
    return sorted(bank_dir.glob("course_*_en.json"))


def seed_banks_if_empty(db, bank_dir: Path = BANK_DIR) -> dict:
    """Nạp mọi ngân hàng nếu review_questions đang trống. Trả {"skipped": bool, "loaded": [...], "failed": [...]}.
    Mỗi file một giao dịch: file lỗi (sai cấu trúc / khóa chưa có trong DB) → bỏ qua file đó, nạp tiếp file khác."""
    if db.scalar(select(func.count()).select_from(ReviewQuestion)):
        return {"skipped": True, "loaded": [], "failed": []}
    loaded, failed = [], []
    for path in bank_files(bank_dir):
        try:
            data = seed_review.load_bank(path)
            errors = seed_review.validate_bank(data) or seed_review.check_against_db(db, data)
            if errors:
                failed.append(path.name)
                logger.warning("Tự nạp đề: bỏ qua %s (%d lỗi, vd: %s)", path.name, len(errors), errors[0])
                continue
            counts = seed_review.seed_bank(db, data)
            db.commit()
            loaded.append(path.name)
            logger.info("Tự nạp đề %s: +%d câu, +%d đoạn tri thức", path.name, counts["questions_added"],
                        counts["chunks_added"])  # fmt: skip
        except Exception:
            db.rollback()
            failed.append(path.name)
            logger.exception("Tự nạp đề: lỗi khi nạp %s", path.name)
    return {"skipped": False, "loaded": loaded, "failed": failed}


def build_missing_embeddings(session_factory, load_model) -> int:
    """Tính vector cho các đoạn tri thức chưa có (như `build_embeddings` không kèm --all). Trả số đoạn đã ghi.
    Không còn đoạn nào thiếu vector → không nạp mô hình."""
    with session_factory() as db:
        missing = db.scalar(select(func.count()).select_from(KnowledgeChunk).where(KnowledgeChunk.embedding.is_(None)))
    if not missing:
        return 0
    model = load_model()
    if model is None:  # máy chưa cài sentence-transformers → bỏ qua, ôn tập vẫn chạy (đề đã đủ câu)
        return 0

    def encode(texts):
        return model.encode(texts, normalize_embeddings=True).tolist()

    db = session_factory()
    try:
        count = build_embeddings.build(db, encode)
        db.commit()
        return count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def run(session_factory) -> dict:
    """Gọi trong init_db(). Không bao giờ ném lỗi ra ngoài."""
    db = None
    try:
        db = session_factory()
        result = seed_banks_if_empty(db)
    except Exception:
        if db is not None:
            db.rollback()
        logger.exception("Tự nạp đề ôn tập thất bại")
        return {"skipped": False, "loaded": [], "failed": ["*"]}
    finally:
        if db is not None:
            db.close()
    if not result["skipped"]:
        logger.info("Tự nạp đề ôn tập: nạp %s, lỗi %s", result["loaded"], result["failed"])
    if "pytest" not in sys.modules:
        threading.Thread(target=_embed_in_background, args=(session_factory,), name="review-embeddings",
                         daemon=True).start()  # fmt: skip
    return result


def _embed_in_background(session_factory) -> None:
    # nặng → chỉ nạp trong luồng nền. Máy mới chưa có mô hình → tải về một lần (load_or_download_model)
    from app.services.review_rag_service import load_or_download_model

    try:
        count = build_missing_embeddings(session_factory, load_or_download_model)
        if count:
            logger.info("Tự nạp đề: đã tính embedding cho %d đoạn tri thức", count)
    except Exception:
        logger.exception("Tự nạp đề: tính embedding thất bại (chạy tay: python -m app.core.seed_data.build_embeddings)")
