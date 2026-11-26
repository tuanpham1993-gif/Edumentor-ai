"""Kho đoạn tri thức cho RAG khi AI soạn câu ôn tập (module 09 · Tuấn · G3a, 24/11/2026).

    ensure_chunks(db, skill_id, write=...)  → kỹ năng chưa đủ TARGET_CHUNKS đoạn thì AI viết thêm từ mô tả khóa, lưu NGAY
                                             (source='ai', dùng trước kiểm sau — D1), tính embedding. G3d gọi ở bước 1.
    create_chunk / update_chunk / delete_chunk → admin thêm / sửa / xóa (source='admin'), tính lại embedding.

Chỉ viết cho kỹ năng MỞ (G3.0) có mô tả khóa đủ dài (D7). Đoạn AI viết sai khung / lẫn quảng cáo → viết lại 1 lần kèm
lỗi; vẫn chưa đủ → báo lỗi, KHÔNG lưu bừa. `write(...)` / `embed(...)` truyền vào → test dùng AI giả, không gọi mạng.
Docs: docs/Review-AI-Tu-Soan-On-Tap.md mục 7.1.
"""

import logging
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.ai.prompts.review_knowledge import KNOWLEDGE_PROMPT_VERSION
from app.ai.review.grading_schema import AIOutputError
from app.ai.review.knowledge_schema import WORDS_MAX, WORDS_MIN, check_passages
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.user import Users
from app.repositories import knowledge_repository as repo
from app.repositories import skill_scope_repository as scope_repo
from app.services import skill_scope_service

logger = logging.getLogger(__name__)

TARGET_CHUNKS = 3
CONTENT_MIN, CONTENT_MAX = 200, 1500  # ký tự — đoạn admin thêm / sửa

# write(skill, courses, n, existing_titles, feedback) -> JSON thô {"passages": [...]}
Write = Callable[[str, list[dict], int, list[str], list[str]], object]
Embed = Callable[[str], list[float] | None]


class KnowledgeError(Exception):
    """Lỗi nghiệp vụ — router đổi sang mã HTTP. code: not_found | not_open | no_source | ai_failed | in_use | invalid"""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _default_embed(text: str) -> list[float] | None:
    from app.services.review_rag_service import embed_query  # nặng → chỉ nạp khi cần

    return embed_query(text)


def _embed_safe(embed: Embed, text: str) -> list[float] | None:
    try:
        return embed(text)
    except Exception:
        logger.warning("Đoạn tri thức: không tính được embedding", exc_info=True)
        return None


def chunk_dict(c: KnowledgeChunk) -> dict:
    return {
        "chunk_id": c.chunk_id,
        "skill_id": c.skill_id,
        "code": c.code,
        "title": c.title,
        "content": c.content,
        "source": c.source,
        "source_course_ids": c.source_course_ids or [],
        "has_embedding": bool(c.embedding),
        "prompt_version": c.prompt_version,
        "updated_at": c.updated_at,
    }


# ─────────────── AI viết đoạn ───────────────


def ensure_chunks(
    db: Session,
    skill_id: int,
    *,
    write: Write,
    embed: Embed = _default_embed,
    model: str = "",
    target: int = TARGET_CHUNKS,
) -> dict:
    """Đủ `target` đoạn thì không làm gì. Trả {"created": [chunk…], "existing": n}. Lỗi → KnowledgeError."""
    name = scope_repo.skill_name(db, skill_id)
    if name is None:
        raise KnowledgeError("not_found", "Không tìm thấy kỹ năng.")
    existing = repo.chunks_for_skill(db, skill_id)
    need = target - len(existing)
    if need <= 0:
        return {"created": [], "existing": len(existing)}
    if not skill_scope_service.is_open(db, skill_id):
        raise KnowledgeError("not_open", "Kỹ năng chưa được mở cho AI soạn (xem trang Phạm vi kỹ năng).")
    courses = repo.course_sources(db, skill_id)
    if not courses:
        raise KnowledgeError("no_source", "Kỹ năng chưa có khóa học nào có mô tả đủ dài để làm nguồn.")

    existing_titles = [c.title for c in existing if c.title]
    passages: list[dict] = []
    feedback: list[str] = []
    for _ in range(2):  # lần đầu + viết lại 1 lần kèm lỗi
        try:
            data = write(name, courses, need, existing_titles, feedback)
        except AIOutputError as err:
            feedback = [f"Previous answer was not valid JSON for the schema: {err}"]
            continue
        passages, errors = check_passages(
            data,
            need,
            course_ids={c["course_id"] for c in courses},
            existing=[c.content for c in existing] + existing_titles,
        )
        if len(passages) >= need:
            break
        feedback = [f"Previous attempt rejected: {e}" for e in errors[:5]] + [
            f"Each passage must be {WORDS_MIN + 20}-{WORDS_MAX - 50} words, no salaries / prices / course marketing."
        ]
    if len(passages) < need:
        raise KnowledgeError("ai_failed", f"AI chưa viết được đủ {need} đoạn hợp lệ — thử lại sau.")

    created = []
    for p in passages:
        chunk = KnowledgeChunk(
            skill_id=skill_id,
            title=p["title"],
            content=p["content"],
            embedding=_embed_safe(embed, p["content"]),
            source="ai",
            source_course_ids=p["course_ids"],
            model=model or None,
            prompt_version=KNOWLEDGE_PROMPT_VERSION,
        )
        db.add(chunk)
        created.append(chunk)
    db.commit()
    for c in created:
        db.refresh(c)
    logger.info("Đoạn tri thức: AI viết %d đoạn cho kỹ năng %s (%s)", len(created), skill_id, name)
    return {"created": [chunk_dict(c) for c in created], "existing": len(existing)}


# ─────────────── Admin thêm / sửa / xóa ───────────────


def _check_text(title: str | None, content: str) -> tuple[str | None, str]:
    content = (content or "").strip()
    if not CONTENT_MIN <= len(content) <= CONTENT_MAX:
        raise KnowledgeError("invalid", f"Nội dung đoạn phải dài {CONTENT_MIN}–{CONTENT_MAX} ký tự.")
    return ((title or "").strip()[:200] or None), content


def create_chunk(db: Session, admin: Users, skill_id: int, *, title, content, embed: Embed = _default_embed) -> dict:
    if scope_repo.skill_name(db, skill_id) is None:
        raise KnowledgeError("not_found", "Không tìm thấy kỹ năng.")
    title, content = _check_text(title, content)
    chunk = KnowledgeChunk(skill_id=skill_id, title=title, content=content, embedding=_embed_safe(embed, content),
                           source="admin", updated_by=admin.user_id)  # fmt: skip
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk_dict(chunk)


def update_chunk(db: Session, admin: Users, chunk_id: int, *, title, content, embed: Embed = _default_embed) -> dict:
    chunk = repo.get_chunk(db, chunk_id)
    if chunk is None:
        raise KnowledgeError("not_found", "Không tìm thấy đoạn tri thức.")
    title, content = _check_text(title, content)
    if content != chunk.content:
        chunk.embedding = _embed_safe(embed, content)
    chunk.title, chunk.content = title, content
    chunk.source = "admin"
    chunk.updated_by = admin.user_id
    db.commit()
    db.refresh(chunk)
    return chunk_dict(chunk)


def delete_chunk(db: Session, chunk_id: int) -> None:
    chunk = repo.get_chunk(db, chunk_id)
    if chunk is None:
        raise KnowledgeError("not_found", "Không tìm thấy đoạn tri thức.")
    used = repo.question_count_for_chunk(db, chunk_id)
    if used:
        raise KnowledgeError("in_use", f"Đoạn đang là nguồn của {used} câu hỏi — sửa đoạn thay vì xóa.")
    db.delete(chunk)
    db.commit()
