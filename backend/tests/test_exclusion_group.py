"""7.5b — nhóm loại trừ (QT7): hai câu cùng exclusion_group không vào cùng một đề (27/11/2026, Tuấn duyệt).

Bộ ráp đề né MỀM (thiếu câu khác nhóm thì vẫn ra đủ đề), bốc tự luận trước trắc nghiệm; seed đọc trường từ file đề
và sửa tại chỗ (không sinh phiên bản 2); scripts/bank/build ghi trường khi khóa khai EXCLUSION.
"""

import copy
import random
import types

import pytest

from app.ai.review.mock_ai import pick_from_bank
from app.core.seed_data import seed_review as script
from app.models import ReviewQuestion
from app.models.review_question_meta import ReviewQuestionMeta
from scripts.bank.build import build
from tests.test_seed_review import bank, course_312  # noqa: F401 — fixture

NEED = {"recognize": 2, "understand": 1, "easy": 1, "advanced": 1}


def cand(qid, level, group=None):
    kind = "mcq" if level in ("recognize", "understand") else "essay"
    return {"question_id": qid, "level": level, "type": kind, "exclusion_group": group}


def test_same_group_never_in_one_exam():
    pool = [
        cand(1, "recognize", "g"), cand(2, "recognize"), cand(3, "recognize"), cand(4, "recognize"),
        cand(5, "understand", "h"), cand(6, "understand"),
        cand(7, "easy", "h"), cand(8, "easy"),
        cand(9, "advanced", "g"), cand(10, "advanced"),
    ]  # fmt: skip
    for seed in range(200):
        picked = pick_from_bank(pool, NEED, random.Random(seed))
        groups = [q["exclusion_group"] for q in picked if q["exclusion_group"]]
        assert len(groups) == len(set(groups)), (seed, [q["question_id"] for q in picked])
        assert [q["level"] for q in picked] == ["recognize", "recognize", "understand", "easy", "advanced"]


def test_essay_is_picked_first_so_the_mcq_gives_way():
    """Một câu tự luận nâng cao duy nhất cùng nhóm với một câu trắc nghiệm → luôn giữ tự luận, trắc nghiệm né."""
    pool = [cand(1, "recognize", "g"), cand(2, "recognize"), cand(3, "recognize"), cand(9, "advanced", "g")]
    for seed in range(100):
        ids = {q["question_id"] for q in pick_from_bank(pool, {"recognize": 2, "advanced": 1}, random.Random(seed))}
        assert ids == {2, 3, 9}


def test_soft_constraint_still_fills_the_exam():
    """Không đủ câu khác nhóm → vẫn ra đủ số câu (không chặn người học)."""
    pool = [cand(1, "recognize", "g"), cand(2, "recognize", "g"), cand(9, "advanced", "g")]
    picked = pick_from_bank(pool, {"recognize": 2, "advanced": 1}, random.Random(0))
    assert sorted(q["question_id"] for q in picked) == [1, 2, 9]


def test_questions_without_group_behave_as_before():
    pool = [cand(i, "recognize") for i in range(1, 6)]
    for seed in range(20):
        assert len(pick_from_bank(pool, {"recognize": 3}, random.Random(seed))) == 3


# ─────────────── seed ───────────────


def _meta(db, code):
    q = db.query(ReviewQuestion).filter_by(code=code).one()
    return q, db.get(ReviewQuestionMeta, q.question_id)


def test_seed_reads_group_and_updates_in_place(db_session, course_312, bank, monkeypatch):  # noqa: F811
    script.seed_bank(db_session, bank)
    code = bank["questions"][0]["code"]
    grouped = copy.deepcopy(bank)
    grouped["questions"][0]["exclusion_group"] = "g1"
    # câu đã có bài làm: sửa nhóm vẫn là sửa nhỏ → tại chỗ, không sinh phiên bản 2
    monkeypatch.setattr(script.review_bank_service.repo, "used_count", lambda db, qid: 1)
    counts = script.seed_bank(db_session, grouped, apply_changes=True)
    q, meta = _meta(db_session, code)
    assert counts["groups_updated"] == 1 and counts["questions_versioned"] == 0
    assert meta.exclusion_group == "g1" and meta.version == 1 and q.is_active
    assert db_session.query(ReviewQuestion).filter(ReviewQuestion.code.like(f"{code}%")).count() == 1

    grouped["questions"][0]["exclusion_group"] = None  # null trong file = bỏ nhóm
    script.seed_bank(db_session, grouped, apply_changes=True)
    assert _meta(db_session, code)[1].exclusion_group is None


def test_seed_without_apply_only_reports_group_change(db_session, course_312, bank):  # noqa: F811
    script.seed_bank(db_session, bank)
    grouped = copy.deepcopy(bank)
    grouped["questions"][0]["exclusion_group"] = "g1"
    counts = script.seed_bank(db_session, grouped)
    assert grouped["questions"][0]["code"] in counts["questions_differ"]
    assert _meta(db_session, grouped["questions"][0]["code"])[1].exclusion_group is None


def test_seed_new_question_gets_group(db_session, course_312, bank):  # noqa: F811
    bank["questions"][0]["exclusion_group"] = "g1"
    script.seed_bank(db_session, bank)
    assert _meta(db_session, bank["questions"][0]["code"])[1].exclusion_group == "g1"


def test_file_without_group_field_leaves_db_group_alone(db_session, course_312, bank):  # noqa: F811
    """File đề cũ (không khai trường) không xóa nhóm admin đã đặt trong DB."""
    script.seed_bank(db_session, bank)
    q, meta = _meta(db_session, bank["questions"][0]["code"])
    meta.exclusion_group = "admin"
    script.seed_bank(db_session, copy.deepcopy(bank), apply_changes=True)
    assert _meta(db_session, q.code)[1].exclusion_group == "admin"


@pytest.mark.parametrize("bad", ["", "x" * 51, 7])
def test_validate_rejects_bad_group(bank, bad):  # noqa: F811
    bank["questions"][0]["exclusion_group"] = bad
    assert any("exclusion_group" in e for e in script.validate_bank(bank))


# ─────────────── scripts/bank/build ───────────────


def _course(**extra):
    base = {
        "COURSE_ID": 1,
        "COURSE_TITLE": "T",
        "NOTE": "n",
        "SKILLS": {"S": 9},
        "CHUNKS": [("S", "t", "c")],
        "MCQ": {"S": [(1, "recognize", "Q?", ["a", "b", "c", "d"], "e")]},
        "ESSAY": {"S": []},
    }
    return types.SimpleNamespace(**base, **extra)


def test_build_without_exclusion_has_no_field():
    assert all("exclusion_group" not in q for q in build(_course())["questions"])


def test_build_writes_group_for_every_question():
    qs = build(_course(EXCLUSION={"S-TN-01": "g"}))["questions"]
    assert [q["exclusion_group"] for q in qs] == ["g"]


def test_build_rejects_unknown_code():
    with pytest.raises(ValueError, match="S-TN-99"):
        build(_course(EXCLUSION={"S-TN-99": "g"}))
