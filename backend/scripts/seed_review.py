"""Nạp ngân hàng câu hỏi + tài liệu tri thức ôn tập từ file JSON (module 09 · Tuấn · GĐ1, 09/11/2026).

Chạy (trong thư mục backend):
    python -m scripts.seed_review                                   # mặc định data/review/course_312.json
    python -m scripts.seed_review --file data/review/course_37.json
    python -m scripts.seed_review --apply-changes                   # áp thay đổi của file vào câu ĐÃ có
    # Chuyển sang ngân hàng tiếng Anh (D1, 13/11) — nạp bản tiếng Anh + ngừng dùng bản tiếng Việt, cùng 1 giao dịch:
    python -m scripts.seed_review --file data/review/course_312_en.json --retire data/review/course_312.json

- KIỂM TRA TRƯỚC, GHI SAU: dữ liệu sai ở đâu → in TẤT CẢ lỗi, không ghi gì vào DB.
- QT4 (chốt 12/11): DATABASE là nơi lưu chính (admin sửa trên trang quản trị). Seed mặc định CHỈ THÊM câu chưa có
  (tìm theo `code`); câu đã có mà nội dung khác file → chỉ BÁO, KHÔNG ghi đè (tránh xóa mất phần admin đã sửa).
  `--apply-changes`: áp thay đổi của file qua review_bank_service.update_question → câu đã có trong bài làm thì tạo
  PHIÊN BẢN MỚI (bài cũ giữ bản cũ — tránh lỗi 11/11 sửa đè đáp án làm lịch sử sai).
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
from app.services import review_bank_service

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


def seed_bank(db: Session, data: dict, *, apply_changes: bool = False) -> dict:
    """Ghi vào DB (chỉ flush — main() commit). Gọi SAU khi validate_bank + check_against_db không lỗi.

    Câu hỏi (QT4): chưa có → thêm (phiên bản 1); có rồi, giống file → bỏ qua; khác file → chỉ ghi mã vào
    `questions_differ` (không đè) trừ khi apply_changes=True (sửa tại chỗ / tạo phiên bản mới nếu đã có bài làm).
    """
    skills = data["skills"]
    counts = {
        "chunks_added": 0,
        "chunks_updated": 0,
        "questions_added": 0,
        "questions_unchanged": 0,
        "questions_differ": [],
        "questions_updated": 0,
        "questions_versioned": 0,
    }

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
        wanted = {
            "skill_id": skills[q["skill"]],
            "chunk_id": chunk_ids.get(q.get("chunk")),
            "level": q["level"],
            "content": q["content"],
            "options": q.get("options"),
            "correct_index": q.get("correct_index"),
            "rubric": q.get("rubric"),
            "explanation": q.get("explanation"),
        }
        row = db.query(ReviewQuestion).filter_by(code=q["code"]).one_or_none()
        if row is None:
            review_bank_service.create_question(db, {"code": q["code"], "type": q["type"], **wanted})
            counts["questions_added"] += 1
            continue
        differs = sorted(f for f, v in wanted.items() if getattr(row, f) != v)
        if not differs:
            counts["questions_unchanged"] += 1
        elif not apply_changes:
            counts["questions_differ"].append(q["code"])  # QT4: chỉ báo, không ghi đè
        else:
            result = review_bank_service.update_question(
                db, row, {f: wanted[f] for f in differs}, note=f"seed --apply-changes: {', '.join(differs)}"
            )
            counts["questions_versioned" if result.versioned else "questions_updated"] += 1
    db.flush()
    return counts


def retire_bank(db: Session, old: dict) -> dict:
    """Ngừng dùng một ngân hàng cũ (vd bản tiếng Việt khi chuyển sang tiếng Anh — D1, 13/11):
    - câu hỏi có mã trong file cũ → TẮT (không xóa: bài làm cũ vẫn trỏ tới, lịch sử vẫn xem đúng);
    - đoạn tri thức có mã trong file cũ → XÓA (bảng không có cột bật / tắt; giữ lại thì RAG lấy lẫn hai ngôn ngữ).
      Câu hỏi đang trỏ tới đoạn đó → chunk_id = NULL trước (không phụ thuộc DB có bật ON DELETE SET NULL hay không).
    Chỉ flush — main() commit chung với seed_bank của ngân hàng mới."""
    codes = [q["code"] for q in old.get("questions", [])]
    deactivated = (
        db.query(ReviewQuestion)
        .filter(ReviewQuestion.code.in_(codes), ReviewQuestion.is_active.is_(True))
        .update({ReviewQuestion.is_active: False}, synchronize_session=False)
    )
    chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.code.in_([c["code"] for c in old.get("chunks", [])])).all()
    chunk_ids = [c.chunk_id for c in chunks]
    if chunk_ids:
        db.query(ReviewQuestion).filter(ReviewQuestion.chunk_id.in_(chunk_ids)).update(
            {ReviewQuestion.chunk_id: None}, synchronize_session=False
        )
    for c in chunks:
        db.delete(c)
    db.flush()
    return {"questions_deactivated": deactivated, "chunks_deleted": len(chunks)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Nạp ngân hàng câu hỏi ôn tập từ JSON")
    parser.add_argument("--file", default=str(DEFAULT_FILE))
    parser.add_argument(
        "--apply-changes",
        action="store_true",
        help="áp thay đổi của file vào câu đã có (câu đã có bài làm → phiên bản mới)",
    )
    parser.add_argument(
        "--retire",
        metavar="FILE_CU",
        help="sau khi nạp --file, ngừng dùng ngân hàng cũ: tắt câu hỏi + xóa đoạn tri thức có mã trong FILE_CU",
    )
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
        counts = seed_bank(db, data, apply_changes=args.apply_changes)
        retired = retire_bank(db, load_bank(args.retire)) if args.retire else None
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(
        f"Khóa {data['course_id']}: đoạn tri thức +{counts['chunks_added']} / cập nhật "
        f"{counts['chunks_updated']}; câu hỏi +{counts['questions_added']} / giữ nguyên "
        f"{counts['questions_unchanged']} / sửa tại chỗ {counts['questions_updated']} / "
        f"phiên bản mới {counts['questions_versioned']}"
    )
    if counts["questions_differ"]:
        print(
            f"{len(counts['questions_differ'])} câu khác file nhưng KHÔNG ghi đè (database là nơi lưu chính — QT4): "
            + ", ".join(counts["questions_differ"])
        )
        print("Muốn áp thay đổi của file: chạy lại với --apply-changes (câu đã có bài làm → phiên bản mới).")
    if retired is not None:
        print(
            f"Ngừng dùng {args.retire}: tắt {retired['questions_deactivated']} câu hỏi, "
            f"xóa {retired['chunks_deleted']} đoạn tri thức. Nhớ chạy: python -m scripts.build_embeddings"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
