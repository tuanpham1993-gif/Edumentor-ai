"""Bước A — chống trùng ý kiến thức theo câu trích (Tuấn · 25/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md mục 7.7).

Không gọi mạng. Chạy:  python -m pytest tests/test_question_idea.py -v
"""

import random

from app.ai.prompts.review_generate import build_question_prompt
from app.ai.review.mock_ai import pick_from_bank
from app.ai.review.question_gate import GateContext, run_gate
from app.ai.review.question_idea import EMPTY, UsedIdea, idea_of, sentences
from app.core.seed_data.dedupe_question_ideas import dedupe
from app.models import ReviewQuestion, ReviewQuestionMeta
from app.services import question_gen_service as gen
from app.services.review_service import attach_ideas
from tests.test_question_gen import P2, SKILL, FakeAI, essay, fact, gdb, mcq  # noqa: F401

TEXT = "Kubectl is the command-line tool for the cluster. It talks to the control plane, then prints the result."


# ─────────────── ý của câu trích ───────────────


def test_sentences_and_idea_of():
    assert sentences(TEXT) == ["kubectl is the command line tool for the cluster",
                               "it talks to the control plane then prints the result"]  # fmt: skip
    whole = idea_of("Kubectl is the command-line tool for the cluster.", 7, TEXT)
    half = idea_of("the command-line tool for the cluster", 7, TEXT)
    assert whole == half == frozenset({(7, 0)})  # trích nửa câu vẫn cùng ý
    assert idea_of("for the cluster. It talks to the control", 7, TEXT) == frozenset({(7, 0), (7, 1)})  # vắt 2 câu
    assert idea_of("a sentence that is not in the passage", 7, TEXT) == EMPTY
    assert idea_of(None, 7, TEXT) == idea_of("Kubectl is the command-line tool", None, TEXT) == EMPTY


# ─────────────── cổng (phép 5) ───────────────


def _gate_q(quote, kind="mcq", content="Which instruction sets the base image?"):
    q = mcq(quote=quote) if kind == "mcq" else essay()
    q.pop("passage"), q.pop("source_quote")
    q.update(type=kind, chunk_id=12, content=content,
             ai_check={"gen": {"source_quote": quote}})  # fmt: skip
    return q


def test_gate_rejects_same_idea_same_type_only():
    used = [UsedIdea(5, "mcq", idea_of(fact(1), 12, P2), fact(1))]
    ctx = GateContext(skill="Docker", chunks={12: P2}, ideas=list(used))
    same = _gate_q(fact(1), content="Q1?")
    new = _gate_q(fact(2), content="Q2?")
    twin = _gate_q(fact(2).lower(), content="Q3?")  # cùng lô, cùng câu nguồn với câu vừa đạt
    passed, failed = run_gate([same, new, twin], "mcq", ctx)
    assert [q["content"] for q in passed] == ["Q2?"]
    assert [q["content"] for q, _ in failed] == ["Q1?", "Q3?"]
    assert "same source sentence" in failed[0][1] and fact(1) in failed[0][1]
    assert passed[0]["ai_check"]["gate"]["idea"] == [[12, 3]] and passed[0]["ai_check"]["gate"]["version"] == "gate-v2"
    assert len(ctx.ideas) == 2  # câu vừa đạt được thêm vào để chặn lô sau
    # tự luận cùng câu nguồn với trắc nghiệm → không phải trùng (khác loại)
    ctx_essay = GateContext(skill="Docker", chunks={12: P2}, ideas=list(used))
    assert run_gate([_gate_q(fact(1), kind="essay")], "essay", ctx_essay)[1] == []


def test_gate_question_without_quote_not_blocked():
    q = _gate_q(None, content="Hand written?")
    ctx = GateContext(skill="Docker", chunks={12: P2}, ideas=[UsedIdea(5, "mcq", frozenset({(12, 0)}), "x")])
    passed, failed = run_gate([q], "mcq", ctx)
    assert failed == [] and passed[0]["ai_check"]["gate"]["idea"] == []


# ─────────────── soạn: gửi câu trích đã dùng, loại câu trùng ý rồi soạn lại ───────────────


def _ai_question(db, qid, quote, *, kind="mcq", level="recognize", active=True, reason=None, mentor=None):
    shape = ({"options": ["a", "b", "c", "d"], "correct_index": 0} if kind == "mcq" else
             {"rubric": essay()["rubric"], "explanation": "Model answer: x"})  # fmt: skip
    db.add(ReviewQuestion(question_id=qid, skill_id=SKILL, chunk_id=12, type=kind, level=level, content=f"AI {qid}?",
                          source="ai", is_active=active, **shape))  # fmt: skip
    db.flush()
    db.add(ReviewQuestionMeta(question_id=qid, family_id=qid, review_status="auto_approved", origin="on_demand",
                              disabled_reason=reason, mentor_status=mentor,
                              ai_check={"gen": {"source_quote": quote}}))  # fmt: skip


def test_prompt_lists_used_quotes():
    prompt = build_question_prompt("Docker", [{"title": "T", "content": P2}], {"recognize": 2}, [], used=[fact(3)])
    assert "SOURCE SENTENCES ALREADY USED" in prompt and fact(3) in prompt
    assert "(none)" in build_question_prompt("Docker", [{"title": "T", "content": P2}], {"recognize": 2}, [])


def test_existing_ideas_skip_questions_disabled_for_errors(gdb):  # noqa: F811
    _ai_question(gdb, 601, fact(1))
    _ai_question(gdb, 602, fact(2), active=False, reason="duplicate_idea")  # tắt vì trùng → vẫn giữ ý
    _ai_question(gdb, 603, fact(3), active=False, reason="mentor_report")  # tắt vì lỗi → trả lại ý
    gdb.commit()
    assert {u.question_id for u in gen.existing_ideas(gdb, SKILL)} == {601, 602}


def test_generate_sends_used_quotes_and_regenerates_same_idea(gdb):  # noqa: F811
    _ai_question(gdb, 601, fact(1))
    gdb.commit()
    again = mcq("recognize", 0)  # trích fact(1) — trùng câu 601
    ai = FakeAI({"mcq": [{"questions": [again]}, {"questions": [mcq("recognize", 4)]}]})
    out = gen.generate(gdb, SKILL, write=ai, need={"recognize": 1})
    assert [q["ai_check"]["gen"]["source_quote"] for q in out["questions"]] == [fact(5)]
    assert ai.calls[0]["used"] == [fact(1)] and any("same source sentence" in f for f in ai.calls[1]["feedback"])


# ─────────────── ráp đề + P2 ───────────────


def _cand(qid, level, idea, kind="mcq"):
    return {"question_id": qid, "level": level, "type": kind, "chunk_id": 12, "idea": idea}


def test_pick_avoids_same_idea_in_one_exam_but_fills_when_short():
    a = [(12, 1)]
    pool = [_cand(1, "recognize", a), _cand(2, "recognize", a), _cand(3, "recognize", [(12, 2)]),
            _cand(4, "understand", a), _cand(5, "understand", [(12, 3)])]  # fmt: skip
    for seed in range(20):
        picked = pick_from_bank(pool, {"recognize": 2, "understand": 1}, random.Random(seed))
        ids = {q["question_id"] for q in picked}
        assert 3 in ids and 5 in ids and len(ids & {1, 2, 4}) == 1  # mỗi ý một câu
    short = pick_from_bank(pool[:2], {"recognize": 2}, random.Random(0))
    assert {q["question_id"] for q in short} == {1, 2}  # hết câu khác ý → vẫn đủ đề (ràng buộc mềm)
    essay_same = pick_from_bank([_cand(1, "recognize", a), _cand(9, "easy", a, kind="essay")],
                                {"recognize": 1, "easy": 1}, random.Random(0))  # fmt: skip
    assert len(essay_same) == 2  # khác loại → không tính trùng


def test_attach_ideas_penalises_same_idea_as_recent_attempts(gdb):  # noqa: F811
    _ai_question(gdb, 601, fact(1))  # đã làm ở lượt gần nhất
    _ai_question(gdb, 602, fact(1))  # khác câu, cùng ý
    _ai_question(gdb, 603, fact(2))
    gdb.commit()
    cands = [{"question_id": q, "type": "mcq"} for q in (602, 603)]
    penalty = attach_ideas(gdb, cands, {601: 3})
    assert penalty == {601: 3, 602: 3} and cands[0]["idea"] == [(12, 2)]  # fact(1) = câu thứ 3 của P2


# ─────────────── script dọn ───────────────


def test_dedupe_keeps_mentor_passed_then_oldest(gdb):  # noqa: F811
    _ai_question(gdb, 601, fact(1))
    _ai_question(gdb, 602, fact(1), mentor="passed")
    _ai_question(gdb, 603, fact(1))
    _ai_question(gdb, 604, fact(2))
    _ai_question(gdb, 605, fact(1), kind="essay", level="easy")  # khác loại → giữ
    gdb.commit()
    dry = dedupe(gdb, SKILL)
    assert dry["disabled"] == [(601, 602), (603, 602)] and gdb.get(ReviewQuestion, 601).is_active  # chạy thử: không ghi
    dedupe(gdb, SKILL, apply=True)
    assert [gdb.get(ReviewQuestion, q).is_active for q in (601, 602, 603, 604, 605)] == [False, True, False, True, True]
    assert gdb.get(ReviewQuestionMeta, 601).disabled_reason == "duplicate_idea"
