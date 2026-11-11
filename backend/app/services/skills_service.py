from sqlalchemy import func, select, delete, or_
from sqlalchemy.orm import Session
from typing import Literal
from app.models import Skills, SkillRelation, CourseSkill
from app.core.embedding_model import generate_embedding_skills_name
from app.services.qdrant_service import qdrant_skill_service

def sync_skill_to_qdrant(skill):
    if not skill.is_active:
        qdrant_skill_service.delete_skill(skill.skill_id)
        return
    embedding = generate_embedding_skills_name([skill.skill])[0]
    qdrant_skill_service.update_skill(
        skill_id=skill.skill_id,
        skill=skill.skill,
        embedding=embedding
    )

def create_skill(db: Session, skill_name: str) -> Skills:
    try:
        new_skill = Skills(skill=skill_name.strip())
        db.add(new_skill)
        db.commit()
        db.refresh(new_skill)
        return new_skill
    
    except Exception:
        db.rollback()
        raise

def update_skill(db: Session,skill_id: int,skill_name: str,) -> Skills:
    try:
        skill = db.get(Skills, skill_id)
        if skill is None:raise ValueError("Skill not found.")
        skill.skill = skill_name.strip()
        db.commit()
        db.refresh(skill)
        return skill
    except Exception:
        db.rollback()
        raise

def delete_skill(db: Session, skill_id: int) -> Skills:
    try:
        skill = db.get(Skills, skill_id)

        if skill is None: raise ValueError("Skill not found.")

        if not skill.is_active: raise ValueError("Skill is already inactive.")

        # Deactivate the skill instead of physically deleting it.
        skill.is_active = False

        # Remove its relationships with other skills.
        #db.execute(delete(SkillRelation).where(or_(SkillRelation.from_skill_id == skill_id,SkillRelation.to_skill_id == skill_id,)))

        db.commit()
        db.refresh(skill)
        return skill

    except Exception:
        db.rollback()
        raise

def get_skill(db: Session, skill_id: int) -> Skills | None:
    return db.get(Skills, skill_id)

def get_skill_with_courses(db: Session, skill_id: int,) -> tuple[Skills, int] | None:
    skill = db.scalars(select(Skills).where(Skills.skill_id == skill_id)).unique().one_or_none()
    if skill is None:
        return None

    total_courses = db.scalar(
        select(func.count())
        .select_from(CourseSkill)
        .where(CourseSkill.skill_id == skill_id)
    )

    return skill, total_courses or 0

def list_skills(
    db: Session, skip: int = 0,
    limit: int = 10, keyword: str | None = None,) -> tuple[int, list[Skills]]:

    query = select(Skills).where(Skills.is_active.is_(True))
    if keyword and keyword.strip(): query = query.where(Skills.skill.ilike(f"%{keyword.strip()}%"))

    count_query = select(func.count()).select_from(query.order_by(None).subquery())

    total = db.scalar(count_query)

    items = db.scalars(
        query.order_by(Skills.skill_id)
        .offset(skip)
        .limit(limit)
    ).unique().all()

    return total, list(items)

#skill_relation

RelationType = Literal["prerequisite", "related", "extension"]
def create_skill_relation(
    db: Session, from_skill_id: int, to_skill_id: int, relation_type: RelationType,
) -> SkillRelation:

    try:
        # 1. Prevent a skill from relating to itself.
        if from_skill_id == to_skill_id:
            raise ValueError("A skill cannot relate to itself.")

        # 2. Check whether both skills exist.
        skill_ids = db.scalars(
            select(Skills.skill_id).where(
                Skills.skill_id.in_([from_skill_id, to_skill_id]),
                Skills.is_active.is_(True),
            )
        ).all()

        if len(skill_ids) != 2: raise ValueError("One or both skills were not found.")

        # 3. Check whether the relationship already exists.
        existing_relation = db.get(SkillRelation,(from_skill_id, to_skill_id),)
        if existing_relation is not None: raise ValueError("This skill relationship already exists.")

        # 4. Create the relationship.
        new_relation = SkillRelation(
            from_skill_id=from_skill_id,
            to_skill_id=to_skill_id,
            relation_type=relation_type,
        )

        db.add(new_relation)
        db.commit()
        db.refresh(new_relation)
        return new_relation

    except Exception:
        db.rollback()
        raise

def get_skill_relations(db: Session, skill_id: int,) -> list[SkillRelation]:

    skill = db.get(Skills, skill_id)

    if skill is None:
        raise ValueError("Skill not found.")

    relations = db.scalars(select(SkillRelation).where((SkillRelation.from_skill_id == skill_id) | (SkillRelation.to_skill_id == skill_id))).all()
    return list(relations)

def update_skill_relation(db: Session, from_skill_id: int, to_skill_id: int, relation_type: RelationType) -> SkillRelation:
    try:
        relation = db.get(SkillRelation, (from_skill_id, to_skill_id))
        if relation is None: raise ValueError("Skill relationship not found.")
        relation.relation_type = relation_type

        db.commit()
        db.refresh(relation)
        return relation
    except Exception:
        db.rollback()
        raise

def delete_skill_relation(db: Session, from_skill_id: int, to_skill_id: int) -> None:
    try:
        relation = db.get(SkillRelation,(from_skill_id, to_skill_id),)

        if relation is None:
            raise ValueError("Skill relationship not found.")

        db.delete(relation)
        db.commit()

    except Exception:
        db.rollback()
        raise