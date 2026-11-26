"""Ý kiến thức của câu AI soạn — Bước A chống trùng ý (module 09 · Tuấn · 25/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md
mục 7.7).

Thử thật 25/11: 30 câu Kubernetes chỉ dùng 15 câu trích; cổng gần trùng theo nghĩa (embedding) chấm các cặp diễn đạt lại
chỉ 0,52–0,80 nên không chặn được. Mỗi câu AI soạn đã có `source_quote` (chép nguyên văn từ đoạn tài liệu) → dùng nó:

    Ý của câu = {(chunk_id, số thứ tự câu trong đoạn)} mà câu trích phủ lên.
    Hai câu CÙNG Ý khi chung ít nhất một câu của cùng một đoạn (trích hai nửa của cùng một câu vẫn bắt được).

Câu soạn tay (không có câu trích) / câu trích không còn khớp đoạn (admin sửa đoạn) → ý rỗng = không bao giờ trùng.
Chỉ so CÙNG LOẠI (trắc nghiệm với trắc nghiệm) — một trắc nghiệm và một tự luận cùng ý là bình thường.
"""

import re
from dataclasses import dataclass

from app.ai.review.question_schema import norm

Idea = frozenset[tuple[int, int]]
EMPTY: Idea = frozenset()
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+|\n+")


def sentences(text: str) -> list[str]:
    """Các câu của đoạn đã chuẩn hóa (như so câu trích), bỏ câu rỗng."""
    return [s for s in (norm(part) for part in _SENTENCE_END.split(text or "")) if s]


def idea_of(quote: str | None, chunk_id: int | None, chunk_text: str | None) -> Idea:
    """Các câu của đoạn mà câu trích phủ lên → {(chunk_id, i)}. Không xác định được → EMPTY."""
    q = norm(quote or "")
    if not q or chunk_id is None or not chunk_text:
        return EMPTY
    spans, pos = [], 0
    for s in sentences(chunk_text):
        spans.append((pos, pos + len(s)))
        pos += len(s) + 1  # nối bằng một khoảng trắng
    joined = " ".join(sentences(chunk_text))
    start = joined.find(q)
    if start < 0:
        return EMPTY
    end = start + len(q)
    return frozenset((chunk_id, i) for i, (a, b) in enumerate(spans) if a < end and start < b)


def quote_of(ai_check: dict | None) -> str | None:
    gen = (ai_check or {}).get("gen") or {}
    return gen.get("source_quote")


@dataclass(frozen=True)
class UsedIdea:
    question_id: int | None  # None = câu vừa đạt trong lần soạn này (chưa lưu)
    type: str  # mcq | essay
    idea: Idea
    quote: str


def from_rows(rows) -> list[UsedIdea]:
    """Dòng review_repository.question_sources → UsedIdea (bỏ câu không xác định được ý)."""
    out = []
    for row in rows:
        quote = quote_of(row.ai_check)
        idea = idea_of(quote, row.chunk_id, row.content)
        if idea:
            out.append(UsedIdea(row.question_id, row.type, idea, quote))
    return out


def clash(idea: Idea, kind: str, used: list[UsedIdea]) -> UsedIdea | None:
    """Câu đã có CÙNG LOẠI dùng chung ít nhất một câu nguồn → câu đó; không → None."""
    if not idea:
        return None
    return next((u for u in used if u.type == kind and u.idea & idea), None)
