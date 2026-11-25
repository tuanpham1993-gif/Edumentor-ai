"""Match a free-text target role (G1 goal.target_role.raw_name) to a job_roles.role_id.

Order (stops at the first accepted result):
  1. exact   - normalized name or alias, also with spaces/hyphens removed
               ("front-end developer" == "frontend developer")
  2. exact   - same, after removing level words ("junior frontend developer")
  3. fuzzy   - token + character similarity over names and aliases
  4. semantic- optional Qdrant search (callable injected by the caller)
  5. otherwise ambiguous / unresolved -> G1 asks the learner to confirm

A wrong role means wrong target skills, so a match is accepted only when the score
is high AND clearly ahead of the next role. Close calls return `ambiguous` with the
candidate role IDs, which the backend turns into a clarification question.

Role data can come from datajson/job_roles.json (load_roles_from_json) or from the
Qdrant collection edumentor_job_roles (load_roles_from_qdrant); qdrant_semantic_search()
builds the optional step-4 search from the same collection.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Callable, Optional

from app.utils.skill_graph.catalogue import DATAJSON

ACCEPT_SCORE = 0.86     # fuzzy/semantic score needed to accept a match
ACCEPT_MARGIN = 0.06    # ...and lead over the second-best role
CANDIDATE_SCORE = 0.60  # roles at or above this are offered as clarification options
MAX_CANDIDATES = 4

LEVEL_WORDS = {
    "junior", "jr", "senior", "sr", "mid", "middle", "midlevel", "entry", "level", "intern",
    "trainee", "fresher", "graduate", "principal", "staff", "lead", "associate", "aspiring",
    "beginner", "experienced",
}
FILLER_WORDS = {"a", "an", "the", "as", "role", "position", "job", "career", "become", "be", "to", "work"}
# Generic head words: sharing only these does not make two role names related.
GENERIC_WORDS = {"developer", "engineer", "programmer", "specialist", "and", "of", "in", "for", "it"}
TOKEN_SYNONYMS = {"dev": "developer", "devs": "developer", "eng": "engineer", "engr": "engineer",
                  "admin": "administrator", "mgr": "manager", "programmer": "programmer",
                  # a career field names its primary role: "data science" -> "data scientist"
                  "engineering": "engineer", "development": "developer", "science": "scientist",
                  "analytics": "analyst", "testing": "tester"}
HEAD_SYNONYMS = {"developer": "developer", "engineer": "developer", "programmer": "developer"}


@dataclass(frozen=True)
class RoleEntry:
    role_id: int
    role_name: str
    aliases: tuple[str, ...] = ()


@dataclass
class RoleMatch:
    raw_name: str
    role_id: Optional[int] = None
    canonical_name: Optional[str] = None
    match_method: Optional[str] = None      # exact | alias | fuzzy | semantic
    match_score: Optional[float] = None     # raw similarity, not a probability
    resolution_status: str = "unresolved"   # matched | ambiguous | unresolved
    candidate_ids: list[int] = field(default_factory=list)

    def to_normalized_target_role(self) -> dict:
        """Fields of NormalizedTargetRole (learner_analyzer/schemas.py)."""
        return {
            "raw_name": self.raw_name, "canonical_name": self.canonical_name, "role_id": self.role_id,
            "match_method": self.match_method, "match_score": self.match_score,
            "resolution_status": self.resolution_status,
        }


# Vietnamese role heads (accents already removed) -> English head word.
# "lap trinh vien backend" -> "backend developer", "ky su du lieu" -> "du lieu engineer".
VI_HEADS = [
    ("lap trinh vien", "developer"), ("nha phat trien", "developer"), ("ky su", "engineer"),
    ("chuyen vien", "specialist"), ("nhan vien", "specialist"), ("quan tri vien", "administrator"),
]
VI_FILLERS = {"lam", "tro", "thanh", "muon", "mot", "vi", "tri", "nghe", "cong", "viec"}


def strip_accents(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def tokens(text: str) -> list[str]:
    text = strip_accents(text).lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9+#]+", " ", text)  # keep + and # (C++, C#)
    text = " " + " ".join(text.split()) + " "
    # "mảng AI" / "lĩnh vực data" / "ngành IT": a leading field marker, not a word of the role.
    # (Needed because "mảng" (area) and "mạng" (network) are both "mang" without accents.)
    for marker in ("mang", "linh vuc", "nganh"):
        if text.startswith(" " + marker + " ") and len(text.split()) > len(marker.split()):
            text = text[len(marker) + 1:]
            break
    head = None
    for vi, en in VI_HEADS:  # Vietnamese head comes first; move it to the end like English
        if text.startswith(" " + vi + " "):
            text, head = text[len(vi) + 1:], en
            break
    out = []
    for t in text.split():
        t = TOKEN_SYNONYMS.get(t, t)
        if t not in FILLER_WORDS and t not in VI_FILLERS:
            out.append(t)
    if head:
        out.append(head)
    elif len(out) > 1 and out[0] == "developer":  # "dev backend" -> "backend developer"
        out = out[1:] + ["developer"]
    return out


def strip_levels(toks: list[str]) -> list[str]:
    kept = [t for t in toks if t not in LEVEL_WORDS]
    return kept or toks


def compact(toks: list[str]) -> str:
    return "".join(toks)


def _dice(a: list[str], b: list[str]) -> float:
    sa = {HEAD_SYNONYMS.get(t, t) for t in a}
    sb = {HEAD_SYNONYMS.get(t, t) for t in b}
    return 2 * len(sa & sb) / (len(sa) + len(sb)) if sa and sb else 0.0


def similarity(a: list[str], b: list[str]) -> float:
    return max(_dice(a, b), SequenceMatcher(None, " ".join(a), " ".join(b)).ratio())


def shares_meaningful_token(a: list[str], b: list[str]) -> bool:
    """True if a and b share a non-generic word, tolerating typos ("andriod" ~ "android")."""
    ka = [t for t in a if t not in GENERIC_WORDS]
    kb = [t for t in b if t not in GENERIC_WORDS]
    return any(x == y or (len(x) > 3 and SequenceMatcher(None, x, y).ratio() >= 0.8) for x in ka for y in kb)


class RoleMatcher:
    def __init__(self, roles: list[RoleEntry],
                 semantic_search: Optional[Callable[[str], list[tuple[int, float]]]] = None):
        """semantic_search(text) -> [(role_id, score), ...] best first (e.g. a Qdrant query)."""
        self.roles = {r.role_id: r for r in roles}
        self.semantic_search = semantic_search
        self._exact: dict[str, dict[int, str]] = {}   # compact key -> {role_id: method}
        self._strings: list[tuple[int, list[str]]] = []
        for r in roles:
            for text, method in [(r.role_name, "exact")] + [(a, "alias") for a in r.aliases]:
                toks = tokens(text)
                self._exact.setdefault(compact(toks), {}).setdefault(r.role_id, method)
                self._strings.append((r.role_id, toks))

    def _result(self, raw: str, role_id: int, method: str, score: Optional[float]) -> RoleMatch:
        return RoleMatch(raw, role_id, self.roles[role_id].role_name, method, score, "matched")

    def match(self, raw_name: Optional[str]) -> RoleMatch:
        if not raw_name or not raw_name.strip():
            return RoleMatch(raw_name or "", resolution_status="unresolved")
        toks = tokens(raw_name)
        if not toks:
            return RoleMatch(raw_name, resolution_status="unresolved")

        # 1-2. exact on name/alias, then without level words
        for key in (compact(toks), compact(strip_levels(toks))):
            hits = self._exact.get(key)
            if hits and len(hits) == 1:
                (rid, method), = hits.items()
                return self._result(raw_name, rid, method, None)
            if hits:
                return RoleMatch(raw_name, resolution_status="ambiguous", candidate_ids=sorted(hits))

        # 3. fuzzy (best string per role)
        query = strip_levels(toks)
        best: dict[int, float] = {}
        for rid, s in self._strings:
            if not shares_meaningful_token(query, s):
                continue  # character similarity alone is noise on short names
            sc = similarity(query, s)
            if sc > best.get(rid, 0.0):
                best[rid] = sc
        ranked = sorted(best.items(), key=lambda kv: -kv[1])
        top_id, top = ranked[0] if ranked else (None, 0.0)
        second = ranked[1][1] if len(ranked) > 1 else 0.0
        if ranked and top >= ACCEPT_SCORE and top - second >= ACCEPT_MARGIN:
            return self._result(raw_name, top_id, "fuzzy", round(top, 3))

        # 4. semantic (optional)
        if self.semantic_search:
            sem = [(rid, sc) for rid, sc in self.semantic_search(raw_name) if rid in self.roles]
            if sem:
                s_top_id, s_top = sem[0]
                s_second = sem[1][1] if len(sem) > 1 else 0.0
                if s_top >= ACCEPT_SCORE and s_top - s_second >= ACCEPT_MARGIN:
                    return self._result(raw_name, s_top_id, "semantic", round(s_top, 3))

        # 5. clarification candidates
        cands = [rid for rid, sc in ranked if sc >= CANDIDATE_SCORE][:MAX_CANDIDATES]
        if cands:
            # single candidate -> the backend asks a yes/no confirmation; several -> a choice question
            return RoleMatch(raw_name, match_score=round(top, 3), resolution_status="ambiguous", candidate_ids=cands)
        return RoleMatch(raw_name, resolution_status="unresolved")


def load_roles_from_json(path: Path = DATAJSON / "job_roles.json") -> list[RoleEntry]:
    data = json.loads(path.read_text(encoding="utf-8"))["roles"]
    return [RoleEntry(r["id"], r["name"], tuple(r.get("aliases", []))) for r in data]


def load_roles_from_qdrant(role_q=None) -> list[RoleEntry]:
    """Read active roles and their aliases from the Qdrant collection edumentor_job_roles."""
    if role_q is None:
        from app.services.qdrant_service import qdrant_role_service as role_q
    aliases: dict[int, list[str]] = {}
    for a in role_q.list_aliases():
        aliases.setdefault(a["role_id"], []).append(a["alias"])
    return [RoleEntry(r["role_id"], r["role_name"], tuple(aliases.get(r["role_id"], [])))
            for r in role_q.list_roles(active_only=True)]


def qdrant_semantic_search(role_q=None, embed=None, limit: int = 10) -> Callable[[str], list[tuple[int, float]]]:
    """Build the semantic_search callable for RoleMatcher from Qdrant (role names + aliases)."""
    if role_q is None:
        from app.services.qdrant_service import qdrant_role_service as role_q
    if embed is None:
        from app.core.embedding_model import generate_embedding_skills_name as embed

    def search(text: str) -> list[tuple[int, float]]:
        return role_q.search_roles(embed([text])[0], limit=limit)

    return search
