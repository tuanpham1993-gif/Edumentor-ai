"""CRUD for the AI reference data stored in Qdrant, kept consistent with Postgres `skills`.

    skill aliases          -> edumentor_skills    (kind="alias")
    job roles              -> edumentor_job_roles (kind="role")
    job role aliases       -> edumentor_job_roles (kind="role_alias")
    role candidate skills  -> payload candidate_skill_ids of the role point

Consistency rules with Postgres:
- An alias or a candidate skill may only point to an existing, active skills.skill_id.
- A skill alias may not equal any skills.skill name (case-insensitive), and one alias maps to one skill.
- A role name / role alias may be used by one role only.
- When a skill changes in Postgres, call on_skill_changed(); when it is deleted, on_skill_deleted().
  (sync_skill_to_qdrant in skills_service.py does this.) Deactivated or deleted skills lose their
  alias points and are removed from every role's candidate list; a renamed skill updates its
  alias payloads, and an alias equal to the new skill name is dropped.
"""
from __future__ import annotations

from typing import Callable, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.learner_profile import LearnerProfile
from app.models.skill import Skills
from app.schemas.job_role import (
    CandidateSkillItem,
    JobRoleAliasResponse,
    JobRoleCreate,
    JobRoleResponse,
    JobRoleUpdate,
)
from app.schemas.skill import SkillAliasCreate, SkillAliasResponse, SkillAliasUpdate


def _norm(text: str) -> str:
    return " ".join(text.lower().split())


def _default_embed(texts: list[str]) -> list[list[float]]:
    from app.core.embedding_model import generate_embedding_skills_name
    return generate_embedding_skills_name(texts)


def _http(code: int, msg: str) -> HTTPException:
    return HTTPException(status_code=code, detail=msg)


class AIReferenceService:
    def __init__(self, db: Session, skill_q=None, role_q=None,
                 embed: Optional[Callable[[list[str]], list[list[float]]]] = None):
        if skill_q is None or role_q is None:
            from app.services.qdrant_service import qdrant_role_service, qdrant_skill_service
            skill_q = skill_q or qdrant_skill_service
            role_q = role_q or qdrant_role_service
        self.db = db
        self.skill_q = skill_q
        self.role_q = role_q
        self.embed = embed or _default_embed

    # ------------------------------------------------------------------ helpers
    def _active_skill(self, skill_id: int) -> Skills:
        skill = self.db.get(Skills, skill_id)
        if skill is None or not skill.is_active:
            raise _http(status.HTTP_404_NOT_FOUND, f"Không tìm thấy kỹ năng đang hoạt động với id {skill_id}")
        return skill

    def _skill_name_taken(self, name: str) -> bool:
        return self.db.execute(
            select(Skills.skill_id).where(func.lower(func.trim(Skills.skill)) == _norm(name)).limit(1)
        ).first() is not None

    def _skill_names(self, skill_ids: list[int]) -> dict[int, str]:
        if not skill_ids:
            return {}
        return dict(self.db.execute(select(Skills.skill_id, Skills.skill).where(Skills.skill_id.in_(skill_ids))).all())

    # ------------------------------------------------------------ skill aliases
    def list_skill_aliases(self, skill_id: Optional[int] = None) -> list[SkillAliasResponse]:
        return [SkillAliasResponse(skill_id=a["skill_id"], skill=a["skill"], alias_name=a["alias"])
                for a in self.skill_q.list_aliases(skill_id)]

    def _check_skill_alias(self, alias: str, skill_id: int, ignore: Optional[str] = None) -> Skills:
        skill = self._active_skill(skill_id)
        if self._skill_name_taken(alias):
            raise _http(status.HTTP_409_CONFLICT, f"Alias '{alias}' trùng với tên một kỹ năng.")
        owner = self.skill_q.get_alias(alias)
        if owner and (ignore is None or _norm(ignore) != _norm(alias)):
            raise _http(status.HTTP_409_CONFLICT,
                        f"Alias '{alias}' đã thuộc kỹ năng {owner['skill_id']} ({owner['skill']}).")
        return skill

    def create_skill_alias(self, data: SkillAliasCreate) -> SkillAliasResponse:
        skill = self._check_skill_alias(data.alias_name, data.skill_id)
        item = {"skill_id": skill.skill_id, "skill": skill.skill, "alias": data.alias_name}
        self.skill_q.upsert_aliases([item], self.embed([data.alias_name]))
        return SkillAliasResponse(skill_id=skill.skill_id, skill=skill.skill, alias_name=data.alias_name)

    def update_skill_alias(self, alias_name: str, data: SkillAliasUpdate) -> SkillAliasResponse:
        current = self.skill_q.get_alias(alias_name)
        if current is None:
            raise _http(status.HTTP_404_NOT_FOUND, f"Không tìm thấy alias '{alias_name}'.")
        new_alias = data.alias_name or current["alias"]
        new_skill_id = data.skill_id or current["skill_id"]
        skill = self._check_skill_alias(new_alias, new_skill_id, ignore=current["alias"])
        if _norm(new_alias) != _norm(current["alias"]):
            self.skill_q.delete_alias(current["alias"])
        self.skill_q.upsert_aliases([{"skill_id": skill.skill_id, "skill": skill.skill, "alias": new_alias}],
                                    self.embed([new_alias]))
        return SkillAliasResponse(skill_id=skill.skill_id, skill=skill.skill, alias_name=new_alias)

    def delete_skill_alias(self, alias_name: str) -> None:
        if self.skill_q.get_alias(alias_name) is None:
            raise _http(status.HTTP_404_NOT_FOUND, f"Không tìm thấy alias '{alias_name}'.")
        self.skill_q.delete_alias(alias_name)

    # ------------------------------------------------------------------- roles
    def _role_response(self, role: dict, aliases: Optional[list[str]] = None,
                       names: Optional[dict[int, str]] = None) -> JobRoleResponse:
        ids = role.get("candidate_skill_ids", [])
        names = names if names is not None else self._skill_names(ids)
        if aliases is None:
            aliases = [a["alias"] for a in self.role_q.list_aliases(role["role_id"])]
        return JobRoleResponse(
            role_id=role["role_id"], role_name=role["role_name"], description=role.get("description"),
            is_active=role.get("is_active", True), aliases=aliases,
            candidate_skills=[CandidateSkillItem(skill_id=i, skill=names[i]) for i in ids if i in names],
        )

    def _get_role_payload(self, role_id: int) -> dict:
        role = self.role_q.get_role(role_id)
        if role is None:
            raise _http(status.HTTP_404_NOT_FOUND, f"Không tìm thấy vai trò với id {role_id}")
        return role

    def _check_role_text(self, text: str, role_id: int) -> None:
        """A role name or alias must not be used by another role."""
        for r in self.role_q.list_roles():
            if r["role_id"] != role_id and _norm(r["role_name"]) == _norm(text):
                raise _http(status.HTTP_409_CONFLICT, f"'{text}' là tên của vai trò {r['role_id']}.")
        owner = self.role_q.get_alias(text)
        if owner and owner["role_id"] != role_id:
            raise _http(status.HTTP_409_CONFLICT, f"'{text}' là alias của vai trò {owner['role_id']}.")

    def _check_candidates(self, skill_ids: list[int]) -> list[int]:
        unique = list(dict.fromkeys(skill_ids))
        for sid in unique:
            self._active_skill(sid)
        return unique

    def list_roles(self, active_only: bool = False) -> list[JobRoleResponse]:
        roles = self.role_q.list_roles(active_only)
        aliases: dict[int, list[str]] = {}
        for a in self.role_q.list_aliases():
            aliases.setdefault(a["role_id"], []).append(a["alias"])
        names = self._skill_names(sorted({i for r in roles for i in r.get("candidate_skill_ids", [])}))
        return [self._role_response(r, aliases.get(r["role_id"], []), names) for r in roles]

    def get_role(self, role_id: int) -> JobRoleResponse:
        return self._role_response(self._get_role_payload(role_id))

    def create_role(self, data: JobRoleCreate) -> JobRoleResponse:
        roles = self.role_q.list_roles()
        role_id = data.role_id or (max((r["role_id"] for r in roles), default=0) + 1)
        if any(r["role_id"] == role_id for r in roles):
            raise _http(status.HTTP_409_CONFLICT, f"role_id {role_id} đã tồn tại.")
        texts = [data.role_name] + data.aliases
        if len({_norm(t) for t in texts}) != len(texts):
            raise _http(status.HTTP_422_UNPROCESSABLE_ENTITY, "Tên vai trò và các alias bị trùng nhau.")
        for t in texts:
            self._check_role_text(t, role_id)
        role = {"role_id": role_id, "role_name": data.role_name, "description": data.description,
                "is_active": True, "candidate_skill_ids": self._check_candidates(data.candidate_skill_ids)}
        vectors = self.embed(texts)
        self.role_q.upsert_role(role, vectors[0])
        if data.aliases:
            self.role_q.upsert_aliases(
                [{"role_id": role_id, "role_name": data.role_name, "alias": a} for a in data.aliases], vectors[1:])
        return self._role_response(role, data.aliases)

    def update_role(self, role_id: int, data: JobRoleUpdate) -> JobRoleResponse:
        role = self._get_role_payload(role_id)
        changes = data.model_dump(exclude_unset=True)
        if changes.get("role_name"):
            self._check_role_text(changes["role_name"], role_id)
        role.update({k: v for k, v in changes.items() if v is not None or k == "description"})
        self.role_q.upsert_role(role, self.embed([role["role_name"]])[0])
        return self._role_response(role)

    def delete_role(self, role_id: int) -> dict:
        """Deactivate a role still referenced by saved learning-path profiles, otherwise delete it."""
        role = self._get_role_payload(role_id)
        used = self.db.execute(
            select(func.count()).select_from(LearnerProfile).where(LearnerProfile.role_id == role_id)
        ).scalar_one()
        if used:
            role["is_active"] = False
            self.role_q.upsert_role(role, self.embed([role["role_name"]])[0])
            return {"action": "deactivated", "role_id": role_id,
                    "message": f"Vai trò đang được {used} lộ trình tham chiếu nên chỉ bị vô hiệu hóa."}
        self.role_q.delete_role(role_id)
        return {"action": "deleted", "role_id": role_id, "message": "Đã xóa vai trò."}

    # ----------------------------------------------------------- role aliases
    def add_role_alias(self, role_id: int, alias: str) -> JobRoleAliasResponse:
        role = self._get_role_payload(role_id)
        if _norm(alias) == _norm(role["role_name"]):
            raise _http(status.HTTP_409_CONFLICT, "Alias trùng với tên vai trò.")
        self._check_role_text(alias, role_id)
        self.role_q.upsert_aliases([{"role_id": role_id, "role_name": role["role_name"], "alias": alias}],
                                   self.embed([alias]))
        return JobRoleAliasResponse(role_id=role_id, role_name=role["role_name"], alias_name=alias)

    def delete_role_alias(self, alias: str) -> None:
        if self.role_q.get_alias(alias) is None:
            raise _http(status.HTTP_404_NOT_FOUND, f"Không tìm thấy alias vai trò '{alias}'.")
        self.role_q.delete_alias(alias)

    # ------------------------------------------------- role candidate skills
    def add_candidate_skill(self, role_id: int, skill_id: int) -> JobRoleResponse:
        role = self._get_role_payload(role_id)
        self._active_skill(skill_id)
        ids = role.get("candidate_skill_ids", [])
        if skill_id in ids:
            raise _http(status.HTTP_409_CONFLICT, f"Kỹ năng {skill_id} đã là kỹ năng đích của vai trò {role_id}.")
        role["candidate_skill_ids"] = ids + [skill_id]
        self.role_q.set_candidates(role_id, role["candidate_skill_ids"])
        return self._role_response(role)

    def remove_candidate_skill(self, role_id: int, skill_id: int) -> JobRoleResponse:
        role = self._get_role_payload(role_id)
        ids = role.get("candidate_skill_ids", [])
        if skill_id not in ids:
            raise _http(status.HTTP_404_NOT_FOUND, f"Kỹ năng {skill_id} không thuộc vai trò {role_id}.")
        role["candidate_skill_ids"] = [i for i in ids if i != skill_id]
        self.role_q.set_candidates(role_id, role["candidate_skill_ids"])
        return self._role_response(role)

    # --------------------------------------------- sync from Postgres skills
    def _drop_skill_from_roles(self, skill_id: int) -> None:
        for r in self.role_q.list_roles():
            ids = r.get("candidate_skill_ids", [])
            if skill_id in ids:
                self.role_q.set_candidates(r["role_id"], [i for i in ids if i != skill_id])

    def on_skill_changed(self, skill: Skills) -> None:
        if not skill.is_active:
            self.skill_q.delete_skill(skill.skill_id)
            self._drop_skill_from_roles(skill.skill_id)
            return
        self.skill_q.update_skill(skill_id=skill.skill_id, skill_name=skill.skill,
                                  embedding=self.embed([skill.skill])[0])
        if self.skill_q.get_alias(skill.skill):  # the new name is now an exact skill name
            self.skill_q.delete_alias(skill.skill)

    def on_skill_deleted(self, skill_id: int) -> None:
        self.skill_q.delete_skill(skill_id)
        self._drop_skill_from_roles(skill_id)
