
# TẠM NGẮT (tuan/future-auth): model của Hòa, bật lại khi gộp với nhóm.
# from app.models.course import Courses
# from app.models.skill import Skills
# from app.models.course_skill import CourseSkill
# from app.models.skill_relation import SkillRelation
# from app.models.learning_path import LearningPath, LearningPathNode, LearningPathEdge

# Model của Tuấn: import ở đây để create_all tạo bảng, ví dụ:
from app.models.user import Users
from app.models.auth_token import PasswordResetToken

__all__ = ["Users","PasswordResetToken"]
