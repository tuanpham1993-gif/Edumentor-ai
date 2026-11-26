"""Mentor duyệt câu ôn tập AI soạn + admin xử lý phản ánh (module 09 · Tuấn · G3f, 25/11/2026).

Docs: docs/Review-AI-Tu-Soan-On-Tap.md D19–D23, mục 7.2. Học viên KHÔNG phản ánh (D19).

Mentor (D21: chỉ câu AI soạn tự duyệt — `review_status='auto_approved'`; D23: chỉ xem + Đạt / Phản ánh lỗi):
    mentor_queue(db, status, skill_id, page, size)    hàng chờ: pending (chưa duyệt) | passed | reported
    mark_passed(db, mentor, question_id)              bấm Đạt
    report(db, mentor, question_id, reason, note)      bấm Phản ánh lỗi → câu TẮT NGAY (D20), chờ admin
Admin:
    open_count / list_page                             trang "Mentor phản ánh" (gom theo câu)
    resolve(db, admin, question_id, action, note)      'keep_disabled' (giữ tắt) | 'dismiss' (bác → bật lại, coi như Đạt)
    close_on_edit(db, admin_id, question_id, new_q)    admin sửa câu → phản ánh tự đóng, câu bật lại, coi như Đạt
    list_mentors / add_mentor(email) / remove_mentor   D22: admin gán / thu hồi vai trò mentor (không đụng admin)
Admin xử lý xong → chuông 'review_report' báo mentor đã phản ánh.
"""

from collections import Counter, defaultdict
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunk
from app.models.review_attempt import ReviewAttempt
from app.models.review_question import ReviewQuestion
from app.models.review_question_meta import ReviewQuestionMeta
from app.models.review_question_report import ReviewQuestionReport
from app.models.skill import Skills
from app.models.user import Users
from app.services import notification_service

REASON_TEXT = {
    "wrong_answer": "Đáp án đúng bị sai",
    "ambiguous": "Câu mơ hồ / có 2 đáp án đúng",
    "wrong_knowledge": "Sai kiến thức",
    "bad_rubric": "Barem tự luận không hợp lý",
    "other": "Khác",
}
MENTOR_REPORT = "mentor_report"  # review_question_meta.disabled_reason


class ReportError(Exception):
    """code: not_found | not_ai | conflict | invalid — router đổi sang mã HTTP."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _now() -> datetime:
    return datetime.now(UTC)


def _skill_name(db: Session, skill_id: int) -> str:
    return db.scalar(select(Skills.skill).where(Skills.skill_id == skill_id)) or ""


def _question_view(q: ReviewQuestion, meta: ReviewQuestionMeta | None, skill: str) -> dict:
    return {
        "question_id": q.question_id,
        "code": q.code,
        "skill_id": q.skill_id,
        "skill": skill,
        "type": q.type,
        "level": q.level,
        "content": q.content,
        "options": q.options,
        "correct_index": q.correct_index,
        "rubric": q.rubric,
        "explanation": q.explanation,
        "source": q.source,
        "review_status": meta.review_status if meta else "approved",
        "mentor_status": meta.mentor_status if meta else None,
        "is_active": q.is_active,
        "disabled_by_report": bool(meta and meta.disabled_reason == MENTOR_REPORT),
    }


# ─────────────── Mentor ───────────────

_QUEUE_FILTER = {
    "pending": ReviewQuestionMeta.mentor_status.is_(None) & ReviewQuestion.is_active.is_(True),
    "passed": ReviewQuestionMeta.mentor_status == "passed",
    "reported": ReviewQuestionMeta.mentor_status == "reported",
}


def mentor_queue(db: Session, *, status: str = "pending", skill_id: int | None = None, page=1, size=10) -> dict:
    """Câu AI soạn tự duyệt. 'pending': kỹ năng có nhiều lượt ôn xếp trước, rồi câu cũ trước; còn lại: mới duyệt trước."""
    base = (
        select(ReviewQuestion, ReviewQuestionMeta)
        .join(ReviewQuestionMeta, ReviewQuestionMeta.question_id == ReviewQuestion.question_id)
        .where(ReviewQuestionMeta.review_status == "auto_approved")
    )
    counts = {
        key: db.scalar(select(func.count()).select_from(base.where(cond).subquery()))
        for key, cond in _QUEUE_FILTER.items()
    }
    stmt = base.where(_QUEUE_FILTER[status])
    if skill_id is not None:
        stmt = stmt.where(ReviewQuestion.skill_id == skill_id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    if status == "pending":
        attempts = (
            select(ReviewAttempt.skill_id, func.count().label("n"))
            .where(ReviewAttempt.skill_id.is_not(None))
            .group_by(ReviewAttempt.skill_id)
            .subquery()
        )
        stmt = stmt.outerjoin(attempts, attempts.c.skill_id == ReviewQuestion.skill_id).order_by(
            func.coalesce(attempts.c.n, 0).desc(), ReviewQuestion.question_id
        )
    else:
        stmt = stmt.order_by(ReviewQuestionMeta.mentor_at.desc().nulls_last(), ReviewQuestion.question_id.desc())
    rows = db.execute(stmt.offset((page - 1) * size).limit(size)).all()

    skills = dict(db.execute(select(Skills.skill_id, Skills.skill).where(
        Skills.skill_id.in_({q.skill_id for q, _ in rows}))).all())  # fmt: skip
    chunks = {c.chunk_id: c for c in db.scalars(select(KnowledgeChunk).where(
        KnowledgeChunk.chunk_id.in_({q.chunk_id for q, _ in rows if q.chunk_id}))) }  # fmt: skip
    names = dict(db.execute(select(Users.user_id, Users.full_name).where(
        Users.user_id.in_({m.mentor_by for _, m in rows if m.mentor_by}))).all())  # fmt: skip
    open_reports = {r.question_id: r for r in db.scalars(select(ReviewQuestionReport).where(
        ReviewQuestionReport.question_id.in_([q.question_id for q, _ in rows]),
        ReviewQuestionReport.status == "open"))}  # fmt: skip

    items = []
    for q, meta in rows:
        chunk = chunks.get(q.chunk_id)
        report = open_reports.get(q.question_id)
        items.append({
            **_question_view(q, meta, skills.get(q.skill_id, "")),
            "chunk": {"chunk_id": chunk.chunk_id, "title": chunk.title, "content": chunk.content} if chunk else None,
            "mentor_name": names.get(meta.mentor_by),
            "mentor_at": meta.mentor_at,
            "report": {"reason": report.reason, "note": report.note} if report else None,
        })  # fmt: skip
    return {"items": items, "total": total, "page": page, "size": size, "counts": counts}


def _ai_question(db: Session, question_id: int) -> tuple[ReviewQuestion, ReviewQuestionMeta]:
    question = db.get(ReviewQuestion, question_id)
    if question is None:
        raise ReportError("not_found", "Không tìm thấy câu hỏi.")
    meta = db.get(ReviewQuestionMeta, question_id)
    if meta is None or meta.review_status != "auto_approved":
        raise ReportError("not_ai", "Mentor chỉ duyệt câu AI soạn tự duyệt (câu soạn tay đã có người duyệt).")
    return question, meta


def mark_passed(db: Session, mentor: Users, question_id: int) -> dict:
    question, meta = _ai_question(db, question_id)
    if meta.mentor_status == "reported":
        raise ReportError("conflict", "Câu đang bị phản ánh, chờ admin xử lý.")
    if meta.mentor_status == "passed":
        raise ReportError("conflict", "Câu đã được duyệt Đạt.")
    if not question.is_active:
        raise ReportError("conflict", "Câu đang tắt, không cần duyệt.")
    meta.mentor_status, meta.mentor_by, meta.mentor_at = "passed", mentor.user_id, _now()
    db.commit()
    return {"question_id": question_id, "mentor_status": "passed", "is_active": question.is_active}


def report(db: Session, mentor: Users, question_id: int, reason: str, note: str | None) -> dict:
    """D20: câu TẮT NGAY (disabled_reason='mentor_report'), chờ admin. Câu đã Đạt vẫn phản ánh được (thấy lỗi sau)."""
    question, meta = _ai_question(db, question_id)
    note = (note or "").strip()[:500] or None
    if reason == "bad_rubric" and question.type != "essay":
        raise ReportError("invalid", "Lý do 'Barem tự luận không hợp lý' chỉ dùng cho câu tự luận.")
    if reason == "other" and not note:
        raise ReportError("invalid", "Chọn 'Khác' thì cần ghi chú lỗi là gì.")
    if meta.mentor_status == "reported":
        raise ReportError("conflict", "Câu này đã bị phản ánh, đang chờ admin xử lý.")
    if not question.is_active:
        raise ReportError("conflict", "Câu đang tắt, không cần phản ánh.")

    db.add(ReviewQuestionReport(question_id=question_id, user_id=mentor.user_id, reason=reason, note=note))
    question.is_active = False
    meta.disabled_reason = MENTOR_REPORT
    meta.mentor_status, meta.mentor_by, meta.mentor_at = "reported", mentor.user_id, _now()
    try:
        db.commit()
    except IntegrityError:  # hai mentor bấm cùng lúc → index "một phản ánh đang mở / câu"
        db.rollback()
        raise ReportError("conflict", "Câu này đã bị phản ánh, đang chờ admin xử lý.") from None
    return {"question_id": question_id, "mentor_status": "reported", "is_active": False}


# ─────────────── Admin: phản ánh ───────────────


def open_count(db: Session) -> int:
    """Số CÂU đang có phản ánh chờ xử lý (số đỏ trên menu)."""
    return db.scalar(
        select(func.count(func.distinct(ReviewQuestionReport.question_id))).where(ReviewQuestionReport.status == "open")
    )


def list_page(db: Session, *, status: str = "open", reason=None, skill_id=None, page=1, size=10) -> dict:
    """Gom theo câu hỏi. status: open | handled (đã xử lý) | all. Câu có phản ánh mới nhất trước."""
    stmt = select(ReviewQuestionReport, Users.full_name).join(Users, Users.user_id == ReviewQuestionReport.user_id)
    if status == "open":
        stmt = stmt.where(ReviewQuestionReport.status == "open")
    elif status == "handled":
        stmt = stmt.where(ReviewQuestionReport.status != "open")
    rows = db.execute(
        stmt.order_by(ReviewQuestionReport.created_at.desc(), ReviewQuestionReport.report_id.desc())
    ).all()

    grouped: dict[int, list] = defaultdict(list)
    for r, name in rows:
        grouped[r.question_id].append((r, name))
    questions = {q.question_id: q for q in db.scalars(select(ReviewQuestion).where(
        ReviewQuestion.question_id.in_(grouped)))}  # fmt: skip
    metas = {m.question_id: m for m in db.scalars(select(ReviewQuestionMeta).where(
        ReviewQuestionMeta.question_id.in_(grouped)))}  # fmt: skip
    skills = dict(db.execute(select(Skills.skill_id, Skills.skill).where(
        Skills.skill_id.in_({q.skill_id for q in questions.values()}))).all())  # fmt: skip

    items = []
    for question_id, reports in grouped.items():
        q = questions[question_id]
        if skill_id is not None and q.skill_id != skill_id:
            continue
        if reason and not any(r.reason == reason for r, _ in reports):
            continue
        items.append({
            "question": _question_view(q, metas.get(question_id), skills.get(q.skill_id, "")),
            "people": len({r.user_id for r, _ in reports}),
            "reason_counts": dict(Counter(r.reason for r, _ in reports)),
            "latest_at": reports[0][0].created_at,
            "reports": [
                {"report_id": r.report_id, "user_name": name, "reason": r.reason, "note": r.note, "status": r.status,
                 "admin_note": r.admin_note, "created_at": r.created_at, "resolved_at": r.resolved_at}
                for r, name in reports
            ],
        })  # fmt: skip
    return {"items": items[(page - 1) * size : page * size], "total": len(items), "page": page, "size": size,
            "open_total": open_count(db)}  # fmt: skip


def _close(db: Session, question_id: int, admin_id: int, status: str, note: str | None) -> list[ReviewQuestionReport]:
    reports = list(db.scalars(select(ReviewQuestionReport).where(
        ReviewQuestionReport.question_id == question_id, ReviewQuestionReport.status == "open")))  # fmt: skip
    now = _now()
    for r in reports:
        r.status, r.resolved_by, r.resolved_at = status, admin_id, now
        r.admin_note = (note or "").strip()[:500] or None
    return reports


def _notify(db: Session, reports: list[ReviewQuestionReport], skill: str, outcome: str) -> None:
    """Chuông cho mentor đã phản ánh: admin đã xử lý thế nào."""
    for user_id in {r.user_id for r in reports}:
        notification_service.notify(db, user_id, "review_report", f"Câu hỏi bạn phản ánh {outcome}.",
                                    body=f"Kỹ năng: {skill}" if skill else None, link="/mentor/review")  # fmt: skip


def _mark_passed_by(meta: ReviewQuestionMeta, admin_id: int) -> None:
    meta.disabled_reason = None
    meta.mentor_status, meta.mentor_by, meta.mentor_at = "passed", admin_id, _now()


def resolve(db: Session, admin: Users, question_id: int, action: str, note: str | None = None) -> dict:
    """'dismiss' (bác): phản ánh 'dismissed', câu bật lại (nếu bị tắt do phản ánh), coi như Đạt.
    'keep_disabled' (giữ tắt): phản ánh 'resolved', câu tắt hẳn (bác về sau không tự bật lại)."""
    question = db.get(ReviewQuestion, question_id)
    if question is None:
        raise ReportError("not_found", "Không tìm thấy câu hỏi.")
    meta = db.get(ReviewQuestionMeta, question_id)
    if action == "dismiss":
        reports = _close(db, question_id, admin.user_id, "dismissed", note)
        if reports and meta is not None:
            if meta.disabled_reason == MENTOR_REPORT:
                from app.services import review_bank_service as bank

                question.is_active = bank.is_latest(db, question)
            _mark_passed_by(meta, admin.user_id)
        outcome = "đã được admin xem lại: câu đúng, đã bật lại"
    elif action == "keep_disabled":
        reports = _close(db, question_id, admin.user_id, "resolved", note)
        question.is_active = False
        if meta is not None:
            meta.disabled_reason = None  # admin chủ động giữ tắt
        outcome = "đã được admin xác nhận lỗi, câu đã tắt"
    else:
        raise ReportError("invalid", "Hành động không hợp lệ (dismiss | keep_disabled).")
    if not reports:
        db.rollback()
        raise ReportError("not_found", "Câu này không có phản ánh nào đang chờ xử lý.")
    _notify(db, reports, _skill_name(db, question.skill_id), outcome)
    db.commit()
    return {"question_id": question_id, "closed": len(reports), "is_active": question.is_active}


def close_on_edit(db: Session, admin_id: int, question_id: int, new_question: ReviewQuestion) -> int:
    """Admin sửa câu (tại chỗ hoặc phiên bản mới) → phản ánh đang mở của câu cũ 'resolved'; câu (bản mới) bật lại và
    coi như Đạt vì đã có admin xem (D20). Không commit."""
    reports = _close(db, question_id, admin_id, "resolved", "Câu đã được sửa")
    if reports:
        old_meta = db.get(ReviewQuestionMeta, question_id)
        new_meta = db.get(ReviewQuestionMeta, new_question.question_id)
        if old_meta is not None and old_meta.disabled_reason == MENTOR_REPORT:
            new_question.is_active = True
            old_meta.disabled_reason = None
        if new_meta is not None:
            _mark_passed_by(new_meta, admin_id)
        _notify(db, reports, _skill_name(db, new_question.skill_id), "đã được admin sửa và bật lại")
    return len(reports)


# ─────────────── Admin: tài khoản mentor (D22) ───────────────


def _mentor_view(u: Users) -> dict:
    return {"user_id": u.user_id, "full_name": u.full_name, "email": u.email, "is_active": u.is_active}


def list_mentors(db: Session) -> list[dict]:
    rows = db.scalars(select(Users).where(Users.role == "mentor").order_by(Users.full_name))
    passed = dict(db.execute(select(ReviewQuestionMeta.mentor_by, func.count()).where(
        ReviewQuestionMeta.mentor_status == "passed").group_by(ReviewQuestionMeta.mentor_by)).all())  # fmt: skip
    reported = dict(db.execute(select(ReviewQuestionReport.user_id, func.count()).group_by(
        ReviewQuestionReport.user_id)).all())  # fmt: skip
    return [{**_mentor_view(u), "passed": passed.get(u.user_id, 0), "reported": reported.get(u.user_id, 0)}
            for u in rows]  # fmt: skip


def add_mentor(db: Session, email: str) -> dict:
    user = db.scalar(select(Users).where(func.lower(Users.email) == email.strip().lower()))
    if user is None:
        raise ReportError("not_found", "Không tìm thấy tài khoản có email này.")
    if user.role == "admin":
        raise ReportError("conflict", "Không đổi vai trò của tài khoản admin.")
    if user.role == "mentor":
        raise ReportError("conflict", "Tài khoản này đã là mentor.")
    user.role = "mentor"
    db.commit()
    return {**_mentor_view(user), "passed": 0, "reported": 0}


def remove_mentor(db: Session, user_id: int) -> None:
    user = db.get(Users, user_id)
    if user is None or user.role != "mentor":
        raise ReportError("not_found", "Không tìm thấy mentor này.")
    user.role = "student"
    db.commit()
