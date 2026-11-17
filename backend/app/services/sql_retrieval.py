
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, case, func

from app.models import (
    Courses,
    Skills,
    CourseSkill,
    SkillRelation,
)


# ==========================================
# 0. GIỚI HẠN DỮ LIỆU
# ==========================================

MAX_SKILLS = 5
MAX_COURSES = 5
MAX_RELATED_SKILLS = 5


# ==========================================
# 1. CHUYỂN MODEL THÀNH DICTIONARY
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
# 2. TÌM MỘT SKILL
# ==========================================

def find_skill(db: Session, skill_name: str):

    if not skill_name:
        return None

    # Ưu tiên tên Skill chính xác
    skill = db.execute(
        select(Skills).where(
            Skills.skill.ilike(skill_name),
            Skills.is_active.is_(True),
        )
    ).unique().scalars().first()

    if skill:
        return skill

    # Tìm gần đúng
    skill = db.execute(
        select(Skills)
        .where(
            Skills.skill.ilike(f"%{skill_name}%"),
            Skills.is_active.is_(True),
        )
        .order_by(Skills.skill)
        .limit(1)
    ).unique().scalars().first()

    if skill:
        return skill

    # Hỗ trợ tìm kiếm khi tên có phần chú thích trong ngoặc (ví dụ: "Web Accessibility (a11y)")
    if "(" in skill_name and ")" in skill_name:
        base_name = re.sub(r"\(.*?\)", "", skill_name).strip()
        inside_match = re.search(r"\((.*?)\)", skill_name)
        inside_name = inside_match.group(1).strip() if inside_match else ""

        for candidate in [base_name, inside_name]:
            if not candidate:
                continue
            cand_skill = db.execute(
                select(Skills)
                .where(
                    or_(
                        Skills.skill.ilike(candidate),
                        Skills.skill.ilike(f"%{candidate}%"),
                    ),
                    Skills.is_active.is_(True),
                )
                .order_by(Skills.skill)
                .limit(1)
            ).unique().scalars().first()
            if cand_skill:
                return cand_skill

    return None


# ==========================================
# 3. TÌM NHIỀU SKILL THEO CHỦ ĐỀ
# ==========================================

def search_skills(
    db: Session,
    keyword: str,
    limit: int = MAX_SKILLS,
) -> list:

    if not keyword:
        return []

    limit = max(1, min(limit, MAX_SKILLS))

    # Ưu tiên tên Skill khớp chính xác,
    # sau đó mới đến tên Skill chứa từ khóa.
    exact_match = case(
        (Skills.skill.ilike(keyword), 0),
        else_=1,
    )

    skills = db.execute(
        select(Skills)
        .where(
            Skills.skill.ilike(f"%{keyword}%"),
            Skills.is_active.is_(True),
        )
        .order_by(
            exact_match,
            Skills.skill,
        )
        .limit(limit)
    ).unique().scalars().all()

    return [skill_to_dict(skill) for skill in skills]


# ==========================================
# 4. TÌM COURSE
# ==========================================

def find_course(db: Session, course_name: str):

    if not course_name:
        return None

    course = db.execute(
        select(Courses).where(
            Courses.title.ilike(course_name)
        )
    ).unique().scalars().first()

    if course:
        return course

    return db.execute(
        select(Courses)
        .where(
            Courses.title.ilike(f"%{course_name}%")
        )
        .order_by(Courses.title)
        .limit(1)
    ).unique().scalars().first()


# ==========================================
# 5. TÌM COURSE THEO SKILL
# ==========================================

def get_courses_by_skill(
    db: Session,
    skill_id: int,
    limit: int = MAX_COURSES,
) -> list:

    limit = max(1, min(limit, MAX_COURSES))

    courses = db.execute(
        select(Courses)
        .join(
            CourseSkill,
            Courses.course_id == CourseSkill.course_id,
        )
        .where(
            CourseSkill.skill_id == skill_id
        )
        .order_by(
            Courses.rating.desc().nullslast(),
            Courses.title,
        )
        .limit(limit)
    ).unique().scalars().all()

    return [course_to_dict(course) for course in courses]


# ==========================================
# 6. TÌM SKILL THEO COURSE
# ==========================================

def get_skills_by_course(
    db: Session,
    course_id: int,
    limit: int = MAX_SKILLS,
) -> list:

    limit = max(1, min(limit, MAX_SKILLS))

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
        .limit(limit)
    ).unique().scalars().all()

    return [skill_to_dict(skill) for skill in skills]


# ==========================================
# 7. TÌM SKILL LIÊN QUAN
# ==========================================

def get_related_skills(
    db: Session,
    skill_id: int,
    limit: int = MAX_RELATED_SKILLS,
) -> list:

    limit = max(1, min(limit, MAX_RELATED_SKILLS))

    relations = db.execute(
        select(SkillRelation)
        .where(
            or_(
                SkillRelation.from_skill_id == skill_id,
                SkillRelation.to_skill_id == skill_id,
            )
        )
        .limit(limit * 2)
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

        related_skill = db.execute(
            select(Skills).where(
                Skills.skill_id == related_skill_id,
                Skills.is_active.is_(True),
            )
        ).scalars().first()

        if related_skill is None:
            continue

        if relation.relation_type == "related":
            unique_key = (
                related_skill_id,
                relation.relation_type,
            )
        else:
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

        if len(results) >= limit:
            break

    return results


# ==========================================
# 8. TÌM NHIỀU COURSE THEO TỪ KHÓA
# ==========================================

def search_courses(
    db: Session,
    keyword: str,
    limit: int = MAX_COURSES,
) -> list:

    if not keyword:
        return []

    limit = max(1, min(limit, MAX_COURSES))

    clean_kw = re.sub(r"\(.*?\)", "", keyword).strip() or keyword

    courses = db.execute(
        select(Courses)
        .where(
            or_(
                Courses.title.ilike(f"%{keyword}%"),
                Courses.title.ilike(f"%{clean_kw}%"),
            )
        )
        .order_by(
            Courses.rating.desc().nullslast()
        )
        .limit(limit)
    ).unique().scalars().all()

    return [course_to_dict(course) for course in courses]


# ==========================================
# 8.1. TÌM COURSE THEO TỔ CHỨC / TRƯỜNG ĐẠI HỌC
# ==========================================

def get_courses_by_organization(
    db: Session,
    org_name: str,
    limit: int = MAX_COURSES,
) -> list:

    if not org_name:
        return []

    limit = max(1, min(limit, MAX_COURSES))

    courses = db.execute(
        select(Courses)
        .where(Courses.organization.ilike(f"%{org_name}%"))
        .order_by(Courses.rating.desc().nullslast())
        .limit(limit)
    ).unique().scalars().all()

    return [course_to_dict(course) for course in courses]


# ==========================================
# 8.2. TÌM COURSE THEO GIẢNG VIÊN
# ==========================================

def get_courses_by_instructor(
    db: Session,
    instructor_name: str,
    limit: int = MAX_COURSES,
) -> list:

    if not instructor_name:
        return []

    limit = max(1, min(limit, MAX_COURSES))

    courses = db.execute(
        select(Courses)
        .where(Courses.instructor.ilike(f"%{instructor_name}%"))
        .order_by(Courses.rating.desc().nullslast())
        .limit(limit)
    ).unique().scalars().all()

    return [course_to_dict(course) for course in courses]


# ==========================================
# 8.3. TÌM COURSE THEO ĐÁNH GIÁ (RATING)
# ==========================================

def get_courses_by_rating(
    db: Session,
    min_rating: float = 4.8,
    limit: int = MAX_COURSES,
) -> list:

    limit = max(1, min(limit, MAX_COURSES))

    courses = db.execute(
        select(Courses)
        .where(Courses.rating >= min_rating)
        .order_by(
            Courses.rating.desc(),
            Courses.num_reviews.desc().nullslast(),
        )
        .limit(limit)
    ).unique().scalars().all()

    return [course_to_dict(course) for course in courses]


# ==========================================
# 8.4. TÌM COURSE THEO CẤP ĐỘ (LEVEL)
# ==========================================

def get_courses_by_level(
    db: Session,
    level: str,
    limit: int = MAX_COURSES,
) -> list:

    if not level:
        return []

    limit = max(1, min(limit, MAX_COURSES))

    courses = db.execute(
        select(Courses)
        .where(Courses.level.ilike(f"%{level}%"))
        .order_by(
            Courses.rating.desc().nullslast(),
            Courses.num_reviews.desc().nullslast(),
        )
        .limit(limit)
    ).unique().scalars().all()

    return [course_to_dict(course) for course in courses]


# ==========================================
# 8.5. TÌM COURSE ĐƯỢC HỌC NHIỀU NHẤT / NỔI BẬT (POPULAR)
# ==========================================

def get_popular_courses(
    db: Session,
    limit: int = MAX_COURSES,
) -> list:

    limit = max(1, min(limit, MAX_COURSES))

    courses = db.execute(
        select(Courses)
        .order_by(
            Courses.num_enrolled.desc().nullslast(),
            Courses.rating.desc().nullslast(),
        )
        .limit(limit)
    ).unique().scalars().all()

    return [course_to_dict(course) for course in courses]


# ==========================================
# 8.6. TÌM SKILL NỔI BẬT / PHỔ BIẾN (POPULAR SKILLS)
# ==========================================

def get_popular_skills(
    db: Session,
    limit: int = MAX_SKILLS,
) -> list:

    limit = max(1, min(limit, MAX_SKILLS))

    skills = db.execute(
        select(Skills)
        .join(
            CourseSkill,
            Skills.skill_id == CourseSkill.skill_id,
        )
        .where(Skills.is_active.is_(True))
        .group_by(Skills.skill_id)
        .order_by(
            func.count(CourseSkill.course_id).desc(),
            Skills.skill,
        )
        .limit(limit)
    ).unique().scalars().all()

    return [skill_to_dict(s) for s in skills]


# ==========================================
# 9. SQL RETRIEVAL CHÍNH
# ==========================================

def retrieve_for_query(
    db: Session,
    route_result: dict,
) -> dict:

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
    # 1. TÌM NHIỀU SKILL THEO CHỦ ĐỀ
    # ======================================

    if intent == "skill_search":

        if entity_type == "popular":

            skills = get_popular_skills(
                db,
                limit=MAX_SKILLS,
            )
            result["skills"] = skills
            result["found"] = len(skills) > 0
            return result

        skill = find_skill(db, entity_name) if entity_name else None

        if skill is not None:
            result["skill"] = skill_to_dict(skill)
            result["related_skills"] = get_related_skills(
                db,
                skill.skill_id,
            )

        skills = search_skills(
            db,
            entity_name,
            limit=MAX_SKILLS,
        )

        result["skills"] = skills
        result["found"] = bool(
            result["skill"] or result["skills"] or result["related_skills"]
        )

        return result

    # ======================================
    # 2. TÌM COURSE
    # ======================================

    if intent == "course_search":

        if entity_type == "popular":

            courses = get_popular_courses(
                db,
                limit=MAX_COURSES,
            )
            result["courses"] = courses
            result["found"] = len(courses) > 0
            return result

        if entity_type == "organization":

            courses = get_courses_by_organization(
                db,
                entity_name,
            )
            result["courses"] = courses
            result["found"] = len(courses) > 0
            return result

        if entity_type == "instructor":

            courses = get_courses_by_instructor(
                db,
                entity_name,
            )
            result["courses"] = courses
            result["found"] = len(courses) > 0
            return result

        if entity_type == "rating":

            try:
                min_r = float(entity_name) if entity_name else 4.8
            except (ValueError, TypeError):
                min_r = 4.8

            courses = get_courses_by_rating(
                db,
                min_rating=min_r,
            )
            result["courses"] = courses
            result["found"] = len(courses) > 0
            return result

        if entity_type == "level":

            courses = get_courses_by_level(
                db,
                entity_name,
            )
            result["courses"] = courses
            result["found"] = len(courses) > 0
            return result

        if entity_type == "skill":

            skill = find_skill(db, entity_name)

            if skill is not None:
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

            # Fallback: Nếu không tìm thấy trong bảng Skills, tìm trực tiếp qua tiêu đề/mô tả khóa học
            courses = search_courses(
                db,
                entity_name,
            )

            if courses:
                result["courses"] = courses
                result["found"] = True

            return result

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
    # 3. TÌM MỘT SKILL CỤ THỂ
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
    # 4. TÌM COURSE VÀ SKILL LIÊN QUAN
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

            remaining = MAX_RELATED_SKILLS - len(
                result["related_skills"]
            )

            if remaining <= 0:
                break

            related_list = get_related_skills(
                db,
                skill["skill_id"],
                limit=remaining,
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

                if len(result["related_skills"]) >= MAX_RELATED_SKILLS:
                    break

        return result

    return result
