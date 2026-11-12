"""Chấm bài ôn tập — thang 10 (A3, A10–A12, H1 — chốt 09/11) (module 09 · Tuấn · GĐ3, 09/11/2026).

  - Trắc nghiệm: CODE so đáp án (không dùng AI — H1). selected_index là vị trí TRÊN MÀN HÌNH nên đổi về
    lựa chọn gốc qua option_order. Đúng = 0,5đ; sai / bỏ trống = 0 (không trừ điểm — A12).
  - Tự luận: AI chấm TỪNG câu riêng theo barem từng ý → điểm câu /10 → quy đổi về điểm câu
    (dễ 1đ, nâng cao 2đ). AI lỗi / kết quả sai quy tắc → chấm bằng từ khóa (keyword_grader) để vẫn có điểm.
  - Bỏ trống tự luận → 0, không gọi AI.
Ghi điểm vào từng ReviewAnswer (chỉ sửa object — review_service commit).

T1 (12/11/2026) — chấm quá lâu:
  start_ai_grading()  gửi các câu tự luận cho AI SONG SONG (luồng riêng, không đụng DB) → Future theo vị trí câu.
  collect()           chờ tối đa N giây, lấy các câu AI đã chấm xong.
  grade_answers(..., ai_results=…)  ghi điểm; câu AI chưa xong / lỗi → chấm bằng từ khóa.
"""

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import wait as wait_futures

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


AIResult = tuple[list[dict] | None, str | None]  # (kết quả từng ý | None nếu không dùng được, lỗi)
TIMEOUT_ERROR = "AI chấm quá thời gian chờ"


def _has_text(answer: ReviewAnswer) -> bool:
    return bool(answer.text_answer and answer.text_answer.strip())


def ai_grade(ai: ReviewAI, question: dict, text: str) -> AIResult:
    """Gọi AI chấm MỘT câu + kiểm quy tắc. Không đụng DB → chạy được trong luồng riêng."""
    try:
        results = ai.grade_essay(question, text)
    except AIUnavailableError as err:
        return None, f"AI không dùng được: {err}"
    except Exception as err:  # lỗi lạ trong luồng chấm không được làm treo bài → rơi về từ khóa
        logger.exception("Ôn tập: AI chấm lỗi không lường trước")
        return None, f"AI lỗi: {type(err).__name__}"
    problems = grading_errors(results, question["rubric"])
    if problems:
        return None, "; ".join(problems[:3])
    return results, None


def start_ai_grading(ai: ReviewAI, answers: list[ReviewAnswer]) -> dict[int, Future]:
    """Gửi mọi câu tự luận CÓ bài làm cho AI cùng lúc (3 câu ≈ thời gian 1 câu). Trả {vị trí câu: Future}."""
    jobs = {
        a.position: (_question_dict(a), a.text_answer)
        for a in answers
        if a.question.type == "essay" and _has_text(a)
    }
    if not jobs:
        return {}
    pool = ThreadPoolExecutor(max_workers=len(jobs), thread_name_prefix="review-grade")
    futures = {pos: pool.submit(ai_grade, ai, q, text) for pos, (q, text) in jobs.items()}
    pool.shutdown(wait=False)  # luồng vẫn chạy tiếp; không giữ request chờ
    return futures


def collect(futures: dict[int, Future], timeout: float) -> tuple[dict[int, AIResult], bool]:
    """Chờ tối đa `timeout` giây. Trả (kết quả các câu đã xong, còn câu chưa xong hay không)."""
    if futures:
        wait_futures(futures.values(), timeout=max(0.0, timeout))
    done = {pos: f.result() for pos, f in futures.items() if f.done()}
    return done, len(done) < len(futures)


def grade_essay(ai: ReviewAI, answer: ReviewAnswer, ai_result: AIResult | None = None) -> tuple[list[dict], str | None]:
    """Trả (kết quả từng ý, lỗi AI nếu phải dùng chấm từ khóa).
    ai_result: kết quả AI đã chấm sẵn (luồng song song — T1); None → gọi AI ngay tại đây."""
    rubric = answer.question.rubric
    if not _has_text(answer):
        return [{"result": "none", "points": 0.0, "evidence": None} for _ in rubric], None
    results, error = ai_result if ai_result is not None else ai_grade(ai, _question_dict(answer), answer.text_answer)
    if results is not None:
        return results, None
    logger.warning("Ôn tập: chấm tự luận câu %s bằng từ khóa (%s)", answer.position, error)
    return keyword_grader.grade_essay(rubric, answer.text_answer, answer.question.content), error


def grade_answers(
    answers: list[ReviewAnswer], ai: ReviewAI, ai_results: dict[int, AIResult] | None = None
) -> tuple[float, dict]:
    """Chấm tất cả câu, ghi points / rubric_result vào từng câu. Trả (tổng điểm CHƯA làm tròn, vết chấm).

    ai_results=None: gọi AI lần lượt ngay tại đây (như trước T1).
    ai_results={vị trí: kết quả}: dùng kết quả đã chấm song song; câu có bài làm mà THIẾU trong dict
    (AI chưa xong khi hết giờ) → chấm bằng từ khóa với lỗi "quá thời gian".
    """
    total = 0.0
    fallbacks = []
    for answer in answers:
        max_points = float(answer.max_points)
        if answer.question.type == "mcq":
            points = max_points if is_mcq_correct(answer) else 0.0
        else:
            given = None
            if ai_results is not None:
                given = ai_results.get(answer.position, (None, TIMEOUT_ERROR))
            results, error = grade_essay(ai, answer, given)
            answer.rubric_result = results
            points = sum(r["points"] for r in results) / 10 * max_points
            if error:
                fallbacks.append({"position": answer.position, "error": error})
        answer.points = round(points, 2)
        total += points
    return total, {"ai": ai.name, "keyword_fallback": fallbacks}
