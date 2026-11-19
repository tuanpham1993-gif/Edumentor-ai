from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.learning_path import (
    LearningPathEdgeResponse,
    LearningPathEdgeCreate,
    LearningPathEdgeUpdate,
    LearningPathEdgeRemove
    )
from app.models import Users
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.services import learning_path_edge_service as node_service

router = APIRouter()

@router.post(
    "/add",
    response_model=LearningPathEdgeResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_edge(
    request: LearningPathEdgeCreate,
    record_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return node_service.add_learning_path_edge(
            db=db,
            path_id=record_id,
            student_id=current_user.user_id,
            from_skill_id=request.from_skill_id,
            to_skill_id=request.to_skill_id,
            relation_type=request.relation_type,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/update",
    response_model=LearningPathEdgeResponse,
)
def update_edge(
    request: LearningPathEdgeUpdate,
    record_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return node_service.update_learning_path_edge(
            db=db,
            path_id=record_id,
            student_id=current_user.user_id,
            from_skill_id=request.from_skill_id,
            to_skill_id=request.to_skill_id,
            relation_type=request.relation_type,
        )

    except ValueError as e:
        message = str(e)

        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in message.lower()
            or "access denied" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(status_code=code, detail=message)


@router.delete("/remove", status_code=status.HTTP_204_NO_CONTENT)
def remove_edge(
    request: LearningPathEdgeRemove,
    record_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        node_service.delete_learning_path_edge(
            db=db,
            path_id=record_id,
            student_id=current_user.user_id,
            from_skill_id=request.from_skill_id,
            to_skill_id=request.to_skill_id,
        )

    except ValueError as e:
        message = str(e)

        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in message.lower()
            or "access denied" in message.lower()
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(status_code=code, detail=message)

    return None