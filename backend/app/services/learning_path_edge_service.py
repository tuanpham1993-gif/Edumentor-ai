from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Literal
from app.models.learning_path import LearningPathEdge, LearningPathNode, LearningPath
from app.utils.learning_path import *

RelationType = Literal["prerequisite", "related", "extension"]

def add_new_learning_path_edges(db: Session, path_id: int, edges: list[dict],nodes: list[dict],) -> list[LearningPathEdge]:
    valid_relation_types = { "prerequisite", "related", "extension",}

    # 1. Get all skill IDs belonging to this submitted path.
    path_skill_ids = {node["skill_id"] for node in nodes}

    # 2. Validate and prepare edge records.
    new_edges = []
    seen_edges = set()

    for edge in edges:
        from_skill_id = edge["from_skill_id"]
        to_skill_id = edge["to_skill_id"]
        relation_type = edge["relation_type"]

        # Both endpoints must exist in the submitted nodes.
        if (from_skill_id not in path_skill_ids or to_skill_id not in path_skill_ids):
            raise ValueError(
                f"Edge references a skill outside the learning path: "
                f"{from_skill_id} -> {to_skill_id}"
            )

        # Prevent an edge connecting a skill to itself.
        if from_skill_id == to_skill_id: raise ValueError("A skill cannot have an edge to itself.")

        # Validate relationship type.
        if relation_type not in valid_relation_types:
            raise ValueError(f"Invalid relation type: {relation_type}")

        # Prevent duplicate directed edges.
        edge_pair = (from_skill_id, to_skill_id)
        if edge_pair in seen_edges: raise ValueError(f"Duplicate edge found: {from_skill_id} -> {to_skill_id}")
        seen_edges.add(edge_pair)

        new_edge = LearningPathEdge(
            path_id=path_id, from_skill_id=from_skill_id,
            to_skill_id=to_skill_id, relation_type=relation_type,
        )

        new_edges.append(new_edge)

    # 3. Add all edges to the current transaction.
    db.add_all(new_edges)
    db.flush()

    return new_edges

def add_edge(db: Session,
             path_id: int, 
             target_skill_id: int, 
             skill_id: int, 
             relation_type: RelationType | None) -> None:
    
    if relation_type is None: return
    if relation_type == "extension":
        # The new skill extends the existing skill.
        from_skill_id = target_skill_id
        to_skill_id = skill_id
    else:
        from_skill_id = skill_id
        to_skill_id = target_skill_id
        if relation_type in DIRECTED_RELATIONS:
            if would_create_cycle(
                db=db,
                path_id=path_id,
                from_skill_id=from_skill_id,
                to_skill_id=to_skill_id,):
                raise ValueError("This relationship would create a cycle in your learning path.")
        db.add(LearningPathEdge(path_id=path_id, from_skill_id=from_skill_id, to_skill_id=to_skill_id, relation_type=relation_type))

def update_edge(db: Session, path_id: int, 
                from_skill_id: int, to_skill_id: int, 
                relation_type: RelationType) -> LearningPathEdge:
    edge = db.scalar(
        select(LearningPathEdge).where(
            LearningPathEdge.path_id == path_id,
            LearningPathEdge.from_skill_id == from_skill_id,
            LearningPathEdge.to_skill_id == to_skill_id,
        ))
    if edge is None: raise ValueError("Learning path edge not found.")
    edge.relation_type = relation_type
    return edge


def delete_edge(
    db: Session, path_id: int,
    from_skill_id: int, to_skill_id: int) -> None:
    # 1. Find the edge.
    edge = db.scalar(
        select(LearningPathEdge).where(
            LearningPathEdge.path_id == path_id,
            LearningPathEdge.from_skill_id == from_skill_id,
            LearningPathEdge.to_skill_id == to_skill_id,
        )
    )

    # 2. Check whether the edge exists.
    if edge is None:
        raise ValueError("Learning path edge not found.")

    # 3. Mark the edge for deletion.
    db.delete(edge)

def add_learning_path_edge(
    db,
    path_id: int,
    student_id: int,
    from_skill_id: int,
    to_skill_id: int,
    relation_type: RelationType,
):
    try:
        # 1. Verify ownership of the learning path.
        path_exists = db.scalar(
            select(LearningPath.record_id).where(
                LearningPath.record_id == path_id,
                LearningPath.student_id == student_id,
            )
        )

        if path_exists is None:
            raise ValueError(
                "Learning path not found or access denied."
            )

        # 2. Verify that both skills belong to this path.
        path_nodes = list(
            db.scalars(
                select(LearningPathNode).where(
                    LearningPathNode.path_id == path_id,
                    LearningPathNode.skill_id.in_(
                        [from_skill_id, to_skill_id]
                    ),
                )
            ).all()
        )

        existing_ids = {node.skill_id for node in path_nodes}

        if from_skill_id not in existing_ids:
            raise ValueError("Source skill is not in this learning path.")

        if to_skill_id not in existing_ids:
            raise ValueError("Target skill is not in this learning path.")

        if from_skill_id == to_skill_id:
            raise ValueError("A skill cannot have a relationship with itself.")

        # 3. Prevent duplicate edges.
        existing_edge = db.scalar(
            select(LearningPathEdge).where(
                LearningPathEdge.path_id == path_id,
                LearningPathEdge.from_skill_id == from_skill_id,
                LearningPathEdge.to_skill_id == to_skill_id,
            )
        )

        if existing_edge is not None:
            raise ValueError("This relationship already exists.")

        # 4. Check directed cycles.
        if relation_type in DIRECTED_RELATIONS:
            if would_create_cycle(
                db,
                path_id,
                from_skill_id,
                to_skill_id,
            ):
                raise ValueError(
                    "This relationship would create a cycle."
                )

        # 5. Create the edge.
        new_edge = LearningPathEdge(
            path_id=path_id,
            from_skill_id=from_skill_id,
            to_skill_id=to_skill_id,
            relation_type=relation_type,
        )

        db.add(new_edge)
        db.commit()
        db.refresh(new_edge)

        return new_edge

    except Exception:
        db.rollback()
        raise

def update_learning_path_edge(
    db,
    path_id: int,
    student_id: int,
    from_skill_id: int,
    to_skill_id: int,
    relation_type: RelationType,
):
    try:
        # 1. Verify path ownership.
        path_exists = db.scalar(
            select(LearningPath.record_id).where(
                LearningPath.record_id == path_id,
                LearningPath.student_id == student_id,
            )
        )

        if path_exists is None:
            raise ValueError(
                "Learning path not found or access denied."
            )

        # 2. Find the existing edge.
        edge = db.scalar(
            select(LearningPathEdge).where(
                LearningPathEdge.path_id == path_id,
                LearningPathEdge.from_skill_id == from_skill_id,
                LearningPathEdge.to_skill_id == to_skill_id,
            )
        )

        if edge is None:
            raise ValueError("Learning path edge not found.")

        # 3. Check for a cycle using the new relationship type.
        if relation_type in DIRECTED_RELATIONS:
            if would_create_cycle(
                db=db,
                path_id=path_id,
                from_skill_id=from_skill_id,
                to_skill_id=to_skill_id,
                exclude_edge=(from_skill_id, to_skill_id),
            ):
                raise ValueError(
                    "This relationship would create a cycle."
                )

        # 4. Update the relationship.
        edge.relation_type = relation_type

        db.commit()
        db.refresh(edge)

        return edge

    except Exception:
        db.rollback()
        raise

def delete_learning_path_edge(
    db,
    path_id: int,
    student_id: int,
    from_skill_id: int,
    to_skill_id: int,
):
    try:
        path_exists = db.scalar(
            select(LearningPath.record_id).where(
                LearningPath.record_id == path_id,
                LearningPath.student_id == student_id,
            )
        )
        if path_exists is None:
            raise ValueError(
                "Learning path not found or access denied."
            )
        edge = db.scalar(
            select(LearningPathEdge).where(
                LearningPathEdge.path_id == path_id,
                LearningPathEdge.from_skill_id == from_skill_id,
                LearningPathEdge.to_skill_id == to_skill_id,
            )
        )
        if edge is None:
            raise ValueError("Learning path edge not found.")
        db.delete(edge)
        db.commit()
    except Exception:
        db.rollback()
        raise