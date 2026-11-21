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


class ChunkOut(BaseModel):
    """Đoạn tri thức RAG của kỹ năng — ô chọn "Đoạn tri thức" khi sửa / thêm câu (7.6)."""

    model_config = ConfigDict(from_attributes=True)

    chunk_id: int
    code: str | None
    title: str | None


# ─────────────── mức sẵn sàng (7.4) ───────────────


class SkillReadinessOut(BaseModel):
    skill_id: int
    skill: str
    by_level: dict[str, int]  # số câu ĐANG BẬT theo mức: recognize / understand / easy / advanced
    active: int
    mcq: int
    essay: int
    pending: int  # câu AI soạn chờ duyệt (chưa tính vào ôn được)
    target: int  # REVIEW_BANK_TARGET_PER_SKILL
    missing: list[str]  # mức chưa có câu nào (vd "tự luận nâng cao")


class CourseReadinessOut(BaseModel):
    course_id: int
    title: str
    ready: bool  # = plan_exam ráp được đề 15 câu (đúng điều kiện học viên bắt đầu ôn)
    missing: list[str]  # lý do chưa ôn được
    skill_count: int
    active: int
    mcq: int
    essay: int
    pending: int
    target: int  # mục tiêu × số kỹ năng
    skills: list[SkillReadinessOut]  # chỉ khi gọi ?course_id= (danh sách mọi khóa: rỗng cho nhẹ)


class ReadinessOut(BaseModel):
    target_per_skill: int
    structure: dict[str, int]  # khung đề: {"recognize": 6, "understand": 6, "easy": 2, "advanced": 1}
    courses: list[CourseReadinessOut]  # ôn được trước, rồi khóa nhiều câu hơn
    courses_without_questions: int  # thẻ "Khóa khác · N khóa · chưa có câu hỏi"


# ─────────────── Bài cần xem lại (17/11/2026) ───────────────

FlagReason = Literal[
    "needs_review", "near_pass", "instruction_in_answer", "evidence_missing", "keyword_fallback", "ai_stricter"
]
ItemLabel = Literal["full", "none"]


class FlagRubricOut(BaseModel):
    text: str
    max_points: float
    result: str  # full | none (partial: bài chấm trước 15/11)
    points: float
    evidence: str | None
    reason: str | None


class FlagReviewOut(BaseModel):
    by: int
    by_name: str
    at: str
    before: list[str]
    after: list[str]
    note: str | None
    score_before: float | None
    score_after: float


class FlagItemOut(BaseModel):
    attempt_id: int
    position: int
    user_id: int
    user_name: str
    user_email: str
    course_id: int
    course_title: str
    submitted_at: datetime | None
    attempt_score: float | None
    attempt_passed: bool | None
    question_id: int
    question_code: str | None
    level: str
    content: str
    model_answer: str | None
    text_answer: str | None
    max_points: float
    points: float
    feedback: str | None
    reasons: list[FlagReason]
    rubric: list[FlagRubricOut]
    review: FlagReviewOut | None  # None = chưa xem lại


class FlagPageOut(BaseModel):
    items: list[FlagItemOut]
    total: int
    page: int
    size: int
    open_total: int  # tổng câu đang chờ xem lại (không theo bộ lọc)
    resolved_total: int
    reason_counts: dict[str, int]  # số câu đang chờ theo từng lý do


class FlagResolveRequest(BaseModel):
    labels: list[ItemLabel] = Field(min_length=1, max_length=10)  # mỗi ý barem một nhãn, đúng thứ tự
    note: str | None = Field(default=None, max_length=500)


class FlagResolveOut(BaseModel):
    item: FlagItemOut
    score_changed: bool
    passed_changed: bool
    completed_course: bool  # đổi sang đạt → khóa vừa Hoàn thành


# ─────────────── Tìm kỹ năng theo tên (G1, 21/11/2026 — docs/Review-Skill-Search.md) ───────────────


class SkillAliasOut(BaseModel):
    skill_id: int
    skill: str


class SkillMatchOut(BaseModel):
    skill_id: int  # đại diện nhóm tên trùng: id có nhiều câu đang bật nhất
    skill: str
    score: float  # điểm gộp RRF (chỉ để xếp hạng)
    match: Literal["exact", "keyword", "vector", "hybrid"]
    cosine: float  # độ gần nghĩa với truy vấn (0 = không có từ nguồn vector)
    aliases: list[SkillAliasOut]  # các id khác cùng tên chuẩn hóa
    active_questions: int
    pending_questions: int


class SkillSearchOut(BaseModel):
    query: str
    confident: bool  # True = chắc chắn (khớp nguyên văn / rất gần và bỏ xa); False = để người dùng chọn
    results: list[SkillMatchOut]

