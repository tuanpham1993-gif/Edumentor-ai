"""Lỗi nhỏ sau review 25/11 (Tuấn · 26/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md mục 7.7):
3a lý do câu bị loại lưu vào việc soạn · 3b lời giải thích không nhắc "the text" · 3c cấu hình REVIEW_REVEAL_ON_FAIL.

AI giả, không gọi mạng. Chạy:  python -m pytest tests/test_generation_detail.py -v
"""

import pytest
from pydantic import ValidationError

from app.ai.prompts.review_generate import GEN_SYSTEM_PROMPT
from app.ai.review.question_schema import check_questions, clean_explanation
from app.services import review_generation_service as gen
from tests.test_generation_jobs import SKILL, sync_jobs  # noqa: F401
from tests.test_question_gen import PASSAGES, FakeAI, essay, gdb, mcq  # noqa: F401

# ─────────────── 3a: lý do câu bị loại ───────────────


@pytest.mark.parametrize(
    ("reason", "group"),
    [
        ('Question "Q": tests the same source sentence as an existing question ("x")', "same_idea"),
        ("an independent solver chose B (x) instead of A", "solver"),
        ("the model answer only scores 5.0/10 with keyword grading", "model_answer"),
        ("copying the question text already scores 6/10", "leaks_answer"),
        ("the question text already contains the keywords of rubric item(s) [1]", "leaks_answer"),
        ("an answer to a different question scores 7/10 — rubric too generic", "generic_rubric"),
        ("the correct option is 2.1x longer than the longest wrong option (guessable)", "length_hint"),
        ("means almost the same as an existing question (similarity 0.97)", "near_duplicate"),
        ('Question 2 ("Q"): repeats an existing question', "near_duplicate"),
        ("source_quote is not copied exactly from passage 1", "quote"),
        ("passage must be 1..2", "quote"),
        ("the answer was not valid JSON for the schema (x)", "schema"),
        ('Question 1 ("Q"): question: câu advanced phải có 4–5 ý, đang có 3', "shape"),
        ("question: tổng max_points phải = 10, đang = 9", "shape"),
        ("question: 4 lựa chọn bị trùng nhau", "shape"),
        ("missing explanation", "shape"),
        ("level 'easy' was not requested (allowed: recognize)", "shape"),
        ("something new", "other"),
    ],
)
def test_reason_group(reason, group):
    assert gen.reason_group(reason) == group


def test_job_detail_records_rejections_per_round(gdb, sync_jobs):  # noqa: F811
    bad = {"questions": [essay("easy", 1) | {"passage": 9}]}  # tự luận luôn hỏng: passage không hợp lệ
    mcqs = {"questions": [mcq("recognize", i) for i in range(6)] + [mcq("understand", i) for i in range(6)]}
    sync_jobs["ai"] = FakeAI({"mcq": [mcqs], "essay": [bad] * 6})
    job = gen.request(gdb, SKILL, None)
    assert job.status == "failed"
    rounds = job.detail["rounds"]
    assert rounds[0]["step"] == 2 and rounds[0]["saved"] == 11 and rounds[0]["rejected"] == {}
    essay_rounds = [r for r in rounds if r["step"] == 3]
    assert len(essay_rounds) == 2 and all(r["saved"] == 0 for r in essay_rounds)
    assert essay_rounds[0]["rejected"] == {"quote": 3} and len(essay_rounds[0]["examples"]) == 3
    assert all(len(e) <= gen.EXAMPLE_CHARS for e in essay_rounds[0]["examples"])


# ─────────────── 3b: lời giải thích không nhắc "the text" ───────────────


@pytest.mark.parametrize(
    ("text", "clean"),
    [
        ("The text states that containers share a context.", "Containers share a context."),
        ("The correct option is right because the text states the goal is safety.",
         "The correct option is right because the goal is safety."),
        ("According to the passage, a Pod is the smallest unit. This passage explains that pods die.",
         "A Pod is the smallest unit. Pods die."),
        ("Model answer: The source says images are templates.", "Model answer: Images are templates."),
        ("kubectl get pods lists pods.", "kubectl get pods lists pods."),  # không đụng câu không dẫn nguồn
        (None, None),
    ],
)  # fmt: skip
def test_clean_explanation(text, clean):
    assert clean_explanation(text) == clean


def test_generated_question_explanation_is_cleaned():
    q = mcq() | {"explanation": "The passage states that FROM names the base image."}
    good, _ = check_questions({"questions": [q]}, "mcq", {"recognize": 1}, passages=PASSAGES)
    assert good[0]["explanation"] == "FROM names the base image."
    assert 'never write "the text"' in GEN_SYSTEM_PROMPT


# ─────────────── 3c: cấu hình sai giá trị ───────────────


def test_reveal_setting_rejects_typo():
    from app.core.config import Settings

    with pytest.raises(ValidationError):
        Settings(REVIEW_REVEAL_ON_FAIL="mcq-only")
    assert Settings(REVIEW_REVEAL_ON_FAIL="none").REVIEW_REVEAL_ON_FAIL == "none"
