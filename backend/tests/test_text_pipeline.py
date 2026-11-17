"""Test B1 — khối 1 tiền xử lý NLP tiếng Anh (module 09 · Tuấn · 14/11/2026).

Chạy:  python -m pytest tests/test_text_pipeline.py -v      (trong thư mục backend)
Cần dữ liệu NLTK: punkt_tab, stopwords, wordnet, averaged_perceptron_tagger_eng (xem docstring text_pipeline.py).
"""

import pytest

from app.ai.review.text_pipeline import (
    normalize,
    preprocess,
    remove_stopwords,
    tokenize,
)


def test_lists_can_be_changed():
    words = preprocess("Lists CAN be changed!")
    assert "list" in words and "change" in words
    assert "!" not in words


@pytest.mark.parametrize(
    "text",
    ["tuples cannot be modified", "Tuples can't be modified", "Tuples can’t be modified", "Tuples are not modifiable"],
)
def test_negation_is_kept(text):
    """Bỏ phủ định thì "tuple không đổi được" thành "tuple đổi được" — nghĩa bị đảo."""
    words = preprocess(text)
    assert "not" in words and "tuple" in words


@pytest.mark.parametrize("text", ["", "   ", "\n\t", "?!.,"])
def test_empty_or_punctuation_only(text):
    assert preprocess(text) == []


@pytest.mark.parametrize("word", ["loops", "looping", "looped", "loop"])
def test_verb_forms_share_lemma(word):
    assert preprocess(f"The program {word}") == ["program", "loop"]


@pytest.mark.parametrize(
    "plural, singular",
    [("tuples", "tuple"), ("lists", "list"), ("dictionaries", "dictionary"), ("classes", "class"), ("keys", "key")],
)
def test_programming_plurals(plural, singular):
    """WordNet không biết "tuple" → luật bỏ đuôi số nhiều."""
    assert preprocess(plural) == [singular]


def test_code_symbols_kept_punctuation_dropped():
    words = preprocess("Lists use [ ], tuples use ( ). Example: a[0] = 9.")
    for symbol in ["[", "]", "(", ")", "="]:
        assert symbol in words
    for punct in [",", ".", ":"]:
        assert punct not in words


@pytest.mark.parametrize(
    "text, expected",
    [
        ("7 // 2 = 3", ["7", "//", "2", "=", "3"]),
        ("7 / 2 = 3.5", ["7", "/", "2", "=", "3.5"]),
        ("count != 0", ["count", "!=", "0"]),  # trước khi sửa: ["count", "=", "0"] — đảo nghĩa
        ("2 ** 3 = 8", ["2", "**", "3", "=", "8"]),
        ("i <= 10", ["i", "<=", "10"]),  # "i" là stopword nhưng cạnh ký hiệu → tên biến, giữ (14/11)
        ("pi is 3.14.", ["pi", "is", "3.14"]),
    ],
)
def test_operators_and_decimals(text, expected):
    assert preprocess(text) == expected


@pytest.mark.parametrize(
    "packed, spaced",
    [("range(1,n+1)", "range(1, n + 1)"), ("total+=i", "total += i"), ("count!=0", "count != 0"), ("x==y", "x == y")],
)
def test_operator_spacing_does_not_matter(packed, spaced):
    """NLTK coi "n+1" là một từ rồi bỏ đi — tách ký hiệu trước để viết liền hay cách đều như nhau."""
    assert preprocess(packed) == preprocess(spaced)


def test_hyphenated_words_and_methods_kept():
    assert preprocess("a read-only list") == ["read-only", "list"]
    assert "3.5" in preprocess("7 / 2 = 3.5")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("a = 7", ["a", "=", "7"]),  # trước 14/11: ["=", "7"] — khớp nhầm "b = 7"
        ("a, b = b, a", ["a", "b", "=", "b", "a"]),
        ("total += i", ["total", "+=", "i"]),
        ("a is 7", ["a", "is", "7"]),  # mạo từ "a" không đứng trước "is" → tên biến
        ("a list is mutable", ["list", "is", "mutable"]),  # mạo từ → vẫn bỏ
        ("I use a loop", ["use", "loop"]),
    ],
)
def test_single_letter_variables_kept_near_code(text, expected):
    assert preprocess(text) == expected


def test_meaningful_stopwords_kept():
    assert "only" in preprocess("Only lists can change")
    assert "but" in preprocess("lists change but tuples do not")
    assert "again" in preprocess("enter the password again")


def test_normalize():
    assert normalize("  Hello\tWORLD \n ") == "hello world"
    assert normalize("can’t") == "can't"
    assert normalize("") == ""


def test_steps_compose():
    tokens = tokenize(normalize("The list is NOT empty"))
    assert tokens == ["the", "list", "is", "not", "empty"]
    assert remove_stopwords(tokens) == ["list", "is", "not", "empty"]  # "is" là từ khóa Python → giữ


@pytest.mark.parametrize(
    "text, expected",
    [
        ("while loop", ["while", "loop"]),
        ("for loop", ["for", "loop"]),
        ("if and else", ["if", "and", "else"]),
        ("x in my_list", ["x", "in", "my_list"]),
        ("the function returns True", ["function", "return", "true"]),
    ],
)
def test_python_keywords_kept(text, expected):
    """Stopwords NLTK có for / while / if / in / and... — bỏ đi thì không phân biệt được for với while."""
    assert preprocess(text) == expected
