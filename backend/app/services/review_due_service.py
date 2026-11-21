"""Đến hạn ôn (module 09 · Tuấn · 21/11/2026 — Q12 trong docs/guide.md).

Quy tắc (chốt 21/11):
  - Tính THEO KỸ NĂNG. Đạt bài ôn của một khóa = đã ôn mọi kỹ năng của khóa đó.
  - Chỉ xét kỹ năng đang "Đã biết" VÀ đã từng ôn đạt ít nhất một lần (Đang học / tự khai chưa ôn → không xét).
  - Khoảng nhắc giãn dần theo số lần ĐẠT liên tiếp gần nhất: lần 1 → 7 ngày, lần 2 → 30, lần 3+ → 90
    (settings.REVIEW_DUE_INTERVALS). Lần ôn gần nhất chưa đạt → quay về khoảng đầu (7 ngày) tính từ lần đó.
  - Quá hạn CHỈ NHẮC, không hạ "Đã biết" (nhất quán FR-57: không kéo lùi tiến độ).
  - Nhắc: huy hiệu (API /me/review/skills) + chuông (gom tối đa 1 lần / 24 giờ) + email (tối đa 1 lần / tuần,
    chỉ khi bật "Nhắc ôn tập"). Bảng review_due_reminders ghi đã nhắc → không nhắc lặp cùng một hạn.
Tính từ lịch sử bài ôn mỗi lần gọi, không lưu trạng thái "đến hạn" (đổi quy tắc / cấu hình là có hiệu lực ngay).
"""

import logging
import threading
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.email import send_review_due_email
from app.models.review_due_reminder import ReviewDueReminder
from app.models.user import Users
from app.repositories import review_repository as repo
from app.services import email_preference_service, notification_service

logger = logging.getLogger(__name__)

NOTIFY_EVERY = timedelta(hours=24)
REVIEW_LINK = "/me/courses"  # Khóa học của tôi: nút "Làm bài ôn tập" của từng khóa


def _aware(value: datetime) -> datetime:
    """SQLite (test) trả datetime không múi giờ → coi là UTC."""
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def interval_days(streak: int) -> int:
    """streak = số lần ĐẠT liên tiếp gần nhất (0 = lần gần nhất chưa đạt)."""
    steps = settings.REVIEW_DUE_INTERVALS
    return steps[0] if streak <= 0 else steps[min(streak, len(steps)) - 1]


def due_info(db: Session, user_id: int, skill_ids=None, *, now: datetime | None = None) -> dict[int, dict]:
    """{skill_id: {due, due_at, last_reviewed_at, last_passed, last_score, streak, interval_days}} cho các kỹ năng
    được xét (Đã biết + từng ôn đạt). skill_ids=None → mọi kỹ năng Đã biết của người học."""
    now = now or datetime.now(UTC)
    known = repo.known_skill_ids(db, user_id, skill_ids)
    history: dict[int, list] = defaultdict(list)
    for skill_id, submitted_at, passed, score in repo.skill_review_history(db, user_id, known):
        history[skill_id].append((_aware(submitted_at), bool(passed), score))

    result = {}
    for skill_id, rows in history.items():
        if not any(passed for _, passed, _ in rows):
            continue  # chưa từng ôn đạt → chưa có gì để "ôn lại"
        last_at, last_passed, last_score = rows[-1]
        streak = 0
        for _, passed, _ in reversed(rows):
            if not passed:
                break
            streak += 1
        days = interval_days(streak)
        due_at = last_at + timedelta(days=days)
        result[skill_id] = {
            "due": now >= due_at,
            "due_at": due_at,
            "last_reviewed_at": last_at,
            "last_passed": last_passed,
            "last_score": float(last_score) if last_score is not None else None,
            "streak": streak,
            "interval_days": days,
        }
    return result


def _reminders(db: Session, user_id: int, due: dict[int, dict]) -> list[ReviewDueReminder]:
    """Dòng nhắc cho đúng HẠN HIỆN TẠI của các kỹ năng đến hạn (tạo nếu chưa có)."""
    rows = []
    for skill_id, info in due.items():
        row = db.scalar(
            select(ReviewDueReminder).where(
                ReviewDueReminder.user_id == user_id,
                ReviewDueReminder.skill_id == skill_id,
                ReviewDueReminder.due_at == info["due_at"],
            )
        )
        if row is None:
            row = ReviewDueReminder(user_id=user_id, skill_id=skill_id, due_at=info["due_at"])
            db.add(row)
        rows.append(row)
    db.flush()
    return rows


def _last(db: Session, user_id: int, column) -> datetime | None:
    # MAX bỏ qua NULL trên mọi CSDL. (ORDER BY … DESC LIMIT 1 trên PostgreSQL đưa NULL lên ĐẦU → trả None dù đã
    # từng nhắc → mất giới hạn 24 giờ / 1 tuần; SQLite xếp NULL cuối nên test không bắt được — sửa 21/11.)
    value = db.scalar(select(func.max(column)).where(ReviewDueReminder.user_id == user_id))
    return _aware(value) if value is not None else None


def remind_user(db: Session, user_id: int, *, now: datetime | None = None) -> dict:
    """Nhắc MỘT người học (chỉ flush; người gọi commit). Trả {"notified": số kỹ năng, "emailed": số kỹ năng}."""
    now = now or datetime.now(UTC)
    due = {s: i for s, i in due_info(db, user_id, now=now).items() if i["due"]}
    if not due:
        return {"notified": 0, "emailed": 0}
    rows = _reminders(db, user_id, due)
    names = repo.skill_names(db, due)
    out = {"notified": 0, "emailed": 0}

    to_notify = [r for r in rows if r.notified_at is None]
    last_notified = _last(db, user_id, ReviewDueReminder.notified_at)
    if to_notify and (last_notified is None or now - last_notified >= NOTIFY_EVERY):
        skills = [names.get(r.skill_id, f"Kỹ năng {r.skill_id}") for r in to_notify]
        notification_service.notify(
            db,
            user_id,
            "review_due",
            f"Có {len(skills)} kỹ năng đến hạn ôn" if len(skills) > 1 else f"Đến hạn ôn: {skills[0]}",
            body="Ôn lại đúng lúc giúp bạn nhớ lâu hơn: " + ", ".join(skills) + ".",
            link=REVIEW_LINK,
        )
        for r in to_notify:
            r.notified_at = now
        out["notified"] = len(to_notify)

    to_email = [r for r in rows if r.emailed_at is None]
    last_emailed = _last(db, user_id, ReviewDueReminder.emailed_at)
    email_due = last_emailed is None or now - last_emailed >= timedelta(days=settings.REVIEW_DUE_EMAIL_EVERY_DAYS)
    if to_email and email_due and email_preference_service.get_preferences(db, user_id)["review_reminder"]:
        user = db.get(Users, user_id)
        if user is not None and user.is_active:
            send_review_due_email(user.email, user.full_name, [names.get(s, f"Kỹ năng {s}") for s in due])
            for r in to_email:
                r.emailed_at = now
            out["emailed"] = len(to_email)
    db.flush()
    return out


def run_reminders(db: Session, *, now: datetime | None = None) -> dict:
    """Một lượt quét mọi người học từng ôn đạt. Lỗi ở một người không làm dừng cả lượt."""
    total = {"users": 0, "notified": 0, "emailed": 0}
    for user_id in repo.users_with_passed_review(db):
        try:
            out = remind_user(db, user_id, now=now)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Nhắc đến hạn ôn thất bại (user %s)", user_id)
            continue
        if out["notified"] or out["emailed"]:
            total["users"] += 1
            total["notified"] += out["notified"]
            total["emailed"] += out["emailed"]
    return total


# ─────────────── Luồng nền chạy kèm backend ───────────────

_stop = threading.Event()
_thread: threading.Thread | None = None
FIRST_RUN_DELAY = 60  # giây: để backend khởi động xong rồi mới quét


def _loop(session_factory) -> None:
    wait = FIRST_RUN_DELAY
    while not _stop.wait(wait):
        db = session_factory()
        try:
            total = run_reminders(db)
            if total["users"]:
                logger.info("Nhắc đến hạn ôn: %s", total)
        except Exception:
            logger.exception("Lượt nhắc đến hạn ôn thất bại")
        finally:
            db.close()
        wait = settings.REVIEW_DUE_JOB_INTERVAL


def start_background(session_factory) -> bool:
    """Gọi trong lifespan của app. MẶC ĐỊNH TẮT — bật bằng REVIEW_DUE_JOB_ENABLED=true trong backend/.env. Chạy
    trùng (nhiều tiến trình) vẫn không nhắc lặp nhờ bảng review_due_reminders."""
    global _thread
    if not settings.REVIEW_DUE_JOB_ENABLED or (_thread is not None and _thread.is_alive()):
        return False
    _stop.clear()
    _thread = threading.Thread(target=_loop, args=(session_factory,), name="review-due-reminders", daemon=True)
    _thread.start()
    return True


def stop_background() -> None:
    _stop.set()
