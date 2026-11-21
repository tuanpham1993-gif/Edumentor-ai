"""Tìm kỹ năng theo tên → skill_id (module 09 · Tuấn · G1, 21/11/2026 — docs/Review-Skill-Search.md).

    search(db, "java", limit=5) -> {"query", "confident", "results": [{skill_id, skill, score, match, cosine,
                                     aliases, active_questions, pending_questions}], "trace"}
Dùng chung: trang admin Ngân hàng câu hỏi (ô "Tìm kỹ năng"), sau này ôn tập theo kỹ năng (G2), AI lộ trình đổi tên kỹ
năng → id. Chỉ ĐỌC bảng skills, không sửa dữ liệu của Hòa / Khôi.

Vector tên kỹ năng (khối 4) tính MỘT lần (~25 giây cho 5.893 tên) và lưu ra data/cache/skill_name_vectors.npz kèm
tên mô hình + dấu vân tay danh sách kỹ năng; lệch (thêm / đổi tên kỹ năng, đổi mô hình) thì tính lại ở luồng nền.
Chưa có vector / mô hình → vẫn tìm bằng khớp nguyên văn + BM25.
"""

import hashlib
import logging
import sys
import threading
import time
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.review.pipeline import skill_search
from app.core.config import settings
from app.models.skill import Skills
from app.repositories import review_repository as repo

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parents[2]
CACHE_FILE = BACKEND_DIR / "data" / "cache" / "skill_name_vectors.npz"
INDEX_TTL = 600  # giây: dựng lại chỉ mục chữ định kỳ (bắt kỹ năng mới / đổi tên)

_LOCK = threading.Lock()
_state: dict = {"index": None, "built": 0.0, "signature": None}


def _rows(db: Session) -> list[tuple[int, str]]:
    stmt = select(Skills.skill_id, Skills.skill).where(Skills.is_active.is_(True)).order_by(Skills.skill_id)
    return [(i, n) for i, n in db.execute(stmt).all()]


def signature(rows: list[tuple[int, str]]) -> str:
    """Dấu vân tay danh sách kỹ năng + mô hình: đổi bất kỳ → vector cũ không còn đúng."""
    h = hashlib.sha1(settings.REVIEW_EMBEDDING_MODEL.encode())
    for i, n in rows:
        h.update(f"{i}\t{n}\n".encode())
    return h.hexdigest()


def load_vectors(sig: str, path: Path = CACHE_FILE):
    """Vector đã lưu nếu khớp dấu vân tay, không thì None."""
    if not path.exists():
        return None
    try:
        import numpy as np

        data = np.load(path, allow_pickle=False)
        if str(data["signature"]) != sig:
            return None
        return data["vectors"]
    except Exception:  # file hỏng / numpy lỗi → coi như chưa có
        logger.warning("Tìm kỹ năng: không đọc được %s", path, exc_info=True)
        return None


def build_vectors(rows: list[tuple[int, str]], encode, path: Path = CACHE_FILE) -> int:
    """encode(list[str]) -> ma trận (n, d) đã chuẩn hóa. Lưu file cache. Trả số tên đã mã hóa."""
    import numpy as np

    vectors = np.asarray(encode([n for _, n in rows]), dtype=np.float32)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, vectors=vectors, signature=np.array(signature(rows)))
    return len(rows)


def get_index(db: Session, *, force: bool = False) -> skill_search.SkillIndex:
    with _LOCK:
        fresh = _state["index"] is not None and time.time() - _state["built"] < INDEX_TTL
        if fresh and not force:
            return _state["index"]
        rows = _rows(db)
        sig = signature(rows)
        vectors = load_vectors(sig)
        _state.update(index=skill_search.SkillIndex.build(rows, vectors), built=time.time(), signature=sig)
        return _state["index"]


def question_counts(db: Session, skill_ids: list[int]) -> dict[int, tuple[int, int]]:
    """skill_id → (số câu đang bật, số câu chờ duyệt)."""
    active: dict[int, int] = {}
    for (skill_id, _level), n in repo.bank_counts(db, skill_ids).items():
        active[skill_id] = active.get(skill_id, 0) + n
    pending = repo.pending_counts(db, skill_ids)
    return {s: (active.get(s, 0), pending.get(s, 0)) for s in set(skill_ids)}


def _embed(text: str):
    from app.services.review_rag_service import embed_query  # nặng → chỉ nạp khi cần

    return embed_query(text)


def search(db: Session, query: str, limit: int = 5, *, embed=_embed, index=None) -> dict:
    ctx = skill_search.SearchCtx(
        query=query,
        index=index or get_index(db),
        limit=max(1, min(limit, 20)),
        embed=embed,
        counts=lambda ids: question_counts(db, ids),
    )
    skill_search.run(ctx)
    return {"query": ctx.query, "confident": ctx.confident, "results": ctx.results, "trace": ctx.trace}


# ─────────────── Tính vector ở luồng nền lúc khởi động ───────────────


def ensure_vectors(session_factory, load_model) -> int:
    """Cache thiếu / lệch → tính lại (máy mới tự tải mô hình qua load_model). Trả số tên đã mã hóa (0 = đã đủ)."""
    with session_factory() as db:
        rows = _rows(db)
    if not rows or load_vectors(signature(rows)) is not None:
        return 0
    model = load_model()
    if model is None:
        return 0
    count = build_vectors(rows, lambda texts: model.encode(texts, normalize_embeddings=True, batch_size=64))
    with _LOCK:
        _state["index"] = None  # lần tìm sau dựng lại chỉ mục, có vector
    return count


def warm_up_in_background(session_factory) -> None:
    if "pytest" in sys.modules:
        return

    def _work():
        from app.services.review_rag_service import load_or_download_model

        try:
            count = ensure_vectors(session_factory, load_or_download_model)
            if count:
                logger.info("Tìm kỹ năng: đã tính vector cho %d tên kỹ năng", count)
        except Exception:
            logger.exception(
                "Tìm kỹ năng: tính vector thất bại (chạy tay: python -m app.core.seed_data.build_skill_vectors)"
            )

    threading.Thread(target=_work, name="skill-search-vectors", daemon=True).start()
