"""Hiệu chỉnh cổng G3c trên câu SOẠN TAY đã duyệt (module 09 · Tuấn · 25/11/2026 — bước 5 phase 05 của thầy).

Chạy các phép kiểm của cổng (KHÔNG loại câu nào, KHÔNG ghi DB) trên mọi câu đang bật, đã duyệt (khóa demo 312 / 743 /
1855…) rồi xuất CSV + bảng tóm tắt để chốt ngưỡng trong config.py. Giải mù gom theo kỹ năng, tối đa 12 câu / lần gọi.
Câu soạn tay bị giải mù ra đáp án khác → Tuấn xem lại (có thể ngân hàng sai thật). Cần AI_MODE=real + khóa Gemini.

    cd backend
    python -m app.core.seed_data.calibrate_question_gate --out data/cache/gate_calibration
"""

import argparse
import csv
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal

BATCH = 12


def _pct(values: list[float], p: float) -> float | None:
    values = sorted(v for v in values if v is not None)
    if not values:
        return None
    k = (len(values) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(values) - 1)
    return round(values[lo] + (values[hi] - values[lo]) * (k - lo), 3)


def _solve_with_waits(solve, skill, items):
    from app.ai.review.base import AIUnavailableError

    for wait in (20, 40, 60, None):
        try:
            return solve(skill, items)
        except AIUnavailableError as err:
            if wait is None:
                print(f"  {skill}: bỏ qua giải mù ({err})")
                return None
            print(f"  {skill}: {err} — chờ {wait} giây")
            time.sleep(wait)
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Hiệu chỉnh cổng G3c trên câu soạn tay")
    parser.add_argument("--out", default="data/cache/gate_calibration", help="thư mục xuất CSV + tóm tắt")
    parser.add_argument("--no-solve", action="store_true", help="không gọi Gemini (chỉ L1, trùng, bám nguồn, bài giả)")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    from app.ai.review.question_gate import (
        GateContext,
        _cosine,
        blind_solve,
        fake_scores,
        length_hint,
        length_ratio,
        model_answer,
    )
    from app.ai.review.real_ai import RealAI, review_llm
    from app.models.knowledge_chunk import KnowledgeChunk
    from app.models.review_question import ReviewQuestion
    from app.models.review_question_meta import ReviewQuestionMeta
    from app.models.skill import Skills
    from app.services.review_rag_service import embed_query

    solve = None
    if not args.no_solve:
        key, model = review_llm()
        if settings.AI_MODE != "real" or not key or not model:
            print("Cần AI_MODE=real + khóa Gemini (hoặc chạy --no-solve).")
            return 1
        solve = RealAI().solve_mcqs

    rows: list[dict] = []
    with SessionLocal() as db:
        questions = db.scalars(
            select(ReviewQuestion)
            .outerjoin(ReviewQuestionMeta, ReviewQuestionMeta.question_id == ReviewQuestion.question_id)
            .where(ReviewQuestion.is_active.is_(True))
            .where((ReviewQuestionMeta.review_status == "approved") | ReviewQuestionMeta.question_id.is_(None))
            .order_by(ReviewQuestion.skill_id, ReviewQuestion.question_id)
        ).all()
        chunks = {c.chunk_id: c.content for c in db.scalars(select(KnowledgeChunk))}
        names = dict(db.execute(select(Skills.skill_id, Skills.skill)).all())
        by_skill: dict[int, list] = defaultdict(list)
        for q in questions:
            by_skill[q.skill_id].append(q)
        print(f"{len(questions)} câu soạn tay, {len(by_skill)} kỹ năng")

        ctx = GateContext(skill="", chunks=chunks, embed=embed_query, rng=random.Random(2026))
        for skill_id, items in by_skill.items():
            skill = names.get(skill_id, str(skill_id))
            ctx.skill = skill
            dicts = [{"question_id": q.question_id, "code": q.code, "type": q.type, "level": q.level,
                      "content": q.content, "options": q.options, "correct_index": q.correct_index,
                      "rubric": q.rubric, "explanation": q.explanation, "chunk_id": q.chunk_id} for q in items]  # fmt: skip
            mcqs = [d for d in dicts if d["type"] == "mcq"]
            solved: dict[int, int | None] = {}
            if solve is not None:
                for start in range(0, len(mcqs), BATCH):
                    part = mcqs[start : start + BATCH]
                    ctx.solve = lambda s, it: _solve_with_waits(solve, s, it)
                    for d, index in zip(part, blind_solve(part, ctx), strict=True):
                        solved[d["question_id"]] = index
            vectors = {d["question_id"]: ctx.vector(d["content"]) for d in dicts}
            essays = [model_answer(d) for d in dicts if d["type"] == "essay"]
            for d in dicts:
                vec = vectors[d["question_id"]]
                same_type = {x["question_id"] for x in dicts if x["type"] == d["type"]}
                others = [(qid, _cosine(vec, v)) for qid, v in vectors.items()
                          if qid != d["question_id"] and qid in same_type and v]  # fmt: skip
                sim_id, sim = max(others, key=lambda x: x[1], default=(None, None))
                chunk = chunks.get(d["chunk_id"])
                if d["type"] == "mcq":
                    answer = d["options"][d["correct_index"]]
                else:
                    answer = " ".join(i.get("text", "") for i in d["rubric"] or [])
                grounding = None
                if chunk and vec:
                    grounding = round(_cosine(ctx.vector(f"{d['content']} {answer}"), ctx.vector(chunk)), 3)
                row = {"question_id": d["question_id"], "code": d["code"], "skill": skill, "type": d["type"],
                       "level": d["level"], "content": d["content"][:120],
                       "max_similarity": round(sim, 3) if sim is not None else None, "similar_question_id": sim_id,
                       "grounding": grounding}  # fmt: skip
                if d["type"] == "mcq":
                    index = solved.get(d["question_id"])
                    row |= {"length_ratio": length_ratio(d), "length_hint": length_hint(d), "correct_index": d["correct_index"], "solver_index": index,
                            "solver_match": None if index is None else index == d["correct_index"]}  # fmt: skip
                else:
                    fake = fake_scores(d, [e for e in essays if e != model_answer(d)])
                    row |= {"fake_model": fake["model"], "fake_copy": fake["copy"], "fake_other": fake.get("other")}
                rows.append(row)
            print(f"- {skill}: {len(dicts)} câu")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    fields = sorted({k for r in rows for k in r}, key=lambda k: list(rows[0]).index(k) if k in rows[0] else 99)
    with (out / "gate_calibration.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    mcq = [r for r in rows if r["type"] == "mcq"]
    essay = [r for r in rows if r["type"] == "essay"]
    solved_rows = [r for r in mcq if r.get("solver_match") is not None]
    mismatch = [r for r in solved_rows if not r["solver_match"]]
    sims = [r["max_similarity"] for r in rows]
    ground = [r["grounding"] for r in rows]
    ratios = [r["length_ratio"] for r in mcq]
    models = [r["fake_model"] for r in essay]
    copies = [r["fake_copy"] for r in essay]
    other = [r["fake_other"] for r in essay]
    rate = 100 * len(mismatch) / max(len(solved_rows), 1)
    lines = [
        "# Hiệu chỉnh cổng G3c trên câu soạn tay\n",
        f"- Câu: {len(rows)} ({len(mcq)} trắc nghiệm, {len(essay)} tự luận)",
        f"- Giải mù: {len(solved_rows)} câu có kết quả, **lệch {len(mismatch)} câu ({rate:.1f}%)** — mục tiêu ≤ 5%",
        (
            f"- L1: tỉ lệ p50 {_pct(ratios, .5)}, p95 {_pct(ratios, .95)}; bị loại (> {settings.REVIEW_GATE_LENGTH_RATIO}"
            f" và dài hơn ≥ {settings.REVIEW_GATE_LENGTH_MIN_DIFF} ký tự): {sum(r['length_hint'] for r in mcq)} câu"
        ),
        (
            f"- Gần trùng (cùng loại, cùng kỹ năng): p50 {_pct(sims, .5)}, p95 {_pct(sims, .95)}, max {_pct(sims, 1)};"
            f" ≥ {settings.REVIEW_GATE_DUP_MAX}: {sum((s or 0) >= settings.REVIEW_GATE_DUP_MAX for s in sims)} câu"
        ),
        f"- Bám nguồn: p5 {_pct(ground, .05)}, p50 {_pct(ground, .5)}",
        (
            f"- Bài mẫu: p5 {_pct(models, .05)} (< {settings.REVIEW_GATE_MODEL_MIN}:"
            f" {sum(m < settings.REVIEW_GATE_MODEL_MIN for m in models)} câu)"
        ),
        (
            f"- Chép đề: max {_pct(copies, 1)} (> {settings.REVIEW_GATE_COPY_MAX}:"
            f" {sum(c > settings.REVIEW_GATE_COPY_MAX for c in copies)} câu)"
        ),
        (
            f"- Bài câu khác: max {_pct(other, 1)} (> {settings.REVIEW_GATE_OTHER_MAX}:"
            f" {sum((o or 0) > settings.REVIEW_GATE_OTHER_MAX for o in other)} câu)"
        ),
        "\n## Câu soạn tay bị giải mù ra đáp án khác (cần xem lại)\n",
    ]
    for r in mismatch:
        lines.append(f"- #{r['question_id']} `{r['code']}` ({r['skill']}): {r['content']} — ghi"
                     f" {'ABCD'[r['correct_index']]}, solver chọn {'ABCD'[r['solver_index']]}")  # fmt: skip
    (out / "gate_calibration.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:10]))
    print(f"Đã xuất → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
