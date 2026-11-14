"""Test B4 — gom bài, tạo phiếu chấm, gộp gold.csv (module 09 · Tuấn · 14/11/2026). Không cần DB.

Chạy:  python -m pytest tests/test_gold_sheets.py -v      (trong thư mục backend)
"""

import pytest

from scripts import gold_sheets as gs

SPLIT = gs.load_split()


def answer(answer_id, code="ITER-TL-01", source="real", text="break exits the loop."):
    return {
        "answer_id": answer_id,
        "question_code": code,
        "split": SPLIT["split_of"][code],
        "source": source,
        "answer_text": text,
    }


def labelled(sheet, labels):
    """Điền nhãn vào phiếu theo {(answer_id, item_no): nhãn}."""
    return [{**r, "label": labels[(r["answer_id"], int(r["item_no"]))]} for r in sheet]


def test_split_is_by_question_and_bank_matches():
    assert not set(SPLIT["dev"]) & set(SPLIT["test"])
    assert sorted(SPLIT["forms"]["A"] + SPLIT["forms"]["B"]) == sorted(SPLIT["dev"] + SPLIT["test"])
    skills = lambda codes: sorted(c.split("-")[0] for c in codes)
    assert skills(SPLIT["dev"]) == skills(SPLIT["test"]) == ["COND", "CS", "ITER", "PY", "VAR"]
    assert all(q["type"] == "essay" for q in SPLIT["questions"].values())


def test_collect_reads_form_export_and_skips_no_consent_and_blank():
    rows = [
        {
            "Timestamp": "1",
            "Consent to use my answers": "Yes, I agree",
            "[ITER-TL-01] Explain break and continue": "break stops the loop",
            "[PY-TL-03] Explain print": "",
        },
        {"Timestamp": "2", "Consent to use my answers": "No", "[ITER-TL-01] Explain break and continue": "x"},
    ]
    out = gs.collect([rows], SPLIT)
    assert out == [
        {
            "answer_id": "R0001",
            "question_code": "ITER-TL-01",
            "split": "dev",
            "source": "real",
            "answer_text": "break stops the loop",
        }
    ]


def test_ai_answers_are_not_allowed_in_test():
    errors = gs.answer_errors([answer("A001", code="PY-TL-02", source="ai")], SPLIT)
    assert any("không được nằm trong test" in e for e in errors)
    assert gs.answer_errors([answer("A002", source="ai")], SPLIT) == []  # dev thì được


def test_wrong_split_and_duplicate_id_are_errors():
    bad = {**answer("R1"), "split": "test"}
    errors = gs.answer_errors([bad, answer("R1")], SPLIT)
    assert any("split phải là 'dev'" in e for e in errors) and any("trùng" in e for e in errors)


def test_sheets_have_one_row_per_item_without_scores_and_differ_in_order():
    answers = [answer(f"R{i}") for i in range(10)] + [answer("R99", code="PY-TL-02", text="A list is mutable.")]
    a = gs.make_sheet(answers, SPLIT, "hoa")
    b = gs.make_sheet(answers, SPLIT, "tam")
    assert len(a) == 10 * 2 + 5  # ITER-TL-01: 2 ý; PY-TL-02: 5 ý
    assert set(a[0]) == set(gs.SHEET_FIELDS) and all(r["label"] == "" for r in a)
    assert [r["answer_id"] for r in a] != [r["answer_id"] for r in b]
    assert gs.make_sheet(answers, SPLIT, "hoa") == a  # tái lập được


def test_merge_agreement_disagreement_and_adjudication():
    answers = [answer("R1"), answer("R2")]
    sheet = gs.make_sheet(answers, SPLIT, "hoa")
    a = labelled(sheet, {("R1", 1): "full", ("R1", 2): "none", ("R2", 1): "partial", ("R2", 2): "full"})
    b = labelled(sheet, {("R1", 1): "full", ("R1", 2): "partial", ("R2", 1): "partial", ("R2", 2): "full"})

    result = gs.merge(answers, SPLIT, a, b)
    assert result["stats"]["item_agreement"] == 0.75 and result["stats"]["unresolved"] == 1
    assert [(d["answer_id"], d["item_no"]) for d in result["disagreements"]] == [("R1", 2)]
    r1 = [g for g in result["gold"] if g["answer_id"] == "R1"]
    assert r1[0]["label"] == "full" and r1[0]["points"] == 5.0 and r1[1]["label"] == ""

    done = gs.merge(answers, SPLIT, a, b, {("R1", 2): "partial"})
    assert done["stats"]["unresolved"] == 0
    assert [g["points"] for g in done["gold"] if g["answer_id"] == "R1"] == [5.0, 2.5]


def test_merge_rejects_missing_or_invalid_labels():
    answers = [answer("R1")]
    sheet = gs.make_sheet(answers, SPLIT, "hoa")
    good = labelled(sheet, {("R1", 1): "full", ("R1", 2): "none"})
    with pytest.raises(gs.GoldError) as e:
        gs.merge(answers, SPLIT, good, labelled(sheet, {("R1", 1): "ok", ("R1", 2): "none"}))
    assert "full / partial / none" in e.value.errors[0]
    with pytest.raises(gs.GoldError) as e:
        gs.merge(answers, SPLIT, good, good[:1])
    assert "thiếu 1 ý" in e.value.errors[0]


def test_perfect_agreement_kappa_is_one():
    answers = [answer("R1"), answer("R2", text="continue skips.")]
    sheet = gs.make_sheet(answers, SPLIT, "hoa")
    a = labelled(sheet, {("R1", 1): "full", ("R1", 2): "none", ("R2", 1): "none", ("R2", 2): "full"})
    stats = gs.merge(answers, SPLIT, a, a)["stats"]
    assert stats["item_agreement"] == 1.0 and stats["item_kappa"] == 1.0


def test_csv_roundtrip_keeps_vietnamese_and_excel_bom(tmp_path):
    path = tmp_path / "answers.csv"
    gs.write_csv(path, gs.ANSWER_FIELDS, [answer("R1", text="vòng lặp — break")])
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
    assert gs.read_csv(path)[0]["answer_text"] == "vòng lặp — break"
