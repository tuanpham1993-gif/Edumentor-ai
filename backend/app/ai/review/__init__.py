"""Lớp AI của module 09 Ôn tập (Tuấn) — tách riêng khỏi ai/client.py, ai/validators.py (chatbot của Tâm).

    base.py            khuôn chung ReviewAI + GenerationRequest
    mock_ai.py         AI giả (AI_MODE=mock): bốc câu ngân hàng gắn với đoạn RAG; chấm bằng từ khóa
    keyword_grader.py  chấm tự luận theo từ khóa (mock + dự phòng khi AI thật lỗi)
    validator.py       kiểm tra câu hỏi + kết quả chấm (dùng chung cho ngân hàng soạn tay và AI)
    get_review_ai() chọn AI theo settings.AI_MODE
"""

from app.ai.review.base import AIUnavailableError, ReviewAI
from app.ai.review.mock_ai import MockAI
from app.core.config import settings


def get_review_ai() -> ReviewAI:
    """AI_MODE=mock → MockAI. AI_MODE=real → RealAI (Gemini, 12/11) — thiếu LLM_API_KEY / LLM_MODEL thì báo
    không dùng được, review_service tự rơi về dự phòng (ngân hàng + chấm từ khóa — A6)."""
    if settings.AI_MODE == "mock":
        return MockAI()
    if settings.AI_MODE == "real":
        from app.ai.review.real_ai import RealAI, review_llm

        key, model = review_llm()  # REVIEW_LLM_* (riêng Ôn tập) hoặc LLM_* (chung chatbot)
        if key and model:
            return RealAI()
        return _UnavailableAI("AI_MODE='real' nhưng chưa cấu hình LLM_API_KEY / LLM_MODEL")
    return _UnavailableAI(f"AI_MODE='{settings.AI_MODE}' không hợp lệ (mock | real)")


class _UnavailableAI(ReviewAI):
    name = "unavailable"

    def __init__(self, reason: str):
        self.reason = reason

    def generate_questions(self, request, rng):
        raise AIUnavailableError(self.reason)

    def grade_essay(self, question, answer):
        raise AIUnavailableError(self.reason)
