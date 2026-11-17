"""Test ví dụ chấm mẫu (few-shot) trong prompt chấm tự luận (module 09 · Tuấn · 17/11/2026). Không gọi Gemini.

Chạy:  python -m pytest tests/test_review_grading_fewshot.py -v      (trong thư mục backend)
"""

import json
import re
from types import SimpleNamespace

import pytest

from app.ai.prompts.review_grading import (
    FEWSHOT_EN,
    FEWSHOT_SOURCE_CODES,
    GRADE_SYSTEM_PROMPT_EN,
    GRADE_SYSTEM_PROMPT_VI,
    grading_prompt,
)
from app.core.config import settings
from app.services import review_grader
from scripts.gold_sheets import BACKEND, load_split

QUESTION = {
    "content": "Explain what print() and input() do in Python.",
    "rubric": [
        {"text": "print() displays data on the screen", "max_points": 5},
        {"text": "input() reads data typed by the user", "max_points": 5},
    ],
    "explanation": "Model answer: print shows data, input reads what the user types.",
}


def bank_questions() -> dict[str, dict]:
    with open(BACKEND / load_split()["bank"], encoding="utf-8") as f:
        bank = json.load(f)
    return {q["code"]: q for q in bank["questions"] if q.get("code")}


def test_without_flag_prompt_is_unchanged():
    system, _, version = grading_prompt(QUESTION, "print shows text")
    assert system == GRADE_SYSTEM_PROMPT_EN and version == "grade-en-v2"


def test_few_shot_adds_examples_to_system_prompt_and_version():
    system, user, version = grading_prompt({**QUESTION, "few_shot": True}, "print shows text")
    assert system == GRADE_SYSTEM_PROMPT_EN + FEWSHOT_EN and "CALIBRATION EXAMPLES" in system
    assert version == "grade-en-v2+fs"
    assert "CALIBRATION" not in user  # ví dụ cố định ở system prompt, user prompt chỉ có câu đang chấm


def test_few_shot_with_rag_version():
    chunks = [{"title": "print", "content": "print() writes to the screen."}]
    _, _, version = grading_prompt({**QUESTION, "few_shot": True, "context_chunks": chunks}, "x")
    assert version == "grade-en-v2+rag+fs"


def test_vietnamese_prompt_has_no_english_examples():
    question = {"content": "Hàm print() dùng để làm gì?", "rubric": [{"text": "In dữ liệu ra màn hình", "max_points": 10}],
                "few_shot": True}  # fmt: skip
    system, _, version = grading_prompt(question, "in ra màn hình")
    assert system == GRADE_SYSTEM_PROMPT_VI and version == "grade-vi-v2"


def _phrases(text: str, n: int = 5) -> set[str]:
    words = re.findall(r"[a-z0-9_()=+/<>]+", text.lower())
    return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}


def test_examples_only_come_from_dev_questions():
    """Chống rò rỉ: ví dụ KHÔNG được chứa đề / barem / đáp án mẫu của câu TEST (B10 đo trên test một lần)."""
    split, bank = load_split(), bank_questions()
    examples = _phrases(FEWSHOT_EN)
    for code in split["test"]:
        q = bank[code]
        texts = [q["content"], q.get("explanation") or ""] + [r["text"] for r in q["rubric"]]
        leaked = examples & set().union(*(_phrases(t) for t in texts))
        assert not leaked, f"Ví dụ trùng câu test {code}: {sorted(leaked)[:3]}"
    # và mọi câu dùng làm ví dụ đều là câu dev; mỗi ý barem được trích trong ví dụ có thật ở câu đó
    assert set(FEWSHOT_SOURCE_CODES) <= set(split["dev"])
    dev_items = {r["text"].lower() for c in FEWSHOT_SOURCE_CODES for r in bank[c]["rubric"]}
    for quoted in re.findall(r'Item: "([^"]+)"', FEWSHOT_EN):
        assert any(quoted.lower() in item for item in dev_items), quoted


@pytest.mark.parametrize("flag", [True, False])
def test_grader_sets_flag_from_settings(monkeypatch, flag):
    monkeypatch.setattr(settings, "REVIEW_GRADING_FEWSHOT", flag)
    monkeypatch.setattr(settings, "REVIEW_GRADING_RAG", False)
    answer = SimpleNamespace(question=SimpleNamespace(type="essay", **QUESTION))
    question = review_grader._question_dict(answer)
    assert question.get("few_shot", False) is flag
