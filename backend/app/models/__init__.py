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

# Model ôn tập của Tuấn
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.review_question import ReviewQuestion
from app.models.review_question_meta import ReviewQuestionMeta
from app.models.review_attempt import ReviewAttempt, ReviewAnswer
from app.models.review_due_reminder import ReviewDueReminder
from app.models.review_skill_scope import ReviewSkillScope
from app.models.review_question_report import ReviewQuestionReport

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

    # Ôn tập
    "KnowledgeChunk",
    "ReviewQuestion",
    "ReviewQuestionMeta",
    "ReviewAttempt",
    "ReviewSkillScope",
    "ReviewQuestionReport",
    "ReviewAnswer",
    "ReviewDueReminder",

    # Chatbot Tutor
    "ChatSession",
    "ChatMessage",

    # Feedback
    "Feedback",
]
