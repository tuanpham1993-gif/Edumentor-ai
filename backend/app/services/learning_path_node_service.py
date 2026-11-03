from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload
from typing import Literal

from app.models.learning_path import (
    LearningPath, LearningPathNode, LearningPathEdge
)
from app.models import Skills
from app.services.learning_path_edge_service import add_edge, delete_edge

RelationType = Literal["prerequisite", "related", "extension"]

def get_detail_node(db:Session, path_id: int, skill_id: int):
    query = select(LearningPathNode).options(joinedload(LearningPathNode.skill)).where(
        LearningPathNode.path_id == path_id,
        LearningPathNode.skill_id == skill_id,
    )
    return db.scalar(query)

def add_new_learning_path_nodes(db: Session, path_id: int, nodes: list[dict]) -> list[LearningPathNode]:
    if not nodes: raise ValueError("A learning path must contain at least one node.")
    skill_ids = [node["skill_id"] for node in nodes]
    if len(skill_ids) != len(set(skill_ids)): raise ValueError("Duplicate skills found in the learning path.")
    # 3. Check whether all skill IDs exist in the Skills table.
    existing_skill_ids = set(db.scalars(select(Skills.skill_id).where(Skills.skill_id.in_(skill_ids))).all())

    missing_skill_ids = set(skill_ids) - existing_skill_ids

    if missing_skill_ids:
        raise ValueError(f"Skills not found: {sorted(missing_skill_ids)}")

    # 4. Convert JSON node data into ORM objects.
    new_nodes = []

    for node in nodes:
        new_node = LearningPathNode(
            path_id=path_id,
            skill_id=node["skill_id"],
            node_role=node.get("node_role"),
            is_target=node.get("is_target", False),
            added_by="system",
            is_required=node.get("is_required", False),
            display_order=node["display_order"],
        )

        new_nodes.append(new_node)

    # 5. Add all nodes to the current transaction.
    db.add_all(new_nodes)
    db.flush()
    return new_nodes

def add_learning_path_node(
    db: Session, path_id: int, student_id: int,
    skill_id: int, #skill want to insert
    insert_before_skill_id: int, #node before it
    relation_to_current: RelationType | None = None,
    relation_to_next: RelationType | None = None,
    node_role: RelationType | None = None,
    is_target: bool = False, is_required: bool = False,
) -> LearningPathNode:
    try:
        path_exists = db.scalar(select(LearningPath.record_id).where(
            LearningPath.record_id == path_id,
            LearningPath.student_id == student_id,
        ))
        if path_exists is None: raise ValueError("Learning path not found or access denied.")

        skill_exists = db.scalar(select(Skills.skill_id).where(Skills.skill_id == skill_id))
        if skill_exists is None:
            raise ValueError("Skill not found.")

        # 3. Load the nodes in this path, ordered for display.
        nodes = list(
            db.scalars(
                select(LearningPathNode).where(
                    LearningPathNode.path_id == path_id).order_by(
                        LearningPathNode.display_order, LearningPathNode.skill_id)).all())

        # 4. Find the node before which the new skill will be inserted.
        anchor_index = next((i for i, node in enumerate(nodes) if node.skill_id == insert_before_skill_id), None)

        if anchor_index is None:
            raise ValueError("The selected insertion node is not in this path.")

        # 5. Prevent duplicate skills in the same path.
        if any(node.skill_id == skill_id for node in nodes):
            raise ValueError("This skill already exists in the learning path.")

        # 6. Find the next node after the selected anchor.
        next_node = (nodes[anchor_index + 1] if anchor_index + 1 < len(nodes) else None) 
        # Suppose Length of node is 4 => anchor is 3 mean that it in last node. 
        # if anchor is 2 mean insert between 2 and 3 => nextNode = node[3]
        anchor_node = nodes[anchor_index] #insert_before_skill_id
        previous_node = (nodes[anchor_index - 1] if anchor_index > 0 else None) #before insert_before_skill_id

        # 7. Calculate the new display order.
        if previous_node is None: 
            new_order = anchor_node.display_order - 1000
        #Suppose that insert_before_skill_id = 0 and it order is 1000 and new skill will be insert between 0 and 1.
        #Then this case previous will be None and the insert_before_skill_id will be derank order from 1000 -> 0

        elif (anchor_node.display_order - previous_node.display_order) > 1:
            new_order = ( previous_node.display_order + anchor_node.display_order ) // 2

        else:
            # No integer gap remains: renumber existing nodes.
            for index, node in enumerate(nodes, start=1):
                node.display_order = index * 1000
            db.flush()

            # Recalculate the insertion position.
            anchor_node = nodes[anchor_index]
            previous_node = (nodes[anchor_index - 1] if anchor_index > 0 else None)

            if previous_node is None: new_order = anchor_node.display_order - 1000
            else: new_order = ( previous_node.display_order + anchor_node.display_order) // 2

        # 8. Validate node_role.
        valid_roles = {"prerequisite", "related", "extension"}
        if node_role is not None and node_role not in valid_roles: raise ValueError("Invalid node_role.")

        # 9. Create the user-added node.
        new_node = LearningPathNode(
            path_id=path_id, skill_id=skill_id,
            node_role=node_role, is_target=is_target,
            added_by="user", is_required=is_required,
            display_order=new_order,
        )

        db.add(new_node)
        db.flush()

        # 10. Create an edge based on the relationship selected.
        add_edge(db, path_id, anchor_node.skill_id, skill_id, relation_to_current)
        if next_node is not None:
            add_edge(db, path_id, next_node.skill_id, skill_id, relation_to_next)
        db.commit()
        db.refresh(new_node)
        return new_node
    
    except Exception:
        db.rollback()
        raise

def update_learning_path_node( db: Session,
    path_id: int, student_id: int,
    skill_id: int, node_role: RelationType | None = None,
    passed_test: bool | None = None) -> LearningPathNode:
    try:
        # 1. Check that the learning path belongs to this student.
        path_exists = db.scalar(
            select(LearningPath.record_id).where(
                LearningPath.record_id == path_id,
                LearningPath.student_id == student_id
            ))

        if path_exists is None: raise ValueError("Learning path not found or access denied.")

        # 2. Find the node to update.
        node = db.scalar(
            select(LearningPathNode).where(
                LearningPathNode.path_id == path_id,
                LearningPathNode.skill_id == skill_id,
            ))

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

def delete_learning_path_node(
    db: Session, path_id: int,
    student_id: int, skill_id: int) -> None:
    try:
        # 1. Check that the learning path belongs to this student.
        path_exists = db.scalar(
            select(LearningPath.record_id).where(
                LearningPath.record_id == path_id,
                LearningPath.student_id == student_id,
            ))

        if path_exists is None: raise ValueError("Learning path not found or access denied.")

        # 2. Find the node to delete.
        node = db.scalar(
            select(LearningPathNode).where(
                LearningPathNode.path_id == path_id, 
                LearningPathNode.skill_id == skill_id))

        if node is None:
            raise ValueError("Learning path node not found.")

        # 3. Find all edges connected to this node.
        edges = db.scalars(
            select(LearningPathEdge).where(
                LearningPathEdge.path_id == path_id,
                or_( LearningPathEdge.from_skill_id == skill_id, 
                    LearningPathEdge.to_skill_id == skill_id))).all()

        # 4. Delete each connected edge using the existing helper.
        for edge in edges:
            delete_edge(db=db, path_id=path_id,
                from_skill_id=edge.from_skill_id,
                to_skill_id=edge.to_skill_id)

        # 5. Delete the node.
        db.delete(node)

        # 6. Commit all deletions together.
        db.commit()

    except Exception:
        db.rollback()
        raise