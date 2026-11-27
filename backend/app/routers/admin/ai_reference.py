"""Admin CRUD for AI reference data in Qdrant: job roles, role aliases, role candidate skills,
skill aliases. Every write is validated against Postgres `skills` (app/services/ai_reference_service.py).
Mounted under /api/admin (admin only)."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.schemas.job_role import (
    JobRoleAliasCreate,
    JobRoleAliasResponse,
    JobRoleCreate,
    JobRoleResponse,
    JobRoleUpdate,
    RoleCandidateSkillCreate,
)
from app.schemas.skill import SkillAliasCreate, SkillAliasResponse, SkillAliasUpdate
from app.services.ai_reference_service import AIReferenceService

router = APIRouter(dependencies=[Depends(require_admin)])


def _svc(db: Session = Depends(get_db)) -> AIReferenceService:
    return AIReferenceService(db)


# ---------------------------------------------------------------- job roles
@router.get("/job-roles", response_model=list[JobRoleResponse], summary="Danh sách vai trò nghề")
def list_job_roles(active_only: bool = Query(default=False), svc: AIReferenceService = Depends(_svc)):
    return svc.list_roles(active_only)


@router.get("/job-roles/{role_id}", response_model=JobRoleResponse, summary="Chi tiết vai trò nghề")
def get_job_role(role_id: int, svc: AIReferenceService = Depends(_svc)):
    return svc.get_role(role_id)


@router.post("/job-roles", response_model=JobRoleResponse, status_code=status.HTTP_201_CREATED,
             summary="Tạo vai trò nghề (kèm alias và kỹ năng đích)")
def create_job_role(data: JobRoleCreate, svc: AIReferenceService = Depends(_svc)):
    return svc.create_role(data)


@router.patch("/job-roles/{role_id}", response_model=JobRoleResponse, summary="Sửa vai trò nghề")
def update_job_role(role_id: int, data: JobRoleUpdate, svc: AIReferenceService = Depends(_svc)):
    return svc.update_role(role_id, data)


@router.delete("/job-roles/{role_id}", summary="Xóa vai trò (vô hiệu hóa nếu lộ trình còn tham chiếu)")
def delete_job_role(role_id: int, svc: AIReferenceService = Depends(_svc)):
    return svc.delete_role(role_id)


# ------------------------------------------------------------- role aliases
@router.post("/job-roles/{role_id}/aliases", response_model=JobRoleAliasResponse,
             status_code=status.HTTP_201_CREATED, summary="Thêm alias cho vai trò")
def add_job_role_alias(role_id: int, data: JobRoleAliasCreate, svc: AIReferenceService = Depends(_svc)):
    return svc.add_role_alias(role_id, data.alias_name)


@router.delete("/job-role-aliases/{alias_name}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Xóa alias vai trò")
def delete_job_role_alias(alias_name: str, svc: AIReferenceService = Depends(_svc)):
    svc.delete_role_alias(alias_name)


# ---------------------------------------------------- role candidate skills
@router.post("/job-roles/{role_id}/candidate-skills", response_model=JobRoleResponse,
             status_code=status.HTTP_201_CREATED, summary="Thêm kỹ năng đích cho vai trò")
def add_role_candidate_skill(role_id: int, data: RoleCandidateSkillCreate, svc: AIReferenceService = Depends(_svc)):
    return svc.add_candidate_skill(role_id, data.skill_id)


@router.delete("/job-roles/{role_id}/candidate-skills/{skill_id}", response_model=JobRoleResponse,
               summary="Gỡ kỹ năng đích khỏi vai trò")
def remove_role_candidate_skill(role_id: int, skill_id: int, svc: AIReferenceService = Depends(_svc)):
    return svc.remove_candidate_skill(role_id, skill_id)


# ------------------------------------------------------------ skill aliases
@router.get("/skill-aliases", response_model=list[SkillAliasResponse], summary="Danh sách alias kỹ năng")
def list_skill_aliases(skill_id: int | None = Query(default=None, gt=0), svc: AIReferenceService = Depends(_svc)):
    return svc.list_skill_aliases(skill_id)


@router.post("/skill-aliases", response_model=SkillAliasResponse, status_code=status.HTTP_201_CREATED,
             summary="Thêm alias kỹ năng")
def create_skill_alias(data: SkillAliasCreate, svc: AIReferenceService = Depends(_svc)):
    return svc.create_skill_alias(data)


@router.patch("/skill-aliases/{alias_name}", response_model=SkillAliasResponse, summary="Sửa alias kỹ năng")
def update_skill_alias(alias_name: str, data: SkillAliasUpdate, svc: AIReferenceService = Depends(_svc)):
    return svc.update_skill_alias(alias_name, data)


@router.delete("/skill-aliases/{alias_name}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa alias kỹ năng")
def delete_skill_alias(alias_name: str, svc: AIReferenceService = Depends(_svc)):
    svc.delete_skill_alias(alias_name)
