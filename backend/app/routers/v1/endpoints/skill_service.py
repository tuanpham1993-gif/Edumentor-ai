from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.services import skills_service as crud_skill_service
from app.core.database import get_db

from app.schemas.skill import SkillRequestResponse, SkillListResponse, SkillWithCoursesResponse, SkillCreate, SkillUpdate
from app.schemas.skill_relation import SkillRelationCreate, SkillRelationResponse, SkillRelationUpdate 
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=SkillListResponse, summary="list of skills with total skill")
def list_all_skills(
    db: Session = Depends(get_db),
    keyword: str | None = Query(default=None, description="Tìm skill theo keyword"),
    skip: int = Query(default=0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(default=6, ge=1, le=50, description="Số bản ghi tối đa (1-50)")):
    total, items = crud_skill_service.list_skills(db=db, skip=skip, limit=limit, keyword=keyword)
    return SkillListResponse(
        total=total,
        skip=skip,
        limit=limit,
        current_total=len(items),
        data=items
    )

@router.get("/{skill_id}", response_model=SkillRequestResponse, summary="Get skill by ID")
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = crud_skill_service.get_skill(db=db, skill_id=skill_id)
    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found.",
        )
    return skill

@router.get("/{skill_id}/courses", response_model=SkillWithCoursesResponse, summary="Get skill with course count")
def get_skill_courses(skill_id: int,db: Session = Depends(get_db)):
    result = crud_skill_service.get_skill_with_courses(db=db, skill_id=skill_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found.",
        )

    skill, total_courses = result

    return SkillWithCoursesResponse(
        skill=skill.skill,
        skill_id=skill.skill_id,
        is_active=skill.is_active,
        total_courses=total_courses,
    )

@router.post("",response_model=SkillRequestResponse, status_code=status.HTTP_201_CREATED, summary="Create skill")
def create_skill(request: SkillCreate,db: Session = Depends(get_db)):
    try:
        skill =  crud_skill_service.create_skill(db=db,skill_name=request.skill)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    try:
        crud_skill_service.sync_skill_to_qdrant(skill)
    except Exception:
        logger.exception(
            "Failed to synchronize newly created skill %s with Qdrant",
            skill.skill_id
        )
    return skill

@router.put("/{skill_id}",response_model=SkillRequestResponse,summary="Update skill",)
def update_skill(skill_id: int,request: SkillUpdate,db: Session = Depends(get_db),):
    try:
        skill = crud_skill_service.update_skill(db=db, skill_id=skill_id, skill_name=request.skill)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    try:
        crud_skill_service.sync_skill_to_qdrant(skill)
    except Exception:
        logger.exception(
            "Failed to synchronize newly created skill %s with Qdrant",
            skill.skill_id
        )
    return skill
    
@router.delete("/{skill_id}", response_model=SkillRequestResponse, summary="Deactivate skill",)
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    try:
        skill = crud_skill_service.delete_skill(db=db, skill_id=skill_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    try:
        crud_skill_service.sync_skill_to_qdrant(skill)
    except Exception:
        logger.exception(
            "Failed to synchronize newly created skill %s with Qdrant",
            skill.skill_id
        )
    return skill

#skill_relation
# POST /skill-relations
@router.post(
    "/skill_relation",
    response_model=SkillRelationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a skill relationship",
)
def create_skill_relation(
    request: SkillRelationCreate,
    db: Session = Depends(get_db),
):
    try:
        return crud_skill_service.create_skill_relation(
            db=db,
            from_skill_id=request.from_skill_id,
            to_skill_id=request.to_skill_id,
            relation_type=request.relation_type,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# GET /skill-relations/{skill_id}
@router.get(
    "/skill_relation/{skill_id}",
    response_model=list[SkillRelationResponse],
    summary="Get relationships for a skill",
)
def get_skill_relations(
    skill_id: int,
    db: Session = Depends(get_db),
):
    try:
        return crud_skill_service.get_skill_relations(
            db=db,
            skill_id=skill_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

# PUT /skill-relations/{from_skill_id}/{to_skill_id}
@router.put(
    "/skill_relation/{from_skill_id}/{to_skill_id}",
    response_model=SkillRelationResponse,
    summary="Update a skill relationship",
)
def update_skill_relation(
    from_skill_id: int,
    to_skill_id: int,
    request: SkillRelationUpdate,
    db: Session = Depends(get_db),
):
    try:
        return crud_skill_service.update_skill_relation(
            db=db,
            from_skill_id=from_skill_id,
            to_skill_id=to_skill_id,
            relation_type=request.relation_type,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

# DELETE /skill-relations/{from_skill_id}/{to_skill_id}
@router.delete(
    "/skill_relation/{from_skill_id}/{to_skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a skill relationship",
)
def delete_skill_relation(
    from_skill_id: int,
    to_skill_id: int,
    db: Session = Depends(get_db),
):
    try:
        crud_skill_service.delete_skill_relation(
            db=db,
            from_skill_id=from_skill_id,
            to_skill_id=to_skill_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return None


