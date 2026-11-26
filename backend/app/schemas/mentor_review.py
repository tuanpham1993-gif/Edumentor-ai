"""Schema trang mentor duyệt câu ôn tập AI soạn (module 09 · Tuấn · G3f, 25/11/2026 — D19–D23)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.review_admin import ReportedQuestionOut, ReportReason


class MentorChunkOut(BaseModel):
    chunk_id: int
    title: str | None
    content: str


class MentorReportBrief(BaseModel):
    reason: ReportReason
    note: str | None


class MentorQuestionOut(ReportedQuestionOut):
    chunk: MentorChunkOut | None  # đoạn tài liệu AI đã dựa vào để soạn câu
    mentor_name: str | None  # ai đã duyệt / phản ánh (admin bác / sửa → tên admin)
    mentor_at: datetime | None
    report: MentorReportBrief | None  # phản ánh đang chờ admin


class MentorQueueCounts(BaseModel):
    pending: int
    passed: int
    reported: int


class MentorQueueOut(BaseModel):
    items: list[MentorQuestionOut]
    total: int
    page: int
    size: int
    counts: MentorQueueCounts


class MentorReportIn(BaseModel):
    reason: ReportReason
    note: str | None = Field(default=None, max_length=500)  # bắt buộc khi reason='other' (kiểm ở service)


class MentorActionOut(BaseModel):
    question_id: int
    mentor_status: Literal["passed", "reported"]
    is_active: bool
