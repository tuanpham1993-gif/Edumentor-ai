"""Test B5 — script đo độ chính xác chấm tự luận (module 09 · Tuấn · 14/11/2026). Không cần DB, không gọi Gemini.

Chạy:  python -m pytest tests/test_eval_grading.py -v      (trong thư mục backend)
"""

import pytest

from scripts import eval_grading as ev
from scripts import gold_sheets as gs

SPLIT = gs.load_split()


def p(answer_id, item_no, human, ai, max_points=5.0, latency=10.0, failed=False):
    return {"answer_id": answer_id, "item_no": item_no, "question_code": "ITER-TL-01", "max_points": max_points,
            "human": human, "ai": ai, "failed": failed, "latency_ms": latency}  # fmt: skip


def model_answers(which="dev"):
    """Đáp án mẫu của các câu trong split làm bài → bộ chấm từ khóa phải ra full mọi ý."""
    codes = SPLIT[which]
    return [
        {"answer_id": f"T{i:03d}", "question_code": c, "split": which, "source": "team",
         "answer_text": SPLIT["questions"][c]["explanation"].removeprefix("Model answer:").strip()}
        for i, c in enumerate(codes, start=1)
    ]  # fmt: skip


def gold_for(answers, label="full"):
    return [
        {"answer_id": a["answer_id"], "question_code": a["question_code"], "split": a["split"], "source": a["source"],
         "item_no": str(no), "max_points": str(item["max_points"]), "label_a": label, "label_b": label, "label": label,
         "points": ""}
        for a in answers
        for no, item in enumerate(SPLIT["questions"][a["question_code"]]["rubric"], start=1)
    ]  # fmt: skip


def test_label_prf_matches_demo2_formula():
    pairs = [p("R1", 1, "full", "full"), p("R1", 2, "full", "partial"), p("R2", 1, "none", "full"),
             p("R2", 2, "partial", "partial")]  # fmt: skip
    prf = ev.label_prf(pairs)
    assert (prf["full"]["tp"], prf["full"]["fp"], prf["full"]["fn"]) == (1, 1, 1)
    assert prf["full"]["precision"] == 0.5 and prf["full"]["recall"] == 0.5 and prf["full"]["f1"] == 0.5
    assert prf["partial"]["precision"] == 0.5 and prf["partial"]["recall"] == 1.0
    assert prf["none"] == {"tp": 0, "fp": 0, "fn": 1, "precision": 0.0, "recall": 0.0, "f1": 0.0}


def test_metrics_on_known_totals():
    # R1: người 10, AI 5 (lệch 5) · R2: người 0, AI 10 (bài sai bị chấm cao) · R3: khớp 5 = 5
    pairs = [p("R1", 1, "full", "full"), p("R1", 2, "full", "none"),
             p("R2", 1, "none", "full"), p("R2", 2, "none", "full"),
             p("R3", 1, "full", "full"), p("R3", 2, "none", "none")]  # fmt: skip
    m = ev.metrics(pairs)
    assert m["answers"] == 3 and m["items"] == 6
    assert m["mae"] == pytest.approx(5.0) and m["rmse"] == pytest.approx((125 / 3) ** 0.5)
    assert m["item_agreement"] == pytest.approx(3 / 6) and m["within_1"] == pytest.approx(1 / 3)
    assert m["severe_overgrade"] == 1 and m["mean_bias"] == pytest.approx(5 / 3)
    assert m["confusion"]["none"]["full"] == 2


def test_partial_counts_half_points():
    t = ev.totals([p("R1", 1, "partial", "full", max_points=4), p("R1", 2, "full", "partial", max_points=6)])
    assert t == {"R1": (2 + 6, 4 + 3)}


def test_failed_ai_item_counts_as_none_and_is_reported():
    gold = gold_for(model_answers()[:1])
    run_rows = [
        {
            "answer_id": g["answer_id"],
            "item_no": g["item_no"],
            "result": "",
            "latency_ms": "5",
            "max_points": g["max_points"],
        }
        for g in gold
    ]
    pairs = ev.pair(gold, run_rows)
    assert all(x["ai"] == "none" and x["failed"] for x in pairs)
    assert ev.metrics(pairs)["failed_items"] == len(gold)


def test_pair_requires_adjudicated_gold():
    gold = gold_for(model_answers()[:1])
    gold[0]["label"] = ""
    run_rows = [
        {
            "answer_id": g["answer_id"],
            "item_no": g["item_no"],
            "result": "full",
            "latency_ms": "1",
            "max_points": g["max_points"],
        }
        for g in gold
    ]
    with pytest.raises(gs.GoldError, match="chưa có nhãn cuối"):
        ev.pair(gold, run_rows)


def test_run_keyword_on_model_answers_is_perfect_end_to_end():
    answers = model_answers("dev")
    rows = ev.run(answers, SPLIT, "keyword", run_id="t", which="dev")
    assert {r["result"] for r in rows} == {"full"} and not any(r["error"] for r in rows)
    assert set(rows[0]) == set(ev.RUN_FIELDS)
    m = ev.metrics(ev.pair(gold_for(answers), rows))
    assert m["mae"] == 0 and m["item_agreement"] == 1.0 and m["qwk"] == 1.0


def test_run_respects_split_filter():
    answers = model_answers("dev") + model_answers("test")
    rows = ev.run(answers, SPLIT, "keyword", run_id="t", which="dev")
    assert {r["split"] for r in rows} == {"dev"}


def test_run_records_errors_without_stopping(monkeypatch):
    def boom(question, text):
        raise RuntimeError("Gemini timeout")

    monkeypatch.setitem(ev.METHODS, "boom", (boom, "m", "v1"))
    rows = ev.run(model_answers()[:2], SPLIT, "boom", run_id="t")
    assert rows and all(r["result"] == "" and "Gemini timeout" in r["error"] for r in rows)


def test_paired_bootstrap_detects_clear_improvement_and_not_noise():
    ids = [f"R{i}" for i in range(30)]
    a = [p(i, 1, "full", "none") for i in ids] + [p(i, 2, "none", "none") for i in ids]  # A sai mọi ý 1
    b = [p(i, 1, "full", "full") for i in ids] + [p(i, 2, "none", "none") for i in ids]  # B đúng hết
    result = ev.paired_bootstrap(a, b, n=200)
    assert result["mae_diff"]["diff"] == pytest.approx(-5.0) and result["mae_diff"]["significant"]
    assert result["item_agreement_diff"]["ci_low"] > 0
    same = ev.paired_bootstrap(a, a, n=200)
    assert not same["mae_diff"]["significant"]


def test_stability_between_two_runs():
    r1 = [{"answer_id": "R1", "item_no": "1", "result": "full"}, {"answer_id": "R1", "item_no": "2", "result": "none"}]
    r2 = [{"answer_id": "R1", "item_no": "1", "result": "full"}, {"answer_id": "R1", "item_no": "2", "result": "full"}]
    assert ev.stability(r1, r2) == 0.5


def test_report_text_marks_targets():
    m = ev.metrics([p("R1", 1, "full", "full"), p("R1", 2, "none", "none")])
    text = ev.format_report(m, "demo")
    assert "mae" in text and "✓" in text and "ma trận nhầm" in text


# ─────────────── review B5 (14/11) ───────────────


def test_rounding_is_half_up_not_bankers():
    assert [gs.round_score(x) for x in (2.5, 3.5, 7.5, 7.4, 0.5)] == [3, 4, 8, 7, 1]  # round() cho 2, 4, 8, 7, 0


def test_run_missing_an_item_of_an_answer_is_an_error():
    answers = model_answers()[:1]
    rows = ev.run(answers, SPLIT, "keyword", run_id="t")
    with pytest.raises(gs.GoldError, match="lần chạy thiếu"):
        ev.pair(gold_for(answers), rows[1:])


def test_rubric_changed_between_gold_and_run_is_an_error():
    answers = model_answers()[:1]
    rows = ev.run(answers, SPLIT, "keyword", run_id="t")
    rows[0] = {**rows[0], "max_points": float(rows[0]["max_points"]) + 1}
    with pytest.raises(gs.GoldError, match="max_points"):
        ev.pair(gold_for(answers), rows)


def test_missing_answers_only_counts_splits_that_were_run():
    dev, test = model_answers("dev"), model_answers("test")
    for i, a in enumerate(test):
        a["answer_id"] = f"X{i}"
    gold = gold_for(dev + test)
    rows = ev.run(dev[1:], SPLIT, "keyword", run_id="t")  # bỏ sót bài dev đầu tiên; test không chạy
    assert ev.missing_answers(gold, rows) == [dev[0]["answer_id"]]


def test_stability_matches_csv_string_and_int_item_numbers():
    a = [{"answer_id": "R1", "item_no": 1, "result": "full"}]
    b = [{"answer_id": "R1", "item_no": "1", "result": "full"}]
    assert ev.stability(a, b) == 1.0
