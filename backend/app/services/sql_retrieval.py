
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.models import (
    Courses,
    Skills,
    CourseSkill,
    SkillRelation,
)


# ==========================================
# 1. Chuyển SQLAlchemy Model thành Dictionary
# ==========================================

def skill_to_dict(skill: Skills) -> dict:
    return {
        "skill_id": skill.skill_id,
        "skill": skill.skill,
        "is_active": skill.is_active,
    }


def course_to_dict(course: Courses) -> dict:
    return {
        "course_id": course.course_id,
        "title": course.title,
        "description": course.description,
        "instructor": course.instructor,
        "organization": course.organization,
        "level": course.level,
        "rating": course.rating,
        "num_reviews": course.num_reviews,
        "num_enrolled": course.num_enrolled,
        "url": course.url,
        "image": course.image,
    }


# ==========================================
# 2. Tìm Skill
# ==========================================

def find_skill(db: Session, skill_name: str):
    if not skill_name:
        return None

    # Ưu tiên tìm chính xác tên Skill
    skill = db.execute(
        select(Skills).where(
            Skills.skill.ilike(skill_name),
            Skills.is_active.is_(True),
        )
    ).unique().scalars().first()

    if skill:
        return skill

    # Nếu không có, tìm gần đúng
    return db.execute(
        select(Skills).where(
            Skills.skill.ilike(f"%{skill_name}%"),
            Skills.is_active.is_(True),
        ).order_by(Skills.skill)
    ).unique().scalars().first()


# ==========================================
# 3. Tìm Course
# ==========================================

def find_course(db: Session, course_name: str):
    if not course_name:
        return None

    # Ưu tiên tìm chính xác tên Course
    course = db.execute(
        select(Courses).where(
            Courses.title.ilike(course_name)
        )
    ).unique().scalars().first()

    if course:
        return course

    # Nếu không có, tìm gần đúng
    return db.execute(
        select(Courses).where(
            Courses.title.ilike(f"%{course_name}%")
        ).order_by(Courses.title)
    ).unique().scalars().first()


# ==========================================
# 4. Tìm Course theo Skill
# ==========================================

def get_courses_by_skill(db: Session, skill_id: int) -> list:
    courses = db.execute(
        select(Courses)
        .join(
            CourseSkill,
            Courses.course_id == CourseSkill.course_id,
        )
        .where(CourseSkill.skill_id == skill_id)
        .order_by(Courses.title)
    ).unique().scalars().all()

    return [course_to_dict(course) for course in courses]


# ==========================================
# 5. Tìm Skill theo Course
# ==========================================

def get_skills_by_course(db: Session, course_id: int) -> list:
    skills = db.execute(
        select(Skills)
        .join(
            CourseSkill,
            Skills.skill_id == CourseSkill.skill_id,
        )
        .where(
            CourseSkill.course_id == course_id,
            Skills.is_active.is_(True),
        )
        .order_by(Skills.skill)
    ).unique().scalars().all()

    return [skill_to_dict(skill) for skill in skills]


# ==========================================
# 6. Tìm Skill liên quan
# ==========================================

def get_related_skills(db: Session, skill_id: int) -> list:
    relations = db.execute(
        select(SkillRelation).where(
            or_(
                SkillRelation.from_skill_id == skill_id,
                SkillRelation.to_skill_id == skill_id,
            )
        )
    ).unique().scalars().all()

    results = []
    seen = set()

    for relation in relations:
        if relation.from_skill_id == skill_id:
            related_skill_id = relation.to_skill_id
            direction = "outgoing"
        else:
            related_skill_id = relation.from_skill_id
            direction = "incoming"

        related_skill = db.get(Skills, related_skill_id)

        if related_skill is None or not related_skill.is_active:
            continue

        # Quan hệ related có tính hai chiều,
        # nên tránh hiển thị cùng một Skill hai lần.
        if relation.relation_type == "related":
            unique_key = (
                related_skill_id,
                relation.relation_type,
            )
        else:
            # Giữ nguyên chiều của prerequisite và extension.
            unique_key = (
                related_skill_id,
                relation.relation_type,
                direction,
            )

        if unique_key in seen:
            continue

        seen.add(unique_key)

        results.append({
            "skill": skill_to_dict(related_skill),
            "relation_type": relation.relation_type,
            "direction": direction,
        })

    return results


# ==========================================
# 7. Tìm nhiều Course theo từ khóa
# ==========================================

def search_courses(db: Session, keyword: str, limit: int = 10) -> list:
    if not keyword:
        return []

    courses = db.execute(
        select(Courses)
        .where(Courses.title.ilike(f"%{keyword}%"))
        .order_by(Courses.rating.desc().nullslast())
        .limit(limit)
    ).unique().scalars().all()

    return [course_to_dict(course) for course in courses]


# ==========================================
# 8. SQL Retrieval chính
# ==========================================


def retrieve_for_query(db: Session, route_result: dict) -> dict:
    intent = route_result.get("intent")
    entity_type = route_result.get("entity_type")
    entity_name = route_result.get("entity_name")

    result = {
        "intent": intent,
        "entity_type": entity_type,
        "entity_name": entity_name,
        "found": False,
        "skill": None,
        "course": None,
        "courses": [],
        "skills": [],
        "related_skills": [],
    }

    # ======================================
    # 1. COURSE SEARCH THEO SKILL
    # ======================================

    if intent == "course_search":

        # Người dùng tìm khóa học theo chủ đề Skill.
        # Ví dụ: Cho tôi những khóa học của Python.

        if entity_type == "skill":

            skill = find_skill(db, entity_name)

            if skill is None:
                return result

            result["found"] = True
            result["skill"] = skill_to_dict(skill)

            courses = get_courses_by_skill(
                db,
                skill.skill_id,
            )

            result["courses"] = courses

            result["related_skills"] = get_related_skills(
                db,
                skill.skill_id,
            )

            return result

        # Người dùng tìm khóa học theo tên Course.

        if entity_type == "course":

            courses = search_courses(
                db,
                entity_name,
            )

            result["courses"] = courses
            result["found"] = len(courses) > 0

            return result

        return result

    # ======================================
    # 2. TÌM SKILL
    # ======================================

    if entity_type == "skill":

        skill = find_skill(db, entity_name)

        if skill is None:
            return result

        result["found"] = True
        result["skill"] = skill_to_dict(skill)

        result["courses"] = get_courses_by_skill(
            db,
            skill.skill_id,
        )

        result["related_skills"] = get_related_skills(
            db,
            skill.skill_id,
        )

        return result

    # ======================================
    # 3. TÌM COURSE VÀ SKILL LIÊN QUAN
    # ======================================

    if entity_type == "course":

        course = find_course(db, entity_name)

        if course is None:
            return result

        result["found"] = True
        result["course"] = course_to_dict(course)

        skills = get_skills_by_course(
            db,
            course.course_id,
        )

        result["skills"] = skills

        seen = set()

        for skill in skills:

            related_list = get_related_skills(
                db,
                skill["skill_id"],
            )

            for item in related_list:

                related_id = item["skill"]["skill_id"]

                unique_key = (
                    related_id,
                    item["relation_type"],
                    item["direction"],
                )

                if unique_key in seen:
                    continue

                seen.add(unique_key)

                result["related_skills"].append({
                    "source_skill": skill,
                    **item,
                })

        return result

    return result

