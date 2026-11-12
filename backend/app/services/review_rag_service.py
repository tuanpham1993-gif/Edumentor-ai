"""RAG — tìm đoạn tri thức liên quan nhất cho một kỹ năng (module 09 · Tuấn · GĐ2, 09/11/2026).

    retrieve_chunks(db, skill_id, query) → các đoạn của kỹ năng, xếp theo cosine(vector câu hỏi, vector đoạn)

- Vector của ĐOẠN tính sẵn offline (scripts/build_embeddings.py) → lưu cột knowledge_chunks.embedding.
- Vector của CÂU TRUY VẤN (tên kỹ năng) tính lúc chạy bằng cùng mô hình settings.REVIEW_EMBEDDING_MODEL,
  chỉ dùng mô hình ĐÃ TẢI SẴN trên máy (local_files_only — không tải từ mạng giữa một request).
- Chưa có vector / chưa có mô hình → vẫn trả đủ đoạn của kỹ năng theo thứ tự tạo, score=None
  (ôn tập không bị chặn chỉ vì thiếu embedding). trace ghi rõ embedding đã dùng hay chưa.
"""

import logging
import math
import sys
import threading
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.ai.review.base import RetrievedChunk
from app.core.config import settings
from app.repositories import review_repository

logger = logging.getLogger(__name__)

TOP_K = 3  # số đoạn đưa vào ngữ cảnh cho mỗi kỹ năng

Embedder = Callable[[str], list[float] | None]


def cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Hai vector khác số chiều (đổi mô hình mà chưa chạy lại build_embeddings?)")
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


# Luồng nạp nền + request đầu tiên có thể gọi CÙNG LÚC → khóa + kiểm tra lại bên trong khóa → chỉ nạp MỘT lần (12/11)
_MODEL_LOCK = threading.Lock()
_model_state: dict = {}  # {"model": SentenceTransformer | None} sau khi đã thử nạp


def _load_model():
    """Nạp mô hình MỘT lần (import ~40 giây + nạp ~6 giây khi máy nguội). Không có thư viện / mô hình → None."""
    if "model" in _model_state:
        return _model_state["model"]
    with _MODEL_LOCK:
        if "model" not in _model_state:  # bên tới sau: bên kia đã nạp xong trong lúc mình chờ khóa
            _model_state["model"] = _try_load()
    return _model_state["model"]


def _try_load():
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(settings.REVIEW_EMBEDDING_MODEL, local_files_only=True)
    except Exception as err:  # noqa: BLE001 — thiếu thư viện / chưa tải mô hình / lỗi file: đều rơi về chế độ không xếp hạng
        logger.warning("RAG: không nạp được mô hình embedding (%s) — xếp đoạn theo thứ tự tạo", err)
        return None


def warm_up_in_background() -> None:
    """Nạp sẵn mô hình embedding ở LUỒNG NỀN lúc bật server (12/11).

    Trước đây mô hình chỉ nạp ở request ôn tập ĐẦU TIÊN → request đó có lúc > 60 giây (đo 11/11).
    Chạy nền nên server vẫn khởi động ngay; request tới trước khi nạp xong thì chờ phần còn lại
    (_MODEL_LOCK: bên tới sau chờ bên đang nạp rồi dùng luôn kết quả). Bỏ qua khi chạy pytest.
    """
    if "pytest" in sys.modules:
        return

    def _work() -> None:
        model = _load_model()
        if model is not None:
            model.encode("khởi động", normalize_embeddings=True)  # lần encode đầu cũng chậm → làm luôn
            logger.info("RAG: đã nạp sẵn mô hình embedding %s", settings.REVIEW_EMBEDDING_MODEL)

    threading.Thread(target=_work, name="rag-warm-up", daemon=True).start()


def embed_query(text: str) -> list[float] | None:
    model = _load_model()
    if model is None:
        return None
    return model.encode(text, normalize_embeddings=True).tolist()


def retrieve_chunks(
    db: Session,
    skill_id: int,
    query: str,
    *,
    top_k: int = TOP_K,
    embedder: Embedder | None = None,
) -> list[RetrievedChunk]:
    chunks = review_repository.chunks_for_skill(db, skill_id)
    results = [
        RetrievedChunk(chunk_id=c.chunk_id, code=c.code, title=c.title, content=c.content)
        for c in chunks
    ]
    vectors = {c.chunk_id: c.embedding for c in chunks if c.embedding}
    if not vectors:  # chưa chạy build_embeddings → khỏi nạp mô hình
        return results[:top_k]

    query_vector = (embedder or embed_query)(query)
    if query_vector is None:
        return results[:top_k]
    try:
        for r in results:
            if r.chunk_id in vectors:
                r.score = round(cosine(query_vector, vectors[r.chunk_id]), 4)
    except ValueError as err:
        logger.warning("RAG: %s", err)
        for r in results:
            r.score = None
        return results[:top_k]
    # Đoạn chưa có vector xếp cuối; còn lại theo cosine giảm dần.
    results.sort(key=lambda r: (r.score is None, -(r.score or 0)))
    return results[:top_k]
