"""AI reference data in Qdrant (in-memory): seeding from datajson, CRUD validated against Postgres
`skills` (SQLite here), sync when a skill changes, the role matcher reading from Qdrant, and the
per-learning-path LearnerProfile snapshot built from a NormalizedG1Output."""
import hashlib
import json

import numpy as np
import pytest
from fastapi import HTTPException
from qdrant_client import QdrantClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models as m
from app.core.database import Base
from app.core.seed_data.seed_ai_data import DATAJSON, seed_ai_data
from app.schemas.job_role import JobRoleCreate, JobRoleUpdate
from app.schemas.learner_profile import LearnerProfileCreate, LearnerProfileResponse
from app.schemas.skill import SkillAliasCreate, SkillAliasUpdate
from app.services.ai_reference_service import AIReferenceService
from app.services.qdrant_service import QdrantJobRoleService, QdrantSkillService
from app.utils.learner_analyzer.schemas import NormalizedG1Output
from app.utils.skill_graph.role_matcher import RoleMatcher, load_roles_from_qdrant

TABLES = ["users", "skills", "courses", "course_skill", "skill_relation", "learning_paths", "learner_profiles"]


def fake_embed(texts):
    """Deterministic 384-d unit vectors (no model download in tests)."""
    out = []
    for t in texts:
        rng = np.random.default_rng(int(hashlib.md5(t.lower().encode()).hexdigest()[:8], 16))
        v = rng.normal(size=384)
        out.append((v / np.linalg.norm(v)).tolist())
    return out


def _session_factory():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(eng, tables=[Base.metadata.tables[t] for t in TABLES])
    return sessionmaker(bind=eng)


def _qdrant():
    client = QdrantClient(":memory:")
    return (QdrantSkillService(None, "edumentor_skills", 384, client=client),
            QdrantJobRoleService(None, "edumentor_job_roles", 384, client=client))


@pytest.fixture(scope="module")
def skills():
    return json.loads((DATAJSON / "skill_table.json").read_text(encoding="utf-8"))


@pytest.fixture()
def env(skills):
    Session = _session_factory()
    with Session() as s:  # same as seed_data_code.py: insert without skill_id, IDs follow file order
        s.add_all(m.Skills(skill=x["skill"]) for x in skills)
        s.commit()
    skill_q, role_q = _qdrant()
    seed_ai_data(Session(), skill_q=skill_q, role_q=role_q, embed=fake_embed)
    return Session, skill_q, role_q


def test_seed_indexes_roles_aliases_candidates_and_is_idempotent(env):
    Session, skill_q, role_q = env
    roles = json.loads((DATAJSON / "job_roles.json").read_text(encoding="utf-8"))["roles"]
    cands = {r["role_id"]: r["candidate_skills"] for r in
             json.loads((DATAJSON / "role_candidate_skills.json").read_text(encoding="utf-8"))}
    assert role_q.count(kind="role") == len(roles)
    assert role_q.count(kind="role_alias") > 0
    assert skill_q.count(kind="alias") > 0
    frontend = role_q.get_role(1)
    assert frontend["role_name"] == "Frontend Developer"
    assert frontend["candidate_skill_ids"] == [c["skill_id"] for c in cands[1]]

    before = (role_q.count(kind="role"), role_q.count(kind="role_alias"), skill_q.count(kind="alias"))
    seed_ai_data(Session(), skill_q=skill_q, role_q=role_q, embed=fake_embed)
    assert (role_q.count(kind="role"), role_q.count(kind="role_alias"), skill_q.count(kind="alias")) == before


def test_seed_refuses_when_skill_ids_drift(skills):
    Session = _session_factory()
    with Session() as s:  # one extra skill first -> every id shifts by one
        s.add(m.Skills(skill="Extra skill seeded first"))
        s.add_all(m.Skills(skill=x["skill"]) for x in skills)
        s.commit()
    skill_q, role_q = _qdrant()
    seed_ai_data(Session(), skill_q=skill_q, role_q=role_q, embed=fake_embed)
    assert role_q.count(kind="role") == 0
    assert skill_q.count(kind="alias") == 0


def test_role_matcher_reads_roles_from_qdrant(env):
    _, _, role_q = env
    matcher = RoleMatcher(load_roles_from_qdrant(role_q))
    assert matcher.match("front-end developer").role_id == 1
    assert matcher.match("Lập trình viên backend").role_id == 2


def test_skill_alias_crud_is_validated_against_postgres(env):
    Session, skill_q, role_q = env
    with Session() as db:
        svc = AIReferenceService(db, skill_q, role_q, embed=fake_embed)
        js = db.execute(select(m.Skills).where(m.Skills.skill == "JavaScript")).scalars().first()

        with pytest.raises(HTTPException) as e:   # alias equal to a skill name
            svc.create_skill_alias(SkillAliasCreate(skill_id=js.skill_id, alias_name="python"))
        assert e.value.status_code == 409
        with pytest.raises(HTTPException) as e:   # unknown skill
            svc.create_skill_alias(SkillAliasCreate(skill_id=999999, alias_name="Whatever lang"))
        assert e.value.status_code == 404
        with pytest.raises(HTTPException) as e:   # alias already owned by JavaScript in the seed
            svc.create_skill_alias(SkillAliasCreate(skill_id=1, alias_name="JS"))
        assert e.value.status_code == 409

        created = svc.create_skill_alias(SkillAliasCreate(skill_id=js.skill_id, alias_name="JScript ES"))
        assert created.skill == "JavaScript"
        renamed = svc.update_skill_alias("JScript ES", SkillAliasUpdate(alias_name="ES Script"))
        assert skill_q.get_alias("JScript ES") is None and renamed.alias_name == "ES Script"
        svc.delete_skill_alias("ES Script")
        assert skill_q.get_alias("ES Script") is None


def test_role_crud_and_candidates(env):
    Session, skill_q, role_q = env
    with Session() as db:
        svc = AIReferenceService(db, skill_q, role_q, embed=fake_embed)
        py = db.execute(select(m.Skills).where(m.Skills.skill == "Python")).scalars().first()

        with pytest.raises(HTTPException):        # name already used by role 1
            svc.create_role(JobRoleCreate(role_name="frontend developer"))
        with pytest.raises(HTTPException):        # alias already used by another role
            svc.create_role(JobRoleCreate(role_name="Web Wizard", aliases=["Frontend Engineer"]))

        role = svc.create_role(JobRoleCreate(role_name="Agent Workflow Engineer", aliases=["AI Agent Builder"],
                                             candidate_skill_ids=[py.skill_id]))
        assert role.role_id > 151 and [c.skill for c in role.candidate_skills] == ["Python"]
        assert svc.add_role_alias(role.role_id, "Agentic Systems Developer").role_name == "Agent Workflow Engineer"
        assert svc.update_role(role.role_id, JobRoleUpdate(role_name="AI Agent Engineer")).role_name == "AI Agent Engineer"
        assert role_q.get_alias("Agentic Systems Developer")["role_name"] == "AI Agent Engineer"
        with pytest.raises(HTTPException):        # duplicate candidate
            svc.add_candidate_skill(role.role_id, py.skill_id)
        assert svc.remove_candidate_skill(role.role_id, py.skill_id).candidate_skills == []
        assert svc.delete_role(role.role_id)["action"] == "deleted"
        assert role_q.get_role(role.role_id) is None and role_q.get_alias("Agentic Systems Developer") is None


def test_skill_changes_in_postgres_sync_to_qdrant(env):
    Session, skill_q, role_q = env
    with Session() as db:
        svc = AIReferenceService(db, skill_q, role_q, embed=fake_embed)
        sid = role_q.get_role(1)["candidate_skill_ids"][0]
        skill = db.get(m.Skills, sid)
        svc.create_skill_alias(SkillAliasCreate(skill_id=sid, alias_name="Temp Alias X"))

        skill.skill = skill.skill + " Renamed"
        svc.on_skill_changed(skill)
        assert skill_q.get_alias("Temp Alias X")["skill"] == skill.skill

        skill.is_active = False
        svc.on_skill_changed(skill)
        assert skill_q.get_alias("Temp Alias X") is None
        assert sid not in role_q.get_role(1)["candidate_skill_ids"]


def test_learner_profile_snapshot_per_learning_path(env):
    Session, *_ = env
    normalized = NormalizedG1Output.model_validate({
        "goal": {"original_query": "I know Python, want to be a data engineer in 6 months, 10h/week",
                 "target_role": {"raw_name": "data engineer", "canonical_name": "Data Engineer", "role_id": 30,
                                 "match_method": "exact", "match_score": None, "resolution_status": "matched"},
                 "target_technologies": [{"raw_name": "Airflow", "skill_id": None, "resolution_status": "unresolved"}],
                 "goal_type": "career"},
        "career_background": {"career_level": "junior",
                              "current_job_title": {"raw_name": "data analyst", "resolution_status": "unresolved"},
                              "technical_domains": [], "certifications": [], "previous_job_roles": []},
        "skill_profiles": [{"skill_name": "Python", "proficiency_level": "basic", "evidence_type": "explicitly_reported",
                            "link": {"raw_name": "Python", "skill_id": 5, "resolution_status": "matched"}}],
        "status": "ready",
        "practical_experience": [{"description": "Built ETL scripts in Python.", "evidence_type": "explicitly_reported",
                                  "related_skills": [{"raw_name": "Python", "skill_id": 5, "resolution_status": "matched"}]}],
        "learning_constraints": {"available_study_time": {"value": 10, "unit": "hours", "period": "per_week"},
                                 "deadline": {"deadline_type": "relative_duration", "duration_value": 6,
                                              "duration_unit": "months"}},
        "clarification_required": [], "unknown_fields": [],
    })
    with Session() as db:
        path = m.LearningPath(student_id=1, original_query=normalized.goal.original_query,
                              goal_type="career", status="ongoing")
        db.add(path)
        db.commit()
        data = LearnerProfileCreate.from_normalized(path.record_id, normalized)
        db.add(m.LearnerProfile(**data.model_dump(mode="json")))
        db.commit()
        db.refresh(path)

        profile = path.learner_profile                       # one profile per learning path
        assert profile.career_level == "junior" and profile.role_id == 30
        assert profile.skill_profiles[0]["skill_id"] == 5
        assert profile.practical_experiences[0]["related_skills"][0]["raw_name"] == "Python"
        resp = LearnerProfileResponse.model_validate(profile)
        assert resp.study_time_value == 10 and resp.deadline_duration_unit.value == "months"
        assert db.execute(select(func.count()).select_from(m.LearnerProfile)).scalar_one() == 1
