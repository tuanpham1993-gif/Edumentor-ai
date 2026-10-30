from sqlalchemy import Select, func, or_, select, case
from sqlalchemy.orm import Session
from typing import Literal
from app.schemas.learning_path import (
    LearningPathCreate, LearningPathResponse,
    LearningPathNodeCreate, LearningPathNodeResponse,
    LearningPathEdgeCreate, LearningPathEdgeResponse)
from app.models.learning_path import (LearningPath, LearningPathNode, LearningPathEdge)
from app.models import Skills

RelationType = Literal["prerequisite", "related", "extension"]
def add_edge(db: Session, path_id: int, target_skill_id: int, skill_id: int, relation_type: RelationType | None) -> None:
    if relation_type is None: return
    if relation_type == "extension":
        # The new skill extends the existing skill.
        from_skill_id = target_skill_id
        to_skill_id = skill_id
    else:
        # The new skill is a prerequisite of the target or the pair is marked as related.
        from_skill_id = skill_id
        to_skill_id = target_skill_id
    db.add(LearningPathEdge(path_id=path_id, from_skill_id=from_skill_id, to_skill_id=to_skill_id, relation_type=relation_type))


def update_learning_path_node(
    db: Session, path_id: int,
    student_id: int, skill_id: int,
    node_role: RelationType | None = None,
    passed_test: bool | None = None) -> LearningPathNode:
    try:
        # 1. Check that the learning path belongs to this student.
        path_exists = db.scalar(select(LearningPath.record_id).where(LearningPath.record_id == path_id, LearningPath.student_id == student_id))
        if path_exists is None: raise ValueError("Learning path not found or access denied.")

        # 2. Find the node to update.
        node = db.scalar(select(LearningPathNode).where(LearningPathNode.path_id == path_id, LearningPathNode.skill_id == skill_id,))
        if node is None: raise ValueError("Learning path node not found.")

        # 3. Update node_role if a new value was provided.
        if node_role is not None: node.node_role = node_role

        # 4. Update is_target only when a test result is provided.
        if passed_test is not None: node.is_target = passed_test

        db.commit()
        db.refresh(node)

        return node

    except Exception:
        db.rollback()
        raise