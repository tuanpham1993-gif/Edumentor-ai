"""Quản trị ngân hàng câu hỏi ôn tập (module 09 · Tuấn · GĐ7 bước 7.3, 13/11/2026).

Lớp mỏng phía trên `review_bank_service` (7.2): kiểm tra tồn tại / kỹ năng / đoạn tri thức / mã trùng, gọi hàm ngân hàng,
rồi COMMIT một lần cho mỗi thao tác (lỗi → rollback). Quy tắc phiên bản, sửa nhỏ, bật / tắt, xóa nằm ở review_bank_service.
"""

import re
from collections import Counter

from sqlalchemy.orm import Session

from app.repositories import review_repository as repo
from app.schemas.review_admin import ApproveRequest, QuestionCreate, QuestionUpdate
from app.services import review_bank_service as bank
from app.services.review_bank_service import BankError


class QuestionNotFoundError(Exception):
    pass


class DuplicateCodeError(BankError):
    """Mã câu đã có (mã là unique)."""


class InvalidReferenceError(BankError):
    """Kỹ năng / đoạn tri thức không tồn tại hoặc đoạn không thuộc kỹ năng của câu."""


class ApprovalNotAllowedError(BankError):
    """Chỉ duyệt / từ chối được câu đang 'pending'."""


# ─────────────── đọc ───────────────


def list_questions(
    db: Session,
    *,
    course_id: int | None = None,
    skill_id: int | None = None,
    type: str | None = None,
    level: str | None = None,
    source: str | None = None,
    is_active: bool | None = None,
    review_status: str | None = None,
    q: str | None = None,
    latest_only: bool = True,
    page: int = 1,
    size: int = 20,
) -> dict:
    skill_ids = None
    if course_id is not None:
        skill_ids = [sid for sid, _ in repo.course_skills(db, course_id)]
    if skill_id is not None:
        skill_ids = [skill_id] if skill_ids is None or skill_id in skill_ids else []
    rows, total = repo.list_questions(
        db,
        skill_ids=skill_ids,
        type=type,
        level=level,
        source=source,
        is_active=is_active,
        review_status=review_status,
        q=q,
        latest_only=latest_only,
        offset=(page - 1) * size,
        limit=size,
    )
    items = [
        {
            **_base(question),
            "version": version,
            "family_id": family_id,
            "review_status": status,
            "used_count": used_count,
            "skill_name": skill_name,
        }
        for question, version, family_id, status, used_count, skill_name in rows
    ]
    return {"total": total, "page": page, "size": size, "items": items}


def get_detail(db: Session, question_id: int) -> dict:
    return _detail(db, _get(db, question_id))


# Mã câu: "<khóa>-<kỹ năng>-<TN|TL>-<số>" (câu cũ, vd 312-VAR-TN-09) hoặc "<kỹ năng>-<TN|TL>-<số>" (câu mới, QT9),
# có thể kèm đuôi phiên bản cũ "~v1".
CODE_PATTERN = re.compile(r"^(?:\d+-)?([A-Z][A-Z0-9]*)-(TN|TL)-(\d+)(?:~v\d+)?$")
TYPE_TAG = {"mcq": "TN", "essay": "TL"}


def suggest_code(db: Session, question_id: int) -> dict:
    """Gợi ý mã khi duyệt (Tuấn chốt 13/11): lấy viết tắt kỹ năng từ các mã ĐÃ CÓ của kỹ năng đó (DB chưa lưu viết
    tắt — chỉ có trong data/review/*.json), số = lớn nhất cùng loại + 1, bỏ tiền tố khóa (QT9).
    Vd kỹ năng đã có 312-VAR-TN-01..14 → "VAR-TN-15". Kỹ năng chưa có mã nào → None (admin tự nhập)."""
    question = _get(db, question_id)
    parsed = [m.groups() for m in map(CODE_PATTERN.match, repo.codes_for_skill(db, question.skill_id)) if m]
    if not parsed:
        return {"code": None}
    abbr = Counter(a for a, _, _ in parsed).most_common(1)[0][0]
    tag = TYPE_TAG[question.type]
    number = max((int(n) for a, t, n in parsed if a == abbr and t == tag), default=0) + 1
    code = f"{abbr}-{tag}-{number:02d}"
    while repo.get_question_by_code(db, code) is not None:  # phòng mã đã bị dùng ở kỹ năng khác
        number += 1
        code = f"{abbr}-{tag}-{number:02d}"
    return {"code": code}


# ─────────────── ghi (mỗi hàm commit một lần) ───────────────


def create(db: Session, body: QuestionCreate, admin_id: int) -> dict:
    data = body.model_dump()
    _check_code_free(db, data["code"])
    _check_refs(db, data["skill_id"], data["chunk_id"])
    return _commit(db, lambda: bank.create_question(db, data, user_id=admin_id))


def update(db: Session, question_id: int, body: QuestionUpdate, admin_id: int) -> dict:
    question = _get(db, question_id, for_update=True)
    changes = body.model_dump(exclude_unset=True, exclude={"minor", "note"})
    if "skill_id" in changes or "chunk_id" in changes:
        _check_refs(
            db,
            changes.get("skill_id", question.skill_id),
            changes.get("chunk_id", question.chunk_id),
        )

    result = _commit(
        db,
        lambda: bank.update_question(db, question, changes, minor=body.minor, user_id=admin_id, note=body.note),
        as_detail=False,
    )
    return {
        "question": _detail(db, result.question),
        "versioned": result.versioned,
        "changed": result.changed,
    }


def set_active(db: Session, question_id: int, active: bool) -> dict:
    question = _get(db, question_id, for_update=True)
    return _commit(db, lambda: bank.set_active(db, question, active))


def delete(db: Session, question_id: int) -> dict:
    question = _get(db, question_id, for_update=True)
    result = _commit(db, lambda: bank.delete_question(db, question), as_detail=False)
    return {"result": result}


def approve(db: Session, question_id: int, body: ApproveRequest, admin_id: int) -> dict:
    """Duyệt câu AI soạn (QT6): cấp mã (bắt buộc — schema kiểm) + đã duyệt + bật (nếu là phiên bản mới nhất)."""
    question = _get(db, question_id, for_update=True)

    def run():
        meta = bank.ensure_meta(db, question)
        if meta.review_status != "pending":
            raise ApprovalNotAllowedError("Chỉ duyệt được câu đang chờ duyệt")
        if body.code != question.code:
            _check_code_free(db, body.code)
            question.code = body.code
        bank.mark_reviewed(meta, "approved", admin_id)
        db.flush()
        if bank.is_latest(db, question):
            bank.set_active(db, question, True)
        return question

    return _commit(db, run)


def reject(db: Session, question_id: int, admin_id: int) -> dict:
    """Từ chối câu AI soạn: ẩn (tắt), không xóa — vẫn xem được trong bộ lọc "Bị từ chối"."""
    question = _get(db, question_id, for_update=True)

    def run():
        meta = bank.ensure_meta(db, question)
        if meta.review_status != "pending":
            raise ApprovalNotAllowedError("Chỉ từ chối được câu đang chờ duyệt")
        bank.mark_reviewed(meta, "rejected", admin_id)
        question.is_active = False
        db.flush()
        return question

    return _commit(db, run)


# ─────────────── nội bộ ───────────────


def _get(db: Session, question_id: int, *, for_update: bool = False):
    question = repo.get_question(db, question_id, for_update=for_update)
    if question is None:
        raise QuestionNotFoundError(question_id)
    return question


def _commit(db: Session, action, *, as_detail: bool = True):
    """Chạy thao tác ghi → commit; lỗi bất kỳ → rollback rồi ném tiếp (router đổi thành HTTP)."""
    try:
        result = action()
        db.commit()
    except Exception:
        db.rollback()
        raise
    return _detail(db, result) if as_detail else result


def _check_code_free(db: Session, code: str | None) -> None:
    if code and repo.get_question_by_code(db, code) is not None:
        raise DuplicateCodeError(f"Mã câu '{code}' đã tồn tại")


def _check_refs(db: Session, skill_id: int, chunk_id: int | None) -> None:
    if not repo.skill_exists(db, skill_id):
        raise InvalidReferenceError(f"Kỹ năng {skill_id} không tồn tại")
    if chunk_id is not None:
        chunk_skill = repo.chunk_skill_id(db, chunk_id)
        if chunk_skill is None:
            raise InvalidReferenceError(f"Đoạn tri thức {chunk_id} không tồn tại")
        if chunk_skill != skill_id:
            raise InvalidReferenceError(f"Đoạn tri thức {chunk_id} không thuộc kỹ năng {skill_id}")


def _base(question) -> dict:
    return {
        f: getattr(question, f)
        for f in (
            "question_id",
            "code",
            "skill_id",
            "type",
            "level",
            "content",
            "source",
            "is_active",
            "created_at",
        )
    }


def _detail(db: Session, question) -> dict:
    missing_meta = repo.get_meta(db, question.question_id) is None
    meta = bank.ensure_meta(db, question)  # câu nạp trước 13/11 chưa có meta → tạo v1 (chỉ flush)
    if missing_meta:
        db.commit()  # lưu luôn meta vừa tạo (request đọc không có commit nào khác)
    return {
        **_base(question),
        "skill_name": repo.skill_names(db, [question.skill_id]).get(question.skill_id),
        "family_id": meta.family_id,
        "version": meta.version,
        "review_status": meta.review_status,
        "used_count": repo.used_count(db, question.question_id),
        "chunk_id": question.chunk_id,
        "options": question.options,
        "correct_index": question.correct_index,
        "rubric": question.rubric,
        "explanation": question.explanation,
        "exclusion_group": meta.exclusion_group,
        "change_note": meta.change_note,
        "versions": bank.versions(db, question),
    }
