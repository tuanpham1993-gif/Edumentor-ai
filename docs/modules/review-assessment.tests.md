# Kịch bản kiểm thử — Ôn tập & Đánh giá kiến thức

Mô tả **kịch bản** (chưa phải test code) cho `backend/tests/test_review.py`. Mỗi kịch bản trỏ tới quy tắc trong `docs/modules/review-assessment.md` (`RV-Rxx`) hoặc mục API (`§4.x`). CONVENTIONS §6 bắt buộc có test chấm điểm ôn tập.

Kịch bản có cột "Chờ" = phụ thuộc một `[NEEDS DECISION]`: chỉ viết test khi điểm đó đã chốt.

**Dữ liệu mẫu chung**

- Khóa **C1** dạy 3 kỹ năng S1, S2, S3 (CourseSkillRelation); mỗi kỹ năng 10 câu `is_active = true` (tổng 30 ≥ 20).
- Khóa **C2** dạy 1 kỹ năng S4 với 15 câu active (tổng < 20).
- Học viên **A** có StudentCourse(C1) = `ongoing`; học viên **B** không theo dõi C1.
- `REVIEW_PASS_PERCENT = 60`.
- `send_email` được giả lập để kiểm tra có được gọi hay không.

---

## 1. Kiểm tra bài ôn tập — `GET /api/courses/{course_id}/review`

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| RV-T01 | — | A gọi cho C1 | 200, `available = true` | RV-R02 | |
| RV-T02 | — | A gọi cho C2 | 200, `available = false` + lý do thiếu câu hỏi | RV-R02 | |
| RV-T03 | C1 có 25 câu nhưng 10 câu `is_active = false` | A gọi cho C1 | `available = false` (chỉ đếm câu active) | RV-R02 | |
| RV-T04 | — | Khóa không tồn tại | 404 | §4.1 | |
| RV-T05 | — | Không có token | 401 | backend-rules §2 | |
| RV-T06 | Khóa không có kỹ năng nào | Gọi | Theo quyết định | — | ND-28 |

## 2. Bắt đầu — `POST /api/courses/{course_id}/review-attempts`

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| RV-T10 | A ongoing C1 | Bắt đầu | Trả `attempt_id` + đúng 20 câu, `position` 1–20; CSDL có 1 ReviewAttempt + 20 ReviewAnswer (`selected_index` trống) | RV-R06 | Mã 200/201: ND-33 |
| RV-T11 | Như RV-T10 | Kiểm tra response | **Không** có `correct_index`, `explanation` ở bất kỳ câu nào (kể cả lồng sâu) | RV-R07 | |
| RV-T12 | Như RV-T10 | Kiểm tra 20 câu | Mọi câu thuộc S1/S2/S3, đều `is_active = true`, không trùng | RV-R06 | |
| RV-T13 | Như RV-T10 | Kiểm tra phân bố | Số câu mỗi kỹ năng chênh lệch không quá 1 (ví dụ 7/7/6) | RV-R06, G5 | ND-20 (phần dư, thiếu câu) |
| RV-T14 | A đã có bài dở C1 | Bắt đầu lại | Trả **cùng** `attempt_id`; không tạo attempt mới | RV-R04 | |
| RV-T15 | B không có StudentCourse C1 | Bắt đầu | 409 | RV-R03 | |
| RV-T16 | StudentCourse(C1) = `bookmarked` | Bắt đầu | 409 | RV-R03 | |
| RV-T17 | StudentCourse(C1) = `abandoned` | Bắt đầu | 409 | RV-R03 | |
| RV-T18 | StudentCourse(C1) = `completed` | Bắt đầu | Thành công (ôn lại) | RV-R03, D10 | |
| RV-T19 | A ongoing C2 | Bắt đầu | 409 (thiếu câu hỏi) | RV-R03 | |
| RV-T20 | — | Khóa không tồn tại | 404 | §4.2 | |
| RV-T21 | Giả lập lỗi khi ghi ReviewAnswer thứ 10 | Bắt đầu | Rollback: không còn ReviewAttempt hay ReviewAnswer nào | RV-R06 | |
| RV-T22 | A gửi 2 request bắt đầu đồng thời | — | Theo quyết định (tối đa 1 bài dở) | RV-R04 | ND-29 |

## 3. Xem attempt — `GET /api/review-attempts/{attempt_id}`

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| RV-T30 | Attempt chưa nộp của A | A gọi | 200; câu hỏi không có `correct_index`, `explanation` | RV-R07 | |
| RV-T31 | Attempt của A | B gọi | **404** (không phải 403) | RV-R08 | |
| RV-T32 | — | `attempt_id` không tồn tại | 404 | §4.3 | |
| RV-T33 | Attempt đã nộp | A gọi | Theo quyết định | — | ND-26 |

## 4. Nộp bài và chấm điểm — `POST /api/review-attempts/{attempt_id}/submit`

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| RV-T40 | Bài dở của A (C1 ongoing) | Trả lời đúng 17/20 | 200; `score_percent = 85`, `passed = true`, số câu đúng = 17; ReviewAnswer có `selected_index`, `is_correct`; `submitted_at` được ghi | RV-R11, RV-R12 | `submitted_at`: ND-31 |
| RV-T41 | Như RV-T40 | — | StudentCourse(C1) = `completed`, `completed_at` có giá trị | RV-R14 | |
| RV-T42 | Như RV-T40; A có S1 = learning, chưa có S2, S3 | — | UserSkill S1, S2, S3 = `known` | RV-R15 | |
| RV-T43 | Bài dở | Đúng 12/20 (60%) | `passed = true` (biên ≥ 60) | RV-R12 | |
| RV-T44 | Bài dở | Đúng 11/20 (55%) | `passed = false`; StudentCourse **vẫn** `ongoing`; UserSkill **không** đổi | RV-R16 | |
| RV-T45 | Bài dở | Chỉ gửi 15 câu (đều đúng) | 5 câu thiếu: `is_correct = FALSE`; `score_percent = 75` | RV-R10 | |
| RV-T46 | Bài dở | `selected_index = 4` hoặc `-1` | 422 | §4.4 | |
| RV-T47 | Bài dở | Gửi `question_id` không thuộc attempt / trùng | Theo quyết định; dù thế nào thì câu lạ **không** được tính điểm | RV-R09 | ND-22 |
| RV-T48 | Attempt đã nộp | Nộp lần hai | 409; điểm không đổi | RV-R13 | |
| RV-T49 | Attempt của A | B nộp | 404 | RV-R08 | |
| RV-T50 | StudentCourse(C1) = `completed` (completed_at = T0) | Ôn lại và đạt | Thêm một ReviewAttempt; status vẫn `completed`, `completed_at` vẫn = T0 | RV-R14, D10 | UserSkill: ND-23 |
| RV-T51 | — | Đổi `REVIEW_PASS_PERCENT` từ 60 → 80 sau khi đã có attempt đạt 70% | Attempt cũ vẫn `passed = true` | RV-R12 | |
| RV-T52 | — | Kiểm tra code/cấu hình | Ngưỡng đọc từ `REVIEW_PASS_PERCENT`, không hard-code | RV-R12 | |

## 5. Transaction nộp bài

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| RV-T60 | Bài đạt; giả lập lỗi khi upsert UserSkill (bước 4) | Nộp | Lỗi; **rollback toàn bộ**: ReviewAnswer chưa chấm, `score_percent`/`passed` trống, StudentCourse vẫn `ongoing`; có thể nộp lại | RV-R17, G4 | |
| RV-T61 | Bài đạt; giả lập lỗi khi cập nhật StudentCourse (bước 3) | Nộp | Rollback toàn bộ như RV-T60 | RV-R17 | |
| RV-T62 | Bài đạt; giả lập `send_email` ném lỗi | Nộp | 200 với kết quả; dữ liệu **đã** lưu; lỗi chỉ ghi log | RV-R18 | |
| RV-T63 | Bài đạt | Nộp | `send_email` được gọi **sau** commit; nội dung không chứa đáp án; có link `FRONTEND_URL/review/history/{attempt_id}` | RV-R18 | |
| RV-T64 | Bài không đạt | Nộp | `send_email` có được gọi không | RV-R18 | ND-25 |
| RV-T65 | Hai request nộp đồng thời cùng attempt | — | Chỉ một lần chấm được ghi nhận | RV-R13 | ND-29 |
| RV-T66 | Bài đạt; khóa thuộc một LearningPath ongoing | Nộp | Theo quyết định | — | ND-24 |

## 6. Lịch sử — `GET /api/me/review-history`, `/{attempt_id}`

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| RV-T70 | A có 3 attempt đã nộp (2 ở C1, 1 ở C3) | `GET /api/me/review-history` | Đúng 3 lần làm của A; có `items`, `total`, `page`, `page_size` | RV-R19 | Bài dở: ND-34 |
| RV-T71 | Như trên | `?course_id=C1` | Chỉ 2 lần làm ở C1 | RV-R19 | |
| RV-T72 | Như trên (1 đạt, 2 trượt) | `?passed=true` / `?passed=false` | Đúng tập tương ứng | RV-R19 | |
| RV-T73 | Như trên | `?page=2&page_size=2` | 1 phần tử; `total = 3` | RV-R19 | |
| RV-T74 | B có attempt | A gọi danh sách | Không thấy attempt của B | RV-R08 | |
| RV-T75 | Attempt đã nộp của A | `GET /api/me/review-history/{id}` | Có từng câu: `selected_index`, `is_correct`, `correct_index`, `explanation` | §4.6, RV-R07 | |
| RV-T76 | Attempt của A | B gọi chi tiết | 404 | RV-R08 | |
| RV-T77 | Attempt chưa nộp | Gọi chi tiết | Theo quyết định; **không** được lộ `correct_index` | RV-R07 | ND-26 |
| RV-T78 | — | Không có token | 401 | backend-rules §2 | |

## 7. Kiểm tra chống lộ đáp án (tổng hợp)

| ID | Hành động | Kết quả mong đợi | Quy tắc |
|---|---|---|---|
| RV-T80 | Duyệt toàn bộ response của §4.2, §4.3 (và §4.4) trước/khi nộp | Không chứa khóa `correct_index` hoặc `explanation` ở bất kỳ cấp nào | RV-R07, G9 |
