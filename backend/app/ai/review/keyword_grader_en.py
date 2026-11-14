"""Chấm tự luận TIẾNG ANH theo từ khóa — dự phòng khi Gemini lỗi + đối chiếu (module 09 · Tuấn · B3, 14/11/2026).

Cùng luật với bộ tiếng Việt (`keyword_grader.py`, A10 / L4–L13 / QT12), chỉ khác cách SO KHỚP:
khớp trên DÃY TỪ ĐÃ LEMMATIZE của khối 1 (`text_pipeline.preprocess`) thay vì regex trên chuỗi ký tự, nên
"loops / looping / looped" ≡ "loop", "tuples" ≡ "tuple", "cannot be changed" ≡ "not change".

Mỗi ý barem: main_keywords (nội dung ý) + sub_keywords (chủ thể, có thể rỗng):
  - full    : từ khóa chính + chủ thể cùng ĐOẠN (hoặc đoạn liền kề cùng vế — QT12) → đủ điểm ý
  - partial : có từ khóa chính nhưng thiếu chủ thể / chủ thể ở vế khác → ½ điểm
  - none    : không có từ khóa chính (chỉ nhắc chủ thể = 0, L13)
Một từ khóa có thể nhiều từ ("square bracket", "not change"): khớp khi các từ đứng LIỀN NHAU sau tiền xử lý.

Phủ định: từ khóa CHÍNH có "not / no / never…" trong NEGATION_WINDOW từ đứng trước (cùng đoạn) → không tính
("tuples cannot be changed" không khớp "change" của ý "list thay đổi được"). Từ khóa tự mang phủ định
("not change") khớp bình thường.

Tách vế (QT12): ranh giới CỨNG ";" và "but / whereas / however" (đổi ý); dấu phẩy là ranh giới MỀM (mượn chủ thể ở
đoạn liền kề cùng vế, trừ khi đoạn chứa từ khóa chính đã có chủ thể của ý khác). KHÔNG tách ở "and".
Chống lách (giống bộ tiếng Việt): bỏ câu chép đề (L7), câu liệt kê từ khóa không được full (L8), cả bài mật độ
từ khóa > ANSWER_LIST_DENSITY hoặc < MIN_ANSWER_WORDS từ → tối đa partial.
Bằng chứng (evidence) = câu gốc trong bài làm đã khớp.
"""

import re
from dataclasses import dataclass, field
from functools import lru_cache

from app.ai.review.text_pipeline import NEGATIONS, normalize, preprocess, tokenize

MIN_ANSWER_WORDS = 6
COPY_NGRAM = 3
COPY_RATIO = 0.7
LIST_MIN_WORDS = 5
LIST_DENSITY = 0.75
LIST_MIN_ITEMS = 2
ANSWER_LIST_DENSITY = 0.85
NEGATION_WINDOW = 2  # số từ (sau tiền xử lý) đứng trước từ khóa chính được xét phủ định

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+|\n+")
_HARD_BOUNDARY = re.compile(r";|(?<!\w)(?:but|whereas|however)(?!\w)", re.IGNORECASE)
_SOFT_BOUNDARY = re.compile(r",")
# Dấu phẩy giữa hai "từ" ≤ 2 ký tự là dấu phẩy của CODE ("a, b = b, a", "range(1, n + 1)", "1, 5, 9") — không tách vế,
# nếu không mỗi mảnh được tiền xử lý riêng và tên biến "a" bị bỏ như stopword (sửa 14/11 khi duyệt B2).
_CODE_COMMA_BEFORE = re.compile(r"(?:^|\W)\w{1,2}\s*$")
_CODE_COMMA_AFTER = re.compile(r"^\s*\w{1,2}(?:\W|$)")


def _is_code_comma(raw: str, pos: int) -> bool:
    return bool(_CODE_COMMA_BEFORE.search(raw[:pos]) and _CODE_COMMA_AFTER.match(raw[pos + 1 :]))


@lru_cache(maxsize=2048)
def _kw(keyword: str) -> tuple[str, ...]:
    """Từ khóa → dãy từ sau tiền xử lý (cache: cùng barem được chấm nhiều lần)."""
    return tuple(preprocess(keyword))


def _word_count(text: str) -> int:
    """Số từ thật (chữ / số) — kể cả stopwords; dùng cho luật bài ngắn và mật độ liệt kê."""
    return sum(1 for t in tokenize(normalize(text)) if t.isalnum())


@dataclass
class Sentence:
    raw: str  # câu gốc (bằng chứng)
    lemmas: list[str] = field(default_factory=list)  # dãy từ đã tiền xử lý của cả câu
    seg: list[int] = field(default_factory=list)  # seg[i] = đoạn chứa lemmas[i]
    hard: list[bool] = field(default_factory=list)  # hard[j] = ranh giới TRƯỚC đoạn j là ranh giới cứng
    words: int = 0
    copied: bool = False
    listing: bool = False

    @classmethod
    def build(cls, raw: str) -> "Sentence":
        cuts = [(m.start(), True) for m in _HARD_BOUNDARY.finditer(raw)]
        cuts += [(m.start(), False) for m in _SOFT_BOUNDARY.finditer(raw) if not _is_code_comma(raw, m.start())]
        cuts.sort()
        bounds = [(0, False), *cuts, (len(raw), False)]
        s = cls(raw=raw, words=_word_count(raw))
        for j in range(len(bounds) - 1):
            start, is_hard = bounds[j]
            piece = raw[start : bounds[j + 1][0]]
            if piece.startswith((",", ";")):
                piece = piece[1:]
            s.hard.append(is_hard)
            for lemma in preprocess(piece):
                s.lemmas.append(lemma)
                s.seg.append(j)
        return s

    def find(self, kw: tuple[str, ...]) -> list[int]:
        """Vị trí bắt đầu các lần dãy kw xuất hiện liền nhau trong câu."""
        n = len(kw)
        if not n:
            return []
        return [i for i in range(len(self.lemmas) - n + 1) if tuple(self.lemmas[i : i + n]) == kw]

    def negated(self, i: int) -> bool:
        """Có từ phủ định trong NEGATION_WINDOW từ ngay trước vị trí i, cùng đoạn."""
        lo = max(0, i - NEGATION_WINDOW)
        return any(self.lemmas[k] in NEGATIONS and self.seg[k] == self.seg[i] for k in range(lo, i))

    def same_clause(self, a: int, b: int) -> bool:
        lo, hi = min(a, b), max(a, b)
        return hi == lo + 1 and not self.hard[hi]


def _main_starts(s: Sentence, keywords: list[str]) -> list[int]:
    """Vị trí các lần khớp từ khóa CHÍNH, bỏ lần đứng sau phủ định (trừ từ khóa tự mang phủ định)."""
    out = []
    for k in keywords:
        kw = _kw(k)
        self_negative = any(w in NEGATIONS for w in kw)
        out += [i for i in s.find(kw) if self_negative or not s.negated(i)]
    return out


def _starts(s: Sentence, keywords: list[str]) -> list[int]:
    return [i for k in keywords for i in s.find(_kw(k))]


def _covered(s: Sentence, keywords: list[str]) -> int:
    """Số TỪ chữ / số (sau tiền xử lý) nằm trong một lần khớp từ khóa bất kỳ. Không đếm ký hiệu "[ ]", "( )" —
    mẫu số (_word_count) cũng chỉ đếm chữ / số; đếm lệch thì câu tự nhiên có "[ ]" bị coi là liệt kê."""
    hit: set[int] = set()
    for k in keywords:
        kw = _kw(k)
        for i in s.find(kw):
            hit.update(range(i, i + len(kw)))
    return sum(1 for i in hit if s.lemmas[i].isalnum())


def _all_keywords(rubric: list[dict]) -> list[str]:
    return [k for item in rubric for k in (item.get("main_keywords") or []) + (item.get("sub_keywords") or [])]


def _ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def _is_copied(s: Sentence, question_lemmas: list[str]) -> bool:
    if not question_lemmas or not s.lemmas:
        return False
    if len(s.lemmas) < COPY_NGRAM:
        return all(t in set(question_lemmas) for t in s.lemmas)
    grams = _ngrams(s.lemmas, COPY_NGRAM)
    return len(grams & _ngrams(question_lemmas, COPY_NGRAM)) / len(grams) >= COPY_RATIO


def split_sentences(text: str) -> list[str]:
    return [p.strip() for p in _SENTENCE_END.split(text or "") if p.strip()]


def prepare(answer: str | None, rubric: list[dict], question: str | None = None) -> list[Sentence]:
    question_lemmas = preprocess(question or "")
    keywords = _all_keywords(rubric)
    sentences = [Sentence.build(raw) for raw in split_sentences(answer or "")]
    for s in sentences:
        s.copied = _is_copied(s, question_lemmas)
        items_hit = sum(1 for item in rubric if _starts(s, item.get("main_keywords") or []))
        s.listing = (
            s.words >= LIST_MIN_WORDS and items_hit >= LIST_MIN_ITEMS and _covered(s, keywords) / s.words > LIST_DENSITY
        )
    return sentences


def _full_in_sentence(s: Sentence, main: list[str], sub: list[str], other_sub: list[str]) -> bool:
    main_segs = {s.seg[i] for i in _main_starts(s, main)}
    if not main_segs:
        return False
    if not sub:
        return True
    sub_segs = {s.seg[i] for i in _starts(s, sub)}
    other_segs = {s.seg[i] for i in _starts(s, other_sub)}
    for m in main_segs:
        if m in sub_segs:
            return True
        if m in other_segs:
            continue  # đoạn này nói về chủ thể của ý khác → không mượn chủ thể bên cạnh (QT12)
        if any(n in sub_segs and s.same_clause(m, n) for n in (m - 1, m + 1)):
            return True
    return False


def grade_item(sentences: list[Sentence], item: dict, *, cap_partial: bool, other_sub: list[str]) -> dict:
    main = item.get("main_keywords") or []
    sub = item.get("sub_keywords") or []
    max_points = float(item["max_points"])
    usable = [s for s in sentences if not s.copied]
    main_hits = [s for s in usable if _main_starts(s, main)]
    with_subject = [s for s in main_hits if not sub or _starts(s, sub)]
    full_hits = [s for s in with_subject if not s.listing and _full_in_sentence(s, main, sub, other_sub)]
    if full_hits and not cap_partial:
        return {"result": "full", "points": max_points, "evidence": full_hits[0].raw}
    if main_hits:
        return {"result": "partial", "points": max_points / 2, "evidence": (with_subject or main_hits)[0].raw}
    return {"result": "none", "points": 0.0, "evidence": None}


def grade_essay(rubric: list[dict], answer: str | None, question: str | None = None) -> list[dict]:
    """Một kết quả cho mỗi ý barem, đúng thứ tự barem (cùng giao diện với keyword_grader.grade_essay)."""
    sentences = prepare(answer, rubric, question)
    own = [s for s in sentences if not s.copied]
    own_words = sum(s.words for s in own)
    keywords = _all_keywords(rubric)
    density = sum(_covered(s, keywords) for s in own) / own_words if own_words else 0.0
    cap_partial = own_words < MIN_ANSWER_WORDS or density > ANSWER_LIST_DENSITY
    results = []
    for item in rubric:
        own_sub = {_kw(k) for k in item.get("sub_keywords") or []}
        other_sub = [
            k for other in rubric if other is not item for k in other.get("sub_keywords") or [] if _kw(k) not in own_sub
        ]
        results.append(grade_item(sentences, item, cap_partial=cap_partial, other_sub=other_sub))
    return results
