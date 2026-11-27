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
from app.models.user import Users
from app.services import recommendation_service
from app.schemas.learning_path import LearningPathResponse
from app.services import learning_path_service as path_service
from app.core.dependencies import get_llm_client, get_current_user
from app.services.skill_extraction_service import generate_skill_result
from app.utils.learner_analyzer.inference import LLMInferenceError, generate_g1_response
from app.utils.learner_analyzer.prompt import build_messages
from app.utils.learner_analyzer.schemas import G1Input, G1Output
from app.schemas.learning_path_generation_v2 import (
    LearningPathConfirm2Request,
    LearningPathConfirm2Response,
    LearningPathFormOptions,
    LearningPathPreview2Response,
)
from app.services import learning_path_generation_v2_service as lp2_service
from pydantic import ValidationError
import httpx
import logging
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/learning_path_generate", 
             response_model=SkillExtractionResponse,
             description="For testing purpose")
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
    client: httpx.AsyncClient = Depends(get_llm_client)):
    try:
        result = await generate_skill_result(
            request.original_query, client
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


async def _run_g1(request: G1Input, client: httpx.AsyncClient) -> G1Output:
    """Call the fine-tuned Qwen3 (llama.cpp + LoRA) and validate its JSON against G1Output."""
    messages = build_messages(request)
    try:
        raw_response = await generate_g1_response(messages, client)
        return G1Output.model_validate_json(raw_response)
    except LLMInferenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except ValidationError as exc:
        logger.exception("G1 LLM output validation error")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The LLM returned an invalid G1 output structure.",
        ) from exc


@router.post(
    "/generate_ai_2",
    response_model=LearningPathPreview2Response,
    status_code=status.HTTP_200_OK,
    summary="AI learning path v2: G1 profile extraction -> targets -> personalized prerequisite graph (preview)",
)
async def generate_ai_2(
    request: G1Input,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    client: httpx.AsyncClient = Depends(get_llm_client),
):
    """Nothing is saved here. status="needs_clarification" means the goal could not be turned
    into target skills (or is ambiguous): show clarification_required to the learner. When
    nodes is not empty the preview can still be accepted with /confirm-2."""
    g1 = await _run_g1(request, client)
    try:
        return await run_in_threadpool(lp2_service.build_preview, db, current_user.user_id, g1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post(
    "/generate_ai_2/raw",
    response_model=G1Output,
    status_code=status.HTTP_200_OK,
    summary="Raw G1 LLM output (testing the GGUF adapter; no linking, no graph)",
)
async def generate_ai_2_raw(
    request: G1Input,
    client: httpx.AsyncClient = Depends(get_llm_client),
):
    return await _run_g1(request, client)


@router.get(
    "/options",
    response_model=LearningPathFormOptions,
    summary="Options for the Make learning path form (career levels, proficiency, certifications, domains)",
)
def get_learning_path_form_options(db: Session = Depends(get_db)):
    return lp2_service.form_options(db)


@router.post(
    "/confirm-2",
    response_model=LearningPathConfirm2Response | LearningPathRejectedResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept (save path + learner profile + graph) or reject an AI learning path v2 preview",
)
def confirm_learning_path_2(
    request: LearningPathConfirm2Request,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
    try:
        return lp2_service.confirm(db, current_user.user_id, request)
    except ValueError as exc:   # also pydantic ValidationError (a ValueError) from the profile snapshot
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


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
    current_user: Users = Depends(get_current_user),
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
        student_id = current_user.user_id
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
