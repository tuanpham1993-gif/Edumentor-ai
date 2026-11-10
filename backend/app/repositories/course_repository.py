from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, delete
from app.models.course import Courses
from app.models.course_skill import CourseSkill
from app.models.skill import Skills


class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, course_id: int) -> Optional[Courses]:
        return self.db.get(Courses, course_id)

    def get_by_url(self, url: str) -> Optional[Courses]:
        stmt = select(Courses).where(Courses.url == url)
        return self.db.execute(stmt).scalars().unique().one_or_none()

    def list_courses(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        level: Optional[str] = None,
    ) -> Tuple[int, List[Courses]]:
        stmt = select(Courses)

        if search:
            search_term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Courses.title.ilike(search_term),
                    Courses.description.ilike(search_term),
                    Courses.instructor.ilike(search_term),
                    Courses.organization.ilike(search_term),
                )
            )

        if level:
            stmt = stmt.where(Courses.level == level)

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        # Pagination
        offset = (page - 1) * page_size
        stmt = stmt.order_by(Courses.course_id.desc()).offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).scalars().unique().all())

        return total, items

    def create(self, course_data: dict) -> Courses:
        course = Courses(**course_data)
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def update(self, course: Courses, update_data: dict) -> Courses:
        for key, value in update_data.items():
            if value is not None and hasattr(course, key):
                setattr(course, key, value)
        self.db.commit()
        self.db.refresh(course)
        return course

    def delete(self, course: Courses) -> None:
        # Xóa các ràng buộc trong CourseSkill trước
        self.db.execute(delete(CourseSkill).where(CourseSkill.course_id == course.course_id))
        self.db.delete(course)
        self.db.commit()

    # CourseSkill relations
    def get_relation(self, course_id: int, skill_id: int) -> Optional[CourseSkill]:
        stmt = select(CourseSkill).where(
            CourseSkill.course_id == course_id,
            CourseSkill.skill_id == skill_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_relations(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        skill_id: Optional[int] = None,
    ) -> Tuple[int, List[dict]]:
        stmt = (
            select(
                CourseSkill.course_id,
                Courses.title.label("course_title"),
                CourseSkill.skill_id,
                Skills.skill.label("skill_name"),
            )
            .join(Courses, CourseSkill.course_id == Courses.course_id)
            .join(Skills, CourseSkill.skill_id == Skills.skill_id)
        )

        if course_id is not None:
            stmt = stmt.where(CourseSkill.course_id == course_id)
        if skill_id is not None:
            stmt = stmt.where(CourseSkill.skill_id == skill_id)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        offset = (page - 1) * page_size
        stmt = stmt.order_by(CourseSkill.course_id.asc(), CourseSkill.skill_id.asc()).offset(offset).limit(page_size)
        rows = self.db.execute(stmt).mappings().all()

        return total, [dict(r) for r in rows]

    def add_relation(self, course_id: int, skill_id: int) -> CourseSkill:
        relation = CourseSkill(course_id=course_id, skill_id=skill_id)
        self.db.add(relation)
        self.db.commit()
        return relation

    def delete_relation(self, course_id: int, skill_id: int) -> bool:
        stmt = delete(CourseSkill).where(
            CourseSkill.course_id == course_id,
            CourseSkill.skill_id == skill_id,
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0

