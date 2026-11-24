"""Truy vấn bảng review_skill_scopes (module 09 · Tuấn · G3.0, 24/11/2026). Chỉ ĐỌC skills / courses (bảng của Hòa /
Khôi); chỉ GHI review_skill_scopes. Không commit — service commit."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.course import Courses
from app.models.course_skill import CourseSkill
from app.models.review_skill_scope import ReviewSkillScope
from app.models.skill import Skills
from app.models.user import Users


def unlabeled_skills(db: Session, limit: int | None = None) -> list[tuple[int, str]]:
    """Kỹ năng đang dùng CHƯA có nhãn, theo skill_id."""
    stmt = (
        select(Skills.skill_id, Skills.skill)
        .outerjoin(ReviewSkillScope, ReviewSkillScope.skill_id == Skills.skill_id)
        .where(Skills.is_active.is_(True), ReviewSkillScope.skill_id.is_(None))
        .order_by(Skills.skill_id)
    )
    if limit:
        stmt = stmt.limit(limit)
    return [(i, n) for i, n in db.execute(stmt).all()]


def top_course_titles(db: Session, skill_ids: list[int], per_skill: int = 2) -> dict[int, list[str]]:
    """skill_id → tên tối đa `per_skill` khóa NHIỀU học viên nhất có kỹ năng đó (gửi kèm khi phân loại)."""
    if not skill_ids:
        return {}
    rows = db.execute(
        select(CourseSkill.skill_id, Courses.title, Courses.num_enrolled)
        .join(Courses, Courses.course_id == CourseSkill.course_id)
        .where(CourseSkill.skill_id.in_(skill_ids))
    ).all()
    grouped: dict[int, list[tuple[int, str]]] = {}
    for skill_id, title, enrolled in rows:
        grouped.setdefault(skill_id, []).append((enrolled or 0, title))
    return {s: [t for _, t in sorted(v, key=lambda x: (-x[0], x[1]))[:per_skill]] for s, v in grouped.items()}


def get(db: Session, skill_id: int) -> ReviewSkillScope | None:
    return db.get(ReviewSkillScope, skill_id)


def counts(db: Session) -> dict[str, int]:
    """Số kỹ năng ĐANG DÙNG theo nhãn + số chưa có nhãn."""
    rows = db.execute(
        select(ReviewSkillScope.label, func.count())
        .join(Skills, Skills.skill_id == ReviewSkillScope.skill_id)
        .where(Skills.is_active.is_(True))
        .group_by(ReviewSkillScope.label)
    ).all()
    out = {"open": 0, "closed": 0, "unsure": 0}
    out.update({label: n for label, n in rows})
    total = db.scalar(select(func.count()).select_from(Skills).where(Skills.is_active.is_(True)))
    out["unlabeled"] = total - sum(out.values())
    return out


def page(
    db: Session,
    *,
    label: str | None,
    category: str | None,
    source: str | None,
    q: str | None,
    skill_id: int | None,
    offset: int,
    limit: int,
) -> tuple[list[tuple], int]:
    """Danh sách cho admin: (scope | None, skill_id, skill, tên người sửa). label="unlabeled" → kỹ năng chưa có nhãn."""
    updater = Users.full_name.label("updated_by_name")
    stmt = (
        select(ReviewSkillScope, Skills.skill_id, Skills.skill, updater)
        .select_from(Skills)
        .outerjoin(ReviewSkillScope, ReviewSkillScope.skill_id == Skills.skill_id)
        .outerjoin(Users, Users.user_id == ReviewSkillScope.updated_by)
        .where(Skills.is_active.is_(True))
    )
    if label == "unlabeled":
        stmt = stmt.where(ReviewSkillScope.skill_id.is_(None))
    elif label:
        stmt = stmt.where(ReviewSkillScope.label == label)
    if category:
        stmt = stmt.where(ReviewSkillScope.category == category)
    if source:
        stmt = stmt.where(ReviewSkillScope.source == source)
    if q:
        stmt = stmt.where(Skills.skill.ilike(f"%{q}%"))
    if skill_id is not None:
        stmt = stmt.where(Skills.skill_id == skill_id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.execute(stmt.order_by(Skills.skill_id).offset(offset).limit(limit)).all()
    return [tuple(r) for r in rows], total


def skill_name(db: Session, skill_id: int) -> str | None:
    return db.scalar(select(Skills.skill).where(Skills.skill_id == skill_id, Skills.is_active.is_(True)))
