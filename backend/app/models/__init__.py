
from app.models.course import Courses
from app.models.skill import Skills
from app.models.course_skill import CourseSkill
from app.models.skill_relation import SkillRelation
from app.models.learning_path import LearningPath, LearningPathNode, LearningPathEdge

__all__ = ["Courses", "Skills", "CourseSkill", "SkillRelation", "LearningPath", "LearningPathNode", "LearningPathEdge"]
