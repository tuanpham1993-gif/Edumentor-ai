"""Khuôn chung cho "AI" của module 09 (Tuấn · GĐ2, 09/11/2026).

Mọi AI (mock, thật) nhận CÙNG một GenerationRequest và trả về danh sách câu hỏi dạng dict
(định dạng ở ai/review/validator.py). review_service không cần biết đang dùng AI nào (AI_MODE).
"""

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class AIUnavailableError(Exception):
    """AI không dùng được (chưa cấu hình, hết lượt, mất mạng…) → review_service dùng ngân hàng dự phòng."""


@dataclass
class RetrievedChunk:
    """Một đoạn tri thức RAG tìm được. score = cosine (None khi chưa có embedding)."""

    chunk_id: int
    code: str | None
    title: str | None
    content: str
    score: float | None = None


@dataclass
class GenerationRequest:
    """Yêu cầu sinh câu hỏi cho MỘT kỹ năng.

    need:        số câu cần theo mức độ, vd {"recognize": 2, "understand": 1, "easy": 1}
    chunks:      đoạn tri thức RAG vừa truy xuất (ngữ cảnh cho AI)
    candidates:  câu đang có trong ngân hàng của kỹ năng (mock bốc từ đây; AI thật dùng để tránh trùng)
    avoid_question_ids: câu của lượt trước — tránh lặp lại nếu còn câu khác (A1)
    system_prompt / prompt: prompt đã dựng (lưu vết — A4)
    """

    course_title: str
    skill_id: int
    skill_name: str
    need: dict[str, int]
    chunks: list[RetrievedChunk] = field(default_factory=list)
    candidates: list[dict] = field(default_factory=list)
    avoid_question_ids: set[int] = field(default_factory=set)
    system_prompt: str = ""
    prompt: str = ""
    pending_count: int = 0  # câu AI đã soạn đang chờ duyệt (7.5c) — tính vào ngưỡng "đủ câu"


@dataclass
class EssayGrade:
    """Kết quả chấm chi tiết MỘT câu (B7): items như grade_essay + nhận xét chung + phiên bản prompt + số lần gọi."""

    items: list[dict]
    feedback: str | None = None
    prompt_version: str | None = None
    attempts: int = 1


class ReviewAI(ABC):
    name = "base"

    @abstractmethod
    def generate_questions(self, request: GenerationRequest, rng: random.Random) -> list[dict]:
        """Trả về đúng số câu theo request.need (validator kiểm lại). Lỗi AI → AIUnavailableError."""

    @abstractmethod
    def grade_essay(self, question: dict, answer: str | None) -> list[dict]:
        """Chấm MỘT câu tự luận theo barem question["rubric"] (H1 — chấm từng câu riêng).

        Trả một kết quả cho MỖI ý, đúng thứ tự barem:
            {"result": "full" | "none", "points": số điểm của ý, "evidence": câu trích | None}
        (validator.grading_errors kiểm lại). Lỗi AI → AIUnavailableError.
        """

    def grade_essay_detailed(self, question: dict, answer: str | None) -> EssayGrade:
        """Như grade_essay + feedback / prompt_version / attempts (B7). Mặc định bọc grade_essay — AI nào có thêm
        thông tin (Gemini) thì ghi đè. Pipeline khối 4 gọi hàm này."""
        return EssayGrade(items=self.grade_essay(question, answer))
