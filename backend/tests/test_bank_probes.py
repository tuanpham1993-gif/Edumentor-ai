"""Ngân hàng đề soạn tay (scripts/bank/courses/course_<id>) — kiểm hồi quy tự động (27/11/2026, Tuấn duyệt).

1. File đề đang dùng (data/review/course_<id>_en.json) khớp với nguồn → không ai sửa tay JSON mà quên nguồn.
2. Mọi bài thử PROBES (trừ nhãn "c" = giới hạn đã biết) đạt điều kiện → sửa bộ chấm từ khóa (text_pipeline,
   keyword_grader_en) mà làm hỏng ca đã biết ("without", đảo QoS, "0.1 °C", gain 41…) thì test trượt ngay.
3. Mọi câu mô tả ý theo mẫu "(any one of: …)" / "(both needed: …)".
Chỉ dùng bộ chấm từ khóa — không gọi Gemini, không chạm DB.
"""

import importlib
import json
import pkgutil

import pytest

import scripts.bank.courses as courses_pkg
from app.ai.review.question_gate import keyword_score
from scripts.bank.build import build
from scripts.bank.check import template_problems
from scripts.bank.common import bank_path

COURSES = {
    int(m.name.removeprefix("course_")): importlib.import_module(f"scripts.bank.courses.{m.name}")
    for m in pkgutil.iter_modules(courses_pkg.__path__)
    if m.name.startswith("course_")
}


def _essays(course) -> dict[str, dict]:
    return {q["code"]: q for q in build(course)["questions"] if q["type"] == "essay"}


PROBE_CASES = [
    pytest.param(course_id, code, label, text, cond, id=f"{course_id}-{code}-{label[:30]}")
    for course_id, course in COURSES.items()
    for code, cases in course.PROBES.items()
    for label, text, cond in cases
    if cond != "c"
]


def test_courses_found():
    assert 494 in COURSES


@pytest.mark.parametrize("course_id", sorted(COURSES))
def test_bank_file_matches_source(course_id):
    """Sửa đề phải sửa ở nguồn rồi chạy `python -m scripts.bank.build <id>`, không sửa tay file JSON."""
    on_disk = json.loads(bank_path(course_id).read_text(encoding="utf-8"))
    assert on_disk == build(COURSES[course_id])


@pytest.mark.parametrize(("course_id", "code", "label", "text", "cond"), PROBE_CASES)
def test_probe(course_id, code, label, text, cond):
    q = _essays(COURSES[course_id])[code]
    score = keyword_score(q["rubric"], text, q["content"])
    op, limit = cond[:2], float(cond[2:])
    assert (score >= limit) if op == ">=" else (score <= limit), f"{code} [{label}]: {score}/10, cần {cond}"


@pytest.mark.parametrize("course_id", sorted(COURSES))
def test_rubric_text_templates(course_id):
    problems = [
        p
        for code, q in _essays(COURSES[course_id]).items()
        for i, item in enumerate(q["rubric"], start=1)
        for p in template_problems(code, i, item["text"])
    ]
    assert problems == []


@pytest.mark.parametrize("course_id", sorted(COURSES))
def test_every_essay_has_probes(course_id):
    course = COURSES[course_id]
    assert sorted(_essays(course)) == sorted(course.PROBES)
