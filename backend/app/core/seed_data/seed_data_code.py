
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text

from app.models import (
    Courses,
    Skills,
    CourseSkill,
    SkillRelation,
    LearningPath,
    LearningPathNode,
    LearningPathEdge,
)

from pathlib import Path
import json


# Đường dẫn đến thư mục Edumentor-ai/datajson
DATA_DIR = Path(__file__).resolve().parents[4] / "datajson"


def normalize_schedule(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "" or value.lower() == "none":
        return None

    return value


def normalize_num_enrolled(value):
    if value is None:
        return None

    value = str(value).strip()

    if not value or value.lower() in {
        "none",
        "enrollment number not found"
    }:
        return None

    return int(value.replace(",", ""))


def normalize_rating(value):
    if value is None:
        return None

    value = str(value).strip()

    if not value or value.lower() in {
        "none",
        "rating not found"
    }:
        return None

    return float(value)


def normalize_num_reviews(value):
    if value is None:
        return None

    value = str(value).strip()

    if not value or value.lower() == "none":
        return None

    return int(float(value))


def seed_data(dbSession) -> None:
    db: Session = dbSession

    try:
        # =====================================
        # 1. SKILLS
        # =====================================
        if db.execute(
            select(func.count(Skills.skill_id))
        ).scalar_one() == 0:

            data_file = DATA_DIR / "skill_table.json"

            with open(data_file, "r", encoding="utf-8") as file:
                skills_list = json.load(file)

            loaded_data = [
                Skills(
                    skill_id=each["skill_id"],
                    skill=each["skill"],
                    is_active=True
                )
                for each in skills_list
            ]

            if loaded_data:
                db.add_all(loaded_data)
                db.flush()
                db.commit()

                print(f"Loaded {len(loaded_data)} skills")

        # =====================================
        # 2. COURSES
        # =====================================
        if db.execute(
            select(func.count(Courses.course_id))
        ).scalar_one() == 0:

            data_file = DATA_DIR / "course_table.json"

            with open(data_file, "r", encoding="utf-8") as file:
                courses_list = json.load(file)

            loaded_data = []

            for each in courses_list:
                # Giữ lại course_id từ JSON
                course = each.copy()

                # Chuẩn hóa dữ liệu trước khi lưu DB
                course["schedule"] = normalize_schedule(
                    course.get("schedule")
                )

                course["num_enrolled"] = normalize_num_enrolled(
                    course.get("num_enrolled")
                )

                course["rating"] = normalize_rating(
                    course.get("rating")
                )

                course["num_reviews"] = normalize_num_reviews(
                    course.get("num_reviews")
                )

                # Giữ nguyên image từ JSON
                loaded_data.append(Courses(**course))

            if loaded_data:
                db.add_all(loaded_data)
                db.flush()
                db.commit()

                print(f"Loaded {len(loaded_data)} courses")

        # =====================================
        # ĐỒNG BỘ SEQUENCE
        # =====================================
        # Vì course_id và skill_id được import từ JSON
        # nên cần đồng bộ sequence để ID tự tăng không bị trùng.

        db.execute(text("""
            SELECT setval(
                pg_get_serial_sequence('courses', 'course_id'),
                COALESCE(MAX(course_id), 1),
                MAX(course_id) IS NOT NULL
            )
            FROM courses
        """))

        db.execute(text("""
            SELECT setval(
                pg_get_serial_sequence('skills', 'skill_id'),
                COALESCE(MAX(skill_id), 1),
                MAX(skill_id) IS NOT NULL
            )
            FROM skills
        """))

        db.commit()

        # =====================================
        # 3. COURSE_SKILL
        # =====================================
        if db.execute(
            select(func.count()).select_from(CourseSkill)
        ).scalar_one() == 0:

            data_file = DATA_DIR / "course_skill_relation.json"

            with open(data_file, "r", encoding="utf-8") as file:
                course_skill_list = json.load(file)

            loaded_data = []

            for each in course_skill_list:
                course_skill = {
                    k: v
                    for k, v in each.items()
                    if k != "title" and k != "skill"
                }

                loaded_data.append(
                    CourseSkill(**course_skill)
                )

            if loaded_data:
                db.add_all(loaded_data)
                db.flush()
                db.commit()

                print(f"Loaded {len(loaded_data)} course-skill relations")

        # =====================================
        # 4. SKILL_RELATION
        # =====================================
        if db.execute(
            select(func.count()).select_from(SkillRelation)
        ).scalar_one() == 0:

            data_file = DATA_DIR / "skill_relation.json"

            with open(data_file, "r", encoding="utf-8") as file:
                relations_list = json.load(file)

            loaded_data = [
                SkillRelation(
                    from_skill_id=each["from_skill_id"],
                    to_skill_id=each["to_skill_id"],
                    relation_type=each["relation_type"]
                )
                for each in relations_list
            ]

            if loaded_data:
                db.add_all(loaded_data)
                db.flush()
                db.commit()

                print(f"Loaded {len(loaded_data)} skill relations")

        # =====================================
        # 5. LEARNING PATH
        # GIỮ NGUYÊN LOGIC CỦA NHÓM
        # =====================================
        if (
            db.execute(
                select(func.count()).select_from(LearningPath)
            ).scalar_one() == 0

            and db.execute(
                select(func.count()).select_from(LearningPathNode)
            ).scalar_one() == 0

            and db.execute(
                select(func.count()).select_from(LearningPathEdge)
            ).scalar_one() == 0
        ):

            data_file_list = [
                DATA_DIR / "studentsRecord_0001_0300.json",
                DATA_DIR / "studentsRecord_0301_0600.json",
                DATA_DIR / "studentsRecord_0601_0900_and_1401_1500.json",
                DATA_DIR / "studentsRecord_0901_1200.json"
            ]

            for data_file in data_file_list:

                with open(data_file, "r", encoding="utf-8") as file:
                    historical_records = json.load(file)

                skills = db.execute(
                    select(Skills.skill_id, Skills.skill)
                ).all()

                skill_ids = {
                    skill.skill: skill.skill_id
                    for skill in skills
                }

                paths = [
                    LearningPath(
                        student_id=int(record["student_id"]),
                        original_query=record["goal_session"]["original_query"],
                        goal_type=record["goal_session"]["goal_type"],
                        status=record["learning_path"]["status"],
                    )
                    for record in historical_records
                ]

                if paths:
                    db.add_all(paths)
                    db.flush()
                    print(f"Loaded {len(paths)} learning paths")

                nodes = [
                    LearningPathNode(
                        path_id=path.record_id,
                        skill_id=skill_ids[node["skill_name"]],
                        node_role=node["node_role"],
                        is_target=node["is_target"],
                        added_by=node["added_by"],
                        is_required=node["is_required"],
                        display_order=node["display_order"],
                    )
                    for record, path in zip(historical_records, paths)
                    for node in record["nodes"]
                ]

                if nodes:
                    db.add_all(nodes)
                    print(f"Loaded {len(nodes)} learning path nodes")

                edges = [
                    LearningPathEdge(
                        path_id=path.record_id,
                        from_skill_id=skill_ids[edge["from_skill_name"]],
                        to_skill_id=skill_ids[edge["to_skill_name"]],
                        relation_type=edge["relation_type"],
                    )
                    for record, path in zip(historical_records, paths)
                    for edge in record["edges"]
                ]

                if edges:
                    db.add_all(edges)
                    print(f"Loaded {len(edges)} learning path edges")

                db.commit()

            return

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
