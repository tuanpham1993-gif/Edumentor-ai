"""Nghiệp vụ kỹ năng trong hồ sơ (module 01 · Tuấn · GĐ4, 08/11/2026).

4.2 GET   /api/me/skills — xem (chỉ đọc, không commit)
4.3 PATCH /api/me/skills — thêm / đổi / gỡ trong MỘT lần lưu (S1–S4, S6)
FĐ6 GET /api/me/skills/suggestions — gợi ý cho ô "Thêm kỹ năng" (học tiếp / liên quan / phổ biến)

Quyết định của thầy (S6, 08/11): người dùng được thay đổi MỌI kỹ năng trong hồ sơ của mình,
kể cả kỹ năng đạt qua bài ôn tập; admin không sửa dữ liệu người dùng (không có API admin nào ở đây).
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import Users
from app.repositories import user_skill_repository
from app.schemas.user_skill import UpdateSkillsRequest
from app.utils import skill_categories


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


def suggest_skills(db: Session, user: Users, *, limit: int = 12) -> list[dict]:
    """Gợi ý kỹ năng CHƯA có trong hồ sơ, theo thứ tự ưu tiên:
    1. next    — kỹ năng của bạn là nền (prerequisite) hoặc được mở rộng (extension) thành kỹ năng này
    2. related — có quan hệ "related" với kỹ năng của bạn
    3. popular — dạy trong nhiều khóa học nhất (lấp chỗ trống, kể cả khi hồ sơ trống)
    """
    rows = user_skill_repository.list_by_user(db, user.user_id)
    mine = {row.skill_id: name for row, name in rows}

    candidates = []  # (ưu tiên, skill_id, reason, via_id)
    for from_id, to_id, relation_type in user_skill_repository.relations_of(
        db, list(mine)
    ):
        if relation_type in ("prerequisite", "extension"):
            if from_id in mine and to_id not in mine:
                candidates.append((0, to_id, "next", from_id))
        elif relation_type == "related":
            other, via = (to_id, from_id) if from_id in mine else (from_id, to_id)
            if other not in mine and via in mine:
                candidates.append((1, other, "related", via))

    names = user_skill_repository.active_skill_names(db, {c[1] for c in candidates})
    picked: dict[int, dict] = {}
    for _, skill_id, reason, via_id in sorted(candidates):
        if len(picked) >= limit:
            break
        if skill_id in names and skill_id not in picked:
            picked[skill_id] = {
                "skill_id": skill_id,
                "skill": names[skill_id],
                "reason": reason,
                "via": mine[via_id],
            }

    if len(picked) < limit:
        exclude = list(mine) + list(picked)
        popular = user_skill_repository.popular_skills(db, exclude, limit - len(picked))
        for skill_id, name, count in popular:
            picked[skill_id] = {
                "skill_id": skill_id,
                "skill": name,
                "reason": "popular",
                "course_count": count,
            }
    return list(picked.values())


# ─────────────── Trang "Khám phá kỹ năng" theo danh mục (FĐ6 — gợi ý của thầy, 08/11) ───────────────


def _catalog(db: Session) -> list[dict]:
    rows = user_skill_repository.active_skills_with_course_count(db)
    return [
        {
            "skill_id": skill_id,
            "skill": name,
            "category": skill_categories.categorize(name),
            "course_count": count,
        }
        for skill_id, name, count in rows
    ]


def skill_categories_with_counts(db: Session) -> list[dict]:
    """Danh mục theo thứ tự cố định (Khác ở cuối) + số kỹ năng mỗi mục."""
    counts: dict[str, int] = {}
    for item in _catalog(db):
        counts[item["category"]] = counts.get(item["category"], 0) + 1
    return [
        {"key": key, "label": skill_categories.LABELS[key], "count": counts.get(key, 0)}
        for key in skill_categories.KEYS
    ]


def browse_catalog(
    db: Session,
    user: Users,
    *,
    category: str | None,
    q: str | None,
    sort: str,
    page: int,
    size: int,
) -> dict:
    """Lọc theo danh mục + chữ tìm, sắp xếp (popular | name), phân trang; đánh dấu kỹ năng đã có."""
    items = _catalog(db)
    if category:
        items = [i for i in items if i["category"] == category]
    if q and q.strip():
        needle = q.strip().lower()
        items = [i for i in items if needle in i["skill"].lower()]
    if sort == "name":
        items.sort(key=lambda i: i["skill"].lower())
    else:  # popular: nhiều khóa học trước, cùng số thì theo tên
        items.sort(key=lambda i: (-i["course_count"], i["skill"].lower()))

    total = len(items)
    page_items = items[(page - 1) * size : page * size]
    mine = {
        row.skill_id: row.status
        for row, _ in user_skill_repository.list_by_user(db, user.user_id)
    }
    for item in page_items:
        item["my_status"] = mine.get(item["skill_id"])
    return {"total": total, "page": page, "size": size, "items": page_items}


# ─────────────── Hàm cho module KHÁC gọi (08/11) — tự ghi kỹ năng theo khóa học / ôn tập ───────────────
# KHÔNG commit: chạy trong transaction của module gọi (vd API "Tham gia khóa học" của Hòa) → module đó
# commit một lần cho cả việc đổi trạng thái khóa học lẫn kỹ năng (lỗi thì rollback cả hai).
#
# Quyết định (Tuấn, 08/11):
#   D05 Tham gia khóa học  → kỹ năng của khóa thành "learning" (source="course"); đã "known" thì giữ nguyên
#   S7  Bỏ khóa học        → gỡ kỹ năng "learning" có source="course" của khóa đó (trừ kỹ năng mà khóa đang
#                            học KHÁC cũng dạy); học lại → tham gia lại → tự thêm lại
#   S8  Hoàn thành khóa    → kỹ năng của khóa thành "known" (source="course")
#   T13 Làm đạt ôn tập     → kỹ năng của khóa thành "known" (source="review", module 09)


def add_learning_from_course(db: Session, user_id: int, skill_ids) -> None:
    """D05 — tham gia khóa học. Kỹ năng đã có trong hồ sơ (dù known hay learning) giữ nguyên."""
    ids = list(dict.fromkeys(skill_ids))
    existing = user_skill_repository.get_many(db, user_id, ids)
    for skill_id in ids:
        if skill_id not in existing:
            user_skill_repository.add(
                db,
                user_id=user_id,
                skill_id=skill_id,
                status="learning",
                source="course",
            )
    db.flush()


def remove_learning_from_course(
    db: Session, user_id: int, skill_ids, *, keep_skill_ids=()
) -> None:
    """S7 — bỏ khóa học. Chỉ gỡ kỹ năng vẫn đang "learning" do khóa học thêm vào (source="course").

    keep_skill_ids: kỹ năng của các khóa người dùng VẪN đang học → không gỡ.
    Không đụng kỹ năng người dùng tự thêm (manual) hoặc đã "known".
    """
    keep = set(keep_skill_ids)
    ids = [i for i in dict.fromkeys(skill_ids) if i not in keep]
    for row in user_skill_repository.get_many(db, user_id, ids).values():
        if row.status == "learning" and row.source == "course":
            user_skill_repository.delete(db, row)
    db.flush()


def mark_known(db: Session, user_id: int, skill_ids, *, source: str) -> None:
    """S8 (source="course") / T13 (source="review") — kỹ năng của khóa thành "known".

    Chưa có → thêm "known"; đang "learning" → nâng lên "known". Ôn tập (review) là xác nhận mạnh nhất
    → luôn ghi source="review"; hoàn thành khóa không ghi đè kỹ năng đã xác nhận qua ôn tập.
    """
    if source not in ("course", "review"):
        raise ValueError("source phải là 'course' hoặc 'review'")
    ids = list(dict.fromkeys(skill_ids))
    existing = user_skill_repository.get_many(db, user_id, ids)
    for skill_id in ids:
        row = existing.get(skill_id)
        if row is None:
            user_skill_repository.add(
                db, user_id=user_id, skill_id=skill_id, status="known", source=source
            )
        elif row.status != "known" or (source == "review" and row.source != "review"):
            row.status = "known"
            row.source = source
    db.flush()
