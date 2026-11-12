# """
# Script tạo dữ liệu mẫu (mock data) để test các API:
# - Skills (kỹ năng)
# - Courses (khóa học)
# - CourseSkill (liên kết khóa học - kỹ năng)
# """
# import sys
# from pathlib import Path

# # Thêm backend vào sys.path
# backend_dir = Path(__file__).resolve().parent.parent
# sys.path.insert(0, str(backend_dir))

# from app.core.database import SessionLocal
# from app.models.course import Courses
# from app.models.skill import Skills
# from app.models.course_skill import CourseSkill

# def seed():
#     db = SessionLocal()
#     try:
#         # 1. Kiểm tra nếu đã có skills thì bỏ qua
#         existing_skills = db.query(Skills).count()
#         if existing_skills == 0:
#             print("🌱 Đang thêm dữ liệu Skills mẫu...")
#             skills = [
#                 Skills(skill="Python Programming", is_active=True),
#                 Skills(skill="FastAPI", is_active=True),
#                 Skills(skill="PostgreSQL & SQL", is_active=True),
#                 Skills(skill="ReactJS & Frontend", is_active=True),
#                 Skills(skill="Machine Learning Basics", is_active=True),
#                 Skills(skill="Docker & DevOps", is_active=True),
#             ]
#             db.add_all(skills)
#             db.commit()
#             print(f"✅ Đã thêm {len(skills)} skills!")
#         else:
#             print(f"ℹ️ Đã có {existing_skills} skills trong database.")

#         # 2. Kiểm tra nếu đã có courses thì bỏ qua
#         existing_courses = db.query(Courses).count()
#         if existing_courses == 0:
#             print("🌱 Đang thêm dữ liệu Courses mẫu...")
#             courses = [
#                 Courses(
#                     title="Python for Everybody Specialization",
#                     description="Khóa học Python nền tảng từ cơ bản đến nâng cao cho người mới bắt đầu.",
#                     instructor="Dr. Charles Severance",
#                     organization="University of Michigan",
#                     level="Beginner",
#                     rating=4.8,
#                     num_reviews=12500,
#                     num_enrolled=450000,
#                     schedule="Approx. 2 months to complete",
#                     url="https://www.coursera.org/specializations/python",
#                     modules="5 courses",
#                 ),
#                 Courses(
#                     title="Building REST APIs with FastAPI and Python",
#                     description="Học cách xây dựng Web API hiện đại, hiệu năng cao với FastAPI và SQLAlchemy.",
#                     instructor="Jose Salvatierra",
#                     organization="Teclado",
#                     level="Intermediate",
#                     rating=4.7,
#                     num_reviews=3400,
#                     num_enrolled=25000,
#                     schedule="Approx. 1 month to complete",
#                     url="https://fastapi.tiangolo.com/tutorial/",
#                     modules="4 modules",
#                 ),
#                 Courses(
#                     title="The Complete React Developer Course",
#                     description="Lập trình React toàn diện: Hooks, Redux, Context API và triển khai ứng dụng.",
#                     instructor="Andrew Mead",
#                     organization="Udemy",
#                     level="All Levels",
#                     rating=4.6,
#                     num_reviews=8900,
#                     num_enrolled=120000,
#                     schedule="39 hours on-demand video",
#                     url="https://react.dev/",
#                     modules="12 sections",
#                 ),
#                 Courses(
#                     title="Machine Learning Specialization",
#                     description="Học các thuật toán học máy từ chuyên gia hàng đầu AI Andrew Ng.",
#                     instructor="Andrew Ng",
#                     organization="DeepLearning.AI",
#                     level="Beginner",
#                     rating=4.9,
#                     num_reviews=22000,
#                     num_enrolled=800000,
#                     schedule="Approx. 3 months to complete",
#                     url="https://www.coursera.org/specializations/machine-learning-introduction",
#                     modules="3 courses",
#                 ),
#             ]
#             db.add_all(courses)
#             db.commit()
#             print(f"✅ Đã thêm {len(courses)} courses!")

#             # 3. Gắn liên kết Course <-> Skill
#             all_skills = {s.skill: s.skill_id for s in db.query(Skills).all()}
#             all_courses = {c.title: c.course_id for c in db.query(Courses).all()}

#             relations = [
#                 ("Python for Everybody Specialization", "Python Programming"),
#                 ("Building REST APIs with FastAPI and Python", "Python Programming"),
#                 ("Building REST APIs with FastAPI and Python", "FastAPI"),
#                 ("Building REST APIs with FastAPI and Python", "PostgreSQL & SQL"),
#                 ("The Complete React Developer Course", "ReactJS & Frontend"),
#                 ("Machine Learning Specialization", "Python Programming"),
#                 ("Machine Learning Specialization", "Machine Learning Basics"),
#             ]

#             course_skills = []
#             for course_title, skill_name in relations:
#                 c_id = all_courses.get(course_title)
#                 s_id = all_skills.get(skill_name)
#                 if c_id and s_id:
#                     course_skills.append(CourseSkill(course_id=c_id, skill_id=s_id))

#             if course_skills:
#                 db.add_all(course_skills)
#                 db.commit()
#                 print(f"✅ Đã gắn {len(course_skills)} liên kết khóa học - kỹ năng!")
#         else:
#             print(f"ℹ️ Đã có {existing_courses} courses trong database.")

#     except Exception as e:
#         db.rollback()
#         print(f"❌ Lỗi khi seed dữ liệu: {e}")
#     finally:
#         db.close()

# if __name__ == "__main__":
#     seed()

