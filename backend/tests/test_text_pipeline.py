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


def test_meaningful_stopwords_kept():
    assert "only" in preprocess("Only lists can change")
    assert "but" in preprocess("lists change but tuples do not")


def test_normalize():
    assert normalize("  Hello\tWORLD \n ") == "hello world"
    assert normalize("can’t") == "can't"
    assert normalize("") == ""


def test_steps_compose():
    tokens = tokenize(normalize("The list is NOT empty"))
    assert tokens == ["the", "list", "is", "not", "empty"]
    assert remove_stopwords(tokens) == ["list", "not", "empty"]
