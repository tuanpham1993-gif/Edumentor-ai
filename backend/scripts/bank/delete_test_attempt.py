"""Xóa MỘT lượt ôn tập của TÀI KHOẢN THỬ (sau khi chạy thử đề trên server) — có rào chắn vì nằm trong repo chung.

    python -m scripts.bank.delete_test_attempt 86              CHẠY THỬ: chỉ in những gì sẽ xóa
    python -m scripts.bank.delete_test_attempt 86 --apply      sao lưu → xóa (một transaction) → kiểm lại còn 0 dòng

Rào chắn (Tuấn duyệt 27/11):
  1. Mặc định chỉ chạy thử; phải có --apply mới xóa.
  2. Chỉ tài khoản thử, phải thỏa CẢ HAI: user ID có trong scripts/bank/test_users.local.json (file cục bộ, .gitignore —
     mẫu test_users.example.json) VÀ email đúng mẫu tài khoản thử (@example.com hoặc bí danh "+hv<số>@"). Không in email.
  3. Bắt buộc sao lưu trước khi xóa (data/bank_runs/backups/, .gitignore); ghi sao lưu lỗi → không xóa.
  4. Lượt đã làm khóa học Hoàn thành (is_first_pass) → từ chối, xử lý tay.
Xóa cùng lượt: bài làm, chuông kết quả (source_id = lượt), kỹ năng "Đã biết" CHỈ KHI dòng đó do chính lượt này tạo
(source='review', tạo cùng lúc với chuông kết quả, chưa sửa lần nào). Cờ hàng chờ giáo viên nằm trong trace của lượt →
mất theo. Email kết quả đã gửi thì không rút lại được.
"""

import argparse
import json
import re
from pathlib import Path

from scripts.bank.common import TEST_USERS_FILE, quiet, run_file, write_json

TEST_EMAIL = re.compile(r"(@example\.com$)|(\+hv\d+@)", re.IGNORECASE)


class Refused(Exception):
    """Không được xóa — lý do trong thông điệp."""


def allowed_user_ids(path: Path = TEST_USERS_FILE) -> set[int]:
    if not path.exists():
        raise Refused(
            f"chưa có {path.name} — chép test_users.example.json thành {path.name} rồi ghi user ID tài khoản thử"
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    return {int(u) for u in data.get("user_ids", [])}


def _row(obj) -> dict:
    return {c.name: getattr(obj, c.key) for c in obj.__table__.columns}


def plan(db, attempt_id: int, allowed: set[int]) -> dict:
    """Những dòng sẽ xóa. Từ chối (Refused) nếu không phải tài khoản thử / lượt làm khóa Hoàn thành."""
    from app.models import Notification, ReviewAnswer, ReviewAttempt, Users, UserSkill

    attempt = db.get(ReviewAttempt, attempt_id)
    if attempt is None:
        raise Refused(f"không có lượt {attempt_id}")
    user = db.get(Users, attempt.user_id)
    if attempt.user_id not in allowed or not TEST_EMAIL.search((user.email if user else "") or ""):
        raise Refused(f"lượt {attempt_id} không thuộc tài khoản thử (cần CẢ user ID trong danh sách VÀ email đúng mẫu)")
    if attempt.is_first_pass:
        raise Refused(f"lượt {attempt_id} đã làm khóa học Hoàn thành — xử lý tay, không xóa bằng công cụ")
    answers = db.query(ReviewAnswer).filter_by(attempt_id=attempt_id).all()
    notes = db.query(Notification).filter_by(source_id=attempt_id, user_id=attempt.user_id, type="review_graded").all()
    skills = []
    if attempt.passed and attempt.skill_id is not None and notes:
        row = db.get(UserSkill, (attempt.user_id, attempt.skill_id))
        graded_at = notes[0].created_at
        if row is not None and row.source == "review" and row.created_at == graded_at and row.updated_at == graded_at:
            skills.append(row)
    return {"attempt": attempt, "review_answers": answers, "notifications": notes, "user_skills": skills}


def counts(p: dict) -> dict:
    return {
        "review_attempts": 1,
        "review_answers": len(p["review_answers"]),
        "notifications": len(p["notifications"]),
        "user_skills": len(p["user_skills"]),
    }


def backup(p: dict, path: Path) -> None:
    write_json(
        path,
        {
            "note": f"Sao lưu trước khi xóa lượt thử {p['attempt'].attempt_id}",
            "review_attempts": [_row(p["attempt"])],
            "review_answers": [_row(a) for a in p["review_answers"]],
            "notifications": [_row(n) for n in p["notifications"]],
            "user_skills": [_row(s) for s in p["user_skills"]],
        },
    )


def delete(db, attempt_id: int, allowed: set[int], backup_path: Path) -> dict:
    """Sao lưu rồi xóa trong MỘT transaction; kiểm lại còn 0 dòng. Lỗi ở bất kỳ bước nào → rollback, không xóa gì."""
    from app.models import Notification, ReviewAnswer, ReviewAttempt

    try:
        p = plan(db, attempt_id, allowed)
        expected = counts(p)
        backup(p, backup_path)  # lỗi ghi file → ngoại lệ → không xóa
        if not backup_path.exists():
            raise Refused("không ghi được file sao lưu — không xóa")
        for obj in (*p["notifications"], *p["user_skills"], *p["review_answers"]):
            db.delete(obj)
        db.flush()
        db.delete(p["attempt"])
        db.flush()
        left = {
            "review_attempts": db.query(ReviewAttempt).filter_by(attempt_id=attempt_id).count(),
            "review_answers": db.query(ReviewAnswer).filter_by(attempt_id=attempt_id).count(),
            "notifications": db.query(Notification).filter_by(source_id=attempt_id, type="review_graded").count(),
        }
        if any(left.values()):
            raise Refused(f"xóa xong vẫn còn dòng {left} — rollback")
        db.commit()
        return expected
    except Exception:
        db.rollback()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Xóa một lượt ôn tập của tài khoản thử (mặc định chỉ chạy thử)")
    parser.add_argument("attempt_id", type=int)
    parser.add_argument("--apply", action="store_true", help="xóa thật (mặc định chỉ in những gì sẽ xóa)")
    args = parser.parse_args()
    quiet()
    from app.core.database import SessionLocal

    try:
        allowed = allowed_user_ids()
        with SessionLocal() as db:
            if not args.apply:
                p = plan(db, args.attempt_id, allowed)
                a = p["attempt"]
                print(
                    f"CHẠY THỬ — lượt {a.attempt_id} (user {a.user_id}, kỹ năng {a.skill_id}, khóa {a.course_id}, "
                    f"đạt={a.passed}) sẽ xóa: {counts(p)}. Thêm --apply để xóa (có sao lưu)."
                )
                return 0
            out = run_file(f"backups/attempt_{args.attempt_id}")
            n = delete(db, args.attempt_id, allowed, out)
            print(f"đã sao lưu → {out}\nđã xóa: {n}; kiểm lại: còn 0 dòng")
            return 0
    except Refused as err:
        print("TỪ CHỐI:", err)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
