"""Test chấm tự luận bằng từ khóa — ai/review/keyword_grader.py (A10, cách a) (module 09 · Tuấn · GĐ3).
Cập nhật 10/11 theo checklist sửa ngân hàng 312: L4, L7, L8, L10, L13, V1.

Chạy:  python -m pytest tests/test_keyword_grader.py -v      (trong thư mục backend)
"""

import unicodedata

import pytest

from app.ai.review.keyword_grader import fold, grade_essay, normalize, split_sentences
from app.ai.review.validator import grading_errors
from scripts import seed_review

BANK = seed_review.load_bank(seed_review.DEFAULT_FILE)


def question(code):
    return next(q for q in BANK["questions"] if q["code"] == code)


def rubric_of(code):
    return question(code)["rubric"]


def grade(code, answer):
    """Chấm như hệ thống thật: có truyền đề (để bỏ câu chép đề — L7)."""
    q = question(code)
    return grade_essay(q["rubric"], answer, q["content"])


LIST_TUPLE = rubric_of("312-PY-TL-02")  # ví dụ ở mục 5 tài liệu họp 09/11
# V1 (chốt 10/11): bài làm mẫu mới — vẫn 7/10 với luật chặt hơn (L2a, L13a)
SAMPLE_ANSWER = "List thì sửa được còn tuple thì không sửa được. List dùng ngoặc vuông. Tuple thì dùng ngoặc tròn."
ESSAYS = [q["code"] for q in BANK["questions"] if q["type"] == "essay"]


def total(results):
    return sum(r["points"] for r in results)


def test_normalize_removes_vietnamese_marks():
    assert normalize("  Thay ĐỔI   được ") == "thay doi duoc"
    assert normalize("Điều kiện") == "dieu kien"


def test_fold_keeps_marks_and_removes_spaces_around_symbols():
    assert fold("Tong = TONG + i") == "tong=tong+i"  # L4
    assert fold("Điều  kiện") == "điều kiện"  # giữ dấu (L10)
    assert fold(unicodedata.normalize("NFD", "kiểu")) == "kiểu"  # NFD → NFC


def test_split_sentences_keeps_decimals_and_method_calls():
    text = "Điểm 6.5 là Khá. Gọi a.append(4) để thêm!\nDòng mới"
    assert split_sentences(text) == ["Điểm 6.5 là Khá.", "Gọi a.append(4) để thêm!", "Dòng mới"]


def test_meeting_example_scores_7_of_10():
    """Bài làm mẫu (V1, chốt 10/11): Y1 đạt 3 · Y2 đạt 3 · Y3 một phần 1 · Y4 không có 0 = 7/10."""
    results = grade("312-PY-TL-02", SAMPLE_ANSWER)

    assert [r["result"] for r in results] == ["full", "full", "partial", "none"]
    assert [r["points"] for r in results] == [3, 3, 1, 0]
    assert results[0]["evidence"] == "List thì sửa được còn tuple thì không sửa được."
    assert results[2]["evidence"] == "Tuple thì dùng ngoặc tròn."
    assert results[3]["evidence"] is None
    assert grading_errors(results, LIST_TUPLE) == []


def test_old_meeting_sample_is_now_stricter():
    """Bài mẫu cũ: "tuple thì không" không còn đạt ý Y2 (L2a); chỉ nhắc "ngoặc vuông" (từ khóa phụ) = 0 (L13a)."""
    results = grade("312-PY-TL-02", "List thì sửa được còn tuple thì không. List dùng ngoặc vuông.")
    assert [r["result"] for r in results] == ["full", "none", "none", "none"]


def test_answer_without_diacritics_scores_the_same():
    results = grade("312-PY-TL-02", "list thi sua duoc con tuple thi khong sua duoc. list dung ngoac vuong. tuple thi dung ngoac tron.")
    assert total(results) == 7


def test_nfd_input_scores_the_same():
    assert total(grade("312-PY-TL-02", unicodedata.normalize("NFD", SAMPLE_ANSWER))) == 7


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


# ─────────────── Checklist 10/11 ───────────────


@pytest.mark.parametrize("code", ESSAYS)
def test_copying_the_question_scores_zero(code):
    """L7: chép nguyên đề → 0 điểm ở mọi câu tự luận."""
    assert total(grade(code, question(code)["content"])) == 0


def test_copy_plus_own_answer_still_counts():
    """Chép đề rồi tự trả lời: chỉ câu chép bị bỏ qua."""
    answer = "Biến là gì? Biến là một cái tên gắn với dữ liệu lưu trong bộ nhớ. Ví dụ: tuoi = 20."
    assert total(grade("312-VAR-TL-01", answer)) == 10


@pytest.mark.parametrize(
    ("code", "answer"),
    [
        ("312-ITER-TL-01", "Ta dùng break và continue trong bài này."),  # "dùng" ≠ "dừng"
        ("312-COND-TL-01", "Ta dùng if trong chương trình của mình."),  # "dùng" ≠ "đúng"
        ("312-COND-TL-02", "Đề bài yêu cầu viết chương trình xếp loại và dùng else."),  # "yêu" ≠ "yếu"
        ("312-PY-TL-02", "Tôi không biết tuple là gì cả."),  # L2a: "không" không còn là từ khóa
    ],
)
def test_accent_collisions_and_subject_only_score_zero(code, answer):
    """L10 + L13a: không trùng chữ khi bỏ dấu; chỉ nhắc chủ thể (từ khóa phụ) = 0."""
    assert total(grade(code, answer)) == 0


def test_unaccented_answer_still_matches():
    """L10: câu gõ hoàn toàn không dấu vẫn so được với từ khóa có dấu."""
    answer = "List thay doi duoc bang append. Tuple bat bien sau khi tao. List dung [ ] con tuple dung ( ). Vi du toa do (x, y) nen dung tuple."
    assert total(grade("312-PY-TL-02", answer)) == 10


def test_symbol_spacing_does_not_matter():
    """L4: tong=0 và tong = tong + i được tính như tong = 0 và tong += i."""
    answer = "Nhập n bằng n = int(input()). Đặt tong=0 trước vòng lặp. Dùng for i in range(1, n+1) để chạy. Mỗi vòng ta viết tong = tong + i."
    assert [r["result"] for r in grade("312-ITER-TL-03", answer)] == ["full"] * 4


@pytest.mark.parametrize(
    ("code", "answer"),
    [
        ("312-PY-TL-02", "list sửa thay đổi tuple không thay đổi bất biến ngoặc tròn ngoặc vuông tọa độ ví dụ"),
        ("312-ITER-TL-01", "break dừng thoát continue bỏ qua lần tiếp"),
    ],
)
def test_long_keyword_listing_is_capped(code, answer):
    """L8: chuỗi từ khóa nhồi nhiều ý trên một dòng → không ý nào được "full"."""
    assert all(r["result"] != "full" for r in grade(code, answer))


def test_short_real_sentence_is_not_a_listing():
    """L8: câu thật ngắn, dày thuật ngữ nhưng chỉ một ý → vẫn được "full"."""
    assert grade("312-PY-TL-02", "List thay đổi được bằng append. Tuple bất biến sau khi tạo.")[0]["result"] == "full"


@pytest.mark.parametrize(
    ("code", "answer"),
    [
        ("312-ITER-TL-01", "break thoát dừng kết thúc. continue bỏ qua lần lặp tiếp."),
        ("312-COND-TL-01", "if điều kiện đúng. elif thêm khác tiếp. else sai còn lại tất cả."),
        ("312-PY-TL-02", "list sửa thay đổi append. tuple không thay đổi bất biến. tuple ngoặc tròn ngoặc vuông. tuple tọa độ ngày tháng."),
    ],
)
def test_listing_split_into_short_sentences_is_capped(code, answer):
    """Luật cả bài: chuỗi từ khóa chia thành nhiều câu ngắn (mỗi câu một ý) → mật độ cả bài > 85% → tối đa "một phần"."""
    assert all(r["result"] != "full" for r in grade(code, answer))
