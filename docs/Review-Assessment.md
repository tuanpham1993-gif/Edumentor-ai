# Review-Assessment — Kế hoạch code module Ôn tập & Đánh giá kiến thức (F09)

> Người thực hiện: **Tuấn** · Người review: **Claude** · Bắt đầu: **16/11/2026** · Dự kiến xong: **25/11/2026**
> **Tổng thời gian 2 module (01 + 09): 05/11 → 25/11/2026.**
> Căn cứ: `EdumentorAi_BA_v3.md` — UC-09, FR-24 → FR-29, FR-54, BR-04, bảng API (dòng ~1494–1500, ~1533–1536); giao diện demo `docs/EduMentor-UI-design/ui-design/` (ReviewStart, ReviewQuiz, ReviewResult, ReviewHistory, ReviewDetail, ReviewDetail-Explanation, Profile).
> Cách dùng: làm xong việc nào thì tích `[x]` và điền **ngày thực tế**. Hết mỗi giai đoạn, nhắn "review GĐ x — Assessment" để Claude review.
> Làm **sau** module Tài khoản (`docs/Review-Auth.md`) vì cần: `get_current_user`, `UserSkill` (GĐ4 Auth), `core/email.py` (GĐ5 Auth).

> ⚠️ **06/11/2026 — Thầy bổ sung yêu cầu: AI sinh câu hỏi (system prompt + RAG), gồm trắc nghiệm và tự luận.**
> Đề xuất chi tiết: **`docs/De-xuat-AI-On-tap.md`** (kèm Phụ lục A — tiêu chí chấm) — trạng thái **CHỜ THẦY XÁC NHẬN** (câu A1–A13, chép ở bảng "Câu hỏi cần chốt" bên dưới).
> 📅 **Thảo luận sâu phần Ôn tập: 09/11/2026.**
> Kế hoạch các giai đoạn bên dưới **vẫn là bản cũ (ngân hàng câu hỏi, chỉ trắc nghiệm)**; sẽ viết lại GĐ1–GĐ7 và lịch sau khi thầy trả lời A1–A9.
> Ảnh hưởng dự kiến: thêm `type` / `source` / `rubric` cho câu hỏi, `text_answer` / `ai_score` / `ai_feedback` cho câu trả lời, bảng `KnowledgeChunk` (RAG), `ai/client.py` + mock, system prompt, validator, AI chấm tự luận. Cần cập nhật BA FR-24, FR-25, FR-26.

---

## Tổng quan tiến độ

| GĐ | Nội dung | Dự kiến | Thực tế bắt đầu | Thực tế xong | Xong |
|---|---|---|---|---|---|
| 0 | Đọc nghiệp vụ, chốt phụ thuộc | 16/11 → 16/11 | __/__ | __/__ | [ ] |
| 1 | Model Question, ReviewAttempt, ReviewAnswer | 17/11 → 17/11 | __/__ | __/__ | [ ] |
| 2 | Ngân hàng câu hỏi (admin / dữ liệu mẫu) | 18/11 → 18/11 | __/__ | __/__ | [ ] |
| 3 | Màn "Bắt đầu ôn tập" | 19/11 → 19/11 | __/__ | __/__ | [ ] |
| 4 | Tạo / tiếp tục bài, lưu câu trả lời | 20/11 → 21/11 | __/__ | __/__ | [ ] |
| 5 | Nộp bài, chấm điểm, cập nhật khóa học & kỹ năng | 22/11 → 23/11 | __/__ | __/__ | [ ] |
| 6 | Lịch sử ôn tập | 24/11 → 24/11 | __/__ | __/__ | [ ] |
| 7 | Hoàn thiện, kiểm thử, gộp nhánh | 25/11 → 25/11 | __/__ | __/__ | [ ] |

---

## Giai đoạn 0 — Đọc nghiệp vụ, chốt phụ thuộc (16/11)

- [ ] **0.1 Đọc BA**: UC-09, FR-24 → FR-29, FR-54 — dự kiến 16/11 · thực tế __/__
- [ ] **0.2 Xem màn demo**: ReviewStart, ReviewQuiz, ReviewResult, ReviewHistory, ReviewDetail(-Explanation), mục "ôn tập gần đây" ở Profile — dự kiến 16/11 · thực tế __/__
  - Ghi lại: mỗi màn cần dữ liệu gì → đó là response của API.
- [ ] **0.3 Chốt phụ thuộc với nhóm** — dự kiến 16/11 · thực tế __/__
  - Bảng khóa học + liên kết khóa học ↔ kỹ năng (Khôi/Hòa).
  - Bảng trạng thái khóa học của người dùng `ongoing`/`completed` (Hòa — Theo dõi tiến trình).
  - Ai làm quản trị ngân hàng câu hỏi (FR-54) — xem Q1.
- [ ] **0.4 Chọn cách đặt file model** — dự kiến 16/11 · thực tế __/__
  - Repo đang có cả `models/review_attempt.py`, `models/review_question.py` (rỗng) và cây mục tiêu ghi `models/review.py`. Chọn một cách, không giữ cả hai.

## Giai đoạn 1 — Model (17/11)

- [ ] **1.1 `Question`** — `question_id`, `skill_id`, nội dung, **4 lựa chọn**, đáp án đúng, giải thích, `created_at` (FR-25) — dự kiến 17/11 · thực tế __/__
- [ ] **1.2 `ReviewAttempt`** — `attempt_id`, `user_id`, `course_id`, trạng thái (đang làm / đã nộp), số câu đúng, tổng câu, phần trăm, đạt hay không, `started_at`, `submitted_at` — dự kiến 17/11 · thực tế __/__
  - Ràng buộc: mỗi người dùng + khóa học có **tối đa một bài đang làm** (UC-09).
- [ ] **1.3 `ReviewAnswer`** — `attempt_id`, `question_id`, thứ tự câu (1–20), lựa chọn đã chọn (có thể trống), đúng/sai — dự kiến 17/11 · thực tế __/__
- [ ] **1.4 `core/config.py`** — `REVIEW_PASS_PERCENT=60`, `REVIEW_QUESTION_COUNT=20` đọc từ `.env`, **không ghi cứng** (FR-26) — dự kiến 17/11 · thực tế __/__
- [ ] **1.5 Kiểm tra bảng trong pgAdmin + nhờ Claude review GĐ1** — dự kiến 17/11 · thực tế __/__

## Giai đoạn 2 — Ngân hàng câu hỏi (18/11)

> Cần trả lời Q1 trước. Nếu admin câu hỏi không phải phần của bạn: chỉ làm 2.4 (dữ liệu mẫu) để test.

- [ ] **2.1 `schemas/review.py`** — `QuestionCreate`, `QuestionUpdate`, `QuestionResponse` (admin thấy đáp án) — dự kiến 18/11 · thực tế __/__
  - Kiểm tra: đúng 4 lựa chọn, đáp án đúng nằm trong 4 lựa chọn đó.
- [ ] **2.2 `repositories/review_repository.py`, `services/question_service.py`** — dự kiến 18/11 · thực tế __/__ → __/__
- [ ] **2.3 `endpoints/admin/questions.py`** (dùng `require_admin`) — dự kiến 18/11 · thực tế __/__ → __/__
  - `GET /api/admin/questions?skill_id=`, `POST /api/admin/questions`, `PATCH /api/admin/questions/{question_id}`, `DELETE /api/admin/questions/{question_id}`.
- [ ] **2.4 Dữ liệu mẫu câu hỏi** — đủ ≥ 20 câu cho các kỹ năng của 1–2 khóa để test — dự kiến 18/11 · thực tế __/__
- [ ] **2.5 Test + nhờ Claude review GĐ2** — student gọi API admin → 403 — dự kiến 18/11 · thực tế __/__

## Giai đoạn 3 — Màn "Bắt đầu ôn tập" (19/11)

- [ ] **3.1 `GET /api/courses/{course_id}/review`** — dự kiến 19/11 · thực tế __/__
  - Trả: kỹ năng của khóa, số câu (20), ngưỡng đạt (lấy từ config), bài đang làm dở nếu có, các lần làm trước, **lý do chưa thể ôn tập**:
    - chưa tham gia khóa học (không ở trạng thái Đang học),
    - khóa chưa đủ 20 câu hỏi → "Bài ôn tập chưa sẵn sàng".
- [ ] **3.2 Test + nhờ Claude review GĐ3** — dự kiến 19/11 · thực tế __/__

## Giai đoạn 4 — Tạo / tiếp tục bài, lưu câu trả lời (20/11 → 21/11)

- [ ] **4.1 Thuật toán chọn 20 câu chia đều theo kỹ năng** (`services/review_service.py`) — dự kiến 20/11 · thực tế __/__
  - Ví dụ 3 kỹ năng → 7 + 7 + 6. Trường hợp chia lẻ hoặc một kỹ năng thiếu câu → xem Q3.
  - Viết test riêng cho hàm này trước khi gắn vào API.
- [ ] **4.2 `POST /api/courses/{course_id}/review-attempts`** — có bài dở thì **trả lại bài đó**, không có thì tạo mới — dự kiến 20/11 · thực tế __/__
- [ ] **4.3 `GET /api/review-attempts/{attempt_id}`** — câu hỏi + câu đã chọn, **không lộ đáp án đúng và giải thích** — dự kiến 20/11 · thực tế __/__
- [ ] **4.4 `PATCH /api/review-attempts/{attempt_id}/answers`** — lưu câu trả lời khi Tạm rời (FR-29); bài đã nộp thì không cho sửa — dự kiến 21/11 · thực tế __/__
- [ ] **4.5 Kiểm tra quyền sở hữu** — người khác mở `attempt_id` của mình phải bị chặn (BR-01, NFR-06) — dự kiến 21/11 · thực tế __/__
- [ ] **4.6 Test + nhờ Claude review GĐ4** — dự kiến 21/11 · thực tế __/__

## Giai đoạn 5 — Nộp bài, chấm điểm (22/11 → 23/11)

- [ ] **5.1 `POST /api/review-attempts/{attempt_id}/submit`** — dự kiến 22/11 · thực tế __/__ → __/__
  - So lựa chọn với đáp án lưu sẵn; **câu bỏ trống = sai** (FR-26).
  - Tính số câu đúng, phần trăm; **đạt khi ≥ `REVIEW_PASS_PERCENT`**.
  - Nộp lần hai cùng một bài → từ chối.
- [ ] **5.2 Khi đạt — cập nhật trong cùng một transaction** — dự kiến 22/11 · thực tế __/__
  - Khóa học của người dùng → `completed` (bảng của Hòa — phối hợp).
  - Kỹ năng của khóa → `known` trong `UserSkill` (bảng của bạn).
  - Lỗi giữa chừng → rollback toàn bộ, không báo thành công (FR-43).
- [ ] **5.3 Gửi email kết quả** (dùng `core/email.py`) — gửi **sau** khi lưu xong — dự kiến 23/11 · thực tế __/__
- [ ] **5.4 Test**: đạt / chưa đạt / đúng ngưỡng 60% / bỏ trống / nộp lại — dự kiến 23/11 · thực tế __/__
- [ ] **5.5 Nhờ Claude review GĐ5** (giai đoạn quan trọng nhất) — dự kiến 23/11 · thực tế __/__

## Giai đoạn 6 — Lịch sử ôn tập (24/11)

- [ ] **6.1 `GET /api/me/review-history`** — lọc `course_id`, `passed`; có phân trang (`core/pagination.py`) — dự kiến 24/11 · thực tế __/__
- [ ] **6.2 `GET /api/me/review-history/{attempt_id}`** — từng câu, đáp án đã chọn, đáp án đúng, giải thích (FR-28) — dự kiến 24/11 · thực tế __/__
  - Chỉ trả cho bài **đã nộp** của **chính người dùng**.
- [ ] **6.3 Test + nhờ Claude review GĐ6** — dự kiến 24/11 · thực tế __/__

## Giai đoạn 7 — Hoàn thiện (25/11)

- [ ] **7.1 Chạy toàn bộ** `pytest`, `black .`, `ruff check .` — dự kiến 25/11 · thực tế __/__
- [ ] **7.2 Rà bảo mật**: không lộ đáp án trước khi nộp; không xem được bài của người khác; API admin chặn student — dự kiến 25/11 · thực tế __/__
- [ ] **7.3 Gộp với module Theo dõi tiến trình + Khóa học của nhóm**, test lại luồng đầy đủ: tham gia khóa → ôn tập → đạt → khóa `completed`, kỹ năng `known` — dự kiến 25/11 · thực tế __/__
- [ ] **7.4 Tạo Pull Request** — dự kiến 25/11 · thực tế __/__

---

## Checklist endpoint

| Method | Endpoint | GĐ | Code | Test | Review |
|---|---|---|---|---|---|
| GET | `/api/courses/{course_id}/review` | 3 | [ ] | [ ] | [ ] |
| POST | `/api/courses/{course_id}/review-attempts` | 4 | [ ] | [ ] | [ ] |
| GET | `/api/review-attempts/{attempt_id}` | 4 | [ ] | [ ] | [ ] |
| PATCH | `/api/review-attempts/{attempt_id}/answers` | 4 | [ ] | [ ] | [ ] |
| POST | `/api/review-attempts/{attempt_id}/submit` | 5 | [ ] | [ ] | [ ] |
| GET | `/api/me/review-history` | 6 | [ ] | [ ] | [ ] |
| GET | `/api/me/review-history/{attempt_id}` | 6 | [ ] | [ ] | [ ] |
| GET | `/api/admin/questions?skill_id=` | 2 (Q1) | [ ] | [ ] | [ ] |
| POST | `/api/admin/questions` | 2 (Q1) | [ ] | [ ] | [ ] |
| PATCH | `/api/admin/questions/{question_id}` | 2 (Q1) | [ ] | [ ] | [ ] |
| DELETE | `/api/admin/questions/{question_id}` | 2 (Q1) | [ ] | [ ] | [ ] |

## Câu hỏi cần chốt (BA chưa nói rõ)

| # | Câu hỏi | Cần trước GĐ | Trả lời | Ngày chốt |
|---|---|---|---|---|
| Q1 | Quản trị ngân hàng câu hỏi (FR-54) có thuộc phần của Tuấn không? README chưa ghi người phụ trách. | 2 | | |
| Q2 | Lưu 4 lựa chọn thế nào: 4 cột riêng hay một cột JSON? Đáp án đúng lưu dạng chỉ số (0–3) hay ký tự (A–D)? | 1 | | |
| Q3 | 20 câu không chia hết cho số kỹ năng, hoặc một kỹ năng thiếu câu — bù từ kỹ năng khác hay báo chưa sẵn sàng? | 4 | | |
| Q4 | Có xáo trộn thứ tự câu / lựa chọn mỗi lần làm không? | 4 | | |
| Q5 | Bài đang làm dở có hết hạn không? | 4 | | |
| Q6 | Truy cập bài của người khác trả 403 hay 404? | 4 | | |
| Q7 | Phần trăm làm tròn thế nào (12/20 = 60% đạt; 11.9 câu không xảy ra, nhưng khi tổng câu khác 20?) | 5 | | |
| Q8 | Gửi email thất bại thì kết quả bài vẫn lưu và báo thành công? | 5 | | |
| Q9 | Đã `completed` rồi làm lại và trượt — khóa có quay về `ongoing` không? | 5 | | |
| Q10 | Sửa/xóa câu hỏi đã nằm trong bài người dùng từng làm — lịch sử hiển thị thế nào? | 2, 6 | | |
| **A1** | (AI) "Kỹ năng đã học" = kỹ năng **của khóa đang ôn** hay **mọi kỹ năng trong hồ sơ**? — đề xuất: theo khóa | 0 | ⏳ hỏi thầy | |
| **A2** | (AI) Số câu, tỉ lệ trắc nghiệm / tự luận? — đề xuất: 20 câu = 16 TN + 4 TL | 0 | ⏳ hỏi thầy | |
| **A3** | (AI) Tự luận AI chấm có tính vào điều kiện Đạt? — đề xuất: có (mỗi câu 1 điểm, TL = điểm AI/10) | 0 | ⏳ hỏi thầy | |
| **A4** | (AI) LLM nào: API (Gemini/OpenAI/Claude…) hay Qwen3-1.7B cục bộ? Ai cấp API key? — đề xuất: API + mock | 1 | ⏳ hỏi thầy | |
| **A5** | (AI) Câu AI sinh có cần Admin duyệt? — đề xuất: không, validator tự động | 2 | ⏳ hỏi thầy | |
| **A6** | (AI) AI lỗi/chậm → dùng ngân hàng câu hỏi dự phòng? — đề xuất: có | 4 | ⏳ hỏi thầy | |
| **A7** | (AI) Kho vector: pgvector hay bảng thường + cosine bằng Python? — đề xuất: bảng thường | 1 | ⏳ hỏi thầy | |
| **A8** | (AI) Nguồn tri thức RAG: soạn tài liệu ngắn theo kỹ năng hay chỉ mô tả khóa học? — đề xuất: soạn tài liệu cho 1–2 khóa demo | 1 | ⏳ hỏi thầy | |
| **A9** | (AI) Giữ hạn 25/11 (thu hẹp) hay lùi hạn 4–5 ngày? | 0 | ⏳ hỏi thầy | |
| **A10** | (Chấm) Tự luận **chấm theo từng ý đáp án** — đúng ý nào được điểm ý đó (3–5 ý/câu, tổng 10; đạt / ½ / 0; AI trích bằng chứng)? — **Tuấn chọn cách này** (thay khung C1–C4) | 5 | ⏳ hỏi thầy | |
| **A11** | (Chấm) Tổng điểm PA A (mỗi câu 1đ) / B (TN 60% + TL 40%) / C (TL chỉ nhận xét)? — đề xuất: A | 5 | ⏳ hỏi thầy | |
| **A12** | (Chấm) Trừ điểm khi chọn sai trắc nghiệm? — đề xuất: không | 5 | ⏳ hỏi thầy | |
| **A13** | (Chấm) Tỉ lệ TN Nhận biết / Thông hiểu / Vận dụng? — đề xuất: 40/40/20 | 4 | ⏳ hỏi thầy | |

## Nhật ký

| Ngày | Đã làm | Vướng mắc |
|---|---|---|
| 06/11 | Thầy bổ sung yêu cầu AI sinh câu hỏi (system prompt + RAG, trắc nghiệm + tự luận); viết đề xuất `docs/De-xuat-AI-On-tap.md` | Chờ thầy trả lời A1–A9 trước khi viết lại kế hoạch |
| 06/11 | Đề xuất tiêu chí chấm trắc nghiệm + tự luận (Phụ lục A trong đề xuất); thêm A10–A13 | **Hẹn thảo luận sâu phần Ôn tập ngày 09/11** |
| 06/11 | Tuấn chốt hướng: **tự luận chấm theo từng ý đáp án** (đúng ý nào được điểm ý đó) — cập nhật Phụ lục A2 | Chờ thầy xác nhận (A10) |
| | | |
