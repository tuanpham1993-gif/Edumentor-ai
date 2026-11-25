"""Tạo 6 câu MẪU "AI soạn — tự duyệt" cho kỹ năng Docker để test tay trang mentor (module 09 · Tuấn · G3f, 25/11/2026).

Chưa có G3c (AI soạn câu thật) thì hàng chờ mentor trống → script này tạo câu giả lập. Câu mẫu gắn
`ai_check = {"sample": "g3f"}` để xóa đúng câu mẫu. Có 1 câu CỐ Ý SAI (câu "mọi chỉ thị tạo layer") để mentor thử
"Phản ánh lỗi". KHÔNG gọi Gemini.

    cd backend
    python -m app.core.seed_data.make_sample_ai_questions            # tạo (bỏ qua nếu đã có)
    python -m app.core.seed_data.make_sample_ai_questions --remove   # xóa câu mẫu (kèm phản ánh của chúng)
"""

import argparse
import sys

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.review_question import ReviewQuestion
from app.models.review_question_meta import ReviewQuestionMeta
from app.models.skill import Skills

MARK = {"sample": "g3f"}


def _mcq(chunk, level, content, options, correct, explanation):
    return {
        "chunk": chunk,
        "type": "mcq",
        "level": level,
        "content": content,
        "options": options,
        "correct_index": correct,
        "explanation": explanation,
    }


SAMPLES = [
    _mcq(
        0,
        "recognize",
        "Which command lists ALL containers, including stopped ones?",
        ["docker run -a", "docker ps", "docker ps -a", "docker list"],
        2,
        "`docker ps` shows only running containers; `-a` adds stopped ones.",
    ),
    _mcq(
        1,
        "recognize",
        "Which Dockerfile instruction sets the base image?",
        ["FROM", "BASE", "IMAGE", "RUN"],
        0,
        "Every Dockerfile starts from a base image declared with FROM.",
    ),
    _mcq(
        1,
        "understand",
        "Every instruction in a Dockerfile creates a new image layer. True or false?",
        ["True", "False", "Only in multi-stage builds", "Only for COPY"],
        0,
        "CỐ Ý SAI để test: thực ra chỉ RUN / COPY / ADD tạo layer (đáp án đúng phải là False).",
    ),
    _mcq(
        2,
        "understand",
        "What happens to data written inside a container when the container is removed " "(no volume mounted)?",
        ["It is kept in the image", "It is lost", "It moves to a volume automatically", "It is pushed to the registry"],
        1,
        "The writable container layer is deleted with the container; use volumes to persist data.",
    ),
    {
        "chunk": 0,
        "type": "essay",
        "level": "easy",
        "content": "Explain the difference between a Docker image and a Docker container.",
        "rubric": [
            {
                "text": "An image is a read-only template / blueprint",
                "max_points": 5,
                "main_keywords": ["read-only", "template"],
                "sub_keywords": ["blueprint", "image"],
            },
            {
                "text": "A container is a running instance of an image",
                "max_points": 5,
                "main_keywords": ["instance", "running"],
                "sub_keywords": ["container"],
            },
        ],
        "explanation": "Image = template; container = running instance with its own writable layer.",
    },
    {
        "chunk": 2,
        "type": "essay",
        "level": "easy",
        "content": "Why should you use a volume for a database running in a container?",
        "rubric": [
            {
                "text": "Container data is lost when the container is removed",
                "max_points": 5,
                "main_keywords": ["lost", "removed"],
                "sub_keywords": ["delete"],
            },
            {
                "text": "A volume keeps data outside the container lifecycle",
                "max_points": 5,
                "main_keywords": ["volume", "persist"],
                "sub_keywords": ["outside", "keep"],
            },
        ],
        "explanation": "Volumes persist data independently of the container.",
    },
]


def _docker(db) -> int | None:
    """Id kỹ năng Docker có đoạn tài liệu (G3a đã viết cho #192)."""
    return db.scalar(
        select(Skills.skill_id)
        .join(KnowledgeChunk, KnowledgeChunk.skill_id == Skills.skill_id)
        .where(func.lower(Skills.skill) == "docker")
        .order_by(Skills.skill_id)
        .limit(1)
    )


def _samples(db) -> list[ReviewQuestionMeta]:
    metas = db.scalars(select(ReviewQuestionMeta).where(ReviewQuestionMeta.review_status == "auto_approved"))
    return [m for m in metas if m.ai_check == MARK]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Câu mẫu AI soạn để test trang mentor (G3f)")
    parser.add_argument("--remove", action="store_true", help="xóa các câu mẫu")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    from app.services import review_bank_service as bank

    with SessionLocal() as db:
        existing = _samples(db)
        if args.remove:
            for meta in existing:
                db.delete(db.get(ReviewQuestion, meta.question_id))  # CASCADE: meta + phản ánh
            db.commit()
            print(f"Đã xóa {len(existing)} câu mẫu.")
            return 0
        if existing:
            print(f"Đã có {len(existing)} câu mẫu — bỏ qua. Xóa: --remove")
            return 0
        skill_id = _docker(db)
        if skill_id is None:
            print("Không có kỹ năng Docker nào có đoạn tài liệu (chạy G3a trước).")
            return 1
        chunks = db.scalars(
            select(KnowledgeChunk.chunk_id).where(KnowledgeChunk.skill_id == skill_id).order_by(KnowledgeChunk.chunk_id)
        ).all()
        for sample in SAMPLES:
            data = {k: v for k, v in sample.items() if k != "chunk"}
            data |= {"skill_id": skill_id, "chunk_id": chunks[min(sample["chunk"], len(chunks) - 1)]}
            question = bank.create_question(db, data, source="ai", review_status="auto_approved")
            question.is_active = True  # auto_approved: dùng ngay (D1)
            db.get(ReviewQuestionMeta, question.question_id).ai_check = MARK
        db.commit()
        print(f"Đã tạo {len(SAMPLES)} câu mẫu AI soạn cho Docker #{skill_id} (câu 3 cố ý sai).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
