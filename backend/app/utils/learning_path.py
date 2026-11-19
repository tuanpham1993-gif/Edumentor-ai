from collections import defaultdict
from app.models.learning_path import LearningPathEdge

DIRECTED_RELATIONS = {"prerequisite", "extension"}

def would_create_cycle(
    db,
    path_id: int,
    from_skill_id: int,
    to_skill_id: int,
    exclude_edge: tuple[int, int] | None = None,
) -> bool:

    if from_skill_id == to_skill_id:
        return True

    edges = db.query(LearningPathEdge).filter(
        LearningPathEdge.path_id == path_id,
        LearningPathEdge.relation_type.in_(DIRECTED_RELATIONS),
    ).all()

    graph = defaultdict(list)

    for edge in edges:
        current_pair = (
            edge.from_skill_id,
            edge.to_skill_id,
        )

        # Ignore the old edge when validating an update.
        if exclude_edge == current_pair:
            continue

        graph[edge.from_skill_id].append(edge.to_skill_id)

    stack = [to_skill_id]
    visited = set()

    while stack:
        current = stack.pop()

        if current == from_skill_id:
            return True

        if current in visited:
            continue

        visited.add(current)
        stack.extend(graph[current])

    return False