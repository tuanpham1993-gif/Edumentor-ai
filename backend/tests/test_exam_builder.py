"""Test khung đề ôn tập services/exam_builder.py (module 09 · Tuấn · GĐ2, 09/11/2026).

Chạy:  python -m pytest tests/test_exam_builder.py -v      (trong thư mục backend)
"""

import random
from collections import Counter

import pytest

from app.services.exam_builder import (
    MAX_POINTS,
    STRUCTURE,
    NotEnoughQuestionsError,
    order_exam,
    plan_exam,
)

# Giống ngân hàng khóa 312: 5 kỹ năng × (3 NB + 3 TH); TL 6 dễ + 4 nâng cao
SKILLS = [167, 170, 400, 769, 770]
AVAILABLE_312 = {
    **{(s, "recognize"): 3 for s in SKILLS},
    **{(s, "understand"): 3 for s in SKILLS},
    (769, "easy"): 1, (770, "easy"): 1, (400, "easy"): 2, (167, "easy"): 1, (170, "easy"): 1,
    (167, "advanced"): 1, (400, "advanced"): 1, (770, "advanced"): 1, (769, "advanced"): 1,
}


def totals(plan):
    count = Counter()
    for levels in plan.values():
        count.update(levels)
    return count


@pytest.mark.parametrize("seed", range(100))
def test_plan_always_matches_structure(seed):
    plan = plan_exam(SKILLS, AVAILABLE_312, random.Random(seed))

    assert totals(plan) == STRUCTURE  # 6 NB + 6 TH + 2 dễ + 1 nâng cao
    for s in SKILLS:  # mỗi kỹ năng ≥ 1 câu TN
        assert plan[s].get("recognize", 0) + plan[s].get("understand", 0) >= 1
    for (s, level), n in AVAILABLE_312.items():  # không vượt số câu đang có
        assert plan.get(s, {}).get(level, 0) <= n
    essay_skills = [s for s, lv in plan.items() for level in lv if level in ("easy", "advanced")]
    assert len(set(essay_skills)) == 3  # 3 câu TL thuộc 3 kỹ năng khác nhau


def test_plan_is_random_but_repeatable():
    plans = {str(sorted(plan_exam(SKILLS, AVAILABLE_312, random.Random(s)).items())) for s in range(20)}
    assert len(plans) > 1  # đề khác nhau giữa các lần
    assert plan_exam(SKILLS, AVAILABLE_312, random.Random(7)) == plan_exam(
        SKILLS, AVAILABLE_312, random.Random(7)
    )


@pytest.mark.parametrize("seed", range(100))
def test_next_plan_prefers_unused_questions(seed):
    """Lượt sau: phần tự luận không phải lặp (ngân hàng 312 đủ câu mới) — A1 tránh câu lượt trước."""
    first = plan_exam(SKILLS, AVAILABLE_312, random.Random(seed))
    fresh = {k: v - first.get(k[0], {}).get(k[1], 0) for k, v in AVAILABLE_312.items()}

    second = plan_exam(SKILLS, AVAILABLE_312, random.Random(seed + 1000), fresh=fresh)

    assert totals(second) == STRUCTURE
    for s, levels in second.items():
        for level in ("easy", "advanced"):
            assert levels.get(level, 0) <= max(fresh[(s, level)], 0) if (s, level) in fresh else True


def test_more_than_12_skills_rotates_to_skills_not_asked_last_time():
    skills = list(range(1, 16))  # 15 kỹ năng > 12 câu TN
    available = {**{(s, "recognize"): 1 for s in skills}, **{(s, "understand"): 1 for s in skills}}
    available.update({(1, "easy"): 2, (2, "advanced"): 1})
    previous = set(range(1, 13))  # lượt trước đã hỏi kỹ năng 1..12

    plan = plan_exam(skills, available, random.Random(3), previous_skill_ids=previous)

    mcq_skills = {s for s, lv in plan.items() if lv.get("recognize") or lv.get("understand")}
    assert len(mcq_skills) == 12
    assert {13, 14, 15} <= mcq_skills  # kỹ năng lượt trước chưa hỏi được ưu tiên


@pytest.mark.parametrize("missing", [(167, "advanced"), "all_advanced", "few_recognize"])
def test_not_enough_questions(missing):
    available = dict(AVAILABLE_312)
    if missing == "all_advanced":
        available = {k: v for k, v in available.items() if k[1] != "advanced"}
    elif missing == "few_recognize":
        available = {k: (1 if k[1] == "recognize" else v) for k, v in available.items()}
    else:
        available = {k: v for k, v in available.items() if k[1] == "recognize"}

    with pytest.raises(NotEnoughQuestionsError):
        plan_exam(SKILLS, available, random.Random(0))


def test_one_skill_course_still_works():
    available = {(1, "recognize"): 6, (1, "understand"): 6, (1, "easy"): 2, (1, "advanced"): 1}

    plan = plan_exam([1], available, random.Random(0))

    assert plan == {1: STRUCTURE}


# ─────────────── order_exam ───────────────


def fake_questions():
    qs = []
    for level, n in STRUCTURE.items():
        qtype = "mcq" if level in ("recognize", "understand") else "essay"
        qs += [{"question_id": f"{level}{i}", "type": qtype, "level": level} for i in range(n)]
    return qs


def test_order_exam_layout():
    ordered = order_exam(fake_questions(), random.Random(1))

    assert [q["position"] for q in ordered] == list(range(1, 16))
    assert [q["type"] for q in ordered] == ["mcq"] * 12 + ["essay"] * 3
    assert [q["level"] for q in ordered[12:]] == ["easy", "easy", "advanced"]
    assert sum(q["max_points"] for q in ordered) == 10  # thang 10
    assert all(q["max_points"] == MAX_POINTS[q["level"]] for q in ordered)
    for q in ordered[:12]:
        assert sorted(q["option_order"]) == [0, 1, 2, 3]  # hoán vị 4 lựa chọn
    assert all("option_order" not in q for q in ordered[12:])


def test_order_exam_shuffles_questions_and_options():
    a = order_exam(fake_questions(), random.Random(1))
    b = order_exam(fake_questions(), random.Random(2))

    assert [q["question_id"] for q in a[:12]] != [q["question_id"] for q in b[:12]]
    assert any(q["option_order"] != [0, 1, 2, 3] for q in a[:12])
