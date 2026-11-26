"""AI viết đoạn tri thức cho MỘT VÀI kỹ năng theo tên (module 09 · Tuấn · G3a, 24/11/2026) — dùng để đo / thử.

Bình thường đoạn được viết TỰ ĐỘNG khi học viên ôn kỹ năng thiếu câu (G3d) hoặc admin bấm "AI viết đoạn tài liệu".
Script này không viết hàng loạt cho cả 3.467 kỹ năng Mở (tốn lượt Gemini). Cần AI_MODE=real + LLM_API_KEY / LLM_MODEL.

    cd backend
    python -m app.core.seed_data.write_knowledge_chunks --skills "Docker,Git,Microsoft Excel" --out data/cache/chunks.md
"""

import argparse
import sys
import time
from pathlib import Path

from sqlalchemy import func, select

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.skill import Skills


def _pick(db, name: str) -> int | None:
    """Tên trùng ("Docker" / "docker") → ưu tiên id đang Mở, có nhiều khóa làm nguồn nhất."""
    from app.repositories import knowledge_repository as repo
    from app.services import skill_scope_service

    ids = db.scalars(
        select(Skills.skill_id).where(func.lower(Skills.skill) == name.strip().lower(), Skills.is_active.is_(True))
    ).all()
    if not ids:
        return None
    return max(ids, key=lambda i: (skill_scope_service.is_open(db, i), len(repo.course_sources(db, i)), -i))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AI viết đoạn tri thức cho vài kỹ năng (G3a)")
    parser.add_argument("--skills", required=True, help='tên kỹ năng, cách nhau bằng dấu phẩy, vd "Docker,Git"')
    parser.add_argument("--out", default="data/cache/knowledge_chunks_preview.md", help="xuất các đoạn ra file để đọc")
    args = parser.parse_args(argv)

    from app.ai.review.base import AIUnavailableError
    from app.ai.review.real_ai import RealAI, review_llm
    from app.repositories import knowledge_repository as repo
    from app.services import knowledge_service

    key, model = review_llm()
    if settings.AI_MODE != "real" or not key or not model:
        print("Cần AI_MODE=real và LLM_API_KEY / LLM_MODEL trong .env để gọi Gemini.")
        return 1
    ai = RealAI()
    lines = ["# Đoạn tri thức AI viết (G3a — xem trước để kiểm)\n"]
    with SessionLocal() as db:
        for name in [n for n in args.skills.split(",") if n.strip()]:
            skill_id = _pick(db, name)
            if skill_id is None:
                print(f"- {name}: không tìm thấy kỹ năng")
                continue
            result = None
            for wait in (20, 40, None):  # Gemini 503 (quá tải, đo 24/11) → chờ rồi thử lại
                try:
                    result = knowledge_service.ensure_chunks(db, skill_id, write=ai.write_knowledge, model=model)
                    break
                except knowledge_service.KnowledgeError as err:
                    print(f"- {name} (#{skill_id}): {err.message}")
                    break
                except AIUnavailableError as err:
                    if wait is None:
                        print(f"- {name} (#{skill_id}): AI không phản hồi ({err}) — bỏ qua")
                        break
                    print(f"  {name}: {err} — chờ {wait} giây rồi thử lại")
                    time.sleep(wait)
            if result is None:
                continue
            print(f"- {name} (#{skill_id}): viết mới {len(result['created'])} đoạn, đã có {result['existing']}")
            sources = {c["course_id"]: c["title"] for c in repo.course_sources(db, skill_id)}
            lines.append(f"\n## {name} (#{skill_id})\n\nNguồn: " + " · ".join(sources.values()) + "\n")
            for c in repo.chunks_for_skill(db, skill_id):
                lines.append(f"\n### {c.title} — `{c.source}` ({len(c.content.split())} từ)\n\n{c.content}\n")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(lines), encoding="utf-8")
    print(f"Đã xuất → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
