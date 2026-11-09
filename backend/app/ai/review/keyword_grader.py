"""Chấm tự luận theo TỪ KHÓA — dùng cho MockAI và làm dự phòng khi AI thật lỗi
(A10 — chốt 09/11, cách a) (module 09 · Tuấn · GĐ3, 09/11/2026).

Mỗi ý barem có main_keywords (nội dung ý) và sub_keywords (chủ thể của ý):
  - full    (đủ điểm ý): có từ khóa chính NẰM CÙNG CÂU với một từ khóa phụ
                         (ý không có từ khóa phụ → chỉ cần có từ khóa chính)
  - partial (½ điểm ý):  có từ khóa chính nhưng ở câu không có chủ thể, HOẶC chỉ có từ khóa phụ
  - none    (0):         không có từ khóa nào
So sánh sau khi chuẩn hóa: chữ thường, BỎ DẤU tiếng Việt, gộp khoảng trắng ("Thay đổi" = "thay doi").
Bằng chứng (evidence) = câu gốc trong bài làm đã khớp.
Chống lách: bài quá ngắn (< MIN_ANSWER_WORDS từ) hoặc câu khớp quá ngắn (< MIN_SENTENCE_WORDS từ,
vd chỉ liệt kê "list tuple mutable") → tối đa "partial".
Hạn chế (ghi rõ khi bảo vệ): chỉ dò từ khóa, không hiểu nghĩa — giai đoạn 2 AI thật chấm theo ngữ nghĩa.
"""

import re
import unicodedata

MIN_ANSWER_WORDS = 6
MIN_SENTENCE_WORDS = 3

# Tách câu ở . ! ? khi theo sau là khoảng trắng / hết bài (không cắt "6.5", "a.append"), và ở xuống dòng.
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+|\n+")
_WORD = re.compile(r"\w+")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END.split(text or "") if s.strip()]


def _contains(sentence: str, keyword: str) -> bool:
    """Từ khóa dạng chữ/số khớp NGUYÊN TỪ ("so" không khớp "sosanh"); ký hiệu ("+=", "()") khớp chuỗi con."""
    kw = normalize(keyword)
    if not kw:
        return False
    left = r"(?<!\w)" if kw[0].isalnum() else ""
    right = r"(?!\w)" if kw[-1].isalnum() else ""
    return re.search(left + re.escape(kw) + right, sentence) is not None


def _word_count(text: str) -> int:
    return len(_WORD.findall(text))


def grade_item(sentences: list[tuple[str, str]], item: dict, *, cap_partial: bool) -> dict:
    """sentences = [(câu gốc, câu đã chuẩn hóa)]. Trả {"result", "points", "evidence"} cho MỘT ý."""
    main = item.get("main_keywords") or []
    sub = item.get("sub_keywords") or []
    max_points = float(item["max_points"])

    def has(norm: str, keywords: list[str]) -> bool:
        return any(_contains(norm, k) for k in keywords)

    main_hits = [(raw, norm) for raw, norm in sentences if has(norm, main)]
    full_hits = [(raw, norm) for raw, norm in main_hits if not sub or has(norm, sub)]
    full_hits = [(raw, norm) for raw, norm in full_hits if _word_count(norm) >= MIN_SENTENCE_WORDS]
    sub_hits = [(raw, norm) for raw, norm in sentences if sub and has(norm, sub)]

    if full_hits and not cap_partial:
        return {"result": "full", "points": max_points, "evidence": full_hits[0][0]}
    evidence = (full_hits or main_hits or sub_hits or [(None, None)])[0][0]
    if evidence is not None:
        return {"result": "partial", "points": max_points / 2, "evidence": evidence}
    return {"result": "none", "points": 0.0, "evidence": None}


def grade_essay(rubric: list[dict], answer: str | None) -> list[dict]:
    """Chấm cả câu: một kết quả cho mỗi ý barem, theo đúng thứ tự barem."""
    sentences = [(raw, normalize(raw)) for raw in split_sentences(answer or "")]
    cap_partial = _word_count(answer or "") < MIN_ANSWER_WORDS
    return [grade_item(sentences, item, cap_partial=cap_partial) for item in rubric]
