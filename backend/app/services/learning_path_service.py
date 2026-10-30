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

def build_learning_path_query(
        student_id: int,
        keyword: str | None = None,
        goal_type: Literal["career", "project"] | None = None, 
        status: Literal['completed', 'ongoing', 'abandoned'] | None = None
)->Select:
    select_query = select(LearningPath).where(LearningPath.student_id == student_id)
    if(keyword and keyword.strip()):
        pattern = f"%{keyword.strip()}%"
        select_query = select_query.where(LearningPath.original_query.ilike(pattern))
    if(goal_type):
        select_query = select_query.where(LearningPath.goal_type == goal_type)
    if(status):
        select_query = select_query.where(LearningPath.status == status)
    
    return select_query.order_by(LearningPath.record_id.desc())

def count_total_learning_path(select_query: Select):
    return select(func.count()).select_from(select_query.order_by(None).subquery())

def list_learning_path(db: Session, skip: int = 0, limit: int = 10, **filters) -> tuple[int, list[LearningPath]]:
    select_query = build_learning_path_query(**filters)
    #extracts one value from the query result
    total = db.execute(count_total_learning_path(select_query)).scalar_one()
    #lazy joined effect we use unique to filter out distinct row-> scalars take value out of each row return object
    #.all() return as list
    items = db.execute(select_query.offset(skip).limit(limit)).unique().scalars().all()
    return total, list(items)

def get_learning_path(db: Session, record_id: int) -> LearningPath | None:
    return db.get(LearningPath, record_id)

def get_learning_path_statistics(db: Session, student_id: int,) -> dict[str, int]:
    query = select(
        func.count(LearningPath.record_id).label("total"),
        func.count(case((LearningPath.status == "ongoing", 1))).label("ongoing"),
        func.count(case((LearningPath.status == "completed", 1))).label("completed"),
        ).where(LearningPath.student_id == student_id)
    result = db.execute(query).one()

    return {
        "total": result.total,
        "ongoing": result.ongoing,
        "completed": result.completed,
    }

def abandon_learning_path(db: Session, record_id: int):
    learning_path = get_learning_path(db, record_id)
    if learning_path is None: return None
    learning_path.status = "abandoned"
    db.commit()
    db.refresh(learning_path)

from app.models import Skills
RelationType = Literal["prerequisite", "related", "extension"]
def add_learning_path_node(
    db: Session, student_id: int,
    path_id: int, skill_id: int, #skill want to insert
    insert_before_skill_id: int, #node before it
    relation_to_current: RelationType | None = None,
    relation_to_next: RelationType | None = None,
    node_role: RelationType | None = None,
    is_target: bool = False, is_required: bool = False,
) -> LearningPathNode:
    try:
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
        if previous_node is None: new_order = anchor_node.display_order - 1000
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
            previous_node = (
                nodes[anchor_index - 1]
                if anchor_index > 0
                else None
            )

            if previous_node is None:
                new_order = anchor_node.display_order - 1000
            else:
                new_order = (
                    previous_node.display_order
                    + anchor_node.display_order
                ) // 2

        # 8. Validate node_role.
        valid_roles = {"prerequisite", "related", "extension"}

        if node_role is not None and node_role not in valid_roles:
            raise ValueError("Invalid node_role.")

        # 9. Create the user-added node.
        new_node = LearningPathNode(
            path_id=path_id,
            skill_id=skill_id,
            node_role=node_role,
            is_target=is_target,
            added_by="user",
            is_required=is_required,
            display_order=new_order,
        )

        db.add(new_node)
        db.flush()

        # 10. Create an edge based on the relationship selected.
        def add_edge(
            target_skill_id: int,
            relation_type: RelationType | None,
        ) -> None:
            if relation_type is None:
                return

            if relation_type == "extension":
                # The new skill extends the existing skill.
                from_skill_id = target_skill_id
                to_skill_id = skill_id
            else:
                # The new skill is a prerequisite of the target,
                # or the pair is marked as related.
                from_skill_id = skill_id
                to_skill_id = target_skill_id

            db.add(
                LearningPathEdge(
                    path_id=path_id,
                    from_skill_id=from_skill_id,
                    to_skill_id=to_skill_id,
                    relation_type=relation_type,
                )
            )

        add_edge(
            anchor_node.skill_id,
            relation_to_current,
        )

        if next_node is not None:
            add_edge(
                next_node.skill_id,
                relation_to_next,
            )

        db.commit()
        db.refresh(new_node)

        return new_node

    except Exception:
        db.rollback()
        raise
