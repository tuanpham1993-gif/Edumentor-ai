"""Pipeline chấm MỘT câu tự luận (module 09 · Tuấn · B6 14/11, B8 15/11/2026 — docs/Review-AI-Grading.md mục 2).

    0_input ──(bài trống → 0 điểm, dừng)
      → 1_preprocess        tiền xử lý NLP (khối 1, text_pipeline) — số từ, dùng cho đối chiếu
      → 2_guard             gắn CỜ, không chặn: quá dài (cắt bớt trước khi gửi AI), có câu ra lệnh cho AI, viết
                            tiếng Việt. Mọi bài vẫn được chấm theo barem (không phát hiện "bài do AI viết").
      → 3_context           đề + barem + đáp án mẫu (RAG ở B9)
      → 4_llm_grade ──(lỗi / quá giờ)──→ 4b_keyword_fallback ──→ 7_aggregate (bỏ qua 5, 6)
      → 5_verify            ý "full" phải có câu trích THẬT trong bài (so sau chuẩn hóa) — không có → none + cờ
      → 6_cross_check       so điểm AI với điểm chấm từ khóa: lệch > CROSS_CHECK_GAP → chấm lại 1 lần (về 4)
                            → vẫn lệch → cờ needs_review (điểm vẫn tính tạm — D10)
      → 7_aggregate → 8_trace

Mỗi ý chỉ Đạt / Không đạt (15/11). Không đụng DB → khối 4 chạy được trong luồng song song (T1).
"""

import logging
import re
import time
import unicodedata
from dataclasses import dataclass, field
from typing import NamedTuple

from app.ai.review import keyword_grading
from app.ai.review.base import AIUnavailableError, ReviewAI
from app.ai.review.pipeline.runner import Node, NodeFailed, Step, run_pipeline
from app.ai.review.text_pipeline import preprocess
from app.ai.review.validator import grading_errors

logger = logging.getLogger(__name__)

MAX_ANSWER_CHARS = 3000  # bài dài hơn: cắt trước khi gửi AI (giới hạn chi phí, chống nhồi bài) + cờ "too_long"
CROSS_CHECK_GAP = 3.0  # điểm AI và điểm từ khóa (thang 10) lệch hơn mức này → chấm lại
EVIDENCE_NGRAM_MATCH = 0.8  # câu trích khớp ≥ 80% cụm 3 từ trong bài → coi là có thật (AI hay sửa dấu câu)

_INJECTION = re.compile(
    r"ignore\s+(all\s+|the\s+|any\s+)?(previous|above|prior)\s+(instructions|rules)"
    r"|(give|grant|award)\s+(me\s+|this\s+answer\s+)?(full|maximum|max|10|ten)\s+(marks|points|score)"
    r"|you\s+are\s+now\b|system\s+prompt|as\s+an\s+ai\s+grader"
    r"|cho\s+(tôi|em|mình)?\s*(điểm\s+tối\s+đa|10\s+điểm|full\s+điểm)|bỏ\s+qua\s+(các\s+|mọi\s+)?(hướng\s+dẫn|quy\s+tắc)",
    re.IGNORECASE,
)


class AIResult(NamedTuple):
    """Kết quả công việc khối 4 (chạy được trong luồng song song). Tuple 3 phần tử cũ (results, error, ms) vẫn
    dùng được — các trường sau có mặc định."""

    results: list[dict] | None  # None = không dùng được → dự phòng từ khóa
    error: str | None
    ms: float | None  # thời gian gọi AI
    attempts: int = 1  # số lần gọi AI (B7: sai khung → thử lại 1 lần)
    feedback: str | None = None
    prompt_version: str | None = None


TIMEOUT_ERROR = "AI chấm quá thời gian chờ"


def text_for_ai(text: str) -> str:
    """Bài gửi cho AI: cắt ở MAX_ANSWER_CHARS (dùng chung cho luồng song song và chấm lại → hai đường như nhau)."""
    return text if len(text) <= MAX_ANSWER_CHARS else text[:MAX_ANSWER_CHARS]


def ai_grade(ai: ReviewAI, question: dict, text: str) -> AIResult:
    """Gọi AI chấm MỘT câu + kiểm quy tắc (công việc của khối 4). Không đụng DB → chạy được trong luồng riêng."""
    start = time.perf_counter()

    def elapsed():
        return round((time.perf_counter() - start) * 1000, 1)

    try:
        grade = ai.grade_essay_detailed(question, text_for_ai(text))
    except AIUnavailableError as err:
        return AIResult(None, f"AI không dùng được: {err}", elapsed(), getattr(err, "attempts", 1))
    except Exception as err:  # lỗi lạ trong luồng chấm không được làm treo bài → rơi về từ khóa
        logger.exception("Ôn tập: AI chấm lỗi không lường trước")
        return AIResult(None, f"AI lỗi: {type(err).__name__}", elapsed())
    problems = grading_errors(grade.items, question["rubric"])
    if problems:
        return AIResult(None, "; ".join(problems[:3]), elapsed(), grade.attempts)
    return AIResult(grade.items, None, elapsed(), grade.attempts, grade.feedback, grade.prompt_version)


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
    feedback: str | None = None  # nhận xét chung của AI (B7) — KHÔNG ghi vào trace khối (có thể trích bài làm)
    flags: list[str] = field(default_factory=list)  # too_long, instruction_in_answer, vietnamese, evidence_missing…
    needs_review: bool = False  # D8: điểm AI và từ khóa vẫn lệch sau khi chấm lại
    regraded: bool = False
    score_10: float = 0.0
    done: bool = False
    trace: list[dict] = field(default_factory=list)

    def flag(self, name: str) -> None:
        if name not in self.flags:
            self.flags.append(name)


# ─────────────── các khối ───────────────


def node_input(ctx: EssayContext) -> Step:
    """[0] Nhận bài. Bài trống → mọi ý none, 0 điểm, không gọi AI."""
    text = ctx.text or ""
    if not text.strip():
        ctx.results = [{"result": "none", "points": 0.0, "evidence": None} for _ in ctx.question["rubric"]]
        ctx.score_10 = 0.0
        ctx.done = True
        return Step(output={"empty": True})
    return Step(output={"chars": len(text), "words": len(text.split())})


def node_preprocess(ctx: EssayContext) -> Step:
    """[1] Tiền xử lý NLP (Session 01): chuẩn hóa, tách từ, bỏ stopwords, lemmatize. Chỉ ghi số liệu vào trace."""
    lemmas = preprocess(text_for_ai(ctx.text))
    return Step(output={"tokens": len(lemmas), "unique": len(set(lemmas))})


def node_guard(ctx: EssayContext) -> Step:
    """[2] Guard: chỉ GẮN CỜ để admin biết — không chặn, không phát hiện bài do AI viết (chấm theo barem như mọi bài).
    Câu ra lệnh cho AI ("give me full marks") không có tác dụng: prompt coi bài làm là dữ liệu (quy tắc 10)."""
    text = ctx.text
    if len(text) > MAX_ANSWER_CHARS:
        ctx.flag("too_long")
    if _INJECTION.search(text):
        ctx.flag("instruction_in_answer")
    if keyword_grading._VIETNAMESE.search(text) and not keyword_grading.is_vietnamese(
        ctx.question["rubric"], ctx.question.get("content")
    ):
        ctx.flag("vietnamese")  # vẫn chấm theo nghĩa (RATER_GUIDELINE quy tắc 2)
    return Step(output={"flags": list(ctx.flags)})


def node_context(ctx: EssayContext) -> Step:
    """[3] Ngữ cảnh chấm: đề + barem + đáp án mẫu (+ đoạn tri thức của kỹ năng khi REVIEW_GRADING_RAG — Model B, B9).
    Đoạn tri thức được lấy ở luồng chính trước khi chấm song song (review_grader) — khối này ghi lại đã dùng gì."""
    q = ctx.question
    chunks = q.get("context_chunks") or []
    return Step(
        output={
            "items": len(q["rubric"]),
            "model_answer": bool((q.get("explanation") or "").strip()),
            "rag": bool(chunks),
            "chunks": [{"code": c.get("code"), "score": c.get("score")} for c in chunks],
        }
    )


def node_llm_grade(ctx: EssayContext) -> Step:
    """[4] AI chấm theo barem. Lần đầu dùng kết quả luồng song song nếu có; chấm lại (từ khối 6) luôn gọi trực tiếp.
    Lỗi / sai quy tắc → NodeFailed → dự phòng từ khóa."""
    if ctx.regraded:
        source = "regrade"
        r = ai_grade(ctx.ai, ctx.question, ctx.text)
    elif ctx.precomputed is not None:
        source = "parallel"
        r = AIResult(*ctx.precomputed)
    else:
        source = "inline"
        r = ai_grade(ctx.ai, ctx.question, ctx.text)
    output = {"ai": ctx.ai.name, "source": source, "llm_ms": r.ms, "llm_attempts": r.attempts}
    if r.prompt_version:
        output["prompt_version"] = r.prompt_version
    if r.results is None and source == "regrade":
        # Chấm lại lỗi (mạng / quota): giữ kết quả AI lần đầu, đánh dấu cần xem lại — không rơi về từ khóa
        ctx.needs_review = True
        ctx.flag("needs_review")
        return Step(goto="7_aggregate", output={**output, "regrade_error": r.error})
    if r.results is None:
        ctx.error = r.error
        # Kết quả song song đã hỏng / quá giờ → thử lại không đổi được gì (chỉ làm người học chờ thêm)
        raise NodeFailed(r.error or "AI không trả kết quả", output=output, retryable=source == "inline")
    ctx.results = [dict(item) for item in r.results]
    ctx.feedback = r.feedback
    return Step(goto="5_verify", output=output)  # nhảy qua 4b (dự phòng)


def node_keyword_fallback(ctx: EssayContext) -> Step:
    """[4b] Dự phòng: chấm bằng từ khóa (B3) khi AI lỗi / quá giờ — người học vẫn có điểm. Bỏ qua khối 5, 6."""
    logger.warning("Ôn tập: chấm tự luận câu %s bằng từ khóa (%s)", ctx.position, ctx.error)
    ctx.results = keyword_grading.grade_essay(ctx.question["rubric"], ctx.text, ctx.question.get("content"))
    return Step(goto="7_aggregate", output={"reason": ctx.error})


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text).lower().translate(str.maketrans("‘’“”", "''\"\""))
    text = re.sub(r"[\s]+", " ", text)
    return re.sub(r"\s*([.,;:!?])\s*", r"\1 ", text).strip(" .,;:!?")


def evidence_in_answer(evidence: str | None, answer: str) -> bool:
    """Câu trích có thật trong bài? So sau chuẩn hóa (hoa thường, khoảng trắng, dấu nháy, dấu câu); không khớp nguyên
    đoạn thì cho phép ≥ 80% cụm 3 từ của câu trích có trong bài (AI hay bỏ / sửa vài dấu câu khi trích)."""
    if not (evidence and evidence.strip()):
        return False
    ev, ans = _normalize(evidence), _normalize(answer)
    if ev and ev in ans:
        return True
    ev_words, ans_words = ev.split(), ans.split()
    if len(ev_words) < 3:
        return False
    grams = {tuple(ev_words[i : i + 3]) for i in range(len(ev_words) - 2)}
    ans_grams = {tuple(ans_words[i : i + 3]) for i in range(len(ans_words) - 2)}
    return len(grams & ans_grams) / len(grams) >= EVIDENCE_NGRAM_MATCH


def node_verify(ctx: EssayContext) -> Step:
    """[5] Verifier: ý "full" phải dựa trên câu trích có thật trong bài làm. AI không trích / trích bịa → ý đó none
    (0 điểm) + cờ evidence_missing. Chặn kiểu AI "chấm rộng tay" không có căn cứ."""
    downgraded = []
    for no, item in enumerate(ctx.results, start=1):
        if item["result"] != "full":
            continue
        if evidence_in_answer(item.get("evidence"), ctx.text):
            continue
        item.update(result="none", points=0.0, evidence=None)
        item["reason"] = "Không có câu trích từ bài làm làm căn cứ (Verifier)."
        downgraded.append(no)
    if downgraded:
        ctx.flag("evidence_missing")
    return Step(output={"downgraded_items": downgraded})


def node_cross_check(ctx: EssayContext) -> Step:
    """[6] Đối chiếu với chấm từ khóa. Lệch > CROSS_CHECK_GAP điểm → chấm lại 1 lần (quay về khối 4);
    vẫn lệch → needs_review (giữ điểm AI lần chấm lại, tính tạm — D10). Chấm từ khóa không hiểu nghĩa nên chỉ là
    tín hiệu "nên xem lại", không dùng để sửa điểm."""
    ai_score = sum(r["points"] for r in ctx.results)
    kw = keyword_grading.grade_essay(ctx.question["rubric"], ctx.text, ctx.question.get("content"))
    kw_score = sum(r["points"] for r in kw)
    gap = abs(ai_score - kw_score)
    output = {"ai_score": ai_score, "keyword_score": kw_score, "gap": gap}
    if gap <= CROSS_CHECK_GAP:
        return Step(output=output)
    if not ctx.regraded:
        ctx.regraded = True
        return Step(goto="4_llm_grade", output={**output, "action": "regrade"})
    ctx.needs_review = True
    ctx.flag("needs_review")
    return Step(output={**output, "action": "needs_review"})


def node_aggregate(ctx: EssayContext) -> Step:
    """[7] Tổng hợp: CODE cộng điểm từng ý (không để AI tự cộng) → điểm câu thang 10."""
    ctx.score_10 = sum(r["points"] for r in ctx.results)
    return Step(output={"score_10": ctx.score_10, "items": [r["result"] for r in ctx.results]})


def node_trace(ctx: EssayContext) -> Step:
    """[8] Kết thúc: tóm tắt cho trace (review_service lưu cùng điểm vào attempt.trace — một lần commit)."""
    return Step(
        output={
            "graded_by": "keyword" if ctx.error else ctx.ai.name,
            "flags": list(ctx.flags),
            "regraded": ctx.regraded,
        }
    )


ESSAY_NODES = [
    Node("0_input", node_input),
    Node("1_preprocess", node_preprocess),
    Node("2_guard", node_guard),
    Node("3_context", node_context),
    Node("4_llm_grade", node_llm_grade, on_error="4b_keyword_fallback"),
    Node("4b_keyword_fallback", node_keyword_fallback),
    Node("5_verify", node_verify),
    Node("6_cross_check", node_cross_check),
    Node("7_aggregate", node_aggregate),
    Node("8_trace", node_trace),
]


def grade_essay(
    ai: ReviewAI, question: dict, text: str | None, *, precomputed: AIResult | None = None, position: int | None = None
) -> EssayContext:
    """Chạy pipeline cho một câu. Trả ctx: results (từng ý), error (lỗi AI nếu dùng dự phòng), score_10, flags,
    needs_review, trace."""
    ctx = EssayContext(ai=ai, question=question, text=text, precomputed=precomputed, position=position)
    return run_pipeline(ESSAY_NODES, ctx)
