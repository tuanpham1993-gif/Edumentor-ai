from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models import (
    Courses, Skills, CourseSkill, SkillRelation, 
    LearningPath, LearningPathNode, LearningPathEdge)
from pathlib import Path
import json

def normalize_schedule(value):
    if value is None: return None

    value = str(value).strip()
    if value == "" or value.lower() == "none":
        return None
    return value


def normalize_num_enrolled(value):
    if value is None: return None
    value = str(value).strip()
    if not value or value.lower() in {"none", "enrollment number not found"}:
        return None
    return int(value.replace(",", ""))

def normalize_rating(value):
    if value is None: return None
    value = str(value).strip()
    if not value or value.lower() in {"none", "rating not found"}:
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
        #skills
        if db.execute(select(func.count(Skills.skill_id))).scalar_one() == 0:
            loaded_data = []
            data_file = Path(__file__).resolve().parents[5]/"datajson/skill_table.json"
            with open(data_file, "r", encoding='utf-8') as file:
                skills_list = json.load(file)
                for each in skills_list:
                    for k, v in each.items():
                        if(k != "skill_id"):
                            loaded_data.append(Skills(**{k: v}))
            if(len(loaded_data) > 0):
                db.add_all(loaded_data)
                db.flush()
                db.commit()
        #courses
        if db.execute(select(func.count(Courses.course_id))).scalar_one() == 0:
            loaded_data = []
            data_file = data_file = Path(__file__).resolve().parents[5]/"datajson/course_table.json"
            with open(data_file, "r", encoding='utf-8') as file:
                courses_list = json.load(file)
                loaded_data = []
                for each in courses_list:
                    course = { k: v for k, v in each.items() if k != "course_id"}

                    course[ "schedule"] = normalize_schedule(course.get("schedule"))
                    course["num_enrolled"] = normalize_num_enrolled(course.get("num_enrolled"))
                    course["rating"] = normalize_rating(course.get("rating"))
                    course["num_reviews"] = normalize_num_reviews(course.get("num_reviews"))
                    course["image"] = None
                    loaded_data.append(Courses(**course))

                if loaded_data:
                    db.add_all(loaded_data)
                    db.flush()
                    db.commit()

        #course_skill
        if db.execute(select(func.count()).select_from(CourseSkill)).scalar_one() == 0:
            loaded_data = []
            data_file = data_file = Path(__file__).resolve().parents[5]/"datajson/course_skill_relation.json"
            with open(data_file, "r", encoding='utf-8') as file:
                course_skill_list = json.load(file)
                loaded_data = []
                for each in course_skill_list:
                    course_skill = {k: v for k, v in each.items() if k != "title" and k != "skill"}
                    loaded_data.append(CourseSkill(**course_skill))
                if loaded_data:
                    db.add_all(loaded_data)
                    db.commit()

        #skill_relation
        if db.execute(select(func.count()).select_from(SkillRelation)).scalar_one() == 0:
            data_file = Path(__file__).resolve().parents[5]/"datajson/skill_relation.json"
            with open(data_file, "r", encoding="utf-8") as file:
                relations_list = json.load(file)

            loaded_data = [SkillRelation(from_skill_id=each["from_skill_id"],to_skill_id=each["to_skill_id"],relation_type=each["relation_type"]) for each in relations_list]

            if loaded_data:
                db.add_all(loaded_data)
                db.commit()

        #learning_path
        if (db.execute(select(func.count()).select_from(LearningPath)).scalar_one() == 0 and 
            db.execute(select(func.count()).select_from(LearningPathNode)).scalar_one() == 0 and
            db.execute(select(func.count()).select_from(LearningPathEdge)).scalar_one() == 0) :
            data_file = Path(__file__).resolve().parents[5]/"datajson/studentsRecord_0001_0300.json"
            with open(data_file, "r", encoding="utf-8") as file:
                historical_records = json.load(file)
            skills = db.execute(select(Skills.skill_id, Skills.skill)).all()
            skill_ids = {skill.skill: skill.skill_id for skill in skills}

            paths = [
                LearningPath(
                    student_id=int(record["student_id"]),
                    original_query=record["goal_session"]["original_query"],
                    goal_type=record["goal_session"]["goal_type"],
                    status=record["learning_path"]["status"],
                )
                for record in historical_records]

            if(paths):
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

            if (nodes):
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

            if(edges):
                db.add_all(edges)
                print(f"Loaded {len(edges)} learning path edges")
            db.commit()
            return
    except Exception:
        db.rollback()
        raise Exception
    finally:
        db.close()