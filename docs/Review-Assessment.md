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
| 6a | Đổi trạng thái khóa qua **hàm Khôi cung cấp** (đính chính 11/11: phần đăng ký khóa là của **Khôi**, không phải Hòa): `mark_course_completed(db, user_id, course_id)` (chỉ flush) + `get_enrollment_status(db, user_id, course_id)`, đặt trong `course_tracking_service.py` của Khôi. Đã gửi: `BA-nhom/Gui-Khoi-On-tap-09-va-Khoa-hoc.md`. Chưa có → dùng hàm giả để test. |

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
| `services/course_gateway.py` | Service | Cổng sang module Khóa học của **Khôi** (`get_enrollment_status`, `mark_course_completed`) — **nối hàm thật** `course_tracking_service` của Khôi (12/11) | 2, 3 |
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
- [x] **0.3 Gửi Khôi** `BA-nhom/Gui-Khoi-On-tap-09-va-Khoa-hoc.md` (đính chính 11/11: trước ghi nhầm Hòa) — dự kiến 09/11 · thực tế 09/11 👤 — **Khôi đã trả lời 11/11** (xem Q12)
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
- [x] **1.8 Duyệt ngân hàng khóa 312** — Tuấn **gom lỗi, sửa một lần** — thực tế 10/11 👤 chọn · 🤖 sửa
  - Quy ước soạn (chốt 10/11): `backend/data/review/README.md` — tên trường / giá trị liệt kê / mã giữ tiếng Anh như hiện tại; nội dung (đề, phương án, barem, giải thích, đoạn tri thức) tiếng Việt.
  - **Lỗi đã gom (10/11, đã kiểm bằng dữ liệu + bộ chấm thật) — ĐÃ SỬA 10/11** theo lựa chọn của Tuấn trên trang checklist (claude.ai/artifact/JfE6Pe4FihXj53RVYktvnR): tất cả "đồng ý", **L2 = (a)**, **L13 = (a)**, mục dữ liệu Claude sửa, **V1** đổi bài mẫu:

    | # | Câu / đoạn | Lỗi | Hướng sửa (đề xuất) |
    |---|---|---|---|
    | L1 | `312-COND-TN-05` | Đáp án đúng dài 71 ký tự (các phương án khác 4–21) và chứa sẵn lời giải thích → đoán được | Đáp án đúng chỉ ghi "Trung bình"; giải thích để ở `explanation` |
    | L2 | `312-PY-TL-02` ý Y2 | Từ khóa chính `"không"` quá chung: bài *"Tôi không biết tuple là gì cả."* vẫn **đạt** ý "Tuple không thay đổi được" | **Cần quyết định:** (a) siết thành "không thay đổi / không sửa / không đổi / immutable / bất biến" + đổi bài mẫu trong tài liệu họp thành "…tuple thì không sửa được" (vẫn 7/10); (b) giữ, ghi là hạn chế của mock |
    | L3 | `312-PY-TL-01` | Đề hỏi kèm ví dụ nhưng barem không chấm ví dụ; trả lời `bool` (hợp lệ) bị 0 ở ý số thực | Đổi đề: "Kể tên kiểu dữ liệu dùng cho số nguyên, số thực và chuỗi trong Python" |
    | L4 | `312-ITER-TL-03` | `tong=0` (không dấu cách) chỉ được điểm nhờ có chữ "khởi tạo"; `tong = tong + i` chỉ được **một phần** | Bộ chấm chuẩn hóa khoảng trắng quanh ký hiệu (`tong = 0` ≡ `tong=0`, `n + 1` ≡ `n+1`) — áp dụng mọi câu; thêm từ khóa `tong + i`, `= tong +` |
    | L5 | Đoạn `312-VAR-K03` | "None nghĩa là biến chưa có giá trị" — sai, mâu thuẫn `312-CS-K03` (biến **chưa gán** → NameError; `x = None` là đã có giá trị) | "None là giá trị đặc biệt biểu thị 'không có giá trị' (vd x = None); khác biến chưa gán — dùng biến chưa gán báo NameError" |
    | L6 | 30 câu TN | Vị trí đáp án gốc lệch: A 4 · B 12 · C 9 · D 5 | Không ảnh hưởng người học (mỗi lượt đã xáo phương án); cân lại cho gọn — không bắt buộc |
    | L7 | **Bộ chấm** (mọi câu TL) — nặng nhất | **Chép lại đề cũng được điểm**: chép nguyên đề → COND-TL-01 7/10, COND-TL-02 5/10, ITER-TL-03 5/10, VAR-TL-02 4,5/10… (từ khóa có sẵn trong đề: "6.5", "Yếu", "1 đến n", "không hợp lệ"…) | Bỏ qua câu trong bài làm gần trùng đề (vd ≥ 70% số từ có trong đề); từ khóa có sẵn trong đề chỉ tính khi nằm trong câu người học tự viết; test "chép đề → 0 điểm" |
    | L8 | **Bộ chấm** | Liệt kê từ khóa **dài trên một dòng** (không dấu câu) vẫn **10/10** (luật chống lách hiện chỉ bắt bài < 6 từ / câu < 3 từ) | Đo mật độ từ khóa mỗi câu: phần lớn là từ khóa (vd > 60% số từ) → coi là liệt kê, tối đa "một phần"; thêm test |
    | L9 | `data/review/README.md` | Chưa ghi quy tắc `main_keywords` / `sub_keywords` cho người soạn (có trong code + A10) | Thêm mục: đạt = chính + phụ cùng câu (phụ rỗng → chỉ cần chính); một phần = chính ở câu khác hoặc chỉ có phụ; 0 = không có |
    | L10 | **Bộ chấm** — nặng | **Bỏ dấu ở cả hai phía làm trùng chữ**: "dừng" = "dùng" = "đúng" = `dung`; "yếu" khớp "yêu cầu". *"Ta dùng break và continue trong bài này."* được **7,5/10** (ITER-TL-01); *"Ta dùng if…"* đạt ý "điều kiện, đúng" (COND-TL-01) | So **có dấu** (chuẩn hóa NFC) khi câu bài làm có dấu; chỉ so **bỏ dấu** khi câu đó gõ hoàn toàn không dấu. **Giữ luật khớp nguyên từ** (KHÔNG dùng `k in a` trong hàm `has_keyword` được gửi — khớp chuỗi con sẽ làm "if" khớp lại trong "elif"). Đã thử nghiệm bản nháp: các ca nhầm hết "đạt", bài không dấu vẫn đạt, ví dụ list/tuple vẫn 7/10 |
    | L11 | `312-VAR-TL-01` | Chép lại đề được **5/10** — đề có sẵn "giá trị" + "biến" (từ khóa chính + phụ ý 1) | Bỏ "giá trị" khỏi `main_keywords` ý 1 (L7 sửa ở bộ chấm cũng chặn được, nên làm cả hai) |
    | L12 | `312-PY-TN-06` | Giống L1: đáp án đúng "Báo lỗi TypeError vì cộng chuỗi với số" dài 38 ký tự, các phương án khác 7–8 | Rút còn "Báo lỗi TypeError"; lý do để ở `explanation`. (Đã quét cả 30 câu TN: chỉ còn L1 và L12 có đáp án dài bất thường) |
    | L13 | **Bộ chấm** — cần quyết định | Luật "**chỉ có từ khóa phụ → một phần**" quá dễ: chỉ nhắc tên chủ thể (*"Ta dùng break và continue"*) vẫn được ½ mỗi ý → **5/10** (sau khi sửa L10) | (a) Chỉ có từ khóa phụ → **0**; từ khóa chính ở câu khác → ½ (chặt hơn; ý Y3 của ví dụ list/tuple thành 0 → bài mẫu 6/10, phải đổi bài mẫu trong tài liệu họp); (b) giữ như hiện tại, ghi là hạn chế của mock |

  - Nhận xét **không đúng** với code hiện tại (đã kiểm, không cần sửa): "if" khớp trong "elif" — bộ chấm khớp **nguyên từ**; chấm theo từng câu — đã làm; gõ không dấu / NFC–NFD — bộ chấm tách dấu (NFD) rồi bỏ dấu ở **cả bài làm lẫn từ khóa** (đã thử "dieu kien" và chuỗi NFD → đều đạt); CheckConstraint `level` 2 bộ giá trị — ràng buộc viết theo loại câu, seed 40 câu OK; hiển thị code — đã `pre-wrap`; seed kiểm skill_id thuộc khóa — đã có `check_against_db` + test.
  - **Kết quả sửa (10/11):**
    - Bộ chấm viết lại (`keyword_grader.py`): so có dấu / không dấu theo câu (L10), bỏ khoảng trắng quanh ký hiệu (L4), bỏ câu chép đề — cụm 3 từ ≥ 70% (L7), liệt kê từ khóa (L8), chỉ có từ khóa phụ = 0 (L13a). Truyền nội dung đề vào bộ chấm (MockAI + dự phòng).
    - **L8 khác đề xuất:** ngưỡng 60% phạt nhầm đáp án mẫu (câu viết tốt đạt 67–83%), nên đổi thành **> 75% số từ là từ khóa VÀ chạm ≥ 2 ý**; bài liệt kê thật ≈ 93%.
    - **Thêm luật trên cả bài (10/11):** mật độ từ khóa trên mọi câu không chép đề > **85%** → cả bài tối đa "một phần". Vá lỗ hổng chia chuỗi từ khóa thành nhiều câu ngắn (trước đó "break thoát dừng kết thúc. continue bỏ qua lần lặp tiếp." được 10/10). Đo: đáp án mẫu + bài viết thật 24–73%, bài liệt kê 89–100%. Toàn bộ **462 passed**.
    - Dữ liệu: L1, L12 rút đáp án; L2a siết từ khóa Y2; L3 đổi đề; L11 bỏ "giá trị"; L5 sửa đoạn None; L6 vị trí đáp án gốc A 8 · B 7 · C 8 · D 7; thêm từ khóa `tong + i`, `= tong +` (L4). Sửa tại chỗ (chưa có bài làm thật nào dùng các câu này).
    - Tài liệu: L9 thêm mục "Từ khóa chấm tự luận được dùng thế nào" vào `data/review/README.md`; V1 bài mẫu mới *"List thì sửa được còn tuple thì không sửa được. List dùng ngoặc vuông. Tuple thì dùng ngoặc tròn."* → vẫn **7/10** — cập nhật `docs/De-xuat-AI-On-tap.md` + `BA-nhom/…_da-chot-v3.docx`.
    - Kiểm: đáp án mẫu 10 câu TL đều 10/10; chép đề cả 10 câu = 0; "dùng break / dùng if / yêu cầu / không biết tuple" = 0; bài không dấu 10/10; NFD = NFC. Test thêm 23 → toàn bộ **459 passed**; seed lại DB thật.
- [x] **1.9 `scripts/seed_review.py`** — dự kiến 10/11 · thực tế 09/11 🤖
  - Kiểm tra trước, ghi sau: sai ở đâu in **tất cả** lỗi, không ghi gì; kỹ năng phải thuộc khóa (`course_skill`, chỉ đọc). Chạy lại: cập nhật theo `code`, không trùng; đổi nội dung đoạn → xóa embedding cũ; câu đã tắt giữ nguyên tắt.
  - ✅ DB thật: lần 1 `+15 đoạn / +40 câu`, lần 2 `cập nhật 15 / 40`. Test `tests/test_seed_review.py` 23/23; toàn bộ **159 passed**.
- [x] **1.10 Nhờ Claude review GĐ1** — dự kiến 10/11 · thực tế 11/11 🤖
  - ⚠️ Phát hiện: sửa ngân hàng 10/11 (L6 đổi chỗ phương án + `correct_index` ngay trong câu cũ) làm lịch sử 3 lượt thử cũ của tài khoản #20 (lượt 3, 7, 10) hiện đúng/sai **lệch** với điểm đã lưu. Bài học: đúng quy tắc README — đổi đáp án = **tắt câu cũ + thêm mã mới**, không sửa đè. Xử lý: **đã xóa** 7 lượt thử của tài khoản #20 (11/11, Tuấn đồng ý).

## GĐ2 — Sinh đề và làm bài (11/11)

- [x] **2.1 `scripts/build_embeddings.py`** — 🤖 đã viết 09/11 · 👤 **Tuấn chạy**: `python -m scripts.build_embeddings` (lần đầu tải mô hình ~470 MB) — thực tế 10/11 👤 (kiểm DB: **15/15** đoạn có `embedding`)
  - Mô hình **đa ngôn ngữ** `paraphrase-multilingual-MiniLM-L12-v2` (`REVIEW_EMBEDDING_MODEL`) — mô hình `all-MiniLM-L6-v2` của Hòa chỉ hiểu tiếng Anh, tài liệu tri thức viết tiếng Việt.
  - ✅ Xong khi: 15 đoạn có `embedding`; lượt ôn mới có `score` trong trace.
- [x] **2.2 `services/rag_service.py`** — lọc theo kỹ năng → xếp cosine; vector câu truy vấn tính lúc chạy bằng mô hình **đã tải sẵn** (`local_files_only`); chưa có vector / mô hình → vẫn trả đoạn theo thứ tự tạo (không chặn ôn tập) — thực tế 09/11 🤖
  - Ghi chú: `sentence-transformers` đã có trong `requirements.txt` (nhóm dùng cho gợi ý lộ trình) nên backend nạp được mô hình cho câu truy vấn; đoạn tri thức vẫn tính sẵn offline.
- [x] **2.3 `ai/review/base.py` + `mock_ai.py` + `__init__.get_review_ai()` + `ai/prompts/review.py`** — thực tế 09/11 🤖
- [x] **2.4 `ai/review/validator.py`** — **dùng chung** cho ngân hàng soạn tay (`seed_review.py` đổi sang dùng file này) và câu AI sinh; sinh lại ≤ 2 lần → ngân hàng dự phòng; câu AI mới (giai đoạn 2) tự lưu `source='ai'` — thực tế 09/11 🤖
- [x] **2.5 `services/exam_builder.py`** — khung + **ưu tiên câu chưa dùng ở lượt trước** (`fresh`) — test chạy 100 lần mỗi kịch bản — thực tế 09/11 🤖
- [x] **2.6 `GET /api/courses/{course_id}/review`** — lý do chưa thể ôn: `not_enrolled` / `abandoned` / `no_question_bank` — thực tế 09/11 🤖
  - Trạng thái đăng ký đi qua `services/course_gateway.py` — **hàm giả** (coi như đang học) cho tới khi Khôi có hàm thật; chỉ sửa file này khi nối. 11/11: hằng trạng thái đổi theo bảng `user_courses` của Khôi (`ongoing` / `completed` / `abandoned` / `bookmarked` — `bookmarked` = chưa tham gia, không cho ôn; thêm test).
- [x] **2.7 `POST /api/courses/{course_id}/review-attempts`** — có lượt dở → `resumed=true`; bấm 2 lần cùng lúc → unique index chặn, trả lại lượt kia; chưa / bỏ khóa → 403; chưa có ngân hàng → 409 — thực tế 09/11 🤖
- [x] **2.8 `GET /api/review-attempts/{attempt_id}`** — không có `correct_index`, `rubric`, `explanation`, `question_id`, `option_order` — thực tế 09/11 🤖
- [x] **2.9 `PATCH /api/review-attempts/{attempt_id}/answers`** — gửi một phần; TN `selected_index` (null = bỏ chọn), TL `text_answer`; sai câu nào → 422, **không lưu câu nào**; đã nộp → 409 — thực tế 09/11 🤖
- [x] **2.10 Quyền sở hữu** — người khác (kể cả admin) → 404 — thực tế 09/11 🤖
  - ✅ Test: `test_exam_builder.py` (208), `test_review_ai.py` (11), `test_review_api.py` (26, chạy 5 lần liền đều đạt); toàn bộ **404 passed**. Chạy thử trên PostgreSQL thật bằng tài khoản test: đề 15 câu đúng khung, không lộ đáp án, lưu + làm tiếp đúng; đã xóa lượt thử.
- [x] **2.11 Thử tay trên Swagger** đủ luồng bắt đầu → lấy đề → lưu → làm tiếp — dự kiến 11/11 · thực tế 10/11 🤖
  - Gọi thẳng server đang chạy (`/api/docs` đủ **8** endpoint ôn tập) bằng đúng request Swagger gửi: bắt đầu → lấy đề → lưu 5 câu → bắt đầu lại = `resumed` cùng lượt, còn 5/5 câu. Script: `scratchpad/manual_r1_r15.py`; đã dọn dữ liệu thử.
- [x] **2.12 Nhờ Claude review GĐ2** — dự kiến 11/11 · thực tế 11/11 🤖
  - Ghi nhận cho GĐ5: request ôn tập **đầu tiên sau khi bật server** nạp mô hình embedding → có lúc > 60 giây (đo 11/11). Nên nạp sẵn mô hình lúc khởi động server.
  - ✅ **Đã làm 12/11:** `rag_service.warm_up_in_background()` gọi trong `main.py` (lifespan) → nạp mô hình ở **luồng nền**, server vẫn lên ngay. Khóa `_MODEL_LOCK` + kiểm tra lại → luồng nền và request đầu tiên tới cùng lúc vẫn chỉ nạp **1 lần** (thử 5 luồng). Đo: `import sentence_transformers` ~42 giây + nạp ~6 giây; server mới bật, chờ 70 giây → request ôn tập đầu tiên **0.7 giây** (trước: 48–67 giây). Bỏ qua khi chạy pytest. Lưu ý: dùng `uvicorn --reload` mà sửa file liên tục thì mỗi lần reload phải nạp lại từ đầu.

## GĐ3 — Chấm điểm, Hoàn thành, test (12/11)

- [x] **3.1 Chấm trắc nghiệm** (`services/review_grader.py`) — đổi vị trí trên màn hình về lựa chọn gốc qua `option_order`; 0,5đ/câu; bỏ trống / sai = 0 — thực tế 09/11 🤖
- [x] **3.2 Chấm tự luận bằng từ khóa** (`ai/review/keyword_grader.py`, `MockAI.grade_essay`) — thực tế 09/11 🤖
  - Từ khóa chữ khớp **nguyên từ** ("for" ≠ "format"); tách câu không cắt "6.5", "a.append"; bài < 6 từ hoặc câu khớp < 3 từ → tối đa một phần.
  - AI lỗi / trả điểm sai quy tắc (`validator.grading_errors`) → chấm bằng từ khóa, ghi vào `trace.grading.keyword_fallback`.
  - Sửa barem `312-PY-TL-02` ý Y4: bỏ từ khóa phụ "ví dụ", "dùng" (bài làm mẫu bị cộng nhầm thành 8/10) → đúng **7/10** như ví dụ gửi thầy.
  - ✅ Test: ví dụ list/tuple ra 7/10 (có dấu và không dấu); đáp án mẫu của **cả 10 câu tự luận** trong ngân hàng đều đạt 10/10.
- [x] **3.3 `POST /api/review-attempts/{attempt_id}/submit`** — tổng thang 10, đạt khi ≥ `REVIEW_PASS_SCORE` (so trên tổng chưa làm tròn); nộp lần 2 → 409 — thực tế 09/11 🤖
  - ✅ T1 (12/11): chờ quá `REVIEW_GRADING_TIMEOUT` → trạng thái `grading`, chấm nốt ở nền — chi tiết ở mục **5.8**.
- [x] **3.4 Đạt lần đầu — một transaction** — `mark_course_completed` (cổng, hàm giả) + `mark_known(source="review")` mọi kỹ năng của khóa (kể cả kỹ năng đã tự gỡ — 6b) → commit một lần; lỗi giữa chừng → rollback, bài vẫn đang làm, nộp lại được — thực tế 09/11 🤖
  - Chỉ khi trạng thái khóa là **đang học**; đã Hoàn thành (B2) / đã bỏ / chưa đăng ký → chỉ lưu kết quả.
- [x] **3.5 Email kết quả** — `core/email.send_review_result_email`, router gửi bằng `BackgroundTasks` **sau** khi trả kết quả (đã commit) — thực tế 09/11 🤖
  - ⚠️ 12/11: code gửi đã có, nhưng `.env` đang dùng SMTP **mẫu** → email chỉ in ra terminal backend. Bật gửi thật: cấu hình Gmail (mật khẩu ứng dụng) trong `.env`.
  - ✅ 12/11: đã cấu hình Gmail, gửi thật thành công. Người nhận lấy **tự động** từ email tài khoản (`users.email`) — `.env` chỉ cấu hình MỘT hộp thư gửi cho cả hệ thống. Nên đổi sang Gmail riêng cho đồ án trước khi demo.
- [x] **3.6 `GET /api/me/review-history`** (lọc `course_id`, `passed`, `page`, `size`) + **`GET /api/me/review-history/{attempt_id}`** (lượt đang làm → 404, chưa lộ đáp án) — thực tế 09/11 🤖
- [x] **3.7 `GET /api/admin/review-attempts/{attempt_id}/trace`** — student 403, admin 200 — thực tế 09/11 🤖
- [x] **3.8 Test đủ kịch bản** — `test_keyword_grader.py` (13), `test_review_submit.py` (19): 10/10 + Hoàn thành + kỹ năng, bỏ trống = 0, ngưỡng 6,0 / 5,5, ví dụ 7/10 → 1,4đ, đạt lần 2 chỉ lưu lịch sử, kỹ năng đã gỡ quay lại, lỗi giữa transaction, AI chấm lỗi → từ khóa, lịch sử + phân trang, quyền — thực tế 09/11 🤖
- [x] **3.9 Toàn bộ `pytest` + `ruff`** — **436 passed**; ruff sạch các file module 09 (B008 `Depends` giữ như module 01) — thực tế 09/11 🤖
  - Chạy thử PostgreSQL thật (tài khoản test): 9,4/10 Đạt (câu list/tuple 1,4đ), khóa Hoàn thành, 5 kỹ năng "Đã biết"; đã khôi phục hồ sơ + xóa lượt thử.
- [x] **3.10 Nhờ Claude review GĐ3** (giai đoạn quan trọng nhất) — dự kiến 12/11 · thực tế 11/11 🤖
  - 🐞 **Đã sửa:** 2 request Nộp **cùng lúc** đều được chấm (đo trên server thật: 5/5 vòng ra 200 + 200 → chấm 2 lần, gửi 2 email). Sửa: khóa dòng lượt làm bài (`SELECT … FOR UPDATE`) khi **lưu** và **nộp** (`review_repository.get_attempt(for_update=True)`) → request sau chờ rồi nhận 409. Đo lại: 5/5 vòng 200 + 409. Toàn bộ **462 passed**.

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

- [ ] **5.1 `ai/review/real_ai.py`** (giai đoạn 2): API key miễn phí trong `.env`, `AI_MODE=real`, thử trên khóa 312; lỗi / hết lượt → dự phòng — thực tế 12/11 🤖 (chạy thử — chờ chốt model với Tâm)
  - Nhà cung cấp: **Google Gemini** (giống chatbot của Tâm), gọi REST bằng `httpx` (không thêm thư viện). Biến `.env` dùng chung: `LLM_API_KEY`, `LLM_MODEL`. Key của Tuấn: hợp lệ (12/11). Model **tạm** `gemini-3.5-flash-lite` (thử 4 model: 3.1-flash-lite 2.8s · 3.5-flash-lite 3.5s · flash-lite-latest 7.3s · 3.5-flash 30s; `gemini-2.5-flash` đã ngừng cấp cho người dùng mới) → **đổi cho khớp Tâm sau**.
  - ✅ **Chốt model 12/11 — mỗi người một model, dùng chung khóa**: chatbot (Tâm) `LLM_MODEL=gemini-3.6-flash`; Ôn tập (Tuấn) `REVIEW_LLM_MODEL=gemini-3.5-flash-lite` (biến mới, để trống thì dùng `LLM_MODEL`; có thêm `REVIEW_LLM_API_KEY` nếu muốn khóa riêng). Lý do — thử cùng 10 bài, cùng lúc: 3.6-flash **5/10 lỗi 503** (+ 429 hết lượt ở lần trước), 4,7–15,7 giây/câu, chấm bài đúng viết tự nhiên chỉ 7 và 8; 3.5-flash-lite **0 lỗi**, 1,8–3,2 giây, bài đúng 10/10, bài sai 0, không bị lừa. Mỗi model có hạn mức riêng → chatbot và chấm bài không giành lượt của nhau khi demo. Test: `test_review_model_overrides_chatbot_model`.
  - `RealAI.grade_essay`: Gemini chấm **theo nghĩa** từng ý → full / partial / none + câu trích; **điểm do code tính** (đủ / ½ / 0); câu trích không có trong bài → bỏ; bài trống không gửi AI. Lỗi mạng / 429 hết lượt / quá giờ / sai JSON / thiếu ý → `AIUnavailableError` → chấm từ khóa dự phòng (đã có).
  - `RealAI.generate_questions`: kỹ năng đủ `REVIEW_BANK_TARGET_PER_SKILL` (20) câu → bốc ngân hàng, **không gọi AI**; thiếu → Gemini soạn theo prompt RAG (validator kiểm, lưu `source='ai'`). Khóa 312 đủ 20/kỹ năng → chỉ phần CHẤM dùng AI.
  - Chỉ gửi đề, barem, bài làm / đoạn tri thức — **không** gửi tên, email, CCCD. Gói miễn phí: Google có thể dùng dữ liệu để cải thiện sản phẩm → ghi vào báo cáo.
  - Chạy thử Gemini thật (`scratchpad/real_ai_trial.py`): bài đúng viết tự nhiên **0 → 10** (CS-TL-03, PY-TL-04); viết bằng code 7.5 → 10; **bài sai** đảo for/while 7.5 → **0**, đảo break/continue (lỗi 3) 10 → **0**, "None là chuỗi rỗng" 10 → 5; **bài cố tình lừa AI** → 0 (không bị lừa); bài mẫu gửi thầy 7 → 8. Mỗi câu 1.4–8 giây. Gemini soạn 3 câu kỹ năng `variable` → validator **hợp lệ 3/3**, đúng ngữ cảnh.
  - Luồng đầy đủ trên DB thật (`AI_MODE=real`): nộp + chấm 3 tự luận **7.2 giây**, trace `ai: gemini`, không phải dùng từ khóa dự phòng; đã dọn dữ liệu thử.
  - Test: `tests/test_real_ai.py` **12 test** dùng Gemini GIẢ (`httpx.MockTransport`) — không gọi mạng, không tốn lượt. Toàn bộ test vẫn chạy mock.
  - Còn lại: chốt model với Tâm · bật cho server: `.env` đặt `AI_MODE=real` + `LLM_MODEL=…` · ~~T1~~ xong 12/11 (mục 5.8) · sinh câu cho kỹ năng **chưa có câu nào** cần sửa `plan_exam` (hiện A1 chặn khóa có kỹ năng thiếu câu) → bàn sau.
  - Ngân hàng bước 3: kỹ năng thiếu câu → AI sinh → validator → lưu `source="ai"`; đủ 20 câu/kỹ năng thì ngừng sinh.
- [x] **5.8 T1 — AI chấm quá lâu → "Đang chấm", chấm nốt ở nền** — thực tế 12/11 🤖
  - **Song song**: 3 câu tự luận gửi Gemini **cùng lúc** (luồng riêng, không đụng DB) → 3 câu ≈ thời gian 1 câu (`review_grader.start_ai_grading` / `collect`).
  - Chờ tối đa `REVIEW_GRADING_TIMEOUT` (20 giây). Xong kịp → **200** có điểm như cũ.
  - Quá 20 giây → lưu `status="grading"` + giờ nộp (khóa câu trả lời: sửa / nộp lại → 409), trả **202**, chưa có điểm và **chưa lộ đáp án** (`questions: []`). Tác vụ nền (`finish_grading`, phiên DB riêng) chờ AI tới `REVIEW_GRADING_MAX_WAIT` (**120 giây** kể từ lúc nộp, biến mới trong `.env.example`); câu AI chưa xong / lỗi → **chấm từ khóa** → lưu điểm + **chuông** + **email**.
  - Gemini khi chấm được chờ tới 120 giây (trước: 20) để bài chậm vẫn chấm theo nghĩa; sinh đề vẫn chờ 20 giây.
  - **Server khởi động lại giữa lúc chấm** → bài kẹt `grading`: khi người dùng mở trang ôn tập / lịch sử / kết quả mà bài đã quá 120 + 60 giây → tự chấm lại bằng từ khóa (`recover_stuck_grading`, có chuông, không email). Bài mới nộp < 3 phút thì không đụng (luồng nền có thể còn chạy).
  - Frontend: trang kết quả hiện khối **"Đang chấm bài của bạn…"** ("có thể rời trang — xong sẽ báo trên chuông và email"), **tự hỏi lại mỗi 5 giây** rồi chuyển sang kết quả. Hộp Nộp bài báo "tối đa khoảng 20 giây". Lịch sử / trang bắt đầu / hồ sơ hiện "Đang chấm" thay vì điểm.
  - ✅ Test: `tests/test_review_grading_timeout.py` **6 test** (song song < 1 giây cho 3 × 0,4 giây · 202 rồi nền chấm bằng AI + chuông + email · AI không trả lời → từ khóa với lỗi "quá thời gian" · đang chấm thì 409 + ẩn đáp án + chạy nền 2 lần không chấm trùng · cứu bài kẹt · bài mới không bị cứu sớm). Toàn bộ test cũ vẫn đạt.
  - ✅ Thử đầu–cuối trên trình duyệt (server tạm cổng 8010, `AI_MODE=real`, ép chờ 0 giây, SMTP tắt): Nộp → **202** → 1,1 giây vào "Đang chấm" → tự chuyển sang **10/10 Đạt** sau 11,5 giây · 7/7 PASS (`scratchpad/shots/t1_grading.mjs`). Thực tế lần này Gemini **trả 503 quá tải ở 2/3 câu** → 2 câu tự chấm từ khóa, bài vẫn có điểm — đúng lý do cần T1. Đã xóa tài khoản thử.
- [ ] **5.2 Ngân hàng bước 2**: khóa 312 đủ 100 câu (70 TN + 30 TL); khóa 37 (sau khi gỡ "Web") — thực tế 11/11 (khóa 312) 🤖 · khóa 37 còn chờ gỡ "Web"
  - ✅ Khóa 312: **40 → 100 câu** (+40 TN, +20 TL). Mỗi kỹ năng 20 câu = 14 TN (7 NB + 7 TH) + 6 TL; cả khóa 30 TL = 18 dễ + 12 nâng cao. Đáp án đúng TN rải đều (A18 · B17 · C18 · D17). Gắn với 15 đoạn tri thức sẵn có (không cần chạy lại embedding). Đã seed DB: `+60 / cập nhật 40`. 👤 **Tuấn duyệt nội dung 60 câu mới** (mã `…-TN-07..14`, `…-TL-03..06`, `CS-TL-02..06`).
  - Kiểm tự động: validator 0 lỗi; **đáp án mẫu của cả 30 TL đạt 10/10**; 20 TL mới: chép đề = 0, liệt kê từ khóa trong 1 câu = 5/10.
  - 🐞 **Sửa lỗi A1 (`exam_builder.plan_exam`)**: kỹ năng của khóa KHÔNG có câu TN trước đây bị **bỏ qua** → khóa nhiều kỹ năng ra đề toàn câu của 1–2 kỹ năng, đạt thì Hoàn thành + "Đã biết" cả kỹ năng chưa hỏi. Đo trên DB thật: ngân hàng 40 câu đã có 4 khóa ngoài 312 bị (62, 940, 2115, 3417); lên 100 câu sẽ thành **197 khóa**. Sửa: mọi kỹ năng của khóa phải có câu TN, thiếu → "Chưa có đề ôn tập". Sau sửa: ôn được đúng 4 khóa mà MỌI kỹ năng đều có câu (312, 1560, 3020, 3088). Test mới `test_skill_without_mcq_blocks_the_whole_course`; toàn bộ **485 passed**; R1–R15 chạy lại trên server 19/19.
  - ✅ **Đã chốt 11/11 — phương án (a): ghi là hạn chế của bản mock, KHÔNG thêm luật chặn; AI thật (5.1) chấm theo nghĩa.** Chi tiết giới hạn bộ chấm mock: viết mỗi ý thành một câu cực ngắn kèm chữ đệm (vd "cả hai and là. ít nhất một or là. đảo not là.") vẫn được 10/10 — xảy ra ở cả câu CŨ (COND-TL-01, CS-TL-01, COND-TL-02…) lẫn câu mới, vì mật độ từ khóa < 85% nhờ chữ đệm. Hướng: (a) ghi là hạn chế của mock, AI thật (5.1) chấm theo nghĩa; (b) thêm luật: câu được "Đạt" phải có ≥ N từ KHÔNG phải từ khóa (cuộc đua lách – chặn, khó dứt điểm).
- [ ] **5.3 Cập nhật BA/SRS** FR-24/25/26 theo quyết định 09/11 — thực tế __/__
- [ ] **5.4 Làm đẹp giao diện 09** (theo phong cách module 01) — thực tế __/__
- [ ] **5.7 (CHỜ KHÔI XÁC NHẬN) Sửa bộ chấm tự luận theo nhận xét 11/11** — đã thử trên bản sao + đã viết vào code rồi **hoàn tác** (Tuấn: chờ Khôi). Bản sửa lưu sẵn: `BA-nhom/grader_fix_loi_1_2_4.patch` (áp lại: `git apply …patch` ở thư mục repo, rồi seed lại).
  - Lỗi 1 (bài đúng viết tự nhiên bị 0 — thêm từ đồng nghĩa CS-TL-03, PY-TL-04) · Lỗi 2 ("chưa biết trước" vẫn khớp "biết trước" → bỏ khớp đứng sau chưa / không / chẳng; bỏ "số lần" ở ITER-TL-02) · Lỗi 4 (bỏ luật "câu khớp ≥ 3 từ" → bài viết bằng code / "Lỗi logic." không bị trừ; COND-TL-05 thêm chủ thể `print`) · VAR-TL-05 bỏ "rỗng" ("None là chuỗi rỗng" từng được 10/10). Đo khi áp: 30 đáp án mẫu vẫn 10/10, 526 passed.
  - Lỗi 3 (câu ghép 2 vế đảo chủ thể, vd "break bỏ qua … còn continue thoát …" được 10/10) — **chưa làm**, chờ Khôi; patch có sẵn test `xfail` ghi rõ giới hạn này.
- [ ] **5.5 Nghiên cứu lại kho vector** (A7 — có thể chuyển pgvector) — thực tế __/__
- [ ] **5.6 (CHỜ BÀN — sau khi xong các việc khác) Lối vào ôn tập từ đồ thị lộ trình** — Tuấn đề xuất 11/11, ảnh `BA-nhom/PathDetail-on-tap-de-xuat-Tuan.png` (sửa từ màn `PathDetail` của Hòa)
  - Ý tưởng: icon ôn tập trên từng ô kỹ năng → popover "Ôn tập <kỹ năng>: N khóa học có bài ôn tập" (mỗi khóa: điểm lần trước, thời gian, nút Ôn tập) + thẻ "Ôn tập <kỹ năng>" ở khung phải + chú thích "Ôn tập" / "Đến hạn ôn" (chấm cam).
  - Claude góp ý (cần chỉnh khi bàn): (1) không ghi cứng "7/10" — ngưỡng đã chốt 6/10, lấy `pass_score` từ API; (2) đạt = **cả khóa** Hoàn thành + mọi kỹ năng của khóa "Đã biết", không riêng 1 kỹ năng; (3) khóa **chưa tham gia** không cho ôn (B1, R1) → hiện mờ + "Tham gia học"; (4) chỉ hiện icon khi kỹ năng có ≥ 1 khóa ôn được (hiện mới khóa 312 có ngân hàng); (5) "Đến hạn ôn" là **khái niệm mới** — tính từ `review_attempts.submitted_at`, không cần bảng mới, cần chốt số ngày (đề xuất 30); (6) điện thoại: popover → khung trượt từ dưới; vùng bấm icon ≥ 28px.
  - Kỹ thuật (Tuấn): API gộp `GET /api/me/review-options?skill_ids=…` (1 lần cho cả lộ trình) + component `ReviewPopover` trong `features/review/`; Hòa chỉ đặt icon + gọi component. Phụ thuộc: `user_courses` của Khôi; lộ trình của Hòa phải dùng `users.user_id` (hiện `student_id`).
  - Cần chốt khi bàn: quy tắc "Đến hạn ôn" (số ngày) · có làm trong GĐ5 không.
  - 12/11: Tuấn mở lại → Claude soạn kế hoạch gửi Hòa `BA-nhom/Gui-Hoa-On-tap-tu-do-thi-lo-trinh.md` (bản nháp): chia việc T1–T4 (Tuấn: API `GET /api/me/review-options`, component `ReviewPopover` + `ReviewNodeBadge`, nút về lộ trình, quy tắc đến hạn) · H1–H6 (Hòa: gọi API 1 lần, đặt badge / popover, chú thích, đổi `student_id` → `user_id`); đề xuất đến hạn = 30 ngày; lịch 13–18/11. Kiểm 12/11: frontend lộ trình của Hòa (`PathGraph`, `NodeCoursePanel`, `LearningPathDetailPage`) **còn rỗng**. Chờ Hòa trả lời 5 câu.

## GĐ6 — Tích hợp và hoàn thiện (19/11 → 25/11)

- [ ] **6.1 Nối hàm thật của Khôi** (`course_tracking_service`, Khôi hẹn trước 12/11 — kiểm 11/11: chưa push, `user_course.py` + `course_tracking_service.py` trên nhánh Khôi còn rỗng) (thay hàm giả), test luồng đầy đủ với module khóa học — thực tế __/__
  - ✅ **12/11 — nối xong với Khôi** (gộp thử ở nhánh tạm `tuan/merge-khoi`, Tuấn duyệt → đã đưa vào `tuan/future-auth` 12/11): gộp nhánh `feat/Khoi-LuuKhoaHocVaThamGiaKhoaHoc` (bảng `user_courses`, `course_tracking_service`, API `/me/courses`, `/me/bookmarks`, `/courses/{id}/join`). Xung đột 4 file (`course_gateway`, `api.py`, `conftest`, `test_review_api`) đã gộp tay. Điều kiện Hoàn thành đổi thành **đạt + khóa `ongoing`** (bỏ `has_first_pass` — điểm 3). **Test chung T1–T9 đạt 9/9** (`tests/test_review_course_integration.py`, gọi API thật hai bên); toàn bộ test đạt. ⚠️ Frontend chưa có nút "Tham gia khóa học" → sau khi gộp, người dùng phải tham gia khóa (Swagger `POST /api/courses/{id}/join`) mới ôn được.
  - **Đối chiếu câu trả lời của Khôi với code (12/11)** — 4 điểm Khôi làm đúng (cột `user_id` → `users.user_id` + khóa chính kép; 2 hàm chỉ flush; chặn bỏ / PATCH khóa `completed`, chặn tự gửi `completed`; `bookmarked` = chưa tham gia, không thêm kỹ năng). Các điểm lệch / lỗi tìm thấy khi gộp:
    | # | Lỗi / điểm lệch | Mức | Sửa ở đâu |
    |---|---|---|---|
    | L1 | `mark_course_completed_in_tx` **im lặng không làm gì** khi khóa không `ongoing` (khác hợp đồng 3.2: lẽ ra báo `ValueError`). Khe hở: người học bấm "Bỏ khóa" đúng lúc bài đang chấm → bài ghi "Hoàn thành khóa" + kỹ năng "Đã biết" nhưng khóa `abandoned` → dữ liệu lệch | Trung bình (hiếm) | `course_gateway.py` (Tuấn): gọi xong đọc lại trạng thái, chưa `completed` → báo lỗi → rollback cả lần nộp, trả 409 "nộp lại". Không cần Khôi sửa |
    | L2 | Khôi sửa thẳng `course_gateway.py` (file của Tuấn) trên bản CŨ: hằng `IN_PROGRESS = "in_progress"` + bảng ánh xạ, mất hằng `BOOKMARKED` → xung đột khi gộp | Thấp | Đã gộp tay: giữ hằng theo giá trị DB (`ongoing`…), dùng hàm thật của Khôi |
    | L3 | Khôi sửa `tests/conftest.py`, `tests/test_review_api.py` (của Tuấn) — chủ yếu định dạng lại (black) + thêm `UserCourse` vào `bank_312` | Thấp | Gộp tay: giữ fixture chặn email/AI thật, kỹ năng 99001, test `bookmarked`; nhận `UserCourse` của Khôi |
    | L4 | Tên bảng đổi student_courses → **`user_courses`** (Khôi đề xuất) — tài liệu còn ghi tên cũ | Thấp | Đổi tên trong `Review-Assessment.md` + file gửi Khôi |
    | L5 | Test cũ `test_second_pass_only_records_history` dựa vào hàm giả (khóa không bao giờ thành `completed`) → lỗi khi nối thật | Thấp | Sửa test dùng trạng thái thật |
    | L6 | Frontend **chưa có nút "Tham gia khóa học"** → sau khi gộp phải tham gia qua Swagger mới ôn được | Trung bình (ảnh hưởng demo) | Chờ Tuấn quyết: thêm tạm nút ở trang ôn tập hay chờ Khôi |
  - **Kế hoạch chỉnh cho khớp rồi gộp (12/11):**
    - [x] B1. Gộp thử nhánh Khôi vào nhánh tạm `tuan/merge-khoi`, gộp tay 4 file xung đột (L2, L3) — `d721ad7`
    - [x] B2. Test chung T1–T9 tự động (`tests/test_review_course_integration.py`) — 9/9 đạt — `411e83f`
    - [x] B3. Hoàn thành = đạt + `ongoing`, bỏ `has_first_pass` (điểm 3); sửa test L5 — `19bbc61`
    - [x] B4. Sửa L1 trong `course_gateway.py` (`EnrollmentChangedError` → 409 "nộp lại") + test `test_l1_…` (kiểm ngược: bỏ đoạn kiểm thì test trượt)
    - [x] B5. Đổi tên student_courses → `user_courses` trong tài liệu (L4); file gửi Khôi thêm Phần 4
    - [x] B6. Chạy lại toàn bộ test — **595 passed**
    - [x] B7. Gộp `tuan/merge-khoi` vào `tuan/future-auth` (fast-forward, 12/11)
    - [ ] B8. L6 — chờ Tuấn quyết
  - Cần chốt với Khôi trước khi nối (gửi 11/11, `BA-nhom/Gui-Khoi-…` Phần 2–3): (1) cột người dùng của `user_courses` = `users.user_id`; (2) 2 hàm **chỉ flush**; (3) không cho bỏ khóa `completed` + phía Tuấn đổi điều kiện Hoàn thành thành "đạt + đang `ongoing`" (bỏ kiểm lần đạt đầu, tránh kẹt khi bỏ → đăng ký lại); (4) `bookmarked` = chưa tham gia. Test chung T1–T9.
- [ ] **6.2 Kiểm thử thủ công** theo bảng dưới — thực tế __/__ (10/11: chạy API 19/19 đạt; còn R1 chờ Khôi, phần giao diện R4/R5/R15 + email R7 👤)
- [ ] **6.3 Rà bảo mật**: không lộ đáp án / barem trước khi nộp; không xem được bài người khác; API debug chặn student; API key không nằm trong repo — thực tế __/__
- [ ] **6.4 Tập demo + tạo Pull Request** — thực tế __/__

---

## Bảng kiểm thử thủ công

| # | Thao tác | Mong đợi | GĐ | Đạt |
|---|---|---|---|---|
| R1 | Vào trang ôn tập khóa **chưa đăng ký** | Báo chưa thể ôn, không có nút Bắt đầu | 2, 4 | ⚠️ chờ Khôi — stub coi mọi người đã đăng ký; hiện chỉ test tự động kiểm |
| R2 | Vào trang ôn tập khóa **không có ngân hàng** | "Chưa có đề ôn tập" | 2, 4 | ✅ 10/11 — khóa 37: `no_question_bank` |
| R3 | Bắt đầu ôn khóa 312 | Đề 15 câu: 12 TN + 3 TL, đủ 5 kỹ năng | 2, 4 | ✅ 10/11 — 12 TN + 3 TL (2 dễ, 1 nâng cao), 5 kỹ năng |
| R4 | Làm 5 câu → Tạm rời → vào lại | "Làm tiếp", 5 câu vẫn còn | 2, 4 | ✅ 10/11 (API) — `resumed`, còn 5/5 |
| R5 | Mở `F12` → xem response lấy đề | Không có đáp án, barem, giải thích | 2 | ✅ 10/11 (API) — 👤 còn xem bằng F12 |
| R6 | Đăng nhập tài khoản khác, mở link bài của người kia | 404 | 2 | ✅ 10/11 — xem / lưu / nộp / lịch sử đều 404 |
| R7 | Nộp bài đạt (≥ 6) | Kết quả Đạt; khóa Hoàn thành; hồ sơ có 5 kỹ năng "Đã biết"; có email | 3, 4 | ✅ 10/11 — 10/10, Hoàn thành, 5 kỹ năng · 👤 email chưa xem (tài khoản test @example.com) · ⚠️ **Đính chính 12/11:** `.env` có `SMTP_HOST=smtp.example.com` (chữ mẫu) → backend **chỉ in email ra terminal** (`[DEV EMAIL]`), CHƯA gửi thật; báo cáo 10/11 "SMTP đã cấu hình" là SAI (khi đó chỉ kiểm có giá trị). Cần cấu hình Gmail (hướng dẫn: `BA-nhom/Huong-dan-test-backend-Tuan.md` mục 0b) rồi test lại R7 · ✅ **12/11 Tuấn cấu hình Gmail xong** (gửi từ phamthanht009@gmail.com, mật khẩu ứng dụng): đăng nhập SMTP OK, đã gửi thử 2 thư (quên mật khẩu + kết quả ôn tập mẫu) tới phamthanht009@gmail.com — 👤 Tuấn xác nhận đã nhận, rồi làm R7 bằng tài khoản email thật |
| R8 | Nộp bài chưa đạt → làm lại | Đề mới, không trùng câu lượt trước; khóa vẫn đang học | 3, 4 | ✅ 10/11 — trùng 0/15 câu |
| R9 | Gỡ 1 kỹ năng của khóa khỏi hồ sơ → làm đạt lần đầu | Kỹ năng đó quay lại "Đã biết" (6b) | 3 | ✅ 10/11 — gỡ 400 → quay lại `known`/`review` |
| R10 | Khóa đã Hoàn thành → ôn lại (đạt hoặc trượt) | Chỉ thêm lịch sử; khóa và kỹ năng không đổi (B2) | 3 | ✅ 10/11 — `completed_course=false`, kỹ năng không đổi |
| R11 | Viết tự luận không dấu ("list thay doi duoc") | Vẫn chấm đúng ý | 3 | ✅ 10/11 — đáp án mẫu không dấu đủ điểm |
| R12 | Tự luận chỉ liệt kê từ khóa ("list tuple mutable") | Tối đa "một phần" | 3 | ✅ 10/11 — chỉ `partial` / `none` |
| R13 | Bấm Nộp 2 lần liên tiếp | Lần 2 bị từ chối, điểm không đổi | 3 | ✅ 10/11 — lần 2 → 409, điểm giữ nguyên |
| R14 | Student gọi API debug trace | 403 | 3 | ✅ 10/11 — 403 |
| R15 | Lịch sử ôn tập → mở 1 lượt | Từng câu, đáp án đúng, điểm từng ý + bằng chứng | 3, 4 | ✅ 10/11 (API) — 15 câu, đáp án đúng, điểm + bằng chứng từng ý |

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
| Q12 | Tên bảng / cột / giá trị trạng thái đăng ký khóa (**Khôi**) | 3 | — | Bảng `user_courses` (11/11 Khôi ghi tên cũ student_courses, 12/11 đổi tên), cột `status`: `bookmarked` · `ongoing` · `completed` · `abandoned`. 2 hàm trong `course_tracking_service.py`, kịp trước 12/11; `join_course` / `abandon_course` gọi `add_learning_from_course` / `remove_learning_from_course` (đang làm) | 11/11 |
| Q13 | Bảng tạo bằng `create_all()` hay migration Alembic? | 1 | `create_all()` như các bảng hiện có (repo chưa có migration nào) | `create_all()` | 09/11 |

## Nhật ký

| Ngày | Đã làm | Vướng mắc |
|---|---|---|
| 06/11 | Thầy bổ sung yêu cầu AI sinh câu hỏi (system prompt + RAG, trắc nghiệm + tự luận); viết đề xuất `docs/De-xuat-AI-On-tap.md` | Chờ thầy trả lời A1–A9 |
| 06/11 | Đề xuất tiêu chí chấm (Phụ lục A); thêm A10–A13; Tuấn chọn chấm tự luận theo từng ý | Hẹn thảo luận 09/11 |
| 09/11 | Họp thầy: chốt A1–A13, H1, T1, B1, B2. Thảo luận tiếp với Claude: thang 10 (TN 6 + TL 2 dễ × 1 + 1 nâng cao × 2), khung đề + random, mock đi đủ pipeline → API thật sau, chấm từ khóa (a), lịch 09–13/11, 6a (hàm của Khôi — đính chính 11/11), 6b (đạt lần đầu thêm lại kỹ năng đã gỡ), làm lại không giới hạn. Gửi đặc tả phối hợp (ghi nhầm Hòa — đúng là Khôi) | Khôi đã trả lời 11/11 |
| 11/11 | Review GĐ1–3: sửa lỗi nộp 2 lần cùng lúc (khóa dòng). Xóa 7 lượt thử cũ của tài khoản #20 (lịch sử lệch do sửa đè đáp án ngày 10/11). **Đính chính: phần đăng ký / hoàn thành khóa là của Khôi** (trước ghi nhầm Hòa); Khôi trả lời Q12, cổng `course_gateway` đổi hằng trạng thái theo `user_courses` | Chờ Khôi push `course_tracking_service` |
| 09/11 | Chốt khóa demo 312 (37 làm khóa thứ 2). Chốt ngân hàng 3 bước, mục tiêu 20 câu/kỹ năng. Viết lại kế hoạch theo khung `Review-Frontend-Auth.md`: cấu trúc file, màn hình/API, GĐ0–GĐ6, bảng kiểm thử R1–R15. Phát hiện: repo dùng `create_all()` (không migration); `ai/client.py`, `ai/validators.py` là của chatbot Tâm → module 09 dùng `ai/review/` | Tâm chưa merge chatbot — không đụng nhánh Tâm |
| 12/11 | **T1 xong** (mục 5.8): chấm tự luận song song, quá 20 giây → "Đang chấm" (202) + chấm nền ≤ 120 giây + cứu bài kẹt; frontend tự cập nhật. Xóa thư mục khung rỗng `frontend/src/pages`, `src/components` (0 dòng, không ai dùng) | Chờ Tâm chốt model rồi bật `AI_MODE=real` |
| 12/11 | Tâm dùng `gemini-3.6-flash` → thử so sánh, chốt Ôn tập dùng `REVIEW_LLM_MODEL=gemini-3.5-flash-lite` riêng (mục GĐ5 RealAI) | — |
| 12/11 | Khôi push `course_tracking_service` → gộp thử ở `tuan/merge-khoi`, nối `course_gateway` hàm thật, bỏ `has_first_pass`; **T1–T9 đạt 9/9** | Đã đưa vào `tuan/future-auth`; sửa thêm L1 (bỏ khóa lúc đang chấm) |
| | | |
