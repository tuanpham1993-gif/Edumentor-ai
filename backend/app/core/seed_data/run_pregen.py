"""Chạy tay việc SOẠN SẴN ban đêm (module 09 · Tuấn · G3d-3, 25/11/2026 — D24, D26).

Bình thường luồng nền tự chạy mỗi đêm khi REVIEW_PREGEN_ENABLED=true. Lệnh này để xem / thử ngay:

    cd backend
    python -m app.core.seed_data.run_pregen --dry-run          # chỉ liệt kê kỹ năng sẽ soạn (không gọi Gemini)
    python -m app.core.seed_data.run_pregen --limit 2          # soạn thật cho 2 kỹ năng (cần AI_MODE=real)

Câu soạn sẵn lưu origin='nightly' → chỉ vào đề khi mentor đã bấm Đạt (D26).
"""

import argparse
import sys

from app.core.database import SessionLocal


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Soạn sẵn câu ôn tập cho kỹ năng ưu tiên (G3d-3)")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    from app.repositories.skill_scope_repository import skill_name
    from app.services import review_generation_service as gen
    from app.services import review_pregen_service as pregen

    with SessionLocal() as db:
        picked = pregen.pick_skills(db, args.limit)
        for p in picked:
            print(f"- #{p['skill_id']} {skill_name(db, p['skill_id'])}: {p['learners']} người học, "
                  f"{p['attempts']} lượt ôn, thiếu {p['missing']}")  # fmt: skip
    if args.dry_run or not picked:
        return 0
    deps = gen.deps_factory()
    if deps is None:
        print("Cần AI_MODE=real và khóa Gemini.")
        return 1
    print(pregen.run_nightly(SessionLocal, deps, limit=args.limit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
