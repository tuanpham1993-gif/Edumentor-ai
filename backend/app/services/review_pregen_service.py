"""Soạn sẵn câu ôn tập BAN ĐÊM cho kỹ năng ưu tiên (module 09 · Tuấn · G3d-3, 25/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md
D24, D26, mục 7.5).

    pick_skills(db, limit)                 chọn kỹ năng cần soạn sẵn, ưu tiên trước
    run_nightly(session_factory, deps, …)  soạn LẦN LƯỢT từng kỹ năng (việc 'nightly'), câu lưu origin='nightly' →
                                           chỉ vào đề khi mentor đã Đạt (D26)
    start_background(session_factory)      luồng nền chạy mỗi đêm lúc REVIEW_PREGEN_HOUR. MẶC ĐỊNH TẮT
                                           (REVIEW_PREGEN_ENABLED=true trong backend/.env để bật)

Ưu tiên (D24): kỹ năng có trong lộ trình ĐANG HỌC (status 'ongoing') và đang Mở, còn thiếu so với ~30 câu (gồm kỹ năng
sắp hết câu chưa làm và kỹ năng bị mentor tắt câu — đều làm ngân hàng thiếu). Nhiều người học trước, rồi nhiều lượt
ôn trước. Mỗi đêm tối đa REVIEW_PREGEN_PER_NIGHT kỹ năng (giữ trong hạn mức Gemini miễn phí).
"""

import logging
import threading
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.learning_path import LearningPath, LearningPathNode
from app.models.review_attempt import ReviewAttempt
from app.models.review_generation_job import ReviewGenerationJob
from app.models.review_skill_scope import ReviewSkillScope
from app.repositories import knowledge_repository
from app.services import review_generation_service as gen

logger = logging.getLogger(__name__)

_stop = threading.Event()
_thread: threading.Thread | None = None


def pick_skills(db: Session, limit: int) -> list[dict]:
    """[{skill_id, learners, attempts, missing}] — kỹ năng nên soạn sẵn đêm nay, ưu tiên trước."""
    learners = dict(
        db.execute(
            select(LearningPathNode.skill_id, func.count(func.distinct(LearningPath.student_id)))
            .join(LearningPath, LearningPath.record_id == LearningPathNode.path_id)
            .join(ReviewSkillScope, ReviewSkillScope.skill_id == LearningPathNode.skill_id)
            .where(LearningPath.status == "ongoing", ReviewSkillScope.label == "open")
            .group_by(LearningPathNode.skill_id)
        ).all()
    )
    if not learners:
        return []
    attempts = dict(
        db.execute(
            select(ReviewAttempt.skill_id, func.count())
            .where(ReviewAttempt.skill_id.in_(learners))
            .group_by(ReviewAttempt.skill_id)
        ).all()
    )
    busy = set(db.scalars(select(ReviewGenerationJob.skill_id).where(ReviewGenerationJob.status.in_(gen.ACTIVE))))
    order = sorted(learners, key=lambda s: (-learners[s], -attempts.get(s, 0), s))
    picked = []
    for skill_id in order:
        if len(picked) >= limit:
            break
        if skill_id in busy:
            continue
        missing = gen.missing_for(db, skill_id, "nightly")
        if not missing:
            continue
        if not knowledge_repository.chunks_for_skill(db, skill_id) and not knowledge_repository.course_sources(
            db, skill_id
        ):
            continue  # không có nguồn (D7)
        picked.append({"skill_id": skill_id, "learners": learners[skill_id], "attempts": attempts.get(skill_id, 0),
                       "missing": missing})  # fmt: skip
    return picked


def run_nightly(session_factory, deps: gen.Deps | None, *, limit: int | None = None) -> dict:
    """Soạn lần lượt (không song song — nhẹ cho Gemini). Trả {"skills": n, "done": n, "failed": n, "saved": n}."""
    summary = {"skills": 0, "done": 0, "failed": 0, "saved": 0}
    if deps is None:
        logger.info("Soạn sẵn ban đêm: bỏ qua (chưa bật AI thật)")
        return summary
    with session_factory() as db:
        skills = pick_skills(db, limit or settings.REVIEW_PREGEN_PER_NIGHT)
    for item in skills:
        if _stop.is_set():
            break
        with session_factory() as db:
            job = ReviewGenerationJob(skill_id=item["skill_id"], kind="nightly")
            db.add(job)
            try:
                db.commit()
            except IntegrityError:  # vừa có người bấm ôn kỹ năng này → để việc kia chạy
                db.rollback()
                continue
            job_id = job.job_id
        gen.run_job(job_id, session_factory, deps)
        with session_factory() as db:
            job = db.get(ReviewGenerationJob, job_id)
            summary["skills"] += 1
            summary["done" if job.status == "done" else "failed"] += 1
            summary["saved"] += job.saved
    logger.info("Soạn sẵn ban đêm: %s", summary)
    return summary


def _seconds_until(hour: int, now: datetime | None = None) -> float:
    now = now or datetime.now()
    target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


def _loop(session_factory) -> None:
    while not _stop.wait(_seconds_until(settings.REVIEW_PREGEN_HOUR)):
        try:
            run_nightly(session_factory, gen.deps_factory())
        except Exception:
            logger.exception("Soạn sẵn ban đêm lỗi")


def start_background(session_factory) -> None:
    """Gọi trong lifespan của app. MẶC ĐỊNH TẮT — REVIEW_PREGEN_ENABLED=true để bật."""
    global _thread
    if not settings.REVIEW_PREGEN_ENABLED or (_thread is not None and _thread.is_alive()):
        return
    _stop.clear()
    _thread = threading.Thread(target=_loop, args=(session_factory,), name="review-pregen", daemon=True)
    _thread.start()


def stop_background() -> None:
    _stop.set()
