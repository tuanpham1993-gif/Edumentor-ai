from fastapi import (APIRouter,Depends,HTTPException,status)
from fastapi import Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.learning_path_generation import (
    LearningPathGenerateRequest,
    LearningPathPreviewResponse,
    LearningPathConfirmRequest,
    LearningPathRejectedResponse,
)

from app.services import recommendation_service
from app.schemas.learning_path import LearningPathResponse
from app.services import learning_path_service as path_service

router = APIRouter()
@router.post("/generate",
    response_model=LearningPathPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a learning path preview",
)
def generate_learning_path(request: LearningPathGenerateRequest, db: Session = Depends(get_db),):
    try:
        learning_path = (
            recommendation_service.generate_learning_path_preview(
                db=db, original_query=request.original_query)
        )
        return learning_path
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ======================================================
# Confirm learning path preview
# ======================================================

@router.post(
    "/confirm",
    response_model=LearningPathResponse | LearningPathRejectedResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm or reject a learning path preview",
)
def confirm_learning_path(
    request: LearningPathConfirmRequest,
    student_id: int = Query(...,description="Temporary student ID until authentication is implemented",),
    db: Session = Depends(get_db)):

    if not request.confirmed:
        return LearningPathRejectedResponse(
            confirmed=False,
            message=(
                "Thank you for your feedback. "
                "Could you provide more information about your learning goals, "
                "current skills, or preferred learning direction? "
                "This will help us generate a more suitable learning path."
            ),
            next_action="provide_more_information",
        )

    # --------------------------------------------------
    # 2. User confirms the generated learning path
    # --------------------------------------------------

    try:
        nodes = [
            {
                "skill_id": node.skill_id,
                "node_role": node.node_role,
                "is_target": node.is_target,
                "added_by": node.added_by,
                "is_required": node.is_required,
                "display_order": node.display_order,
            }
            for node in request.nodes]

        # Convert preview edges into database creation data.
        edges = [
            {
                "from_skill_id": edge.from_skill_id,
                "to_skill_id": edge.to_skill_id,
                "relation_type": edge.relation_type,
            }
            for edge in request.edges
        ]

        saved_path = path_service.create_learning_path(
            db=db,
            student_id=student_id,
            original_query=request.original_query,
            goal_type=request.goal_type,
            nodes=nodes,
            edges=edges,
        )

        return saved_path

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e))
