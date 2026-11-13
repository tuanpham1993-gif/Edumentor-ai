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
from app.schemas.skill_extraction import(
    SkillExtractionRequest, SkillExtractionResponse
)

from app.services import recommendation_service
from app.schemas.learning_path import LearningPathResponse
from app.services import learning_path_service as path_service
from app.core.dependencies import get_llm_client, get_llm_client_base
from app.services.skill_extraction_service import generate_skill_result, rearrange_learning_path
import httpx
import logging
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/learning_path_generate", 
             response_model=SkillExtractionResponse)
async def generate_learning_path_async(
    request: SkillExtractionRequest,
    client: httpx.AsyncClient = Depends(get_llm_client)
):
    try:
        result = await generate_skill_result(request.prompt, client)
        return result
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to communicate with the LLM server."
        ) from exc
    except (ValueError, KeyError, TypeError) as exc:
        logger.exception("LLM response processing error")

        raise HTTPException(
            status_code=502,
            detail="The LLM returned an invalid response."
        ) from exc

@router.post("/generate",
    response_model=LearningPathPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a learning path preview",
)
async def generate_learning_path(
    request: LearningPathGenerateRequest, 
    db: Session = Depends(get_db),
    client: httpx.AsyncClient = Depends(get_llm_client),
    base_client: httpx.AsyncClient = Depends(get_llm_client_base)):
    try:
        result = await generate_skill_result(
            request.original_query,
            client
        )

        goal_type = result["goal_type"]
        extracted_skills = result["skills"]
        if goal_type not in ["career", "project"]:
            raise ValueError("Invalid goal_type returned by LLM")

        if not isinstance(extracted_skills, list):
            raise ValueError("Invalid skills list returned by LLM")

        if not all(isinstance(skill, str) for skill in extracted_skills):
            raise ValueError("Skill names must be strings")
        target_skill_ids = await run_in_threadpool(
            recommendation_service.extract_target_skills,
            extracted_skills=extracted_skills,
            db=db
        )
        #logger.info(target_skill_ids)
        if not target_skill_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No matching skills were found."
            )

    except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail="Unable to communicate with the LLM server."
            ) from exc
    except (ValueError, KeyError, TypeError) as exc:
        logger.exception("LLM response processing error")

        raise HTTPException(
            status_code=502,
            detail="The LLM returned an invalid response."
        ) from exc

    try:
        learning_path = await run_in_threadpool(
            recommendation_service.generate_learning_path_preview,
            db=db,
            original_query=request.original_query,
            target_skill_ids=target_skill_ids,
            goal_type=goal_type
        )
        return learning_path
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
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
