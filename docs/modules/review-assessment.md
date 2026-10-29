# Module: Ôn tập & Đánh giá kiến thức

Đặc tả nghiệp vụ và API contract của module. Đây là nguồn chi tiết duy nhất cho module này; bảng tóm tắt endpoint ở `docs/api-endpoints.md` §10, schema đầy đủ ở `docs/database-design.md` §6, quy tắc kỹ thuật chung ở `docs/backend-rules.md`, quyết định và điểm còn mở ở `docs/decisions.md`.

Mã quy tắc `RV-Rxx` dùng để tham chiếu từ `review-assessment.tests.md` và code review.

---

## 1. Phạm vi

**Owner: Tuấn** (D-OWN-01) · **Đặc tả: SPEC CONFIRMED** — trừ RV-R03, RV-R10, RV-R13 đang **BLOCKED** vì T16 chưa được nhóm tick (`docs/decisions.md` §3) và các điểm còn mở ở §10 · **Implementation: NOT IMPLEMENTED**

Bài ôn tập tính **theo khóa học** (D01): 20 câu trắc nghiệm lấy từ các kỹ năng mà khóa dạy; làm đạt thì khóa học thành `completed` và kỹ năng của khóa được ghi nhận `known`.

**Thuộc module:**

| Endpoint |
|---|
| `GET /api/courses/{course_id}/review` |
| `POST /api/courses/{course_id}/review-attempts` |
| `GET /api/review-attempts/{attempt_id}` |
| `POST /api/review-attempts/{attempt_id}/submit` |
| `GET /api/me/review-history` |
| `GET /api/me/review-history/{attempt_id}` |

**Không thuộc module** (chỉ là dependency, xem mục 9):

- `/api/admin/questions*` (T19–T21) — quản trị ngân hàng câu hỏi. Module này chỉ **đọc** `Question`.
- `GET/PATCH /api/me/skills` — module Xác thực & Hồ sơ.
- `POST /api/courses/{id}/join`, chuyển trạng thái StudentCourse khác — module Course Tracking.
- Cập nhật `LearningPath.status` (T18) — module Learning Path, `[ND-24]`.
- Các endpoint cũ `/api/skills/{skill_id}/review*` — **đã bỏ** (T11). Không implement.

---

## 2. File liên quan

Theo `docs/structure.md` (đã cập nhật):

| Lớp | File |
|---|---|
| Router | `backend/app/routers/reviews.py` |
| Schema | `backend/app/schemas/review.py` |
| Model (thuộc module) | `backend/app/models/question.py`, `backend/app/models/review_attempt.py`, `backend/app/models/review_answer.py` |
| Model (dùng) | `student_course.py`, `course_skill.py`, `course.py`, `skill.py`, `user_skill.py`, `user.py` |
| Service | `backend/app/services/review_service.py` |
| Core | `backend/app/core/email.py` (dùng chung), `core/config.py` (`REVIEW_PASS_PERCENT`, `FRONTEND_URL`) |
| Repository | `backend/app/repositories/` (STRUCTURE chưa đặt tên file) |
| Test | `backend/tests/test_review.py` |

Frontend tương ứng (tham khảo): `api/review.api.js`, `pages/review/*` (route `/review/:courseId`), `components/review/*`, `components/profile/ReviewHistoryList.jsx`.

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §6 và §3.

### Bảng thuộc module

| Bảng | Khóa | Ràng buộc quan trọng | Module ghi? |
|---|---|---|---|
| `Question` | PK `question_id` | `skill_id` NN FK → Skill; `options` JSONB đúng 4 đáp án; `correct_index` 0–3; `is_active` NN DEFAULT TRUE | **Chỉ đọc** (admin ghi) |
| `ReviewAttempt` | PK `attempt_id` | `student_course_id` NN FK → StudentCourse (CASCADE); `score_percent` NUMERIC(5,2) 0–100 NULL; `passed` NULL; `attempted_at` NN; `submitted_at` NULL (`[ND-31]`) | Có |
| `ReviewAnswer` | PK (`attempt_id`, `question_id`) | `position` 1–20 NN; `selected_index` 0–3 NULL; `is_correct` NULL; FK → Question **RESTRICT** | Có |

### Bảng của module khác mà module này dùng

| Bảng | Đọc / ghi | Mục đích |
|---|---|---|
| `StudentCourse` | Đọc + ghi `status`, `completed_at` | Điều kiện bắt đầu; đánh dấu `completed` khi đạt |
| `CourseSkillRelation` | Đọc | Kỹ năng của khóa → nguồn câu hỏi, kỹ năng cần ghi nhận |
| `UserSkill` | Ghi (upsert `known`) | Ghi nhận kỹ năng khi đạt (bảng của module Auth/Profile) |
| `Course` | Đọc | Kiểm tra khóa tồn tại; tên khóa trong email |
| `User` | Đọc | Email nhận kết quả |

### Quan hệ

```text
User 1 ──< StudentCourse >── 1 Course
                │                 │
                1                 └──< CourseSkillRelation >── Skill ──< Question
                │                                               │          │
                └──< ReviewAttempt 1 ──< ReviewAnswer >─────────┼──────────┘
                                                                │
User 1 ──< UserSkill >──────────────────────────────────────────┘
```

Người sở hữu một attempt = `ReviewAttempt → StudentCourse.user_id`.

---

## 4. API contract

Quy ước chung (xác thực, cấu trúc lỗi): `docs/backend-rules.md`. Mọi endpoint yêu cầu xác thực (người dùng, mọi role).

### 4.1. `GET /api/courses/{course_id}/review`

| Mục | Nội dung |
|---|---|
| Path | `course_id` |
| Response | **200** `available` (true/false), kèm lý do nếu `false` |
| Điều kiện `available` | Tổng số câu `is_active = true` của mọi kỹ năng khóa dạy (qua CourseSkillRelation) ≥ 20 (RV-R02) |
| Lỗi | **404** khóa học không tồn tại; **401** |
| Chưa chốt | Khóa không có kỹ năng nào `[ND-28]` |

### 4.2. `POST /api/courses/{course_id}/review-attempts`

| Mục | Nội dung |
|---|---|
| Path | `course_id` |
| Body | — |
| Điều kiện | Người dùng có StudentCourse với khóa này ở `ongoing` hoặc `completed` (RV-R03); khóa đủ câu hỏi (RV-R02) |
| Hành vi | Đã có bài đang dở của StudentCourse này → trả lại bài đó (RV-R04). Ngược lại → tạo ReviewAttempt + 20 ReviewAnswer trong một transaction (RV-R06) |
| Response | `attempt_id` + 20 câu, mỗi câu **chỉ** gồm `question_id`, `content`, `options`, `position` (RV-R07). Mã 200/201 khi trả bài dở: `[ND-33]` |
| Lỗi | **409** chưa có StudentCourse hoặc chưa tham gia (hướng dẫn bấm "Tham gia"); **409** khóa thiếu câu hỏi; **404** khóa học không tồn tại; **401** |
| Chưa chốt | Thời gian làm bài `[ND-21]`; đồng thời `[ND-29]`; thuật toán chia câu `[ND-20]` |

### 4.3. `GET /api/review-attempts/{attempt_id}`

| Mục | Nội dung |
|---|---|
| Path | `attempt_id` |
| Response | **200** trạng thái lần làm bài + câu hỏi (`question_id`, `content`, `options`, `position`) — **không** có `correct_index`, `explanation` |
| Lỗi | **404** không tồn tại **hoặc** không phải chủ sở hữu (RV-R08); **401** |
| Chưa chốt | Nội dung trả về khi attempt đã nộp `[ND-26]` |

### 4.4. `POST /api/review-attempts/{attempt_id}/submit`

| Mục | Nội dung |
|---|---|
| Path | `attempt_id` |
| Body | `{"answers": [{"question_id": int, "selected_index": int}]}` |
| Validation | `selected_index` ∈ 0–3; câu không gửi / bỏ trống tính là sai (RV-R10). `question_id` lạ hoặc trùng: `[ND-22]` |
| Điều kiện | Chủ sở hữu (RV-R08); chưa nộp (RV-R13) |
| Hành vi | Transaction nộp bài (mục 7) → commit → trả kết quả → email chạy nền (RV-R18) |
| Response | **200** `score_percent`, `passed`, số câu đúng |
| Lỗi | **409** đã nộp rồi; **404** không tồn tại hoặc không phải chủ sở hữu; **422** dữ liệu sai; **401** |
| Chưa chốt | `[ND-22, ND-23, ND-24, ND-25, ND-28, ND-29]` |

### 4.5. `GET /api/me/review-history`

| Mục | Nội dung |
|---|---|
| Query | `course_id` (tùy chọn), `passed` = `true`\|`false` (tùy chọn), `page`, `page_size` |
| Response | **200** danh sách phân trang (`items`, `total`, `page`, `page_size`) các lần làm bài của người dùng hiện tại |
| Lỗi | **401** |
| Chưa chốt | Có gồm bài đang dở không `[ND-34]`; các trường hiển thị theo wireframe 12 (kỹ năng, mức, điểm "x/20") `[ND-27]` |

### 4.6. `GET /api/me/review-history/{attempt_id}`

| Mục | Nội dung |
|---|---|
| Path | `attempt_id` |
| Response | **200** chi tiết lần làm bài: từng câu với đáp án đã chọn, đáp án đúng (`correct_index`), giải thích (`explanation`), đúng/sai — **chỉ sau khi nộp** |
| Lỗi | **404** không tồn tại hoặc không phải chủ sở hữu; **401** |
| Chưa chốt | Attempt chưa nộp `[ND-26]` |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| RV-R01 | Bài ôn tập tính theo khóa học; 20 câu trắc nghiệm, mỗi câu 4 đáp án. | D01, T11, `.docx` 6.1 |
| RV-R02 | Khóa có bài ôn tập khi tổng câu `is_active = true` của các kỹ năng khóa dạy ≥ 20; không cần mỗi kỹ năng đủ 20 câu. | D04, `.docx` 6.1 |
| RV-R03 | Chỉ bắt đầu khi StudentCourse của người dùng với khóa đó ở `ongoing` hoặc `completed` (ôn lại). Không có / trạng thái khác → 409. Khóa thiếu câu → 409. | T16, D10, `.docx` 6.2 |
| RV-R04 | Mỗi StudentCourse tối đa **một** bài đang dở (`submitted_at` trống); bắt đầu lại trả bài dở đó. | D03 |
| RV-R05 | Làm lại không giới hạn số lần; số lần = số ReviewAttempt theo `student_course_id`. | D03 |
| RV-R06 | Khi bắt đầu, server gom câu `is_active = true` của mọi kỹ năng khóa dạy, chia đều giữa các kỹ năng, chọn ngẫu nhiên 20 câu (trộn thứ tự) và ghi 20 dòng ReviewAnswer (`position` 1–20, `selected_index` trống) cùng ReviewAttempt trong một transaction. Chi tiết chia: `[ND-20]`. | T14, D04, G5 |
| RV-R07 | `correct_index` và `explanation` **không** trả ở bất kỳ endpoint làm bài nào trước khi nộp; chỉ xuất hiện ở `GET /api/me/review-history/{attempt_id}` sau khi nộp. | T15, G9 |
| RV-R08 | Chỉ chủ sở hữu xem/nộp được attempt; attempt của người khác → **404** (không phải 403). | T15 |
| RV-R09 | Khi nộp, server chỉ chấm đúng 20 dòng ReviewAnswer đã tạo; client không thêm được câu hỏi. | T14, G5 |
| RV-R10 | Câu bỏ trống khi nộp tính là sai (`is_correct = FALSE`). | T16 |
| RV-R11 | `score_percent` = phần trăm số câu đúng trên 20 (ví dụ 17/20 = 85). | `.docx` 6.2, G4 |
| RV-R12 | `passed = score_percent ≥ REVIEW_PASS_PERCENT` (60), lưu tại lúc nộp; đổi ngưỡng sau này không đổi kết quả cũ. | D02, T28 |
| RV-R13 | Mỗi attempt chỉ nộp một lần; nộp lần hai → 409. | T16 |
| RV-R14 | Nếu đạt: `StudentCourse.status → completed`, ghi `completed_at`. Khóa đã `completed` thì giữ nguyên status và `completed_at` (ôn lại chỉ lưu thêm lịch sử). | T13, D10 |
| RV-R15 | Nếu đạt: thêm/cập nhật `UserSkill = known` cho **mọi** kỹ năng của khóa (qua CourseSkillRelation). Trường hợp ôn lại: `[ND-23]`. | T13 |
| RV-R16 | Không đạt: không đổi StudentCourse, không đổi UserSkill. | `.docx` 6.2 (bước 3–4 chỉ "nếu đạt") |
| RV-R17 | Nộp bài (chấm, ghi điểm, cập nhật StudentCourse, UserSkill) là **một transaction**; bước nào lỗi → rollback toàn bộ. | T13, G4 |
| RV-R18 | Sau khi commit: trả ngay `score_percent`, `passed`, số câu đúng; rồi chạy nền gửi email kết quả tới `User.email` (tên khóa, điểm %, Đạt/Không đạt, số câu đúng/20, thời gian nộp, link `FRONTEND_URL/review/history/{attempt_id}`, **không** kèm đáp án). Gửi lỗi chỉ ghi log, không rollback, không báo lỗi. Gửi mọi lần hay chỉ khi đạt: `[ND-25]`. | T29 |
| RV-R19 | `GET /api/me/review-history` lọc theo `course_id`, `passed`, có phân trang. | T17 |
| RV-R20 | Frontend không gửi request cập nhật kỹ năng sau khi nộp; chỉ tải lại dữ liệu. | STRUCTURE §3 |
| RV-R21 | Điểm ôn tập **không** được dùng để xếp hạng gợi ý khóa học. | CONVENTIONS §2, api-endpoints §14 |
| RV-R22 | `completed` của khóa học chỉ đến từ việc làm đạt bài ôn tập, không phải từ việc mở URL ngoài. | CONVENTIONS §2 |

---

## 6. Luồng nghiệp vụ

```text
1. Kiểm tra bài ôn tập
   GET /courses/{id}/review → khóa tồn tại? (404) → đếm câu active của các kỹ năng khóa
   → available = (tổng ≥ 20), kèm lý do nếu false

2. Bắt đầu
   POST /courses/{id}/review-attempts
   → tìm StudentCourse(user hiện tại, course)
       không có / không phải ongoing|completed → 409 (hướng dẫn "Tham gia")
   → khóa thiếu câu → 409
   → đã có attempt chưa nộp? → trả lại attempt đó          (D03)
   → [transaction] tạo ReviewAttempt + chọn 20 câu + ghi 20 ReviewAnswer
   → trả attempt_id + 20 câu (KHÔNG có đáp án)              (T15)

3. Làm bài (client)
   GET /review-attempts/{id} → câu hỏi (KHÔNG có đáp án); không phải chủ → 404

4. Nộp bài
   POST /review-attempts/{id}/submit {answers}
   → không phải chủ → 404 | đã nộp → 409
   → [transaction]
        (1) chấm 20 dòng ReviewAnswer: ghi selected_index, is_correct (trống = sai)
        (2) ghi score_percent, passed, submitted_at
        (3) nếu đạt: StudentCourse → completed + completed_at (đã completed thì giữ)
        (4) nếu đạt: upsert UserSkill = known cho mọi kỹ năng của khóa
        (5) [ND-24] kiểm tra LearningPath — CHƯA CHỐT, không implement
     commit (lỗi bất kỳ → rollback toàn bộ)
   → trả score_percent, passed, số câu đúng
   → chạy nền: gửi email kết quả ([ND-25])

5. Xem lại
   GET /me/review-history?course_id=&passed=&page=&page_size=
   GET /me/review-history/{id} → chi tiết có đáp án đúng + giải thích (chỉ khi đã nộp)
```

---

## 7. Transaction

| Thao tác | Các ghi trong cùng transaction | Ngoài transaction | Nguồn |
|---|---|---|---|
| Bắt đầu | Tạo ReviewAttempt + 20 ReviewAnswer | — | T14, `.docx` 6.3 |
| Nộp bài | ReviewAnswer (20 dòng) + ReviewAttempt (điểm, passed, submitted_at) + StudentCourse (nếu đạt) + UserSkill (nếu đạt). Bước LearningPath: `[ND-24]` | Gửi email (sau commit) | T13, T29, G4 |

Ví dụ hậu quả nếu không dùng transaction (G4): khóa đã `completed` nhưng UserSkill chưa cập nhật → lộ trình không bao giờ nhận kỹ năng đó.

Xử lý đồng thời cho bắt đầu / nộp bài: `[ND-29]`.

---

## 8. Bảo mật

| Chủ đề | Quy tắc | Nguồn |
|---|---|---|
| Lộ đáp án | Schema câu hỏi khi làm bài không có `correct_index`, `explanation` — kể cả trường ẩn trên giao diện, vì DevTools đọc được mọi dữ liệu API | T15, G9 |
| IDOR | Attempt của người khác → 404; truy vấn luôn ràng buộc theo người dùng hiện tại qua StudentCourse | T15 |
| Gian lận câu hỏi | Server chọn và lưu sẵn 20 câu; chỉ chấm các câu đó; client không chọn câu | T14, G5 |
| Chấm điểm | Chỉ server chấm; client không gửi điểm hay `is_correct` | `.docx` 6.3 |
| Email | Không chứa đáp án | T29 |
| Ngưỡng đạt | Đọc từ cấu hình, không hard-code | T28 |

---

## 9. Phụ thuộc với module khác

| Module | Chiều | Nội dung |
|---|---|---|
| Xác thực & Hồ sơ | Ôn tập → Auth | `get_current_user`; ghi `UserSkill = known` (bảng của Auth/Profile); dùng chung `core/email.py`; `/me/review-history*` nằm trong namespace `/me` nhưng thuộc `routers/reviews.py` |
| Course Tracking | Ôn tập ↔ Course Tracking | Đọc StudentCourse để kiểm tra điều kiện; ghi `completed`/`completed_at` khi đạt. Người dùng phải `join` (ongoing) trước khi làm bài |
| Quản trị câu hỏi | Admin → Ôn tập | Ngân hàng câu hỏi do `/api/admin/questions*` quản lý (ngoài phạm vi). Câu đã dùng chỉ bị `is_active = false`, không bị xóa (FK RESTRICT) |
| Learning Path | Ôn tập → Learning Path | Bước 5 (T18): `[ND-24]`, hàm thuộc `learning_path_service` (Tâm) |
| Gợi ý khóa học | — | Không được dùng điểm ôn tập (RV-R21) |

---

## 10. Điểm còn mở

`ND-20`, `ND-21`, `ND-22`, `ND-23`, `ND-24`, `ND-25`, `ND-26`, `ND-27`, `ND-28`, `ND-29`, `ND-30`, `ND-31`, `ND-33`, `ND-34` — chi tiết trong `docs/decisions.md` §4.2.
