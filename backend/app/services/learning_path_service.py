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



