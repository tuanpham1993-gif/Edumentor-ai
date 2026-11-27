"""Load the skill catalogue and resolve skill / role names to canonical IDs.

Canonical rule (one concept -> one skill_id):
1. Exact, case-sensitive match on skills.skill, if unique.
2. Alias match from skill_alias.json (alias -> canonical skill_id).
3. Case-insensitive match; if several records share the name, prefer the
   record used as canonical in skill_alias.json, otherwise the lowest id.
Unresolvable names raise KeyError so curation mistakes fail loudly.
"""
from __future__ import annotations

import json
import re
from functools import cached_property
from pathlib import Path

DATAJSON = Path(__file__).resolve().parents[4] / "datajson"


def norm(name: str) -> str:
    return " ".join(name.lower().split())


def concept_key(name: str) -> str:
    """Name without parenthetical qualifiers, for duplicate detection.

    "Python (Programming Language)" -> "python"; "Docker (Software)" -> "docker".
    """
    return norm(re.sub(r"\([^)]*\)", " ", name))


class Catalogue:
    def __init__(self, datajson: Path = DATAJSON):
        self.datajson = datajson
        self.skills: list[dict] = json.loads((datajson / "skill_table.json").read_text(encoding="utf-8"))
        self.aliases: list[dict] = json.loads((datajson / "skill_alias.json").read_text(encoding="utf-8"))
        self.roles: list[dict] = json.loads((datajson / "job_roles.json").read_text(encoding="utf-8"))["roles"]

    @cached_property
    def name_by_id(self) -> dict[int, str]:
        return {s["skill_id"]: s["skill"].strip() for s in self.skills}

    @cached_property
    def alias_canonical_ids(self) -> set[int]:
        return {a["skill_id"] for a in self.aliases}

    @cached_property
    def _exact(self) -> dict[str, list[int]]:
        out: dict[str, list[int]] = {}
        for s in self.skills:
            out.setdefault(s["skill"].strip(), []).append(s["skill_id"])
        return out

    @cached_property
    def _lower(self) -> dict[str, list[int]]:
        out: dict[str, list[int]] = {}
        for s in self.skills:
            out.setdefault(norm(s["skill"]), []).append(s["skill_id"])
        return out

    @cached_property
    def _alias(self) -> dict[str, int]:
        return {norm(alias): a["skill_id"] for a in self.aliases for alias in a["aliases"]}

    @cached_property
    def concept_groups(self) -> dict[str, list[int]]:
        out: dict[str, list[int]] = {}
        for s in self.skills:
            out.setdefault(concept_key(s["skill"]), []).append(s["skill_id"])
        return out

    def resolve_skill(self, name: str) -> int:
        exact = self._exact.get(name.strip(), [])
        if len(exact) == 1:
            return exact[0]
        if norm(name) in self._alias:
            return self._alias[norm(name)]
        ids = exact or self._lower.get(norm(name), [])
        if not ids:
            raise KeyError(f"skill not found: {name!r}")
        preferred = [i for i in ids if i in self.alias_canonical_ids]
        return preferred[0] if preferred else min(ids)

    def non_canonical_duplicate(self, skill_id: int) -> int | None:
        """If skill_id duplicates a concept whose canonical record is in skill_alias.json, return that canonical id."""
        group = self.concept_groups.get(concept_key(self.name_by_id[skill_id]), [])
        canon = [i for i in group if i in self.alias_canonical_ids]
        if canon and skill_id not in canon:
            return canon[0]
        return None

    @cached_property
    def role_id_by_name(self) -> dict[str, int]:
        out = {}
        for r in self.roles:
            for n in [r["name"]] + r.get("aliases", []):
                out[norm(n)] = r["id"]
        return out

    def resolve_role(self, name: str) -> int:
        try:
            return self.role_id_by_name[norm(name)]
        except KeyError:
            raise KeyError(f"role not found: {name!r}") from None

    @cached_property
    def role_name_by_id(self) -> dict[int, str]:
        return {r["id"]: r["name"] for r in self.roles}
