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

B6 (14/11/2026): mỗi câu tự luận đi qua pipeline kiểu n8n (app/ai/review/pipeline) — hành vi chấm không đổi,
thêm trace từng khối vào attempt.trace["grading"]["essays"] (khối nào chạy, bao lâu, ra gì, lỗi gì).
"""

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import wait as wait_futures

from sqlalchemy.orm import object_session

from app.ai.review import pipeline
from app.ai.review.base import ReviewAI
from app.ai.review.pipeline import TIMEOUT_ERROR, AIResult, ai_grade
from app.core.config import settings
from app.models.review_attempt import ReviewAnswer
from app.services import review_rag_service

__all__ = ["TIMEOUT_ERROR", "AIResult", "ai_grade"]  # giữ tên cũ cho code gọi từ ngoài

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
    question = {"content": q.content, "rubric": q.rubric, "explanation": q.explanation}
    if settings.REVIEW_GRADING_RAG and q.type == "essay":
        question["context_chunks"] = _grading_chunks(answer, question)
    if settings.REVIEW_GRADING_FEWSHOT and q.type == "essay":
        question["few_shot"] = True  # 17/11: kèm ví dụ chấm mẫu (prompt grade-en-v3+fs)
    return question


def _grading_chunks(answer: ReviewAnswer, question: dict) -> list[dict]:
    """B9 (Model B): đoạn tri thức của kỹ năng cho câu này. Lấy ở luồng chính (cần DB) TRƯỚC khi gửi luồng song
    song. Lỗi truy xuất → không kèm đoạn nào (chấm như Model A), không làm hỏng việc chấm."""
    db = object_session(answer)
    if db is None:
        return []
    try:
        chunks = review_rag_service.retrieve_for_grading(
            db, answer.question.skill_id, answer.question.chunk_id, question
        )
    except Exception:  # thiếu mô hình / lỗi DB: chấm như Model A
        logger.exception("Ôn tập: không lấy được đoạn tri thức khi chấm (RAG)")
        return []
    return [{"code": c.code, "title": c.title, "content": c.content, "score": c.score} for c in chunks]


def _has_text(answer: ReviewAnswer) -> bool:
    return bool(answer.text_answer and answer.text_answer.strip())


def start_ai_grading(ai: ReviewAI, answers: list[ReviewAnswer]) -> dict[int, Future]:
    """Gửi mọi câu tự luận CÓ bài làm cho AI cùng lúc (3 câu ≈ thời gian 1 câu). Trả {vị trí câu: Future}.
    Luồng chỉ chạy công việc khối 4 (ai_grade); các khối còn lại chạy khi ghi điểm (grade_answers)."""
    jobs = {
        a.position: (_question_dict(a), a.text_answer) for a in answers if a.question.type == "essay" and _has_text(a)
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


def grade_essay(
    ai: ReviewAI, answer: ReviewAnswer, ai_result: AIResult | None = None
) -> tuple[list[dict], str | None, list[dict], dict]:
    """Chạy pipeline cho một câu. Trả (kết quả từng ý, lỗi AI nếu phải dùng chấm từ khóa, trace từng khối,
    thông tin thêm: feedback (B7), flags + needs_review (B8)).
    ai_result: kết quả khối 4 đã chạy sẵn (luồng song song — T1); None → gọi AI ngay trong pipeline."""
    ctx = pipeline.grade_essay(
        ai, _question_dict(answer), answer.text_answer, precomputed=ai_result, position=answer.position
    )
    return (
        ctx.results,
        ctx.error,
        ctx.trace,
        {"feedback": ctx.feedback, "flags": ctx.flags, "needs_review": ctx.needs_review},
    )


def grade_answers(
    answers: list[ReviewAnswer], ai: ReviewAI, ai_results: dict[int, AIResult] | None = None
) -> tuple[float, dict]:
    """Chấm tất cả câu, ghi points / rubric_result vào từng câu. Trả (tổng điểm CHƯA làm tròn, vết chấm).

    ai_results=None: gọi AI lần lượt ngay tại đây (như trước T1).
    ai_results={vị trí: kết quả}: dùng kết quả đã chấm song song; câu có bài làm mà THIẾU trong dict
    (AI chưa xong khi hết giờ) → chấm bằng từ khóa với lỗi "quá thời gian".
    Vết chấm: {"ai", "keyword_fallback": [{position, error}],
               "needs_review": [vị trí câu điểm AI vẫn lệch chấm từ khóa sau khi chấm lại — B8, tính tạm (D10)],
               "essays": [{position, nodes: [trace từng khối], feedback, flags, needs_review}]}.
    Lý do từng ý (reason, B7) nằm trong answer.rubric_result.
    """
    total = 0.0
    fallbacks, essays = [], []
    for answer in answers:
        max_points = float(answer.max_points)
        if answer.question.type == "mcq":
            points = max_points if is_mcq_correct(answer) else 0.0
        else:
            given = None
            if ai_results is not None and _has_text(answer):
                given = ai_results.get(answer.position, AIResult(None, TIMEOUT_ERROR, None))
            results, error, nodes, extra = grade_essay(ai, answer, given)
            answer.rubric_result = results
            points = sum(r["points"] for r in results) / 10 * max_points
            if error:
                fallbacks.append({"position": answer.position, "error": error})
            essays.append({"position": answer.position, "nodes": nodes, **extra})
        answer.points = round(points, 2)
        total += points
    needs_review = [e["position"] for e in essays if e.get("needs_review")]
    return total, {"ai": ai.name, "keyword_fallback": fallbacks, "needs_review": needs_review, "essays": essays}
