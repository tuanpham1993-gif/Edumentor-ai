"""G2 linking against Postgres + Qdrant: skill names, job roles, certifications, technical domains.

Skill name -> skills.skill_id, first accepted step wins:
  1. alias    Qdrant skill alias point (edumentor_skills, kind="alias"; the id is the normalized
              alias text, so this is an exact, case-insensitive lookup)
  2. exact    case-insensitive name match on active skills. Several records with the same name:
              prefer one that is a node of the prerequisite graph, then the lowest id
  3. semantic Qdrant nearest neighbour (skills + aliases). Accepted when the score is high and
              clearly ahead of a different skill; close calls are "ambiguous" with candidates
A match that is not in the graph is redirected to a same-concept record that is
("Docker (Software)" -> "Docker"), so the learning graph can use it.

Qdrant or the embedding model being down never fails a request: those steps are skipped and the
name stays unresolved (logged).
"""
from __future__ import annotations

import logging
import re
from typing import Callable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile_reference import Certification, TechnicalDomain
from app.models.skill import Skills
from app.utils.learner_analyzer.schemas import EntityMatch, MatchMethod, ResolutionStatus, SkillLink
from app.utils.skill_graph.role_matcher import RoleMatch, RoleMatcher, load_roles_from_qdrant, qdrant_semantic_search

logger = logging.getLogger(__name__)

SEMANTIC_ACCEPT = 0.80      # MiniLM cosine needed to accept a semantic skill match
SEMANTIC_MARGIN = 0.03      # ...and lead over the best *different* skill
SEMANTIC_CANDIDATE = 0.65   # scores at or above this are kept as candidates
MAX_CANDIDATES = 4

Embed = Callable[[list[str]], list[list[float]]]


def norm(text: str) -> str:
    return " ".join(text.lower().split())


def concept_key(name: str) -> str:
    """'Python (Programming Language)' -> 'python'."""
    return norm(re.sub(r"\([^)]*\)", " ", name))


class SkillLinker:
    def __init__(self, db: Session, graph_nodes: set[int], skill_q=None, embed: Optional[Embed] = None):
        self.db = db
        self.graph_nodes = graph_nodes
        self._skill_q = skill_q
        self._embed = embed
        rows = db.execute(select(Skills.skill_id, Skills.skill).where(Skills.is_active.is_(True))).all()
        self.name_by_id = {sid: name.strip() for sid, name in rows}
        self.by_name: dict[str, list[int]] = {}
        self.by_concept: dict[str, list[int]] = {}
        for sid, name in self.name_by_id.items():
            self.by_name.setdefault(norm(name), []).append(sid)
            self.by_concept.setdefault(concept_key(name), []).append(sid)

    # lazy so tests and Qdrant-less runs don't import the model
    @property
    def skill_q(self):
        if self._skill_q is None:
            from app.services.qdrant_service import qdrant_skill_service
            self._skill_q = qdrant_skill_service
        return self._skill_q

    @property
    def embed(self) -> Embed:
        if self._embed is None:
            from app.core.embedding_model import generate_embedding_skills_name
            self._embed = generate_embedding_skills_name
        return self._embed

    def _pick(self, ids: list[int]) -> int:
        in_graph = [i for i in ids if i in self.graph_nodes]
        return min(in_graph or ids)

    def _to_graph(self, sid: int) -> int:
        """Redirect to a same-concept record that is in the prerequisite graph, if sid is not."""
        if sid in self.graph_nodes or sid not in self.name_by_id:
            return sid
        same = [i for i in self.by_concept.get(concept_key(self.name_by_id[sid]), []) if i in self.graph_nodes]
        return min(same) if same else sid

    def _matched(self, raw: str, sid: int, method: MatchMethod, score: Optional[float] = None) -> SkillLink:
        sid = self._to_graph(sid)
        return SkillLink(raw_name=raw, skill_id=sid, canonical_name=self.name_by_id.get(sid),
                         match_method=method, match_score=score, resolution_status=ResolutionStatus.MATCHED)

    def _alias(self, raw: str) -> Optional[int]:
        try:
            payload = self.skill_q.get_alias(raw)
        except Exception as exc:  # noqa: BLE001 - Qdrant down: skip this step
            logger.warning("Skill alias lookup skipped: %s", exc)
            return None
        sid = int(payload["skill_id"]) if payload else None
        return sid if sid in self.name_by_id else None

    def link(self, names: list[str]) -> list[SkillLink]:
        out: dict[int, SkillLink] = {}
        pending: list[tuple[int, str]] = []
        for i, raw in enumerate(names):
            sid = self._alias(raw)
            if sid is not None:
                out[i] = self._matched(raw, sid, MatchMethod.ALIAS)
                continue
            ids = self.by_name.get(norm(raw))
            if ids:
                out[i] = self._matched(raw, self._pick(ids), MatchMethod.EXACT)
                continue
            pending.append((i, raw))
        if pending:
            out.update(self._semantic(pending))
        return [out[i] for i in range(len(names))]

    def _semantic(self, pending: list[tuple[int, str]]) -> dict[int, SkillLink]:
        unresolved = {i: SkillLink(raw_name=raw, resolution_status=ResolutionStatus.UNRESOLVED) for i, raw in pending}
        try:
            vectors = self.embed([raw for _, raw in pending])
        except Exception as exc:  # noqa: BLE001
            logger.warning("Semantic skill linking skipped: %s", exc)
            return unresolved
        result = dict(unresolved)
        for (i, raw), vec in zip(pending, vectors):
            try:
                hits = self.skill_q.search_skill(vec, limit=8)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Semantic skill linking skipped: %s", exc)
                return unresolved
            best: dict[int, float] = {}
            for h in hits:
                sid = int(h.payload["skill_id"])
                if sid in self.name_by_id:
                    best[sid] = max(best.get(sid, 0.0), float(h.score))
            ranked = sorted(best.items(), key=lambda kv: -kv[1])
            if not ranked:
                continue
            top_id, top = ranked[0]
            second = ranked[1][1] if len(ranked) > 1 else 0.0
            if top >= SEMANTIC_ACCEPT and top - second >= SEMANTIC_MARGIN:
                result[i] = self._matched(raw, top_id, MatchMethod.SEMANTIC, round(top, 3))
            else:
                cands = [sid for sid, sc in ranked if sc >= SEMANTIC_CANDIDATE][:MAX_CANDIDATES]
                if cands:
                    result[i] = SkillLink(raw_name=raw, match_score=round(top, 3),
                                          resolution_status=ResolutionStatus.AMBIGUOUS, candidate_ids=cands)
        return result


class EntityLinker:
    """Certifications and technical domains: exact or alias, case-insensitive. Industry has no list."""

    def __init__(self, db: Session):
        self.tables: dict[str, dict[str, tuple[int, str]]] = {"certification": {}, "technical_domain": {}}
        for c in db.scalars(select(Certification).where(Certification.is_active.is_(True))):
            for text in [c.name] + list(c.aliases or []):
                self.tables["certification"].setdefault(norm(text), (c.cert_id, c.name))
        for d in db.scalars(select(TechnicalDomain).where(TechnicalDomain.is_active.is_(True))):
            self.tables["technical_domain"].setdefault(norm(d.name), (d.domain_id, d.name))

    def match(self, kind: str, raw: str) -> EntityMatch:
        hit = self.tables.get(kind, {}).get(norm(raw))
        if hit:
            method = MatchMethod.EXACT if norm(hit[1]) == norm(raw) else MatchMethod.ALIAS
            return EntityMatch(raw_name=raw, canonical_id=hit[0], canonical_name=hit[1], match_method=method,
                               resolution_status=ResolutionStatus.MATCHED)
        return EntityMatch(raw_name=raw, resolution_status=ResolutionStatus.UNRESOLVED)


def build_role_matcher(role_q=None, embed: Optional[Embed] = None) -> Optional[RoleMatcher]:
    """RoleMatcher over the Qdrant job roles; None when Qdrant is unavailable."""
    try:
        roles = load_roles_from_qdrant(role_q)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Job roles unavailable (Qdrant): %s", exc)
        return None
    try:
        semantic = qdrant_semantic_search(role_q, embed)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Semantic role search disabled: %s", exc)
        semantic = None
    return RoleMatcher(roles, semantic_search=semantic)


def safe_role_match(matcher: Optional[RoleMatcher], raw: Optional[str]) -> RoleMatch:
    if matcher is None or not raw:
        return RoleMatch(raw or "", resolution_status="unresolved")
    try:
        return matcher.match(raw)
    except Exception as exc:  # noqa: BLE001 - semantic step failed: retry without it
        logger.warning("Role semantic search failed, using string matching only: %s", exc)
        return RoleMatcher(list(matcher.roles.values())).match(raw)
