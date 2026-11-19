from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.learning_path import (
    LearningPathCreate, LearningPathResponse,
    LearningPathListResponse
)
from app.services import learning_path_service as path_service
from app.services import learning_path_node_service as node_service
from app.core.dependencies import get_current_user, require_admin
from app.models.user import Users
router = APIRouter()

@router.post("", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED, summary="Create a brand new learning path")
def create_learning_path(
    request: LearningPathCreate,
    current_user: Users = Depends(require_admin),
    db: Session = Depends(get_db)):
    try:
        student_id = current_user.user_id
        return path_service.create_learning_path(
            db=db, student_id=student_id,
            original_query=request.original_query,
            goal_type=request.goal_type,
            nodes=[node.model_dump() for node in request.nodes],
            edges=[edge.model_dump() for edge in request.edges],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e),)

@router.get("", response_model=LearningPathListResponse, 
            summary="List learning paths with path query")
def list_learning_paths(
    current_user: Users = Depends(get_current_user),
    keyword: str | None = Query(default=None),
    goal_type: Literal["career", "project"] | None = Query(default=None),
    path_status: Literal["completed", "ongoing", "abandoned"] | None = Query(default=None,alias="status",),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    student_id = current_user.user_id
    total, items = path_service.list_learning_path(
        db=db, skip=skip, limit=limit,
        student_id=student_id, keyword=keyword,
        goal_type=goal_type, status=path_status,
    )

    return LearningPathListResponse(
        total=total, skip=skip, limit=limit, 
        current_total=len(items), data=items,
    )

@router.get("/stat", summary="Get learning path statistics",)
def get_learning_path_statistics(student_id: int = Query(...), db: Session = Depends(get_db)):
    return path_service.get_learning_path_statistics(db=db, student_id=student_id)

@router.get("/{record_id}", response_model=LearningPathResponse, 
            summary="Get a learning path from student id + record id or from record_id only")
def get_learning_path(record_id: int, 
                      current_user: Users = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    student_id = current_user.user_id
    learning_path = path_service.get_learning_path(
        db=db, record_id=record_id,
        student_id=student_id,
    )
    if learning_path is None:
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found.",)
    return learning_path

@router.patch(
    "/{record_id}/abandon",
    response_model=LearningPathResponse,
    summary="Abandon a learning path",
)
def abandon_learning_path(record_id: int, student_id: int = Query(...), db: Session = Depends(get_db)):
    try:
        learning_path = path_service.abandon_learning_path(db=db, record_id=record_id, student_id=student_id,)

        if learning_path is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found.")
        return learning_path

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))