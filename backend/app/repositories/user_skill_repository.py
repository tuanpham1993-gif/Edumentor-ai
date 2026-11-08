"""Repository bảng `user_skills` (module 01 · Tuấn · GĐ4, 08/11/2026).

Chỉ truy vấn — KHÔNG commit (service quyết định khi nào lưu hẳn).
Bảng `skills` là của Hòa: chỉ ĐỌC tên kỹ năng (join), không sửa.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.skill import Skills
from app.models.user_skill import UserSkill


def list_by_user(db: Session, user_id: int, status: str | None = None):
    """Kỹ năng trong hồ sơ của một người, kèm tên kỹ năng, sắp theo tên.

    Tương đương SQL:
        SELECT us.*, s.skill FROM user_skills us
        JOIN skills s ON s.skill_id = us.skill_id
        WHERE us.user_id = :user_id [AND us.status = :status]
        ORDER BY s.skill
    Trả về list các cặp (UserSkill, tên kỹ năng).
    """
    query = (
        select(UserSkill, Skills.skill)
        .join(Skills, Skills.skill_id == UserSkill.skill_id)
        .where(UserSkill.user_id == user_id)
        .order_by(Skills.skill)
    )
    if status is not None:
        query = query.where(UserSkill.status == status)
    # .all() trả về các Row (UserSkill, str) — service đổi thành dict cho schema.
    return db.execute(query).all()


# ─────────────── 4.3 PATCH /api/me/skills ───────────────


def active_skill_ids(db: Session, skill_ids: list[int]) -> set[int]:
    """Trong các id gửi lên, id nào CÓ trong danh mục và đang bật (is_active) — dùng cho S4."""
    if not skill_ids:
        return set()
    query = select(Skills.skill_id).where(
        Skills.skill_id.in_(skill_ids), Skills.is_active.is_(True)
    )
    return set(db.scalars(query))


def get_many(db: Session, user_id: int, skill_ids: list[int]) -> dict[int, UserSkill]:
    """Các dòng user_skills của người dùng ứng với skill_ids, dạng {skill_id: dòng} — dùng cho S2, S3."""
    if not skill_ids:
        return {}
    query = select(UserSkill).where(
        UserSkill.user_id == user_id, UserSkill.skill_id.in_(skill_ids)
    )
    return {row.skill_id: row for row in db.scalars(query)}


def add(db: Session, *, user_id: int, skill_id: int, status: str, source: str) -> None:
    db.add(UserSkill(user_id=user_id, skill_id=skill_id, status=status, source=source))


def delete(db: Session, row: UserSkill) -> None:
    db.delete(row)
