"""Resolve graph_source.py, validate it, and write the JSON outputs.

Run from Edumentor-ai/backend:
    python -m app.utils.skill_graph.build_skill_graph

Writes:
    datajson/skill_relation.json          (same format as the old file)
    datajson/role_candidate_skills.json   (role -> candidate target skills)
Exits with code 1 and lists every problem if any rule fails; nothing is written then.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict

from app.utils.skill_graph import graph_source as src
from app.utils.skill_graph.catalogue import DATAJSON, Catalogue

MAX_DEPTH_TO_ROOT = 8


def build(cat: Catalogue) -> tuple[list[dict], list[dict], list[str], dict]:
    errors: list[str] = []
    resolved: dict[str, int] = {}

    def rid(name: str) -> int | None:
        if name in resolved:
            return resolved[name]
        try:
            sid = cat.resolve_skill(name)
        except KeyError as exc:
            errors.append(str(exc))
            return None
        dup = cat.non_canonical_duplicate(sid)
        if dup is not None:
            errors.append(f"{name!r} -> {sid} is not canonical; use {cat.name_by_id[dup]!r} ({dup})")
        resolved[name] = sid
        return sid

    roots = {rid(n) for n in src.ROOTS}
    pairs: dict[tuple[int, int], str] = {}

    def add(frm: str, to: str, kind: str) -> None:
        a, b = rid(frm), rid(to)
        if a is None or b is None:
            return
        if a == b:
            errors.append(f"self-loop: {frm!r}")
            return
        if (a, b) in pairs:
            errors.append(f"duplicate pair {frm!r} -> {to!r} ({pairs[(a, b)]} and {kind})")
            return
        if kind == "related" and (b, a) in pairs:
            errors.append(f"related pair already linked in reverse: {frm!r} <-> {to!r} ({pairs[(b, a)]})")
            return
        pairs[(a, b)] = kind

    for child, parents in src.PREREQUISITES.items():
        for p in parents:
            add(p, child, "prerequisite")
    for a, b in src.EXTENSIONS:
        add(a, b, "extension")
    for a, b in src.RELATED:
        add(a, b, "related")

    prereq_parents: dict[int, set[int]] = defaultdict(set)
    nodes: set[int] = set(roots)
    for (a, b), kind in pairs.items():
        if kind == "prerequisite":
            prereq_parents[b].add(a)
        nodes.update((a, b))

    # Every non-root node has a prerequisite.
    for n in sorted(nodes):
        if n not in roots and not prereq_parents[n]:
            errors.append(f"no prerequisite (would be an unverified start): {cat.name_by_id[n]!r} ({n})")
    for r in roots:
        if prereq_parents[r]:
            errors.append(f"root has prerequisites: {cat.name_by_id[r]!r}")

    # Extension targets must have their own prerequisite path.
    for (a, b), kind in pairs.items():
        if kind == "extension" and not prereq_parents[b]:
            errors.append(f"extension target has no prerequisite: {cat.name_by_id[b]!r}")

    # DAG check + longest distance to a root.
    depth: dict[int, int] = {}
    state: dict[int, int] = {}

    def longest(n: int, path: list[int]) -> int:
        if state.get(n) == 2:
            return depth[n]
        if state.get(n) == 1:
            cyc = path[path.index(n):] + [n]
            errors.append("cycle: " + " -> ".join(cat.name_by_id[x] for x in cyc))
            return 0
        state[n] = 1
        d = 0 if not prereq_parents[n] else 1 + max(longest(p, path + [n]) for p in prereq_parents[n])
        state[n] = 2
        depth[n] = d
        return d

    for n in nodes:
        longest(n, [])
    for n, d in depth.items():
        if d > MAX_DEPTH_TO_ROOT:
            errors.append(f"depth {d} > {MAX_DEPTH_TO_ROOT}: {cat.name_by_id[n]!r}")

    # Role candidates.
    roles_out: list[dict] = []
    seen_roles: set[int] = set()
    for role_name, skills in src.ROLE_CANDIDATES.items():
        try:
            role_id = cat.resolve_role(role_name)
        except KeyError as exc:
            errors.append(str(exc))
            continue
        if role_id in seen_roles:
            errors.append(f"role listed twice: {role_name!r}")
        seen_roles.add(role_id)
        cands = []
        for s in skills:
            sid = rid(s)
            if sid is None:
                continue
            if sid not in nodes:
                errors.append(f"candidate not in graph: {role_name!r} -> {s!r}")
            if sid in roots:
                errors.append(f"candidate is a root: {role_name!r} -> {s!r}")
            if any(c["skill_id"] == sid for c in cands):
                errors.append(f"duplicate candidate: {role_name!r} -> {s!r}")
            cands.append({"skill_id": sid, "skill": cat.name_by_id[sid]})
        roles_out.append({"role_id": role_id, "role_name": cat.role_name_by_id[role_id], "candidate_skills": cands})
    missing_roles = sorted(set(cat.role_name_by_id) - seen_roles)
    for r in missing_roles:
        errors.append(f"role without candidates: {cat.role_name_by_id[r]!r} ({r})")

    relations = [
        {
            "from_skill_id": a, "to_skill_id": b,
            "from_skill_name": cat.name_by_id[a], "to_skill_name": cat.name_by_id[b],
            "relation_type": kind,
        }
        for (a, b), kind in sorted(pairs.items(), key=lambda kv: (kv[1], kv[0]))
    ]
    roles_out.sort(key=lambda r: r["role_id"])
    stats = {
        "nodes": len(nodes),
        "roots": sorted(cat.name_by_id[r] for r in roots),
        "prerequisite": sum(1 for k in pairs.values() if k == "prerequisite"),
        "extension": sum(1 for k in pairs.values() if k == "extension"),
        "related": sum(1 for k in pairs.values() if k == "related"),
        "max_depth_to_root": max(depth.values()) if depth else 0,
        "roles": len(roles_out),
    }
    return relations, roles_out, errors, stats


def main() -> int:
    cat = Catalogue()
    relations, roles, errors, stats = build(cat)
    if errors:
        print(f"{len(errors)} problem(s); nothing written:")
        for e in errors:
            print("  -", e)
        return 1
    (DATAJSON / "skill_relation.json").write_text(json.dumps(relations, indent=2, ensure_ascii=False), encoding="utf-8")
    (DATAJSON / "role_candidate_skills.json").write_text(json.dumps(roles, indent=2, ensure_ascii=False), encoding="utf-8")
    print("OK", json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
