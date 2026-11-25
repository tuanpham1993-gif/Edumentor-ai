"""G3c — cổng kiểm câu AI soạn: giải mù, L1, gần trùng theo nghĩa, bài giả tự luận (Tuấn · 25/11/2026).

Solver và embedder giả (không gọi mạng). Docs: docs/Review-AI-Tu-Soan-On-Tap.md mục 7.4.
Chạy:  python -m pytest tests/test_question_gate.py -v
"""

import random

import pytest

from app.ai.review.base import AIUnavailableError
from app.ai.review.grading_schema import AIOutputError
from app.ai.review.question_gate import GateContext, blind_solve, fake_scores, length_ratio, run_gate
from tests.test_question_gen import FakeAI, essay, gdb, mcq  # noqa: F401 — dùng lại fixture + câu mẫu G3b


def q_mcq(content="Which instruction sets the base image?", options=None, correct=0):
    return {"type": "mcq", "level": "recognize", "content": content,
            "options": options or ["FROM", "BASE", "IMAGE", "RUN"], "correct_index": correct,
            "explanation": "FROM names the base image.", "chunk_id": 1}  # fmt: skip


def q_essay(level="easy", n=1):
    q = essay(level, n)
    q.pop("passage"), q.pop("source_quote")
    return {**q, "type": "essay", "chunk_id": 1}


class Solver:
    """Giải đúng theo nội dung: chọn vị trí đang hiển thị của đáp án `answers[content]` (sau khi server xáo)."""

    def __init__(self, answers: dict[str, str] | None = None, *, wrong: bool = False):
        self.answers, self.wrong, self.seen = answers or {}, wrong, []

    def __call__(self, skill, items):
        self.seen.append(items)
        out = []
        for item in items:
            target = self.answers.get(item["content"], "FROM")
            index = item["options"].index(target)
            out.append({"id": item["id"], "index": (index + 1) % 4 if self.wrong else index})
        return {"answers": out}


def ctx(**kw) -> GateContext:
    return GateContext(skill="Docker", chunks={1: "A Dockerfile begins with FROM, which names the base image."},
                       rng=random.Random(7), **kw)  # fmt: skip


# ─────────────── giải mù ───────────────


def test_blind_solve_maps_shuffled_order_back():
    solver = Solver()
    questions = [q_mcq(), q_mcq("Which word starts a Dockerfile?", ["RUN", "COPY", "FROM", "CMD"], correct=2)]
    assert blind_solve(questions, ctx(solve=solver)) == [0, 2]
    shown = solver.seen[0]
    assert "correct_index" not in shown[0] and "explanation" not in shown[0]  # solver không thấy đáp án / giải thích
    assert any(item["options"] != q["options"] for item, q in zip(shown, questions, strict=True))  # đã xáo


def test_solver_disagrees_rejects():
    passed, failed = run_gate([q_mcq()], "mcq", ctx(solve=Solver(wrong=True)))
    assert passed == [] and "independent solver" in failed[0][1]


def test_solver_bad_output_is_skipped_not_rejected():
    def broken(skill, items):
        raise AIOutputError("bad json")

    passed, failed = run_gate([q_mcq()], "mcq", ctx(solve=broken))
    assert failed == [] and passed[0]["ai_check"]["gate"]["solver"] == "skipped"
    passed, _ = run_gate([q_mcq()], "mcq", ctx(solve=lambda s, i: {"answers": [{"id": 1, "index": 9}]}))
    assert passed[0]["ai_check"]["gate"]["solver_index"] is None


def test_solver_unavailable_propagates():
    def down(skill, items):
        raise AIUnavailableError("503")

    with pytest.raises(AIUnavailableError):
        run_gate([q_mcq()], "mcq", ctx(solve=down))


# ─────────────── L1 ───────────────


def test_l1_long_correct_option_rejected():
    long_q = q_mcq(options=["It shares the host operating system kernel directly", "RAM", "Disk", "Fan"])
    assert length_ratio(long_q) > 1.5
    short_q = q_mcq(options=["The Developers", "PO", "SM", "CEO"])  # tỉ lệ 4,7 nhưng chỉ chênh 11 ký tự → không loại
    assert run_gate([short_q], "mcq", ctx(solve=Solver({short_q["content"]: "The Developers"})))[1] == []
    passed, failed = run_gate([long_q], "mcq", ctx(solve=Solver()))
    assert passed == [] and "longer than" in failed[0][1]


# ─────────────── gần trùng theo nghĩa + bám nguồn ───────────────


def fake_embed(text: str) -> list[float]:
    """Vector giả: câu có chữ 'base image' giống nhau; đoạn tài liệu gần với câu đúng."""
    t = text.lower()
    return [1.0 if "base image" in t else 0.0, 1.0 if "from" in t else 0.0, 0.1]


def test_near_duplicate_rejected_and_grounding_recorded():
    c = ctx(solve=Solver(), embed=fake_embed, existing=[(42, "What sets the base image of a build?", "mcq")])
    passed, failed = run_gate([q_mcq()], "mcq", c)
    assert passed == [] and "almost the same" in failed[0][1]

    c = ctx(solve=Solver(), embed=fake_embed, existing=[(42, "How do volumes keep data?", "mcq")])
    passed, failed = run_gate([q_mcq()], "mcq", c)
    gate = passed[0]["ai_check"]["gate"]
    assert failed == [] and gate["max_similarity"] < 0.9 and gate["similar_question_id"] == 42
    assert gate["grounding"] > 0.9 and gate["passed"] is True


def test_duplicates_inside_same_batch():
    passed, failed = run_gate([q_mcq(), q_mcq("Which base image instruction comes first?")], "mcq",
                              ctx(solve=Solver({"Which base image instruction comes first?": "FROM"}),
                                  embed=fake_embed))  # fmt: skip
    assert len(passed) == 1 and len(failed) == 1


def test_without_embedder_skips():
    passed, _ = run_gate([q_mcq()], "mcq", ctx(solve=Solver()))
    assert passed[0]["ai_check"]["gate"]["max_similarity"] is None


# ─────────────── bài giả tự luận ───────────────


def test_good_essay_passes_fake_answers():
    passed, failed = run_gate([q_essay("easy", 1), q_essay("easy", 2)], "essay", ctx())
    assert failed == [] and len(passed) == 2
    scores = passed[1]["ai_check"]["gate"]["fake_scores"]
    assert scores["model"] == 10 and scores["copy"] == 0 and scores["other"] == 0  # bài mẫu câu 1 không ăn barem câu 2


def test_model_answer_missing_keywords_rejected():
    q = q_essay()
    q["explanation"] = "Model answer: they are different things."
    passed, failed = run_gate([q], "essay", ctx())
    assert passed == [] and "model answer only scores" in failed[0][1]


def test_question_that_gives_answer_away_rejected():
    q = q_essay()
    q["content"] = "An image is a read-only template and a container is a running instance; explain."
    assert fake_scores(q, [])["copy"] == 10
    passed, failed = run_gate([q], "essay", ctx())
    assert passed == [] and "gives the answer away" in failed[0][1]


def test_generic_rubric_rejected():
    q = q_essay()
    other = "A read-only template is like a running instance of a class in other languages."
    passed, failed = run_gate([q], "essay", ctx(other_answers=[other]))
    assert passed == [] and "too generic" in failed[0][1]


# ─────────────── nối vào question_gen_service ───────────────


def test_generate_regenerates_gate_failures(gdb):  # noqa: F811
    from app.services import question_gen_service as gen

    first = {"questions": [mcq("recognize", 1), mcq("recognize", 2)]}
    second = {"questions": [mcq("recognize", 3)]}
    ai = FakeAI({"mcq": [first, second]})
    bad_content = mcq("recognize", 2)["content"]

    def solve(skill, items):  # giải sai riêng câu 2 → câu 2 bị loại, soạn lại
        return {"answers": [{"id": it["id"], "index": (it["options"].index("FROM") + (1 if it["content"] == bad_content
                                                                                      else 0)) % 4} for it in items]}  # fmt: skip

    out = gen.generate(gdb, 80, write=ai, need={"recognize": 2}, solve=solve, rng=random.Random(1))
    assert len(out["questions"]) == 2 and out["calls"] == 2 and out["solve_calls"] == 2
    assert any("independent solver" in f for f in ai.calls[1]["feedback"])
    assert all(q["ai_check"]["gate"]["passed"] for q in out["questions"])


def test_duplicate_check_only_same_type():
    c = ctx(solve=Solver(), embed=fake_embed, existing=[(42, "Explain what sets the base image of a build.", "essay")])
    passed, failed = run_gate([q_mcq()], "mcq", c)  # câu tự luận cùng chủ đề không tính là trùng với trắc nghiệm
    assert failed == [] and passed[0]["ai_check"]["gate"]["similar_question_id"] is None


def test_rejection_names_missing_rubric_items():
    q = q_essay()
    q["explanation"] = "Model answer: An image is a read-only template. Containers differ."
    passed, failed = run_gate([q], "essay", ctx())
    assert passed == [] and "item 2 (keywords: running, instance)" in failed[0][1]
