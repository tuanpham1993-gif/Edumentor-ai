"""Dựng file đề JSON từ nguồn của một khóa (scripts/bank/courses/course_<id>/).

    python -m scripts.bank.build 494                 → data/review/course_494_en.json
    python -m scripts.bank.build 494 --out x.json

Nhóm loại trừ (7.5b): khóa khai `EXCLUSION = {mã câu: tên nhóm}` → câu cùng nhóm không vào cùng một đề (bộ ráp đề
né mềm). Khóa không khai EXCLUSION → JSON không có trường này (giữ nguyên từng byte file cũ).

Trắc nghiệm: đáp án đúng viết ĐẦU TIÊN trong nguồn; ở đây xoay nó vào vị trí 0..3 (vòng tròn qua mọi kỹ năng) để
đáp án đúng rải đều A/B/C/D. Mã câu: <KỸ NĂNG>-TN-01…, <KỸ NĂNG>-TL-01…; mã đoạn: <KỸ NĂNG>-K01…
"""

import argparse
import json
from pathlib import Path

from scripts.bank.common import bank_path, load_course


def build(course) -> dict:
    chunk_codes, chunks = {}, []
    for skill in course.SKILLS:
        n = 0
        for s, title, content in course.CHUNKS:
            if s != skill:
                continue
            n += 1
            code = f"{skill}-K{n:02d}"
            chunk_codes[(skill, n)] = code
            chunks.append({"code": code, "skill": skill, "title": title, "content": content})
    questions, slot = [], 0
    for skill in course.SKILLS:
        for i, (c, level, content, options, expl) in enumerate(course.MCQ[skill], start=1):
            target = slot % 4
            slot += 1
            opts = options[1:]
            opts.insert(target, options[0])
            questions.append(
                {
                    "code": f"{skill}-TN-{i:02d}",
                    "skill": skill,
                    "chunk": chunk_codes[(skill, c)],
                    "type": "mcq",
                    "level": level,
                    "content": content,
                    "options": opts,
                    "correct_index": target,
                    "explanation": expl,
                }
            )
        for i, (c, level, content, items, answer) in enumerate(course.ESSAY[skill], start=1):
            rubric = [
                {"text": t, "max_points": p, "main_keywords": kws, "sub_keywords": sub} for t, p, kws, sub in items
            ]
            questions.append(
                {
                    "code": f"{skill}-TL-{i:02d}",
                    "skill": skill,
                    "chunk": chunk_codes[(skill, c)],
                    "type": "essay",
                    "level": level,
                    "content": content,
                    "rubric": rubric,
                    "explanation": "Model answer: " + answer,
                }
            )
    # Câu trắc nghiệm BỔ SUNG (MCQ_EXTRA, 27/11): mã nối tiếp, xoay vị trí đáp án tiếp từ `slot` — câu cũ không đổi
    for skill in course.SKILLS:
        start = len(course.MCQ.get(skill, []))
        for i, (c, level, content, options, expl) in enumerate(getattr(course, "MCQ_EXTRA", {}).get(skill, []), 1):
            target = slot % 4
            slot += 1
            opts = options[1:]
            opts.insert(target, options[0])
            questions.append(
                {
                    "code": f"{skill}-TN-{start + i:02d}",
                    "skill": skill,
                    "chunk": chunk_codes[(skill, c)],
                    "type": "mcq",
                    "level": level,
                    "content": content,
                    "options": opts,
                    "correct_index": target,
                    "explanation": expl,
                }
            )
    exclusion = getattr(course, "EXCLUSION", None)
    if exclusion is not None:  # 7.5b: khóa có khai EXCLUSION → MỌI câu có trường (null = không nhóm, seed bỏ nhóm cũ)
        unknown = set(exclusion) - {q["code"] for q in questions}
        if unknown:
            raise ValueError(f"EXCLUSION có mã câu không tồn tại: {sorted(unknown)}")
        for q in questions:
            q["exclusion_group"] = exclusion.get(q["code"])
    return {
        "course_id": course.COURSE_ID,
        "course_title": course.COURSE_TITLE,
        "note": course.NOTE,
        "skills": course.SKILLS,
        "chunks": chunks,
        "questions": questions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Dựng file đề JSON từ scripts/bank/courses/course_<id>/")
    parser.add_argument("course_id", type=int)
    parser.add_argument("--out", type=Path, help="mặc định data/review/course_<id>_en.json")
    args = parser.parse_args()
    out = args.out or bank_path(args.course_id)
    out.write_text(
        json.dumps(build(load_course(args.course_id)), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("đã ghi", out)


if __name__ == "__main__":
    main()
