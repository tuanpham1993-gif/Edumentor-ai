"""Xem trước câu AI soạn cho vài kỹ năng (module 09 · Tuấn · G3b, 25/11/2026) — gọi Gemini thật, KHÔNG lưu DB.

Dùng để đọc chất lượng câu trước khi làm cổng kiểm tra (G3c) và soạn ở nền (G3d). Cần AI_MODE=real + khóa Gemini, kỹ năng
phải Mở (G3.0) và có đoạn tài liệu (G3a).

    cd backend
    python -m app.core.seed_data.preview_generated_questions --skills "Docker,Power BI" --out data/cache/questions.md
"""

import argparse
import sys
import time
from pathlib import Path

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.seed_data.write_knowledge_chunks import _pick

LETTERS = "ABCD"
LEVEL_VI = {"recognize": "TN nhận biết", "understand": "TN thông hiểu", "easy": "TL dễ", "advanced": "TL nâng cao"}


def _render(result: dict, chunks: dict[int, str]) -> list[str]:
    lines = [f"\n## {result['skill']} (#{result['skill_id']}) — {len(result['questions'])} câu, "
             f"{result['calls']} lần gọi Gemini" + (f", còn thiếu {result['missing']}" if result["missing"] else "")
             + "\n"]  # fmt: skip
    for i, q in enumerate(result["questions"], start=1):
        gen = q["ai_check"]["gen"]
        lines.append(f"\n### {i}. [{LEVEL_VI[q['level']]}] {q['content']}\n")
        if q["type"] == "mcq":
            for k, opt in enumerate(q["options"]):
                mark = " ✅" if k == q["correct_index"] else ""
                lines.append(f"- {LETTERS[k]}. {opt}{mark}")
        else:
            for item in q["rubric"]:
                lines.append(f"- ({item['max_points']} đ) {item['text']} — từ khóa: {', '.join(item['main_keywords'])}")
        lines.append(f"\n*Giải thích:* {q['explanation']}  ")
        lines.append(f"*Đoạn nguồn:* {chunks.get(q['chunk_id'], q['chunk_id'])} · *câu trích:* \"{gen['source_quote']}\""
                     f" · lần soạn {gen['attempt']}\n")  # fmt: skip
    if result["rejected"]:
        lines.append("\n**Bị loại / soạn lại:**\n")
        for r in result["rejected"]:
            lines += [f"- {r['kind']} lần {r['attempt']}: {e}" for e in r["errors"]]
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Xem trước câu AI soạn (G3b) — không lưu DB")
    parser.add_argument("--skills", required=True, help='tên kỹ năng, cách nhau bằng dấu phẩy, vd "Docker,Power BI"')
    parser.add_argument("--out", default="data/cache/generated_questions_preview.md")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    from app.ai.prompts.review_generate import GEN_PROMPT_VERSION
    from app.ai.review.base import AIUnavailableError
    from app.ai.review.real_ai import RealAI, review_llm
    from app.repositories import knowledge_repository
    from app.services import question_gen_service as gen

    key, model = review_llm()
    if settings.AI_MODE != "real" or not key or not model:
        print("Cần AI_MODE=real và LLM_API_KEY / LLM_MODEL trong .env để gọi Gemini.")
        return 1
    ai = RealAI()
    lines = [f"# Câu AI soạn — xem trước (G3b, prompt {GEN_PROMPT_VERSION}, model {model})\n"]
    with SessionLocal() as db:
        for name in [n.strip() for n in args.skills.split(",") if n.strip()]:
            skill_id = _pick(db, name)
            if skill_id is None:
                print(f"- {name}: không tìm thấy kỹ năng")
                continue
            result = None
            for wait in (20, 40, None):  # Gemini 503 (quá tải) → chờ rồi thử lại cả kỹ năng
                try:
                    result = gen.generate(db, skill_id, write=ai.write_questions, model=model)
                    break
                except gen.GenError as err:
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
            print(f"- {name} (#{skill_id}): {len(result['questions'])} câu, {result['calls']} lần gọi, "
                  f"thiếu {result['missing'] or 0}")  # fmt: skip
            chunks = {c.chunk_id: c.title for c in knowledge_repository.chunks_for_skill(db, skill_id)}
            lines += _render(result, chunks)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Đã xuất → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
