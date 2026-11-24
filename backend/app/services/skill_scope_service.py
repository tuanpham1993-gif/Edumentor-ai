"""Phạm vi ôn tập theo kỹ năng — AI gắn nhãn open / closed / unsure (module 09 · Tuấn · G3.0, 24/11/2026).

    is_open(db, skill_id)          → AI có được tự soạn câu cho kỹ năng này không (G3d dùng). Chưa có nhãn = False.
    run(db, classify, ...)         → phân loại kỹ năng CHƯA có nhãn theo lô (script classify_skill_scopes gọi)
    list_page / set_scope          → API admin "Phạm vi kỹ năng"

Tiêu chí (docs/guide.md Q8, sửa 22/11): câu có ĐÁP ÁN ĐÚNG RÕ RÀNG và nhóm / học viên NHẬN RA khi AI soạn sai.
Nhãn admin (source="admin") không bao giờ bị phân loại lại ghi đè. `classify(items) -> JSON thô` truyền vào → test dùng
AI giả, không gọi mạng.
"""

import logging
import time
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.ai.prompts.review_scope import SCOPE_PROMPT_VERSION
from app.ai.review.base import AIUnavailableError
from app.ai.review.grading_schema import AIOutputError
from app.ai.review.scope_schema import parse_scope
from app.models.review_skill_scope import ReviewSkillScope
from app.models.user import Users
from app.repositories import skill_scope_repository as repo

logger = logging.getLogger(__name__)

BATCH_SIZE = 100
TRANSIENT_WAITS = (20.0, 40.0, 60.0, 60.0)  # giây chờ trước mỗi lần thử lại lô khi Gemini 503 / mất mạng
MISSING_REASON = "AI không trả kết quả cho kỹ năng này — để Chưa rõ"

Classify = Callable[[list[dict]], object]  # items → JSON thô của mô hình ({"results": [...]})


class ScopeSkillNotFoundError(Exception):
    pass


def is_open(db: Session, skill_id: int) -> bool:
    scope = repo.get(db, skill_id)
    return scope is not None and scope.label == "open"


# ─────────────── Phân loại theo lô ───────────────


def classify_batch(items: list[dict], classify: Classify) -> tuple[dict[int, dict], int]:
    """→ ({skill_id: {label, category, reason}} cho MỌI id trong lô, số lần gọi AI).
    Thiếu id / sai khung → gọi lại 1 lần cho phần còn thiếu; vẫn thiếu → 'unsure'.
    Lỗi mạng / hết lượt (AIUnavailableError không phải AIOutputError) → ném ra: dừng, không đoán."""
    results: dict[int, dict] = {}
    calls = 0
    pending = list(items)
    for _ in range(2):
        calls += 1
        try:
            results.update(parse_scope(classify(pending), {i["skill_id"] for i in pending}))
        except AIOutputError as err:
            logger.warning("Phân loại phạm vi: lô trả sai khung (%s) — thử lại", err)
        pending = [i for i in items if i["skill_id"] not in results]
        if not pending:
            break
    for item in pending:
        results[item["skill_id"]] = {"label": "unsure", "category": "other", "reason": MISSING_REASON}
    return results, calls


def _classify_with_waits(items, classify: Classify, waits: tuple[float, ...], log) -> tuple[dict[int, dict], int]:
    """Gemini quá tải (503) / mất mạng → chờ rồi thử lại CẢ LÔ (đo 24/11: cứ 2–3 lô lại gặp 503). Hết lượt chờ → ném ra."""
    calls = 0
    for wait in (*waits, None):
        try:
            results, n = classify_batch(items, classify)
            return results, calls + n
        except AIOutputError:
            raise  # classify_batch đã tự xử lý sai khung — tới đây là lỗi lạ, không thử lại mù
        except AIUnavailableError as err:
            calls += 1
            if wait is None:
                raise
            log(f"  Gemini lỗi tạm thời ({err}) — chờ {wait:g} giây rồi thử lại lô này")
            time.sleep(wait)
    raise AssertionError("unreachable")  # pragma: no cover


def run(
    db: Session,
    classify: Classify,
    *,
    model: str = "",
    limit: int | None = None,
    batch_size: int = BATCH_SIZE,
    pause: float = 0.0,
    dry_run: bool = False,
    waits: tuple[float, ...] = TRANSIENT_WAITS,
    log: Callable[[str], None] = print,
) -> dict:
    """Phân loại kỹ năng CHƯA có nhãn. Mỗi lô commit riêng → ngắt giữa chừng thì lần sau làm tiếp phần còn lại.
    dry_run: in kết quả, không lưu. Trả tóm tắt {skills, calls, open, closed, unsure}."""
    skills = repo.unlabeled_skills(db, limit)
    summary = {"skills": 0, "calls": 0, "open": 0, "closed": 0, "unsure": 0}
    for start in range(0, len(skills), batch_size):
        chunk = skills[start : start + batch_size]
        titles = repo.top_course_titles(db, [i for i, _ in chunk])
        items = [{"skill_id": i, "skill": n, "courses": titles.get(i, [])} for i, n in chunk]
        results, calls = _classify_with_waits(items, classify, waits, log)
        summary["calls"] += calls
        summary["skills"] += len(items)
        for item in items:
            r = results[item["skill_id"]]
            summary[r["label"]] += 1
            if dry_run:
                log(f"  #{item['skill_id']:<5} {r['label']:<7} {r['category']:<18} {item['skill']} — {r['reason']}")
                continue
            if repo.get(db, item["skill_id"]) is None:  # chỉ kỹ năng chưa có nhãn — nhãn admin không bị ghi đè
                db.add(ReviewSkillScope(skill_id=item["skill_id"], source="ai", model=model or None,
                                        prompt_version=SCOPE_PROMPT_VERSION, **r))  # fmt: skip
        if not dry_run:
            db.commit()
        log(f"Lô {start // batch_size + 1}: {len(items)} kỹ năng · đã xong {summary['skills']}/{len(skills)}")
        if pause and start + batch_size < len(skills):
            time.sleep(pause)  # giãn cách: không vượt giới hạn lượt gọi / phút của Gemini
    return summary


# ─────────────── API admin ───────────────


def _row(scope, skill_id: int, skill: str, updated_by_name: str | None) -> dict:
    return {
        "skill_id": skill_id,
        "skill": skill,
        "label": scope.label if scope else None,
        "category": scope.category if scope else None,
        "reason": scope.reason if scope else None,
        "source": scope.source if scope else None,
        "model": scope.model if scope else None,
        "prompt_version": scope.prompt_version if scope else None,
        "updated_by_name": updated_by_name,
        "updated_at": scope.updated_at if scope else None,
    }


def list_page(db: Session, *, label=None, category=None, source=None, q=None, skill_id=None, page=1, size=20) -> dict:
    rows, total = repo.page(db, label=label, category=category, source=source, q=(q or "").strip() or None,
                            skill_id=skill_id, offset=(page - 1) * size, limit=size)  # fmt: skip
    return {"items": [_row(*r) for r in rows], "total": total, "page": page, "size": size, "counts": repo.counts(db)}


def set_scope(db: Session, admin: Users, skill_id: int, *, label: str, category=None, reason=None) -> dict:
    """Admin đặt nhãn (tạo dòng nếu chưa có) → source='admin'; phân loại lại sẽ không ghi đè."""
    name = repo.skill_name(db, skill_id)
    if name is None:
        raise ScopeSkillNotFoundError
    scope = repo.get(db, skill_id)
    if scope is None:
        scope = ReviewSkillScope(skill_id=skill_id, category=category or "other")
        db.add(scope)
    scope.label = label
    if category:
        scope.category = category
    if reason is not None:
        scope.reason = reason.strip()[:200] or None
    scope.source = "admin"
    scope.updated_by = admin.user_id
    db.commit()
    db.refresh(scope)
    return _row(scope, skill_id, name, admin.full_name)
