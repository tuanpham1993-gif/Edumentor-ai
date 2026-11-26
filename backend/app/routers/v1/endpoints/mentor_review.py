"""Router mentor duyệt câu ôn tập AI soạn (module 09 · Tuấn · G3f, 25/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md D19–D23).

Chỉ mentor và admin (`require_mentor`: chưa đăng nhập 401, học viên 403). Mentor chỉ XEM + Đạt / Phản ánh lỗi (D23).

    GET   /api/mentor/review-questions?status=pending|passed|reported&skill_id=  — hàng chờ câu AI soạn
    POST  /api/mentor/review-questions/{question_id}/pass                        — Đạt
    POST  /api/mentor/review-questions/{question_id}/report                      — Phản ánh lỗi → câu tắt ngay (D20)
"""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_mentor
from app.models.user import Users
from app.schemas.mentor_review import MentorActionOut, MentorQueueOut, MentorReportIn
from app.services import review_report_service as service

router = APIRouter()

_STATUS = {"not_found": 404, "not_ai": 409, "conflict": 409, "invalid": 422}


def _error(err: service.ReportError) -> HTTPException:
    return HTTPException(_STATUS.get(err.code, 400), err.message)


@router.get("/review-questions", response_model=MentorQueueOut, summary="[Mentor] Hàng chờ duyệt câu AI soạn")
def mentor_queue(
    status_: Literal["pending", "passed", "reported"] = Query("pending", alias="status"),
    skill_id: int | None = Query(None, ge=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    _: Users = Depends(require_mentor),
    db: Session = Depends(get_db),
):
    return service.mentor_queue(db, status=status_, skill_id=skill_id, page=page, size=size)


@router.post("/review-questions/{question_id}/pass", response_model=MentorActionOut, summary="[Mentor] Đạt")
def pass_question(question_id: int, mentor: Users = Depends(require_mentor), db: Session = Depends(get_db)):
    try:
        return service.mark_passed(db, mentor, question_id)
    except service.ReportError as err:
        raise _error(err) from None


@router.post("/review-questions/{question_id}/report", response_model=MentorActionOut,
             summary="[Mentor] Phản ánh lỗi — câu tắt ngay, chờ admin")  # fmt: skip
def report_question(
    question_id: int, body: MentorReportIn, mentor: Users = Depends(require_mentor), db: Session = Depends(get_db)
):
    try:
        return service.report(db, mentor, question_id, body.reason, body.note)
    except service.ReportError as err:
        raise _error(err) from None
