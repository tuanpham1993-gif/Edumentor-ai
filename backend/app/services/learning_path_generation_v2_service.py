"""AI learning path v2 (Phase 5-7): G1 output -> linked profile -> targets -> personalized graph -> save.

build_preview(...)   POST /api/learning-paths-generation/generate_ai_2 (after the LLM call)
confirm(...)         POST /api/learning-paths-generation/confirm-2
form_options(...)    GET  /api/learning-paths-generation/options
get_path_profile(...)GET  /api/learning-paths/{record_id}/profile

Targets (final nodes):
  career  -> candidate skills of the matched job role (Qdrant edumentor_job_roles)
             + target technologies that are skill-graph nodes
  project -> each target technology that is a skill-graph node
Known skills = explicit G1 skill_profiles + user_skills.status == "known" (the account profile,
"Hồ sơ của tôi" -> Kỹ năng, module 01). user_skills "learning" is shown, not treated as known.
Graph rules: app/utils/skill_graph/learning_graph.py.
"""
from __future__ import annotations

import logging
import re
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.learner_profile import LearnerProfile
from app.models.learning_path import LearningPath
from app.models.learning_path_graph import LearningPathGraph
from app.models.profile_reference import Certification, TechnicalDomain
from app.models.skill import Skills
from app.models.skill_relation import SkillRelation
from app.models.user_skill import UserSkill
from app.schemas.learner_profile import LearnerProfileCreate, LearnerProfileResponse
from app.schemas.learning_path_generation_v2 import (
    CertificationOption,
    GraphStats,
    GraphTarget,
    LearningPathConfirm2Request,
    LearningPathConfirm2Response,
    LearningPathFormOptions,
    LearningPathPreview2Response,
    LearningPathProfileResponse,
    MatchedRole,
    PreviewNode2,
    TechnicalDomainOption,
)
from app.schemas.learning_path_generation import LearningPathPreviewEdge
from app.services.learning_path_edge_service import add_new_learning_path_edges
from app.services.learning_path_node_service import add_new_learning_path_nodes
from app.services.learning_path_service import add_learning_path
from app.services.skill_linking_service import EntityLinker, SkillLinker, build_role_matcher, safe_role_match
from app.utils.learner_analyzer.normalizer import normalize_g1
from app.utils.learner_analyzer.schemas import (
    CareerLevel,
    ClarificationItem,
    G1Output,
    G1Status,
    NormalizedG1Output,
    ProficiencyLevel,
    ResolutionStatus,
)
from app.utils.skill_graph.graph_ops import prerequisite_index
from app.utils.skill_graph.learning_graph import (
    GENERATOR_VERSION,
    build_personalized_graph,
    explicit_known_ids,
    select_targets,
)

logger = logging.getLogger(__name__)

_VI_CHARS = re.compile(r"[ăâđêôơưàáạảãèéẹẻẽìíịỉĩòóọỏõùúụủũỳýỵỷỹ]", re.IGNORECASE)


def _vi(text: str) -> bool:
    return bool(_VI_CHARS.search(text or ""))


# ---- data loading ------------------------------------------------------------

def load_prerequisite_graph(db: Session) -> tuple[dict[int, list[int]], set[int]]:
    rows = db.execute(select(SkillRelation.from_skill_id, SkillRelation.to_skill_id, SkillRelation.relation_type)
                      .where(SkillRelation.relation_type == "prerequisite")).all()
    relations = [{"from_skill_id": a, "to_skill_id": b, "relation_type": t} for a, b, t in rows]
    nodes = {a for a, _, _ in rows} | {b for _, b, _ in rows}
    return prerequisite_index(relations), nodes


def user_skill_ids(db: Session, user_id: int) -> tuple[set[int], set[int]]:
    rows = db.execute(select(UserSkill.skill_id, UserSkill.status).where(UserSkill.user_id == user_id)).all()
    return {s for s, st in rows if st == "known"}, {s for s, st in rows if st == "learning"}


def skill_names(db: Session, ids: set[int]) -> dict[int, str]:
    if not ids:
        return {}
    return {sid: name.strip() for sid, name in db.execute(
        select(Skills.skill_id, Skills.skill).where(Skills.skill_id.in_(ids))).all()}


def _role_payload(role_q, role_id: int) -> Optional[dict]:
    if role_q is None:
        from app.services.qdrant_service import qdrant_role_service as role_q
    try:
        return role_q.get_role(role_id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Job role %s unavailable (Qdrant): %s", role_id, exc)
        return None


# ---- clarification -----------------------------------------------------------

def _clarifications(normalized: NormalizedG1Output, role_options: list[str], has_targets: bool) -> list[ClarificationItem]:
    """System questions when the goal cannot be turned into targets (or the role is ambiguous)."""
    goal = normalized.goal
    vi = _vi(goal.original_query)
    tr = goal.target_role
    items: list[ClarificationItem] = []
    if tr.raw_name and tr.resolution_status == ResolutionStatus.AMBIGUOUS:
        items.append(ClarificationItem(
            field="goal.target_role",
            question=(f"“{tr.raw_name}” gần với vị trí nào nhất?" if vi
                      else f"Which role is closest to “{tr.raw_name}”?"),
            options=role_options or None))
    if has_targets:
        return items
    if goal.goal_type.value == "project":
        items.append(ClarificationItem(
            field="goal.target_technologies",
            question=("Bạn muốn dùng công nghệ nào để làm dự án này?" if vi
                      else "Which technologies do you want to use for this project?"),
            options=None))
    elif tr.raw_name and tr.resolution_status == ResolutionStatus.UNRESOLVED:
        items.append(ClarificationItem(
            field="goal.target_role",
            question=(f"Chưa nhận ra vị trí “{tr.raw_name}”. Bạn ghi tên nghề cụ thể hơn được không?" if vi
                      else f"We don't recognise the role “{tr.raw_name}”. Could you name it more specifically?"),
            options=None))
    elif not tr.raw_name:
        items.append(ClarificationItem(
            field="goal.target_role",
            question="Bạn muốn làm vị trí công việc nào?" if vi else "Which job role are you aiming for?",
            options=None))
    return items


# ---- preview -----------------------------------------------------------------

def build_preview(db: Session, user_id: int, g1: G1Output, *, skill_q=None, role_q=None, embed=None,
                  role_matcher=None) -> LearningPathPreview2Response:
    prereq_idx, graph_nodes = load_prerequisite_graph(db)
    linker = SkillLinker(db, graph_nodes, skill_q=skill_q, embed=embed)
    entities = EntityLinker(db)
    matcher = role_matcher if role_matcher is not None else build_role_matcher(role_q, embed)

    normalized = normalize_g1(g1, linker.link, lambda raw: safe_role_match(matcher, raw), entities.match)
    goal = normalized.goal
    tr = goal.target_role

    role: Optional[MatchedRole] = None
    role_candidates: list[int] = []
    if tr.role_id is not None and tr.resolution_status == ResolutionStatus.MATCHED:
        payload = _role_payload(role_q, tr.role_id)
        if payload:
            role = MatchedRole(role_id=tr.role_id, role_name=payload["role_name"],
                               match_method=tr.match_method.value if tr.match_method else None,
                               match_score=tr.match_score)
            role_candidates = [int(s) for s in payload.get("candidate_skill_ids", []) if int(s) in linker.name_by_id]

    tech_ids = [t.skill_id for t in goal.target_technologies
                if t.skill_id is not None and t.resolution_status == ResolutionStatus.MATCHED]
    sel = select_targets(goal.goal_type.value, role_candidates, tech_ids, graph_nodes)

    role_options: list[str] = []
    if matcher is not None and tr.raw_name and tr.resolution_status == ResolutionStatus.AMBIGUOUS:
        # NormalizedTargetRole has no candidate_ids, so ask the matcher again for the options
        role_options = [matcher.roles[c].role_name for c in safe_role_match(matcher, tr.raw_name).candidate_ids
                        if c in matcher.roles]

    clarifications = list(normalized.clarification_required) if normalized.status == G1Status.NEEDS_CLARIFICATION else []
    clarifications += _clarifications(normalized, role_options, bool(sel.targets))
    clarifications = clarifications[:3]

    base = dict(original_query=goal.original_query, goal_type=goal.goal_type.value, profile=normalized,
                role=role, generator_version=GENERATOR_VERSION, warnings=list(sel.warnings))
    if not sel.targets:
        return LearningPathPreview2Response(status="needs_clarification", clarification_required=clarifications, **base)

    known_profile, learning_profile = user_skill_ids(db, user_id)
    known = explicit_known_ids([(s.link.skill_id, s.evidence_type.value) for s in normalized.skill_profiles])
    known |= known_profile
    graph = build_personalized_graph(sel.target_ids, prereq_idx, known, learning_profile)

    names = skill_names(db, {n["skill_id"] for n in graph["nodes"]} | set(sel.target_ids))
    source = dict(sel.targets)
    ordered = sorted(graph["nodes"], key=lambda n: (n["layer"], n["is_target"], names.get(n["skill_id"], "").lower()))
    nodes = [
        PreviewNode2(
            skill_id=n["skill_id"], skill_name=names.get(n["skill_id"], f"#{n['skill_id']}"),
            node_role=None if n["is_target"] else "prerequisite", is_target=n["is_target"], added_by="system",
            is_required=n["state"] not in ("known", "satisfied"), display_order=(i + 1) * 1000,
            state=n["state"], layer=n["layer"])
        for i, n in enumerate(ordered)
    ]
    edges = [LearningPathPreviewEdge(from_skill_id=a, from_skill_name=names.get(a, f"#{a}"),
                                     to_skill_id=b, to_skill_name=names.get(b, f"#{b}"),
                                     relation_type="prerequisite")
             for a, b in graph["edges"]]
    targets = [GraphTarget(skill_id=sid, skill_name=names.get(sid, f"#{sid}"), source=source[sid])
               for sid in graph["target_skill_ids"]]
    return LearningPathPreview2Response(
        status="needs_clarification" if clarifications else "ready",
        clarification_required=clarifications,
        targets=targets, nodes=nodes, edges=edges, layer=graph["layer"],
        retrieval_status=graph["retrieval_status"], stats=GraphStats(**graph["stats"]),
        **{**base, "warnings": base["warnings"] + graph["warnings"]},
    )


# ---- confirm -----------------------------------------------------------------

def confirm(db: Session, user_id: int, req: LearningPathConfirm2Request) -> LearningPathConfirm2Response:
    """Save path + nodes + edges + learner profile + generated graph in ONE transaction."""
    try:
        path = add_learning_path(db=db, student_id=user_id, original_query=req.original_query.strip(),
                                 goal_type=req.goal_type)
        nodes = [{"skill_id": n.skill_id, "node_role": n.node_role, "is_target": n.is_target,
                  "added_by": "system", "is_required": n.is_required, "display_order": n.display_order}
                 for n in req.nodes]
        edges = [{"from_skill_id": e.from_skill_id, "to_skill_id": e.to_skill_id, "relation_type": e.relation_type}
                 for e in req.edges]
        add_new_learning_path_nodes(db=db, path_id=path.record_id, nodes=nodes)
        add_new_learning_path_edges(db=db, path_id=path.record_id, edges=edges, nodes=nodes)

        data = LearnerProfileCreate.from_normalized(path.record_id, req.profile)
        row = data.model_dump(mode="json")
        row["deadline_target_date"] = data.deadline_target_date      # Date column needs a date object
        profile = LearnerProfile(**row)
        db.add(profile)
        db.flush()

        graph = LearningPathGraph(
            path_id=path.record_id, profile_id=profile.profile_id,
            role_id=req.role.role_id if req.role else None,
            targets=[t.model_dump() for t in req.targets],
            node_states={str(n.skill_id): n.state for n in req.nodes},
            layer={str(k): v for k, v in req.layer.items()},
            retrieval_status=req.retrieval_status, warnings=req.warnings,
            generator_version=req.generator_version or GENERATOR_VERSION,
        )
        db.add(graph)
        db.commit()
        return LearningPathConfirm2Response(record_id=path.record_id, profile_id=profile.profile_id,
                                            graph_id=graph.graph_id)
    except Exception:
        db.rollback()
        raise


# ---- reads -------------------------------------------------------------------

def form_options(db: Session) -> LearningPathFormOptions:
    certs = db.scalars(select(Certification).where(Certification.is_active.is_(True)).order_by(Certification.name)).all()
    domains = db.scalars(select(TechnicalDomain).where(TechnicalDomain.is_active.is_(True))
                         .order_by(TechnicalDomain.name)).all()
    return LearningPathFormOptions(
        career_levels=[c.value for c in CareerLevel],
        proficiency_levels=[p.value for p in ProficiencyLevel],
        certifications=[CertificationOption(cert_id=c.cert_id, name=c.name, issuer=c.issuer) for c in certs],
        technical_domains=[TechnicalDomainOption(domain_id=d.domain_id, name=d.name) for d in domains],
    )


def get_path_profile(db: Session, user_id: int, record_id: int) -> Optional[LearningPathProfileResponse]:
    path = db.scalar(select(LearningPath).where(LearningPath.record_id == record_id,
                                                LearningPath.student_id == user_id))
    if path is None or path.learner_profile is None:
        return None
    g = path.generated_graph
    return LearningPathProfileResponse(
        record_id=record_id,
        profile=LearnerProfileResponse.model_validate(path.learner_profile),
        role_id=g.role_id if g else None,
        targets=[GraphTarget(**t) for t in (g.targets if g else [])],
        node_states=g.node_states if g else {},
        retrieval_status=g.retrieval_status if g else None,
        warnings=g.warnings if g else [],
        generator_version=g.generator_version if g else None,
        created_at=path.learner_profile.created_at,
    )
