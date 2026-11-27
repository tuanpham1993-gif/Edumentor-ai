"""Build the personalized learning graph for an AI learning path (Phase 6 + 7).

Pure functions: no database, no Qdrant. The service
(app/services/learning_path_generation_v2_service.py) loads the data and calls them.

1. select_targets      final nodes of the graph
     - career : candidate skills of the matched job role (Qdrant edumentor_job_roles),
                plus target technologies that are nodes of the skill graph
     - project: every target technology that is a node of the skill graph is a final node;
                the role's candidates are used only when no technology could be linked
     A technology outside the skill graph is reported, not added (it would be a lone node).
2. retrieve            backward prerequisite walk over skill_relation (graph_ops). Iterative BFS
                       with a visited set, so a cycle in the data cannot loop forever; depth,
                       node and edge limits stop runaway graphs.
3. break_cycles        drop back edges (if the data has a cycle) so layering is well defined.
4. personalize + trim  known skills = explicit skills from the G1 output
                       (explicitly_reported, user_provided_structured; never inferred_from_context)
                       + skills marked "known" in the learner's account profile (user_skills).
                       A known skill also satisfies its prerequisite ancestors (closure over the
                       full graph, Phase 7 §7.2.2). The path keeps:
                         - every skill still needed to reach the targets, and
                         - the known skills directly in front of them, as context ("you start here").
                       Deeper known ancestors are trimmed.
5. layer               longest-path layering (prerequisites first) for the React Flow layout.

Node states: known (learner has it) | satisfied (implied by a known skill) | learning
(user_skills status "learning") | eligible (all prerequisites satisfied) | locked.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field

from app.utils.skill_graph.graph_ops import retrieve_prerequisite_graph, trim_by_known_skills

GENERATOR_VERSION = "lp2-v1"
EXPLICIT_EVIDENCE = {"explicitly_reported", "user_provided_structured"}


@dataclass
class TargetSelection:
    targets: list[tuple[int, str]] = field(default_factory=list)   # (skill_id, "role" | "technology")
    outside_graph: list[int] = field(default_factory=list)          # linked technologies not in the graph
    warnings: list[str] = field(default_factory=list)

    @property
    def target_ids(self) -> list[int]:
        return [sid for sid, _ in self.targets]


def select_targets(goal_type: str, role_candidate_ids: list[int], technology_ids: list[int],
                   graph_nodes: set[int]) -> TargetSelection:
    sel = TargetSelection()
    seen: set[int] = set()

    def add(sid: int, source: str) -> None:
        if sid not in seen:
            seen.add(sid)
            sel.targets.append((sid, source))

    techs_in_graph = []
    for sid in dict.fromkeys(technology_ids):
        (techs_in_graph if sid in graph_nodes else sel.outside_graph).append(sid)
    if sel.outside_graph:
        sel.warnings.append(f"{len(sel.outside_graph)} target technologies have no prerequisite data "
                            f"and were not added as targets.")

    if goal_type == "project":
        for sid in techs_in_graph:
            add(sid, "technology")
        if not sel.targets and role_candidate_ids:
            sel.warnings.append("No target technology could be placed in the skill graph; "
                                "the job role's skills were used instead.")
            for sid in role_candidate_ids:
                add(sid, "role")
    else:
        for sid in role_candidate_ids:
            add(sid, "role")
        for sid in techs_in_graph:
            add(sid, "technology")
    return sel


def explicit_known_ids(skill_profiles: list[tuple[int | None, str]]) -> set[int]:
    """skill ids whose evidence may satisfy prerequisites: [(skill_id, evidence_type)]."""
    return {sid for sid, evidence in skill_profiles if sid is not None and evidence in EXPLICIT_EVIDENCE}


def break_cycles(nodes: list[int], edges: list[tuple[int, int]]) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Remove back edges found by an iterative DFS. Returns (acyclic_edges, removed_edges)."""
    succ: dict[int, list[int]] = defaultdict(list)
    for a, b in edges:
        succ[a].append(b)
    WHITE, GREY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}
    removed: set[tuple[int, int]] = set()
    for root in sorted(nodes):
        if color[root] != WHITE:
            continue
        color[root] = GREY
        stack = [(root, iter(sorted(succ[root])))]
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                color[node] = BLACK
                stack.pop()
            elif color.get(nxt, BLACK) == GREY:
                removed.add((node, nxt))
            elif color.get(nxt) == WHITE:
                color[nxt] = GREY
                stack.append((nxt, iter(sorted(succ[nxt]))))
    return [e for e in edges if e not in removed], sorted(removed)


def longest_path_layers(nodes: list[int], edges: list[tuple[int, int]]) -> dict[int, int]:
    """layer(n) = 0 for sources, else 1 + max(layer of prerequisites). Edges must be acyclic."""
    preds: dict[int, list[int]] = defaultdict(list)
    succ: dict[int, list[int]] = defaultdict(list)
    indeg = {n: 0 for n in nodes}
    for a, b in edges:
        preds[b].append(a)
        succ[a].append(b)
        indeg[b] += 1
    layer = {}
    queue = deque(sorted(n for n in nodes if indeg[n] == 0))
    while queue:
        n = queue.popleft()
        layer[n] = max((layer[p] + 1 for p in preds[n]), default=0)
        for s in succ[n]:
            indeg[s] -= 1
            if indeg[s] == 0:
                queue.append(s)
    for n in nodes:   # only reachable if edges were not acyclic; keep every node placed
        layer.setdefault(n, 0)
    return layer


def build_personalized_graph(target_ids: list[int], prereq_idx: dict[int, list[int]],
                             known_ids: set[int], learning_ids: set[int] | None = None) -> dict:
    """Retrieve, personalize and trim. Returns nodes/edges/layer ready for the service to name."""
    learning_ids = (learning_ids or set()) - known_ids
    full = retrieve_prerequisite_graph(target_ids, prereq_idx)
    edges, removed = break_cycles(full["nodes"], [tuple(e) for e in full["edges"]])
    full = {**full, "edges": edges}
    warnings = [f"retrieval stopped at skill {w['skill_id']} ({w['reason']})" for w in full["retrieval_warnings"]]
    if removed:
        warnings.append(f"{len(removed)} cyclic prerequisite relations were ignored: {removed}")

    trim = trim_by_known_skills(full, known_ids, known_implies_prerequisites=True, prereq_idx=prereq_idx)
    satisfied = set(trim["satisfied_skill_ids"])
    remaining = set(trim["remaining_skill_ids"])
    eligible = set(trim["eligible_now"])
    targets = list(dict.fromkeys(target_ids))

    # Targets always stay visible (a known target is shown as "known").
    context = {a for a, b in edges if b in remaining and a in satisfied}
    keep = remaining | context | set(targets)
    kept_edges = sorted((a, b) for a, b in edges if a in keep and b in keep)
    kept_nodes = sorted(keep)
    layers = longest_path_layers(kept_nodes, kept_edges)

    def state(n: int) -> str:
        if n in satisfied:
            return "known" if n in known_ids else "satisfied"
        if n in learning_ids:
            return "learning"
        return "eligible" if n in eligible else "locked"

    target_set = set(targets)
    nodes = [{"skill_id": n, "is_target": n in target_set, "state": state(n), "layer": layers[n]} for n in kept_nodes]
    layer_map: dict[int, list[int]] = defaultdict(list)
    for n in kept_nodes:
        layer_map[layers[n]].append(n)
    return {
        "target_skill_ids": targets,
        "nodes": nodes,
        "edges": kept_edges,
        "layer": dict(sorted(layer_map.items())),
        "retrieval_status": full["retrieval_status"],
        "warnings": warnings,
        "stats": {
            "full_graph_nodes": len(full["nodes"]),
            "kept_nodes": len(kept_nodes),
            "known_or_satisfied": len(satisfied),
            "trimmed_nodes": len(full["nodes"]) - len(kept_nodes),
            "remaining_to_learn": len(remaining),
            "eligible_now": len(eligible),
            "all_targets_satisfied": trim["all_targets_satisfied"],
        },
    }
