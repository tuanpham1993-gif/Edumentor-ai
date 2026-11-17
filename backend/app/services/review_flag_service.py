"""Bài cần xem lại — admin xem và chấm lại câu tự luận đáng ngờ (module 09 · Tuấn · 17/11/2026).

Human-in-the-loop theo bài "Kiến trúc RAG cho 6.000 kỹ năng" thầy gửi: pipeline đã gắn cờ (B8) nhưng chưa có chỗ
cho người xử lý. Cờ tính TỪ DỮ LIỆU ĐÃ CÓ (attempt.trace["grading"]["essays"] + điểm lượt) — không thêm cột, nên
cả bài chấm trước hôm nay cũng hiện lên.

Lý do đưa một câu tự luận (có bài làm) vào danh sách:
    needs_review          điểm AI vẫn lệch chấm từ khóa sau khi chấm lại (khối 6, D10)
    near_pass             điểm cả lượt sát ngưỡng đạt (|điểm − ngưỡng| ≤ NEAR_PASS_MARGIN) — một ý có thể đổi Đạt
    instruction_in_answer bài làm có câu ra lệnh cho AI (khối 2 Guard)
    evidence_missing      Verifier phải hạ ý "Đạt" vì AI không trích được câu có thật (khối 5)
    keyword_fallback      Gemini lỗi / quá giờ → chấm bằng từ khóa

Admin chấm lại (resolve): chọn Đạt / Không đạt cho từng ý → tính lại điểm câu, điểm lượt, đạt hay không.
    - Đổi sang ĐẠT + khóa đang học → khóa Hoàn thành + kỹ năng "Đã biết" (như nộp bài) + chuông + email (mẫu cũ).
    - Điểm đổi nhưng không thành đạt → cập nhật chuông kết quả (không email).
    - Đổi từ đạt sang CHƯA ĐẠT → khóa đã Hoàn thành giữ nguyên (Khôi: Hoàn thành không đảo ngược được).
Lịch sử chấm lại lưu ở essay["review"] trong trace (ai, lúc nào, nhãn trước / sau, ghi chú).
"""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.review_attempt import ReviewAttempt
from app.models.user import Users
from app.repositories import review_repository as repo
from app.services import review_service

NEAR_PASS_MARGIN = 0.5
REASONS = ("needs_review", "near_pass", "instruction_in_answer", "evidence_missing", "keyword_fallback")
REASON_TEXT = {
    "needs_review": "AI lệch chấm từ khóa",
    "near_pass": "Điểm sát ngưỡng đạt",
    "instruction_in_answer": "Bài có câu ra lệnh cho AI",
    "evidence_missing": "AI không trích được bằng chứng",
    "keyword_fallback": "Chấm bằng từ khóa (AI lỗi)",
}
LABEL_POINTS = {"full": 1.0, "none": 0.0}


class FlagNotFoundError(Exception):
    """Không có lượt / câu này, hoặc câu không phải tự luận có bài làm."""


class FlagConflictError(Exception):
    """Lượt chưa chấm xong — không chấm lại được."""


class FlagInvalidError(Exception):
    """Số nhãn không khớp số ý của barem."""


# ─────────────── Lý do ───────────────


def _essays(attempt: ReviewAttempt) -> dict[int, dict]:
    grading = (attempt.trace or {}).get("grading") or {}
    return {e["position"]: e for e in grading.get("essays", [])}


def _fallback_positions(attempt: ReviewAttempt) -> set[int]:
    grading = (attempt.trace or {}).get("grading") or {}
    if grading.get("ai") in ("mock", "unavailable"):
        return set()  # AI_MODE=mock: mọi câu đều chấm từ khóa — không phải sự cố, không đưa vào danh sách
    return {f["position"] for f in grading.get("keyword_fallback", [])}


def reasons_for(attempt: ReviewAttempt, position: int) -> list[str]:
    essay = _essays(attempt).get(position, {})
    flags = set(essay.get("flags") or [])
    out = []
    if essay.get("needs_review") or "needs_review" in flags:
        out.append("needs_review")
    if attempt.score is not None and abs(float(attempt.score) - settings.REVIEW_PASS_SCORE) <= NEAR_PASS_MARGIN:
        out.append("near_pass")
    for flag in ("instruction_in_answer", "evidence_missing"):
        if flag in flags:
            out.append(flag)
    if position in _fallback_positions(attempt):
        out.append("keyword_fallback")
    return out


def _has_text(answer) -> bool:
    return bool(answer.text_answer and answer.text_answer.strip())


# ─────────────── Danh sách ───────────────


def list_flags(
    db: Session,
    *,
    status: str = "open",
    reason: str | None = None,
    course_id: int | None = None,
    page: int = 1,
    size: int = 20,
) -> dict:
    """status: open (chưa xem lại) | resolved (đã xem lại) | all."""
    attempts = repo.graded_attempts(db, course_id)
    rows, counts = [], dict.fromkeys(REASONS, 0)
    open_total = resolved_total = 0
    for attempt in attempts:
        essays = _essays(attempt)
        for answer in attempt.answers:
            if answer.question.type != "essay" or not _has_text(answer):
                continue
            reasons = reasons_for(attempt, answer.position)
            reviewed = bool(essays.get(answer.position, {}).get("review"))
            if not reasons and not reviewed:
                continue
            if reviewed:
                resolved_total += 1
            else:
                open_total += 1
                for r in reasons:
                    counts[r] += 1
            if status == "open" and reviewed or status == "resolved" and not reviewed:
                continue
            if reason and reason not in reasons:
                continue
            rows.append((attempt, answer, reasons))
    total = len(rows)
    rows = rows[(page - 1) * size : page * size]
    users = repo.user_names(db, [a.user_id for a, _, _ in rows])
    titles = repo.course_titles(db, [a.course_id for a, _, _ in rows])
    reviewer_ids = [(_essays(a).get(ans.position, {}).get("review") or {}).get("by") for a, ans, _ in rows]
    reviewers = repo.user_names(db, [uid for uid in reviewer_ids if uid is not None])
    return {
        "items": [_item(a, ans, reasons, users, titles, reviewers) for a, ans, reasons in rows],
        "total": total,
        "page": page,
        "size": size,
        "open_total": open_total,
        "resolved_total": resolved_total,
        "reason_counts": counts,
    }


def _item(attempt, answer, reasons, users, titles, reviewers) -> dict:
    q = answer.question
    essay = _essays(attempt).get(answer.position, {})
    results = answer.rubric_result or [{} for _ in q.rubric]
    review = essay.get("review")
    name, email = users.get(attempt.user_id, ("", ""))
    return {
        "attempt_id": attempt.attempt_id,
        "position": answer.position,
        "user_id": attempt.user_id,
        "user_name": name,
        "user_email": email,
        "course_id": attempt.course_id,
        "course_title": titles.get(attempt.course_id, ""),
        "submitted_at": attempt.submitted_at,
        "attempt_score": float(attempt.score) if attempt.score is not None else None,
        "attempt_passed": attempt.passed,
        "question_id": q.question_id,
        "question_code": q.code,
        "level": q.level,
        "content": q.content,
        "model_answer": q.explanation,
        "text_answer": answer.text_answer,
        "max_points": float(answer.max_points),
        "points": float(answer.points) if answer.points is not None else 0.0,
        "feedback": essay.get("feedback"),
        "reasons": reasons,
        "rubric": [
            {
                "text": r["text"],
                "max_points": float(r["max_points"]),
                "result": res.get("result", "none"),
                "points": float(res.get("points", 0.0)),
                "evidence": res.get("evidence"),
                "reason": res.get("reason"),
            }
            for r, res in zip(q.rubric, results, strict=True)
        ],
        "review": (
            {
                **review,
                "by_name": reviewers.get(review.get("by"), ("", ""))[0],
            }
            if review
            else None
        ),
    }


# ─────────────── Chấm lại ───────────────


def resolve(
    db: Session, attempt_id: int, position: int, labels: list[str], admin: Users, note: str | None = None
) -> dict:
    """Admin chọn Đạt / Không đạt cho từng ý. Một lần commit. Trả {item, score_changed, passed_changed,
    completed_course, notify_email} — router gửi email khi notify_email."""
    attempt = repo.get_attempt(db, attempt_id, for_update=True)
    if attempt is None:
        raise FlagNotFoundError
    answer = next((a for a in attempt.answers if a.position == position), None)
    if answer is None or answer.question.type != "essay" or not _has_text(answer):
        raise FlagNotFoundError
    if attempt.status != "graded":
        raise FlagConflictError("Lượt này chưa chấm xong.")
    rubric = answer.question.rubric
    if len(labels) != len(rubric) or any(label not in LABEL_POINTS for label in labels):
        raise FlagInvalidError(f"Cần đúng {len(rubric)} nhãn full / none (mỗi ý một nhãn).")

    try:
        before = [dict(r) for r in (answer.rubric_result or [{} for _ in rubric])]
        old_score, old_passed = attempt.score, attempt.passed
        after = []
        for item, old, label in zip(rubric, before, labels, strict=True):
            new = dict(old)
            if old.get("result") != label:
                new["result"] = label
                new["reason"] = "Giáo viên chấm lại: " + ("Đạt." if label == "full" else "Không đạt.")
                if label == "none":
                    new["evidence"] = None
            new["points"] = LABEL_POINTS[label] * float(item["max_points"])
            after.append(new)
        answer.rubric_result = after  # list MỚI → SQLAlchemy biết cột JSON đã đổi
        answer.points = round(sum(r["points"] for r in after) / 10 * float(answer.max_points), 2)

        total = sum(_raw_points(a) for a in attempt.answers)
        attempt.score = round(total, 2)
        attempt.passed = round(total, 6) >= settings.REVIEW_PASS_SCORE
        became_passed = bool(attempt.passed) and not bool(old_passed)
        completed = False
        if became_passed:
            completed = review_service.complete_if_first_pass(db, attempt.user_id, attempt)

        trace = dict(attempt.trace or {})
        grading = dict(trace.get("grading") or {})
        essays = [dict(e) for e in grading.get("essays", [])]
        essay = next((e for e in essays if e["position"] == position), None)
        if essay is None:
            essay = {"position": position}
            essays.append(essay)
        essay["needs_review"] = False
        essay["review"] = {
            "by": admin.user_id,
            "at": datetime.now(UTC).isoformat(),
            "before": [r.get("result", "none") for r in before],
            "after": labels,
            "note": (note or "").strip() or None,
            "score_before": float(old_score) if old_score is not None else None,
            "score_after": float(attempt.score),
        }
        grading["essays"] = essays
        grading["needs_review"] = [p for p in grading.get("needs_review", []) if p != position]
        trace["grading"] = grading
        attempt.trace = trace

        score_changed = old_score is None or float(old_score) != float(attempt.score)
        if score_changed:
            user = db.get(Users, attempt.user_id)
            review_service._notify_result(db, user, attempt, renew=True)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(attempt)
    reasons = reasons_for(attempt, position)
    users = repo.user_names(db, [attempt.user_id, admin.user_id])
    titles = repo.course_titles(db, [attempt.course_id])
    answer = next(a for a in attempt.answers if a.position == position)
    return {
        "item": _item(attempt, answer, reasons, users, titles, users),
        "score_changed": score_changed,
        "passed_changed": bool(attempt.passed) != bool(old_passed),
        "completed_course": completed,
        "notify_email": became_passed,
    }


def _raw_points(answer) -> float:
    """Điểm chưa làm tròn của một câu (giống lúc nộp bài: tổng so ngưỡng trên số chưa làm tròn — Q7)."""
    if answer.question.type == "essay" and answer.rubric_result:
        return sum(float(r.get("points", 0.0)) for r in answer.rubric_result) / 10 * float(answer.max_points)
    return float(answer.points or 0.0)
