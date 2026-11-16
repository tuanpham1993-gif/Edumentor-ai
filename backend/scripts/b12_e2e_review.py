"""B12 — kiểm thử toàn luồng ôn tập trên Docker (module 09 · Tuấn · 16/11/2026).

Đóng vai học viên, gọi ĐÚNG các API trình duyệt gọi: đăng ký → đăng nhập → tham gia khóa 312 → bắt đầu ôn tập →
làm bài (3 câu tự luận: 1 đúng = đáp án mẫu, 1 sai / lạc đề, 1 bỏ trống) → nộp (đo thời gian, mục tiêu ≤ 20 s
hoặc "Đang chấm") → đọc kết quả (graded_by, lý do, câu trích có thật trong bài, nhận xét — B11).

Chạy (backend Docker đang chạy, AI_MODE=real, có khóa Gemini; trong thư mục backend):
    python scripts/b12_e2e_review.py                              # mặc định http://localhost:8001/api
    python scripts/b12_e2e_review.py http://localhost:8000/api    # backend chạy local
Tạo 1 học viên thử b12.<giờ>@example.com trong DB DEV mỗi lần chạy — KHÔNG chạy trên DB thật.
"""

import json
import sys
import time
from pathlib import Path

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001/api"
BANK = json.loads((Path(__file__).resolve().parents[1] / "data/review/course_312_en.json").read_text(encoding="utf-8"))
MODEL = {q["content"]: q for q in BANK["questions"]}
c = httpx.Client(base_url=BASE, timeout=180)


def ok(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)

email = f"b12.{int(time.time())}@example.com"
pw = "B12test@123"
r = c.post("/auth/register", json={"full_name": "Học viên B12", "email": email, "password": pw, "confirm_password": pw})
ok(r.status_code in (200, 201), f"đăng ký {email}: {r.status_code}")
tok = c.post("/auth/login", json={"email": email, "password": pw}).json()["access_token"]
c.headers["Authorization"] = f"Bearer {tok}"
ok(c.post("/courses/312/join").status_code in (200, 201), "tham gia khóa 312")

info = c.get("/courses/312/review").json()
ok(info["can_start"], f"được bắt đầu ôn tập (blocked={info['blocked']})")

t0 = time.perf_counter()
att = c.post("/courses/312/review-attempts")
t_start = time.perf_counter() - t0
att = att.json()
qs = att["questions"]
ok(len(qs) == 15, f"đề có {len(qs)} câu, sinh trong {t_start:.1f} s")
english = all(not any(ch in q["content"] for ch in "ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệ") for q in qs)
ok(english, "đề toàn tiếng Anh (ngân hàng B2)")
essays = [q for q in qs if q["type"] == "essay"]
print(f"  · {len(qs) - len(essays)} trắc nghiệm, {len(essays)} tự luận")

answers, plan = [], {}
for q in qs:
    if q["type"] == "mcq":
        answers.append({"position": q["position"], "selected_index": 0})
for i, q in enumerate(essays):
    bank_q = MODEL.get(q["content"])
    if i == 0 and bank_q:
        text = bank_q["explanation"].removeprefix("Model answer:").strip()
        plan[q["position"]] = "đúng (đáp án mẫu)"
    elif i == 1:
        text = ("I think the answer is the opposite of what the lesson says. It always does the reverse, "
                "and it is not related to the question at all.")  # fmt: skip
        plan[q["position"]] = "sai / lạc đề"
    else:
        text = ""
        plan[q["position"]] = "bỏ trống"
    if text:
        answers.append({"position": q["position"], "text_answer": text})
ok(c.patch(f"/review-attempts/{att['attempt_id']}/answers", json={"answers": answers}).status_code == 200,
   "lưu câu trả lời")  # fmt: skip

t0 = time.perf_counter()
res = c.post(f"/review-attempts/{att['attempt_id']}/submit").json()
t_submit = time.perf_counter() - t0
ok(t_submit <= 25, f"nộp bài trả về sau {t_submit:.1f} s, trạng thái '{res['status']}' (mục tiêu ≤ 20 s hoặc 'grading')")
waited = 0
while res["status"] == "grading" and waited < 150:
    time.sleep(5)
    waited += 5
    res = c.get(f"/me/review-history/{att['attempt_id']}").json()
if waited:
    ok(res["status"] == "graded", f"'Đang chấm' → chấm xong sau thêm ~{waited} s")

print(f"\n  Điểm: {res['score']}/10 (TN {res['mcq_score']}, TL {res['essay_score']}) · đạt: {res['passed']}")
for q in res["questions"]:
    if q["type"] != "essay":
        continue
    print(f"\n  Câu {q['position']} [{plan.get(q['position'])}] {q['points']}/{q['max_points']} · graded_by={q['graded_by']}"
          f" · needs_review={q['needs_review']}")  # fmt: skip
    for r_ in q["rubric"]:
        ev = r_["evidence"]
        print(f"    - {r_['result']:<5} {r_['text'][:60]} | lý do: {(r_['reason'] or '—')[:90]}")
        if ev:
            ok(ev.lower() in (q["text_answer"] or "").lower(), f"câu trích có trong bài: “{ev[:50]}”")
    if q["feedback"]:
        print(f"    nhận xét: {q['feedback'][:160]}")
print(f"\nATTEMPT_ID={att['attempt_id']} EMAIL={email}")
