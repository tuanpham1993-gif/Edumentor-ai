"""Simulate learning graphs for goal_type="project" (target technologies as targets).

Run from Edumentor-ai/backend:
    python -m app.utils.skill_graph.simulate_targets

1. Collect every goal.target_technologies name from datajson/LLM_dataset/g1/raw/batch_*.json.
2. Link each name like the backend skill linker does offline: exact / alias / case-insensitive
   (Catalogue.resolve_skill), then redirect a non-canonical duplicate to its canonical record.
3. For each linked technology: backward prerequisite retrieval over skill_relation.json and the
   checks used for roles (complete, depth <= 8, nodes <= 100, every start node is a ROOT).
4. For every project sample: all its technologies together -> one graph, same checks.
Writes datajson/target_tech_graph_report.json; exit 1 if a linked technology fails.
"""
from __future__ import annotations

import json
import sys
from collections import Counter

from app.utils.skill_graph import graph_source as src
from app.utils.skill_graph.catalogue import DATAJSON, Catalogue
from app.utils.skill_graph.graph_ops import (
    MAX_GRAPH_NODES,
    MAX_PREREQUISITE_DEPTH,
    prerequisite_index,
    retrieve_prerequisite_graph,
)


def link(cat: Catalogue, name: str) -> int | None:
    try:
        sid = cat.resolve_skill(name)
    except KeyError:
        return None
    return cat.non_canonical_duplicate(sid) or sid


def check(g: dict, roots: set[int], names: dict[int, str]) -> list[str]:
    problems = []
    if g["retrieval_status"] != "complete":
        problems.append(f"incomplete: {g['retrieval_warnings']}")
    if g["max_depth"] > MAX_PREREQUISITE_DEPTH:
        problems.append(f"depth {g['max_depth']}")
    if len(g["nodes"]) > MAX_GRAPH_NODES:
        problems.append(f"{len(g['nodes'])} nodes")
    bad = [names[s] for s in g["start_nodes"] if s not in roots]
    if bad:
        problems.append(f"non-root starts: {bad}")
    return problems


def ordered_path(g: dict, names: dict[int, str]) -> list[str]:
    """Nodes in learning order (prerequisites first)."""
    parents: dict[int, set[int]] = {n: set() for n in g["nodes"]}
    for frm, to in g["edges"]:
        parents[to].add(frm)
    order, done = [], set()
    while len(done) < len(parents):
        ready = sorted((n for n, ps in parents.items() if n not in done and ps <= done), key=lambda n: names[n])
        if not ready:
            break
        order += ready
        done |= set(ready)
    return [names[n] for n in order]


def main() -> int:
    cat = Catalogue()
    names = cat.name_by_id
    relations = json.loads((DATAJSON / "skill_relation.json").read_text(encoding="utf-8"))
    idx = prerequisite_index(relations)
    roots = {cat.resolve_skill(n) for n in src.ROOTS}
    graph_nodes = {r["from_skill_id"] for r in relations} | {r["to_skill_id"] for r in relations} | roots

    samples = []
    for p in sorted((DATAJSON / "LLM_dataset" / "g1" / "raw").glob("batch_*.json")):
        samples += json.loads(p.read_text(encoding="utf-8"))
    counts = Counter(t for s in samples for t in s["expected_output"]["goal"]["target_technologies"])

    tech_reports, unresolved, outside, failures = [], [], [], []
    for tech, n in counts.most_common():
        sid = link(cat, tech)
        if sid is None:
            unresolved.append({"name": tech, "count": n})
            continue
        if sid not in graph_nodes:
            outside.append({"name": tech, "skill_id": sid, "skill": names[sid], "count": n})
            continue
        g = retrieve_prerequisite_graph([sid], idx)
        problems = check(g, roots, names)
        rep = {"name": tech, "skill_id": sid, "skill": names[sid], "count": n, "nodes": len(g["nodes"]),
               "max_depth": g["max_depth"], "path": ordered_path(g, names),
               "status": "ok" if not problems else "fail", "problems": problems}
        tech_reports.append(rep)
        if problems:
            failures.append(rep)

    project_reports = []
    for s in samples:
        goal = s["expected_output"]["goal"]
        if goal["goal_type"] != "project":
            continue
        ids = [i for i in (link(cat, t) for t in goal["target_technologies"]) if i in graph_nodes]
        if not ids:
            project_reports.append({"sample_id": s["sample_id"], "technologies": goal["target_technologies"],
                                    "status": "no_linked_target"})
            continue
        g = retrieve_prerequisite_graph(ids, idx)
        problems = check(g, roots, names)
        project_reports.append({"sample_id": s["sample_id"], "technologies": goal["target_technologies"],
                                "targets": [names[i] for i in ids], "nodes": len(g["nodes"]),
                                "max_depth": g["max_depth"], "status": "ok" if not problems else "fail",
                                "problems": problems})

    report = {
        "distinct_technologies": len(counts),
        "linked_in_graph": len(tech_reports),
        "unresolved": unresolved,
        "linked_but_outside_graph": outside,
        "technology_failures": len(failures),
        "projects": {"total": len(project_reports),
                     "ok": sum(r["status"] == "ok" for r in project_reports),
                     "no_linked_target": sum(r["status"] == "no_linked_target" for r in project_reports),
                     "fail": sum(r["status"] == "fail" for r in project_reports)},
        "technologies": tech_reports,
        "project_samples": project_reports,
    }
    (DATAJSON / "target_tech_graph_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                                           encoding="utf-8")
    print(f"{len(counts)} distinct target technologies: {len(tech_reports)} linked into the graph, "
          f"{len(outside)} linked but outside the graph, {len(unresolved)} unresolved")
    print(f"technology graphs failing checks: {len(failures)}")
    print("project samples:", report["projects"])
    for r in failures:
        print("  FAIL", r["name"], r["problems"])
    if unresolved:
        print("unresolved:", [u["name"] for u in unresolved])
    if outside:
        print("outside graph:", [(o["name"], o["skill"]) for o in outside])
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
