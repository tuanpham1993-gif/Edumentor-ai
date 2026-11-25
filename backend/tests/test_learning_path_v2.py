"""AI learning path v2 (Phase 5-7): target selection, cycle-safe retrieval, personalization/trim,
G1 normalization, and the full preview -> confirm -> profile flow on SQLite + in-memory Qdrant
seeded from the real datajson files."""
import json

import pytest
from sqlalchemy import func, select

import app.models as m
from app.core.database import Base
from app.core.seed_data.seed_ai_data import DATAJSON, seed_ai_data
from app.core.seed_data.seed_profile_reference import seed_profile_reference
from app.schemas.learning_path_generation_v2 import LearningPathConfirm2Request
from app.services import learning_path_generation_v2_service as svc
from app.utils.learner_analyzer.normalizer import normalize_g1
from app.utils.learner_analyzer.schemas import EntityMatch, G1Output, SkillLink
from app.utils.skill_graph.learning_graph import break_cycles, build_personalized_graph, select_targets
from app.utils.skill_graph.role_matcher import RoleMatch
from tests.test_seed_ai_data import _qdrant, fake_embed

TABLES = ["skills", "courses", "course_skill", "skill_relation", "learning_paths", "learning_path_nodes",
          "learning_path_edges", "learner_profiles", "learning_path_graphs", "user_skills",
          "certifications", "technical_domains"]


# ---- pure graph rules ------------------------------------------------------------

#   1 -> 2 -> 3 -> 5 ;  4 -> 5 ;  1 -> 4      (5 is the target)
IDX = {2: [1], 3: [2], 5: [3, 4], 4: [1]}


def test_project_targets_are_linked_technologies_in_graph():
    sel = select_targets("project", role_candidate_ids=[9], technology_ids=[5, 77, 3], graph_nodes={1, 2, 3, 4, 5})
    assert sel.targets == [(5, "technology"), (3, "technology")]
    assert sel.outside_graph == [77]


def test_project_without_graph_technology_falls_back_to_role():
    sel = select_targets("project", role_candidate_ids=[5], technology_ids=[77], graph_nodes={5})
    assert sel.targets == [(5, "role")] and sel.warnings


def test_career_targets_are_role_candidates_plus_technologies():
    sel = select_targets("career", role_candidate_ids=[5, 3], technology_ids=[4, 3], graph_nodes={1, 2, 3, 4, 5})
    assert sel.targets == [(5, "role"), (3, "role"), (4, "technology")]


def test_nothing_known_keeps_full_graph_and_starts_at_roots():
    g = build_personalized_graph([5], IDX, known_ids=set())
    assert {n["skill_id"] for n in g["nodes"]} == {1, 2, 3, 4, 5}
    states = {n["skill_id"]: n["state"] for n in g["nodes"]}
    assert states[1] == "eligible" and states[5] == "locked"
    assert g["layer"][0] == [1] and 5 in g["layer"][max(g["layer"])]


def test_known_skill_trims_its_ancestors_and_stays_as_context():
    # knows 2 -> 1 satisfied by closure; 4 still needed (its prerequisite 1 is satisfied -> eligible)
    g = build_personalized_graph([5], IDX, known_ids={2})
    states = {n["skill_id"]: n["state"] for n in g["nodes"]}
    assert states[2] == "known"            # direct prerequisite of a remaining skill: kept as context
    assert states[1] == "satisfied"        # kept: it feeds 4, which is still needed
    assert states[3] == "eligible" and states[4] == "eligible" and states[5] == "locked"
    g2 = build_personalized_graph([5], IDX, known_ids={3, 4})
    assert {n["skill_id"] for n in g2["nodes"]} == {3, 4, 5}      # 1 and 2 trimmed
    assert g2["stats"]["trimmed_nodes"] == 2


def test_known_target_is_kept_as_known():
    g = build_personalized_graph([5], IDX, known_ids={5})
    assert [(n["skill_id"], n["state"]) for n in g["nodes"]] == [(5, "known")]
    assert g["stats"]["all_targets_satisfied"]


def test_learning_skill_from_profile_is_marked_learning():
    g = build_personalized_graph([5], IDX, known_ids=set(), learning_ids={1})
    assert {n["skill_id"]: n["state"] for n in g["nodes"]}[1] == "learning"


def test_cycle_in_data_terminates_and_is_reported():
    cyclic = {2: [1], 1: [2], 3: [2]}      # 1 <-> 2, 3 needs 2
    g = build_personalized_graph([3], cyclic, known_ids=set())
    assert {n["skill_id"] for n in g["nodes"]} == {1, 2, 3}
    assert any("cyclic" in w for w in g["warnings"])
    _, removed = break_cycles([1, 2, 3], [(1, 2), (2, 1), (2, 3)])
    assert len(removed) == 1


# ---- normalizer -------------------------------------------------------------------

def _g1(**over) -> G1Output:
    data = {
        "goal": {"original_query": "I know Python and SQL and want to become a data engineer",
                 "target_role": {"raw_name": "data engineer", "canonical_name": None, "role_id": None},
                 "target_technologies": [], "goal_type": "career"},
        "career_background": {"career_level": "junior", "current_job_title": "backend developer",
                              "industry": None, "technical_domains": ["Backend Development"],
                              "certifications": ["CKA"], "previous_job_roles": [],
                              "relevant_it_work_experience": "1 year"},
        "skill_profiles": [
            {"skill_name": "Python", "proficiency_level": None, "experience_duration": None,
             "evidence_type": "explicitly_reported"},
            {"skill_name": "SQL", "proficiency_level": "basic", "experience_duration": None,
             "evidence_type": "explicitly_reported"},
        ],
        "status": "ready", "practical_experience": [],
        "learning_constraints": {"available_study_time": {"value": 10, "unit": "hours", "period": "per_week"},
                                 "deadline": None},
        "clarification_required": [], "unknown_fields": ["industry", "deadline"],
    }
    for k, v in over.items():
        data[k] = {**data[k], **v} if isinstance(v, dict) else v
    return G1Output.model_validate(data)


def test_normalizer_links_each_name_once_and_maps_roles():
    calls = []

    def link(names):
        calls.append(list(names))
        return [SkillLink(raw_name=n, skill_id=i + 1, resolution_status="matched") for i, n in enumerate(names)]

    def role(raw):
        return RoleMatch(raw, 42, "Data Engineer", "exact", None, "matched") if raw == "data engineer" \
            else RoleMatch(raw, resolution_status="unresolved")

    out = normalize_g1(_g1(), link, role,
                       lambda kind, n: EntityMatch(raw_name=n, resolution_status="unresolved"))
    assert calls == [["Python", "SQL"]]
    assert out.goal.target_role.role_id == 42 and out.goal.target_role.raw_name == "data engineer"
    assert out.skill_profiles[1].link.skill_id == 2
    assert out.career_background.current_job_title.resolution_status.value == "unresolved"


# ---- full flow (SQLite + in-memory Qdrant, real datajson) ------------------------------

@pytest.fixture(scope="module")
def world():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(eng, tables=[Base.metadata.tables[t] for t in TABLES])
    Session = sessionmaker(bind=eng)
    skills = json.loads((DATAJSON / "skill_table.json").read_text(encoding="utf-8"))
    relations = json.loads((DATAJSON / "skill_relation.json").read_text(encoding="utf-8"))
    with Session() as s:
        s.add_all(m.Skills(skill=x["skill"]) for x in skills)
        s.flush()
        s.add_all(m.SkillRelation(from_skill_id=r["from_skill_id"], to_skill_id=r["to_skill_id"],
                                  relation_type=r["relation_type"]) for r in relations)
        s.commit()
    seed_profile_reference(Session())
    skill_q, role_q = _qdrant()
    seed_ai_data(Session(), skill_q=skill_q, role_q=role_q, embed=fake_embed)
    from app.services.skill_linking_service import build_role_matcher
    matcher = build_role_matcher(role_q, fake_embed)
    return Session, skill_q, role_q, matcher


def _preview(world, g1, user_id=1):
    Session, skill_q, role_q, matcher = world
    with Session() as db:
        return svc.build_preview(db, user_id, g1, skill_q=skill_q, role_q=role_q, embed=fake_embed,
                                 role_matcher=matcher)


def test_career_preview_uses_role_candidates_and_known_skills(world):
    p = _preview(world, _g1())
    assert p.status == "ready", p.clarification_required
    assert p.role and p.role.role_name == "Data Engineer"
    _, _, role_q, _ = world
    cands = set(role_q.get_role(p.role.role_id)["candidate_skill_ids"])
    assert {t.skill_id for t in p.targets} == cands and all(t.source == "role" for t in p.targets)
    by_id = {n.skill_id: n for n in p.nodes}
    assert all(t.skill_id in by_id and by_id[t.skill_id].is_target for t in p.targets)
    # Python / SQL are explicit -> known (or trimmed) and never locked
    py, sql = p.profile.skill_profiles[0].link.skill_id, p.profile.skill_profiles[1].link.skill_id
    assert py and sql
    for sid in (py, sql):
        assert sid not in by_id or by_id[sid].state in ("known", "satisfied")
    # edges only between kept nodes, layers consistent with prerequisite direction
    for e in p.edges:
        assert by_id[e.from_skill_id].layer < by_id[e.to_skill_id].layer
    assert p.profile.career_background.certifications[0].canonical_name == "Certified Kubernetes Administrator (CKA)"
    assert p.profile.career_background.technical_domains[0].resolution_status.value == "matched"


def test_project_preview_targets_each_technology(world):
    g1 = _g1(goal={"original_query": "Tôi muốn làm một web app bán hàng bằng React và Docker",
                   "target_role": {"raw_name": None, "canonical_name": None, "role_id": None},
                   "target_technologies": ["React", "Docker"], "goal_type": "project"},
             skill_profiles=[])
    p = _preview(world, g1)
    assert p.status == "ready"
    assert [t.skill_name for t in p.targets] == ["React", "Docker"]
    assert all(t.source == "technology" for t in p.targets)
    finals = {n.skill_id for n in p.nodes if n.is_target}
    assert finals == {t.skill_id for t in p.targets}


def test_project_without_technologies_asks_in_learner_language(world):
    g1 = _g1(goal={"original_query": "Tôi muốn làm một ứng dụng",
                   "target_role": {"raw_name": None, "canonical_name": None, "role_id": None},
                   "target_technologies": [], "goal_type": "project"})
    p = _preview(world, g1)
    assert p.status == "needs_clarification" and not p.nodes
    assert p.clarification_required[0].field == "goal.target_technologies"
    assert "công nghệ" in p.clarification_required[0].question


def test_profile_skills_from_account_are_known(world):
    Session, *_ = world
    with Session() as db:
        k8s = db.scalar(select(m.Skills.skill_id).where(m.Skills.skill == "Kubernetes"))
        db.add(m.UserSkill(user_id=7, skill_id=k8s, status="known", source="manual"))
        db.commit()
    g1 = _g1(goal={"original_query": "build a deployment platform with Kubernetes",
                   "target_role": {"raw_name": None, "canonical_name": None, "role_id": None},
                   "target_technologies": ["Kubernetes"], "goal_type": "project"}, skill_profiles=[])
    p = _preview(world, g1, user_id=7)
    assert [(n.skill_id, n.state) for n in p.nodes] == [(k8s, "known")]


def test_confirm_saves_path_profile_and_graph_in_one_transaction(world):
    Session, *_ = world
    p = _preview(world, _g1())
    req = LearningPathConfirm2Request.model_validate({"confirmed": True, **p.model_dump(mode="json")})
    with Session() as db:
        res = svc.confirm(db, 1, req)
    with Session() as db:
        path = db.get(m.LearningPath, res.record_id)
        assert len(path.nodes) == len(p.nodes) and len(path.edges) == len(p.edges)
        assert path.learner_profile.role_id == p.role.role_id
        assert path.learner_profile.study_time_value == 10
        g = path.generated_graph
        assert g.profile_id == path.learner_profile.profile_id
        assert g.node_states == {str(n.skill_id): n.state for n in p.nodes}
        out = svc.get_path_profile(db, 1, res.record_id)
        assert out.profile.skill_profiles[0].raw_skill_name == "Python"
        assert svc.get_path_profile(db, 2, res.record_id) is None       # other user's path


def test_confirm_rolls_back_on_bad_node(world):
    Session, *_ = world
    p = _preview(world, _g1())
    body = p.model_dump(mode="json")
    body["nodes"][0]["skill_id"] = 999_999
    body["edges"] = []
    req = LearningPathConfirm2Request.model_validate({"confirmed": True, **body})
    with Session() as db:
        before = db.execute(select(func.count()).select_from(m.LearningPath)).scalar_one()
        with pytest.raises(ValueError):
            svc.confirm(db, 1, req)
        assert db.execute(select(func.count()).select_from(m.LearningPath)).scalar_one() == before


def test_form_options(world):
    Session, *_ = world
    with Session() as db:
        o = svc.form_options(db)
    assert "career_switcher" in o.career_levels and "expert" in o.proficiency_levels
    assert any(c.name == "CISSP" for c in o.certifications)
    assert any(d.name == "Backend Development" for d in o.technical_domains)
