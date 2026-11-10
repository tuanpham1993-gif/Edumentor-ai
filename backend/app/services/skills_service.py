from typing import Optional, Literal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.skill_repository import SkillRepository
from app.schemas.skill import (
    SkillCreate,
    SkillUpdate,
    SkillRequestResponse,
    SkillWithCoursesResponse,
)
from app.schemas.skill_relation import SkillRelationCreate, SkillRelationResponse, SkillRelationUpdate
from app.schemas.common import PaginatedResponse
from app.models.skill import Skills
from app.models.skill_relation import SkillRelation


class SkillsService:
    def __init__(self, db: Session):
        self.db = db
        self.skill_repo = SkillRepository(db)

    def list_skills_admin(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> PaginatedResponse[SkillRequestResponse]:
        total, items = self.skill_repo.list_skills(
            page=page, page_size=page_size, search=search, is_active=is_active
        )
        return PaginatedResponse(
            items=[SkillRequestResponse.model_validate(s) for s in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_skill(self, skill_id: int) -> SkillRequestResponse:
        skill = self.skill_repo.get_by_id(skill_id)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy kỹ năng với id {skill_id}",
            )
        return SkillRequestResponse.model_validate(skill)

    def create_skill(self, data: SkillCreate) -> SkillRequestResponse:
        existing = self.skill_repo.get_by_name(data.skill)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Kỹ năng '{data.skill}' đã tồn tại trong hệ thống.",
            )
        skill = self.skill_repo.create(data.skill)
        return SkillRequestResponse.model_validate(skill)

    def update_skill(self, skill_id: int, data: SkillUpdate) -> SkillRequestResponse:
        skill = self.skill_repo.get_by_id(skill_id)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy kỹ năng với id {skill_id}",
            )

        update_dict = data.model_dump(exclude_unset=True)

        if "skill" in update_dict and update_dict["skill"] is not None:
            existing = self.skill_repo.get_by_name(update_dict["skill"])
            if existing and existing.skill_id != skill_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Tên kỹ năng '{update_dict['skill']}' đã được sử dụng.",
                )

        updated_skill = self.skill_repo.update(skill, update_dict)
        return SkillRequestResponse.model_validate(updated_skill)

    def delete_skill(self, skill_id: int) -> dict:
        skill = self.skill_repo.get_by_id(skill_id)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy kỹ năng với id {skill_id}",
            )

        usages = self.skill_repo.count_usages(skill_id)

        # Nếu kỹ năng đã được gắn vào khóa học, lộ trình hoặc quan hệ kỹ năng
        if usages["total_usages"] > 0:
            # Vô hiệu hóa (soft delete) thay vì xóa vật lý gây lỗi Foreign Key
            self.skill_repo.soft_delete(skill)
            return {
                "message": f"Kỹ năng '{skill.skill}' đang được sử dụng ({usages['course_skills']} khóa học, "
                           f"{usages['skill_relations']} quan hệ, {usages['learning_path_nodes']} lộ trình). "
                           "Đã vô hiệu hóa kỹ năng (is_active = False) thay vì xóa vật lý.",
                "action": "deactivated",
                "skill_id": skill_id,
            }

        # Nếu không vướng ràng buộc nào, xóa thật
        self.skill_repo.delete_physical(skill)
        return {
            "message": f"Đã xóa hoàn toàn kỹ năng '{skill.skill}' khỏi danh mục.",
            "action": "deleted",
            "skill_id": skill_id,
        }


# Giữ lại các hàm cũ cho các endpoint ngoài nếu có module khác import
def list_skills(db: Session, skip: int = 0, limit: int = 6, keyword: Optional[str] = None):
    repo = SkillRepository(db)
    page = (skip // limit) + 1 if limit > 0 else 1
    total, items = repo.list_skills(page=page, page_size=limit, search=keyword, is_active=True)
    return total, items

def get_skill(db: Session, skill_id: int):
    return SkillRepository(db).get_by_id(skill_id)

def get_skill_with_courses(db: Session, skill_id: int):
    skill = SkillRepository(db).get_by_id(skill_id)
    if not skill:
        return None
    total_courses = len(skill.courses_info)
    return skill, total_courses

def create_skill(db: Session, skill_name: str) -> Skills:
    return SkillRepository(db).create(skill_name)

def update_skill(db: Session, skill_id: int, skill_name: str) -> Skills:
    skill = SkillRepository(db).get_by_id(skill_id)
    if not skill:
        raise ValueError("Skill not found.")
    return SkillRepository(db).update(skill, {"skill": skill_name})

def delete_skill(db: Session, skill_id: int) -> Skills:
    skill = SkillRepository(db).get_by_id(skill_id)
    if not skill:
        raise ValueError("Skill not found.")
    return SkillRepository(db).soft_delete(skill)

# Skill relation helpers
RelationType = Literal["prerequisite", "related", "extension"]

def create_skill_relation(db: Session, from_skill_id: int, to_skill_id: int, relation_type: RelationType) -> SkillRelation:
    if from_skill_id == to_skill_id:
        raise ValueError("A skill cannot relate to itself.")
    new_rel = SkillRelation(from_skill_id=from_skill_id, to_skill_id=to_skill_id, relation_type=relation_type)
    db.add(new_rel)
    db.commit()
    db.refresh(new_rel)
    return new_rel

def get_skill_relations(db: Session, skill_id: int) -> list[SkillRelation]:
    from sqlalchemy import select
    return list(db.scalars(select(SkillRelation).where((SkillRelation.from_skill_id == skill_id) | (SkillRelation.to_skill_id == skill_id))).all())

def update_skill_relation(db: Session, from_skill_id: int, to_skill_id: int, relation_type: RelationType) -> SkillRelation:
    rel = db.get(SkillRelation, (from_skill_id, to_skill_id))
    if not rel:
        raise ValueError("Skill relationship not found.")
    rel.relation_type = relation_type
    db.commit()
    db.refresh(rel)
    return rel

def delete_skill_relation(db: Session, from_skill_id: int, to_skill_id: int) -> None:
    rel = db.get(SkillRelation, (from_skill_id, to_skill_id))
    if not rel:
        raise ValueError("Skill relationship not found.")
    db.delete(rel)
    db.commit()
