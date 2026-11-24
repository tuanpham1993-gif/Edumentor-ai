"""Gắn nhãn phạm vi ôn tập cho kỹ năng CHƯA có nhãn bằng Gemini (module 09 · Tuấn · G3.0, 24/11/2026).

Chạy TAY, một lần (không chạy lúc khởi động server — tốn lượt Gemini). Ngắt giữa chừng → chạy lại làm tiếp phần còn thiếu.
Nhãn admin đã sửa không bao giờ bị ghi đè. Cần AI_MODE=real + LLM_API_KEY / LLM_MODEL (hoặc REVIEW_LLM_*) trong .env.

    cd backend
    python -m app.core.seed_data.classify_skill_scopes --limit 200 --dry-run   # thử 200 kỹ năng, in ra, KHÔNG lưu
    python -m app.core.seed_data.classify_skill_scopes                          # phân loại tất cả kỹ năng chưa có nhãn
    python -m app.core.seed_data.classify_skill_scopes --sample 50              # xuất 50 kỹ năng ngẫu nhiên để người kiểm
"""

import argparse
import csv
import random
import sys
from pathlib import Path

from app.core.config import settings
from app.core.database import SessionLocal


def _sample(db, n: int, out: Path) -> None:
    """Xuất n kỹ năng ĐÃ có nhãn AI ra CSV (cột human_label để trống) — người gắn tay rồi so (mục 6 thiết kế G3.0)."""
    from app.models.review_skill_scope import ReviewSkillScope
    from app.models.skill import Skills
    from app.repositories import skill_scope_repository as repo

    rows = db.query(ReviewSkillScope, Skills.skill).join(Skills, Skills.skill_id == ReviewSkillScope.skill_id).all()
    picked = random.Random(2511).sample(rows, min(n, len(rows)))
    titles = repo.top_course_titles(db, [s.skill_id for s, _ in picked])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["skill_id", "skill", "courses", "human_label", "ai_label", "ai_category", "ai_reason"])
        for s, name in picked:
            w.writerow([s.skill_id, name, " | ".join(titles.get(s.skill_id, [])), "", s.label, s.category, s.reason])
    print(f"Đã xuất {len(picked)} kỹ năng → {out}  (điền cột human_label: open / closed / unsure)")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Gắn nhãn phạm vi ôn tập cho kỹ năng (G3.0)")
    parser.add_argument("--limit", type=int, default=None, help="chỉ phân loại N kỹ năng đầu tiên chưa có nhãn")
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--pause", type=float, default=4.0, help="giây nghỉ giữa 2 lô (giới hạn lượt / phút)")
    parser.add_argument("--dry-run", action="store_true", help="in kết quả, không lưu DB")
    parser.add_argument("--sample", type=int, default=0, help="xuất N kỹ năng đã gắn nhãn ra CSV để người kiểm")
    parser.add_argument("--out", default="data/cache/skill_scope_sample.csv")
    args = parser.parse_args(argv)

    with SessionLocal() as db:
        if args.sample:
            _sample(db, args.sample, Path(args.out))
            return 0
        from app.ai.review.real_ai import RealAI, review_llm

        key, model = review_llm()
        if settings.AI_MODE != "real" or not key or not model:
            print("Cần AI_MODE=real và LLM_API_KEY / LLM_MODEL trong .env để gọi Gemini.")
            return 1
        from app.services import skill_scope_service

        summary = skill_scope_service.run(db, RealAI().classify_skills, model=model, limit=args.limit,
                                          batch_size=args.batch_size, pause=args.pause, dry_run=args.dry_run)  # fmt: skip
        print(f"Xong: {summary}" + ("  (dry-run — chưa lưu)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
