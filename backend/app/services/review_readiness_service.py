"""Mức sẵn sàng ôn tập của khóa — GĐ7 bước 7.4 (module 09 · Tuấn · 16/11/2026).

Chỉ để admin XEM (thẻ trên cùng trang /admin/questions). Việc chặn học viên khi thiếu câu đã có sẵn ở luồng làm bài
(`no_question_bank`) — ở đây DÙNG LẠI đúng `exam_builder.plan_exam` để "ôn được" trùng với điều kiện bắt đầu ôn,
không viết luật riêng.

Chỉ tính câu ĐANG BẬT (câu chờ duyệt / bị từ chối / đã tắt đều tắt → không vào đề). Câu chờ duyệt đếm riêng để admin
biết duyệt xong sẽ có thêm bao nhiêu.
"""

import random

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories import review_repository as repo
from app.services import exam_builder
from app.services.exam_builder import MCQ_LEVELS, STRUCTURE

LEVEL_LABELS = {
    "recognize": "trắc nghiệm nhận biết",
    "understand": "trắc nghiệm thông hiểu",
    "easy": "tự luận dễ",
    "advanced": "tự luận nâng cao",
}


class CourseNotFoundError(Exception):
    pass


def readiness(db: Session, course_id: int | None = None) -> dict:
    """Mọi khóa đã có câu hỏi (hoặc 1 khóa nếu truyền course_id) + số khóa chưa có câu nào.

    Danh sách mọi khóa: chỉ tóm tắt (`skills` rỗng) — DB thật có ~200 khóa dùng chung kỹ năng "Python Programming",
    trả cả bảng kỹ năng thì nặng ~330 KB. Chi tiết từng kỹ năng: gọi lại với ?course_id=.
    Ôn được trước, rồi khóa nhiều câu hơn.
    """
    with_questions = repo.courses_with_questions(db)
    if course_id is None:
        courses = with_questions
    else:
        title = repo.get_course_title(db, course_id)
        if title is None:
            raise CourseNotFoundError
        courses = [(course_id, title)]
    target = settings.REVIEW_BANK_TARGET_PER_SKILL

    # 3 truy vấn cho cả trang (trước: 3 truy vấn × mỗi khóa → 2,5 s trên DB thật)
    skills_of = repo.course_skills_many(db, [cid for cid, _ in courses])
    skill_ids = sorted({sid for skills in skills_of.values() for sid, _ in skills})
    counts = repo.bank_counts(db, skill_ids)
    pending = repo.pending_counts(db, skill_ids)

    rows = [
        _course(cid, title, skills_of[cid], counts, pending, target, with_skills=course_id is not None)
        for cid, title in courses
    ]
    rows.sort(key=lambda c: (not c["ready"], -c["active"], c["course_id"]))
    return {
        "target_per_skill": target,
        "structure": dict(STRUCTURE),
        "courses": rows,
        "courses_without_questions": repo.count_courses(db) - len(with_questions),
    }


def _course(
    course_id: int,
    title: str,
    skills: list[tuple[int, str]],
    counts: dict,
    pending: dict[int, int],
    target: int,
    *,
    with_skills: bool,
) -> dict:
    rows = [_skill(sid, name, counts, pending.get(sid, 0), target) for sid, name in skills]
    ready, missing = _check(skills, counts)
    return {
        "course_id": course_id,
        "title": title,
        "ready": ready,
        "missing": missing,
        "skill_count": len(skills),
        "active": sum(r["active"] for r in rows),
        "mcq": sum(r["mcq"] for r in rows),
        "essay": sum(r["essay"] for r in rows),
        "pending": sum(r["pending"] for r in rows),
        "target": target * len(skills),
        "skills": rows if with_skills else [],
    }


def _skill(skill_id: int, name: str, counts: dict, pending: int, target: int) -> dict:
    by_level = {lv: counts.get((skill_id, lv), 0) for lv in STRUCTURE}
    mcq = sum(by_level[lv] for lv in MCQ_LEVELS)
    return {
        "skill_id": skill_id,
        "skill": name,
        "by_level": by_level,
        "active": sum(by_level.values()),
        "mcq": mcq,
        "essay": sum(by_level.values()) - mcq,
        "pending": pending,
        "target": target,
        # kỹ năng KHÔNG có câu TN → cả khóa không ôn được (A1). Mức khác trống chỉ là thông tin.
        "missing": [LEVEL_LABELS[lv] for lv, n in by_level.items() if n == 0],
    }


def _check(skills: list[tuple[int, str]], counts: dict) -> tuple[bool, list[str]]:
    """Ôn được = plan_exam ráp được đề 15 câu. Không được → lý do dễ đọc cho admin."""
    try:
        exam_builder.plan_exam([s for s, _ in skills], counts, random.Random(0))
        return True, []
    except exam_builder.NotEnoughQuestionsError:
        pass
    reasons = [
        f"Kỹ năng «{name}» chưa có câu trắc nghiệm"
        for sid, name in skills
        if not any(counts.get((sid, lv), 0) for lv in MCQ_LEVELS)
    ]
    for level, need in STRUCTURE.items():
        have = sum(counts.get((sid, level), 0) for sid, _ in skills)
        if have < need:
            reasons.append(f"Thiếu {LEVEL_LABELS[level]}: có {have}/{need} câu")
    if not skills:
        reasons.insert(0, "Khóa chưa gắn kỹ năng nào")
    return False, reasons or ["Chưa ráp được đề 15 câu từ ngân hàng hiện có"]
