"""AI giả cho giai đoạn 1 — AI_MODE=mock, 0 đồng (module 09 · Tuấn · GĐ2, 09/11/2026).

Không gọi LLM. "Sinh đề" = bốc câu trong ngân hàng của kỹ năng, ƯU TIÊN câu gắn với các đoạn tri thức
mà RAG vừa truy xuất (A4: RAG quyết định thật sự đề gồm những câu nào), tránh câu của lượt trước.
pick_from_bank() cũng là "ngân hàng dự phòng" (A6) khi AI lỗi: bốc không cần ưu tiên đoạn RAG.
"""

import random

from app.ai.review import keyword_grader
from app.ai.review.base import GenerationRequest, ReviewAI


def pick_from_bank(
    candidates: list[dict],
    need: dict[str, int],
    rng: random.Random,
    *,
    prefer_chunk_ids: set[int] | None = None,
    avoid_question_ids: set[int] | None = None,
) -> list[dict]:
    """Bốc câu cho từng mức độ theo thứ tự ưu tiên:
    1) thuộc đoạn RAG + chưa có ở lượt trước → 2) chưa có ở lượt trước → 3) còn lại (đành lặp lại).
    Trong cùng một nhóm ưu tiên thì ngẫu nhiên. Thiếu câu → trả về ít hơn (validator sẽ báo).
    """
    prefer = prefer_chunk_ids or set()
    avoid = avoid_question_ids or set()
    picked = []
    for level, count in need.items():
        pool = [q for q in candidates if q["level"] == level]
        rng.shuffle(pool)
        pool.sort(
            key=lambda q: (
                q["question_id"] in avoid,
                bool(prefer) and q.get("chunk_id") not in prefer,
            )
        )
        picked += pool[:count]
    return picked


class MockAI(ReviewAI):
    name = "mock"

    def generate_questions(self, request: GenerationRequest, rng: random.Random) -> list[dict]:
        return pick_from_bank(
            request.candidates,
            request.need,
            rng,
            prefer_chunk_ids={c.chunk_id for c in request.chunks},
            avoid_question_ids=request.avoid_question_ids,
        )

    def grade_essay(self, question: dict, answer: str | None) -> list[dict]:
        return keyword_grader.grade_essay(question["rubric"], answer)
