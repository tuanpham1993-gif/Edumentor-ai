"""Schema quản trị ngân hàng câu hỏi ôn tập (module 09 · Tuấn · GĐ7 bước 7.3, 13/11/2026).

Khác schema học viên (`schemas/review.py`): ở đây LUÔN có đáp án / barem — chỉ admin gọi được.
Kiểm tra nội dung câu (4 lựa chọn, barem tổng 10…) do `ai/review/validator.py` làm ở service — dùng chung với seed
và câu AI sinh, không viết lại bằng Pydantic.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

QuestionType = Literal["mcq", "essay"]
QuestionLevel = Literal["recognize", "understand", "easy", "advanced"]
ReviewStatus = Literal["pending", "approved", "rejected"]


# ─────────────── vào ───────────────


class RubricItem(BaseModel):
    text: str
    max_points: int | float  # giữ số nguyên khi admin gửi 3 (không thành 3.0)
    main_keywords: list[str] = []
    sub_keywords: list[str] = []


class QuestionCreate(BaseModel):
    code: str | None = Field(default=None, max_length=50)
    skill_id: int
    chunk_id: int | None = None
    type: QuestionType
    level: QuestionLevel
    content: str
    options: list[str] | None = None  # chỉ mcq
    correct_index: int | None = None  # chỉ mcq
    rubric: list[RubricItem] | None = None  # chỉ essay
    explanation: str | None = None
    exclusion_group: str | None = Field(default=None, max_length=50)


class QuestionUpdate(BaseModel):
    """Chỉ gửi trường muốn đổi (service dùng exclude_unset). Không đổi được `type` — đổi loại = câu mới."""

    skill_id: int | None = None
    chunk_id: int | None = None
    level: QuestionLevel | None = None
    content: str | None = None
    options: list[str] | None = None
    correct_index: int | None = None
    rubric: list[RubricItem] | None = None
    explanation: str | None = None
    exclusion_group: str | None = Field(default=None, max_length=50)
    minor: bool = False  # "Sửa nhỏ" (QT5) — không tạo phiên bản; chỉ giải thích / đoạn tri thức / nhóm / chính tả đề
    note: str | None = None  # ghi chú cho phiên bản mới


class ApproveRequest(BaseModel):
    """Duyệt câu AI soạn → cấp mã + bật. Mã TÙY CHỌN (nhóm chốt 14/11): bỏ trống → hệ thống tự cấp mã gợi ý
    (QT9: "VAR-TN-15"); admin nhập mã khác thì dùng mã đó."""

    model_config = ConfigDict(str_strip_whitespace=True)

    code: str | None = Field(default=None, max_length=50)

    @field_validator("code")
    @classmethod
    def _blank_is_none(cls, value: str | None) -> str | None:
        return value or None  # "" / "   " (sau strip) = không nhập


class SuggestedCodeOut(BaseModel):
    code: str | None  # None = kỹ năng chưa có câu nào có mã → admin tự nhập


# ─────────────── ra ───────────────


class QuestionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question_id: int
    code: str | None
    skill_id: int
    skill_name: str | None
    type: QuestionType
    level: QuestionLevel
    content: str
    source: str
    is_active: bool
    family_id: int
    version: int
    review_status: ReviewStatus
    used_count: int  # số bài làm đã dùng câu này (> 0 → sửa nội dung sẽ tạo phiên bản mới)
    created_at: datetime


class QuestionPage(BaseModel):
    total: int
    page: int
    size: int
    items: list[QuestionListItem]


class VersionOut(BaseModel):
    question_id: int
    version: int
    code: str | None
    is_active: bool
    used_count: int
    created_at: datetime
    created_by: int | None
    change_note: str | None


class QuestionDetail(QuestionListItem):
    chunk_id: int | None
    options: list[str] | None
    correct_index: int | None
    rubric: list[dict] | None
    explanation: str | None
    exclusion_group: str | None
    change_note: str | None
    versions: list[VersionOut]  # mọi phiên bản cùng họ, mới nhất trước


class EditResultOut(BaseModel):
    question: QuestionDetail  # câu hiện hành (dòng mới nếu vừa tạo phiên bản)
    versioned: bool
    changed: list[str]


class DeleteResultOut(BaseModel):
    result: Literal["deleted", "deactivated"]
