"""Bộ bài chuẩn (gold set) — thu bài, tạo phiếu chấm cho người chấm, gộp thành gold.csv (module 09 · Tuấn · B4, 14/11/2026).

Quy trình (chi tiết: docs/ai-grading/DATA_COLLECTION.md), chạy trong thư mục backend:

    # 1. Gom bài từ file CSV xuất ra từ Google Form (Form A, Form B) → answers.csv (định dạng dọc, mỗi dòng một bài)
    python -m scripts.gold_sheets collect --form form_a.csv --form form_b.csv --out data/ai-grading/private/answers.csv
       Bài nhóm tự viết / AI sinh: thêm tay vào answers.csv (source = team / ai, mã T001 / A001). AI chỉ được ở dev.
    # 2. Tạo phiếu chấm riêng cho từng người chấm (thứ tự bài xáo khác nhau, KHÔNG có điểm AI / điểm người kia)
    python -m scripts.gold_sheets sheets --answers data/ai-grading/private/answers.csv \
        --out-dir data/ai-grading/private --rater hoa --rater tam
    # 3. Gộp hai phiếu đã chấm → gold.csv + disagreements.csv (các ý hai người lệch nhau) + in độ đồng thuận
    python -m scripts.gold_sheets merge --answers data/ai-grading/private/answers.csv \
        --sheet data/ai-grading/private/rater_hoa.csv --sheet data/ai-grading/private/rater_tam.csv \
        --out data/ai-grading/private/gold.csv
    # 4. Tuấn / thầy điền cột `final` trong disagreements.csv → chạy lại merge kèm --adjudicated disagreements.csv

Dữ liệu thật nằm trong data/ai-grading/private/ — thư mục này bị .gitignore, KHÔNG commit.
Nhãn mỗi ý: full / partial / none (điểm = max_points / ½ max_points / 0) — giống bộ chấm và AI (docs/ai-grading/RATER_GUIDELINE.md).
"""

import argparse
import csv
import json
import math
import random
import re
import sys
from pathlib import Path

from sklearn.metrics import cohen_kappa_score

BACKEND = Path(__file__).resolve().parents[1]
SPLIT_FILE = BACKEND / "data" / "ai-grading" / "split.json"
LABELS = ("full", "partial", "none")
SOURCES = ("real", "team", "ai")
ANSWER_FIELDS = ["answer_id", "question_code", "split", "source", "answer_text"]
SHEET_FIELDS = [
    "row_id",
    "answer_id",
    "question_code",
    "question",
    "answer",
    "item_no",
    "item",
    "max_points",
    "label",
    "note",
]
GOLD_FIELDS = [
    "answer_id",
    "question_code",
    "split",
    "source",
    "item_no",
    "max_points",
    "label_a",
    "label_b",
    "label",
    "points",
]
DISAGREE_FIELDS = ["answer_id", "question_code", "item_no", "item", "answer", "label_a", "label_b", "final"]
_CODE_IN_HEADER = re.compile(r"\[([A-Z]+-TL-\d{2})\]")  # tiêu đề câu hỏi trên Form: "[PY-TL-03] Explain ..."
_CONSENT_YES = ("yes", "i agree", "đồng ý", "dong y")


class GoldError(Exception):
    """Dữ liệu sai — in tất cả lỗi, không ghi gì."""

    def __init__(self, errors: list[str]):
        super().__init__("\n".join(errors))
        self.errors = errors


# ─────────────── đọc / ghi ───────────────


def load_split(path=SPLIT_FILE) -> dict:
    with open(path, encoding="utf-8") as f:
        split = json.load(f)
    with open(BACKEND / split["bank"], encoding="utf-8") as f:
        bank = {q["code"]: q for q in json.load(f)["questions"]}
    split["questions"] = {code: bank[code] for code in split["dev"] + split["test"]}
    split["split_of"] = {**{c: "dev" for c in split["dev"]}, **{c: "test" for c in split["test"]}}
    return split


def read_csv(path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as f:  # utf-8-sig: file mở / lưu bằng Excel có BOM
        return list(csv.DictReader(f))


def write_csv(path, fields: list[str], rows: list[dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:  # BOM để Excel / Google Sheets hiện đúng chữ
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def round_score(x: float) -> int:
    """Làm tròn điểm tổng để tính QWK: NỬA LÊN (7,5 → 8). round() của Python làm tròn về số chẵn (2,5 → 2,
    7,5 → 8) — điểm có ½ (nhãn partial) rất hay gặp nên sẽ lệch không đều."""
    return math.floor(x + 0.5)


def points_of(label: str, max_points: float) -> float:
    return {"full": max_points, "partial": max_points / 2, "none": 0.0}[label]


# ─────────────── 1. collect ───────────────


def collect(form_rows: list[list[dict]], split: dict, *, start: int = 1) -> list[dict]:
    """Bảng Google Form (mỗi dòng một người, mỗi cột một câu) → mỗi dòng một bài. Bỏ người không đồng ý, bài trống."""
    out, n = [], start
    for rows in form_rows:
        for row in rows:
            consent = next((v for k, v in row.items() if k and "consent" in k.lower()), None)
            if consent is not None and not consent.strip().lower().startswith(_CONSENT_YES):
                continue
            for header, text in row.items():
                m = _CODE_IN_HEADER.search(header or "")
                if not m or m.group(1) not in split["split_of"] or not (text or "").strip():
                    continue
                code = m.group(1)
                out.append(
                    {
                        "answer_id": f"R{n:04d}",
                        "question_code": code,
                        "split": split["split_of"][code],
                        "source": "real",
                        "answer_text": text.strip(),
                    }
                )
                n += 1
    return out


# ─────────────── kiểm tra answers.csv ───────────────


def answer_errors(answers: list[dict], split: dict) -> list[str]:
    errors, seen = [], set()
    for a in answers:
        where = f"Bài {a.get('answer_id') or '(thiếu mã)'}"
        if not a.get("answer_id"):
            errors.append("Có bài thiếu answer_id")
        elif a["answer_id"] in seen:
            errors.append(f"{where}: answer_id bị trùng")
        seen.add(a.get("answer_id"))
        code = a.get("question_code")
        if code not in split["split_of"]:
            errors.append(f"{where}: câu '{code}' không có trong split.json")
        elif a.get("split") != split["split_of"][code]:
            errors.append(f"{where}: split phải là '{split['split_of'][code]}' (chia theo câu hỏi)")
        if a.get("source") not in SOURCES:
            errors.append(f"{where}: source phải là một trong {SOURCES}")
        elif a["source"] == "ai" and a.get("split") == "test":
            errors.append(f"{where}: bài AI sinh không được nằm trong test")
        if not (a.get("answer_text") or "").strip():
            errors.append(f"{where}: bài trống")
    return errors


# ─────────────── 2. sheets ───────────────


def make_sheet(answers: list[dict], split: dict, rater: str) -> list[dict]:
    """Phiếu chấm của một người: mỗi dòng một (bài, ý). Thứ tự bài xáo theo tên người chấm (tái lập được, khác nhau
    giữa hai người → không bị ảnh hưởng thứ tự). Không có cột điểm AI / điểm người khác."""
    errors = answer_errors(answers, split)
    if errors:
        raise GoldError(errors)
    order = list(answers)
    random.Random(f"gold-{rater}").shuffle(order)
    rows = []
    for a in order:
        q = split["questions"][a["question_code"]]
        for no, item in enumerate(q["rubric"], start=1):
            rows.append(
                {
                    "row_id": len(rows) + 1,
                    "answer_id": a["answer_id"],
                    "question_code": a["question_code"],
                    "question": q["content"],
                    "answer": a["answer_text"],
                    "item_no": no,
                    "item": item["text"],
                    "max_points": item["max_points"],
                    "label": "",
                    "note": "",
                }
            )
    return rows


# ─────────────── 3. merge ───────────────


def _labels(sheet: list[dict], name: str, expected: set[tuple[str, int]]) -> tuple[dict, list[str]]:
    errors, labels = [], {}
    for r in sheet:
        key = (r["answer_id"], int(r["item_no"]))
        label = (r.get("label") or "").strip().lower()
        if label not in LABELS:
            errors.append(
                f"Phiếu {name}, dòng {r.get('row_id')} ({key[0]} ý {key[1]}): nhãn '{label}' phải là full / partial / none"
            )
        labels[key] = label
    missing = expected - labels.keys()
    if missing:
        errors.append(f"Phiếu {name}: thiếu {len(missing)} ý, ví dụ {sorted(missing)[:3]}")
    return labels, errors


def merge(answers: list[dict], split: dict, sheet_a: list[dict], sheet_b: list[dict], adjudicated=None) -> dict:
    """Hai phiếu → dòng gold + danh sách bất đồng + thống kê đồng thuận. `adjudicated`: {(answer_id, item_no): nhãn}."""
    errors = answer_errors(answers, split)
    by_id = {a["answer_id"]: a for a in answers}
    expected = {
        (a["answer_id"], no)
        for a in answers
        if a.get("question_code") in split["questions"]
        for no in range(1, len(split["questions"][a["question_code"]]["rubric"]) + 1)
    }
    labels_a, err_a = _labels(sheet_a, "A", expected)
    labels_b, err_b = _labels(sheet_b, "B", expected)
    errors += err_a + err_b
    adjudicated = adjudicated or {}
    errors += [f"Phân xử {k[0]} ý {k[1]}: nhãn '{v}' không hợp lệ" for k, v in adjudicated.items() if v not in LABELS]
    if errors:
        raise GoldError(errors)

    gold, disagreements = [], []
    for answer_id, no in sorted(expected):
        a = by_id[answer_id]
        item = split["questions"][a["question_code"]]["rubric"][no - 1]
        la, lb = labels_a[(answer_id, no)], labels_b[(answer_id, no)]
        final = la if la == lb else adjudicated.get((answer_id, no), "")
        if la != lb:
            disagreements.append(
                {
                    "answer_id": answer_id,
                    "question_code": a["question_code"],
                    "item_no": no,
                    "item": item["text"],
                    "answer": a["answer_text"],
                    "label_a": la,
                    "label_b": lb,
                    "final": final,
                }
            )
        gold.append(
            {
                "answer_id": answer_id,
                "question_code": a["question_code"],
                "split": a["split"],
                "source": a["source"],
                "item_no": no,
                "max_points": item["max_points"],
                "label_a": la,
                "label_b": lb,
                "label": final,
                "points": points_of(final, float(item["max_points"])) if final else "",
            }
        )
    return {"gold": gold, "disagreements": disagreements, "stats": agreement(gold)}


def agreement(gold: list[dict]) -> dict:
    """Đồng thuận giữa hai người chấm: % ý trùng nhãn, kappa theo nhãn ý, QWK theo tổng điểm bài (làm tròn)."""
    la = [g["label_a"] for g in gold]
    lb = [g["label_b"] for g in gold]
    totals: dict[str, list[float]] = {}
    for g in gold:
        mp = float(g["max_points"])
        t = totals.setdefault(g["answer_id"], [0.0, 0.0])
        t[0] += points_of(g["label_a"], mp)
        t[1] += points_of(g["label_b"], mp)
    ta = [round_score(t[0]) for t in totals.values()]
    tb = [round_score(t[1]) for t in totals.values()]
    return {
        "items": len(gold),
        "answers": len(totals),
        "item_agreement": sum(x == y for x, y in zip(la, lb, strict=True)) / len(gold) if gold else 0.0,
        "item_kappa": _kappa(la, lb),
        "total_qwk": _kappa(ta, tb, weights="quadratic"),
        "unresolved": sum(1 for g in gold if not g["label"]),
    }


def _kappa(a: list, b: list, weights=None) -> float:
    if not a or len(set(a) | set(b)) < 2:
        return 1.0 if a == b else 0.0  # chỉ một nhãn duy nhất → kappa không xác định
    return float(cohen_kappa_score(a, b, weights=weights))


# ─────────────── CLI ───────────────


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252 → lỗi khi in "✓", tiếng Việt
    parser = argparse.ArgumentParser(description="Bộ bài chuẩn (B4): collect → sheets → merge")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("collect", help="CSV xuất từ Google Form → answers.csv")
    p.add_argument("--form", action="append", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("sheets", help="answers.csv → phiếu chấm cho từng người")
    p.add_argument("--answers", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--rater", action="append", required=True)
    p = sub.add_parser("merge", help="hai phiếu đã chấm → gold.csv + disagreements.csv")
    p.add_argument("--answers", required=True)
    p.add_argument("--sheet", action="append", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--adjudicated", help="disagreements.csv đã điền cột final")
    args = parser.parse_args()
    split = load_split()

    try:
        if args.cmd == "collect":
            rows = collect([read_csv(f) for f in args.form], split)
            write_csv(args.out, ANSWER_FIELDS, rows)
            print(f"Đã gom {len(rows)} bài thật → {args.out}")
        elif args.cmd == "sheets":
            answers = read_csv(args.answers)
            for rater in args.rater:
                path = Path(args.out_dir) / f"rater_{rater}.csv"
                rows = make_sheet(answers, split, rater)
                write_csv(path, SHEET_FIELDS, rows)
                print(f"Phiếu {rater}: {len(rows)} ý / {len(answers)} bài → {path}")
        else:
            if len(args.sheet) != 2:
                parser.error("merge cần đúng 2 --sheet")
            adjudicated = None
            if args.adjudicated:
                adjudicated = {
                    (r["answer_id"], int(r["item_no"])): r["final"].strip().lower()
                    for r in read_csv(args.adjudicated)
                    if (r.get("final") or "").strip()
                }
            result = merge(read_csv(args.answers), split, *(read_csv(s) for s in args.sheet), adjudicated)
            write_csv(args.out, GOLD_FIELDS, result["gold"])
            dis_path = Path(args.out).with_name("disagreements.csv")
            write_csv(dis_path, DISAGREE_FIELDS, result["disagreements"])
            s = result["stats"]
            print(
                f"{s['answers']} bài / {s['items']} ý — trùng nhãn {s['item_agreement']:.1%}, kappa ý {s['item_kappa']:.3f}, "
                f"QWK tổng điểm {s['total_qwk']:.3f}; {len(result['disagreements'])} ý lệch → {dis_path}"
            )
            if s["unresolved"]:
                print(
                    f"Còn {s['unresolved']} ý chưa phân xử: điền cột final trong {dis_path} rồi chạy lại với --adjudicated"
                )
    except GoldError as e:
        print(f"Có {len(e.errors)} lỗi — KHÔNG ghi gì:")
        for err in e.errors:
            print("-", err)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
