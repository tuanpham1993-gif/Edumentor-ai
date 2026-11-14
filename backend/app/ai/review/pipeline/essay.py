"""Pipeline chấm MỘT câu tự luận (module 09 · Tuấn · B6, 14/11/2026 — docs/Review-AI-Grading.md mục 2).

B6 chỉ BỌC code có sẵn thành khối — hành vi chấm không đổi (toàn bộ test cũ vẫn xanh):

    0_input ──(bài trống → 0 điểm, dừng)
      → 3_context
      → 4_llm_grade ──(lỗi / quá giờ)──→ 4b_keyword_fallback
      │      (ok: nhảy qua dự phòng)              │
      └──────────────→ 7_aggregate ←──────────────┘
      → 8_trace

Khối 1 (tiền xử lý NLP), 2 (Guard), 5 (Verifier), 6 (Đối chiếu → chấm lại) thêm ở B8; khối 3 có RAG ở B9 —
chỉ cần chèn Node vào ESSAY_NODES, runner và review_grader không phải sửa.
Không đụng DB → chạy được trong luồng song song (T1).
"""

import logging
import time
from dataclasses import dataclass, field

from app.ai.review import keyword_grading
from app.ai.review.base import AIUnavailableError, ReviewAI
from app.ai.review.pipeline.runner import Node, NodeFailed, Step, run_pipeline
from app.ai.review.validator import grading_errors

logger = logging.getLogger(__name__)

# (kết quả từng ý | None nếu không dùng được, lỗi, thời gian gọi AI ms | None)
AIResult = tuple[list[dict] | None, str | None, float | None]
TIMEOUT_ERROR = "AI chấm quá thời gian chờ"


def ai_grade(ai: ReviewAI, question: dict, text: str) -> AIResult:
    """Gọi AI chấm MỘT câu + kiểm quy tắc (công việc của khối 4). Không đụng DB → chạy được trong luồng riêng."""
    start = time.perf_counter()

    def done(results, error):
        return results, error, round((time.perf_counter() - start) * 1000, 1)

    try:
        results = ai.grade_essay(question, text)
    except AIUnavailableError as err:
        return done(None, f"AI không dùng được: {err}")
    except Exception as err:  # lỗi lạ trong luồng chấm không được làm treo bài → rơi về từ khóa
        logger.exception("Ôn tập: AI chấm lỗi không lường trước")
        return done(None, f"AI lỗi: {type(err).__name__}")
    problems = grading_errors(results, question["rubric"])
    if problems:
        return done(None, "; ".join(problems[:3]))
    return done(results, None)


@dataclass
class EssayContext:
    """Trạng thái một câu đi qua pipeline (giống item JSON chảy qua các node n8n)."""

    ai: ReviewAI
    question: dict  # {content, rubric, explanation}
    text: str | None
    precomputed: AIResult | None = None  # kết quả khối 4 đã chạy sẵn ở luồng song song (T1)
    position: int | None = None
    results: list[dict] | None = None
    error: str | None = None  # lỗi AI khi phải dùng dự phòng từ khóa
    score_10: float = 0.0
    done: bool = False
    trace: list[dict] = field(default_factory=list)


# ─────────────── các khối ───────────────


def node_input(ctx: EssayContext) -> Step:
    """[0] Nhận bài. Bài trống → mọi ý none, 0 điểm, không gọi AI (giữ hành vi cũ)."""
    text = ctx.text or ""
    if not text.strip():
        ctx.results = [{"result": "none", "points": 0.0, "evidence": None} for _ in ctx.question["rubric"]]
        ctx.score_10 = 0.0
        ctx.done = True
        return Step(output={"empty": True})
    return Step(output={"chars": len(text), "words": len(text.split())})


def node_context(ctx: EssayContext) -> Step:
    """[3] Ngữ cảnh chấm: đề + barem + đáp án mẫu. RAG (Model B) thêm ở B9."""
    q = ctx.question
    return Step(
        output={"items": len(q["rubric"]), "model_answer": bool((q.get("explanation") or "").strip()), "rag": False}
    )


def node_llm_grade(ctx: EssayContext) -> Step:
    """[4] AI chấm theo barem. Dùng kết quả luồng song song nếu có; lỗi / sai quy tắc → NodeFailed → dự phòng."""
    source = "parallel" if ctx.precomputed is not None else "inline"
    results, error, ms = ctx.precomputed if ctx.precomputed is not None else ai_grade(ctx.ai, ctx.question, ctx.text)
    output = {"ai": ctx.ai.name, "source": source, "llm_ms": ms}
    if results is None:
        ctx.error = error
        # Kết quả song song đã hỏng / quá giờ → thử lại không đổi được gì (chỉ làm người học chờ thêm)
        raise NodeFailed(error or "AI không trả kết quả", output=output, retryable=source == "inline")
    ctx.results = results
    return Step(goto="7_aggregate", output=output)


def node_keyword_fallback(ctx: EssayContext) -> Step:
    """[4b] Dự phòng: chấm bằng từ khóa (B3) khi AI lỗi / quá giờ — người học vẫn có điểm."""
    logger.warning("Ôn tập: chấm tự luận câu %s bằng từ khóa (%s)", ctx.position, ctx.error)
    ctx.results = keyword_grading.grade_essay(ctx.question["rubric"], ctx.text, ctx.question.get("content"))
    return Step(output={"reason": ctx.error})


def node_aggregate(ctx: EssayContext) -> Step:
    """[7] Tổng hợp: CODE cộng điểm từng ý (không để AI tự cộng) → điểm câu thang 10."""
    ctx.score_10 = sum(r["points"] for r in ctx.results)
    return Step(output={"score_10": ctx.score_10, "items": [r["result"] for r in ctx.results]})


def node_trace(ctx: EssayContext) -> Step:
    """[8] Kết thúc: tóm tắt cho trace (review_service lưu cùng điểm vào attempt.trace — một lần commit)."""
    return Step(output={"graded_by": "keyword" if ctx.error else ctx.ai.name})


ESSAY_NODES = [
    Node("0_input", node_input),
    Node("3_context", node_context),
    Node("4_llm_grade", node_llm_grade, on_error="4b_keyword_fallback"),
    Node("4b_keyword_fallback", node_keyword_fallback),
    Node("7_aggregate", node_aggregate),
    Node("8_trace", node_trace),
]


def grade_essay(
    ai: ReviewAI, question: dict, text: str | None, *, precomputed: AIResult | None = None, position: int | None = None
) -> EssayContext:
    """Chạy pipeline cho một câu. Trả ctx: results (từng ý), error (lỗi AI nếu dùng dự phòng), score_10, trace."""
    ctx = EssayContext(ai=ai, question=question, text=text, precomputed=precomputed, position=position)
    return run_pipeline(ESSAY_NODES, ctx)
