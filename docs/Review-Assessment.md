# Review-Assessment — Kế hoạch module Ôn tập & Đánh giá kiến thức dùng AI (F09)

> Người thực hiện: **Tuấn** · Người review: **Claude** · Bắt đầu: **09/11/2026** · Lõi module xong: **13/11/2026** · Hạn cuối: **25/11/2026**
> Căn cứ: yêu cầu của thầy 06/11 (AI sinh câu hỏi bằng **system prompt + RAG**, trắc nghiệm + tự luận); **buổi họp 09/11** (`BA-nhom/Cau-hoi-hop-thay-09-11-On-tap-AI_da-chot-v2.docx`); `EdumentorAi_BA_v3.md` — UC-09, FR-24 → FR-29, BR-04 (FR-24/25/26 **cần cập nhật** theo quyết định bên dưới); đề xuất `docs/De-xuat-AI-On-tap.md`.
> Công nghệ: backend **FastAPI + SQLAlchemy 2 (sync) + PostgreSQL**, bảng tạo bằng `create_all()` khi khởi động (repo **không dùng migration Alembic** — `alembic/versions` rỗng); frontend **React 18 + Vite 6**, CSS Modules theo thư mục tính năng (`SetUp-CSS.md`).
> Dùng lại từ module 01: `get_current_user`, `require_admin`, `core/email.py`, hook `user_skill_service.mark_known(..., source="review")`.
> Chuẩn giao diện: bộ demo `docs/EduMentor-UI-design/ui-design/` (ReviewStart, ReviewQuiz, ReviewResult, ReviewHistory, ReviewDetail).
> Cách dùng: làm xong việc nào thì tích `[x]` và điền **ngày thực tế**. Hết mỗi giai đoạn, nhắn "review GĐ x — Assessment" để Claude review. Ký hiệu: 👤 Tuấn làm · 🤖 Claude làm.

---

## Tổng quan tiến độ

| GĐ | Nội dung | Dự kiến | Thực tế bắt đầu | Thực tế xong | Xong |
|---|---|---|---|---|---|
| 0 | Chuẩn bị: đặc tả, khóa demo, phối hợp nhóm, fixture admin | 09/11 → 09/11 | 09/11 | __/__ | [ ] |
| 1 | Bảng dữ liệu + ngân hàng câu hỏi khóa 312 (bước 1: 40 câu) | 10/11 → 10/11 | __/__ | __/__ | [ ] |
| 2 | Sinh đề (embedding, RAG, AI mock, validator, khung đề) + API làm bài | 11/11 → 11/11 | __/__ | __/__ | [ ] |
| 3 | Chấm điểm, Hoàn thành khóa + kỹ năng, email, lịch sử, API debug, test | 12/11 → 12/11 | __/__ | __/__ | [ ] |
| 4 | Frontend 09 bản gọn + demo đầu–cuối | 13/11 → 13/11 | __/__ | __/__ | [ ] |
| 5 | Mở rộng: AI thật, ngân hàng bước 2, khóa 37, BA/SRS, làm đẹp UI | 14/11 → 18/11 | __/__ | __/__ | [ ] |
| 6 | Tích hợp với nhóm, kiểm thử thủ công, tập demo, PR | 19/11 → 25/11 | __/__ | __/__ | [ ] |

---

## Quyết định đã chốt (09/11/2026)

### Đề ôn tập
| # | Quyết định |
|---|---|
| A1 | Câu hỏi lấy từ **kỹ năng của khóa đang ôn**. Mỗi kỹ năng có **≥ 1 câu trắc nghiệm** (khóa > 12 kỹ năng → luân phiên giữa các lượt); 3 câu tự luận ưu tiên **3 kỹ năng khác nhau**; trong từng nhóm câu bốc **ngẫu nhiên**, tránh câu của lượt trước; **xáo** thứ tự câu và thứ tự đáp án. |
| A2, A13 | **15 câu = 12 trắc nghiệm (6 Nhận biết + 6 Thông hiểu) + 3 tự luận (Vận dụng)**. |
| A10, A11 | **Thang 10** = TN 12 × 0,5 = **6đ** + TL **4đ** = **2 câu dễ** (barem 2–3 ý, **1đ/câu**) + **1 câu nâng cao** (barem 4–5 ý, **2đ**). Mỗi câu tự luận chấm theo ý trên /10 rồi quy đổi về điểm câu. Loại câu (dễ / nâng cao) xác định bằng **số ý trong barem**. |
| A3, A12 | Tự luận **tính vào** điều kiện Đạt. **Không trừ điểm** khi chọn sai. **Đạt ≥ 6/10**; câu bỏ trống = 0. |
| — | **Khóa demo:** chính là **312 · Python Basics: Selection and Iteration** (Computer Science, Python Programming, Iteration, variable, Conditionals — "Computer Science" dùng câu tổng quát). Khóa thứ 2 (14–18/11): **37 · Introduction to HTML, CSS, & JavaScript**, bỏ kỹ năng "Web" (nhờ Khôi/Hòa gỡ khỏi `course_skill`). |
| — | **Ngân hàng câu hỏi — mục tiêu 20 câu/kỹ năng** (14 TN: 7 NB + 7 TH; 6 TL; toàn khóa TL dễ : nâng cao = 6 : 4). **Bước 1** (10/11): khóa 312 soạn tay **8 câu/kỹ năng = 40 câu** (30 TN + 10 TL). **Bước 2** (14–18/11): khóa 312 đủ **100 câu** (70 TN + 30 TL) + khóa 37. **Bước 3** (AI thật): kỹ năng còn thiếu câu thì AI sinh, qua validator thì **lưu vào ngân hàng** dùng chung; đủ 20 câu thì ngừng sinh; tùy chọn sinh trước cho ~448 kỹ năng phổ biến (≥ 5 khóa). Hệ thống có 5.893 kỹ năng — không soạn tay toàn bộ. Khóa chưa có câu (giai đoạn mock) → **"Chưa có đề ôn tập"**. |

### AI và dữ liệu
| # | Quyết định |
|---|---|
| A4, A7, A8 | **Giai đoạn 1: `AI_MODE=mock` (0 đồng)**, nhưng **đi đủ pipeline thật**: RAG truy xuất đoạn tri thức (cosine) → dựng prompt thật → mock trả câu hỏi **gắn với các đoạn vừa truy xuất** → validator + sinh lại (≤ 2 lần) + ngân hàng dự phòng chạy thật. Mỗi lượt **lưu vết** đoạn tri thức + prompt; xem qua **API debug chỉ admin**. Embedding **tính sẵn offline** (sentence-transformers, script riêng); backend chỉ đọc vector và tính cosine (không cài torch). Tài liệu tri thức nhóm tự soạn theo kỹ năng. **Giai đoạn 2** (khi mock ổn): thêm `RealAI` dùng API key miễn phí (chỉ trong `.env`), đổi `AI_MODE=real` để test. **Test tự động luôn chạy mock.** |
| A5, A6 | Không cần admin duyệt câu AI sinh (validator tự kiểm tra). Có **ngân hàng dự phòng**. |

### Chấm điểm
| # | Quyết định |
|---|---|
| H1 | Code chấm trắc nghiệm (so đáp án); "AI" chấm **từng** câu tự luận riêng. |
| T1 | **Chấm ngay khi nộp** (chờ tối đa ~20 giây); quá thời gian → trạng thái "đang chấm", không báo đạt/sai. |
| A10 mock | Mỗi ý barem có **từ khóa chính** + **từ khóa phụ**. **Đạt** = có từ khóa chính **cùng câu** với chủ thể; **một phần (½)** = chỉ có từ khóa phụ, hoặc từ khóa chính nằm ở câu khác; **0** = không có. Chuẩn hóa chữ thường + bỏ dấu trước khi so. Lưu **câu khớp làm bằng chứng**. Bài chỉ liệt kê từ khóa / quá ngắn → tối đa "một phần". (Hạn chế của mock — giai đoạn 2 AI chấm theo ngữ nghĩa.) |

### Khóa học và kỹ năng
| # | Quyết định |
|---|---|
| B1 | Khóa **chỉ "Hoàn thành" khi đạt ôn tập**; không có chức năng tự đánh dấu hoàn thành (trả lời S8: không). Lần đạt **đầu tiên**: khóa Hoàn thành + **mọi** kỹ năng của khóa thành "Đã biết" (`source="review"`), **kể cả kỹ năng người dùng đã tự gỡ** (6b) — **cùng một lần commit**. |
| B2 | Ôn lại khóa đã Hoàn thành: **chỉ lưu lịch sử**; không đổi trạng thái khóa, không cập nhật kỹ năng. |
| — | Chưa đạt: làm lại **không giới hạn**, mỗi lượt một đề mới. Mỗi người dùng + khóa có **tối đa 1 lượt đang làm**. |
| 6a | Đổi trạng thái khóa qua **hàm Hòa cung cấp**: `mark_course_completed(db, user_id, course_id)` (chỉ flush) + `get_enrollment_status(db, user_id, course_id)`. Đã gửi: `BA-nhom/Gui-Hoa-On-tap-09-va-Khoa-hoc.md`. Hòa chưa kịp → dùng hàm giả để test. |

### Thời gian (A9)
Lõi module 09 làm **09 → 13/11** với khóa demo 312, `AI_MODE=mock`. Mở rộng **14 → 18/11**. Tích hợp với nhóm + tập demo: **19 → 25/11**.

---

## Cấu trúc file (module 09)

> Thư mục `app/ai/client.py`, `ai/validators.py`, `ai/prompts/tutor.py` là phần **chatbot của Tâm** — module 09 dùng **file riêng** dưới `ai/review/` và `ai/prompts/review.py` để không xung đột khi Tâm merge.

| File | Tầng | Việc | GĐ |
|---|---|---|---|
| `models/knowledge_chunk.py` | Model | Bảng đoạn tri thức theo kỹ năng + vector embedding (kho cho RAG) | 1 |
| `models/review_question.py` | Model | Bảng ngân hàng câu hỏi: kỹ năng, loại TN/TL, mức độ, 4 lựa chọn + đáp án / barem + từ khóa, nguồn bank/ai | 1 |
| `models/review_attempt.py` | Model | `ReviewAttempt` (lượt làm bài: trạng thái, điểm, đạt, vết RAG/prompt) + `ReviewAnswer` (từng câu: đã chọn/đã viết, điểm, bằng chứng từng ý) | 1 |
| `schemas/review.py` | Schema | Dữ liệu vào/ra API; đề **không có** đáp án, barem | 2, 3 |
| `repositories/review_repository.py` | Repository | Chỉ đọc/ghi DB: lấy câu theo kỹ năng, lượt đang làm dở, lưu câu trả lời | 2, 3 |
| `services/review_service.py` | Service | **Luồng chính** + **commit duy nhất**: bắt đầu → tạo đề → lưu bài → nộp → chấm → Hoàn thành + "Đã biết" → email | 2, 3 |
| `services/exam_builder.py` | Service | Ráp đề theo khung 6 NB + 6 TH + 2 dễ + 1 nâng cao (A1) | 2 |
| `services/review_grader.py` | Service | Chấm TN; chấm TL theo ý; quy đổi thang 10 | 3 |
| `services/rag_service.py` | Service | Từ kỹ năng → các đoạn tri thức gần nhất (cosine) | 2 |
| `ai/review/base.py` | AI | Khuôn chung: `generate_questions()`, `grade_essay()` | 2 |
| `ai/review/mock_ai.py` | AI | AI giả: bốc câu gắn với đoạn RAG; chấm từ khóa | 2, 3 |
| `ai/review/real_ai.py` | AI | AI thật gọi API (giai đoạn 2) — chọn bằng `AI_MODE` | 5 |
| `ai/review/validator.py` | AI | Kiểm tra kết quả AI; sai → sinh lại ≤ 2 lần → dự phòng | 2 |
| `ai/prompts/review.py` | AI | System prompt sinh đề + chấm tự luận | 2 |
| `routers/v1/endpoints/review.py` | Router | Các API (bảng dưới), kiểm tra đăng nhập / quyền | 2, 3 |
| `scripts/build_embeddings.py` | Script (chạy tay) | Tính vector một lần rồi ghi DB (server không cần torch) | 2 |
| `scripts/seed_review.py` | Script (chạy tay) | Nạp ngân hàng + tài liệu tri thức đã duyệt từ JSON; chạy lại không trùng | 1 |
| `data/review/course_312.json` | Dữ liệu | Ngân hàng + tài liệu tri thức khóa 312 **đã duyệt** | 1 |

---

## Màn hình và API

| Màn demo | Route | Trang (file) | API | GĐ |
|---|---|---|---|---|
| ReviewStart | `/courses/:courseId/review` | `features/review/pages/ReviewStartPage.jsx` | `GET /api/courses/{course_id}/review`, `POST /api/courses/{course_id}/review-attempts` | 2, 4 |
| ReviewQuiz | `/review/:attemptId` | `features/review/pages/ReviewQuizPage.jsx` | `GET /api/review-attempts/{attempt_id}`, `PATCH /api/review-attempts/{attempt_id}/answers`, `POST /api/review-attempts/{attempt_id}/submit` | 2, 3, 4 |
| ReviewResult, ReviewDetail | `/review/:attemptId/result` | `features/review/pages/ReviewResultPage.jsx` | `GET /api/me/review-history/{attempt_id}` | 3, 4 |
| ReviewHistory | `/me/review-history` | `features/review/pages/ReviewHistoryPage.jsx` | `GET /api/me/review-history` | 3, 4 |
| (admin, không có màn) | — | — | `GET /api/admin/review-attempts/{attempt_id}/trace` | 3 |
| (tự động) | — | `api/review.api.js` | mỗi API một hàm | 4 |

---

## GĐ0 — Chuẩn bị (09/11)

- [x] **0.1 Viết lại tài liệu này** theo quyết định 09/11 — dự kiến 09/11 · thực tế 09/11 🤖
- [ ] **0.2 Commit `docs/Review-Assessment.md`** — dự kiến 09/11 · thực tế __/__ 🤖
- [ ] **0.3 Gửi Hòa** `BA-nhom/Gui-Hoa-On-tap-09-va-Khoa-hoc.md` — dự kiến 09/11 · thực tế __/__ 👤
  - Nhận lại: tên bảng / cột / giá trị trạng thái đăng ký khóa; hạn có `mark_course_completed`, `get_enrollment_status`.
- [x] **0.4 Chọn khóa demo** — **312** (37 làm khóa thứ 2) — thực tế 09/11
- [ ] **0.5 Đối chiếu khóa 312 trong DB thật** — dự kiến 09/11 · thực tế __/__ 👤 bật Docker · 🤖 kiểm tra
  - ✅ Xong khi: `course_id` = 312 đúng tên khóa, có đủ 5 kỹ năng, ghi lại 5 `skill_id`.
- [ ] **0.6 Duyệt cấu trúc file** (bảng "Cấu trúc file" ở trên) — dự kiến 09/11 · thực tế __/__ 👤
- [ ] **0.7 Fixture `admin_headers`** trong `tests/conftest.py` (chỉ **thêm**, không sửa fixture cũ) — dự kiến 09/11 · thực tế __/__ 🤖
  - ✅ Xong khi: `pytest` chạy hết, không test nào đỏ.

## GĐ1 — Bảng dữ liệu + ngân hàng câu hỏi (10/11)

- [ ] **1.1 Model `KnowledgeChunk`** — `chunk_id`, `skill_id` (FK), nội dung, `embedding` (mảng số thực, cột JSON), `created_at` — dự kiến 10/11 · thực tế __/__ 🤖
- [ ] **1.2 Model `ReviewQuestion`** — `question_id`, `skill_id`, `chunk_id`, `type` (`mcq` / `essay`), `level` (`recognize` / `understand` cho TN; `easy` / `advanced` cho TL), nội dung, `options` (4 lựa chọn, JSON) + `correct_index` 0–3 (TN), `rubric` (TL: danh sách ý `{text, max_points, main_keywords, sub_keywords}`), giải thích, `source` (`bank` / `ai`), `is_active`, `created_at` — dự kiến 10/11 · thực tế __/__ 🤖
  - CHECK: `type` và `level` khớp nhau; TN có `correct_index`; TL có `rubric`.
- [ ] **1.3 Model `ReviewAttempt`** — `attempt_id`, `user_id`, `course_id`, `status` (`in_progress` / `grading` / `graded`), `score` (0–10), `passed`, `is_first_pass`, `trace` (đoạn tri thức + prompt), `started_at`, `submitted_at` — dự kiến 10/11 · thực tế __/__ 🤖
  - Ràng buộc: mỗi `user_id` + `course_id` có **tối đa 1** lượt `in_progress` (unique index có điều kiện).
- [ ] **1.4 Model `ReviewAnswer`** — `attempt_id`, `question_id`, thứ tự câu (1–15), thứ tự đáp án đã xáo, `selected_index` (TN), `text_answer` (TL), `points`, `rubric_result` (mỗi ý: đạt / một phần / 0 + câu bằng chứng) — dự kiến 10/11 · thực tế __/__ 🤖
- [ ] **1.5 Đăng ký model** trong `models/__init__.py` (khối "Model của Tuấn") → khởi động lại server — dự kiến 10/11 · thực tế __/__ 🤖
  - ✅ Xong khi: thấy 4 bảng mới trong pgAdmin.
- [ ] **1.6 Cấu hình** `core/config.py` + `.env.example`: `AI_MODE=mock`, `REVIEW_PASS_SCORE=6`, `REVIEW_GRADING_TIMEOUT=20`, `AI_API_KEY=` (để trống), **có giá trị mặc định**, không ghi cứng trong code — dự kiến 10/11 · thực tế __/__ 🤖
- [ ] **1.7 Soạn nháp ngân hàng bước 1 khóa 312** → xuất ra `BA-nhom` (Word để đọc + JSON để nạp) — dự kiến 10/11 · thực tế __/__ 🤖
  - Tài liệu tri thức: 3–4 đoạn/kỹ năng (~15 đoạn).
  - 40 câu: 5 kỹ năng × 6 TN (3 NB + 3 TH) = 30 TN; 10 TL = 6 dễ + 4 nâng cao, có barem + từ khóa chính/phụ.
- [ ] **1.8 Duyệt 40 câu** — sửa đáp án, barem, từ khóa — dự kiến 10/11 · thực tế __/__ 👤
- [ ] **1.9 `scripts/seed_review.py`** nạp `data/review/course_312.json` (bản đã duyệt) — dự kiến 10/11 · thực tế __/__ 🤖
  - ✅ Xong khi: DB có 40 câu + ~15 đoạn; chạy lại lần 2 không bị trùng.
- [ ] **1.10 Nhờ Claude review GĐ1** — dự kiến 10/11 · thực tế __/__

## GĐ2 — Sinh đề và làm bài (11/11)

- [ ] **2.1 `scripts/build_embeddings.py`** — chạy trên máy (sentence-transformers), ghi vector vào `knowledge_chunks` — dự kiến 11/11 · thực tế __/__ 🤖 viết · 👤 chạy
  - ✅ Xong khi: mọi đoạn có `embedding`; backend **không** cần cài sentence-transformers.
- [ ] **2.2 `services/rag_service.py`** — theo kỹ năng → các đoạn có cosine cao nhất — dự kiến 11/11 · thực tế __/__ 🤖
  - ✅ Xong khi: test hỏi "Iteration" ra đoạn về vòng lặp.
- [ ] **2.3 `ai/review/base.py` + `mock_ai.py` + `ai/prompts/review.py`** — dựng system prompt + ngữ cảnh thật; mock trả câu gắn với đoạn đã truy xuất; chọn bằng `AI_MODE` — dự kiến 11/11 · thực tế __/__ 🤖
- [ ] **2.4 `ai/review/validator.py`** — đúng JSON, 4 lựa chọn, 1 đáp án, không trùng câu, barem đúng số ý → lỗi thì sinh lại ≤ 2 lần → vẫn lỗi thì ngân hàng dự phòng — dự kiến 11/11 · thực tế __/__ 🤖
  - ✅ Xong khi: test cho mock cố tình trả JSON lỗi → rơi về dự phòng.
- [ ] **2.5 `services/exam_builder.py`** — khung 6 NB + 6 TH + 2 dễ + 1 nâng cao; mỗi kỹ năng ≥ 1 TN; TL ưu tiên 3 kỹ năng; tránh câu lượt trước; xáo câu và đáp án — **viết test trước khi gắn API** — dự kiến 11/11 · thực tế __/__ 🤖
  - ✅ Xong khi: test chạy 100 lần, đề nào cũng đúng khung.
- [ ] **2.6 `GET /api/courses/{course_id}/review`** — kỹ năng của khóa, cấu trúc đề, ngưỡng đạt, lượt dở, các lượt trước, **lý do chưa thể ôn**: chưa đăng ký / đã bỏ khóa / "Chưa có đề ôn tập" — dự kiến 11/11 · thực tế __/__ 🤖
- [ ] **2.7 `POST /api/courses/{course_id}/review-attempts`** — có lượt dở thì **trả lại lượt đó**, không thì sinh đề mới + lưu vết — dự kiến 11/11 · thực tế __/__ 🤖
- [ ] **2.8 `GET /api/review-attempts/{attempt_id}`** — câu hỏi + câu trả lời đã lưu, **không lộ đáp án, barem, giải thích** — dự kiến 11/11 · thực tế __/__ 🤖
- [ ] **2.9 `PATCH /api/review-attempts/{attempt_id}/answers`** — lưu khi Tạm rời (FR-29); lượt đã nộp thì không cho sửa — dự kiến 11/11 · thực tế __/__ 🤖
- [ ] **2.10 Quyền sở hữu** — người khác mở `attempt_id` → **404** (BR-01, NFR-06) — dự kiến 11/11 · thực tế __/__ 🤖
- [ ] **2.11 Thử tay trên Swagger** đủ luồng bắt đầu → lấy đề → lưu → làm tiếp — dự kiến 11/11 · thực tế __/__ 👤
- [ ] **2.12 Nhờ Claude review GĐ2** — dự kiến 11/11 · thực tế __/__

## GĐ3 — Chấm điểm, Hoàn thành, test (12/11)

- [ ] **3.1 Chấm trắc nghiệm** (`review_grader.py`) — theo thứ tự đáp án đã xáo, 0,5đ/câu, bỏ trống = 0 — dự kiến 12/11 · thực tế __/__ 🤖
- [ ] **3.2 Chấm tự luận bằng từ khóa** (`mock_ai.grade_essay`) — đạt / một phần / 0, bỏ dấu, lưu câu bằng chứng; chỉ liệt kê từ khóa / quá ngắn → tối đa một phần — dự kiến 12/11 · thực tế __/__ 🤖
  - ✅ Xong khi: test ví dụ list/tuple ra **7/10** (Y1 3 · Y2 3 · Y3 1 · Y4 0).
- [ ] **3.3 `POST /api/review-attempts/{attempt_id}/submit`** — quy đổi TL về 1đ / 2đ, tổng thang 10, **đạt ≥ `REVIEW_PASS_SCORE`**; nộp lần 2 → từ chối; quá `REVIEW_GRADING_TIMEOUT` → `grading` (T1) — dự kiến 12/11 · thực tế __/__ 🤖
  - ✅ Xong khi: test ví dụ tổng: TN 10/12 = 5; TL dễ 8/10 → 0,8; dễ 5/10 → 0,5; nâng cao 7/10 → 1,4 ⇒ **7,7 → Đạt**.
- [ ] **3.4 Đạt lần đầu — cùng một transaction** (B1, 6b) — dự kiến 12/11 · thực tế __/__ 🤖
  - Lưu kết quả → `mark_course_completed` (hàm của Hòa, **hoặc hàm giả** có TODO nối sau) → `user_skill_service.mark_known(..., source="review")` → **commit một lần**. Lỗi giữa chừng → rollback toàn bộ (FR-43).
  - Đã Hoàn thành rồi (B2) → chỉ lưu kết quả.
- [ ] **3.5 Email kết quả** (`core/email.py`) — gửi **sau** commit; email lỗi không làm hỏng kết quả (ghi log) — dự kiến 12/11 · thực tế __/__ 🤖
- [ ] **3.6 `GET /api/me/review-history`** (lọc `course_id`, `passed`, phân trang) + **`GET /api/me/review-history/{attempt_id}`** (từng câu, đáp án đã chọn, đáp án đúng, điểm từng ý + bằng chứng, giải thích — chỉ lượt **đã nộp** của **chính mình**) — dự kiến 12/11 · thực tế __/__ 🤖
- [ ] **3.7 `GET /api/admin/review-attempts/{attempt_id}/trace`** (`require_admin`) — đoạn tri thức + prompt của lượt (A4) — dự kiến 12/11 · thực tế __/__ 🤖
  - ✅ Xong khi: student gọi → 403; admin (`admin_headers`) → 200.
- [ ] **3.8 Test đủ kịch bản** — dự kiến 12/11 · thực tế __/__ 🤖
  - Đúng ngưỡng 6,0 / dưới ngưỡng 5,9; bỏ trống; nộp lại; ôn lại sau Hoàn thành (B2); kỹ năng đã tự gỡ được thêm lại khi đạt lần đầu (6b); lỗi giữa transaction → không lưu gì; không dấu vẫn khớp từ khóa.
- [ ] **3.9 Chạy toàn bộ `pytest` + `ruff check .`** (black chỉ file của mình) — dự kiến 12/11 · thực tế __/__ 🤖
- [ ] **3.10 Nhờ Claude review GĐ3** (giai đoạn quan trọng nhất) — dự kiến 12/11 · thực tế __/__

## GĐ4 — Frontend 09 + demo đầu–cuối (13/11)

> Bản gọn, đủ chức năng; hiệu ứng để GĐ5. Thư mục `features/review/` (pages, components, styles — theo `SetUp-CSS.md`), tái dùng `features/common`.

- [ ] **4.1 `api/review.api.js` + route** các trang (bảng "Màn hình và API") — dự kiến 13/11 · thực tế __/__ 🤖
- [ ] **4.2 `ReviewStartPage`** — cấu trúc đề, ngưỡng đạt, nút "Bắt đầu" / "Làm tiếp", lý do chưa thể ôn ("Chưa có đề ôn tập"…) — dự kiến 13/11 · thực tế __/__ 🤖
- [ ] **4.3 `ReviewQuizPage`** — 12 TN + 3 ô tự luận, lưu tạm, Tạm rời, Nộp bài (hỏi xác nhận) — dự kiến 13/11 · thực tế __/__ 🤖
- [ ] **4.4 `ReviewResultPage`** — điểm, đạt / chưa đạt, từng câu, điểm từng ý + bằng chứng; trạng thái "đang chấm" — dự kiến 13/11 · thực tế __/__ 🤖
- [ ] **4.5 `ReviewHistoryPage`** — dự kiến 13/11 · thực tế __/__ 🤖
- [ ] **4.6 Demo đầu–cuối** — đăng ký khóa 312 → ôn tập → đạt → khóa Hoàn thành, hồ sơ có 5 kỹ năng "Đã biết" — dự kiến 13/11 · thực tế __/__ 👤 + 🤖
  - ✅ Xong khi: chạy trọn không lỗi → **commit + push**.

## GĐ5 — Mở rộng (14/11 → 18/11)

- [ ] **5.1 `ai/review/real_ai.py`** (giai đoạn 2): API key miễn phí trong `.env`, `AI_MODE=real`, thử trên khóa 312; lỗi / hết lượt → dự phòng — thực tế __/__
  - Ngân hàng bước 3: kỹ năng thiếu câu → AI sinh → validator → lưu `source="ai"`; đủ 20 câu/kỹ năng thì ngừng sinh.
- [ ] **5.2 Ngân hàng bước 2**: khóa 312 đủ 100 câu (70 TN + 30 TL); khóa 37 (sau khi gỡ "Web") — thực tế __/__
- [ ] **5.3 Cập nhật BA/SRS** FR-24/25/26 theo quyết định 09/11 — thực tế __/__
- [ ] **5.4 Làm đẹp giao diện 09** (theo phong cách module 01) — thực tế __/__
- [ ] **5.5 Nghiên cứu lại kho vector** (A7 — có thể chuyển pgvector) — thực tế __/__

## GĐ6 — Tích hợp và hoàn thiện (19/11 → 25/11)

- [ ] **6.1 Nối hàm thật của Hòa** (thay hàm giả), test luồng đầy đủ với module khóa học — thực tế __/__
- [ ] **6.2 Kiểm thử thủ công** theo bảng dưới — thực tế __/__
- [ ] **6.3 Rà bảo mật**: không lộ đáp án / barem trước khi nộp; không xem được bài người khác; API debug chặn student; API key không nằm trong repo — thực tế __/__
- [ ] **6.4 Tập demo + tạo Pull Request** — thực tế __/__

---

## Bảng kiểm thử thủ công

| # | Thao tác | Mong đợi | GĐ | Đạt |
|---|---|---|---|---|
| R1 | Vào trang ôn tập khóa **chưa đăng ký** | Báo chưa thể ôn, không có nút Bắt đầu | 2, 4 | [ ] |
| R2 | Vào trang ôn tập khóa **không có ngân hàng** | "Chưa có đề ôn tập" | 2, 4 | [ ] |
| R3 | Bắt đầu ôn khóa 312 | Đề 15 câu: 12 TN + 3 TL, đủ 5 kỹ năng | 2, 4 | [ ] |
| R4 | Làm 5 câu → Tạm rời → vào lại | "Làm tiếp", 5 câu vẫn còn | 2, 4 | [ ] |
| R5 | Mở `F12` → xem response lấy đề | Không có đáp án, barem, giải thích | 2 | [ ] |
| R6 | Đăng nhập tài khoản khác, mở link bài của người kia | 404 | 2 | [ ] |
| R7 | Nộp bài đạt (≥ 6) | Kết quả Đạt; khóa Hoàn thành; hồ sơ có 5 kỹ năng "Đã biết"; có email | 3, 4 | [ ] |
| R8 | Nộp bài chưa đạt → làm lại | Đề mới, không trùng câu lượt trước; khóa vẫn đang học | 3, 4 | [ ] |
| R9 | Gỡ 1 kỹ năng của khóa khỏi hồ sơ → làm đạt lần đầu | Kỹ năng đó quay lại "Đã biết" (6b) | 3 | [ ] |
| R10 | Khóa đã Hoàn thành → ôn lại (đạt hoặc trượt) | Chỉ thêm lịch sử; khóa và kỹ năng không đổi (B2) | 3 | [ ] |
| R11 | Viết tự luận không dấu ("list thay doi duoc") | Vẫn chấm đúng ý | 3 | [ ] |
| R12 | Tự luận chỉ liệt kê từ khóa ("list tuple mutable") | Tối đa "một phần" | 3 | [ ] |
| R13 | Bấm Nộp 2 lần liên tiếp | Lần 2 bị từ chối, điểm không đổi | 3 | [ ] |
| R14 | Student gọi API debug trace | 403 | 3 | [ ] |
| R15 | Lịch sử ôn tập → mở 1 lượt | Từng câu, đáp án đúng, điểm từng ý + bằng chứng | 3, 4 | [ ] |

---

## Câu hỏi cần chốt

| # | Câu hỏi | Cần trước GĐ | Đề xuất | Trả lời | Ngày chốt |
|---|---|---|---|---|---|
| Q1 | Quản trị ngân hàng câu hỏi qua API (FR-54)? | 5 | Không làm ở giai đoạn này — ngân hàng nạp từ seed đã duyệt; câu AI sinh tự vào sau validator (A5) | Không làm | 09/11 |
| Q2 | Lưu 4 lựa chọn: 4 cột hay JSON? Đáp án dạng chỉ số hay ký tự? | 1 | `options` JSON + `correct_index` 0–3 | | |
| Q3 | Chia câu khi không chia hết số kỹ năng / kỹ năng thiếu câu | 2 | Theo A1 | Theo A1 | 09/11 |
| Q4 | Xáo thứ tự câu / lựa chọn? | 2 | Có | Có (A1) | 09/11 |
| Q5 | Lượt làm dở có hết hạn không? | 2 | Không hết hạn | | |
| Q6 | Mở bài của người khác: 403 hay 404? | 2 | 404 (không lộ bài có tồn tại) | | |
| Q7 | Làm tròn điểm | 3 | Lưu 2 chữ số thập phân; so ngưỡng trên số chưa làm tròn | | |
| Q8 | Email lỗi thì kết quả vẫn lưu và báo thành công? | 3 | Có, ghi log lỗi email | | |
| Q9 | Đã Hoàn thành, ôn lại và trượt → khóa quay về đang học? | 3 | Không | Không (B2) | 09/11 |
| Q10 | Câu hỏi bị sửa / tắt sau khi đã nằm trong bài cũ | 3 | Tắt bằng `is_active=false`, không xóa; lịch sử đọc theo câu gốc | | |
| Q11 | Khóa demo chính? | 0 | 312 | 312 chính, 37 thứ 2 | 09/11 |
| Q12 | Tên bảng / cột / giá trị trạng thái đăng ký khóa (Hòa) | 3 | — | Chờ Hòa | |
| Q13 | Bảng tạo bằng `create_all()` hay migration Alembic? | 1 | `create_all()` như các bảng hiện có (repo chưa có migration nào) | | |

## Nhật ký

| Ngày | Đã làm | Vướng mắc |
|---|---|---|
| 06/11 | Thầy bổ sung yêu cầu AI sinh câu hỏi (system prompt + RAG, trắc nghiệm + tự luận); viết đề xuất `docs/De-xuat-AI-On-tap.md` | Chờ thầy trả lời A1–A9 |
| 06/11 | Đề xuất tiêu chí chấm (Phụ lục A); thêm A10–A13; Tuấn chọn chấm tự luận theo từng ý | Hẹn thảo luận 09/11 |
| 09/11 | Họp thầy: chốt A1–A13, H1, T1, B1, B2. Thảo luận tiếp với Claude: thang 10 (TN 6 + TL 2 dễ × 1 + 1 nâng cao × 2), khung đề + random, mock đi đủ pipeline → API thật sau, chấm từ khóa (a), lịch 09–13/11, 6a (hàm của Hòa), 6b (đạt lần đầu thêm lại kỹ năng đã gỡ), làm lại không giới hạn. Gửi Hòa đặc tả phối hợp | Chờ Hòa trả lời |
| 09/11 | Chốt khóa demo 312 (37 làm khóa thứ 2). Chốt ngân hàng 3 bước, mục tiêu 20 câu/kỹ năng. Viết lại kế hoạch theo khung `Review-Frontend-Auth.md`: cấu trúc file, màn hình/API, GĐ0–GĐ6, bảng kiểm thử R1–R15. Phát hiện: repo dùng `create_all()` (không migration); `ai/client.py`, `ai/validators.py` là của chatbot Tâm → module 09 dùng `ai/review/` | Tâm chưa merge chatbot — không đụng nhánh Tâm |
| | | |
