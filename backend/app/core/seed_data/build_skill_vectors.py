"""Tính vector tên kỹ năng cho tìm kỹ năng (G1) — chạy TAY khi cần (module 09 · Tuấn · 21/11/2026).

Backend tự tính ở luồng nền khi khởi động nếu cache thiếu / lệch; lệnh này để tính ngay hoặc tính lại:
    python -m app.core.seed_data.build_skill_vectors          (trong thư mục backend)
Kết quả: data/cache/skill_name_vectors.npz (không đưa vào git).
"""

import sys

from app.core.database import SessionLocal
from app.services import skill_search_service as svc


def main() -> int:
    from app.services.review_rag_service import load_or_download_model

    db = SessionLocal()
    try:
        rows = svc._rows(db)
    finally:
        db.close()
    model = load_or_download_model()
    if model is None:
        print("Không nạp được mô hình embedding — kiểm tra sentence-transformers / mạng.")
        return 1
    count = svc.build_vectors(rows, lambda t: model.encode(t, normalize_embeddings=True, batch_size=64,
                                                             show_progress_bar=True))  # fmt: skip
    print(f"Đã tính vector cho {count} tên kỹ năng → {svc.CACHE_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
