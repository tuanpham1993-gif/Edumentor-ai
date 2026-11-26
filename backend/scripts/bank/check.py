"""Kiểm ngân hàng đề soạn tay bằng các phép kiểm của hệ thống — KHÔNG gọi Gemini, không ghi DB.

    python -m scripts.bank.check 494                 (file data/review/course_494_en.json + bài thử của khóa)
    python -m scripts.bank.check 494 --file x.json

Kiểm: khung + khớp DB (seed_review) · L1 đáp án đúng dài bất thường · bài mẫu tự luận chấm từ khóa ≥ ngưỡng · chép đề
≤ ngưỡng · bài mẫu câu khác ≤ ngưỡng (barem chung chung) · đề lộ ý barem (L7) · từ khóa bị rút còn 1 chữ · bài thử
cố định (PROBES) · mẫu câu mô tả ý (any one of / both needed).
"""

import argparse
import re

from scripts.bank.common import bank_path, load_bank, load_course, quiet

ANY_ONE = re.compile(r"\(any one of:([^)]*)\)")
BOTH = re.compile(r"\(both needed:([^)]*)\)")
_PARENS = re.compile(r"\([^)]*\)")


def template_problems(code: str, i: int, text: str) -> list[str]:
    """Mẫu câu mô tả ý (26/11): danh sách "any one of" không có "and" (quy tắc 12 của prompt chấm bắt "A and B" phải
    đủ); "both needed" phải có ≥ 2 phần ngăn bằng ";"; ngoài ngoặc KHÔNG có "A and B" — kể cả câu đã dùng mẫu: phần đứng
    trước "(both needed: …)" chỉ là chủ thể, không phải câu tóm tắt (Gemini coi câu tóm tắt là ý chính, 26/11)."""
    out = []
    m = ANY_ONE.search(text)
    if m and re.search(r"\band\b", m.group(1)):
        out.append(f"{code} ý {i}: danh sách 'any one of' có chữ 'and' — Gemini sẽ đòi đủ (quy tắc 12)")
    b = BOTH.search(text)
    if b and len([p for p in b.group(1).split(";") if p.strip()]) < 2:
        out.append(f"{code} ý {i}: 'both needed' cần ≥ 2 phần ngăn bằng ';'")
    if re.search(r"\band\b", _PARENS.sub("", text)):
        out.append(f"{code} ý {i}: câu mô tả có 'A and B' ngoài mẫu — dùng (any one of: …) hoặc (both needed: …)")
    return out


def check(data: dict, probes: dict | None = None) -> tuple[list[str], list[str], dict]:
    """→ (vấn đề, giới hạn đã biết (c), vị trí đáp án đúng). Cần DB (khớp mã kỹ năng)."""
    from app.ai.review.keyword_grader_en import _kw
    from app.ai.review.question_gate import fake_scores, keyword_score, length_hint, length_ratio, model_answer
    from app.ai.review.question_schema import leaked_items
    from app.core.config import settings
    from app.core.database import SessionLocal
    from app.core.seed_data.seed_review import check_against_db, validate_bank

    problems = [f"khung: {e}" for e in validate_bank(data)]
    with SessionLocal() as db:
        problems += [f"DB: {e}" for e in check_against_db(db, data)]
    essays = [q for q in data["questions"] if q["type"] == "essay"]
    answers = {q["code"]: model_answer(q) for q in essays}
    pos: dict[int, int] = {}
    for q in data["questions"]:
        code = q["code"]
        if q["type"] == "mcq":
            pos[q["correct_index"]] = pos.get(q["correct_index"], 0) + 1
            if length_hint(q):
                problems.append(f"{code}: L1 đáp án đúng dài bất thường (tỉ lệ {length_ratio(q)})")
            continue
        others = [a for c, a in answers.items() if c != code and c.split("-")[0] == code.split("-")[0]]
        fake = fake_scores(q, others)
        if fake["model"] < settings.REVIEW_GATE_MODEL_MIN:
            problems.append(f"{code}: bài mẫu chỉ {fake['model']}/10")
        if fake["copy"] > settings.REVIEW_GATE_COPY_MAX:
            problems.append(f"{code}: chép đề đã {fake['copy']}/10")
        if fake.get("other", 0) > settings.REVIEW_GATE_OTHER_MAX:
            problems.append(f"{code}: bài câu khác {fake['other']}/10 — barem chung chung")
        leaked = leaked_items(q["content"], q["rubric"])
        if leaked:
            problems.append(f"{code}: đề lộ ý barem {leaked}")
        for i, item in enumerate(q["rubric"], start=1):
            problems += template_problems(code, i, item["text"])
            for kw in item["main_keywords"]:
                toks = _kw(kw)
                if not toks:
                    problems.append(f"{code} ý {i}: từ khóa '{kw}' rỗng sau tiền xử lý")
                elif len(kw.split()) > 1 and len(toks) == 1:
                    problems.append(f"{code} ý {i}: từ khóa '{kw}' rút gọn còn 1 chữ '{toks[0]}'")

    known = []
    if probes is not None:
        byc = {q["code"]: q for q in essays}
        for code, cases in probes.items():
            q = byc[code]
            for label, text, cond in cases:
                sc = keyword_score(q["rubric"], text, q["content"])
                if cond == "c":
                    known.append(f"{code} [{label}]: {sc}/10")
                    continue
                op, lim = cond[:2], float(cond[2:])
                if (op == ">=" and sc < lim) or (op == "<=" and sc > lim):
                    problems.append(f"{code} bài thử [{label}]: {sc}/10, cần {cond}")
        problems += [f"{c}: chưa có bài thử" for c in byc if c not in probes]
    return problems, known, pos


def main() -> int:
    parser = argparse.ArgumentParser(description="Kiểm ngân hàng đề soạn tay (không gọi Gemini)")
    parser.add_argument("course_id", type=int)
    parser.add_argument("--file", help="mặc định data/review/course_<id>_en.json")
    args = parser.parse_args()
    quiet()
    data = load_bank(args.file or bank_path(args.course_id))
    problems, known, pos = check(data, load_course(args.course_id).PROBES)
    print(f"{len(data['chunks'])} đoạn, {len(data['questions'])} câu; vị trí đáp án đúng: {dict(sorted(pos.items()))}")
    print(f"{len(problems)} vấn đề")
    for p in problems:
        print(" -", p)
    if known:
        print("Giới hạn đã biết của bộ chấm từ khóa (không tính lỗi):")
        for k in known:
            print(" -", k)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
