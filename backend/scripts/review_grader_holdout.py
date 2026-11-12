"""Bộ kiểm cuối bộ chấm từ khóa (QT12 · 12/11): 5 bài MỚI, chưa dùng khi chỉnh barem / bộ chấm. Chuẩn = Gemini.
Gọi Gemini THẬT (5 lượt, cần LLM_API_KEY). Chạy trong backend/:  python -X utf8 -m scripts.review_grader_holdout"""
import json
import sys
import time

sys.path.insert(0, ".")
from app.ai.review.base import AIUnavailableError
from app.ai.review.keyword_grader import grade_essay
from app.ai.review.real_ai import RealAI, review_llm

with open("data/review/course_312.json", encoding="utf-8") as f:
    bank = json.load(f)
Q = {q["code"].removeprefix("312-"): q for q in bank["questions"]}

HOLDOUT = [
    ("H1 đúng, viết tự nhiên", "CS-TL-01",
     "Thuật toán là một dãy các bước rõ ràng để giải quyết một bài toán. Nó phải dừng sau một số bước hữu hạn và mỗi bước phải rõ ràng, không mơ hồ."),
    ("H2 sai, đảo print / input", "PY-TL-03",
     "print() dùng để nhập dữ liệu từ bàn phím, còn input() dùng để in kết quả ra màn hình."),
    ("H3 đúng, viết bằng code", "ITER-TL-05",
     "mk = input('Nhập mật khẩu: ')\nwhile mk != 'abc123':\n    mk = input('Sai, nhập lại: ')\nprint('Đăng nhập thành công')\nDùng while vì không biết trước người dùng sẽ nhập sai bao nhiêu lần."),
    ("H4 thiếu ý (không nêu tuoi = 30)", "COND-TL-06",
     "if tuoi < 12 or tuoi >= 60: print('Giảm giá'). Dùng or vì chỉ cần thỏa một trong hai điều kiện là được giảm."),
    ("H5 đúng, không dấu", "VAR-TL-03",
     "phep gan dung dau = de dua gia tri vao bien. x = x + 1 lay gia tri cu cua x cong them 1 roi gan lai cho x, tuc la tang x len 1."),
]

ai = RealAI(timeout=60)
print(f"Gemini model: {review_llm()[1]}\n")
print(f"{'Bài':36} {'Câu':11} {'Từ khóa':>8} {'Gemini':>7} {'lệch':>5}  cờ (>3)")
rows = []
for name, code, answer in HOLDOUT:
    q = Q[code]
    kw = sum(r["points"] for r in grade_essay(q["rubric"], answer, q["content"]))
    try:
        gem = sum(r["points"] for r in ai.grade_essay({"content": q["content"], "rubric": q["rubric"], "explanation": q.get("explanation")}, answer))
        diff = abs(kw - gem)
        print(f"{name:36} {code:11} {kw:8.1f} {gem:7.1f} {diff:5.1f}  {'⚑' if diff > 3 else ''}")
        rows.append((name, kw, gem))
    except AIUnavailableError as err:
        print(f"{name:36} {code:11} {kw:8.1f} {'LỖI':>7}         {err}")
    time.sleep(1)
if rows:
    mae = sum(abs(k - g) for _, k, g in rows) / len(rows)
    print(f"\nLệch trung bình |từ khóa − Gemini|: {mae:.2f} điểm / 10 · số bài lệch > 3: {sum(abs(k - g) > 3 for _, k, g in rows)}/{len(rows)}")
