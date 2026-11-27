"""Compact spec format for writing G1 samples, and the builder that expands it.

A human writes only the judgement parts of a sample (query, form input, and what the
query itself says). The builder applies the deterministic Phase 2 rules:

- goal.original_query is copied from the query
- target_role.canonical_name / role_id are null
- form (learner_input) values win over query values for the same field
- form skills become `user_provided_structured`; a query mention of the same skill only
  fills the form's null proficiency/duration
- form and query list values are merged without duplicates
- status = needs_clarification exactly when clarifications exist
- unknown_fields is computed from the final output (fixed vocabulary and order)

Spec helpers:
    S(lang, persona, scenario, difficulty, q, f=None, role=None, tech=(), gt="career",
      lvl=None, title=None, ind=None, dom=(), certs=(), prev=(), exp=None,
      sk=(), px=(), st=None, dl=None, cl=())
    F(title=, lvl=, exp=, ind=, dom=(), sk=(), certs=(), st=, dl=)   # frontend form
    sk(name, prof=None, dur=None, ev="e")    # ev: "e" explicitly_reported, "i" inferred_from_context
    fs(name, prof=None, dur=None)            # a form skill
    px(description, related_skills)
    st = (value, "hours"|"minutes", "per_day"|"per_week")
    dl = ("rel", value, unit) | ("fix", "YYYY-MM-DD")
    cl(field, question, options_or_None)

lang: "en" | "vi".  persona: see PERSONAS.  These two are stored in the manifest,
not in the sample (G1Metadata allows only scenario_type and difficulty).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

PERSONAS = ("student", "intern_fresher", "junior", "middle", "senior", "lead_arch_mgr", "switcher", "unknown")
LANGS = ("en", "vi")
EVIDENCE = {"e": "explicitly_reported", "i": "inferred_from_context"}
UNKNOWN_ORDER = [
    "target_role", "career_level", "current_job_title", "industry", "technical_domains",
    "relevant_it_work_experience", "skill_profiles", "certifications", "available_study_time", "deadline",
]


@dataclass
class Form:
    title: Optional[str] = None
    lvl: Optional[str] = None
    exp: Optional[str] = None
    ind: Optional[str] = None
    dom: tuple = ()
    sk: tuple = ()
    certs: tuple = ()
    st: Optional[tuple] = None
    dl: Optional[tuple] = None

    def is_empty(self) -> bool:
        return not any([self.title, self.lvl, self.exp, self.ind, self.dom, self.sk, self.certs, self.st, self.dl])


@dataclass
class Spec:
    lang: str
    persona: str
    scenario: str
    difficulty: str
    q: str
    f: Form = field(default_factory=Form)
    role: Optional[str] = None
    tech: tuple = ()
    gt: str = "career"
    lvl: Optional[str] = None
    title: Optional[str] = None
    ind: Optional[str] = None
    dom: tuple = ()
    certs: tuple = ()
    prev: tuple = ()
    exp: Optional[str] = None
    sk: tuple = ()
    px: tuple = ()
    st: Optional[tuple] = None
    dl: Optional[tuple] = None
    cl: tuple = ()


def S(lang, persona, scenario, difficulty, q, f=None, **kw) -> Spec:
    assert lang in LANGS, lang
    assert persona in PERSONAS, persona
    return Spec(lang, persona, scenario, difficulty, q, f or Form(), **{k: tuple(v) if isinstance(v, list) else v for k, v in kw.items()})


def F(**kw) -> Form:
    return Form(**{k: tuple(v) if isinstance(v, list) else v for k, v in kw.items()})


def sk(name, prof=None, dur=None, ev="e"):
    return (name, prof, dur, ev)


def fs(name, prof=None, dur=None):
    return (name, prof, dur)


def px(description, related):
    return (description, tuple(related))


def cl(field_, question, options=None):
    return (field_, question, list(options) if options is not None else None)


def _time(st):
    return None if st is None else {"value": st[0], "unit": st[1], "period": st[2]}


def _deadline(dl):
    if dl is None:
        return None
    if dl[0] == "fix":
        return {"deadline_type": "fixed_date", "target_date": dl[1], "duration_value": None, "duration_unit": None}
    return {"deadline_type": "relative_duration", "target_date": None, "duration_value": dl[1], "duration_unit": dl[2]}


def _merge_list(form_items, query_items):
    out, seen = [], set()
    for x in list(form_items) + list(query_items):
        k = " ".join(x.lower().split())
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out


def build(spec: Spec, sample_id: str) -> tuple[dict, dict]:
    """Return (G1DatasetSample dict, manifest row)."""
    f = spec.f
    learner_input = {
        "current_job_title": f.title, "career_level": f.lvl, "relevant_it_work_experience": f.exp,
        "industry": f.ind, "technical_domains": list(f.dom),
        "skill_profiles": [{"skill_name": n, "proficiency_level": p, "experience_duration": d} for n, p, d in f.sk],
        "certifications": list(f.certs),
        "learning_constraints": {"available_study_time": _time(f.st), "deadline": _deadline(f.dl)},
    }

    # skills: form first (structured), then query-only skills
    skills, index = [], {}
    for n, p, d in f.sk:
        index[n.lower()] = len(skills)
        skills.append({"skill_name": n, "proficiency_level": p, "experience_duration": d,
                       "evidence_type": "user_provided_structured"})
    for n, p, d, ev in spec.sk:
        if n.lower() in index:
            rec = skills[index[n.lower()]]
            rec["proficiency_level"] = rec["proficiency_level"] or p
            rec["experience_duration"] = rec["experience_duration"] or d
        else:
            index[n.lower()] = len(skills)
            skills.append({"skill_name": n, "proficiency_level": p, "experience_duration": d,
                           "evidence_type": EVIDENCE[ev]})

    pick = lambda form_v, query_v: form_v if form_v is not None else query_v  # noqa: E731
    out = {
        "goal": {
            "original_query": spec.q,
            "target_role": {"raw_name": spec.role, "canonical_name": None, "role_id": None},
            "target_technologies": list(spec.tech),
            "goal_type": spec.gt,
        },
        "career_background": {
            "career_level": pick(f.lvl, spec.lvl),
            "current_job_title": pick(f.title, spec.title),
            "industry": pick(f.ind, spec.ind),
            "technical_domains": _merge_list(f.dom, spec.dom),
            "certifications": _merge_list(f.certs, spec.certs),
            "previous_job_roles": list(spec.prev),
            "relevant_it_work_experience": pick(f.exp, spec.exp),
        },
        "skill_profiles": skills,
        "status": "needs_clarification" if spec.cl else "ready",
        "practical_experience": [
            {"description": d, "related_skills": list(r), "evidence_type": "explicitly_reported"} for d, r in spec.px
        ],
        "learning_constraints": {"available_study_time": _time(pick(f.st, spec.st)),
                                 "deadline": _deadline(pick(f.dl, spec.dl))},
        "clarification_required": [{"field": a, "question": b, "options": c} for a, b, c in spec.cl],
    }
    cb, lc = out["career_background"], out["learning_constraints"]
    values = {
        "target_role": spec.role, "career_level": cb["career_level"], "current_job_title": cb["current_job_title"],
        "industry": cb["industry"], "technical_domains": cb["technical_domains"],
        "relevant_it_work_experience": cb["relevant_it_work_experience"], "skill_profiles": skills,
        "certifications": cb["certifications"], "available_study_time": lc["available_study_time"],
        "deadline": lc["deadline"],
    }
    out["unknown_fields"] = [k for k in UNKNOWN_ORDER if values[k] in (None, [])]

    # input-source pattern (for the manifest only)
    query_bg = any([spec.lvl, spec.title, spec.ind, spec.dom, spec.certs, spec.exp, spec.sk, spec.st, spec.dl])
    same = lambda a, b: (" ".join(a.lower().split()) == " ".join(b.lower().split())  # noqa: E731
                         if isinstance(a, str) and isinstance(b, str) else a == b)
    conflict = any(fv is not None and qv is not None and not same(fv, qv) for fv, qv in
                   [(f.lvl, spec.lvl), (f.title, spec.title), (f.ind, spec.ind), (f.exp, spec.exp),
                    (f.st, spec.st), (f.dl, spec.dl)])
    form_skill_names = {n.lower() for n, *_ in f.sk}
    conflict = conflict or any(n.lower() in form_skill_names and p is not None and
                               next(fp for fn, fp, _ in f.sk if fn.lower() == n.lower()) not in (None, p)
                               for n, p, *_ in spec.sk)
    if f.is_empty():
        pattern = "query_only"
    elif conflict:
        pattern = "conflict"
    elif not query_bg:
        pattern = "mostly_structured"
    else:
        pattern = "complementary"

    sample = {
        "sample_id": sample_id,
        "input": {"original_query": spec.q, "learner_input": learner_input},
        "expected_output": out,
        "metadata": {"scenario_type": spec.scenario, "difficulty": spec.difficulty},
    }
    # how many kinds of information the query itself carries (goal counts as one)
    query_facts = 1 + sum(bool(x) for x in [
        spec.lvl, spec.title, spec.ind, spec.dom, spec.certs, spec.prev, spec.exp,
        spec.sk, spec.px, spec.st, spec.dl, spec.tech])
    manifest = {"sample_id": sample_id, "lang": spec.lang, "persona": spec.persona, "input_pattern": pattern,
                "status": out["status"], "goal_type": spec.gt, "query_facts": query_facts}
    return sample, manifest
