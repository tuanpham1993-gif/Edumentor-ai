"""Simulate learning-graph generation for every role and for sample learners.

Run from Edumentor-ai/backend:
    python -m app.utils.skill_graph.simulate_roles

For every role in role_candidate_skills.json:
  candidates (final nodes) -> backward prerequisite retrieval -> checks:
  retrieval complete, depth <= 8, nodes <= 100, every start node is a ROOT.
For every sample in datajson/LLM_dataset/exampleDataset.json:
  target_role.raw_name -> role via role_matcher (exact, alias, fuzzy; Qdrant hook in production)
  -> candidates (+ linked target_technologies) -> graph -> trim with known skills.
Writes datajson/skill_graph_report.json and prints a summary. Exit 1 if any role fails.
"""
from __future__ import annotations

import json
import sys

from app.utils.skill_graph import graph_source as src
from app.utils.skill_graph.catalogue import DATAJSON, Catalogue
from app.utils.skill_graph.role_matcher import RoleMatcher, load_roles_from_json
from app.utils.skill_graph.graph_ops import (
    MAX_GRAPH_NODES,
    MAX_PREREQUISITE_DEPTH,
    prerequisite_index,
    retrieve_prerequisite_graph,
    trim_by_known_skills,
)


def main() -> int:
    cat = Catalogue()
    relations = json.loads((DATAJSON / "skill_relation.json").read_text(encoding="utf-8"))
    roles = json.loads((DATAJSON / "role_candidate_skills.json").read_text(encoding="utf-8"))
    idx = prerequisite_index(relations)
    roots = {cat.resolve_skill(n) for n in src.ROOTS}
    name = cat.name_by_id

    role_reports, failures = [], []
    for role in roles:
        targets = [c["skill_id"] for c in role["candidate_skills"]]
        g = retrieve_prerequisite_graph(targets, idx)
        problems = []
        if g["retrieval_status"] != "complete":
            problems.append(f"incomplete: {g['retrieval_warnings']}")
        if g["max_depth"] > MAX_PREREQUISITE_DEPTH:
            problems.append(f"depth {g['max_depth']}")
        if len(g["nodes"]) > MAX_GRAPH_NODES:
            problems.append(f"{len(g['nodes'])} nodes")
        bad_starts = [name[s] for s in g["start_nodes"] if s not in roots]
        if bad_starts:
            problems.append(f"non-root starts: {bad_starts}")
        rep = {
            "role_id": role["role_id"], "role_name": role["role_name"],
            "targets": len(targets), "nodes": len(g["nodes"]), "edges": len(g["edges"]),
            "max_depth": g["max_depth"], "start_nodes": [name[s] for s in g["start_nodes"]],
            "status": "ok" if not problems else "fail", "problems": problems,
        }
        role_reports.append(rep)
        if problems:
            failures.append(rep)

    # Sample learners from the G1 example dataset.
    samples = json.loads((DATAJSON / "LLM_dataset" / "exampleDataset.json").read_text(encoding="utf-8"))
    role_by_id = {r["role_id"]: r for r in roles}
    matcher = RoleMatcher(load_roles_from_json())
    sample_reports = []
    for s in samples:
        out = s["expected_output"]
        raw_role = out["goal"]["target_role"]["raw_name"]
        rep = {"sample_id": s["sample_id"], "raw_target_role": raw_role}
        match = matcher.match(raw_role)
        role_id = match.role_id
        rep["role_match"] = {"status": match.resolution_status, "method": match.match_method,
                             "candidates": [cat.role_name_by_id[c] for c in match.candidate_ids]}
        targets = [c["skill_id"] for c in role_by_id[role_id]["candidate_skills"]] if role_id else []
        graph_nodes = {r["from_skill_id"] for r in relations} | {r["to_skill_id"] for r in relations}
        extra, unresolved, outside = [], [], []
        for tech in out["goal"]["target_technologies"]:
            try:
                sid = cat.resolve_skill(tech)
            except KeyError:
                unresolved.append(tech)
                continue
            # A requested technology is a target only if it is a graph node;
            # otherwise it would become a start node with no prerequisites.
            (extra if sid in graph_nodes else outside).append(sid)
        rep["outside_graph_target_technologies"] = [name[x] for x in outside]
        targets = list(dict.fromkeys(targets + extra))
        known = set()
        for sp in out["skill_profiles"]:
            if sp["evidence_type"] == "inferred_from_context":
                continue  # inferred evidence never satisfies a prerequisite
            try:
                known.add(cat.resolve_skill(sp["skill_name"]))
            except KeyError:
                pass
        rep["matched_role"] = cat.role_name_by_id.get(role_id)
        rep["targets"] = [name[t] for t in targets]
        rep["unresolved_target_technologies"] = unresolved
        if not targets:
            rep["result"] = "no targets (role unresolved or project goal without linked technologies)"
        else:
            g = retrieve_prerequisite_graph(targets, idx)
            bad_starts = [name[x] for x in g["start_nodes"] if x not in roots]
            rep["graph_nodes"] = len(g["nodes"])
            rep["known_in_graph"] = [name[x] for x in sorted(set(g["nodes"]) & known)]
            if bad_starts:
                rep["problem_non_root_starts"] = bad_starts
            for mode, flag in (("strict", False), ("closure", True)):
                t = trim_by_known_skills(g, known, known_implies_prerequisites=flag, prereq_idx=idx)
                rep[mode] = {
                    "remaining_to_learn": len(t["remaining_skill_ids"]),
                    "eligible_now": [name[x] for x in t["eligible_now"]],
                }
        sample_reports.append(rep)

    report = {
        "limits": {"max_depth": MAX_PREREQUISITE_DEPTH, "max_nodes": MAX_GRAPH_NODES},
        "roles_total": len(role_reports),
        "roles_failed": len(failures),
        "largest_graphs": sorted(({"role": r["role_name"], "nodes": r["nodes"], "max_depth": r["max_depth"]} for r in role_reports), key=lambda x: -x["nodes"])[:10],
        "roles": role_reports,
        "sample_learners": sample_reports,
    }
    (DATAJSON / "skill_graph_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"roles: {len(role_reports)}  failed: {len(failures)}")
    for f in failures:
        print("  FAIL", f["role_name"], f["problems"])
    sizes = sorted(r["nodes"] for r in role_reports)
    print(f"graph size: min {sizes[0]}, median {sizes[len(sizes)//2]}, max {sizes[-1]} nodes; "
          f"max depth {max(r['max_depth'] for r in role_reports)}")
    for r in report["largest_graphs"][:5]:
        print("  largest:", r)
    print("\nsample learners:")
    for r in sample_reports:
        print(" ", json.dumps(r, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
