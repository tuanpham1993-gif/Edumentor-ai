# Model tài khoản của Tuấn
from app.models.user import Users
from app.models.auth_token import PasswordResetToken, RefreshToken
from app.models.user_course import UserCourse
from app.models.user_skill import UserSkill
from app.models.user_profile import UserProfile
from app.models.notification import Notification
from app.models.email_preference import EmailPreference

# Model khóa học, kỹ năng, lộ trình của Hòa
from app.models.course import Courses
from app.models.skill import Skills
from app.models.course_skill import CourseSkill
from app.models.skill_relation import SkillRelation
from app.models.learning_path import (
    LearningPath,
    LearningPathNode,
    LearningPathEdge,
)

# Model AI learning path: hồ sơ học viên theo từng lộ trình.
# Job roles, role aliases, role candidate skills và skill aliases nằm trong Qdrant
# (app/services/ai_reference_service.py), không còn là bảng Postgres.
from app.models.learner_profile import LearnerProfile
from app.models.learning_path_graph import LearningPathGraph
from app.models.profile_reference import Certification, TechnicalDomain

# Model ôn tập của Tuấn
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.review_question import ReviewQuestion
from app.models.review_question_meta import ReviewQuestionMeta
from app.models.review_attempt import ReviewAttempt, ReviewAnswer

# Model chatbot Tutor của Tâm
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage

# Model Feedback của Tâm
from app.models.feedback import Feedback


__all__ = [
    # Tài khoản
    "Users",
    "PasswordResetToken",
    "RefreshToken",
    "UserCourse",
    "UserSkill",
    "UserProfile",
    "Notification",
    "EmailPreference",

    # Khóa học, kỹ năng, lộ trình
    "Courses",
    "Skills",
    "CourseSkill",
    "SkillRelation",
    "LearningPath",
    "LearningPathNode",
    "LearningPathEdge",

    # AI learning path
    "LearnerProfile",
    "LearningPathGraph",
    "Certification",
    "TechnicalDomain",

    # Ôn tập
    "KnowledgeChunk",
    "ReviewQuestion",
    "ReviewQuestionMeta",
    "ReviewAttempt",
    "ReviewAnswer",

    # Chatbot Tutor
    "ChatSession",
    "ChatMessage",

    # Feedback
    "Feedback",
]
