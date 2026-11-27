"""AI giả cho giai đoạn 1 — AI_MODE=mock, 0 đồng (module 09 · Tuấn · GĐ2, 09/11/2026).

Không gọi LLM. "Sinh đề" = bốc câu trong ngân hàng của kỹ năng, ƯU TIÊN câu gắn với các đoạn tri thức
mà RAG vừa truy xuất (A4: RAG quyết định thật sự đề gồm những câu nào), tránh câu của lượt trước.
pick_from_bank() cũng là "ngân hàng dự phòng" (A6) khi AI lỗi: bốc không cần ưu tiên đoạn RAG.
"""

import logging
import random

from app.ai.review import keyword_grading
from app.ai.review.base import GenerationRequest, ReviewAI

logger = logging.getLogger(__name__)
ESSAY_FIRST = {"advanced": 0, "easy": 1}  # thứ tự BỐC câu (7.5b); mức khác bốc sau, giữ thứ tự trong `need`


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
    G3e P2 (D29): avoid_question_ids có thể là {question_id: mức phạt} — phải lặp thì lặp câu phạt THẤP (lượt cũ) trước.
    Bước A (25/11): câu có "idea" ([(chunk_id, số câu nguồn)] — question_idea) → một đề không lấy 2 câu CÙNG LOẠI chung
    câu nguồn; ràng buộc MỀM: không đủ câu khác ý thì mới lấy câu trùng ý.
    """
    prefer = prefer_chunk_ids or set()
    avoid = avoid_question_ids or set()
    penalty = avoid if isinstance(avoid, dict) else dict.fromkeys(avoid, 1)
    by_level: dict[str, list[dict]] = {}
    used: set[tuple] = set()
    groups: set[str] = set()
    # 7.5b (27/11): bốc TỰ LUẬN trước (ít câu: 2 dễ + 1 nâng cao) rồi mới trắc nghiệm — câu trắc nghiệm cùng nhóm loại
    # trừ với câu tự luận đã chọn dễ né hơn (12 câu / ngân hàng lớn hơn). Kết quả vẫn trả theo thứ tự `need`.
    for level in sorted(need, key=lambda lv: ESSAY_FIRST.get(lv, len(ESSAY_FIRST))):
        count = need[level]
        pool = [q for q in candidates if q["level"] == level]
        rng.shuffle(pool)
        pool.sort(
            key=lambda q: (
                penalty.get(q["question_id"], 0),
                bool(prefer) and q.get("chunk_id") not in prefer,
            )
        )
        chosen, skipped = [], []
        for q in pool:
            if len(chosen) == count:
                break
            keys = {(q.get("type"), *t) for t in q.get("idea") or ()}
            group = q.get("exclusion_group")
            if keys & used or (group and group in groups):
                skipped.append(q)
                continue
            chosen.append(q)
            used |= keys
            if group and q.get("type") == "essay":  # chỉ câu TỰ LUẬN đã chọn chặn nhóm của nó
                groups.add(group)
        fill = skipped[: count - len(chosen)]
        if any(q.get("exclusion_group") in groups for q in fill):
            # Ràng buộc MỀM: thiếu câu khác nhóm thì vẫn ra đủ đề, không chặn người học — chỉ ghi lại
            logger.warning("Ráp đề: mức %s thiếu câu khác nhóm loại trừ — lấy %d câu trùng nhóm", level, len(fill))
        by_level[level] = chosen + fill
    return [q for level in need for q in by_level.get(level, [])]


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
        return keyword_grading.grade_essay(question["rubric"], answer, question.get("content"))
