"""Việc AI soạn câu ôn theo kỹ năng chạy ở NỀN (module 09 · Tuấn · G3d-1, 25/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md
D9, D25, P14, mục 7.5).

    request(db, skill_id, user_id)   học viên bấm ôn mà thiếu câu → tạo việc soạn (hoặc trả việc đang chạy của kỹ năng —
                                      D9: nhiều người bấm cùng lúc chỉ soạn 1 lần) rồi chạy ở luồng nền, trả về NGAY
    run_job(job_id, ...)              4 bước: (1) đoạn tài liệu (G3a, chưa có thì AI viết) → (2) trắc nghiệm → (3) tự luận
                                      (G3b soạn + G3c cổng, lưu NGAY câu đạt: `auto_approved`, origin 'on_demand' — dùng ngay, D1)
                                      → (4) kiểm đủ một đề
    job_view / latest_job             màn "Đang soạn đề… bước x/4" hỏi tiến độ
    recover_on_startup()              server khởi động lại → việc đang chạy dở thành 'failed' (học viên bấm lại là tạo mới)

Loại việc: 'exam' (đủ MỘT đề — học viên đang chờ) → xong thì tự tạo 'topup' (bổ sung tới ~30 câu, D25, ở nền);
'topup' cũng được tạo khi học viên làm lại mà hết câu chưa làm; 'nightly' (soạn sẵn ban đêm, D24 — câu chỉ dùng khi
mentor Đạt, D26) do review_pregen_service tạo.
Gemini quá tải (503) → chờ 20 / 40 / 60 giây rồi thử lại bước đó; vẫn lỗi → 'failed' + thông báo dễ hiểu (P14), câu đã
lưu vẫn giữ. Không có AI thật (AI_MODE=mock / thiếu khóa) → không tạo việc, học viên thấy "Chưa có đề" như G2.
"""

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from math import ceil

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.ai.review.base import AIUnavailableError
from app.core.config import settings
from app.models.review_generation_job import ReviewGenerationJob
from app.models.review_question_meta import ReviewQuestionMeta
from app.repositories import knowledge_repository
from app.repositories import review_repository as repo
from app.services import question_gen_service, skill_scope_service

logger = logging.getLogger(__name__)

STEPS = 4
WAITS = (20, 40, 60)  # giây chờ khi Gemini quá tải (P14)
ROUNDS = 2  # số vòng soạn mỗi bước (mỗi vòng = 1 lần soạn + tối đa 2 lần soạn lại — D3)
TOPUP_ENABLED = True  # D25: đủ đề → tự soạn bổ sung tới ~30 câu (test tắt để đếm lượt gọi gọn)
# 25/11: làm lại ngay sau một việc bổ sung đã kết thúc (xong mà vẫn thiếu / lỗi) → không tạo việc mới trong N phút, ráp
# đề lặp một phần. Chặn vòng "xong → bấm lại → vẫn thiếu → soạn tiếp" tốn lượt Gemini mãi.
TOPUP_RETRY_MINUTES = 10
# Bước B (25/11, sửa D25): số câu theo số ý trong tài liệu — hết ý thì AI viết thêm đoạn (chủ đề con khác), tối đa N đoạn.
MAX_CHUNKS = 6
SENTENCES_PER_CHUNK = 5  # ước lượng số câu (ý) mỗi đoạn AI viết (80–200 từ) khi tính số đoạn cần viết thêm
_sleep = time.sleep  # test thay bằng hàm không chờ
ACTIVE = ("queued", "running")
FAILED_AI = "Chưa soạn được đề vì AI đang quá tải, bạn thử lại sau ít phút."
FAILED_SHORT = "AI chưa soạn đủ câu đạt chất lượng cho một đề, bạn thử lại sau ít phút."
FAILED_OTHER = "Chưa soạn được đề, bạn thử lại sau ít phút."
FAILED_RESTART = "Máy chủ khởi động lại khi đang soạn đề, bạn bấm ôn lại để soạn tiếp."


class GenerationError(Exception):
    """Không tạo được việc soạn. code: ai_off | not_open | no_source"""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class Deps:
    """Các hàm gọi AI — truyền vào để test dùng AI giả (không gọi mạng)."""

    write_knowledge: Callable
    write_questions: Callable
    solve: Callable | None
    embed: Callable | None
    model: str = ""


def default_deps() -> Deps | None:
    """AI thật (Gemini) nếu AI_MODE=real và có khóa; không thì None (không soạn được)."""
    from app.ai.review.real_ai import RealAI, review_llm

    key, model = review_llm()
    if settings.AI_MODE != "real" or not key or not model:
        return None
    from app.services.review_rag_service import embed_query

    ai = RealAI()
    return Deps(ai.write_knowledge, ai.write_questions, ai.solve_mcqs, embed_query, model)


# Cách chạy việc ở nền — test thay bằng hàm chạy đồng bộ.
def _start_thread(job_id: int) -> None:
    from app.core.database import SessionLocal

    deps = default_deps()
    threading.Thread(
        target=run_job, args=(job_id, SessionLocal, deps), name=f"review-gen-{job_id}", daemon=True
    ).start()


runner: Callable[[int], None] = _start_thread
deps_factory: Callable[[], Deps | None] = default_deps


# ─────────────── đọc ───────────────


def job_view(job: ReviewGenerationJob | None) -> dict | None:
    if job is None:
        return None
    return {"job_id": job.job_id, "skill_id": job.skill_id, "kind": job.kind, "status": job.status,
            "step": job.step, "steps": STEPS, "saved": job.saved, "error": job.error}  # fmt: skip


def active_job(db: Session, skill_id: int) -> ReviewGenerationJob | None:
    stmt = select(ReviewGenerationJob).where(
        ReviewGenerationJob.skill_id == skill_id, ReviewGenerationJob.status.in_(ACTIVE)
    )
    return db.scalar(stmt)


def latest_job(db: Session, skill_id: int) -> ReviewGenerationJob | None:
    return db.scalar(
        select(ReviewGenerationJob)
        .where(ReviewGenerationJob.skill_id == skill_id)
        .order_by(ReviewGenerationJob.job_id.desc())
        .limit(1)
    )


def get_job(db: Session, skill_id: int, job_id: int) -> ReviewGenerationJob | None:
    """Đúng việc học viên đang chờ (25/11): màn chờ hỏi theo job_id — việc 'exam' xong tự tạo 'topup', nếu hỏi
    latest_job thì màn chờ theo nhầm việc bổ sung thêm vài phút dù đề đã sẵn. Việc của kỹ năng khác → None."""
    job = db.get(ReviewGenerationJob, job_id)
    return job if job is not None and job.skill_id == skill_id else None


def recent_topup_finished(db: Session, skill_id: int) -> bool:
    """Có việc bổ sung của kỹ năng đã kết thúc (done / failed) trong TOPUP_RETRY_MINUTES phút qua."""
    since = datetime.now(UTC) - timedelta(minutes=TOPUP_RETRY_MINUTES)
    stmt = select(ReviewGenerationJob.job_id).where(
        ReviewGenerationJob.skill_id == skill_id,
        ReviewGenerationJob.kind == "topup",
        ReviewGenerationJob.status.in_(("done", "failed")),
        ReviewGenerationJob.finished_at >= since,
    )
    return db.scalar(stmt.limit(1)) is not None


def cannot_generate(db: Session, skill_id: int) -> str | None:
    """Lý do KHÔNG soạn được (ai_off | not_open | no_source), None = soạn được."""
    if deps_factory() is None:
        return "ai_off"
    if not skill_scope_service.is_open(db, skill_id):
        return "not_open"
    if not knowledge_repository.chunks_for_skill(db, skill_id) and not knowledge_repository.course_sources(
        db, skill_id
    ):
        return "no_source"  # không có đoạn tài liệu, cũng không có mô tả khóa để AI viết đoạn (D7)
    return None


def _gap(target: dict[str, int], have: dict[str, int]) -> dict[str, int]:
    return {lv: n - have.get(lv, 0) for lv, n in target.items() if n > have.get(lv, 0)}


def usable_counts(db: Session, skill_id: int) -> dict[str, int]:
    """Câu DÙNG ĐƯỢC ra đề ôn theo kỹ năng, theo mức."""
    return {lv: n for (_s, lv), n in repo.bank_counts(db, [skill_id], include_auto=True).items()}


def missing_for_exam(db: Session, skill_id: int) -> dict[str, int]:
    """Số câu CÒN THIẾU theo mức để đủ khung 1 đề (chỉ tính câu dùng được cho ôn theo kỹ năng)."""
    return _gap(question_gen_service.FULL_EXAM, usable_counts(db, skill_id))


def missing_for(db: Session, skill_id: int, kind: str) -> dict[str, int]:
    """exam: đủ 1 đề · topup: tới ~30 câu dùng được (D25) · nightly: tới ~30 câu ĐÃ SOẠN (kể cả câu soạn sẵn chờ mentor
    — không soạn lại mỗi đêm khi mentor chưa kịp duyệt).
    Bước B (25/11, sửa D25): đã đủ MAX_CHUNKS đoạn → không vượt số ý còn trống (hết ý = không cần soạn thêm)."""
    if kind == "exam":
        return missing_for_exam(db, skill_id)
    have = repo.stocked_counts(db, skill_id) if kind == "nightly" else usable_counts(db, skill_id)
    gap = _gap(question_gen_service.SKILL_TARGET, have)
    if gap and len(knowledge_repository.chunks_for_skill(db, skill_id)) >= MAX_CHUNKS:
        gap = question_gen_service.cap_by_ideas(gap, question_gen_service.free_ideas(db, skill_id))
    return gap


def _ensure_ideas(db: Session, job: ReviewGenerationJob, deps: Deps) -> None:
    """Bước 1 (G3a + Bước B): chưa có đoạn → AI viết TARGET_CHUNKS đoạn; thiếu ý cho số câu cần soạn → viết thêm
    ceil(thiếu / SENTENCES_PER_CHUNK) đoạn chủ đề con KHÁC (ensure_chunks gửi kèm tên đoạn đã có), tối đa MAX_CHUNKS.
    Viết thêm lỗi khi đã có đoạn → vẫn soạn tiếp bằng đoạn cũ (không làm hỏng việc)."""
    from app.services import knowledge_service

    for _ in range(2):  # lần 2: sau khi viết đoạn đầu tiên mà vẫn thiếu ý
        chunks = knowledge_repository.chunks_for_skill(db, job.skill_id)
        if not chunks:
            target = knowledge_service.TARGET_CHUNKS
        else:
            short = question_gen_service.ideas_short(
                missing_for(db, job.skill_id, job.kind), question_gen_service.free_ideas(db, job.skill_id)
            )
            target = min(MAX_CHUNKS, len(chunks) + ceil(short / SENTENCES_PER_CHUNK)) if short > 0 else len(chunks)
        if target <= len(chunks):
            return
        try:
            _with_waits(knowledge_service.ensure_chunks, db, job.skill_id, write=deps.write_knowledge,
                        embed=deps.embed or (lambda _t: None), model=deps.model, target=target)  # fmt: skip
        except knowledge_service.KnowledgeError:
            if not chunks:
                raise
            logger.warning("Soạn đề: không viết thêm được đoạn tài liệu (kỹ năng %s) — dùng đoạn cũ", job.skill_id)
            return


# ─────────────── tạo việc ───────────────


def request(db: Session, skill_id: int, user_id: int | None, *, kind: str = "exam") -> ReviewGenerationJob:
    """Có việc đang chờ / chạy của kỹ năng → trả việc đó (D9). Không soạn được → GenerationError."""
    job = active_job(db, skill_id)
    if job is not None:
        return job
    reason = cannot_generate(db, skill_id)
    if reason:
        raise GenerationError(reason, reason)
    job = ReviewGenerationJob(skill_id=skill_id, kind=kind, requested_by=user_id)
    db.add(job)
    try:
        db.commit()
    except IntegrityError:  # người khác vừa tạo việc cho cùng kỹ năng
        db.rollback()
        existing = active_job(db, skill_id)
        if existing is None:
            raise
        return existing
    runner(job.job_id)
    db.refresh(job)
    return job


# ─────────────── chạy việc ───────────────


def _with_waits(fn, *args, **kwargs):
    """Gemini quá tải (AIUnavailableError) → chờ WAITS rồi thử lại; hết lượt chờ → ném lỗi ra ngoài."""
    for wait in (*WAITS, None):
        try:
            return fn(*args, **kwargs)
        except AIUnavailableError:
            if wait is None:
                raise
            logger.warning("Soạn đề: AI quá tải, chờ %s giây", wait)
            _sleep(wait)
    raise AssertionError("unreachable")  # pragma: no cover


def save_questions(db: Session, skill_id: int, questions: list[dict], origin: str) -> int:
    """Lưu câu đã qua cổng vào ngân hàng: source='ai', review_status='auto_approved', BẬT ngay (D1). Không commit."""
    from app.services import review_bank_service as bank

    fields = ("chunk_id", "type", "level", "content", "options", "correct_index", "rubric", "explanation")
    saved = 0
    for q in questions:
        try:
            with db.begin_nested():
                question = bank.create_question(db, {**{k: q.get(k) for k in fields}, "skill_id": skill_id},
                                                source="ai", review_status="auto_approved")  # fmt: skip
                question.is_active = True
                meta = db.get(ReviewQuestionMeta, question.question_id)
                meta.ai_check, meta.origin = q.get("ai_check"), origin
            saved += 1
        except bank.BankError as err:
            logger.warning("Soạn đề: bỏ câu không lưu được (kỹ năng %s): %s", skill_id, err)
    return saved


def _set(db: Session, job: ReviewGenerationJob, **fields) -> None:
    for key, value in fields.items():
        setattr(job, key, value)
    db.commit()


def run_job(job_id: int, session_factory, deps: Deps | None) -> None:
    """Chạy một việc soạn (luồng nền). Mọi lỗi đều kết thúc bằng 'failed' + thông báo dễ hiểu."""
    with session_factory() as db:
        job = db.get(ReviewGenerationJob, job_id)
        if job is None or job.status != "queued":
            return
        _set(db, job, status="running", step=1, started_at=datetime.now(UTC))
        try:
            if deps is None:
                raise GenerationError("ai_off", "ai_off")
            # 1) đoạn tài liệu (G3a) — thiếu ý thì viết thêm (Bước B)
            _ensure_ideas(db, job, deps)
            # 2) trắc nghiệm, 3) tự luận — G3b soạn + G3c cổng. Lưu NGAY sau mỗi vòng (vòng sau biết câu vừa lưu, không
            #    soạn trùng). Còn thiếu → thêm một vòng (tự luận hay hỏng phép "bài mẫu ≥ 7" — đo 25/11).
            _generate_steps(db, job, deps, ROUNDS)
            # Bước B dự phòng (26/11): soạn đề vẫn thiếu → viết thêm 1 đoạn (chưa đủ MAX_CHUNKS) rồi soạn thêm 1 vòng
            if job.kind == "exam" and missing_for_exam(db, job.skill_id) and _add_chunk(db, job, deps):
                _generate_steps(db, job, deps, 1)
            # 4) kiểm đủ đề (soạn bổ sung / ban đêm: thiếu một ít vẫn tính xong — lần sau soạn tiếp)
            _set(db, job, step=4)
            if job.kind == "exam" and missing_for_exam(db, job.skill_id):
                raise GenerationError("short", "short")
            _set(db, job, status="done", finished_at=datetime.now(UTC))
            logger.info("Soạn đề xong (%s): kỹ năng %s, lưu %d câu, %d lần gọi AI", job.kind, job.skill_id, job.saved,
                        job.calls)  # fmt: skip
            if job.kind == "exam" and TOPUP_ENABLED and missing_for(db, job.skill_id, "topup"):
                _request_topup(db, job.skill_id)
        except Exception as err:  # việc nền: mọi lỗi phải thành 'failed', không làm treo màn chờ
            _fail(db, job_id, err)


def _add_chunk(db: Session, job: ReviewGenerationJob, deps: Deps) -> bool:
    """Bước B dự phòng: viết thêm MỘT đoạn chủ đề con khác. Đã đủ MAX_CHUNKS / AI lỗi / không có nguồn → False."""
    from app.services import knowledge_service

    count = len(knowledge_repository.chunks_for_skill(db, job.skill_id))
    if count >= MAX_CHUNKS or deps.write_knowledge is None:
        return False
    _set(db, job, step=1)
    try:
        _with_waits(knowledge_service.ensure_chunks, db, job.skill_id, write=deps.write_knowledge,
                    embed=deps.embed or (lambda _t: None), model=deps.model, target=count + 1)  # fmt: skip
    except knowledge_service.KnowledgeError:
        logger.warning("Soạn đề: không viết thêm được đoạn dự phòng (kỹ năng %s)", job.skill_id)
        return False
    return True


def _generate_steps(db: Session, job: ReviewGenerationJob, deps: Deps, rounds: int) -> None:
    """Bước 2 (trắc nghiệm) và 3 (tự luận): mỗi bước tối đa `rounds` vòng soạn, lưu câu đạt ngay sau mỗi vòng."""
    for step, levels in ((2, ("recognize", "understand")), (3, ("easy", "advanced"))):
        _set(db, job, step=step)
        for _round in range(rounds):
            need = missing_for(db, job.skill_id, job.kind)
            if job.kind != "exam":  # Bước B: bổ sung / ban đêm không soạn quá số ý còn trống
                need = question_gen_service.cap_by_ideas(need, question_gen_service.free_ideas(db, job.skill_id))
            part = {lv: need[lv] for lv in levels if need.get(lv)}
            if not part:
                break
            result = _with_waits(question_gen_service.generate, db, job.skill_id, write=deps.write_questions,
                                 need=part, model=deps.model, solve=deps.solve, embed=deps.embed)  # fmt: skip
            job.calls += result["calls"] + result.get("solve_calls", 0)
            origin = "nightly" if job.kind == "nightly" else "on_demand"
            job.saved += save_questions(db, job.skill_id, result["questions"], origin)
            db.commit()


def _fail(db: Session, job_id: int, err: Exception) -> None:
    db.rollback()
    job = db.get(ReviewGenerationJob, job_id)
    if isinstance(err, AIUnavailableError):
        message = FAILED_AI
    elif isinstance(err, GenerationError) and err.code == "short":
        message = FAILED_SHORT
    else:
        message = FAILED_OTHER
        logger.exception("Soạn đề lỗi: kỹ năng %s", job.skill_id)
    _set(db, job, status="failed", error=message, finished_at=datetime.now(UTC))


def _request_topup(db: Session, skill_id: int) -> None:
    """D25: đủ một đề rồi → tự tạo việc soạn bổ sung tới ~30 câu ở nền (học viên không phải chờ)."""
    try:
        request(db, skill_id, None, kind="topup")
    except Exception:  # bổ sung lỗi không ảnh hưởng đề vừa soạn
        logger.warning("Không tạo được việc soạn bổ sung cho kỹ năng %s", skill_id, exc_info=True)


def recover_on_startup(session_factory) -> int:
    """Server khởi động lại → việc 'queued' / 'running' không còn luồng nào chạy → 'failed'."""
    try:
        with session_factory() as db:
            jobs = list(db.scalars(select(ReviewGenerationJob).where(ReviewGenerationJob.status.in_(ACTIVE))))
            for job in jobs:
                job.status, job.error, job.finished_at = "failed", FAILED_RESTART, datetime.now(UTC)
            db.commit()
            return len(jobs)
    except Exception:  # bảng chưa có (DB cũ) thì bỏ qua, không chặn khởi động
        logger.warning("Không dọn được việc soạn đề dở dang", exc_info=True)
        return 0
