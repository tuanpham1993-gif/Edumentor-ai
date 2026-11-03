# F09 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Kiểm tra bài ôn tập khả dụng | §10.10 | SRS-REV-01 | S-21 |
| Bắt đầu bài, chọn câu | FR-24; UC-09 | SRS-REV-02 | S-22 |
| Làm bài, xem câu hỏi | §10.10 | SRS-REV-03, 04 | S-22 |
| Nộp bài, chấm điểm | FR-26; BR-28 | SRS-REV-05 | S-22 |
| Kết quả, phản hồi | FR-27; BR-30 | SRS-REV-06 | S-23 |
| Lịch sử, chi tiết lần làm | FR-28; UC-10 | SRS-REV-07, 08 | S-24, S-25 |
| Điểm trung bình | FR-29; BR-31 | SRS-REV-09 | — |
| Đánh giá tự nguyện | BR-26 | — | — |
| Câu hỏi phù hợp kỹ năng | BR-27 | — | — |
| Tiêu chí nghiệm thu | AC-07 | SRS-AC (chương 11) | — |

Mã yêu cầu `RV-YC01 … RV-YC10`: `docs/modules/review-assessment.md` §1 "Yêu cầu".

BA khác `docs/decisions.md` (theo `decisions.md`, D-DOC-01):

- BA FR-24, UC-09, §10.10 tính bài **theo kỹ năng**; D01 tính **theo khóa học** (ND-58).
- BA §8.6 dùng RAG để truy xuất câu hỏi; D04, T14 lấy câu `is_active` từ CSDL (ND-58).
- BA FR-25, FR-26, BR-29 có câu mở, câu lập trình; hiện chỉ trắc nghiệm (ND-73).
- Đề bài SRS v1.0 FR-07: AI sinh 10 câu; hiện hành 20 câu lấy từ CSDL (ND-58, ND-81).

## B. Quyết định đã chốt

| Mã | Nội dung |
|---|---|
| D-OWN-01 | Tuấn phụ trách Ôn tập và Đánh giá |
| D01 | Ôn tập theo khóa học; 20 câu lấy từ các kỹ năng của khóa |
| D02 | Điểm đạt ≥ 60% (`REVIEW_PASS_PERCENT`) |
| D03 | Làm lại không giới hạn; mỗi khóa tối đa một bài đang dở; bắt đầu lại trả bài dở |
| D04 | Gộp câu của các kỹ năng khóa dạy, tổng ≥ 20; chia đều giữa các kỹ năng |
| D05 | `join` đặt `UserSkill = learning` (điều kiện để có khóa `ongoing`) |
| D10 | Khóa đã `completed` được ôn lại; kết quả chỉ lưu thêm, không đổi `completed` |
| T11 ☑ | Endpoint theo khóa học; bỏ `/api/skills/{skill_id}/review*` |
| T13 ☑ | Nộp bài trong một transaction (bước LearningPath: ND-24) |
| T14 ☑ | Server chọn 20 câu, tạo sẵn 20 ReviewAnswer (thuật toán chia: ND-20) |
| T15 ☑ | Không lộ đáp án trước khi nộp; attempt người khác → 404 |
| T17 ☑ | Lịch sử có lọc, phân trang |
| T19 … T21 ☑ | Quản trị câu hỏi — ngoài phạm vi F09, chỉ là phụ thuộc dữ liệu |
| T26 ☑ | `Question.is_active` |
| T28 ☑ | `REVIEW_PASS_PERCENT`, `FRONTEND_URL`, SMTP |
| T29 ☑ | Email kết quả sau khi nộp (gửi khi nào: ND-25) |
| D-FE-08 | Lưu bài dở (M1) chưa có endpoint: màn vẫn dựng, hiển thị "chưa khả dụng" |

Chưa được tick (không coi là đã chốt): T12 (ND-30), T16 (RV-R03, R10, R13 BLOCKED), T18 (ND-24), T27 (ND-31).

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung | Task bị ảnh hưởng |
|---|---|---|
| ND-20 | Chia câu: phần dư, bù khi kỹ năng thiếu câu | P09-T05 |
| ND-21 | Giới hạn thời gian, bài dở hết hạn | P09-T05, T07 |
| ND-22 | `answers` có `question_id` lạ hoặc trùng | P09-T07 |
| ND-23 | Ôn lại khóa `completed` mà đạt: có upsert `known` lại không | P09-T07 |
| ND-24 | Cập nhật LearningPath sau khi đạt (T18 ☐) | P09-T07 |
| ND-25 | Email gửi mọi lần hay chỉ khi đạt | P09-T08 |
| ND-26 | Response của attempt sau khi nộp, history của bài chưa nộp | P09-T06, T09 |
| ND-27 | Mức Mạnh/Trung bình/Yếu, cột Kỹ năng trên UI | P09-T09, T15 |
| ND-28 | Khóa `abandoned` khi có bài dở; khóa không có kỹ năng | P09-T04, T07 |
| ND-29 | Đồng thời khi bắt đầu, nộp bài | P09-T05, T07 |
| ND-30 | T12 ☐ | — |
| ND-31 | `submitted_at` (T27 ☐) | P09-T02 |
| ND-33 | Mã 200 hay 201 khi trả bài dở | P09-T05 |
| ND-34 | History có liệt kê bài dở không | P09-T09 |
| ND-53, CONFLICT-SCOPE-01 | Quản trị câu hỏi: có màn không, ai làm | P09-T03 (nguồn câu hỏi) |
| ND-55 (M1) | Lưu đáp án bài đang dở | P09-T13 |
| ND-58 | BA, SRS khác D01, D04 (theo kỹ năng, RAG) | P09-T01, P12-T07 |
| ND-66 | Route trong link email kết quả | P09-T08 |
| ND-73 | Câu mở, câu lập trình, điểm trung bình | P09-T01 |
| ND-77, ND-81 | Đề bài khác hiện hành; cần hỏi giảng viên trước khi code F09 | Toàn F09 |
| ND-51, ND-54 | Câu chữ UI, dữ liệu UI chưa có | P09-T12, T13 |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | **Dataset câu hỏi** (`BLOCKED_DATASET`): nguồn, người soạn, số câu mỗi kỹ năng, ngôn ngữ, `explanation` có bắt buộc, định dạng nhập | P09-T03 và chạy thật P09-T04 … T09 |
| 2 | Dùng dữ liệu giả trong CSDL test (không phải dataset chính thức) có được không | P09-T10 |
| 3 | Nội dung email kết quả: ghi chú T29 so với `.docx` 6.2 và RV-R18 (`plans/plan.md` PART 6) | P09-T08 |
| 4 | Mã SRS chưa được đưa vào `docs/modules/review-assessment.md` | Truy vết |

### C3. Mặc định an toàn có trong nguồn

| Mặc định | Nguồn | Điều kiện dùng |
|---|---|---|
| Không implement kiểm tra LearningPath (bước 5) khi nộp bài | `review-assessment.md` §6 bước (5), ND-24 | Tới khi T18 được tick |
| Màn làm bài: "Tạm rời, làm tiếp sau" hiển thị "chưa khả dụng" | D-FE-08 (đã chốt), ND-55 | Tới khi có endpoint M1 |
| Frontend không hiển thị câu chữ "câu bỏ trống tính là sai", "kết quả được gửi qua email" | ND-51 (ghi "tạm thời") | Tới khi T16, ND-25 chốt — không phải quyết định |
| `§10` của `api-endpoints.md` chỉ ghi "xem §2" cho `/api/me/skills` | ND-30 (ghi "tạm thời") | Tới khi T12 được tick |
