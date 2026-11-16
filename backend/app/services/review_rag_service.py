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
GRADING_TOP_K = 2  # B9: số đoạn kèm theo khi CHẤM một câu tự luận (Model B)

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


def warm_up_nlp() -> bool:
    """Nạp sẵn dữ liệu NLTK của khối 1 tiền xử lý / chấm từ khóa (B12, 16/11): NLTK chỉ đọc dữ liệu từ đĩa ở lần gọi
    ĐẦU TIÊN → lần nộp bài đầu sau khi khởi động chậm thêm ~8 s (đo trên Docker). Lỗi chỉ ghi log, không chặn."""
    try:
        from app.ai.review.text_pipeline import preprocess

        preprocess("Warm up: tuples cannot be changed while loops repeat.")
        return True
    except Exception as err:  # noqa: BLE001 — thiếu dữ liệu NLTK: chấm từ khóa sẽ báo lỗi rõ khi dùng tới
        logger.warning("Ôn tập: không nạp sẵn được dữ liệu NLTK (%s)", err)
        return False


def warm_up_in_background() -> None:
    """Nạp sẵn mô hình embedding ở LUỒNG NỀN lúc bật server (12/11).

    Trước đây mô hình chỉ nạp ở request ôn tập ĐẦU TIÊN → request đó có lúc > 60 giây (đo 11/11).
    Chạy nền nên server vẫn khởi động ngay; request tới trước khi nạp xong thì chờ phần còn lại
    (_MODEL_LOCK: bên tới sau chờ bên đang nạp rồi dùng luôn kết quả). Bỏ qua khi chạy pytest.
    """
    if "pytest" in sys.modules:
        return

    def _work() -> None:
        warm_up_nlp()  # nhanh (vài giây) → làm trước mô hình embedding
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


# ─────────────── B9 (15/11): RAG khi CHẤM tự luận (Model B) ───────────────


def grading_query(question: dict) -> str:
    """Câu truy vấn khi chấm = đề + nội dung các ý barem. KHÔNG dùng bài làm: bài sai / lạc đề không được kéo
    theo tài liệu sai, và người học không thể "điều khiển" tài liệu đưa cho AI chấm."""
    return "\n".join([question.get("content") or ""] + [r.get("text", "") for r in question.get("rubric") or []])


def rank_for_grading(
    chunks: list[tuple[RetrievedChunk, list[float] | None]],
    linked_chunk_id: int | None,
    query: str,
    *,
    top_k: int = GRADING_TOP_K,
    embedder: Embedder | None = None,
) -> list[RetrievedChunk]:
    """Hàm THUẦN (không DB) — server và scripts/eval_grading dùng chung để Model B đo được đúng như khi chạy thật.
    chunks: các đoạn CÙNG kỹ năng kèm vector (có thể None). Đoạn gắn với câu hỏi (nguồn soạn câu) đứng đầu;
    còn lại xếp theo cosine với câu truy vấn; không có vector / mô hình → theo thứ tự đầu vào."""
    linked = [c for c, _ in chunks if c.chunk_id == linked_chunk_id]
    others = [(c, v) for c, v in chunks if c.chunk_id != linked_chunk_id]
    if others and any(v for _, v in others):
        query_vector = (embedder or embed_query)(query)
        if query_vector is not None:
            try:
                for c, v in others:
                    c.score = round(cosine(query_vector, v), 4) if v else None
            except ValueError as err:
                logger.warning("RAG chấm bài: %s", err)
                for c, _ in others:
                    c.score = None
            others.sort(key=lambda cv: (cv[0].score is None, -(cv[0].score or 0)))
    return (linked + [c for c, _ in others])[:top_k]


def retrieve_for_grading(
    db: Session, skill_id: int, linked_chunk_id: int | None, question: dict, *, embedder: Embedder | None = None
) -> list[RetrievedChunk]:
    """Đoạn tri thức kèm theo khi chấm MỘT câu tự luận — lọc đúng kỹ năng của câu hỏi."""
    rows = review_repository.chunks_for_skill(db, skill_id)
    chunks = [
        (RetrievedChunk(chunk_id=c.chunk_id, code=c.code, title=c.title, content=c.content), c.embedding) for c in rows
    ]
    return rank_for_grading(chunks, linked_chunk_id, grading_query(question), embedder=embedder)
