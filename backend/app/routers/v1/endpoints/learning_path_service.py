from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional, require_admin
from app.models.user import Users
from app.schemas.learning_path import (
    CloneLearningPathResponse,
    LearningPathCreate,
    LearningPathListResponse,
    LearningPathResponse,
    LearningPathShareResponse,
    SharedLearningPathDetailResponse,
)
from app.services import learning_path_service as path_service

router = APIRouter()


@router.post(
    "",
    response_model=LearningPathResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a brand new learning path",
)
def create_learning_path(
    request: LearningPathCreate, current_user: Users = Depends(require_admin), db: Session = Depends(get_db)
):
    try:
        student_id = current_user.user_id
        return path_service.create_learning_path(
            db=db,
            student_id=student_id,
            original_query=request.original_query,
            goal_type=request.goal_type,
            nodes=[node.model_dump() for node in request.nodes],
            edges=[edge.model_dump() for edge in request.edges],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=LearningPathListResponse, summary="List learning paths with path query")
def list_learning_paths(
    current_user: Users = Depends(get_current_user),
    keyword: str | None = Query(default=None),
    goal_type: Literal["career", "project"] | None = Query(default=None),
    path_status: Literal["completed", "ongoing", "abandoned"] | None = Query(
        default=None,
        alias="status",
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    student_id = current_user.user_id
    total, items = path_service.list_learning_path(
        db=db,
        skip=skip,
        limit=limit,
        student_id=student_id,
        keyword=keyword,
        goal_type=goal_type,
        status=path_status,
    )

    return LearningPathListResponse(
        total=total,
        skip=skip,
        limit=limit,
        current_total=len(items),
        data=items,
    )


@router.get(
    "/stat",
    summary="Get learning path statistics",
)
def get_learning_path_statistics(student_id: int = Query(...), db: Session = Depends(get_db)):
    return path_service.get_learning_path_statistics(db=db, student_id=student_id)


@router.get(
    "/shared/{share_code}", response_model=SharedLearningPathDetailResponse, summary="View a shared learning path"
)
def get_shared_path(
    share_code: str,
    current_user: Users | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    path = path_service.get_shared_learning_path(db=db, share_code=share_code)
    if path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lộ trình chia sẻ không tồn tại hoặc đã bị thu hồi.",
        )

    is_owner = current_user is not None and current_user.user_id == path.student_id

    author_data = None
    if path.student:
        author_data = {
            "user_id": path.student.user_id,
            "full_name": path.student.full_name,
            "avatar_url": path.student.avatar_url,
            "role": path.student.role,
        }

    return SharedLearningPathDetailResponse(
        record_id=path.record_id,
        original_query=path.original_query,
        goal_type=path.goal_type,
        status=path.status,
        share_code=path.share_code,
        shared_at=path.shared_at,
        clone_count=path.clone_count or 0,
        is_owner=is_owner,
        author=author_data,
        nodes=path.nodes,
        edges=path.edges,
    )


@router.post(
    "/shared/{share_code}/clone",
    response_model=CloneLearningPathResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Clone a shared learning path to current user's paths",
)
def clone_shared_path(
    share_code: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        new_path = path_service.clone_shared_learning_path(
            db=db, share_code=share_code, student_id=current_user.user_id
        )
        return CloneLearningPathResponse(
            new_record_id=new_path.record_id,
            message="Đã sao chép lộ trình thành công vào danh sách lộ trình của bạn.",
            learning_path=new_path,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{record_id}/share", response_model=LearningPathShareResponse, summary="Enable sharing for a learning path"
)
def enable_share(
    record_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        path = path_service.enable_learning_path_share(db=db, record_id=record_id, student_id=current_user.user_id)
        share_url = f"{settings.FRONTEND_URL}/shared/learning-paths/{path.share_code}"
        return LearningPathShareResponse(
            record_id=path.record_id,
            is_shared=path.is_shared,
            share_code=path.share_code,
            share_url=share_url,
            shared_at=path.shared_at,
            clone_count=path.clone_count or 0,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{record_id}/share", response_model=LearningPathShareResponse, summary="Disable sharing for a learning path"
)
def disable_share(
    record_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        path = path_service.disable_learning_path_share(db=db, record_id=record_id, student_id=current_user.user_id)
        return LearningPathShareResponse(
            record_id=path.record_id,
            is_shared=path.is_shared,
            share_code=path.share_code,
            share_url=None,
            shared_at=path.shared_at,
            clone_count=path.clone_count or 0,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{record_id}",
    response_model=LearningPathResponse,
    summary="Get a learning path from student id + record id or from record_id only",
)
def get_learning_path(record_id: int, current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    student_id = current_user.user_id
    learning_path = path_service.get_learning_path(
        db=db,
        record_id=record_id,
        student_id=student_id,
    )
    if learning_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found.",
        )
    return learning_path


@router.patch(
    "/{record_id}/abandon",
    response_model=LearningPathResponse,
    summary="Abandon a learning path",
)
def abandon_learning_path(record_id: int, student_id: int = Query(...), db: Session = Depends(get_db)):
    try:
        learning_path = path_service.abandon_learning_path(
            db=db,
            record_id=record_id,
            student_id=student_id,
        )

        if learning_path is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found.")
        return learning_path

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
