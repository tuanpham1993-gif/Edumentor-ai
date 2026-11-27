"""Load the AI learning-path reference data into Qdrant (not Postgres).

    edumentor_skills    kind="alias"       <- datajson/skill_alias.json
    edumentor_job_roles kind="role"        <- datajson/job_roles.json + datajson/role_candidate_skills.json
    edumentor_job_roles kind="role_alias"  <- datajson/job_roles.json (aliases)

Same idea as seed_data_code.py: each part is loaded only when it is empty in Qdrant
(no alias points yet / no role points yet). Later changes go through the admin CRUD
(app/services/ai_reference_service.py), which validates against Postgres `skills`.

Safety checks (a part is skipped with a warning instead of indexing wrong links):
- Every skill_id in a file must exist in Postgres `skills` AND have the same name as in the file.
  seed_data_code.py inserts skills without skill_id, so IDs only match the files when
  skill_table.json was seeded into an empty table in file order.
- A skill alias may not equal any skill name and may be used by one skill only;
  a role alias may not equal another role's name or alias.
Also reports (does not change) a `skill_relation` table whose rows differ from the file.

Called from app/core/database.py:index_skills_to_qdrant() after the skill points exist.
"""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import SkillRelation, Skills

DATAJSON = Path(__file__).resolve().parents[4] / "datajson"


def _load(name: str):
    with open(DATAJSON / name, "r", encoding="utf-8") as file:
        return json.load(file)


def _norm(text: str) -> str:
    return " ".join(text.lower().split())


def _skill_name_mismatches(db: Session, expected: dict[int, str]) -> list[str]:
    """Compare {skill_id: name} from a file with the skills table."""
    in_db = dict(db.execute(select(Skills.skill_id, Skills.skill).where(Skills.skill_id.in_(expected))).all())
    problems = []
    for sid, name in expected.items():
        if sid not in in_db:
            problems.append(f"skill_id {sid} ({name!r}) not in skills table")
        elif in_db[sid].strip() != name.strip():
            problems.append(f"skill_id {sid}: file {name!r} != database {in_db[sid]!r}")
    return problems


def _warn(part: str, problems: list[str]) -> None:
    print(f"[WARNING] Qdrant seed {part} skipped: {len(problems)} problem(s), e.g.:")
    for p in problems[:5]:
        print(f"    - {p}")


def build_skill_aliases(db: Session) -> tuple[list[dict], list[str]]:
    records = _load("skill_alias.json")
    problems = _skill_name_mismatches(db, {r["skill_id"]: r["skill"] for r in records})
    skill_names = {_norm(n) for n in db.execute(select(Skills.skill)).scalars()}
    used: dict[str, int] = {}
    items = []
    for r in records:
        for alias in r["aliases"]:
            key = _norm(alias)
            if key in skill_names:
                problems.append(f"alias {alias!r} equals an existing skill name")
            elif key in used and used[key] != r["skill_id"]:
                problems.append(f"alias {alias!r} used by skills {used[key]} and {r['skill_id']}")
            elif key not in used:
                used[key] = r["skill_id"]
                items.append({"skill_id": r["skill_id"], "skill": r["skill"].strip(), "alias": alias})
    return items, problems


def build_roles(db: Session) -> tuple[list[dict], list[dict], list[str]]:
    roles = _load("job_roles.json")["roles"]
    candidates = {r["role_id"]: r["candidate_skills"] for r in _load("role_candidate_skills.json")}
    role_ids = {r["id"] for r in roles}
    problems = [f"role_candidate_skills: role_id {rid} not in job_roles.json" for rid in candidates if rid not in role_ids]
    problems += _skill_name_mismatches(db, {c["skill_id"]: c["skill"] for cs in candidates.values() for c in cs})

    owner: dict[str, int] = {_norm(r["name"]): r["id"] for r in roles}
    role_items, alias_items = [], []
    for r in roles:
        role_items.append({"role_id": r["id"], "role_name": r["name"], "description": r.get("description"),
                           "is_active": True,
                           "candidate_skill_ids": [c["skill_id"] for c in candidates.get(r["id"], [])]})
        for alias in r.get("aliases", []):
            key = _norm(alias)
            if key in owner and owner[key] != r["id"]:
                problems.append(f"role alias {alias!r} of role {r['id']} already used by role {owner[key]}")
                continue
            if key in owner:  # equals own name or repeated alias
                continue
            owner[key] = r["id"]
            alias_items.append({"role_id": r["id"], "role_name": r["name"], "alias": alias})
    return role_items, alias_items, problems


def check_skill_relation(db: Session) -> None:
    """Report only. The table itself is seeded by seed_data_code.py."""
    relations = _load("skill_relation.json")
    in_db = db.execute(select(func.count()).select_from(SkillRelation)).scalar_one()
    if in_db and in_db != len(relations):
        print(f"[WARNING] skill_relation has {in_db} rows but datajson/skill_relation.json has {len(relations)}. "
              "It is only seeded when empty: delete its rows and restart to load the new graph.")
    names: dict[int, str] = {}
    for r in relations:
        names[r["from_skill_id"]] = r["from_skill_name"]
        names[r["to_skill_id"]] = r["to_skill_name"]
    problems = _skill_name_mismatches(db, names)
    if problems:
        _warn("skill_relation check (IDs in the file do not match the skills table)", problems)


def seed_ai_data(db_session, skill_q=None, role_q=None, embed=None) -> None:
    """Index aliases, roles, role aliases and candidates into Qdrant when they are missing."""
    from app.services.qdrant_service import qdrant_role_service, qdrant_skill_service

    skill_q = skill_q or qdrant_skill_service
    role_q = role_q or qdrant_role_service
    if embed is None:
        from app.core.embedding_model import generate_embedding_skills_name as embed

    db: Session = db_session
    try:
        if db.execute(select(func.count()).select_from(Skills)).scalar_one() == 0:
            print("[WARNING] skills table is empty; AI reference data not indexed")
            return

        skill_q.create_collection()
        if skill_q.count(kind="alias") == 0:
            items, problems = build_skill_aliases(db)
            if problems:
                _warn("skill aliases", problems)
            elif items:
                skill_q.upsert_aliases(items, embed([a["alias"] for a in items]))
                print(f"Indexed {len(items)} skill aliases into Qdrant")

        role_q.create_collection()
        if role_q.count(kind="role") == 0:
            roles, aliases, problems = build_roles(db)
            if problems:
                _warn("job roles", problems)
            else:
                role_q.upsert_roles(roles, embed([r["role_name"] for r in roles]))
                if aliases:
                    role_q.upsert_aliases(aliases, embed([a["alias"] for a in aliases]))
                print(f"Indexed {len(roles)} job roles and {len(aliases)} role aliases into Qdrant")

        check_skill_relation(db)
    finally:
        db.close()
