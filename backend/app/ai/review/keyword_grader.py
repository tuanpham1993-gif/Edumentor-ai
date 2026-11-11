"""Chấm tự luận theo TỪ KHÓA — dùng cho MockAI và làm dự phòng khi AI thật lỗi
(A10 — chốt 09/11, cách a; sửa theo checklist 10/11: L4, L7, L8, L10, L13) (module 09 · Tuấn).

Mỗi ý barem có main_keywords (nội dung ý) và sub_keywords (chủ thể của ý):
  - full    (đủ điểm ý): có từ khóa chính NẰM CÙNG CÂU với một từ khóa phụ
                         (ý không có từ khóa phụ → chỉ cần có từ khóa chính)
  - partial (½ điểm ý):  có từ khóa chính nhưng câu đó không có chủ thể
  - none    (0):         không có từ khóa chính (chỉ nhắc chủ thể cũng = 0 — L13, chốt 10/11)

So khớp (L10, L4 — chốt 10/11):
  - Chuẩn hóa: chữ thường, Unicode NFC (gõ kiểu nào cũng như nhau), gộp khoảng trắng, BỎ khoảng trắng quanh
    ký hiệu ("tong = 0" ≡ "tong=0", "n + 1" ≡ "n+1").
  - Câu có dấu → so CÓ DẤU (để "dùng" ≠ "dừng" ≠ "đúng", "yếu" ≠ "yêu cầu").
    Câu gõ HOÀN TOÀN không dấu → so bản bỏ dấu ("dieu kien" khớp "điều kiện").
  - Từ khóa chữ/số khớp NGUYÊN TỪ ("if" không khớp trong "elif", "for" không khớp "format");
    từ khóa bắt đầu / kết thúc bằng ký hiệu ("+=", "int(") khớp chuỗi con ở phía đó.

Chống lách:
  - Chép đề (L7): câu trong bài làm có ≥ COPY_RATIO cụm 3 từ liên tiếp nằm trong đề → bỏ qua câu đó.
  - Liệt kê từ khóa (L8): câu ≥ LIST_MIN_WORDS từ, > LIST_DENSITY số từ là từ khóa VÀ chạm từ khóa chính của
    ≥ LIST_MIN_ITEMS ý khác nhau (nhồi nhiều ý vào một chuỗi từ khóa) → không được "full".
  - Liệt kê trên CẢ BÀI: tính mật độ từ khóa trên mọi câu không chép đề; > ANSWER_LIST_DENSITY → cả bài tối đa
    "partial" (bắt kiểu chia chuỗi từ khóa thành nhiều câu ngắn, mỗi câu một ý — luật theo câu không bắt được).
  - Bài quá ngắn (< MIN_ANSWER_WORDS từ, không tính câu chép đề) hoặc câu khớp < MIN_SENTENCE_WORDS từ
    → tối đa "partial".
Bằng chứng (evidence) = câu gốc trong bài làm đã khớp.
Hạn chế (ghi rõ khi bảo vệ): chỉ dò từ khóa, không hiểu nghĩa — giai đoạn 2 AI thật chấm theo ngữ nghĩa.
  Ví dụ đã biết (chốt 11/11 — chấp nhận, KHÔNG thêm luật chặn): viết mỗi ý thành một câu cực ngắn kèm chữ đệm,
  vd "cả hai and là. ít nhất một or là. đảo not là." vẫn được 10/10 (mật độ từ khóa < ANSWER_LIST_DENSITY nhờ chữ
  đệm). Chặn thêm chỉ thành cuộc đua lách – chặn; AI thật (bước 5.1) chấm theo nghĩa sẽ xử lý.
"""

import re
import unicodedata
from dataclasses import dataclass, field

MIN_ANSWER_WORDS = 6
MIN_SENTENCE_WORDS = 3
COPY_NGRAM = 3  # độ dài cụm từ dùng để phát hiện chép đề
COPY_RATIO = 0.7  # L7: ≥ 70% cụm 3 từ của câu nằm trong đề → câu chép đề
LIST_MIN_WORDS = 5  # L8: chỉ xét liệt kê với câu từ 5 từ (câu ngắn đã có luật riêng)
LIST_DENSITY = 0.75  # L8: > 75% số từ là từ khóa …
LIST_MIN_ITEMS = 2  # … và chạm ≥ 2 ý → coi là liệt kê.
# (Đề xuất ban đầu 60%: đo trên đáp án mẫu, câu viết tốt đã đạt 67–83% → 60% phạt nhầm; bài liệt kê thật ≈ 93%.)
ANSWER_LIST_DENSITY = 0.85  # Cả bài: > 85% số từ là từ khóa → tối đa "partial".
# (Đo 10/11: đáp án mẫu + bài viết thật 24–73%; bài liệt kê 89–100%.)

# Tách câu ở . ! ? khi theo sau là khoảng trắng / hết bài (không cắt "6.5", "a.append"), và ở xuống dòng.
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+|\n+")
_WORD = re.compile(r"\w+")
_SPACE_AROUND_SYMBOL = re.compile(r"\s*([^\w\s])\s*")


def fold(text: str) -> str:
    """Chữ thường + NFC + gộp khoảng trắng + bỏ khoảng trắng quanh ký hiệu. GIỮ dấu tiếng Việt."""
    text = unicodedata.normalize("NFC", (text or "").lower())
    text = re.sub(r"\s+", " ", text).strip()
    return _SPACE_AROUND_SYMBOL.sub(r"\1", text)


def strip_accents(text: str) -> str:
    """Bỏ dấu tiếng Việt: "điều kiện" → "dieu kien"."""
    text = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    return unicodedata.normalize("NFC", "".join(ch for ch in text if unicodedata.category(ch) != "Mn"))


def normalize(text: str) -> str:
    """Dạng so sánh thô (bỏ dấu) — dùng để đếm từ, phát hiện chép đề."""
    return strip_accents(fold(text))


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END.split(text or "") if s.strip()]


def _word_count(text: str) -> int:
    return len(_WORD.findall(text or ""))


def _ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


@dataclass
class Sentence:
    raw: str  # câu gốc (làm bằng chứng)
    text: str = ""  # dạng so khớp: có dấu, hoặc bỏ dấu nếu câu gõ không dấu
    plain: bool = False  # câu gõ hoàn toàn không dấu
    tokens: list[str] = field(default_factory=list)  # từ (bỏ dấu) — đếm từ, so với đề
    copied: bool = False  # L7
    listing: bool = False  # L8

    @classmethod
    def build(cls, raw: str) -> "Sentence":
        folded = fold(raw)
        plain = folded == strip_accents(folded)
        return cls(raw=raw, text=folded, plain=plain, tokens=_WORD.findall(strip_accents(folded)))


def _pattern(sentence: Sentence, keyword: str) -> re.Pattern | None:
    kw = fold(keyword)
    if sentence.plain:
        kw = strip_accents(kw)
    if not kw:
        return None
    left = r"(?<!\w)" if kw[0].isalnum() else ""
    right = r"(?!\w)" if kw[-1].isalnum() else ""
    return re.compile(left + re.escape(kw) + right)


def _has(sentence: Sentence, keywords: list[str]) -> bool:
    return any((p := _pattern(sentence, k)) is not None and p.search(sentence.text) for k in keywords)


def _keyword_words(sentence: Sentence, keywords: list[str]) -> tuple[int, int]:
    """(số từ nằm trong một từ khóa bất kỳ của barem, tổng số từ) của một câu."""
    covered: set[int] = set()
    for k in keywords:
        p = _pattern(sentence, k)
        if p is None:
            continue
        for m in p.finditer(sentence.text):
            covered.update(range(m.start(), m.end()))
    words = list(_WORD.finditer(sentence.text))
    hit = sum(1 for w in words if any(i in covered for i in range(w.start(), w.end())))
    return hit, len(words)


def _keyword_density(sentence: Sentence, keywords: list[str]) -> float:
    """Tỉ lệ số từ trong câu nằm trong một từ khóa bất kỳ của barem."""
    hit, total = _keyword_words(sentence, keywords)
    return hit / total if total else 0.0


def _all_keywords(rubric: list[dict]) -> list[str]:
    return [k for item in rubric for k in (item.get("main_keywords") or []) + (item.get("sub_keywords") or [])]


def _is_copied(sentence: Sentence, question_tokens: list[str]) -> bool:
    """L7: câu gần như chép lại đề."""
    if not question_tokens or not sentence.tokens:
        return False
    if len(sentence.tokens) < COPY_NGRAM:
        return all(t in set(question_tokens) for t in sentence.tokens)
    grams = _ngrams(sentence.tokens, COPY_NGRAM)
    shared = grams & _ngrams(question_tokens, COPY_NGRAM)
    return len(shared) / len(grams) >= COPY_RATIO


def prepare(answer: str | None, rubric: list[dict], question: str | None = None) -> list[Sentence]:
    """Tách câu + đánh dấu câu chép đề (L7) và câu liệt kê từ khóa (L8)."""
    question_tokens = _WORD.findall(normalize(question or ""))
    all_keywords = _all_keywords(rubric)
    sentences = [Sentence.build(raw) for raw in split_sentences(answer or "")]
    for s in sentences:
        s.copied = _is_copied(s, question_tokens)
        items_hit = sum(1 for item in rubric if _has(s, item.get("main_keywords") or []))
        s.listing = (
            len(s.tokens) >= LIST_MIN_WORDS
            and items_hit >= LIST_MIN_ITEMS
            and _keyword_density(s, all_keywords) > LIST_DENSITY
        )
    return sentences


def grade_item(sentences: list[Sentence], item: dict, *, cap_partial: bool) -> dict:
    """Kết quả MỘT ý: {"result", "points", "evidence"}."""
    main = item.get("main_keywords") or []
    sub = item.get("sub_keywords") or []
    max_points = float(item["max_points"])

    usable = [s for s in sentences if not s.copied]
    main_hits = [s for s in usable if _has(s, main)]
    with_subject = [s for s in main_hits if not sub or _has(s, sub)]
    full_hits = [
        s for s in with_subject if len(s.tokens) >= MIN_SENTENCE_WORDS and not s.listing
    ]

    if full_hits and not cap_partial:
        return {"result": "full", "points": max_points, "evidence": full_hits[0].raw}
    if main_hits:
        evidence = (with_subject or main_hits)[0].raw
        return {"result": "partial", "points": max_points / 2, "evidence": evidence}
    return {"result": "none", "points": 0.0, "evidence": None}


def grade_essay(rubric: list[dict], answer: str | None, question: str | None = None) -> list[dict]:
    """Chấm cả câu: một kết quả cho mỗi ý barem, theo đúng thứ tự barem.

    question: nội dung đề — để bỏ qua câu chép lại đề (L7). Không truyền thì không kiểm chép đề.
    """
    sentences = prepare(answer, rubric, question)
    own = [s for s in sentences if not s.copied]
    own_words = sum(len(s.tokens) for s in own)
    keywords = _all_keywords(rubric)
    counts = [_keyword_words(s, keywords) for s in own]
    total = sum(t for _, t in counts)
    answer_density = sum(h for h, _ in counts) / total if total else 0.0
    cap_partial = own_words < MIN_ANSWER_WORDS or answer_density > ANSWER_LIST_DENSITY
    return [grade_item(sentences, item, cap_partial=cap_partial) for item in rubric]
