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
| `services/course_gateway.py` | Service | Cổng sang module Khóa học của Hòa (`get_enrollment_status`, `mark_course_completed`) — **hàm giả** tới khi Hòa có hàm thật | 2, 3 |
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
- [x] **0.2 Commit `docs/Review-Assessment.md`** — dự kiến 09/11 · thực tế 09/11 🤖 (`7abdb47`)
- [x] **0.3 Gửi Hòa** `BA-nhom/Gui-Hoa-On-tap-09-va-Khoa-hoc.md` — dự kiến 09/11 · thực tế 09/11 👤 — **đã gửi, chờ Hòa xác nhận**
  - Nhận lại: tên bảng / cột / giá trị trạng thái đăng ký khóa; hạn có `mark_course_completed`, `get_enrollment_status`.
- [x] **0.4 Chọn khóa demo** — **312** (37 làm khóa thứ 2) — thực tế 09/11
- [x] **0.5 Đối chiếu khóa 312 trong DB thật** — dự kiến 09/11 · thực tế 09/11 👤 bật Docker · 🤖 kiểm tra
  - ✅ Khớp: `course_id` 312 = "Python Basics: Selection and Iteration" (beginner); 5 kỹ năng đều `is_active`: **167** Python Programming · **170** Computer Science · **400** Iteration · **769** variable (computer science) · **770** Conditionals (Computer Science). DB có 5.893 kỹ năng, 4.509 khóa (khớp `datajson/`).
- [x] **0.6 Duyệt cấu trúc file** (bảng "Cấu trúc file" ở trên) — dự kiến 09/11 · thực tế 09/11 👤 Tuấn chốt
- [x] **0.7 Fixture `admin_headers`** trong `tests/conftest.py` (chỉ **thêm**, không sửa fixture cũ) — dự kiến 09/11 · thực tế 09/11 🤖
  - ✅ Đã có `admin_headers` (tạo bằng `scripts.create_admin`) + `student_headers` (đăng ký qua API, để test 403); đăng nhập thật qua `/api/auth/login`. Test `tests/test_auth_fixtures.py` 3/3; toàn bộ **114 passed**.

## GĐ1 — Bảng dữ liệu + ngân hàng câu hỏi (10/11)

- [x] **1.1 Model `KnowledgeChunk`** — `chunk_id`, `skill_id` (FK), nội dung, `embedding` (mảng số thực, cột JSON), `created_at` — dự kiến 10/11 · thực tế 09/11 🤖
- [x] **1.2 Model `ReviewQuestion`** — `question_id`, `skill_id`, `chunk_id`, `type` (`mcq` / `essay`), `level` (`recognize` / `understand` cho TN; `easy` / `advanced` cho TL), nội dung, `options` (4 lựa chọn, JSON) + `correct_index` 0–3 (TN), `rubric` (TL: danh sách ý `{text, max_points, main_keywords, sub_keywords}`), giải thích, `source` (`bank` / `ai`), `is_active`, `created_at` — dự kiến 10/11 · thực tế 09/11 🤖
  - CHECK: `type` và `level` khớp nhau; TN có `correct_index`; TL có `rubric`.
- [x] **1.3 Model `ReviewAttempt`** — `attempt_id`, `user_id`, `course_id`, `status` (`in_progress` / `grading` / `graded`), `score` (0–10), `passed`, `is_first_pass`, `trace` (đoạn tri thức + prompt), `started_at`, `submitted_at` — dự kiến 10/11 · thực tế 09/11 🤖
  - Ràng buộc: mỗi `user_id` + `course_id` có **tối đa 1** lượt `in_progress` (unique index có điều kiện).
- [x] **1.4 Model `ReviewAnswer`** — `attempt_id`, `question_id`, thứ tự câu (1–15), thứ tự đáp án đã xáo, `selected_index` (TN), `text_answer` (TL), `points`, `rubric_result` (mỗi ý: đạt / một phần / 0 + câu bằng chứng) — dự kiến 10/11 · thực tế 09/11 🤖
- [x] **1.5 Đăng ký model** trong `models/__init__.py` (khối "Model của Tuấn") → khởi động lại server — dự kiến 10/11 · thực tế 09/11 🤖
  - ✅ 4 bảng đã tạo trong PostgreSQL (`create_tables()`), có unique index có điều kiện `uq_review_attempts_one_in_progress`. Test ràng buộc `tests/test_review_models.py` 22/22; toàn bộ **136 passed**.
  - Sửa trong lúc test: cột JSON phải dùng `JSON(none_as_null=True)` — mặc định SQLAlchemy lưu `None` thành chuỗi JSON `'null'` làm CHECK "IS NOT NULL" bị lọt.
  - Thêm so với kế hoạch: cột `code` (mã duy nhất, cho seed chạy lại không trùng) ở `knowledge_chunks`, `review_questions`; `ReviewAnswer.max_points`, `updated_at`; câu hỏi đã nằm trong bài làm không xóa được (`RESTRICT`).
- [x] **1.6 Cấu hình** `core/config.py` + `.env.example`: `AI_MODE=mock`, `REVIEW_PASS_SCORE=6`, `REVIEW_GRADING_TIMEOUT=20`, `REVIEW_BANK_TARGET_PER_SKILL=20`; **dùng lại `LLM_API_KEY` / `LLM_MODEL`** (tên chung với chatbot của Tâm, mặc định rỗng → server vẫn chạy khi chưa có khóa) thay cho `AI_API_KEY` — dự kiến 10/11 · thực tế 09/11 🤖
- [x] **1.7 Ngân hàng bước 1 khóa 312** — `backend/data/review/course_312.json` — dự kiến 10/11 · thực tế 09/11 🤖
  - Tuấn chốt: **không xuất bản nháp ra BA-nhom**, viết thẳng vào repo; cần sửa câu nào thì báo.
  - 15 đoạn tri thức (3/kỹ năng) + 40 câu: 30 TN (mỗi kỹ năng 3 NB + 3 TH) + 10 TL (6 dễ + 4 nâng cao, barem + từ khóa chính/phụ). Đáp án đúng trải đều 4 vị trí.
  - Câu nâng cao `312-PY-TL-02` chính là ví dụ list/tuple ở mục 5 tài liệu họp (barem 3 + 3 + 2 + 2).
- [ ] **1.8 Duyệt 40 câu** — Tuấn đọc `course_312.json`, báo câu cần sửa → sửa file rồi chạy lại seed — thực tế __/__ 👤
- [x] **1.9 `scripts/seed_review.py`** — dự kiến 10/11 · thực tế 09/11 🤖
  - Kiểm tra trước, ghi sau: sai ở đâu in **tất cả** lỗi, không ghi gì; kỹ năng phải thuộc khóa (`course_skill`, chỉ đọc). Chạy lại: cập nhật theo `code`, không trùng; đổi nội dung đoạn → xóa embedding cũ; câu đã tắt giữ nguyên tắt.
  - ✅ DB thật: lần 1 `+15 đoạn / +40 câu`, lần 2 `cập nhật 15 / 40`. Test `tests/test_seed_review.py` 23/23; toàn bộ **159 passed**.
- [ ] **1.10 Nhờ Claude review GĐ1** — dự kiến 10/11 · thực tế __/__

## GĐ2 — Sinh đề và làm bài (11/11)

- [ ] **2.1 `scripts/build_embeddings.py`** — 🤖 đã viết 09/11 · 👤 **Tuấn chạy**: `python -m scripts.build_embeddings` (lần đầu tải mô hình ~470 MB) — thực tế __/__
  - Mô hình **đa ngôn ngữ** `paraphrase-multilingual-MiniLM-L12-v2` (`REVIEW_EMBEDDING_MODEL`) — mô hình `all-MiniLM-L6-v2` của Hòa chỉ hiểu tiếng Anh, tài liệu tri thức viết tiếng Việt.
  - ✅ Xong khi: 15 đoạn có `embedding`; lượt ôn mới có `score` trong trace.
- [x] **2.2 `services/rag_service.py`** — lọc theo kỹ năng → xếp cosine; vector câu truy vấn tính lúc chạy bằng mô hình **đã tải sẵn** (`local_files_only`); chưa có vector / mô hình → vẫn trả đoạn theo thứ tự tạo (không chặn ôn tập) — thực tế 09/11 🤖
  - Ghi chú: `sentence-transformers` đã có trong `requirements.txt` (nhóm dùng cho gợi ý lộ trình) nên backend nạp được mô hình cho câu truy vấn; đoạn tri thức vẫn tính sẵn offline.
- [x] **2.3 `ai/review/base.py` + `mock_ai.py` + `__init__.get_review_ai()` + `ai/prompts/review.py`** — thực tế 09/11 🤖
- [x] **2.4 `ai/review/validator.py`** — **dùng chung** cho ngân hàng soạn tay (`seed_review.py` đổi sang dùng file này) và câu AI sinh; sinh lại ≤ 2 lần → ngân hàng dự phòng; câu AI mới (giai đoạn 2) tự lưu `source='ai'` — thực tế 09/11 🤖
- [x] **2.5 `services/exam_builder.py`** — khung + **ưu tiên câu chưa dùng ở lượt trước** (`fresh`) — test chạy 100 lần mỗi kịch bản — thực tế 09/11 🤖
- [x] **2.6 `GET /api/courses/{course_id}/review`** — lý do chưa thể ôn: `not_enrolled` / `abandoned` / `no_question_bank` — thực tế 09/11 🤖
  - Trạng thái đăng ký đi qua `services/course_gateway.py` — **hàm giả** (coi như đang học) cho tới khi Hòa có hàm thật; chỉ sửa file này khi nối.
- [x] **2.7 `POST /api/courses/{course_id}/review-attempts`** — có lượt dở → `resumed=true`; bấm 2 lần cùng lúc → unique index chặn, trả lại lượt kia; chưa / bỏ khóa → 403; chưa có ngân hàng → 409 — thực tế 09/11 🤖
- [x] **2.8 `GET /api/review-attempts/{attempt_id}`** — không có `correct_index`, `rubric`, `explanation`, `question_id`, `option_order` — thực tế 09/11 🤖
- [x] **2.9 `PATCH /api/review-attempts/{attempt_id}/answers`** — gửi một phần; TN `selected_index` (null = bỏ chọn), TL `text_answer`; sai câu nào → 422, **không lưu câu nào**; đã nộp → 409 — thực tế 09/11 🤖
- [x] **2.10 Quyền sở hữu** — người khác (kể cả admin) → 404 — thực tế 09/11 🤖
  - ✅ Test: `test_exam_builder.py` (208), `test_review_ai.py` (11), `test_review_api.py` (26, chạy 5 lần liền đều đạt); toàn bộ **404 passed**. Chạy thử trên PostgreSQL thật bằng tài khoản test: đề 15 câu đúng khung, không lộ đáp án, lưu + làm tiếp đúng; đã xóa lượt thử.
- [ ] **2.11 Thử tay trên Swagger** đủ luồng bắt đầu → lấy đề → lưu → làm tiếp — dự kiến 11/11 · thực tế __/__ 👤
- [ ] **2.12 Nhờ Claude review GĐ2** — dự kiến 11/11 · thực tế __/__

## GĐ3 — Chấm điểm, Hoàn thành, test (12/11)

- [x] **3.1 Chấm trắc nghiệm** (`services/review_grader.py`) — đổi vị trí trên màn hình về lựa chọn gốc qua `option_order`; 0,5đ/câu; bỏ trống / sai = 0 — thực tế 09/11 🤖
- [x] **3.2 Chấm tự luận bằng từ khóa** (`ai/review/keyword_grader.py`, `MockAI.grade_essay`) — thực tế 09/11 🤖
  - Từ khóa chữ khớp **nguyên từ** ("for" ≠ "format"); tách câu không cắt "6.5", "a.append"; bài < 6 từ hoặc câu khớp < 3 từ → tối đa một phần.
  - AI lỗi / trả điểm sai quy tắc (`validator.grading_errors`) → chấm bằng từ khóa, ghi vào `trace.grading.keyword_fallback`.
  - Sửa barem `312-PY-TL-02` ý Y4: bỏ từ khóa phụ "ví dụ", "dùng" (bài làm mẫu bị cộng nhầm thành 8/10) → đúng **7/10** như ví dụ gửi thầy.
  - ✅ Test: ví dụ list/tuple ra 7/10 (có dấu và không dấu); đáp án mẫu của **cả 10 câu tự luận** trong ngân hàng đều đạt 10/10.
- [x] **3.3 `POST /api/review-attempts/{attempt_id}/submit`** — tổng thang 10, đạt khi ≥ `REVIEW_PASS_SCORE` (so trên tổng chưa làm tròn); nộp lần 2 → 409 — thực tế 09/11 🤖
  - Chưa làm: chờ quá `REVIEW_GRADING_TIMEOUT` → trạng thái `grading` (T1). Mock chấm tức thì nên chưa cần; làm cùng `RealAI` ở GĐ5.
- [x] **3.4 Đạt lần đầu — một transaction** — `mark_course_completed` (cổng, hàm giả) + `mark_known(source="review")` mọi kỹ năng của khóa (kể cả kỹ năng đã tự gỡ — 6b) → commit một lần; lỗi giữa chừng → rollback, bài vẫn đang làm, nộp lại được — thực tế 09/11 🤖
  - Chỉ khi trạng thái khóa là **đang học**; đã Hoàn thành (B2) / đã bỏ / chưa đăng ký → chỉ lưu kết quả.
- [x] **3.5 Email kết quả** — `core/email.send_review_result_email`, router gửi bằng `BackgroundTasks` **sau** khi trả kết quả (đã commit) — thực tế 09/11 🤖
- [x] **3.6 `GET /api/me/review-history`** (lọc `course_id`, `passed`, `page`, `size`) + **`GET /api/me/review-history/{attempt_id}`** (lượt đang làm → 404, chưa lộ đáp án) — thực tế 09/11 🤖
- [x] **3.7 `GET /api/admin/review-attempts/{attempt_id}/trace`** — student 403, admin 200 — thực tế 09/11 🤖
- [x] **3.8 Test đủ kịch bản** — `test_keyword_grader.py` (13), `test_review_submit.py` (19): 10/10 + Hoàn thành + kỹ năng, bỏ trống = 0, ngưỡng 6,0 / 5,5, ví dụ 7/10 → 1,4đ, đạt lần 2 chỉ lưu lịch sử, kỹ năng đã gỡ quay lại, lỗi giữa transaction, AI chấm lỗi → từ khóa, lịch sử + phân trang, quyền — thực tế 09/11 🤖
- [x] **3.9 Toàn bộ `pytest` + `ruff`** — **436 passed**; ruff sạch các file module 09 (B008 `Depends` giữ như module 01) — thực tế 09/11 🤖
  - Chạy thử PostgreSQL thật (tài khoản test): 9,4/10 Đạt (câu list/tuple 1,4đ), khóa Hoàn thành, 5 kỹ năng "Đã biết"; đã khôi phục hồ sơ + xóa lượt thử.
- [ ] **3.10 Nhờ Claude review GĐ3** (giai đoạn quan trọng nhất) — dự kiến 12/11 · thực tế __/__

## GĐ4 — Frontend 09 + demo đầu–cuối (13/11)

> Bản gọn, đủ chức năng; hiệu ứng để GĐ5. Thư mục `features/review/` (pages, components, styles — theo `SetUp-CSS.md`), tái dùng `features/common`.

- [x] **4.1 `api/review.api.js` + 4 route** (`routes/index.jsx`, đặt trên các route "Tạm thời chưa khả dụng") — thực tế 09/11 🤖
  - `nav.js`: thêm trường `match` + hàm `activeNavItem` → trang `/courses/:id/review`, `/review/...` tô sáng mục **Ôn tập** (trước đó tô nhầm "Khóa học"). Header dùng hàm này.
- [x] **4.2 `ReviewStartPage`** — cấu trúc đề, kỹ năng, 3 ô số liệu, lượt dở → "Tiếp tục bài đang làm", các lần trước, lý do chưa thể ôn — thực tế 09/11 🤖
- [x] **4.3 `ReviewQuizPage`** — bảng số câu (đã trả lời / chưa / đang xem, chấm xanh = tự luận); **tự lưu** (TN lưu ngay, TL sau 1 giây ngừng gõ, đổi câu / Tạm rời / Nộp → lưu nốt; lỗi → "Lưu lại"); đóng tab khi chưa lưu → trình duyệt hỏi; hộp xác nhận nộp (báo số câu bỏ trống) — thực tế 09/11 🤖
- [x] **4.4 `ReviewResultPage`** (gộp màn ReviewResult + ReviewDetail) — vòng điểm thang 10, Đạt / Chưa đạt, điểm TN / TL, báo Hoàn thành + kỹ năng; chi tiết từng câu: Bạn chọn / Đáp án đúng, bảng chấm từng ý + bằng chứng, lọc "Câu sai", ẩn / hiện tất cả giải thích — thực tế 09/11 🤖
- [x] **4.5 `ReviewHistoryPage`** — lọc khóa + kết quả (giữ trên URL), phân trang 10 dòng, Xem chi tiết / Làm lại; chưa có lượt nào → nút vào khóa demo 312 (`DEMO_COURSES` — bỏ khi "Khóa học của tôi" của Tâm có nút Ôn tập) — thực tế 09/11 🤖
- [x] **4.6 Demo đầu–cuối** (Chrome thật, tài khoản test) — thực tế 09/11 🤖
  - Header "Ôn tập" → Lịch sử (trống) → khóa 312 → Bắt đầu → trả lời 7 câu → Tạm rời → "Tiếp tục" (7 câu còn nguyên) → làm nốt + gõ 3 tự luận (DB lưu đủ 15) → Nộp → **9/10 Đạt**, khóa Hoàn thành, 5 kỹ năng "Đã biết" → Lịch sử có lượt mới. Khổ 375px: không tràn ngang. **Không có lỗi console.** `npm run build` OK. Đã dọn dữ liệu demo.
  - Sửa sau demo: chữ đậm trong dòng ghi chú bị tách khoảng (li dạng flex) → bọc chữ trong `<span>`.

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
| Q13 | Bảng tạo bằng `create_all()` hay migration Alembic? | 1 | `create_all()` như các bảng hiện có (repo chưa có migration nào) | `create_all()` | 09/11 |

## Nhật ký

| Ngày | Đã làm | Vướng mắc |
|---|---|---|
| 06/11 | Thầy bổ sung yêu cầu AI sinh câu hỏi (system prompt + RAG, trắc nghiệm + tự luận); viết đề xuất `docs/De-xuat-AI-On-tap.md` | Chờ thầy trả lời A1–A9 |
| 06/11 | Đề xuất tiêu chí chấm (Phụ lục A); thêm A10–A13; Tuấn chọn chấm tự luận theo từng ý | Hẹn thảo luận 09/11 |
| 09/11 | Họp thầy: chốt A1–A13, H1, T1, B1, B2. Thảo luận tiếp với Claude: thang 10 (TN 6 + TL 2 dễ × 1 + 1 nâng cao × 2), khung đề + random, mock đi đủ pipeline → API thật sau, chấm từ khóa (a), lịch 09–13/11, 6a (hàm của Hòa), 6b (đạt lần đầu thêm lại kỹ năng đã gỡ), làm lại không giới hạn. Gửi Hòa đặc tả phối hợp | Chờ Hòa trả lời |
| 09/11 | Chốt khóa demo 312 (37 làm khóa thứ 2). Chốt ngân hàng 3 bước, mục tiêu 20 câu/kỹ năng. Viết lại kế hoạch theo khung `Review-Frontend-Auth.md`: cấu trúc file, màn hình/API, GĐ0–GĐ6, bảng kiểm thử R1–R15. Phát hiện: repo dùng `create_all()` (không migration); `ai/client.py`, `ai/validators.py` là của chatbot Tâm → module 09 dùng `ai/review/` | Tâm chưa merge chatbot — không đụng nhánh Tâm |
| | | |
