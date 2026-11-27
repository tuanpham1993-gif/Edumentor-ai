"""Validate G1 dataset samples (Phase 2, section 2.9). Canonical copy of the validator.

Usage (from Edumentor-ai/backend):
    python -m app.utils.g1_dataset.validate <file.json | file.jsonl> [more files...]

Each sample must pass G1DatasetSample.model_validate plus the semantic
checks below. Exit code 1 if any sample fails.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from app.utils.learner_analyzer.schemas import G1DatasetSample

UNKNOWN_ORDER = [
    "target_role", "career_level", "current_job_title", "industry",
    "technical_domains", "relevant_it_work_experience", "skill_profiles",
    "certifications", "available_study_time", "deadline",
]
SCENARIO_TYPES = {
    "goal_only", "goal_with_role", "goal_with_career_level_and_experience",
    "goal_with_skills", "goal_with_projects", "goal_with_certifications",
    "goal_with_industry_or_domain", "goal_with_constraints",
    "mixed_information", "conflicting_or_ambiguous",
}
DIFFICULTIES = {"easy", "normal", "hard"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EXPERIENCE_RE = re.compile(
    r"^((less than|over|about|almost|more than) )?\d+(\.\d+)? (month|months|year|years)$"
)


def _fold(s: str) -> str:
    """Lowercase, remove accents and collapse spaces, for "appears in the query" checks."""
    import unicodedata
    s = s.lower().replace("đ", "d")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return " ".join(s.split())


def norm(s: str) -> str:
    return " ".join(s.lower().split())


def expected_unknown(out: dict) -> list[str]:
    cb, lc = out["career_background"], out["learning_constraints"]
    values = {
        "target_role": out["goal"]["target_role"]["raw_name"],
        "career_level": cb["career_level"],
        "current_job_title": cb["current_job_title"],
        "industry": cb["industry"],
        "technical_domains": cb["technical_domains"],
        "relevant_it_work_experience": cb["relevant_it_work_experience"],
        "skill_profiles": out["skill_profiles"],
        "certifications": cb["certifications"],
        "available_study_time": lc["available_study_time"],
        "deadline": lc["deadline"],
    }
    return [k for k in UNKNOWN_ORDER if values[k] in (None, [])]


def check_sample(raw: dict) -> list[str]:
    errors: list[str] = []
    try:
        G1DatasetSample.model_validate(raw)
    except Exception as exc:  # pydantic ValidationError
        return [f"schema: {exc}".replace("\n", " | ")[:600]]

    inp, out, meta = raw["input"], raw["expected_output"], raw["metadata"]
    li = inp.get("learner_input") or {}
    cb, goal = out["career_background"], out["goal"]

    # goal
    if goal["original_query"] != inp["original_query"]:
        errors.append("goal.original_query differs from input.original_query")
    tr = goal["target_role"]
    if tr["canonical_name"] is not None or tr["role_id"] is not None:
        errors.append("target_role.canonical_name/role_id must be null in model output")

    # deadline consistency
    dl = out["learning_constraints"]["deadline"]
    if dl:
        if dl["deadline_type"] == "fixed_date":
            if not (dl["target_date"] and DATE_RE.match(dl["target_date"])) or dl["duration_value"] is not None or dl["duration_unit"] is not None:
                errors.append("fixed_date deadline needs ISO target_date and null duration fields")
        else:
            if dl["target_date"] is not None or dl["duration_value"] is None or dl["duration_unit"] is None:
                errors.append("relative_duration deadline needs duration fields and null target_date")

    # status / clarification
    cr = out["clarification_required"]
    if (out["status"] == "ready") != (len(cr) == 0):
        errors.append("status must be 'ready' exactly when clarification_required is empty")
    if len(cr) > 3:
        errors.append("more than 3 clarification questions")
    for item in cr:
        if len(item["question"].split()) > 20:
            errors.append(f"clarification question over 20 words: {item['question']!r}")
        if item["options"] is not None and not (2 <= len(item["options"]) <= 5):
            errors.append("clarification options must be 2-5 or null")

    # unknown_fields
    exp = expected_unknown(out)
    if out["unknown_fields"] != exp:
        errors.append(f"unknown_fields {out['unknown_fields']} != expected {exp}")

    # experience format
    exp_str = cb["relevant_it_work_experience"]
    if exp_str is not None and not EXPERIENCE_RE.match(exp_str):
        errors.append(f"relevant_it_work_experience format: {exp_str!r}")
    for s in out["skill_profiles"]:
        if s["experience_duration"] is not None and not EXPERIENCE_RE.match(s["experience_duration"]):
            errors.append(f"experience_duration format: {s['experience_duration']!r}")
    for f in out["career_background"]["technical_domains"]:
        if not re.match(r"^[A-Z][A-Za-z0-9/+#.&-]*( [A-Za-z0-9/+#.&-]+)*$", f):
            errors.append(f"technical_domains must be English Title Case: {f!r}")

    # structured input must be carried over
    for field in ("current_job_title", "career_level", "relevant_it_work_experience", "industry"):
        if li.get(field) not in (None, "") and cb[field] != li[field]:
            errors.append(f"structured {field}={li[field]!r} not preserved (got {cb[field]!r})")
    for field in ("technical_domains", "certifications"):
        have = {norm(x) for x in cb[field]}
        for v in li.get(field) or []:
            if norm(v) not in have:
                errors.append(f"structured {field} value {v!r} missing in output")
    lc_in = li.get("learning_constraints") or {}
    for field in ("available_study_time", "deadline"):
        if lc_in.get(field) is not None and out["learning_constraints"][field] != lc_in[field]:
            errors.append(f"structured learning_constraints.{field} not preserved")

    # skills
    names = [norm(s["skill_name"]) for s in out["skill_profiles"]]
    dupes = [n for n, c in Counter(names).items() if c > 1]
    if dupes:
        errors.append(f"duplicate skill_profiles: {dupes}")
    by_name = {norm(s["skill_name"]): s for s in out["skill_profiles"]}
    for s in li.get("skill_profiles") or []:
        o = by_name.get(norm(s["skill_name"]))
        if o is None:
            errors.append(f"structured skill {s['skill_name']!r} missing")
            continue
        if o["evidence_type"] != "user_provided_structured":
            errors.append(f"structured skill {s['skill_name']!r} must be user_provided_structured")
        for f in ("proficiency_level", "experience_duration"):
            if s.get(f) is not None and o[f] != s[f]:
                errors.append(f"structured skill {s['skill_name']!r} {f} not preserved")
    for pe in out["practical_experience"]:
        for rs in pe["related_skills"]:
            if norm(rs) not in by_name:
                errors.append(f"related skill {rs!r} not in skill_profiles")

    # no invented values: wording must come from the query (or the form for structured skills)
    q = _fold(inp["original_query"])
    raw_role = goal["target_role"]["raw_name"]
    if raw_role and _fold(raw_role) not in q:
        errors.append(f"target_role.raw_name {raw_role!r} does not appear in the query")
    for tech in goal["target_technologies"]:
        if _fold(tech) not in q:
            errors.append(f"target technology {tech!r} does not appear in the query")
    form_skills = {_fold(s["skill_name"]) for s in li.get("skill_profiles") or []}
    for s in out["skill_profiles"]:
        if s["evidence_type"] == "explicitly_reported" and _fold(s["skill_name"]) not in q:
            errors.append(f"explicit skill {s['skill_name']!r} does not appear in the query")
        if s["evidence_type"] == "user_provided_structured" and _fold(s["skill_name"]) not in form_skills:
            errors.append(f"structured skill {s['skill_name']!r} is not in learner_input")

    # metadata
    if meta["scenario_type"] not in SCENARIO_TYPES:
        errors.append(f"unknown scenario_type {meta['scenario_type']!r}")
    if meta["difficulty"] not in DIFFICULTIES:
        errors.append(f"unknown difficulty {meta['difficulty']!r}")
    return errors


def load(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    data = json.loads(text)
    return data if isinstance(data, list) else [data]


def main(paths: list[str]) -> int:
    total = failed = 0
    seen_ids: Counter = Counter()
    seen_queries: Counter = Counter()
    for p in paths:
        for sample in load(Path(p)):
            total += 1
            sid = sample.get("sample_id", f"<no id #{total}>")
            seen_ids[sid] += 1
            seen_queries[norm(sample.get("input", {}).get("original_query", ""))] += 1
            errs = check_sample(sample)
            if errs:
                failed += 1
                print(f"FAIL {sid}")
                for e in errs:
                    print(f"   - {e}")
    for sid, c in seen_ids.items():
        if c > 1:
            failed += 1
            print(f"FAIL duplicate sample_id {sid} x{c}")
    for q, c in seen_queries.items():
        if c > 1:
            print(f"WARN identical query x{c}: {q[:80]}")
    print(f"\n{total} samples, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
