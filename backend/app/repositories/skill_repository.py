from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from app.models.skill import Skills
from app.models.course_skill import CourseSkill
from app.models.skill_relation import SkillRelation
from app.models.learning_path import LearningPathNode


class SkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, skill_id: int) -> Optional[Skills]:
        return self.db.get(Skills, skill_id)

    def get_by_name(self, skill_name: str) -> Optional[Skills]:
        stmt = select(Skills).where(func.lower(Skills.skill) == skill_name.strip().lower())
        return self.db.execute(stmt).scalars().unique().one_or_none()

    def list_skills(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[int, List[Skills]]:
        stmt = select(Skills)

        if search:
            stmt = stmt.where(Skills.skill.ilike(f"%{search.strip()}%"))

        if is_active is not None:
            stmt = stmt.where(Skills.is_active == is_active)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        offset = (page - 1) * page_size
        stmt = stmt.order_by(Skills.skill_id.asc()).offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).scalars().unique().all())

        return total, items

    def create(self, skill_name: str) -> Skills:
        skill = Skills(skill=skill_name.strip(), is_active=True)
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def update(self, skill: Skills, update_data: dict) -> Skills:
        for key, value in update_data.items():
            if value is not None and hasattr(skill, key):
                setattr(skill, key, value)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def count_usages(self, skill_id: int) -> dict:
        """Đếm số liên kết tới Skill để kiểm tra an toàn trước khi xóa."""
        # 1. CourseSkill
        course_skill_count = self.db.execute(
            select(func.count()).select_from(CourseSkill).where(CourseSkill.skill_id == skill_id)
        ).scalar_one()

        # 2. SkillRelation
        skill_rel_count = self.db.execute(
            select(func.count())
            .select_from(SkillRelation)
            .where(or_(SkillRelation.from_skill_id == skill_id, SkillRelation.to_skill_id == skill_id))
        ).scalar_one()

        # 3. LearningPathNode
        path_node_count = self.db.execute(
            select(func.count())
            .select_from(LearningPathNode)
            .where(LearningPathNode.skill_id == skill_id)
        ).scalar_one()

        return {
            "course_skills": course_skill_count,
            "skill_relations": skill_rel_count,
            "learning_path_nodes": path_node_count,
            "total_usages": course_skill_count + skill_rel_count + path_node_count,
        }

    def delete_physical(self, skill: Skills) -> None:
        self.db.delete(skill)
        self.db.commit()

    def soft_delete(self, skill: Skills) -> Skills:
        skill.is_active = False
        self.db.commit()
        self.db.refresh(skill)
        return skill

