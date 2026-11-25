"""Nhãn phạm vi kỹ năng (G3.0) ↔ file JSON (module 09 · Tuấn · P12, làm cùng G3d-1 25/11/2026).

Nhãn Mở / Không mở / Chưa rõ do AI gắn (5.893 kỹ năng, tốn ~60 lần gọi Gemini) chỉ nằm trên DB máy chạy lệnh phân loại →
máy khác / Docker lần đầu = không kỹ năng nào Mở = G3 không soạn được đề. File `data/review/skill_scopes.json` đi theo
repo; khởi tạo DB mà bảng `review_skill_scopes` TRỐNG thì tự nạp (review_autoseed). Đã có nhãn → không đè (admin sửa tay).

    cd backend
    python -m app.core.seed_data.skill_scopes_json --export   # DB → file (sau khi phân loại / admin sửa nhãn)
    python -m app.core.seed_data.skill_scopes_json --import   # file → DB (chỉ khi bảng trống)

Khớp kỹ năng theo `skill_id`; id lệch (DB nạp khác thứ tự) thì khớp theo TÊN (không phân biệt hoa thường).
"""

import argparse
import json
import sys
from pathlib import Path

from sqlalchemy import func, select

from app.models.review_skill_scope import ReviewSkillScope
from app.models.skill import Skills

SCOPES_FILE = Path(__file__).resolve().parents[3] / "data" / "review" / "skill_scopes.json"
FIELDS = ("label", "category", "reason", "source", "model", "prompt_version")


def export_scopes(db, path: Path = SCOPES_FILE) -> int:
    rows = db.execute(
        select(ReviewSkillScope, Skills.skill)
        .join(Skills, Skills.skill_id == ReviewSkillScope.skill_id)
        .order_by(ReviewSkillScope.skill_id)
    ).all()
    data = [{"skill_id": s.skill_id, "skill": name, **{f: getattr(s, f) for f in FIELDS}} for s, name in rows]
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ",\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in data)
    path.write_text(f"[\n{lines}\n]\n", encoding="utf-8")  # một nhãn một dòng → git diff dễ đọc
    return len(data)


def seed_scopes_if_empty(db, path: Path = SCOPES_FILE) -> dict:
    """Bảng trống + có file → nạp. Trả {"skipped": bool, "loaded": n, "unmatched": n}. Không commit."""
    if db.scalar(select(func.count()).select_from(ReviewSkillScope)) or not path.exists():
        return {"skipped": True, "loaded": 0, "unmatched": 0}
    by_id = dict(db.execute(select(Skills.skill_id, func.lower(Skills.skill))).all())
    by_name: dict[str, int] = {}
    for skill_id, name in sorted(by_id.items()):
        by_name.setdefault(name, skill_id)
    loaded = unmatched = 0
    seen: set[int] = set()
    for row in json.loads(path.read_text(encoding="utf-8")):
        name = (row.get("skill") or "").lower()
        skill_id = row["skill_id"] if by_id.get(row["skill_id"]) == name else by_name.get(name)
        if skill_id is None or skill_id in seen:
            unmatched += 1
            continue
        seen.add(skill_id)
        db.add(ReviewSkillScope(skill_id=skill_id, **{f: row.get(f) for f in FIELDS if row.get(f) is not None}))
        loaded += 1
    db.flush()
    return {"skipped": False, "loaded": loaded, "unmatched": unmatched}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Nhãn phạm vi kỹ năng ↔ data/review/skill_scopes.json")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--export", action="store_true")
    group.add_argument("--import", dest="do_import", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    from app.core.database import SessionLocal

    with SessionLocal() as db:
        if args.export:
            print(f"Đã xuất {export_scopes(db)} nhãn → {SCOPES_FILE}")
        else:
            result = seed_scopes_if_empty(db)
            db.commit()
            print("Bảng đã có nhãn — bỏ qua." if result["skipped"] else
                  f"Đã nạp {result['loaded']} nhãn, {result['unmatched']} dòng không khớp kỹ năng.")  # fmt: skip
    return 0


if __name__ == "__main__":
    sys.exit(main())
