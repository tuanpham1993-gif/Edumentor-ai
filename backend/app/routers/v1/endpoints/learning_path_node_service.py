from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.learning_path import (LearningPathNodeInsert,
    LearningPathNodeUpdate, LearningPathNodeResponse
)
from app.services import learning_path_node_service as node_service

router = APIRouter()

@router.get("/{path_id}/nodes/{skill_id}", summary="Get node detail, add user authentication general for student and admin")
def get_learning_path_node_detail(
    path_id: int, skill_id: int, db: Session = Depends(get_db)
):
    node = node_service.get_detail_node(db=db, path_id=path_id, skill_id=skill_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path node not found.")
    return node

@router.get("/{path_id}/nodes/{skill_id}/recommendation", summary="Recommend course based on user learning path and skill still in update phase")
def get_learning_path_node_recommendation(
    skill_id:int
):
    return

@router.post("/{record_id}/nodes", response_model=LearningPathNodeResponse, status_code=status.HTTP_201_CREATED,
             summary="Add a new node to a learning path")
def add_learning_path_node(
    record_id: int, request: LearningPathNodeInsert,
    student_id: int = Query(...), db: Session = Depends(get_db),
):
    try:
        return node_service.add_learning_path_node(
            db=db, path_id=record_id,
            student_id=student_id,
            skill_id=request.skill_id,
            insert_before_skill_id=request.insert_before_skill_id,
            relation_to_current=request.relation_to_current,
            relation_to_next=request.relation_to_next,
            node_role=request.node_role,
            is_target=request.is_target,
            is_required=request.is_required,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch("/{record_id}/nodes/{skill_id}", response_model=LearningPathNodeResponse, 
              summary="Update a learning path node")
def update_learning_path_node(
    record_id: int, skill_id: int, request: LearningPathNodeUpdate,
    student_id: int = Query(...), db: Session = Depends(get_db)
):
    try:
        return node_service.update_learning_path_node(
            db=db, path_id=record_id,
            student_id=student_id, skill_id=skill_id,
            node_role=request.node_role,
            passed_test=request.passed_test,
        )
    except ValueError as e:
        message = str(e)
        if "not found" in message.lower() or "access denied" in message.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=message)

@router.delete("/{record_id}/nodes/{skill_id}", status_code=status.HTTP_204_NO_CONTENT, 
               summary="Delete a node from a learning path")
def delete_learning_path_node(
    record_id: int, skill_id: int,
    student_id: int = Query(...),
    db: Session = Depends(get_db),
):
    try:
        node_service.delete_learning_path_node(
            db=db, path_id=record_id,
            student_id=student_id, skill_id=skill_id,
        )
    except ValueError as e:
        message = str(e)

        if "not found" in message.lower() or "access denied" in message.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return None