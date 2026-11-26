"""Truy vấn kho đoạn tri thức (module 09 · Tuấn · G3a, 24/11/2026). Chỉ ĐỌC courses / course_skill / skills (bảng của
Hòa / Khôi); GHI knowledge_chunks (bảng của module 09). Không commit — service commit."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.course import Courses
from app.models.course_skill import CourseSkill
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.review_question import ReviewQuestion

SOURCE_MIN_CHARS = 200  # mô tả ngắn hơn coi như không có nội dung


def chunks_for_skill(db: Session, skill_id: int) -> list[KnowledgeChunk]:
    stmt = select(KnowledgeChunk).where(KnowledgeChunk.skill_id == skill_id).order_by(KnowledgeChunk.chunk_id)
    return list(db.scalars(stmt))


def get_chunk(db: Session, chunk_id: int) -> KnowledgeChunk | None:
    return db.get(KnowledgeChunk, chunk_id)


def question_count_for_chunk(db: Session, chunk_id: int) -> int:
    return db.scalar(select(func.count()).select_from(ReviewQuestion).where(ReviewQuestion.chunk_id == chunk_id))


def course_sources(db: Session, skill_id: int, limit: int = 3) -> list[dict]:
    """Tối đa `limit` khóa NHIỀU học viên nhất dạy kỹ năng, có mô tả đủ dài → nguồn để AI viết đoạn tri thức."""
    rows = db.execute(
        select(Courses.course_id, Courses.title, Courses.description)
        .join(CourseSkill, CourseSkill.course_id == Courses.course_id)
        .where(
            CourseSkill.skill_id == skill_id, func.length(func.coalesce(Courses.description, "")) >= SOURCE_MIN_CHARS
        )
        .order_by(Courses.num_enrolled.desc().nulls_last(), Courses.course_id)
        .limit(limit)
    ).all()
    return [{"course_id": i, "title": t, "description": d} for i, t, d in rows]
