"""Schema API ôn tập (module 09 · Tuấn · GĐ2, 09/11/2026).

Nguyên tắc bảo mật: đề trả về cho người làm (AttemptOut) KHÔNG có correct_index, rubric, explanation
— chỉ trả sau khi nộp (GĐ3, lịch sử bài làm).
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

QuestionType = Literal["mcq", "essay"]
QuestionLevel = Literal["recognize", "understand", "easy", "advanced"]
AttemptStatus = Literal["in_progress", "grading", "graded"]

MAX_ESSAY_CHARS = 5000


class ReviewSkillOut(BaseModel):
    skill_id: int
    skill: str


class ReviewStructureOut(BaseModel):
    """Cấu trúc đề (chốt 09/11) — hiển thị ở màn Bắt đầu ôn tập."""

    recognize: int
    understand: int
    easy: int
    advanced: int
    total_questions: int
    max_score: float


class ReviewBlockedOut(BaseModel):
    """Lý do chưa thể ôn tập. code: not_enrolled | abandoned | no_question_bank."""

    code: str
    message: str


class AttemptSummaryOut(BaseModel):
    attempt_id: int
    status: AttemptStatus
    score: float | None
    passed: bool | None
    started_at: datetime
    submitted_at: datetime | None


class ReviewInfoOut(BaseModel):
    course_id: int
    course_title: str
    skills: list[ReviewSkillOut]
    structure: ReviewStructureOut
    pass_score: float
    can_start: bool
    blocked: ReviewBlockedOut | None
    in_progress_attempt_id: int | None
    attempts: list[AttemptSummaryOut]


class AttemptQuestionOut(BaseModel):
    position: int
    type: QuestionType
    level: QuestionLevel
    skill_id: int
    skill: str
    content: str
    options: list[str] | None  # đã XÁO theo option_order; None với tự luận
    max_points: float
    selected_index: int | None  # vị trí người dùng chọn TRÊN MÀN HÌNH (0..3)
    text_answer: str | None


class AttemptOut(BaseModel):
    attempt_id: int
    course_id: int
    course_title: str
    status: AttemptStatus
    started_at: datetime
    resumed: bool = False  # True = trả lại lượt đang làm dở thay vì tạo đề mới
    answered: int
    total_questions: int
    questions: list[AttemptQuestionOut]


class AnswerIn(BaseModel):
    """Một câu trả lời. TN gửi selected_index (null = bỏ chọn); TL gửi text_answer."""

    position: int = Field(ge=1)
    selected_index: int | None = Field(default=None, ge=0, le=3)
    text_answer: str | None = Field(default=None, max_length=MAX_ESSAY_CHARS)


class SaveAnswersRequest(BaseModel):
    answers: list[AnswerIn] = Field(min_length=1, max_length=50)

    @field_validator("answers")
    @classmethod
    def unique_positions(cls, answers: list[AnswerIn]) -> list[AnswerIn]:
        positions = [a.position for a in answers]
        if len(set(positions)) != len(positions):
            raise ValueError("Mỗi câu (position) chỉ được gửi một lần")
        return answers
