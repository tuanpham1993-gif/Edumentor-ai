from sqlalchemy import Select, func, select, case
from sqlalchemy.orm import Session
from typing import Literal

from app.models.learning_path import LearningPath

from app.services.learning_path_node_service import add_new_learning_path_nodes
from app.services.learning_path_edge_service import add_new_learning_path_edges

def build_learning_path_query(
    student_id: int | None = None,
    keyword: str | None = None,
    goal_type: Literal["career", "project"] | None = None,
    status: Literal["completed", "ongoing", "abandoned"] | None = None,
) -> Select:
    select_query = select(LearningPath)

    if student_id is not None:
        select_query = select_query.where(LearningPath.student_id == student_id)

    if keyword and keyword.strip():
        pattern = f"%{keyword.strip()}%"
        select_query = select_query.where(LearningPath.original_query.ilike(pattern))

    if goal_type is not None:
        select_query = select_query.where(LearningPath.goal_type == goal_type)

    if status is not None:
        select_query = select_query.where(LearningPath.status == status)
    return select_query.order_by(LearningPath.record_id.desc())

def count_total_learning_path(select_query: Select):
    return select(func.count()).select_from(select_query.order_by(None).subquery())

def list_learning_path(db: Session, skip: int = 0, limit: int = 10, **filters) -> tuple[int, list[LearningPath]]:
    select_query = build_learning_path_query(**filters)
    total = db.execute(count_total_learning_path(select_query)).scalar_one()
    #lazy joined effect we use unique to filter out distinct row-> scalars take value out of each row return object
    #.all() return as list
    items = db.execute(select_query.offset(skip).limit(limit)).unique().scalars().all()
    return total, list(items)

def get_learning_path(db: Session, record_id: int, student_id: int | None = None) -> LearningPath | None:
    query = select(LearningPath).where(LearningPath.record_id == record_id)

    if student_id is not None:
        query = query.where(LearningPath.student_id == student_id)
    return db.scalar(query)

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

def add_learning_path(
    db: Session, student_id: int, original_query: str, goal_type: Literal["career", "project"],
) -> LearningPath:

    new_path = LearningPath(
        student_id=student_id,
        original_query=original_query,
        goal_type=goal_type,
        status="ongoing",
    )

    db.add(new_path)
    db.flush()
    return new_path

def create_learning_path(
    db: Session, student_id: int, original_query: str, goal_type: str, nodes: list, edges: list,
) -> LearningPath:
    try:
        # 1. Create parent learning path.
        new_path = add_learning_path(db=db, student_id=student_id, original_query=original_query, goal_type=goal_type)

        db.flush()  # Generate record_id before creating nodes and edges.

        # 2. Create all nodes.
        add_new_learning_path_nodes(db=db, path_id=new_path.record_id, nodes=nodes)

        # 3. Create all edges.
        add_new_learning_path_edges( db=db, path_id=new_path.record_id, edges=edges, nodes=nodes)

        # 4. Commit everything together.
        db.commit()
        db.refresh(new_path)
        return new_path

    except Exception:
        db.rollback()
        raise

"""
{
  "original_query": "I want to become a backend developer using Python.",
  "goal_type": "career",
  "nodes": [
    {
      "skill_id": 101,
      "skill_name": "Cascading Style Sheets (CSS)",
      "node_role": "prerequisite",
      "is_target": false,
      "added_by": "system",
      "is_required": true,
      "display_order": 1000
    },
    {
      "skill_id": 102,
      "skill_name": "Computer Programming",
      "node_role": "prerequisite",
      "is_target": false,
      "added_by": "system",
      "is_required": true,
      "display_order": 2000
    },
    {
      "skill_id": 103,
      "skill_name": "Database (DBMS)",
      "node_role": "prerequisite",
      "is_target": false,
      "added_by": "system",
      "is_required": true,
      "display_order": 3000
    },
    {
      "skill_id": 104,
      "skill_name": "HTML",
      "node_role": "prerequisite",
      "is_target": false,
      "added_by": "system",
      "is_required": true,
      "display_order": 4000
    },
    {
      "skill_id": 105,
      "skill_name": "Web Development",
      "node_role": "prerequisite",
      "is_target": false,
      "added_by": "system",
      "is_required": true,
      "display_order": 5000
    },
    {
      "skill_id": 106,
      "skill_name": "Backend Systems",
      "node_role": null,
      "is_target": true,
      "added_by": "system",
      "is_required": true,
      "display_order": 6000
    },
    {
      "skill_id": 167,
      "skill_name": "Python Programming",
      "node_role": null,
      "is_target": true,
      "added_by": "system",
      "is_required": true,
      "display_order": 7000
    },
    {
      "skill_id": 107,
      "skill_name": "RESTful API",
      "node_role": null,
      "is_target": true,
      "added_by": "system",
      "is_required": true,
      "display_order": 8000
    },
    {
      "skill_id": 108,
      "skill_name": "SQL",
      "node_role": null,
      "is_target": true,
      "added_by": "system",
      "is_required": true,
      "display_order": 9000
    },
    {
      "skill_id": 109,
      "skill_name": "Flask",
      "node_role": "related",
      "is_target": false,
      "added_by": "system",
      "is_required": false,
      "display_order": 10000
    }
  ],
  "edges": [
    {
      "from_skill_id": 101,
      "from_skill_name": "Cascading Style Sheets (CSS)",
      "to_skill_id": 105,
      "to_skill_name": "Web Development",
      "relation_type": "prerequisite"
    },
    {
      "from_skill_id": 102,
      "from_skill_name": "Computer Programming",
      "to_skill_id": 167,
      "to_skill_name": "Python Programming",
      "relation_type": "prerequisite"
    },
    {
      "from_skill_id": 103,
      "from_skill_name": "Database (DBMS)",
      "to_skill_id": 108,
      "to_skill_name": "SQL",
      "relation_type": "prerequisite"
    },
    {
      "from_skill_id": 104,
      "from_skill_name": "HTML",
      "to_skill_id": 105,
      "to_skill_name": "Web Development",
      "relation_type": "prerequisite"
    },
    {
      "from_skill_id": 105,
      "from_skill_name": "Web Development",
      "to_skill_id": 106,
      "to_skill_name": "Backend Systems",
      "relation_type": "extension"
    },
    {
      "from_skill_id": 105,
      "from_skill_name": "Web Development",
      "to_skill_id": 107,
      "to_skill_name": "RESTful API",
      "relation_type": "prerequisite"
    },
    {
      "from_skill_id": 167,
      "from_skill_name": "Python Programming",
      "to_skill_id": 109,
      "to_skill_name": "Flask",
      "relation_type": "prerequisite"
    },
    {
      "from_skill_id": 107,
      "from_skill_name": "RESTful API",
      "to_skill_id": 109,
      "to_skill_name": "Flask",
      "relation_type": "related"
    }
  ]
}
"""

def abandon_learning_path(db: Session, record_id: int, student_id: int,) -> LearningPath | None:
    try:
        learning_path = get_learning_path(db=db,record_id=record_id,student_id=student_id,)
        if learning_path is None: return None
        if learning_path.status == "abandoned": raise ValueError("Learning path is already abandoned.")
        learning_path.status = "abandoned"
        db.commit()
        db.refresh(learning_path)
        return learning_path

    except Exception:
        db.rollback()
        raise



