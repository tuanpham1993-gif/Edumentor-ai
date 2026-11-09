"""Nạp ngân hàng câu hỏi + tài liệu tri thức ôn tập từ file JSON (module 09 · Tuấn · GĐ1, 09/11/2026).

Chạy (trong thư mục backend):
    python -m scripts.seed_review                                   # mặc định data/review/course_312.json
    python -m scripts.seed_review --file data/review/course_37.json

- KIỂM TRA TRƯỚC, GHI SAU: dữ liệu sai ở đâu → in TẤT CẢ lỗi, không ghi gì vào DB.
- Chạy lại nhiều lần an toàn: tìm theo `code` → có rồi thì CẬP NHẬT, chưa có thì THÊM (không tạo bản trùng).
- Đoạn tri thức đổi nội dung → xóa embedding cũ (phải chạy lại scripts/build_embeddings.py).
- Câu hỏi đang tắt (is_active=false) giữ nguyên trạng thái tắt — seed không tự bật lại.

Định dạng file: xem data/review/course_312.json
    skills:    {"ITER": 400, ...}            — mã ngắn → skill_id (phải thuộc khóa course_id)
    chunks:    [{code, skill, title, content}]
    questions: [{code, skill, chunk, type, level, content, options, correct_index, rubric, explanation}]
"""

import argparse
import json
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.ai.review.validator import question_errors
from app.core.database import SessionLocal, create_tables
from app.models.course_skill import CourseSkill
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.review_question import ReviewQuestion

DEFAULT_FILE = Path(__file__).resolve().parents[1] / "data" / "review" / "course_312.json"


def load_bank(path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _is_text(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def validate_bank(data: dict) -> list[str]:
    """Kiểm tra cấu trúc file (không cần DB). Trả danh sách lỗi; rỗng = hợp lệ."""
    errors = []
    skills = data.get("skills")
    if not isinstance(data.get("course_id"), int):
        errors.append("Thiếu course_id (số nguyên)")
    if not (isinstance(skills, dict) and skills):
        return errors + ["Thiếu skills: {mã ngắn: skill_id}"]

    chunk_skill = {}
    for c in data.get("chunks", []):
        where = f"Đoạn {c.get('code')}"
        if not _is_text(c.get("code")):
            errors.append("Có đoạn tri thức thiếu code")
        elif c["code"] in chunk_skill:
            errors.append(f"{where}: code bị trùng")
        if c.get("skill") not in skills:
            errors.append(f"{where}: skill '{c.get('skill')}' không có trong skills")
        if not _is_text(c.get("content")):
            errors.append(f"{where}: thiếu content")
        chunk_skill[c.get("code")] = c.get("skill")

    seen = set()
    for q in data.get("questions", []):
        where = f"Câu {q.get('code')}"
        if not _is_text(q.get("code")):
            errors.append("Có câu hỏi thiếu code")
        elif q["code"] in seen:
            errors.append(f"{where}: code bị trùng")
        seen.add(q.get("code"))
        if q.get("skill") not in skills:
            errors.append(f"{where}: skill '{q.get('skill')}' không có trong skills")
        if q.get("chunk") is not None:
            if q["chunk"] not in chunk_skill:
                errors.append(f"{where}: chunk '{q['chunk']}' không tồn tại")
            elif chunk_skill[q["chunk"]] != q.get("skill"):
                errors.append(f"{where}: chunk '{q['chunk']}' thuộc kỹ năng khác")
        errors += question_errors(q, where)  # quy tắc chung với câu AI sinh (ai/review/validator.py)
    return errors


def check_against_db(db: Session, data: dict) -> list[str]:
    """Mọi skill_id trong file phải là kỹ năng của khóa course_id (bảng course_skill — chỉ đọc)."""
    course_skill_ids = {
        row.skill_id
        for row in db.query(CourseSkill.skill_id).filter(CourseSkill.course_id == data["course_id"])
    }
    if not course_skill_ids:
        return [f"Khóa {data['course_id']} không có trong DB hoặc chưa có kỹ năng nào"]
    return [
        f"Kỹ năng {code} (skill_id {skill_id}) không thuộc khóa {data['course_id']}"
        for code, skill_id in data["skills"].items()
        if skill_id not in course_skill_ids
    ]


def seed_bank(db: Session, data: dict) -> dict:
    """Ghi vào DB (chỉ flush — main() commit). Gọi SAU khi validate_bank + check_against_db không lỗi."""
    skills = data["skills"]
    counts = {"chunks_added": 0, "chunks_updated": 0, "questions_added": 0, "questions_updated": 0}

    chunk_ids = {}
    for c in data["chunks"]:
        row = db.query(KnowledgeChunk).filter_by(code=c["code"]).one_or_none()
        if row is None:
            row = KnowledgeChunk(code=c["code"])
            db.add(row)
            counts["chunks_added"] += 1
        else:
            counts["chunks_updated"] += 1
            if row.content != c["content"]:
                row.embedding = None  # nội dung đổi → vector cũ không còn đúng
        row.skill_id = skills[c["skill"]]
        row.title = c.get("title")
        row.content = c["content"]
        db.flush()
        chunk_ids[c["code"]] = row.chunk_id

    for q in data["questions"]:
        row = db.query(ReviewQuestion).filter_by(code=q["code"]).one_or_none()
        if row is None:
            row = ReviewQuestion(code=q["code"], source="bank")
            db.add(row)
            counts["questions_added"] += 1
        else:
            counts["questions_updated"] += 1
        row.skill_id = skills[q["skill"]]
        row.chunk_id = chunk_ids.get(q.get("chunk"))
        row.type = q["type"]
        row.level = q["level"]
        row.content = q["content"]
        row.options = q.get("options")
        row.correct_index = q.get("correct_index")
        row.rubric = q.get("rubric")
        row.explanation = q.get("explanation")
    db.flush()
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Nạp ngân hàng câu hỏi ôn tập từ JSON")
    parser.add_argument("--file", default=str(DEFAULT_FILE))
    args = parser.parse_args()

    data = load_bank(args.file)
    errors = validate_bank(data)
    if errors:
        print(f"File {args.file} có {len(errors)} lỗi — KHÔNG nạp:")
        for e in errors:
            print("-", e)
        return 1

    create_tables()  # phòng khi chạy trước lần đầu khởi động server
    db = SessionLocal()
    try:
        errors = check_against_db(db, data)
        if errors:
            print("Dữ liệu không khớp DB — KHÔNG nạp:")
            for e in errors:
                print("-", e)
            return 1
        counts = seed_bank(db, data)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(
        f"Khóa {data['course_id']}: đoạn tri thức +{counts['chunks_added']} / cập nhật "
        f"{counts['chunks_updated']}; câu hỏi +{counts['questions_added']} / cập nhật "
        f"{counts['questions_updated']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
