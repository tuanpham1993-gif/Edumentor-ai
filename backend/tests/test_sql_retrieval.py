
# from app.core.database import SessionLocal
# from app.services.sql_retrieval import retrieve_for_query
# from app.ai.query_router import route_query


# test_cases = [
#     "Tôi muốn ôn tập Skill Python",
#     "Tìm khóa học Python",
#     "Tôi muốn ôn tập khóa học Python",
# ]

# db = SessionLocal()

# try:
#     for question in test_cases:

#         print("\n" + "=" * 60)
#         print("CÂU HỎI:", question)

#         route_result = route_query(question)

#         print("ROUTER:", route_result)

#         sql_result = retrieve_for_query(db, route_result)

#         print("SQL RESULT:")
#         print(sql_result)

# finally:
#     db.close()
# from app.core.database import SessionLocal
# from app.services.sql_retrieval import get_related_skills


# db = SessionLocal()

# try:
#     skill_ids = [64, 773, 1082, 1201]

#     for skill_id in skill_ids:
#         print(f"\n===== SKILL ID: {skill_id} =====")

#         related = get_related_skills(db, skill_id)

#         print("RELATED SKILLS:")

#         for item in related:
#             print(item)

# finally:
#     db.close()

# from app.services.sql_retrieval import retrieve_for_query

# route_result = {
#     "intent": "course_review",
#     "entity_type": "course",
#     "entity_name": "EduMentor Course Not Found"
# }

# result = retrieve_for_query(db, route_result)

# print("\n===== COURSE NOT FOUND =====")
# print(result)
# route_result = {
#     "intent": "course_review",
#     "entity_type": "course",
#     "entity_name": "Analytical Solutions to Common Healthcare Problems"
# }

# result = retrieve_for_query(db, route_result)

# print("\n===== COURSE WITHOUT SKILLS =====")
# print(result)



from app.core.database import SessionLocal
from app.services.sql_retrieval import get_related_skills, retrieve_for_query

db = SessionLocal()

# try:
#     skill_ids = [64, 773, 1082, 1201]

#     for skill_id in skill_ids:
#         print(f"\n===== SKILL ID: {skill_id} =====")

#         related = get_related_skills(db, skill_id)

#         print("RELATED SKILLS:")

#         for item in related:
#             print(item)

# finally:
#     db.close()


# route_result = {
#     "intent": "course_review",
#     "entity_type": "course",
#     "entity_name": "Python"
# }

# result = retrieve_for_query(db, route_result)

# print("\n===== COURSE WITH SKILLS =====")
# print(result)

# route_result = {
#     "intent": "course_review",
#     "entity_type": "course",
#     "entity_name": "Analytical Solutions to Common Healthcare Problems"
# }

# result = retrieve_for_query(db, route_result)

# print("\n===== COURSE WITHOUT SKILLS =====")
# print(result)

route_result = {
    "intent": "course_review",
    "entity_type": "course",
    "entity_name": "EduMentor Course Not Found"
}

result = retrieve_for_query(db, route_result)

print("\n===== COURSE NOT FOUND =====")
print(result)