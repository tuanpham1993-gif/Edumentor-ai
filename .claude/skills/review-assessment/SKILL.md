---
name: review-assessment
description: Điểm vào cho module Ôn tập & Đánh giá kiến thức (do Tuấn phụ trách) của project EduMentor AI — bài ôn tập 20 câu theo khóa học, GET /api/courses/{course_id}/review, POST /api/courses/{course_id}/review-attempts, GET /api/review-attempts/{id}, submit, chấm điểm, điểm đạt REVIEW_PASS_PERCENT, đánh dấu khóa học completed, cập nhật UserSkill known, transaction nộp bài, email kết quả, GET /api/me/review-history, bảng Question/ReviewAttempt/ReviewAnswer. Dùng skill này mỗi khi implement, sửa, review hoặc viết test cho các phần trên, kể cả khi người dùng chỉ nói "làm bài test", "ôn tập", "chấm điểm", "lịch sử bài test" hay mở routers/reviews.py, services/review_service.py, schemas/review.py, tests/test_review.py. Skill project này được ưu tiên hơn skill cấp user edumentor-review trong repo này.
---

# Review & Assessment — EduMentor AI

```text
Owner:          Tuấn                              (D-OWN-01)
Module:         Review & Assessment
Status:         SPEC CONFIRMED
Implementation: NOT IMPLEMENTED
Business decisions: một phần BLOCKED (T16) / PENDING (§4.3)
```

Skill này là điểm vào cho module Ôn tập: phạm vi, trạng thái từng phần, nguồn cần đọc, điều cấm. Chi tiết nghiệp vụ nằm trong `docs/` — đọc ở đó, không làm theo trí nhớ.

**Ưu tiên:** skill project-local này và tài liệu trong repo được ưu tiên cho repository này. Không dùng skill EduMentor cấp user/chung (`edumentor-review`, `database-schema`) khi chúng mâu thuẫn với tài liệu project.

## 0. Trạng thái — luôn phân biệt

| Trạng thái | Nghĩa | Claude được làm gì |
|---|---|---|
| **SPEC CONFIRMED** | Phạm vi/quy tắc đã được nhóm xác nhận ("Nhóm đồng ý" / "Đã chốt" trong `docs/EduMentor_Checklist_Da_Sua_API.xlsx`) và không có mâu thuẫn | Hỗ trợ implement theo `docs/` |
| **IMPLEMENTED** | Đã có code chạy | Hiện **chưa** có endpoint nào ở trạng thái này |
| **PENDING** | Chưa tick, hoặc có `ND-xx` chưa chốt | Không implement phần đó; làm phần còn lại và nói rõ chỗ chờ |
| **BLOCKED** | Phần bắt buộc của luồng phụ thuộc vào hạng mục chưa tick | Dừng, hỏi Tuấn trước khi code phần đó |
| **CONFLICT** | Hai nguồn mô tả khác nhau | Không tự chọn; yêu cầu nhóm quyết định |

Không dùng "DONE" cho phần chưa có code. Cột "Đã làm xong" trong sheet "Endpoint (bản mới)" hiện ☐ cho mọi endpoint.

## 0.1. Phân công

| Module | Owner | Status |
|---|---|---|
| Review & Assessment | **Tuấn** | SPEC CONFIRMED — NOT IMPLEMENTED |
| Auth & Profile | **Tuấn** | SPEC CONFIRMED — NOT IMPLEMENTED (skill `auth-profile`) |
| Course Tracking | Không phải Tuấn | OUT OF SCOPE |
| Feedback | Chưa rõ (Khôi/Tâm) | PENDING |
| Learning Path (gồm T18) | Người khác | OUT OF SCOPE |
| Admin Questions | CONFLICT-SCOPE-01 | DO NOT ASSUME |

Nguồn đầy đủ: `docs/decisions.md` §2 "Phân công".

## 1. Nguồn sự thật (đọc theo thứ tự)

1. `docs/EduMentor_Checklist_Da_Sua_API.xlsx` — trạng thái tick (đã chép vào `docs/decisions.md` §2–§3).
2. `docs/decisions.md` — D01–D11, trạng thái T-item, danh sách `ND-xx`.
3. `docs/modules/review-assessment.md` — contract (§4), quy tắc `RV-Rxx` (§5), luồng (§6), transaction (§7). **Lưu ý:** RV-R03, RV-R10, RV-R13 trong file này đang dựa trên T16 chưa tick → xem §4 bên dưới, trạng thái ở skill này thắng.
4. `docs/api-endpoints.md` §10, `docs/backend-rules.md`, `docs/database-design.md` §6 (và §3.2, §3.3).
5. `docs/modules/review-assessment.tests.md` — kịch bản test.

`docs/conventions.md` §2 "Ôn tập" và `README.md` chỉ tóm tắt và trỏ về tài liệu module (AUD-03, AUD-04 đã sửa) — không dùng chúng làm nguồn quy tắc chi tiết.

## 2. Phạm vi

Owner Tuấn (D-OWN-01; sheet "Endpoint (bản mới)" cũng ghi "Phụ trách = Tuấn" cho §10). Tất cả endpoint dưới đây: **Implementation = NOT IMPLEMENTED**.

| Method | Endpoint | Đặc tả | Nguồn xác nhận | Phần còn PENDING / BLOCKED |
|---|---|---|---|---|
| GET | `/api/courses/{course_id}/review` | **SPEC CONFIRMED** | T11 ☑, D01, D04 | Khóa không có kỹ năng (ND-28) |
| POST | `/api/courses/{course_id}/review-attempts` | **SPEC CONFIRMED (một phần)** | T11 ☑, T14 ☑, T15 ☑, D03, D04, D10 | Điều kiện 409 (**BLOCKED — T16**); cách chọn câu (**CONFLICT — ND-20**); "bài dở" định nghĩa theo `submitted_at` (ND-31); mã trả bài dở (ND-33); khóa không tồn tại 404 hay 409 (AUD-05) |
| GET | `/api/review-attempts/{attempt_id}` | **SPEC CONFIRMED** | T15 ☑ | Response sau khi nộp (ND-26) |
| POST | `/api/review-attempts/{attempt_id}/submit` | **SPEC CONFIRMED (một phần)** | T13 ☑, T29 ☑, D02 | Nộp lần hai 409 và câu trống = sai (**BLOCKED — T16**); bước 5 LearningPath (ND-24); `submitted_at` (ND-31); email mọi lần hay chỉ khi đạt (ND-25); nội dung email (CONFLICT-EMAIL); câu hỏi lạ/trùng (ND-22); ôn lại có upsert UserSkill (ND-23) |
| GET | `/api/me/review-history` | **SPEC CONFIRMED** | T17 ☑ | Có gồm bài dở không (ND-34); trường hiển thị wireframe (ND-27) |
| GET | `/api/me/review-history/{attempt_id}` | **SPEC CONFIRMED** | T15 ☑ | Attempt chưa nộp (ND-26) |

**Đã bỏ — không implement:** `GET /api/skills/{skill_id}/review`, `POST /api/skills/{skill_id}/review-attempts` (T11 ☑).

**Admin Questions — CONFLICT-SCOPE-01, DO NOT ASSUME:** `/api/admin/questions*` (T19, T20, T21 ☑) — sheet Endpoint ghi "Phụ trách = Tuấn", nhưng Tuấn đã loại khỏi phạm vi skill (ND-SCOPE-2). Không tự gán, không implement khi chưa giải quyết. Module này chỉ **đọc** `Question`.

**Không thuộc skill này:** `GET/PATCH /api/me/skills` (skill `auth-profile`; dòng lặp ở §10 đang chờ T12 ☐ — ND-30); `join` và các chuyển trạng thái StudentCourse khác (Course Tracking); cập nhật `LearningPath.status` (T18 ☐, Tâm — ND-24); Feedback (T22–T25 ☐, Khôi).

File được làm: `routers/reviews.py`, `schemas/review.py`, `models/question.py`, `models/review_attempt.py`, `models/review_answer.py`, `services/review_service.py`, repository tương ứng, `tests/test_review.py`, migration cho 3 bảng. Dùng chung `core/email.py` với `auth-profile`.

## 3. Endpoint contract (chỉ phần đã xác nhận)

Chi tiết: `docs/modules/review-assessment.md` §4. Mọi endpoint yêu cầu xác thực.

| Endpoint | Request | Response đã xác nhận | Lỗi đã xác nhận | Nguồn |
|---|---|---|---|---|
| `GET /courses/{id}/review` | — | `available` + lý do nếu false | 404 khóa không tồn tại | XLSX Endpoint, T11 |
| `POST /courses/{id}/review-attempts` | — | `attempt_id` + 20 câu, mỗi câu chỉ `question_id`, `content`, `options`, `position` | 409 — **BLOCKED (T16)** | T11, T14, T15 |
| `GET /review-attempts/{id}` | — | Trạng thái + câu hỏi, không có đáp án | 404 không phải chủ sở hữu | T15 |
| `POST /review-attempts/{id}/submit` | `answers: [{question_id, selected_index}]` | `score_percent`, `passed`, số câu đúng | 404; 409 đã nộp — **BLOCKED (T16)**; lỗi validate theo ND-15 | T13, T29, XLSX Endpoint |
| `GET /me/review-history` | `?course_id=`, `?passed=`, `page`, `page_size` | Danh sách phân trang | 401 | T17 |
| `GET /me/review-history/{id}` | — | Từng câu + đáp án đã chọn + `correct_index` + `explanation` (chỉ sau khi nộp) | 404 | T15 |

Lỗi validate: dùng mã theo quy ước dự án đã được duyệt; **không** tự đặt mã mới — 400 hay 422 đang là ND-15.

## 4. Quy tắc

### 4.1. Bắt buộc (SPEC CONFIRMED)

| Quy tắc | Nguồn |
|---|---|
| Bài ôn tập tính theo **khóa học**, 20 câu trắc nghiệm; không thêm `skill_id` vào ReviewAttempt | D01, T11, RV-R01 |
| Khóa có bài khi tổng câu `is_active = true` của các kỹ năng khóa dạy ≥ 20 | D04, RV-R02 |
| Mỗi khóa tối đa một bài đang dở; bắt đầu lại trả bài dở đó; làm lại không giới hạn | D03, RV-R04, RV-R05 |
| Khóa đã `completed` được ôn lại; kết quả mới chỉ thêm vào lịch sử, không đổi status/`completed_at` | D10, RV-R14 |
| Server chọn và lưu sẵn câu hỏi của lần làm bài (ReviewAnswer) khi bắt đầu; khi nộp chỉ chấm các câu đã lưu | T14, RV-R06, RV-R09 |
| Không trả `correct_index`, `explanation` ở bất kỳ endpoint làm bài nào trước khi nộp | T15, RV-R07 |
| Attempt của người khác → 404 (không phải 403) | T15, RV-R08 |
| `passed = score_percent ≥ REVIEW_PASS_PERCENT` (nhóm chốt 60), đọc từ cấu hình, lưu cố định lúc nộp | D02, T28, RV-R12 |
| Nếu đạt: StudentCourse → `completed` + `completed_at`; UserSkill = `known` cho mọi kỹ năng của khóa — **cùng một transaction** với việc chấm điểm; lỗi → rollback toàn bộ | T13, G4, RV-R14, RV-R15, RV-R17 |
| Không đạt: không đổi StudentCourse, UserSkill | `.docx` 6.2, RV-R16 |
| Sau commit: trả kết quả ngay; email kết quả chạy nền, không kèm đáp án; gửi lỗi chỉ ghi log | T29, RV-R18 |
| Lịch sử lọc theo `course_id`, `passed`, có phân trang | T17, RV-R19 |
| Điểm ôn tập không dùng xếp hạng gợi ý khóa học; frontend không gửi request cập nhật kỹ năng | CONVENTIONS §2, STRUCTURE §3, RV-R20, RV-R21 |

Ghi chú T13: cột ghi chú của nhóm có "(tạm thời chưa quyết định)" đặt sau bước 5. `.docx` 6.2 ghi rõ rollback cho bước 1–4 và tách bước 5 thành "nhóm chưa chốt" → rollback bước 1–4 được coi là SPEC CONFIRMED; bước 5 là ND-24.

### 4.2. BLOCKED — T16 chưa được nhóm xác nhận

Các quy tắc sau có trong `review-assessment.md` nhưng chỉ có nguồn từ T16 (☐) và `.docx` → **chưa được implement như rule đã chốt**:

- RV-R03: chưa có StudentCourse / không ở `ongoing`/`completed` → 409; khóa thiếu câu → 409.
- RV-R10: câu bỏ trống khi nộp = sai.
- RV-R13: nộp lần hai → 409.

Gặp các điểm này: dừng và hỏi Tuấn. (RV-R11 tính điểm trên 20 câu cũng gián tiếp phụ thuộc RV-R10.)

### 4.3. PENDING — không implement cho tới khi chốt

| Mã | Nội dung |
|---|---|
| ND-20 / AUD-11 | **CONFLICT**: T14 (☑) ghi "lấy 60 câu ngẫu nhiên … ghi sẵn 20 câu"; `.docx` 6.3 ghi "chọn ngẫu nhiên 20 câu", chia đều theo kỹ năng. Phần dư và thiếu câu chưa quy định. Không tự chọn cách nào. |
| ND-31 / AUD-02 | `submitted_at` (T27 ☐). Không coi là quyết định đã chốt; định nghĩa "bài dở" (RV-R04) và "thời gian nộp" trong email phụ thuộc mục này. |
| ND-24 | Bước 5 cập nhật LearningPath (T13, T18 ☐). Không implement. |
| ND-25 | Email gửi mọi lần hay chỉ khi đạt. |
| CONFLICT-EMAIL | Ghi chú T29 của nhóm: email "chỉ gửi link, khóa học nào, Đậu/Rớt + Điểm"; `.docx` 6.2 thêm "số câu đúng/20, thời gian nộp". |
| AUD-05 | Khóa không tồn tại khi bắt đầu: 404 (quy ước chung) hay 409 (`.docx`: chưa có StudentCourse). |
| ND-15 / AUD-08 | Mã lỗi validate 400 hay 422. |
| ND-14, ND-16, ND-17 | Danh mục `error.code`; lớp commit transaction; index. |
| ND-21, ND-22, ND-23, ND-26, ND-27, ND-28, ND-29, ND-30, ND-33, ND-34 | Xem `docs/decisions.md` §4.2. |

## 5. Không được làm

- Không tự chọn phương án cho mục PENDING/BLOCKED/CONFLICT; không đặt giá trị mặc định thay nhóm.
- Không thêm endpoint, bảng, cột, ràng buộc, schema ngoài `docs/`; không implement endpoint theo kỹ năng đã bỏ.
- Không sửa `docs/decisions.md` hay Excel để biến ☐ thành ☑.
- Không implement `/api/admin/questions*` khi chưa giải quyết CONFLICT-SCOPE-01.

## 6. Quy trình implement

1. Xác định endpoint/quy tắc trong `review-assessment.md`; đối chiếu trạng thái ở §2–§4 của skill này. Có BLOCKED/CONFLICT trên đường đi → hỏi Tuấn trước.
2. Model + migration khớp `database-design.md` §6 (cột `submitted_at`: chờ ND-31).
3. Schema câu hỏi khi làm bài không có trường đáp án.
4. Repository → Service (giữ transaction §7 của tài liệu module) → Router; email qua `BackgroundTasks` sau commit.
5. Test theo `review-assessment.tests.md`; bỏ qua kịch bản có cột "Chờ" và kịch bản dựa trên RV-R03/R10/R13 cho tới khi T16 được tick.
6. Chạy `pytest`, `black`, `ruff`. Chỉ khi code chạy và test qua mới coi là IMPLEMENTED.

Khuyến nghị kỹ thuật (không phải yêu cầu nghiệp vụ): ràng buộc truy vấn attempt theo người dùng hiện tại ngay trong câu truy vấn; dùng schema riêng cho câu hỏi khi làm bài và cho chi tiết sau khi nộp.

## 7. Kỳ vọng kiểm thử

Kịch bản đã đặc tả và **không** phụ thuộc mục chưa chốt (từ `review-assessment.tests.md`): RV-T01–T05, T10–T12, T14, T18, T21, T30–T32, T40–T44 (T40: phần `submitted_at` chờ ND-31), T50 (phần status), T51–T52, T60–T63, T70–T76, T78, T80. RV-T20 chờ AUD-05; RV-T46 chờ ND-15.

Phụ thuộc T16 (BLOCKED): RV-T15–T17, T19, T45, T48. Phụ thuộc ND khác: xem cột "Chờ".

**TEST COVERAGE GAP** (chưa có kịch bản trong tài liệu — chưa tự thêm):

- RV-R05: bắt đầu lượt mới sau khi đã nộp bài trượt.
- RV-R14/RV-R16: ôn lại khóa đã `completed` mà trượt → status giữ nguyên.
- 401 cho `POST .../review-attempts`, `POST .../submit`, `GET /review-attempts/{id}`.
