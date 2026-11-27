"""Pure graph operations used by the simulator (and reusable by Phase 6/7 services).

- retrieve_prerequisite_graph: walk prerequisite edges backwards from target skills.
- trim_by_known_skills:        mark what the learner already knows and recompute
                               what is still needed / eligible. Nodes and edges are
                               never deleted (Phase 7 rule); "trimming" means the
                               known part is marked satisfied and drops out of the
                               remaining path.
"""
from __future__ import annotations

from collections import defaultdict, deque

MAX_PREREQUISITE_DEPTH = 8
MAX_GRAPH_NODES = 100
MAX_GRAPH_EDGES = 250


def prerequisite_index(relations: list[dict]) -> dict[int, list[int]]:
    """to_skill_id -> list of prerequisite from_skill_ids (prerequisite edges only)."""
    idx: dict[int, list[int]] = defaultdict(list)
    for r in relations:
        if r["relation_type"] == "prerequisite":
            idx[r["to_skill_id"]].append(r["from_skill_id"])
    return idx


def retrieve_prerequisite_graph(target_ids: list[int], prereq_idx: dict[int, list[int]]) -> dict:
    targets = list(dict.fromkeys(target_ids))
    depth: dict[int, int] = {t: 0 for t in targets}
    edges: set[tuple[int, int]] = set()
    queue = deque(targets)
    boundary: list[dict] = []
    while queue:
        node = queue.popleft()
        for pre in prereq_idx.get(node, []):
            edges.add((pre, node))
            if len(edges) > MAX_GRAPH_EDGES:
                boundary.append({"skill_id": node, "reason": "max_edges"})
                continue
            if pre not in depth:
                if depth[node] + 1 > MAX_PREREQUISITE_DEPTH:
                    boundary.append({"skill_id": node, "reason": "max_depth"})
                    continue
                if len(depth) >= MAX_GRAPH_NODES:
                    boundary.append({"skill_id": node, "reason": "max_nodes"})
                    continue
                depth[pre] = depth[node] + 1
                queue.append(pre)
            else:
                depth[pre] = min(depth[pre], depth[node] + 1)
    nodes = set(depth)
    has_incoming = {to for _, to in edges}
    starts = sorted(n for n in nodes if n not in has_incoming)
    intermediate = sorted(nodes - set(starts) - set(targets))
    return {
        "target_skill_ids": targets,
        "start_nodes": starts,
        "end_nodes": targets,
        "intermediate_nodes": intermediate,
        "nodes": sorted(nodes),
        "edges": sorted(edges),
        "max_depth": max(depth.values()) if depth else 0,
        "retrieval_status": "incomplete" if boundary else "complete",
        "retrieval_warnings": boundary,
    }


def expand_known_with_prerequisites(known_skill_ids: set[int], prereq_idx: dict[int, list[int]]) -> set[int]:
    """All prerequisite ancestors of the known skills, over the FULL graph.

    Needed because a known skill (e.g. Java) may be outside the role subgraph while
    its ancestors (e.g. Computer Programming) are inside it.
    """
    out = set(known_skill_ids)
    stack = list(known_skill_ids)
    while stack:
        for p in prereq_idx.get(stack.pop(), []):
            if p not in out:
                out.add(p)
                stack.append(p)
    return out


def trim_by_known_skills(graph: dict, known_skill_ids: set[int], known_implies_prerequisites: bool = True,
                         prereq_idx: dict[int, list[int]] | None = None) -> dict:
    """Mark known skills satisfied; return what remains to learn and what is eligible now.

    known_implies_prerequisites=True (closure, the chosen policy, Phase 7 §7.2.2):
      a known skill also satisfies all of its prerequisite ancestors in the FULL
      graph (knowing Kotlin implies Computer Programming). Requires prereq_idx.
    known_implies_prerequisites=False (strict): a known skill satisfies only itself.
      Kept for comparison and evaluation.
    Callers must pass only explicit evidence (explicitly_reported,
    user_provided_structured, assessed/completed per policy), never
    inferred_from_context skills.
    """
    nodes = set(graph["nodes"])
    preds: dict[int, set[int]] = defaultdict(set)
    for frm, to in graph["edges"]:
        preds[to].add(frm)
    if known_implies_prerequisites:
        if prereq_idx is None:
            raise ValueError("prereq_idx (full graph) is required for known_implies_prerequisites")
        known_skill_ids = expand_known_with_prerequisites(known_skill_ids, prereq_idx)
    satisfied = nodes & known_skill_ids

    # Needed = targets not satisfied, plus (recursively) unsatisfied prerequisites of needed nodes.
    needed: set[int] = set()
    stack = [t for t in graph["target_skill_ids"] if t not in satisfied]
    while stack:
        n = stack.pop()
        if n in needed:
            continue
        needed.add(n)
        stack.extend(p for p in preds[n] if p not in satisfied)

    eligible = sorted(n for n in needed if all(p in satisfied for p in preds[n]))
    return {
        "satisfied_skill_ids": sorted(satisfied),
        "remaining_skill_ids": sorted(needed),
        "eligible_now": eligible,
        "skipped_skill_ids": sorted(nodes - needed - satisfied),  # only needed for known skills
        "all_targets_satisfied": not needed,
    }
