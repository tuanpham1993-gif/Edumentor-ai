"""Khung + bộ kiểm câu hỏi AI soạn cho ôn THEO KỸ NĂNG (module 09 · Tuấn · G3b, 25/11/2026).

    GEMINI_QUESTION_SCHEMAS[kind]          gửi cho Gemini (responseSchema) — kind "mcq" | "essay"
    check_questions(data, kind, need, ...) kiểm LẠI phía server → (câu hợp lệ, lỗi). Lỗi (tiếng Anh) gửi lại cho AI khi soạn lại.
Kiểm: khung (validator chung với ngân hàng soạn tay) · đúng mức của lần gọi · `passage` hợp lệ · `source_quote` có THẬT
trong đoạn đó (chống bịa) · cấm "All / None of the above" · không trùng câu đã có / câu cùng lô (giống chữ ≥ 85%) ·
tự luận: **L7** (P19, 25/11) — một ý barem có TẤT CẢ từ khóa chính nằm sẵn trong đề → học viên chép đề là được điểm → loại.
Kiểm theo NGHĨA (embedding), giải mù, bám nguồn sâu hơn → cổng G3c.
"""

import re
from difflib import SequenceMatcher

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.ai.review.validator import TYPE_OF_LEVEL, question_errors

QUOTE_MIN_WORDS = 5
DUPLICATE_RATIO = 0.85
BANNED_OPTION = re.compile(r"\b(all|none|both) of the (above|options)\b|\bboth [a-d] and [a-d]\b", re.IGNORECASE)


class RubricItemOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    text: str
    max_points: float
    main_keywords: list[str]
    sub_keywords: list[str] = Field(default_factory=list)


class QuestionOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    level: str
    passage: int
    content: str
    options: list[str] | None = None
    correct_index: int | None = None
    rubric: list[RubricItemOut] | None = None
    explanation: str = ""
    source_quote: str = ""


class QuestionsOutput(BaseModel):
    questions: list[QuestionOut]


_COMMON = {
    "level": {"type": "STRING"},
    "passage": {"type": "INTEGER", "description": "Number of the passage the question is based on."},
    "content": {"type": "STRING"},
}
_QUOTE = {"type": "STRING", "description": "A sentence copied EXACTLY from that passage, supporting the answer."}
_MCQ_ITEM = {
    "type": "OBJECT",
    "properties": {
        **_COMMON,
        "level": {"type": "STRING", "enum": ["recognize", "understand"]},
        "options": {"type": "ARRAY", "items": {"type": "STRING"}},
        "correct_index": {"type": "INTEGER"},
        "explanation": {"type": "STRING"},
        "source_quote": _QUOTE,
    },
    "required": ["level", "passage", "content", "options", "correct_index", "explanation", "source_quote"],
    "propertyOrdering": ["level", "passage", "content", "options", "correct_index", "explanation", "source_quote"],
}
_ESSAY_ITEM = {
    "type": "OBJECT",
    "properties": {
        **_COMMON,
        "level": {"type": "STRING", "enum": ["easy", "advanced"]},
        "rubric": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "text": {"type": "STRING"},
                    "max_points": {"type": "NUMBER"},
                    "main_keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "sub_keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
                "required": ["text", "max_points", "main_keywords", "sub_keywords"],
                "propertyOrdering": ["text", "max_points", "main_keywords", "sub_keywords"],
            },
        },
        "explanation": {"type": "STRING", "description": "Model answer that earns every rubric item."},
        "source_quote": _QUOTE,
    },
    "required": ["level", "passage", "content", "rubric", "explanation", "source_quote"],
    "propertyOrdering": ["level", "passage", "content", "rubric", "explanation", "source_quote"],
}
GEMINI_QUESTION_SCHEMAS = {
    kind: {"type": "OBJECT", "properties": {"questions": {"type": "ARRAY", "items": item}}, "required": ["questions"]}
    for kind, item in (("mcq", _MCQ_ITEM), ("essay", _ESSAY_ITEM))
}


def norm(text: str) -> str:
    """chữ thường, bỏ dấu câu / ký hiệu, gộp khoảng trắng — so câu trích và so trùng."""
    return " ".join(re.sub(r"[^\w\s]", " ", (text or "").lower()).split())


# 26/11 (3b): lời giải thích / bài mẫu nhắc tới "the text" — học viên KHÔNG thấy đoạn tài liệu → bỏ cụm dẫn nguồn
_SOURCE_REF = re.compile(
    r"according to the (?:text|passage|source|document|context),?\s*"
    r"|(?:the|this) (?:text|passage|source|document|context) "
    r"(?:states|says|explains|mentions|notes|indicates|shows|describes)(?: that)?\s*",
    re.IGNORECASE,
)


def clean_explanation(text: str | None) -> str | None:
    """Bỏ "The text states that…", "According to the passage, …"; cụm ở đầu câu thì viết hoa chữ kế tiếp."""
    if not text:
        return text
    out, pos = [], 0
    for m in _SOURCE_REF.finditer(text):
        out.append(text[pos : m.start()])
        pos = m.end()
        before = text[: m.start()].rstrip()
        if (not before or before[-1] in ".!?:") and pos < len(text):
            out.append(text[pos].upper())
            pos += 1
    out.append(text[pos:])
    return "".join(out)


def is_duplicate(content: str, others: list[str]) -> bool:
    text = norm(content)
    return any(text == o or SequenceMatcher(None, text, o).ratio() >= DUPLICATE_RATIO for o in others)


def leaked_items(content: str, rubric: list[dict]) -> list[int]:
    """L7: số thứ tự (1..) các ý barem mà MỌI từ khóa chính đều có sẵn trong đề (so cả cụm, theo ranh giới từ)."""
    text = f" {norm(content)} "
    leaked = []
    for i, item in enumerate(rubric, start=1):
        keywords = [norm(k) for k in item.get("main_keywords") or [] if norm(k)]
        if keywords and all(f" {k} " in text for k in keywords):
            leaked.append(i)
    return leaked


def _as_question(q: QuestionOut, kind: str) -> dict:
    data = {
        "type": kind,
        "level": q.level,
        "content": q.content.strip(),
        "explanation": q.explanation.strip() or None,
        "passage": q.passage,
        "source_quote": q.source_quote.strip(),
    }
    if kind == "mcq":
        data |= {"options": [o.strip() for o in q.options or []], "correct_index": q.correct_index}
    else:
        data["rubric"] = [
            {"text": r.text.strip(), "max_points": int(r.max_points) if float(r.max_points).is_integer() else r.max_points,
             "main_keywords": [k.strip() for k in r.main_keywords if k.strip()],
             "sub_keywords": [k.strip() for k in r.sub_keywords if k.strip()]}
            for r in q.rubric or []
        ]  # fmt: skip
    return data


def _problem(q: QuestionOut, kind: str, need: dict[str, int], passages: list[str]) -> str | None:
    if q.level not in need or TYPE_OF_LEVEL.get(q.level) != kind:
        return f"level '{q.level}' was not requested (allowed: {', '.join(need)})"
    data = _as_question(q, kind)
    problems = question_errors(data, "question")
    if problems:
        return "; ".join(problems[:2])
    if not data["explanation"]:
        return "missing explanation"
    if kind == "mcq" and any(BANNED_OPTION.search(o) for o in data["options"]):
        return 'uses "All / None of the above" style option'
    if kind == "essay":
        leaked = leaked_items(data["content"], data["rubric"])
        if leaked:
            return f"the question text already contains the keywords of rubric item(s) {leaked} — ask, do not tell"
    if not 1 <= q.passage <= len(passages):
        return f"passage must be 1..{len(passages)}"
    quote = norm(q.source_quote)
    if len(quote.split()) < QUOTE_MIN_WORDS:
        return f"source_quote must be at least {QUOTE_MIN_WORDS + 1} words copied from the passage"
    if quote not in norm(passages[q.passage - 1]):
        return f"source_quote is not copied exactly from passage {q.passage}"
    return None


def check_questions(
    data, kind: str, need: dict[str, int], *, passages: list[str], existing: list[str] = ()
) -> tuple[list[dict], list[str]]:
    """need: số câu CÒN THIẾU theo mức của lần gọi này. → (câu hợp lệ — tối đa đủ need, lỗi tiếng Anh).
    Câu dư (quá số cần) bị bỏ, không tính là lỗi."""
    try:
        output = QuestionsOutput.model_validate(data)
    except ValidationError as err:
        return [], [f"answer did not match the JSON schema ({err.error_count()} errors)"]
    seen = [norm(e) for e in existing]
    left = {level: n for level, n in need.items() if n > 0}
    good: list[dict] = []
    errors: list[str] = []
    for i, q in enumerate(output.questions, start=1):
        if need.get(q.level, 0) > 0 and left.get(q.level, 0) <= 0:
            continue  # dư
        problem = _problem(q, kind, need, passages)
        if problem is None and is_duplicate(q.content, seen):
            problem = "repeats an existing question"
        if problem:
            errors.append(f'Question {i} ("{q.content[:60]}"): {problem}')
            continue
        seen.append(norm(q.content))
        left[q.level] -= 1
        item = _as_question(q, kind)
        item["explanation"] = clean_explanation(item["explanation"])  # 26/11: không nhắc "the text" (3b)
        good.append(item)
    missing = {level: n for level, n in left.items() if n > 0}
    if missing:
        errors.append("still missing: " + ", ".join(f"{n} {level}" for level, n in missing.items()))
    return good, errors
