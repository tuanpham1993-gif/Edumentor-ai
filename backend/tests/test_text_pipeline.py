"""Test B1 — khối 1 tiền xử lý NLP tiếng Anh (module 09 · Tuấn · 14/11/2026).

Chạy:  python -m pytest tests/test_text_pipeline.py -v      (trong thư mục backend)
Cần dữ liệu NLTK: punkt_tab, stopwords, wordnet, averaged_perceptron_tagger_eng (xem docstring text_pipeline.py).
"""

import pytest

from app.ai.review.text_pipeline import (
    NEGATIONS,
    _verb_of_s_form,
    lemmatize,
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


def test_without_is_a_negation_and_once_is_kept():
    """26/11 (đề 494): "without a broker" phải giữ phủ định; "at most once" không được rút còn "most"."""
    assert preprocess("without a broker") == ["without", "broker"]
    assert "without" in NEGATIONS
    assert preprocess("at most once") == ["most", "once"]
    assert preprocess("at least once") == ["least", "once"]


@pytest.mark.parametrize(
    "text, verb",
    [
        ("A sensor detects motion.", "detect"),
        ("The broker delivers it to all subscribers.", "deliver"),
        ("The network layer transmits the data.", "transmit"),
        ("A gateway connects local devices to the internet.", "connect"),
        ("A client publishes a message to a topic.", "publish"),
        ("The gateway translates between protocols.", "translate"),
        ("The client subscribes to a topic.", "subscribe"),
        ("Assignment uses the = sign to store a value.", "use"),
        ("It uses sensors and actuators.", "use"),
        ("The sensor senses motion.", "sense"),
    ],
)
def test_third_person_verbs_reach_base_form(text, verb):
    """26/11: gán từ loại sau khi bỏ stopwords → động từ "-s" bị coi là danh từ ("detects"), "uses" → "us"."""
    assert verb in preprocess(text)


@pytest.mark.parametrize("word", ["status", "bus", "gas", "less", "always", "this", "news", "analysis", "series"])
def test_non_verb_s_words_kept(word):
    """Từ đuôi "s" không phải động từ ngôi 3 → giữ nguyên."""
    assert _verb_of_s_form(word) == word
    assert lemmatize([word]) == [word]


def test_nouns_with_verb_sense_still_use_noun_branch():
    """Từ vừa danh từ vừa động từ về đúng gốc qua nhánh danh từ như cũ; "users", "leaves" (lá) không bị đổi sang động từ."""
    assert preprocess("Users like the links and switches.") == ["user", "like", "link", "and", "switch"]
    assert "leaf" in preprocess("Green leaves need water.")


def test_keyword_and_answer_share_the_verb_form():
    """Từ khóa đi qua cùng hàm: "detects" / "detect" ở barem và ở bài làm phải về cùng một dạng."""
    assert preprocess("detects") == preprocess("detect") == ["detect"]
    assert preprocess("publishes") == ["publish"]
    assert preprocess("delivers") == preprocess("deliver")


def test_analyses_is_a_known_limit():
    """Giới hạn đã biết (26/11): "analyses" về "analysis" (danh từ số nhiều hợp lệ), không về "analyse"."""
    assert preprocess("A layer analyses data.") == ["layer", "analysis", "data"]


# ─────────────── 27/11: số đi kèm đơn vị đo (Tuấn duyệt) ───────────────


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("17 kWh", ["17", "kwh"]),
        ("17.0 kWh", ["17", "kwh"]),
        ("17kWh", ["17", "kwh"]),
        ("0.10 V", ["0.1", "v"]),
        ("1mV", ["1", "mv"]),
        ("5V supply", ["5", "v", "supply"]),
        ("0,1 °C", ["0.1", "degc"]),
        ("10 °C", ["10", "degc"]),
        ("sample every 2 s", ["sample", "every", "2", "sec"]),
        ("70 %RH", ["70", "%", "rh"]),
    ],
)
def test_numbers_with_units_are_normalised(text, expected):
    assert preprocess(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("print(3.0)", ["print", "(", "3.0", ")"]),  # số không đơn vị: "3.0" khác "3" trong Python
        ("3.0%2", ["3.0", "%", "2"]),  # % là phép chia lấy dư, không phải đơn vị
        ("x%2", ["x", "%", "2"]),
        ("10%3", ["10", "%", "3"]),
        ("2s complement", ["2s", "complement"]),  # đơn vị một chữ phải cách số
        ("5mins", ["5mins"]),  # đơn vị phải hết từ
        ("0x1A", ["0x1a"]),
        ("x1m = 3", ["x1m", "=", "3"]),
        ("1e5", ["1e5"]),
        ("2f", ["2f"]),
        ("x = 1,5", ["x", "=", "1", "5"]),  # tuple, không phải 1.5
    ],
)
def test_code_numbers_are_not_touched(text, expected):
    assert preprocess(text) == expected


def test_digits_around_commas_are_kept():
    """Trước 27/11 "range(1,5)" mất cả hai số (word_tokenize giữ "1,5" thành một từ rồi bị bỏ)."""
    assert preprocess("range(1,5)") == preprocess("range(1, 5)") == ["range", "(", "1", "5", ")"]
    assert preprocess("[1,2,3]") == ["[", "1", "2", "3", "]"]


def test_thousands_style_numbers_stay_one_token():
    """"1,000" / "4,096" giữ nguyên — không đoán hàng nghìn hay thập phân; không tách thành "1" và "000"."""
    assert preprocess("1,000 readings") == ["1,000", "reading"]
    assert preprocess("4,096 V") == ["4,096", "v"]
    assert "1" not in preprocess("1,000 readings")


def test_keywords_go_through_the_same_normalisation():
    assert preprocess("17 kwh") == preprocess("17.0 kWh")
    assert preprocess("0.1 degc") == preprocess("0,1 °C")
    assert preprocess("2 s") == preprocess("2 s") == ["2", "sec"]
    # Từ khóa số KHÔNG kèm đơn vị giữ nguyên dạng → barem ghi "17", không ghi "17.0" (check.py báo)
    assert preprocess("17.0") == ["17.0"]
