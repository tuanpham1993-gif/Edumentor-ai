"""Đo Gemini và bộ chấm từ khóa trên bài thử A/B của một khóa (GEMINI_PROBES) — KHÔNG tạo lượt làm bài.

    python -m scripts.bank.probe_gemini 494                         (mọi câu tự luận, tối đa 40 lần gọi)
    python -m scripts.bank.probe_gemini 494 MSG-TL-02 MSG-TL-03     (chỉ vài câu)
    python -m scripts.bank.probe_gemini 494 --max-calls 60

Gọi RealAI.grade_essay_detailed như server (prompt + model theo cấu hình .env / biến môi trường; key KHÔNG nhận qua
tham số). Chuẩn đạt (Tuấn chốt 26/11): ý "any one of" lệch ≤ 1 điểm giữa Gemini và từ khóa; ý "both needed" ở bản A
(nêu thiếu) thì Gemini phải chấm không đạt.
Kết quả: data/bank_runs/probe_gemini_<id>_<giờ>.json — ghi phiên bản prompt + model để đối chiếu về sau.
"""

import argparse
import time

from scripts.bank.common import bank_path, load_bank, load_course, quiet, run_file, write_json

RETRY_WAITS = (20, 40, 60)  # giây — 429 (hết hạn mức tạm thời) / 503 (quá tải), như đo tay 26/11
MAX_GAP = 1.0


def judge(row: dict) -> str:
    if row["both"] and row["variant"] == "A":
        return "OK" if row["gemini"] == 0 else "LỆCH"
    return "OK" if abs(row["gemini"] - row["keyword"]) <= MAX_GAP else "LỆCH"


def grade_with_retry(ai, question: dict, answer: str, sleep=time.sleep):
    from app.ai.review.base import AIUnavailableError

    for wait in (*RETRY_WAITS, None):
        try:
            return ai.grade_essay_detailed(question, answer)
        except AIUnavailableError as err:
            if wait is None:
                raise
            print(f"  Gemini chưa dùng được ({str(err)[:70]}) — chờ {wait} s rồi gọi lại")
            sleep(wait)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Đo Gemini vs từ khóa trên bài thử A/B (không tạo lượt làm bài)")
    parser.add_argument("course_id", type=int)
    parser.add_argument("codes", nargs="*", help="mã câu tự luận; bỏ trống = mọi câu")
    parser.add_argument("--max-calls", type=int, default=40, help="giới hạn số bài gửi Gemini (mặc định 40)")
    args = parser.parse_args()
    quiet()

    from app.ai.review import get_review_ai
    from app.ai.review.keyword_grading import grade_essay
    from app.ai.review.real_ai import RealAI, review_llm
    from app.core.config import settings

    course = load_course(args.course_id)
    qs = {q["code"]: q for q in load_bank(bank_path(args.course_id))["questions"]}
    codes = args.codes or list(course.GEMINI_PROBES)
    planned = 2 * len(codes)
    if planned > args.max_calls:
        print(f"Cần {planned} lần gọi, vượt --max-calls {args.max_calls} — chọn bớt câu hoặc tăng giới hạn.")
        return 2
    ai = get_review_ai()
    if not isinstance(ai, RealAI):
        print(f"AI_MODE={settings.AI_MODE}: không phải Gemini thật — dừng.")
        return 2
    if settings.REVIEW_GRADING_RAG or settings.REVIEW_GRADING_FEWSHOT:
        print("Lưu ý: server đang bật RAG / few-shot; công cụ này gửi đề + barem + bài mẫu (không kèm đoạn tri thức).")
    print(f"Ước tính {planned} lần gọi (tối đa {args.max_calls}).")

    rows, calls, versions = [], 0, set()
    for code in codes:
        q = qs[code]
        question = {"content": q["content"], "rubric": q["rubric"], "explanation": q["explanation"]}
        for label, answer in zip("AB", course.GEMINI_PROBES[code], strict=True):
            if calls >= args.max_calls:
                print("Đã chạm --max-calls — dừng sớm.")
                break
            g = grade_with_retry(ai, question, answer)
            calls += g.attempts
            versions.add(g.prompt_version)
            kw = grade_essay(q["rubric"], answer, q["content"])
            for i, (item, gi, ki) in enumerate(zip(q["rubric"], g.items, kw, strict=True), start=1):
                rows.append(
                    {
                        "code": code,
                        "variant": label,
                        "item": i,
                        "both": "both needed" in item["text"],
                        "max": item["max_points"],
                        "gemini": gi["points"],
                        "keyword": ki["points"],
                        "reason": gi.get("reason"),
                    }
                )
    for r in rows:
        r["verdict"] = judge(r)
    bad = [r for r in rows if r["verdict"] != "OK"]
    out = run_file(f"probe_gemini_{args.course_id}")
    write_json(
        out,
        {
            "course_id": args.course_id,
            "model": review_llm()[1],  # chỉ tên model — KHÔNG ghi key
            "prompt_versions": sorted(v for v in versions if v),
            "rag": settings.REVIEW_GRADING_RAG,
            "fewshot": settings.REVIEW_GRADING_FEWSHOT,
            "max_calls": args.max_calls,
            "calls": calls,
            "rows": rows,
        },
    )
    print(f"{len(rows)} ý, {calls} lần gọi; lệch: {len(bad)} → {out}")
    for r in rows:
        if r["verdict"] != "OK" or (r["both"] and r["variant"] == "A"):
            print(
                f"{r['verdict']:4} {r['code']} {r['variant']} ý {r['item']}{' [both]' if r['both'] else ''}: "
                f"Gemini {r['gemini']} / từ khóa {r['keyword']} — {r['reason']}"
            )
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
