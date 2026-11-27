"""Qdrant collections used by the AI learning path.

edumentor_skills (QdrantSkillService)
    kind="skill"  one point per active skill        payload {kind, skill_id, skill}
    kind="alias"  one point per skill alias          payload {kind, skill_id, skill, alias}
    Both kinds carry skill_id, so a vector search for "k8s" or "Kubernetes" returns the same
    skills.skill_id. Postgres `skills` stays the source of truth for skill rows.

edumentor_job_roles (QdrantJobRoleService)
    kind="role"        one point per job role        payload {kind, role_id, role_name, description,
                                                              is_active, candidate_skill_ids}
    kind="role_alias"  one point per role alias      payload {kind, role_id, role_name, alias}
    candidate_skill_ids are skills.skill_id values (the target skills of the role).

Point IDs are deterministic (uuid5), so re-indexing overwrites instead of duplicating.
"""
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PointIdsList,
    PointStruct,
    VectorParams,
)

from app.core.config import settings


def _norm(text: str) -> str:
    return " ".join(text.lower().split())


def generate_point_id(skill_id: int) -> str:
    return str(uuid5(NAMESPACE_URL, f"edumentor-skill:{skill_id}"))


def alias_point_id(alias: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"edumentor-skill-alias:{_norm(alias)}"))


def role_point_id(role_id: int) -> str:
    return str(uuid5(NAMESPACE_URL, f"edumentor-role:{role_id}"))


def role_alias_point_id(alias: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"edumentor-role-alias:{_norm(alias)}"))


def _match(**conditions) -> Filter:
    return Filter(must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in conditions.items()])


class _QdrantCollection:
    def __init__(self, qdrant_url, collection_name, vector_size, client: QdrantClient | None = None):
        self.client = client or QdrantClient(url=qdrant_url)  # client: e.g. QdrantClient(":memory:") in tests
        self.COLLECTION_NAME = collection_name
        self.VECTOR_SIZE = vector_size

    def create_collection(self) -> bool:
        """Create the collection if missing. Returns True only when it was created now."""
        existing = [c.name for c in self.client.get_collections().collections]
        if self.COLLECTION_NAME in existing:
            return False
        self.client.create_collection(collection_name=self.COLLECTION_NAME,
                                      vectors_config=VectorParams(size=self.VECTOR_SIZE, distance=Distance.COSINE))
        print(f"Created collection: {self.COLLECTION_NAME}")
        return True

    def _upsert(self, points: list[PointStruct], batch_size: int = 100) -> None:
        for start in range(0, len(points), batch_size):
            self.client.upsert(collection_name=self.COLLECTION_NAME, points=points[start:start + batch_size], wait=True)

    def _scroll(self, flt: Filter) -> list:
        out, offset = [], None
        while True:
            points, offset = self.client.scroll(collection_name=self.COLLECTION_NAME, scroll_filter=flt,
                                                limit=256, offset=offset, with_payload=True, with_vectors=False)
            out.extend(points)
            if offset is None:
                return out

    def count(self, **conditions) -> int:
        return self.client.count(collection_name=self.COLLECTION_NAME, count_filter=_match(**conditions),
                                 exact=True).count

    def _delete_where(self, **conditions) -> None:
        self.client.delete(collection_name=self.COLLECTION_NAME,
                           points_selector=FilterSelector(filter=_match(**conditions)), wait=True)

    def _delete_ids(self, ids: list[str]) -> None:
        self.client.delete(collection_name=self.COLLECTION_NAME, points_selector=PointIdsList(points=ids), wait=True)


class QdrantSkillService(_QdrantCollection):
    # ---- skills ----
    def index_skill(self, skills, embeddings, batch_size=100):
        """skills: [{"skill_id", "skill_name"}], embeddings in the same order."""
        if len(skills) != len(embeddings):
            raise ValueError("Number of skills and embeddings must match.")
        points = [PointStruct(id=generate_point_id(s["skill_id"]), vector=e,
                              payload={"kind": "skill", "skill_id": int(s["skill_id"]), "skill": s["skill_name"]})
                  for s, e in zip(skills, embeddings)]
        self._upsert(points, batch_size)
        print(f"Successfully indexed {len(points)} skills.")

    def search_skill(self, embedding, limit=5):
        """Nearest skills and aliases; every hit has payload["skill_id"]."""
        return self.client.query_points(collection_name=self.COLLECTION_NAME, query=embedding,
                                        limit=limit, with_payload=True).points

    def update_skill(self, skill_id: int, skill_name: str, embedding):
        self._upsert([PointStruct(id=generate_point_id(skill_id), vector=embedding,
                                  payload={"kind": "skill", "skill_id": int(skill_id), "skill": skill_name})])
        # aliases keep the canonical name in their payload
        self.client.set_payload(collection_name=self.COLLECTION_NAME, payload={"skill": skill_name},
                                points=_match(kind="alias", skill_id=int(skill_id)), wait=True)

    def delete_skill(self, skill_id: int):
        """Remove the skill point and all its alias points."""
        self._delete_ids([generate_point_id(skill_id)])
        self._delete_where(kind="alias", skill_id=int(skill_id))

    # ---- aliases ----
    def upsert_aliases(self, aliases: list[dict], embeddings) -> None:
        """aliases: [{"skill_id", "skill", "alias"}], embeddings of the alias texts."""
        points = [PointStruct(id=alias_point_id(a["alias"]), vector=e,
                              payload={"kind": "alias", "skill_id": int(a["skill_id"]),
                                       "skill": a["skill"], "alias": a["alias"]})
                  for a, e in zip(aliases, embeddings)]
        self._upsert(points)

    def get_alias(self, alias: str):
        found = self.client.retrieve(collection_name=self.COLLECTION_NAME, ids=[alias_point_id(alias)], with_payload=True)
        return found[0].payload if found else None

    def list_aliases(self, skill_id: int | None = None) -> list[dict]:
        flt = _match(kind="alias", skill_id=int(skill_id)) if skill_id is not None else _match(kind="alias")
        return sorted((p.payload for p in self._scroll(flt)), key=lambda a: (a["skill_id"], _norm(a["alias"])))

    def delete_alias(self, alias: str) -> None:
        self._delete_ids([alias_point_id(alias)])


class QdrantJobRoleService(_QdrantCollection):
    def upsert_role(self, role: dict, embedding) -> None:
        """role: {role_id, role_name, description, is_active, candidate_skill_ids}"""
        payload = {"kind": "role", "role_id": int(role["role_id"]), "role_name": role["role_name"],
                   "description": role.get("description"), "is_active": bool(role.get("is_active", True)),
                   "candidate_skill_ids": [int(x) for x in role.get("candidate_skill_ids", [])]}
        self._upsert([PointStruct(id=role_point_id(role["role_id"]), vector=embedding, payload=payload)])
        # role aliases keep the current role name in their payload
        self.client.set_payload(collection_name=self.COLLECTION_NAME, payload={"role_name": role["role_name"]},
                                points=_match(kind="role_alias", role_id=int(role["role_id"])), wait=True)

    def upsert_roles(self, roles: list[dict], embeddings) -> None:
        points = [PointStruct(id=role_point_id(r["role_id"]), vector=e,
                              payload={"kind": "role", "role_id": int(r["role_id"]), "role_name": r["role_name"],
                                       "description": r.get("description"), "is_active": bool(r.get("is_active", True)),
                                       "candidate_skill_ids": [int(x) for x in r.get("candidate_skill_ids", [])]})
                  for r, e in zip(roles, embeddings)]
        self._upsert(points)

    def set_candidates(self, role_id: int, skill_ids: list[int]) -> None:
        self.client.set_payload(collection_name=self.COLLECTION_NAME,
                                payload={"candidate_skill_ids": [int(x) for x in skill_ids]},
                                points=[role_point_id(role_id)], wait=True)

    def get_role(self, role_id: int):
        found = self.client.retrieve(collection_name=self.COLLECTION_NAME, ids=[role_point_id(role_id)], with_payload=True)
        return found[0].payload if found else None

    def list_roles(self, active_only: bool = False) -> list[dict]:
        flt = _match(kind="role", is_active=True) if active_only else _match(kind="role")
        return sorted((p.payload for p in self._scroll(flt)), key=lambda r: r["role_id"])

    def delete_role(self, role_id: int) -> None:
        self._delete_ids([role_point_id(role_id)])
        self._delete_where(kind="role_alias", role_id=int(role_id))

    def upsert_aliases(self, aliases: list[dict], embeddings) -> None:
        """aliases: [{"role_id", "role_name", "alias"}]"""
        points = [PointStruct(id=role_alias_point_id(a["alias"]), vector=e,
                              payload={"kind": "role_alias", "role_id": int(a["role_id"]),
                                       "role_name": a["role_name"], "alias": a["alias"]})
                  for a, e in zip(aliases, embeddings)]
        self._upsert(points)

    def get_alias(self, alias: str):
        found = self.client.retrieve(collection_name=self.COLLECTION_NAME, ids=[role_alias_point_id(alias)], with_payload=True)
        return found[0].payload if found else None

    def list_aliases(self, role_id: int | None = None) -> list[dict]:
        flt = _match(kind="role_alias", role_id=int(role_id)) if role_id is not None else _match(kind="role_alias")
        return sorted((p.payload for p in self._scroll(flt)), key=lambda a: (a["role_id"], _norm(a["alias"])))

    def delete_alias(self, alias: str) -> None:
        self._delete_ids([role_alias_point_id(alias)])

    def search_roles(self, embedding, limit: int = 10) -> list[tuple[int, float]]:
        """[(role_id, best score)] over role names and aliases, best first, one entry per role."""
        hits = self.client.query_points(collection_name=self.COLLECTION_NAME, query=embedding,
                                        limit=limit, with_payload=True).points
        best: dict[int, float] = {}
        for h in hits:
            rid = int(h.payload["role_id"])
            best[rid] = max(best.get(rid, 0.0), float(h.score))
        return sorted(best.items(), key=lambda kv: -kv[1])


qdrant_skill_service = QdrantSkillService(qdrant_url=settings.QDRANT_URL,
                                          collection_name="edumentor_skills",
                                          vector_size=384)
qdrant_role_service = QdrantJobRoleService(qdrant_url=settings.QDRANT_URL,
                                           collection_name="edumentor_job_roles",
                                           vector_size=384)
