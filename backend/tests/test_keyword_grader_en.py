"""Test B3 — bộ chấm từ khóa tiếng Anh + bộ chọn theo ngôn ngữ (module 09 · Tuấn · 14/11/2026).

Chạy:  python -m pytest tests/test_keyword_grader_en.py -v      (trong thư mục backend)
Câu mẫu: so sánh list và tuple (ví dụ trong docs/Review-AI-Grading.md).
"""

import json
from pathlib import Path

import pytest

from app.ai.review import keyword_grader, keyword_grader_en, keyword_grading

QUESTION = "Compare lists and tuples in Python, and give an example of when to use a tuple."
RUBRIC = [
    {"text": "A list can be changed", "max_points": 3, "main_keywords": ["change", "mutable", "modify", "append"],
     "sub_keywords": ["list"]},
    {"text": "A tuple cannot be changed after it is created", "max_points": 3,
     "main_keywords": ["immutable", "not change", "not modify"], "sub_keywords": ["tuple"]},
    {"text": "List syntax uses square brackets", "max_points": 1,
     "main_keywords": ["square bracket", "[ ]", "[]"], "sub_keywords": ["list"]},
    {"text": "Tuple syntax uses parentheses", "max_points": 1,
     "main_keywords": ["parenthesis", "round bracket", "( )", "()"], "sub_keywords": ["tuple"]},
    {"text": "A sensible example of when to use a tuple", "max_points": 2,
     "main_keywords": ["coordinate", "date", "dictionary key", "fixed data"], "sub_keywords": []},
]  # fmt: skip

FULL = (
    "A list is mutable, so you can append or modify items. "
    "A tuple is immutable and cannot be changed after it is created. "
    "Lists are written with square brackets [ ], tuples with parentheses ( ). "
    "Use a tuple for fixed data such as coordinates (x, y)."
)


def results(answer, rubric=RUBRIC, question=QUESTION):
    return [r["result"] for r in keyword_grader_en.grade_essay(rubric, answer, question)]


def total(answer):
    return sum(r["points"] for r in keyword_grader_en.grade_essay(RUBRIC, answer, QUESTION))


def test_full_answer_scores_10():
    assert results(FULL) == ["full"] * 5
    assert total(FULL) == 10


def test_word_forms_match():
    """Lemmatize: "Lists ... changing ... tuples" khớp "list", "change", "tuple"."""
    answer = "Lists allow changing their items at any time. Tuples are immutable once you create them."
    assert results(answer)[:2] == ["full", "full"]


def test_negation_blocks_main_keyword():
    """ "tuples cannot be changed" KHÔNG được tính là "list thay đổi được" (ý 1)."""
    answer = "Tuples cannot be changed after creation, that is the main idea of this answer."
    out = results(answer)
    assert out[0] == "none"
    assert out[1] == "full"


def test_swapped_clauses_are_not_full():
    """Đảo chủ thể qua "but" (QT12): không ý nào được trọn điểm."""
    answer = "A list cannot be changed after creation but a tuple can be changed whenever you want."
    out = results(answer)
    assert out[0] != "full" and out[1] != "full"


def test_and_is_not_a_boundary():
    answer = "A tuple is created once and is immutable, so its items stay the same forever."
    assert results(answer)[1] == "full"


def test_comma_neighbor_subject_is_borrowed():
    answer = "For the list, items can be modified later in the program without problems."
    assert results(answer)[0] == "full"


def test_subject_only_scores_zero():
    answer = "Lists and tuples are both very common in Python programs written by students."
    assert results(answer)[:2] == ["none", "none"]


def test_main_without_subject_is_partial():
    answer = "Its items are immutable, nobody can edit them after the object is created."
    assert results(answer)[1] == "partial"


@pytest.mark.parametrize("answer", [None, "", "   "])
def test_empty_answer_scores_zero(answer):
    assert total(answer) == 0


def test_copying_the_question_scores_zero():
    assert total(QUESTION) == 0


def test_keyword_listing_is_capped():
    answer = "list mutable append tuple immutable square bracket parenthesis coordinate"
    assert "full" not in results(answer)


def test_short_answer_is_capped_at_partial():
    assert results("List mutable.")[0] == "partial"


def test_brackets_without_spaces_match():
    answer = "In Python a list uses [] while a tuple uses () when you write them in code."
    out = results(answer)
    assert out[2] == "full" and out[3] == "full"


def test_python_keywords_distinguish_for_and_while():
    rubric = [{"text": "while repeats while a condition is true", "max_points": 10,
               "main_keywords": ["condition"], "sub_keywords": ["while"]}]  # fmt: skip
    assert results("A for loop runs over a range and checks no condition at all here.", rubric, "") == ["none"]
    assert results("A while loop keeps running as long as its condition is true.", rubric, "") == ["full"]


def test_evidence_is_original_sentence():
    out = keyword_grader_en.grade_essay(RUBRIC, FULL, QUESTION)
    assert out[1]["evidence"] == "A tuple is immutable and cannot be changed after it is created."


# ─────────────── chọn bộ chấm theo ngôn ngữ ───────────────


def test_dispatcher_picks_by_language(monkeypatch):
    calls = []
    monkeypatch.setattr(keyword_grader, "grade_essay", lambda *a: calls.append("vi") or [])
    monkeypatch.setattr(keyword_grader_en, "grade_essay", lambda *a: calls.append("en") or [])
    keyword_grading.grade_essay(RUBRIC, FULL, QUESTION)
    vi_rubric = [{"text": "Biến là tên gắn với dữ liệu", "max_points": 10, "main_keywords": ["dữ liệu"]}]
    keyword_grading.grade_essay(vi_rubric, "x", "Biến là gì?")
    assert calls == ["en", "vi"]


def test_vietnamese_bank_still_scores_10_through_dispatcher():
    """Bài tiếng Việt cũ (đang làm dở lúc chuyển ngôn ngữ) vẫn chấm bằng bộ tiếng Việt như trước."""
    bank = json.loads((Path(__file__).parents[1] / "data/review/course_312.json").read_text(encoding="utf-8"))
    essay = next(q for q in bank["questions"] if q["type"] == "essay")
    sample = essay["explanation"].removeprefix("Đáp án mẫu:").strip()
    out = keyword_grading.grade_essay(essay["rubric"], sample, essay["content"])
    assert sum(r["points"] for r in out) == 10


FOR_WHILE = [  # góp ý 12/11 (QT12) — giống test_keyword_grader.EN_FOR_WHILE
    {"text": "for: when the number of loops is known", "max_points": 5,
     "main_keywords": ["number of loops", "known in advance", "each element"], "sub_keywords": ["for"]},
    {"text": "while: when the number of loops is not known", "max_points": 5,
     "main_keywords": ["don't know", "not known", "condition"], "sub_keywords": ["while"]},
]  # fmt: skip


def test_reversed_comma_answer_blocked_by_borrow_rule():
    """Luật chặn mượn vế (QT12): "while … number of loops, for … don't know" KHÔNG được trọn điểm."""
    answer = "Use while when you know the number of loops, for when you don't know how many times to repeat."
    assert "full" not in results(answer, FOR_WHILE, "")


def test_correct_comma_answer_gets_full():
    answer = "Use for when you know the number of loops, while when you don't know how many times to repeat."
    assert results(answer, FOR_WHILE, "") == ["full", "full"]


# ─────────────── ngân hàng tiếng Anh (B2) ───────────────

EN_BANK = json.loads((Path(__file__).parents[1] / "data/review/course_312_en.json").read_text(encoding="utf-8"))
EN_ESSAYS = [q for q in EN_BANK["questions"] if q["type"] == "essay"]


@pytest.mark.parametrize("q", EN_ESSAYS, ids=lambda q: q["code"])
def test_every_english_essay_scores_10_with_its_model_answer(q):
    sample = q["explanation"].removeprefix("Model answer:").strip()
    out = keyword_grader_en.grade_essay(q["rubric"], sample, q["content"])
    assert [r["result"] for r in out] == ["full"] * len(out)


@pytest.mark.parametrize("q", EN_ESSAYS, ids=lambda q: q["code"])
def test_copying_an_english_question_scores_zero(q):
    out = keyword_grading.grade_essay(q["rubric"], q["content"], q["content"])
    assert sum(r["points"] for r in out) == 0


def test_wrong_swap_result_gets_no_credit():
    """Duyệt B2 (14/11): "a = 7" từng thành "= 7" (bỏ "a" như stopword) → bài sai "b = 7 and a = 3" vẫn được ½ ý."""
    q = next(q for q in EN_ESSAYS if q["code"] == "VAR-TL-06")
    out = keyword_grader_en.grade_essay(q["rubric"], "After the swap the values are b = 7 and a = 3.", q["content"])
    assert out[3]["result"] == "none"


def test_code_comma_is_not_a_clause_boundary():
    s = keyword_grader_en.Sentence.build("The short form is a, b = b, a, which swaps them.")
    assert s.find(("a", "b", "=", "b", "a")) and len(set(s.seg)) == 2  # chỉ tách ở ", which"


def test_english_bank_routes_to_english_grader():
    assert not any(keyword_grading.is_vietnamese(q["rubric"], q["content"]) for q in EN_ESSAYS)
