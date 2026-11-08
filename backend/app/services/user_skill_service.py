"""Nghiệp vụ kỹ năng trong hồ sơ (module 01 · Tuấn · GĐ4, 08/11/2026).

4.2 GET   /api/me/skills — xem (chỉ đọc, không commit)
4.3 PATCH /api/me/skills — thêm / đổi / gỡ trong MỘT lần lưu (S1–S4, S6)

Quyết định của thầy (S6, 08/11): người dùng được thay đổi MỌI kỹ năng trong hồ sơ của mình,
kể cả kỹ năng đạt qua bài ôn tập; admin không sửa dữ liệu người dùng (không có API admin nào ở đây).
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import Users
from app.repositories import user_skill_repository
from app.schemas.user_skill import UpdateSkillsRequest


class SkillChangeError(Exception):
    """Lỗi chung của PATCH; `skill_ids` = các kỹ năng gây lỗi (để báo cho người dùng)."""

    def __init__(self, skill_ids):
        super().__init__(skill_ids)
        self.skill_ids = sorted(skill_ids)


class SkillNotInCatalogError(SkillChangeError):
    """S4 — thêm kỹ năng không có trong danh mục hoặc đã bị ẩn (is_active=False) → 422."""


class SkillAlreadyInProfileError(SkillChangeError):
    """S2 — thêm kỹ năng đã có trong hồ sơ → 409."""


class SkillNotInProfileError(SkillChangeError):
    """S3 — đổi / gỡ kỹ năng không có trong hồ sơ → 404."""


def list_skills(db: Session, user: Users, *, status: str | None = None) -> list[dict]:
    """Kỹ năng của người đang đăng nhập; status=None → tất cả."""
    rows = user_skill_repository.list_by_user(db, user.user_id, status)
    return [
        {
            "skill_id": user_skill.skill_id,
            "skill": skill_name,
            "status": user_skill.status,
            "source": user_skill.source,
            "updated_at": user_skill.updated_at,
        }
        for user_skill, skill_name in rows
    ]


def update_skills(db: Session, user: Users, request: UpdateSkillsRequest) -> list[dict]:
    """Áp dụng mọi thay đổi của một lần bấm "Lưu" — TẤT CẢ hoặc KHÔNG GÌ (FR-04).

    Bước 1 — kiểm tra toàn bộ, chưa ghi gì:  S4 → S2 → S3 (lỗi nào gặp trước báo trước).
    Bước 2 — ghi tất cả rồi commit MỘT lần. Có lỗi ở bước 1 → chưa ghi gì nên không cần hoàn tác.
    Trả về danh sách kỹ năng SAU khi lưu → frontend vẽ lại ngay, không phải gọi GET lần nữa.
    """
    add_ids = [c.skill_id for c in request.add]
    change_ids = [c.skill_id for c in request.update] + list(request.remove)

    # S4: kỹ năng thêm mới phải có trong danh mục và đang bật
    missing = set(add_ids) - user_skill_repository.active_skill_ids(db, add_ids)
    if missing:
        raise SkillNotInCatalogError(missing)

    existing = user_skill_repository.get_many(db, user.user_id, add_ids + change_ids)
    # S2: không thêm trùng
    duplicated = [i for i in add_ids if i in existing]
    if duplicated:
        raise SkillAlreadyInProfileError(duplicated)
    # S3: chỉ đổi / gỡ kỹ năng đang có trong hồ sơ
    absent = [i for i in change_ids if i not in existing]
    if absent:
        raise SkillNotInProfileError(absent)

    for change in request.add:
        user_skill_repository.add(
            db,
            user_id=user.user_id,
            skill_id=change.skill_id,
            status=change.status,
            source="manual",
        )
    for change in request.update:
        row = existing[change.skill_id]
        if row.status != change.status:
            row.status = change.status
            # Trạng thái giờ do chính người dùng chọn (S6) → nguồn là "manual"
            row.source = "manual"
    for skill_id in request.remove:
        user_skill_repository.delete(db, existing[skill_id])

    try:
        db.commit()
    except IntegrityError:
        # Hai tab cùng lưu một lúc: tab kia đã thêm kỹ năng này trước → khóa chính kép chặn.
        db.rollback()
        raise SkillAlreadyInProfileError(add_ids) from None
    return list_skills(db, user)
