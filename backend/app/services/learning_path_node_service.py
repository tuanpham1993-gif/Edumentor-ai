from sqlalchemy import Select, func, or_, select, case
from sqlalchemy.orm import Session
from typing import Literal
from app.schemas.learning_path import (
    LearningPathCreate, LearningPathResponse,
    LearningPathNodeCreate, LearningPathNodeResponse,
    LearningPathEdgeCreate, LearningPathEdgeResponse)

from app.models.learning_path import (
    LearningPath, LearningPathNode, LearningPathEdge
)
from app.models import Skills
from app.services.learning_path_edge_service import add_edge

RelationType = Literal["prerequisite", "related", "extension"]
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