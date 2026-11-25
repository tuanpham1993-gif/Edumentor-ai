"""Tắt câu AI soạn TRÙNG Ý đã có trong ngân hàng (module 09 · Tuấn · Bước A, 25/11/2026 — docs mục 7.7).

Cùng ý = cùng loại câu + câu trích phủ lên chung một câu nguồn (app/ai/review/question_idea.py). Mỗi nhóm giữ MỘT câu:
câu mentor đã Đạt trước, rồi câu cũ nhất. Câu còn lại: is_active = False, disabled_reason = 'duplicate_idea' (câu vẫn
nằm trong ngân hàng, admin bật lại được). Câu soạn tay / không có câu trích không bị đụng.

    cd backend
    python -m app.core.seed_data.dedupe_question_ideas --skills "Kubernetes,Power BI"           # chỉ in danh sách
    python -m app.core.seed_data.dedupe_question_ideas --skills "Kubernetes,Power BI" --apply   # tắt thật
"""

import argparse
import sys

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.review import question_idea
from app.core.database import SessionLocal
from app.models.review_question import ReviewQuestion
from app.models.review_question_meta import ReviewQuestionMeta
from app.models.skill import Skills
from app.repositories import review_repository as repo
from app.services.question_gen_service import DUPLICATE_IDEA


def dedupe(db: Session, skill_id: int, *, apply: bool = False) -> dict:
    """→ {"kept": [id…], "disabled": [(id, id câu giữ lại)…]}. apply=False: không ghi DB."""
    rows = [r for r in repo.question_sources(db, skill_id=skill_id) if r.is_active]
    passed = {r.question_id for r in rows if r.mentor_status == "passed"}
    ideas = question_idea.from_rows(rows)
    ideas.sort(key=lambda u: (u.question_id not in passed, u.question_id))
    kept: list[question_idea.UsedIdea] = []
    disabled: list[tuple[int, int]] = []
    for u in ideas:
        same = question_idea.clash(u.idea, u.type, kept)
        if same is None:
            kept.append(u)
        else:
            disabled.append((u.question_id, same.question_id))
    if apply and disabled:
        for qid, _ in disabled:
            db.get(ReviewQuestion, qid).is_active = False
            db.get(ReviewQuestionMeta, qid).disabled_reason = DUPLICATE_IDEA
        db.commit()
    return {"kept": [u.question_id for u in kept], "disabled": disabled}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Tắt câu AI soạn trùng ý (Bước A)")
    parser.add_argument("--skills", required=True, help='Tên kỹ năng, cách nhau bằng dấu phẩy: "Kubernetes,Power BI"')
    parser.add_argument("--apply", action="store_true", help="Tắt thật (mặc định chỉ in danh sách)")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    with SessionLocal() as db:
        for name in [s.strip() for s in args.skills.split(",") if s.strip()]:
            skill_id = db.scalar(select(Skills.skill_id).where(func.lower(Skills.skill) == name.lower()).limit(1))
            if skill_id is None:
                print(f"- {name}: không tìm thấy kỹ năng")
                continue
            result = dedupe(db, skill_id, apply=args.apply)
            print(f"- #{skill_id} {name}: giữ {len(result['kept'])} câu, "
                  f"{'ĐÃ TẮT' if args.apply else 'sẽ tắt'} {len(result['disabled'])} câu")  # fmt: skip
            for qid, keep in result["disabled"]:
                content = db.get(ReviewQuestion, qid).content
                print(f"    #{qid} (trùng ý #{keep}): {content[:100]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
