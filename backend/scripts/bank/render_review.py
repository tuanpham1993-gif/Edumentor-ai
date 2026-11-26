"""Xuất file duyệt Markdown cho người duyệt đề (tiếng Anh gốc + ghi chú tiếng Việt).

    python -m scripts.bank.render_review 494                     (đầy đủ: đoạn + trắc nghiệm + tự luận)
    python -m scripts.bank.render_review 494 --essays-only       (chỉ tự luận + bài thử)
    python -m scripts.bank.render_review 494 --out ~/Downloads/de-494.md

Mặc định ghi vào data/bank_runs/review_<id>_<giờ>.md.
"""

import argparse
from pathlib import Path

from scripts.bank.common import bank_path, load_bank, load_course, quiet, run_file

LEVEL = {"recognize": "Nhận biết", "understand": "Thông hiểu", "easy": "Tự luận dễ", "advanced": "Tự luận nâng cao"}
HEADER = [
    (
        "**Cách đọc barem:** mỗi ý có *từ khóa chính* (phải có trong bài) và có thể có *chủ thể* (phải cùng vế câu với từ "
        "khóa chính). Câu mô tả ý theo hai mẫu: `(any one of: a, b, c)` = nêu MỘT chi tiết là đạt; `(both needed: a; b)` "
        "= phải đủ cả hai. Gemini chấm chính theo nghĩa câu mô tả; từ khóa là dự phòng / đối chiếu."
    ),
    "",
    (
        "**Bài thử:** chạy tự động mỗi lần kiểm đề (`python -m scripts.bank.check`). *(c)* = giới hạn đã biết: đảo vai trò "
        "trong cùng một vế câu vẫn lọt bộ chấm từ khóa."
    ),
    "",
]


def render(data: dict, course, *, essays_only: bool) -> list[str]:
    from app.ai.review.question_gate import keyword_score, model_answer

    title = f"# Đề khóa {course.COURSE_ID} — {course.COURSE_TITLE}" + (" — tự luận" if essays_only else "")
    lines = [title, "", *HEADER]
    for skill, name in course.SKILL_NAMES.items():
        lines += [f"## {name} — #{course.SKILLS[skill]}", ""]
        if not essays_only:
            lines += ["### Đoạn tài liệu", ""]
            for c in [c for c in data["chunks"] if c["skill"] == skill]:
                lines += [
                    f"**{c['code']} — {c['title']}**",
                    "",
                    f"> {c['content']}",
                    "",
                    f"🇻🇳 {course.VN_CHUNK.get(c['code'], '')}",
                    "",
                ]
            lines += ["### Câu hỏi", ""]
        for q in [q for q in data["questions"] if q["skill"] == skill]:
            if q["type"] == "mcq":
                if essays_only:
                    continue
                lines += [f"**{q['code']}** ({LEVEL[q['level']]}, đoạn {q['chunk']}) — {q['content']}", ""]
                for i, o in enumerate(q["options"]):
                    ok = i == q["correct_index"]
                    lines.append(f"- {'**' if ok else ''}{'ABCD'[i]}. {o}{' ✔**' if ok else ''}")
                lines += [f"- *Giải thích:* {q['explanation']}", "", f"🇻🇳 {course.VN_MCQ.get(q['code'], '')}", ""]
                continue
            lines += [
                f"### {q['code']} ({LEVEL[q['level']]}, đoạn {q['chunk']})",
                "",
                f"> {q['content']}",
                "",
                f"🇻🇳 {course.VN_ESSAY.get(q['code'], '')}",
                "",
            ]
            for i, r in enumerate(q["rubric"], start=1):
                sub = f" — chủ thể: `{' | '.join(r['sub_keywords'])}`" if r["sub_keywords"] else ""
                lines.append(
                    f"- **Ý {i} ({r['max_points']} đ):** {r['text']} — từ khóa: `{' | '.join(r['main_keywords'])}`{sub}"
                )
            lines += [
                "",
                f"*{q['explanation']}* → **{keyword_score(q['rubric'], model_answer(q), q['content'])}/10**",
                "",
                "| Bài thử | Điểm | Cần |",
                "|---|---|---|",
            ]
            for label, text, cond in course.PROBES.get(q["code"], []):
                sc = keyword_score(q["rubric"], text, q["content"])
                need = "(c)" if cond == "c" else cond.replace(">=", "≥ ").replace("<=", "≤ ")
                lines.append(f'| {label}: "{text}" | {sc} | {need} |')
            lines.append("")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Xuất file duyệt Markdown")
    parser.add_argument("course_id", type=int)
    parser.add_argument("--essays-only", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    quiet()
    course = load_course(args.course_id)
    lines = render(load_bank(bank_path(args.course_id)), course, essays_only=args.essays_only)
    out = args.out.expanduser() if args.out else run_file(f"review_{args.course_id}", ".md")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("đã ghi", out, len(lines), "dòng")


if __name__ == "__main__":
    main()
