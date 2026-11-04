---
name: review-assessment
description: Điểm vào cho mọi việc thuộc module Ôn tập & Đánh giá kiến thức của project EduMentor AI — bài ôn tập 20 câu theo khóa học, GET /api/courses/{course_id}/review, POST /api/courses/{course_id}/review-attempts, GET /api/review-attempts/{id}, submit, chấm điểm, điểm đạt 60%, đánh dấu khóa học completed, cập nhật UserSkill known, transaction nộp bài, email kết quả, GET /api/me/review-history, bảng Question/ReviewAttempt/ReviewAnswer. Dùng skill này mỗi khi implement, sửa, review hoặc viết test cho các phần trên, kể cả khi người dùng chỉ nói "làm bài test", "ôn tập", "chấm điểm", "lịch sử bài test" hay mở routers/reviews.py, services/review_service.py, schemas/review.py, tests/test_review.py. Ưu tiên skill này hơn skill cấp user edumentor-review khi làm việc trong repo này.
---

# Review & Assessment — EduMentor AI

Skill này là **điểm vào**: nó cho biết phạm vi, cần đọc gì và không được làm gì. Nội dung nghiệp vụ nằm trong tài liệu dưới đây — đọc chúng, vì thiết kế đã đổi so với bản cũ (ôn tập **theo khóa học**, không theo kỹ năng) và nhiều chi tiết dễ đoán sai.

## 1. Đọc trước khi làm (theo thứ tự)

1. `docs/modules/review-assessment.md` — phạm vi, file, dữ liệu, API contract (§4), quy tắc `RV-Rxx` (§5), luồng (§6), transaction (§7), bảo mật (§8). **Nguồn chi tiết chính.**
2. `docs/decisions.md` — D01, D02, D03, D04, D10 và danh sách `[NEEDS DECISION]` §4.2, §4.3.
3. `docs/backend-rules.md` — phân lớp, lỗi, quyền sở hữu (404), transaction, email chạy nền, cấu hình.
4. `docs/database-design.md` §6 (và §3.2, §3.3 cho UserSkill, StudentCourse) — khi đụng tới model hoặc migration.
5. `docs/modules/review-assessment.tests.md` — khi viết hoặc sửa test.

## 2. Phạm vi

**Được làm:** `routers/reviews.py`, `schemas/review.py`, `models/question.py`, `models/review_attempt.py`, `models/review_answer.py`, `services/review_service.py`, repository tương ứng, `tests/test_review.py`, migration cho 3 bảng của module. Dùng chung `core/email.py` với module Auth/Profile.

**Chỉ được dùng, không đổi thiết kế:** `StudentCourse` (đọc; ghi `completed`/`completed_at` khi đạt), `CourseSkillRelation`, `Course`, `UserSkill` (upsert `known` khi đạt).

**Không thuộc phạm vi:** `/api/admin/questions*` (quản trị câu hỏi — module này chỉ đọc `Question`); `GET/PATCH /api/me/skills` (skill `auth-profile`); `join` và các chuyển trạng thái khác của StudentCourse (Course Tracking); cập nhật `LearningPath.status` (T18, ND-24). Endpoint cũ `/api/skills/{skill_id}/review*` đã bị bỏ — không implement.

## 3. Quy tắc bắt buộc

Chi tiết ở `review-assessment.md` §5; đây là những điểm hay bị làm sai:

- Bài theo **khóa học**; khả dụng khi tổng câu `is_active` của các kỹ năng khóa dạy ≥ 20 (RV-R01, RV-R02).
- Chỉ bắt đầu khi StudentCourse ở `ongoing` hoặc `completed`; còn lại → 409. Mỗi khóa tối đa một bài dở; bắt đầu lại trả bài dở đó. Làm lại không giới hạn (RV-R03–R05).
- Server chọn và **lưu sẵn** 20 câu (20 ReviewAnswer) khi bắt đầu; khi nộp chỉ chấm đúng 20 dòng đó (RV-R06, RV-R09).
- **Không bao giờ** trả `correct_index` hoặc `explanation` trước khi nộp, ở bất kỳ endpoint nào; chỉ có ở `GET /api/me/review-history/{id}` sau khi nộp (RV-R07).
- Attempt của người khác → **404**, không phải 403 (RV-R08).
- Câu bỏ trống = sai; `passed = score_percent ≥ REVIEW_PASS_PERCENT` đọc từ cấu hình (60), lưu cố định tại lúc nộp; nộp lần hai → 409 (RV-R10–R13).
- Nộp bài là **một transaction**: chấm + ghi điểm + (nếu đạt) StudentCourse `completed` + UserSkill `known` cho mọi kỹ năng của khóa. Lỗi bất kỳ → rollback toàn bộ (RV-R14–R17).
- Khóa đã `completed` mà ôn lại: không đổi status/`completed_at` (D10). Không đạt: không đổi StudentCourse, UserSkill.
- Email kết quả chạy nền **sau commit**, không chứa đáp án; gửi lỗi chỉ ghi log (RV-R18).

## 4. Không được làm

- Không tự chọn phương án cho `[NEEDS DECISION]`: thuật toán chia phần dư (ND-20), thời gian làm bài (ND-21), câu hỏi lạ khi nộp (ND-22), UserSkill khi ôn lại (ND-23), cập nhật LearningPath (ND-24), email mọi lần hay chỉ khi đạt (ND-25), response sau khi nộp (ND-26), mức Mạnh/TB/Yếu trên wireframe (ND-27), xử lý đồng thời (ND-29)… Gặp chúng thì **dừng và hỏi**, hoặc chỉ làm phần không phụ thuộc và ghi rõ chỗ còn chờ.
- Không implement bước 5 (LearningPath completed) cho tới khi ND-24 được chốt.
- Không thêm endpoint, bảng, cột ngoài `docs/`; không thêm `skill_id` vào ReviewAttempt.
- Không đưa điểm ôn tập vào xếp hạng gợi ý khóa học (RV-R21).
- Không để frontend gửi request cập nhật kỹ năng sau khi nộp (RV-R20).

## 5. Quy trình implement

1. Xác định endpoint/quy tắc liên quan trong `review-assessment.md`; liệt kê `ND-xx` ảnh hưởng; ND chặn đường → hỏi trước.
2. Model + migration khớp `database-design.md` §6 (FK ReviewAnswer → Question là RESTRICT; ReviewAttempt → StudentCourse là CASCADE).
3. Schema: tách rõ schema câu hỏi **khi làm bài** (không có đáp án) và schema **chi tiết sau khi nộp**; đừng dùng chung một schema rồi "ẩn" trường.
4. Repository: mọi truy vấn attempt đều ràng buộc theo người dùng hiện tại qua StudentCourse.
5. Service: giữ trọn ranh giới transaction ở §7 của tài liệu module; gửi email qua `BackgroundTasks` sau commit.
6. Router: chỉ gọi service, trả mã lỗi đúng tài liệu (404/409/422).
7. Test theo `review-assessment.tests.md`; bỏ qua kịch bản có cột "Chờ" cho tới khi ND được chốt. Chạy `pytest`, `black`, `ruff`.
8. Tài liệu thiếu/mâu thuẫn → đề xuất thêm `ND-xx` vào `docs/decisions.md`, không tự vá bằng code.

## 6. Kỳ vọng kiểm thử

Tối thiểu phải có test cho: điều kiện `available`; bắt đầu tạo đúng 20 ReviewAnswer; bắt đầu lại trả bài dở; 409 khi chưa tham gia/thiếu câu; response làm bài **không** có `correct_index`/`explanation`; 404 khi truy cập attempt người khác; chấm điểm (85%, biên 60%, 55%, câu bỏ trống); nộp lần hai 409; đạt → StudentCourse `completed` + UserSkill `known`; không đạt → không đổi gì; **rollback toàn bộ** khi một bước trong transaction lỗi; email lỗi không làm mất kết quả; lọc và phân trang lịch sử.
