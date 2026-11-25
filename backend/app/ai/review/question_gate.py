"""Cổng kiểm câu AI soạn — G3c (module 09 · Tuấn · 25/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md mục 7.4, D8, P7).

Chạy SAU check_questions (G3b: khung, câu trích, trùng chữ, L7). Câu hỏng cổng bị LOẠI và soạn lại (D3) — khác phase 05
của thầy (chỉ gắn cờ) vì câu dùng ngay (D1).

    run_gate(questions, kind, ctx) → (câu đạt — có ai_check["gate"], [(câu hỏng, lý do tiếng Anh)])

Phép kiểm:
  1. Giải mù (trắc nghiệm): Gemini tự làm cả lô trong MỘT lần gọi, không thấy đáp án / giải thích / đoạn tài liệu, thứ tự
     lựa chọn đã xáo rồi quy ngược. Chọn khác đáp án ghi → loại. Solver trả thiếu / sai khung → "skipped" (không loại).
  2. L1 (trắc nghiệm): đáp án đúng dài > REVIEW_GATE_LENGTH_RATIO × lựa chọn sai dài nhất VÀ dài hơn
     ≥ REVIEW_GATE_LENGTH_MIN_DIFF ký tự → loại.
  3. Gần trùng theo nghĩa: cosine embedding với câu CÙNG LOẠI cùng kỹ năng / câu vừa đạt ≥ REVIEW_GATE_DUP_MAX → loại
     (câu trắc nghiệm và tự luận cùng chủ đề là bình thường — hiệu chỉnh 25/11).
  4. Bài giả tự luận (bộ chấm từ khóa, 0 lượt gọi): bài mẫu ≥ REVIEW_GATE_MODEL_MIN; bài chép đề ≤ REVIEW_GATE_COPY_MAX;
     bài mẫu câu khác ≤ REVIEW_GATE_OTHER_MAX → không thì loại.
  5. Trùng ý (25/11, Bước A — question_idea): câu trích phủ lên câu nguồn mà câu CÙNG LOẠI đã có (ngân hàng / vừa đạt)
     đã dùng → loại; lý do gửi lại cho AI "trích câu khác". Không cần embedder.
  + Bám nguồn: cosine(câu + đáp án, đoạn nguồn) — CHỈ GHI, không loại.
Không có embedder → bỏ qua 3 và bám nguồn ("skipped"). Lỗi AI khi giải mù (503…) → AIUnavailableError đi ra ngoài.
"""

import random
import re
from collections.abc import Callable
from dataclasses import dataclass, field

from app.ai.review import keyword_grading, question_idea
from app.ai.review.grading_schema import AIOutputError
from app.core.config import settings

GATE_VERSION = "gate-v2"  # v2 (25/11): + trùng ý (phép 5)

Solve = Callable[[str, list[dict]], object]  # (skill, items[{id, content, options}]) -> {"answers": [{id, index}]}
Embed = Callable[[str], list[float] | None]


@dataclass
class GateContext:
    skill: str
    chunks: dict[int, str]  # chunk_id → nội dung đoạn
    existing: list[tuple[int | None, str, str]] = field(default_factory=list)  # (question_id, đề, loại) cùng kỹ năng
    other_answers: list[str] = field(default_factory=list)  # bài mẫu tự luận khác (cho bài giả "câu khác")
    ideas: list[question_idea.UsedIdea] = field(default_factory=list)  # ý đã dùng (ngân hàng + câu vừa đạt) — phép 5
    solve: Solve | None = None
    embed: Embed | None = None
    rng: random.Random = field(default_factory=random.Random)
    _vectors: dict[str, list[float] | None] = field(default_factory=dict)

    def vector(self, text: str) -> list[float] | None:
        if self.embed is None:
            return None
        if text not in self._vectors:
            self._vectors[text] = self.embed(text)
        return self._vectors[text]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


# ─────────────── từng phép kiểm (hàm thuần) ───────────────


def _lengths(q: dict) -> tuple[int, int]:
    options = q["options"]
    correct = len(options[q["correct_index"]].strip())
    return correct, max(len(o.strip()) for i, o in enumerate(options) if i != q["correct_index"])


def length_ratio(q: dict) -> float:
    """L1: độ dài (ký tự) đáp án đúng / lựa chọn sai dài nhất."""
    correct, longest_wrong = _lengths(q)
    return round(correct / max(longest_wrong, 1), 2)


def length_hint(q: dict) -> bool:
    """L1: đáp án đúng dài bất thường → đoán được (tỉ lệ VÀ chênh lệch tuyệt đối)."""
    correct, longest_wrong = _lengths(q)
    return length_ratio(q) > settings.REVIEW_GATE_LENGTH_RATIO and correct - longest_wrong >= (
        settings.REVIEW_GATE_LENGTH_MIN_DIFF
    )


def blind_solve(questions: list[dict], ctx: GateContext) -> list[int | None]:
    """Chỉ số (theo thứ tự GỐC) mà solver chọn cho từng câu; None = solver không trả lời được câu đó."""
    if ctx.solve is None or not questions:
        return [None] * len(questions)
    orders, items = [], []
    for i, q in enumerate(questions):
        order = list(range(4))
        ctx.rng.shuffle(order)  # vị trí hiện i → lựa chọn gốc order[i]
        orders.append(order)
        items.append({"id": i + 1, "content": q["content"], "options": [q["options"][k] for k in order]})
    try:
        data = ctx.solve(ctx.skill, items)
    except AIOutputError:
        return [None] * len(questions)
    picked: dict[int, int] = {}
    for a in (data or {}).get("answers", []) if isinstance(data, dict) else []:
        try:
            qid, index = int(a["id"]), int(a["index"])
        except (KeyError, TypeError, ValueError):
            continue
        if 1 <= qid <= len(questions) and 0 <= index <= 3:
            picked.setdefault(qid, index)
    return [orders[i][picked[i + 1]] if i + 1 in picked else None for i in range(len(questions))]


def model_answer(q: dict) -> str:
    return re.sub(r"^\s*model answer\s*:\s*", "", q.get("explanation") or "", flags=re.IGNORECASE)


def keyword_score(rubric: list[dict], answer: str, question: str | None = None) -> float:
    """Điểm thang 10 bằng bộ chấm từ khóa (đường dự phòng khi Gemini lỗi)."""
    return round(sum(r["points"] for r in keyword_grading.grade_essay(rubric, answer, question)), 2)


def missed_items(q: dict) -> list[str]:
    """Ý barem mà bài mẫu KHÔNG đạt khi chấm từ khóa → "item 2 (keywords: a, b)" — gửi lại cho AI khi soạn lại."""
    results = keyword_grading.grade_essay(q["rubric"], model_answer(q), q["content"])
    return [f"item {i} (keywords: {', '.join(item['main_keywords'])})"
            for i, (item, r) in enumerate(zip(q["rubric"], results, strict=True), start=1) if r["points"] <= 0]  # fmt: skip


def fake_scores(q: dict, others: list[str]) -> dict:
    """Bài giả tự luận: bài mẫu (chấm như thật, có đề), bài CHÉP ĐỀ (không đưa đề → bộ chấm không trừ câu chép, giống
    mức Gemini có thể cho), bài mẫu của câu khác (barem quá chung chung thì bài lạc đề vẫn được điểm)."""
    scores = {
        "model": keyword_score(q["rubric"], model_answer(q), q["content"]),
        "copy": keyword_score(q["rubric"], q["content"]),
    }
    other = next((o for o in others if o and o != model_answer(q)), None)
    if other:
        scores["other"] = keyword_score(q["rubric"], other, q["content"])
    return scores


def _answer_text(q: dict) -> str:
    if q["type"] == "mcq":
        return q["options"][q["correct_index"]]
    return " ".join(item["text"] for item in q["rubric"])


# ─────────────── chạy cổng ───────────────


def run_gate(questions: list[dict], kind: str, ctx: GateContext) -> tuple[list[dict], list[tuple[dict, str]]]:
    rejected: list[tuple[dict, str]] = []
    checks: list[tuple[dict, dict]] = []
    for q in questions:
        gate: dict = {"version": GATE_VERSION}
        if kind == "mcq":
            gate["length_ratio"] = ratio = length_ratio(q)
            if length_hint(q):
                rejected.append((q, f"the correct option is {ratio}x longer than the longest wrong option (guessable)"))
                continue
        else:
            gate["fake_scores"] = fake = fake_scores(q, ctx.other_answers + [model_answer(o) for o, _ in checks])
            if fake["copy"] > settings.REVIEW_GATE_COPY_MAX:  # kiểm trước: đề lộ đáp án thì bài mẫu cũng bị coi là chép
                reason = (
                    f"copying the question text already scores {fake['copy']}/10 — the question gives the answer away"
                )
                rejected.append((q, reason))
                continue
            if fake["model"] < settings.REVIEW_GATE_MODEL_MIN:
                reason = (
                    f"the model answer only scores {fake['model']}/10 with keyword grading — "
                    f"{'; '.join(missed_items(q))} not found in the model answer. Every main keyword must appear "
                    "word for word in the sentence of the model answer that covers that item"
                )
                rejected.append((q, reason))
                continue
            if fake.get("other", 0) > settings.REVIEW_GATE_OTHER_MAX:
                rejected.append(
                    (q, f"an answer to a different question scores {fake['other']}/10 — rubric too generic")
                )
                continue
        checks.append((q, gate))

    if kind == "mcq":
        solved = blind_solve([q for q, _ in checks], ctx)
        kept = []
        for (q, gate), index in zip(checks, solved, strict=True):
            gate["solver_index"] = index
            gate["solver"] = "skipped" if index is None else "ok"
            if index is not None and index != q["correct_index"]:
                letter = "ABCD"
                reason = (
                    f"an independent solver chose {letter[index]} ({q['options'][index][:40]}) "
                    f"instead of {letter[q['correct_index']]} — answer key wrong or ambiguous"
                )
                rejected.append((q, reason))
                continue
            kept.append((q, gate))
        checks = kept

    passed: list[dict] = []
    seen: list[tuple[int | None, list[float]]] = []
    if ctx.embed is not None:
        seen = [(qid, v) for qid, text, t in ctx.existing if t == kind and (v := ctx.vector(text)) is not None]
    for q, gate in checks:
        quote = question_idea.quote_of(q.get("ai_check"))
        idea = question_idea.idea_of(quote, q.get("chunk_id"), ctx.chunks.get(q.get("chunk_id")))
        gate["idea"] = sorted([list(t) for t in idea])
        same = question_idea.clash(idea, kind, ctx.ideas)
        if same is not None:
            gate["same_idea_as"] = same.question_id
            rejected.append((q, f'tests the same source sentence as an existing question ("{same.quote[:80]}") — '
                                "write about a different sentence of the passages and quote that one"))  # fmt: skip
            continue
        vec = ctx.vector(q["content"])
        if vec is None:
            gate["max_similarity"] = gate["grounding"] = None
        else:
            best_id, best = None, 0.0
            for qid, other in seen:
                score = _cosine(vec, other)
                if score > best:
                    best_id, best = qid, score
            gate["max_similarity"], gate["similar_question_id"] = round(best, 3), best_id
            if best >= settings.REVIEW_GATE_DUP_MAX:
                rejected.append((q, f"means almost the same as an existing question (similarity {best:.2f})"))
                continue
            chunk = ctx.chunks.get(q.get("chunk_id"))
            answer_vec = ctx.vector(f"{q['content']} {_answer_text(q)}")
            chunk_vec = ctx.vector(chunk) if chunk else None
            gate["grounding"] = round(_cosine(answer_vec, chunk_vec), 3) if answer_vec and chunk_vec else None
            seen.append((None, vec))
        gate["passed"] = True
        q.setdefault("ai_check", {})["gate"] = gate
        passed.append(q)
        if idea:
            ctx.ideas.append(question_idea.UsedIdea(None, kind, idea, quote))
    return passed, rejected
