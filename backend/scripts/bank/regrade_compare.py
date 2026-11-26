"""So điểm bộ chấm từ khóa TRƯỚC / SAU khi sửa bộ chấm hoặc barem — dùng khi đổi text_pipeline / keyword_grader.

    python -m scripts.bank.regrade_compare snapshot            → data/bank_runs/grade_snapshot_<giờ>.json
    (sửa code)
    python -m scripts.bank.regrade_compare snapshot
    python -m scripts.bank.regrade_compare compare <cũ.json> <mới.json>

Bộ bài: bài mẫu mọi câu tự luận trong DB + mọi bài học viên đã nộp + bài mẫu các file đề data/review/**.json.
So TỪNG Ý; tách riêng bài GIẢM điểm (sửa bộ chấm để nhận bài đúng thì không được có bài giảm — có là lỗi).
Ảnh chụp chứa bài làm của học viên → nằm trong data/bank_runs/ (.gitignore).
"""

import argparse
import glob
import json
from pathlib import Path

from scripts.bank.common import BACKEND, quiet, run_file, write_json


def snapshot() -> dict:
    from app.ai.review.keyword_grading import grade_essay
    from app.ai.review.question_gate import model_answer
    from app.core.database import SessionLocal
    from app.models.review_attempt import ReviewAnswer
    from app.models.review_question import ReviewQuestion

    out = {}

    def add(key, code, rubric, content, text):
        r = grade_essay(rubric, text, content)
        out[key] = {"code": code, "items": [x["result"] for x in r], "score": sum(x["points"] for x in r), "text": text}

    with SessionLocal() as db:
        qs = {q.question_id: q for q in db.query(ReviewQuestion).filter(ReviewQuestion.type == "essay")}
        for q in qs.values():
            ans = model_answer({"explanation": q.explanation})
            if ans and q.rubric:
                add(f"model:{q.question_id}", q.code, q.rubric, q.content, ans)
        for a in db.query(ReviewAnswer).filter(ReviewAnswer.text_answer.isnot(None)):
            q = qs.get(a.question_id)
            if q and q.rubric and (a.text_answer or "").strip():
                add(f"answer:{a.attempt_id}:{a.position}", q.code or q.question_id, q.rubric, q.content, a.text_answer)
    for f in sorted(glob.glob(str(BACKEND / "data" / "review" / "**" / "*.json"), recursive=True)):
        try:
            bank = json.loads(Path(f).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for q in bank.get("questions", []) if isinstance(bank, dict) else []:
            if q.get("type") == "essay" and q.get("rubric") and model_answer(q):
                add(
                    f"file:{Path(f).name}:{q.get('code')}",
                    q.get("code"),
                    q["rubric"],
                    q.get("content"),
                    model_answer(q),
                )
    return out


def compare(old: dict, new: dict) -> dict:
    diff = [k for k in old if k in new and old[k]["items"] != new[k]["items"]]
    return {
        "total": len(old),
        "down": [k for k in diff if new[k]["score"] < old[k]["score"]],
        "up": [k for k in diff if new[k]["score"] > old[k]["score"]],
        "same_total": [k for k in diff if new[k]["score"] == old[k]["score"]],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="So điểm bộ chấm từ khóa trước / sau khi sửa")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("snapshot")
    c = sub.add_parser("compare")
    c.add_argument("old", type=Path)
    c.add_argument("new", type=Path)
    args = parser.parse_args()
    quiet()
    if args.cmd == "snapshot":
        data = snapshot()
        out = run_file("grade_snapshot")
        write_json(out, data)
        print(len(data), "bài đã chấm →", out)
        return 0
    old, new = (json.loads(p.read_text(encoding="utf-8")) for p in (args.old, args.new))
    r = compare(old, new)
    print(f"{r['total']} bài; tăng {len(r['up'])}, GIẢM {len(r['down'])}, đổi ý giữ tổng {len(r['same_total'])}")
    for title, keys in (
        ("GIẢM ĐIỂM (không được có)", r["down"]),
        ("Tăng điểm", r["up"]),
        ("Đổi ý, tổng giữ", r["same_total"]),
    ):
        if keys:
            print(f"== {title}: {len(keys)}")
            for k in keys:
                print(
                    f"- {k} ({old[k]['code']}): {old[k]['score']} -> {new[k]['score']}  {old[k]['items']} -> "
                    f"{new[k]['items']}"
                )
                print("    ", " ".join(old[k]["text"][:300].split()))
    return 1 if r["down"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
