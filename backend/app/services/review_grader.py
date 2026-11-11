"""Chấm bài ôn tập — thang 10 (A3, A10–A12, H1 — chốt 09/11) (module 09 · Tuấn · GĐ3, 09/11/2026).

  - Trắc nghiệm: CODE so đáp án (không dùng AI — H1). selected_index là vị trí TRÊN MÀN HÌNH nên đổi về
    lựa chọn gốc qua option_order. Đúng = 0,5đ; sai / bỏ trống = 0 (không trừ điểm — A12).
  - Tự luận: AI chấm TỪNG câu riêng theo barem từng ý → điểm câu /10 → quy đổi về điểm câu
    (dễ 1đ, nâng cao 2đ). AI lỗi / kết quả sai quy tắc → chấm bằng từ khóa (keyword_grader) để vẫn có điểm.
  - Bỏ trống tự luận → 0, không gọi AI.
Ghi điểm vào từng ReviewAnswer (chỉ sửa object — review_service commit).
"""

import logging

from app.ai.review import keyword_grader
from app.ai.review.base import AIUnavailableError, ReviewAI
from app.ai.review.validator import grading_errors
from app.models.review_attempt import ReviewAnswer

logger = logging.getLogger(__name__)


def displayed_correct_index(answer: ReviewAnswer) -> int:
    """Vị trí đáp án đúng TRÊN MÀN HÌNH (sau khi xáo)."""
    return answer.option_order.index(answer.question.correct_index)


def is_mcq_correct(answer: ReviewAnswer) -> bool:
    if answer.selected_index is None:
        return False
    return answer.option_order[answer.selected_index] == answer.question.correct_index


def _question_dict(answer: ReviewAnswer) -> dict:
    q = answer.question
    return {"content": q.content, "rubric": q.rubric, "explanation": q.explanation}


def grade_essay(ai: ReviewAI, answer: ReviewAnswer) -> tuple[list[dict], str | None]:
    """Trả (kết quả từng ý, lỗi AI nếu phải dùng chấm từ khóa)."""
    rubric = answer.question.rubric
    if not (answer.text_answer and answer.text_answer.strip()):
        return [{"result": "none", "points": 0.0, "evidence": None} for _ in rubric], None
    try:
        results = ai.grade_essay(_question_dict(answer), answer.text_answer)
        problems = grading_errors(results, rubric)
        if not problems:
            return results, None
        error = "; ".join(problems[:3])
    except AIUnavailableError as err:
        error = f"AI không dùng được: {err}"
    logger.warning("Ôn tập: chấm tự luận câu %s bằng từ khóa (%s)", answer.position, error)
    return keyword_grader.grade_essay(rubric, answer.text_answer, answer.question.content), error


def grade_answers(answers: list[ReviewAnswer], ai: ReviewAI) -> tuple[float, dict]:
    """Chấm tất cả câu, ghi points / rubric_result vào từng câu. Trả (tổng điểm CHƯA làm tròn, vết chấm)."""
    total = 0.0
    fallbacks = []
    for answer in answers:
        max_points = float(answer.max_points)
        if answer.question.type == "mcq":
            points = max_points if is_mcq_correct(answer) else 0.0
        else:
            results, error = grade_essay(ai, answer)
            answer.rubric_result = results
            points = sum(r["points"] for r in results) / 10 * max_points
            if error:
                fallbacks.append({"position": answer.position, "error": error})
        answer.points = round(points, 2)
        total += points
    return total, {"ai": ai.name, "keyword_fallback": fallbacks}
