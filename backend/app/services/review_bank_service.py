"""Ngân hàng câu hỏi ôn tập — thêm / sửa (phiên bản) / tắt / xóa (module 09 · Tuấn · GĐ7 bước 7.2, 13/11/2026).

Dùng chung cho trang quản trị (7.3) và script seed (QT4). Các hàm ở đây CHỈ flush — người gọi commit
(API quản trị commit một lần cho mỗi thao tác; seed commit cuối).

Quy tắc (chốt 12/11, docs/Review-Assessment.md GĐ7):
  - QT2 / QT8 — "sao chép khi sửa": câu ĐÃ có trong bài làm mà đổi nội dung → tạo DÒNG MỚI (phiên bản + 1, cùng họ),
    dòng cũ tắt + đổi mã thành "<mã>~v<n>"; mã gốc chuyển sang dòng mới. Bài cũ vẫn trỏ dòng cũ → kết quả, lịch sử
    hiện đúng câu lúc làm. Câu CHƯA ai làm, hoặc câu AI đang chờ duyệt → sửa tại chỗ.
  - QT5 — "Sửa nhỏ" (không tạo phiên bản, kể cả câu đã dùng): CHỈ giải thích, đoạn tri thức, nhóm loại trừ, lỗi chính
    tả của đề (đề mới giống đề cũ ≥ CONTENT_TYPO_RATIO). Đáp án, lựa chọn, barem, từ khóa, điểm ý, kỹ năng, mức độ →
    bắt buộc phiên bản.
  - Xóa: chưa ai làm → xóa thật; đã làm → chỉ tắt (api-endpoints T20).
  - QT6: câu chờ duyệt / bị từ chối luôn tắt (không vào đề); không bật được bằng công tắc — phải duyệt.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.ai.review.validator import question_errors
from app.models.review_question import ReviewQuestion
from app.models.review_question_meta import ReviewQuestionMeta
from app.repositories import review_repository as repo

CONTENT_TYPO_RATIO = 0.9  # "Sửa nhỏ" đề: đề mới phải giống đề cũ ≥ 90% (chỉ sửa chính tả)

QUESTION_FIELDS = ("skill_id", "chunk_id", "level", "content", "options", "correct_index", "rubric", "explanation")
EDITABLE_FIELDS = (*QUESTION_FIELDS, "exclusion_group")
MINOR_FIELDS = ("explanation", "chunk_id", "exclusion_group", "content")  # content: chỉ khi giống ≥ 90%


class BankError(Exception):
    pass


class QuestionInvalidError(BankError):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


class MinorEditNotAllowedError(BankError):
    """Sửa nhỏ nhưng đổi trường ảnh hưởng chấm điểm / hiển thị kết quả bài cũ → phải lưu phiên bản."""


class ActivationNotAllowedError(BankError):
    pass


@dataclass
class EditResult:
    question: ReviewQuestion  # câu hiện hành sau khi sửa (dòng mới nếu tạo phiên bản)
    versioned: bool  # True = đã tạo phiên bản mới
    changed: list[str]  # các trường thực sự đổi


# ─────────────── meta ───────────────


def ensure_meta(db: Session, question: ReviewQuestion) -> ReviewQuestionMeta:
    """Dòng meta của câu; câu nạp trước 13/11 chưa có → tạo: họ = chính nó, phiên bản 1, đã duyệt."""
    meta = repo.get_meta(db, question.question_id)
    if meta is None:
        meta = ReviewQuestionMeta(
            question_id=question.question_id, family_id=question.question_id, version=1, review_status="approved"
        )
        db.add(meta)
        db.flush()
    return meta


def _as_dict(question: ReviewQuestion, meta: ReviewQuestionMeta | None) -> dict:
    data = {f: getattr(question, f) for f in QUESTION_FIELDS}
    data["type"] = question.type
    data["exclusion_group"] = meta.exclusion_group if meta else None
    return data


def _validate(data: dict) -> None:
    errors = question_errors(data)
    if errors:
        raise QuestionInvalidError(errors)


# ─────────────── thêm ───────────────


def create_question(
    db: Session,
    data: dict,
    *,
    source: str = "bank",
    review_status: str = "approved",
    user_id: int | None = None,
) -> ReviewQuestion:
    """Thêm câu mới (phiên bản 1). Câu AI soạn: review_status='pending' → tắt cho tới khi duyệt (QT6)."""
    _validate(data)
    question = ReviewQuestion(
        code=data.get("code"),
        skill_id=data["skill_id"],
        chunk_id=data.get("chunk_id"),
        type=data["type"],
        level=data["level"],
        content=data["content"],
        options=data.get("options"),
        correct_index=data.get("correct_index"),
        rubric=data.get("rubric"),
        explanation=data.get("explanation"),
        source=source,
        is_active=review_status == "approved",
    )
    db.add(question)
    db.flush()
    db.add(
        ReviewQuestionMeta(
            question_id=question.question_id,
            family_id=question.question_id,
            version=1,
            exclusion_group=data.get("exclusion_group"),
            review_status=review_status,
            created_by=user_id,
        )
    )
    db.flush()
    return question


# ─────────────── sửa ───────────────


def update_question(
    db: Session,
    question: ReviewQuestion,
    changes: dict,
    *,
    minor: bool = False,
    user_id: int | None = None,
    note: str | None = None,
) -> EditResult:
    """Sửa câu. Tự quyết sửa tại chỗ hay tạo phiên bản mới (xem docstring module)."""
    unknown = set(changes) - set(EDITABLE_FIELDS)
    if unknown:
        raise BankError(f"Không sửa được trường: {', '.join(sorted(unknown))}")
    meta = ensure_meta(db, question)
    current = _as_dict(question, meta)
    changed = {k: v for k, v in changes.items() if current.get(k) != v}
    if not changed:
        return EditResult(question, False, [])
    _validate({**current, **changed})

    if minor:
        not_minor = sorted(set(changed) - set(MINOR_FIELDS))
        if not_minor:
            raise MinorEditNotAllowedError(
                f"Sửa nhỏ không được đổi: {', '.join(not_minor)} — hãy lưu phiên bản mới"
            )
        if "content" in changed:
            ratio = SequenceMatcher(None, question.content, changed["content"]).ratio()
            if ratio < CONTENT_TYPO_RATIO:
                raise MinorEditNotAllowedError("Đề thay đổi nhiều (không chỉ chính tả) — hãy lưu phiên bản mới")

    used = repo.used_count(db, question.question_id) > 0
    if minor or not used or meta.review_status == "pending":
        _apply(question, meta, changed)
        db.flush()
        return EditResult(question, False, sorted(changed))
    return EditResult(_new_version(db, question, meta, changed, user_id, note), True, sorted(changed))


def _apply(question: ReviewQuestion, meta: ReviewQuestionMeta, changed: dict) -> None:
    for field, value in changed.items():
        if field == "exclusion_group":
            meta.exclusion_group = value
        else:
            setattr(question, field, value)


def _new_version(
    db: Session,
    old: ReviewQuestion,
    meta: ReviewQuestionMeta,
    changed: dict,
    user_id: int | None,
    note: str | None,
) -> ReviewQuestion:
    code = old.code
    # Nhường mã cho phiên bản mới TRƯỚC khi thêm dòng mới (mã là unique).
    old.code = f"{code}~v{meta.version}" if code else None
    was_active = old.is_active
    old.is_active = False
    db.flush()

    data = {**_as_dict(old, meta), **changed}
    new = ReviewQuestion(
        code=code,
        source=old.source,
        is_active=was_active,
        type=old.type,
        **{f: data[f] for f in QUESTION_FIELDS},
    )
    db.add(new)
    db.flush()
    db.add(
        ReviewQuestionMeta(
            question_id=new.question_id,
            family_id=meta.family_id,
            version=meta.version + 1,
            exclusion_group=data["exclusion_group"],
            review_status=meta.review_status,
            reviewed_by=meta.reviewed_by,
            reviewed_at=meta.reviewed_at,
            created_by=user_id,
            change_note=note,
        )
    )
    db.flush()
    return new


# ─────────────── tắt / bật / xóa ───────────────


def is_latest(db: Session, question: ReviewQuestion) -> bool:
    meta = ensure_meta(db, question)
    return repo.family_metas(db, meta.family_id)[0].question_id == question.question_id


def set_active(db: Session, question: ReviewQuestion, active: bool) -> ReviewQuestion:
    """Công tắc bật / tắt. Bật: chỉ câu đã duyệt và là phiên bản mới nhất của họ."""
    if active:
        meta = ensure_meta(db, question)
        if meta.review_status != "approved":
            raise ActivationNotAllowedError("Câu chưa được duyệt — hãy duyệt trước khi bật")
        if not is_latest(db, question):
            raise ActivationNotAllowedError("Câu đã có phiên bản mới hơn — hãy bật phiên bản mới nhất")
    question.is_active = active
    db.flush()
    return question


def delete_question(db: Session, question: ReviewQuestion) -> str:
    """Chưa ai làm → xóa thật ("deleted"); đã có trong bài làm → chỉ tắt ("deactivated")."""
    if repo.used_count(db, question.question_id) > 0:
        question.is_active = False
        db.flush()
        return "deactivated"
    meta = repo.get_meta(db, question.question_id)
    if meta is not None:
        db.delete(meta)  # xóa meta trước — không phụ thuộc DB có bật ON DELETE CASCADE hay không (SQLite)
        db.flush()
    db.delete(question)
    db.flush()
    return "deleted"


# ─────────────── lịch sử phiên bản ───────────────


def versions(db: Session, question: ReviewQuestion) -> list[dict]:
    """Mọi phiên bản cùng họ (mới nhất trước) + số bài đã làm từng bản — cho panel "Lịch sử phiên bản"."""
    meta = ensure_meta(db, question)
    out = []
    for m in repo.family_metas(db, meta.family_id):
        q = repo.get_question(db, m.question_id)
        out.append(
            {
                "question_id": m.question_id,
                "version": m.version,
                "code": q.code if q else None,
                "is_active": q.is_active if q else False,
                "used_count": repo.used_count(db, m.question_id),
                "created_at": m.created_at,
                "created_by": m.created_by,
                "change_note": m.change_note,
            }
        )
    return out


def mark_reviewed(meta: ReviewQuestionMeta, status: str, user_id: int | None) -> None:
    """Ghi trạng thái duyệt (dùng ở bước duyệt câu AI — 7.3)."""
    meta.review_status = status
    meta.reviewed_by = user_id
    meta.reviewed_at = datetime.now(UTC)
