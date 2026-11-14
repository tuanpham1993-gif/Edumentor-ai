"""Đo độ chính xác chấm tự luận so với bộ bài chuẩn (module 09 · Tuấn · B5, 14/11/2026).

Chỉ số theo docs/Review-AI-Grading.md mục 3. Precision / Recall / F1 từng nhãn tính như bài Session02/demo2.py
(TP / FP / FN) — mỗi nhãn full / partial / none coi là một lớp.

Chạy (trong thư mục backend):
    # 1. Chấm một lần → data/ai-grading/private/results/<run_id>.csv (mỗi dòng một ý: kết quả, điểm, độ trễ, lỗi)
    python -m scripts.eval_grading run --method keyword --answers data/ai-grading/private/answers.csv --split dev
    # 2. Tính chỉ số của một lần chạy so với gold.csv (in bảng + lưu <run_id>.metrics.json)
    python -m scripts.eval_grading report --gold data/ai-grading/private/gold.csv \
        --run data/ai-grading/private/results/<run_id>.csv
    # 3. So hai lần chạy (vd từ khóa vs Model A, A vs B): paired bootstrap 1.000 lần, khoảng tin cậy 95%;
    #    hai lần chạy CÙNG cách chấm → thêm độ ổn định (tỉ lệ ý ra cùng kết quả)
    python -m scripts.eval_grading compare --gold .../gold.csv --run .../A.csv --run .../B.csv

Chống rò rỉ: chỉnh prompt chỉ trên --split dev; test chạy MỘT lần cho bản cuối (B10).
Thêm cách chấm mới (Model A / B — B7, B9): đăng ký hàm vào METHODS, cùng chữ ký với `_keyword`.
"""

import argparse
import json
import math
import random
import sys
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from sklearn.metrics import cohen_kappa_score

from app.ai.review import keyword_grading
from scripts.gold_sheets import (
    LABELS,
    GoldError,
    load_split,
    points_of,
    read_csv,
    round_score,
    write_csv,
)

RESULTS_DIR = Path(__file__).resolve().parents[1] / "data" / "ai-grading" / "private" / "results"
RUN_FIELDS = [
    "run_id", "method", "model", "prompt_version", "answer_id", "question_code", "split", "item_no", "max_points",
    "result", "points", "latency_ms", "error",
]  # fmt: skip
SEVERE_HUMAN_MAX = 4  # "bài sai bị chấm cao": người chấm ≤ 4 …
SEVERE_AI_MIN = 7  # … nhưng AI ≥ 7 (mục tiêu: 0 bài)


# ─────────────── cách chấm ───────────────


def _keyword(question: dict, answer_text: str) -> list[str]:
    """Bộ chấm từ khóa (B3) — tự chọn tiếng Anh / tiếng Việt. Trả nhãn từng ý theo thứ tự barem."""
    return [r["result"] for r in keyword_grading.grade_essay(question["rubric"], answer_text, question["content"])]


# tên → (hàm chấm, model, prompt_version)
METHODS: dict[str, tuple[Callable[[dict, str], list[str]], str, str]] = {
    "keyword": (_keyword, "keyword_grader_en", "-"),
}


def run(answers: list[dict], split: dict, method: str, *, run_id: str, which: str = "dev") -> list[dict]:
    """Chấm mọi bài thuộc `which` (dev / test / all). Lỗi một bài → ghi `error`, các ý của bài đó để trống."""
    grade, model, prompt_version = METHODS[method]
    if method == "keyword":  # nạp dữ liệu NLTK trước (lần đầu ~ vài giây) để không tính vào độ trễ bài đầu tiên
        _keyword(next(iter(split["questions"].values())), "warm up")
    rows = []
    for a in answers:
        if which != "all" and a["split"] != which:
            continue
        q = split["questions"][a["question_code"]]
        start = time.perf_counter()
        try:
            labels, error = grade(q, a["answer_text"]), ""
            if len(labels) != len(q["rubric"]) or any(lb not in LABELS for lb in labels):
                labels, error = [""] * len(q["rubric"]), f"kết quả sai dạng: {labels}"
        except Exception as e:  # noqa: BLE001 — một bài lỗi không làm dừng cả lần chạy; lỗi được ghi lại
            labels, error = [""] * len(q["rubric"]), f"{type(e).__name__}: {e}"
        latency = round((time.perf_counter() - start) * 1000)
        for no, (item, label) in enumerate(zip(q["rubric"], labels, strict=True), start=1):
            rows.append(
                {
                    "run_id": run_id, "method": method, "model": model, "prompt_version": prompt_version,
                    "answer_id": a["answer_id"], "question_code": a["question_code"], "split": a["split"],
                    "item_no": no, "max_points": item["max_points"], "result": label,
                    "points": points_of(label, float(item["max_points"])) if label else "",
                    "latency_ms": latency, "error": error,
                }
            )  # fmt: skip
    return rows


# ─────────────── ghép gold với một lần chạy ───────────────


def pair(gold: list[dict], run_rows: list[dict], which: str = "all") -> list[dict]:
    """Mỗi ý: nhãn người (gold) + nhãn AI, chỉ lấy bài có trong lần chạy.
    Ý AI lỗi (result rỗng) → tính là `none` (học viên thực tế nhận 0 điểm nếu không có dự phòng), đánh dấu `failed`.
    Lỗi (không tính gì): ý gold chưa phân xử; bài có trong lần chạy nhưng thiếu ý; max_points lệch gold
    (barem đã sửa giữa lúc chấm người và lúc chạy → so sánh không còn đúng)."""
    predicted = {(r["answer_id"], int(r["item_no"])): r for r in run_rows}
    run_answers = {r["answer_id"] for r in run_rows}
    errors, out = [], []
    for g in gold:
        key = (g["answer_id"], int(g["item_no"]))
        if g["answer_id"] not in run_answers or (which != "all" and g["split"] != which):
            continue
        if key not in predicted:
            errors.append(f"lần chạy thiếu {key[0]} ý {key[1]} (tổng điểm bài sẽ sai)")
            continue
        if g["label"] not in LABELS:
            errors.append(f"gold {key[0]} ý {key[1]}: chưa có nhãn cuối (chạy merge --adjudicated)")
            continue
        r = predicted[key]
        if float(r["max_points"]) != float(g["max_points"]):
            errors.append(f"{key[0]} ý {key[1]}: max_points lần chạy {r['max_points']} ≠ gold {g['max_points']}")
            continue
        out.append(
            {
                "answer_id": key[0], "item_no": key[1], "question_code": g["question_code"],
                "max_points": float(g["max_points"]), "human": g["label"], "ai": r["result"] or "none",
                "failed": not r["result"], "latency_ms": float(r["latency_ms"] or 0),
            }
        )  # fmt: skip
    if errors:
        raise GoldError(errors)
    if not out:
        raise GoldError(["Không có ý nào chung giữa gold và lần chạy (sai file / sai split?)"])
    return out


def missing_answers(gold: list[dict], run_rows: list[dict]) -> list[str]:
    """Bài gold thuộc các split mà lần chạy có chấm, nhưng lần chạy không có (vd chạy bị dừng giữa chừng)
    → báo cáo chỉ trên phần đã chấm; CLI in cảnh báo để không tưởng là đủ bộ."""
    splits = {r["split"] for r in run_rows}
    done = {r["answer_id"] for r in run_rows}
    return sorted({g["answer_id"] for g in gold if g["split"] in splits and g["answer_id"] not in done})


def totals(pairs: list[dict]) -> dict[str, tuple[float, float]]:
    """Tổng điểm (thang 10 — barem mỗi câu tổng 10) theo bài: (người, AI)."""
    out: dict[str, list[float]] = {}
    for p in pairs:
        t = out.setdefault(p["answer_id"], [0.0, 0.0])
        t[0] += points_of(p["human"], p["max_points"])
        t[1] += points_of(p["ai"], p["max_points"])
    return {k: (v[0], v[1]) for k, v in out.items()}


# ─────────────── chỉ số ───────────────


def label_prf(pairs: list[dict]) -> dict[str, dict]:
    """Precision / Recall / F1 từng nhãn — cùng công thức demo2.py (TP, FP, FN)."""
    out = {}
    for label in LABELS:
        tp = sum(p["human"] == label and p["ai"] == label for p in pairs)
        fp = sum(p["human"] != label and p["ai"] == label for p in pairs)
        fn = sum(p["human"] == label and p["ai"] != label for p in pairs)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        out[label] = {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}
    return out


def confusion(pairs: list[dict]) -> dict[str, dict[str, int]]:
    """confusion[người][AI] = số ý."""
    return {h: {a: sum(p["human"] == h and p["ai"] == a for p in pairs) for a in LABELS} for h in LABELS}


def _qwk(human: list[float], ai: list[float]) -> float:
    h, a = [round_score(x) for x in human], [round_score(x) for x in ai]
    if len(set(h) | set(a)) < 2:
        return 1.0 if h == a else 0.0
    return float(cohen_kappa_score(h, a, weights="quadratic"))


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    return s[min(len(s) - 1, math.ceil(q * len(s)) - 1)]


def metrics(pairs: list[dict]) -> dict:
    t = totals(pairs)
    human = [v[0] for v in t.values()]
    ai = [v[1] for v in t.values()]
    diffs = [b - a for a, b in zip(human, ai, strict=True)]
    latency_by_answer = {p["answer_id"]: p["latency_ms"] for p in pairs}  # độ trễ đo theo bài
    prf = label_prf(pairs)
    return {
        "answers": len(t),
        "items": len(pairs),
        "mae": sum(abs(d) for d in diffs) / len(diffs),
        "rmse": math.sqrt(sum(d * d for d in diffs) / len(diffs)),
        "qwk": _qwk(human, ai),
        "item_agreement": sum(p["human"] == p["ai"] for p in pairs) / len(pairs),
        "within_1": sum(abs(d) <= 1 for d in diffs) / len(diffs),
        "severe_overgrade": sum(h <= SEVERE_HUMAN_MAX and a >= SEVERE_AI_MIN for h, a in zip(human, ai, strict=True)),
        "mean_bias": sum(diffs) / len(diffs),  # > 0: AI chấm rộng tay hơn người
        "macro_f1": sum(v["f1"] for v in prf.values()) / len(prf),
        "labels": prf,
        "confusion": confusion(pairs),
        "failed_items": sum(p["failed"] for p in pairs),
        "latency_p95_ms": _percentile(list(latency_by_answer.values()), 0.95),
    }


def stability(run_a: list[dict], run_b: list[dict]) -> float:
    """Hai lần chạy cùng cách chấm: tỉ lệ ý (có ở cả hai) ra cùng kết quả (mục tiêu ≥ 90%)."""
    a = {(r["answer_id"], int(r["item_no"])): r["result"] for r in run_a}
    b = {(r["answer_id"], int(r["item_no"])): r["result"] for r in run_b}
    common = a.keys() & b.keys()
    return sum(a[k] == b[k] for k in common) / len(common) if common else 0.0


def paired_bootstrap(pairs_a: list[dict], pairs_b: list[dict], *, n: int = 1000, seed: int = 0) -> dict:
    """Lấy mẫu lại THEO BÀI (có hoàn lại), cùng một mẫu cho A và B → khoảng tin cậy 95% của (B − A).
    MAE: B − A < 0 là B tốt hơn; khớp từng ý: B − A > 0 là B tốt hơn. Chỉ kết luận khi khoảng không chứa 0."""
    ta, tb = totals(pairs_a), totals(pairs_b)
    ids = sorted(ta.keys() & tb.keys())
    if not ids:
        raise GoldError(["Hai lần chạy không có bài chung"])
    items_a = _items_by_answer(pairs_a)
    items_b = _items_by_answer(pairs_b)
    rng = random.Random(seed)
    mae_d, agree_d = [], []
    for _ in range(n):
        sample = [rng.choice(ids) for _ in ids]
        mae_d.append(_mae(tb, sample) - _mae(ta, sample))
        agree_d.append(_agree(items_b, sample) - _agree(items_a, sample))
    return {
        "answers": len(ids),
        "n": n,
        "mae_diff": _ci(_mae(tb, ids) - _mae(ta, ids), mae_d),
        "item_agreement_diff": _ci(_agree(items_b, ids) - _agree(items_a, ids), agree_d),
    }


def _items_by_answer(pairs: list[dict]) -> dict[str, tuple[int, int]]:
    out: dict[str, list[int]] = {}
    for p in pairs:
        c = out.setdefault(p["answer_id"], [0, 0])
        c[0] += p["human"] == p["ai"]
        c[1] += 1
    return {k: (v[0], v[1]) for k, v in out.items()}


def _mae(t: dict[str, tuple[float, float]], ids: list[str]) -> float:
    return sum(abs(t[i][1] - t[i][0]) for i in ids) / len(ids)


def _agree(items: dict[str, tuple[int, int]], ids: list[str]) -> float:
    return sum(items[i][0] for i in ids) / sum(items[i][1] for i in ids)


def _ci(point: float, samples: list[float]) -> dict:
    s = sorted(samples)
    lo, hi = s[int(0.025 * len(s))], s[min(len(s) - 1, int(0.975 * len(s)))]
    return {"diff": point, "ci_low": lo, "ci_high": hi, "significant": lo > 0 or hi < 0}


# ─────────────── in báo cáo ───────────────

TARGETS = {  # mục 3 — mục tiêu ban đầu (cần kiểm chứng)
    "mae": ("≤", 1.0), "rmse": ("≤", 1.5), "qwk": ("≥", 0.70), "item_agreement": ("≥", 0.80),
    "within_1": ("≥", 0.85), "severe_overgrade": ("≤", 0),
}  # fmt: skip


def format_report(m: dict, title: str) -> str:
    pct = {"item_agreement", "within_1"}
    lines = [f"== {title} — {m['answers']} bài / {m['items']} ý =="]
    for key, (op, target) in TARGETS.items():
        v = m[key]
        ok = v <= target if op == "≤" else v >= target
        shown = f"{v:.1%}" if key in pct else (f"{v}" if isinstance(v, int) else f"{v:.3f}")
        goal = f"{target:.0%}" if key in pct else f"{target}"
        lines.append(f"  {key:<17} {shown:>8}   mục tiêu {op} {goal:<5} {'✓' if ok else '✗'}")
    lines.append(f"  {'mean_bias':<17} {m['mean_bias']:>+8.3f}   (> 0: AI chấm rộng tay hơn người)")
    lines.append(f"  {'macro_f1':<17} {m['macro_f1']:>8.3f}")
    lines.append(f"  {'latency_p95_ms':<17} {m['latency_p95_ms']:>8.0f}   ý lỗi: {m['failed_items']}")
    lines.append("  nhãn      precision  recall   f1     (tp / fp / fn)")
    for label, v in m["labels"].items():
        lines.append(
            f"  {label:<9} {v['precision']:>9.3f} {v['recall']:>7.3f} {v['f1']:>6.3f}   ({v['tp']} / {v['fp']} / {v['fn']})"
        )
    lines.append("  ma trận nhầm (dòng = người, cột = AI): " + " · ".join(LABELS))
    for h, row in m["confusion"].items():
        lines.append(f"  {h:<9} " + " ".join(f"{row[a]:>6}" for a in LABELS))
    return "\n".join(lines)


# ─────────────── CLI ───────────────


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252 → lỗi khi in "✓", tiếng Việt
    parser = argparse.ArgumentParser(description="Đo độ chính xác chấm tự luận (B5): run → report → compare")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run", help="chấm bộ bài bằng một cách chấm → results/<run_id>.csv")
    p.add_argument("--method", choices=sorted(METHODS), required=True)
    p.add_argument("--answers", required=True)
    p.add_argument("--split", choices=["dev", "test", "all"], default="dev")
    p.add_argument("--run-id")
    p.add_argument("--out-dir", default=str(RESULTS_DIR))
    for name in ("report", "compare"):
        p = sub.add_parser(name)
        p.add_argument("--gold", required=True)
        p.add_argument("--run", action="append", required=True)
        p.add_argument("--split", choices=["dev", "test", "all"], default="all")
    args = parser.parse_args()

    try:
        if args.cmd == "run":
            if args.split == "test":
                print("⚠️  Đang chạy trên TEST — chỉ chạy một lần cho bản cuối (B10).")
            run_id = args.run_id or f"{args.method}-{args.split}-{datetime.now():%Y%m%d-%H%M%S}"
            rows = run(read_csv(args.answers), load_split(), args.method, run_id=run_id, which=args.split)
            path = Path(args.out_dir) / f"{run_id}.csv"
            write_csv(path, RUN_FIELDS, rows)
            print(f"{run_id}: {len(rows)} ý, {sum(1 for r in rows if r['error'])} ý lỗi → {path}")
            return 0
        gold = read_csv(args.gold)
        runs = [read_csv(r) for r in args.run]
        empty = [r for r, rows in zip(args.run, runs, strict=True) if not rows]
        if empty:
            raise GoldError([f"{r}: file kết quả rỗng" for r in empty])
        if args.cmd == "report":
            for path, rows in zip(args.run, runs, strict=True):
                missing = missing_answers(gold, rows)
                if missing:
                    print(
                        f"⚠️  {Path(path).stem}: thiếu {len(missing)} bài so với gold (vd {missing[:3]}) — chỉ tính phần đã chấm"
                    )
                m = metrics(pair(gold, rows, args.split))
                print(format_report(m, f"{Path(path).stem} [{args.split}]"))
                out = Path(path).with_suffix(f".{args.split}.metrics.json")  # dev / test không ghi đè nhau
                out.write_text(json.dumps({"split": args.split, **m}, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"  → {out}")
        else:
            if len(runs) != 2:
                parser.error("compare cần đúng 2 --run (A rồi B)")
            pa, pb = (pair(gold, r, args.split) for r in runs)
            b = paired_bootstrap(pa, pb)
            name_a, name_b = (Path(r).stem for r in args.run)
            print(f"== B ({name_b}) − A ({name_a}) — {b['answers']} bài chung, bootstrap {b['n']} lần ==")
            for key, better in (("mae_diff", "< 0"), ("item_agreement_diff", "> 0")):
                v = b[key]
                verdict = "có ý nghĩa" if v["significant"] else "KHÔNG kết luận được (khoảng chứa 0)"
                print(
                    f"  {key:<20} {v['diff']:+.3f}  CI95 [{v['ci_low']:+.3f}, {v['ci_high']:+.3f}]  "
                    f"(B tốt hơn khi {better}) — {verdict}"
                )
            if runs[0][0]["method"] == runs[1][0]["method"]:
                print(f"  độ ổn định (cùng cách chấm): {stability(*runs):.1%} ý ra cùng kết quả — mục tiêu ≥ 90%")
    except GoldError as e:
        print(f"Có {len(e.errors)} lỗi:")
        for err in e.errors:
            print("-", err)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
