"""Test chấm tự luận bằng từ khóa — ai/review/keyword_grader.py (A10, cách a) (module 09 · Tuấn · GĐ3).

Chạy:  python -m pytest tests/test_keyword_grader.py -v      (trong thư mục backend)
"""

import pytest

from app.ai.review.keyword_grader import grade_essay, normalize, split_sentences
from app.ai.review.validator import grading_errors
from scripts import seed_review

BANK = seed_review.load_bank(seed_review.DEFAULT_FILE)


def rubric_of(code):
    return next(q for q in BANK["questions"] if q["code"] == code)["rubric"]


LIST_TUPLE = rubric_of("312-PY-TL-02")  # ví dụ ở mục 5 tài liệu họp 09/11


def total(results):
    return sum(r["points"] for r in results)


def test_normalize_removes_vietnamese_marks():
    assert normalize("  Thay ĐỔI   được ") == "thay doi duoc"
    assert normalize("Điều kiện") == "dieu kien"


def test_split_sentences_keeps_decimals_and_method_calls():
    text = "Điểm 6.5 là Khá. Gọi a.append(4) để thêm!\nDòng mới"
    assert split_sentences(text) == ["Điểm 6.5 là Khá.", "Gọi a.append(4) để thêm!", "Dòng mới"]


def test_meeting_example_scores_7_of_10():
    """Bài làm mẫu đã gửi thầy: Y1 đạt 3 · Y2 đạt 3 · Y3 một phần 1 · Y4 không có 0 = 7/10."""
    results = grade_essay(LIST_TUPLE, "List thì sửa được còn tuple thì không. List dùng ngoặc vuông.")

    assert [r["result"] for r in results] == ["full", "full", "partial", "none"]
    assert [r["points"] for r in results] == [3, 3, 1, 0]
    assert results[0]["evidence"] == "List thì sửa được còn tuple thì không."
    assert results[2]["evidence"] == "List dùng ngoặc vuông."
    assert results[3]["evidence"] is None
    assert grading_errors(results, LIST_TUPLE) == []


def test_answer_without_diacritics_scores_the_same():
    results = grade_essay(LIST_TUPLE, "list thi sua duoc con tuple thi khong. list dung ngoac vuong.")
    assert total(results) == 7


def test_full_answer_scores_10():
    answer = (
        "List thay đổi được bằng append. Tuple là bất biến sau khi tạo. "
        "List dùng [ ] còn tuple dùng ( ). Ví dụ tọa độ (x, y) nên dùng tuple."
    )
    assert total(grade_essay(LIST_TUPLE, answer)) == 10


def test_main_keyword_without_subject_is_partial():
    """Có "sửa được" nhưng không nói của list hay tuple → chỉ một phần."""
    results = grade_essay(LIST_TUPLE, "Kiểu này thì sửa được, kiểu kia thì không đổi được nữa.")
    assert results[0]["result"] == "partial" and results[0]["points"] == 1.5


@pytest.mark.parametrize("answer", ["list tuple mutable", "list sửa, tuple không"])
def test_keyword_listing_is_capped_at_partial(answer):
    results = grade_essay(LIST_TUPLE, answer)
    assert all(r["result"] != "full" for r in results)


@pytest.mark.parametrize("answer", [None, "", "   "])
def test_empty_answer_scores_zero(answer):
    results = grade_essay(LIST_TUPLE, answer)
    assert total(results) == 0 and all(r["result"] == "none" for r in results)


def test_word_keywords_match_whole_words_only():
    """Từ khóa chữ khớp NGUYÊN TỪ: "for" không khớp nhầm vào "format"."""
    rubric = [
        {"text": "a", "max_points": 5, "main_keywords": ["for"], "sub_keywords": []},
        {"text": "b", "max_points": 5, "main_keywords": ["+="], "sub_keywords": []},
    ]
    results = grade_essay(rubric, "Dùng vòng lặp format để in kết quả ra. Cộng dồn bằng tong += i mỗi lần.")
    assert [r["result"] for r in results] == ["none", "full"]  # "format" ≠ "for"; "+=" khớp chuỗi con


def test_every_bank_essay_scores_10_with_its_model_answer():
    """Đáp án mẫu (explanation) của mỗi câu tự luận trong ngân hàng phải đạt tối đa — kiểm barem có dùng được."""
    for q in BANK["questions"]:
        if q["type"] == "essay":
            results = grade_essay(q["rubric"], q["explanation"].removeprefix("Đáp án mẫu: "))
            assert total(results) == 10, (q["code"], [r["result"] for r in results])
