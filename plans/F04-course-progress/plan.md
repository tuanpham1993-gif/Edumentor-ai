# F04 — Theo dõi tiến trình khóa học, đề xuất khóa học liên quan đến nút của tiến trình

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở file `phase-NN-*.md` của thư mục này. Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F04 — Theo dõi tiến trình khóa học, đề xuất khóa học liên quan đến nút của tiến trình |
| Người phụ trách | **Hòa** (D-OWN-02, `docs/decisions.md` §2) |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/course-tracking.md`](../../docs/modules/course-tracking.md) — DRAFT, chưa được người phụ trách xác nhận |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (2026-11-03) | 9 Task: NOT_STARTED 9 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Theo dõi trạng thái học với từng khóa (`bookmarked`, `ongoing`, `completed`, `abandoned`): tham gia và mở khóa ngoài, xem, đổi trạng thái được phép, ngừng theo dõi (`docs/modules/course-tracking.md` §1).

## 3. Phạm vi

Theo `docs/modules/course-tracking.md` §1 ("Thuộc module", "Không thuộc module"). Tóm tắt: `GET /api/me/courses`, `POST /api/courses/{course_id}/join`, `GET`, `PATCH /api/me/courses/{course_id}/status`, `DELETE /api/me/courses/{course_id}`. `completed` do F09 ghi.

## 4. Mức độ có căn cứ

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `READY_WITH_LIMITATIONS` | Làm được theo D02, T13 (đã chốt); BA FR-18 khác ở câu chữ — ND-76 là việc sửa lời văn BA, không chặn triển khai. Giới hạn: CT-YC06 "đề xuất khóa học liên quan đến node" — `NOT_DEFINED_IN_SOURCE` (không có trong BA §6.4), `NEEDS_OWNER_INPUT`: câu hỏi cho Hòa (D-OWN-02) — CT-YC06 có thuộc phạm vi yêu cầu chính thức của F04 không? |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | BA AC-05; SRS-TRK-02 … 05 — các mã này chưa có trong `docs/modules/course-tracking.md`. Câu hỏi cho Hòa (D-OWN-02): AC-05, SRS-TRK-02 … 05 có phải tiêu chí nghiệm thu chính thức của F04 để đưa vào đặc tả không? Việc tài liệu kiểm thử (riêng): chưa có `docs/modules/course-tracking.tests.md`, cần tạo |
| UI | `READY_FOR_IMPLEMENTATION` | CourseDetail, JoinDialog, MyCourses |
| API | `NEEDS_OWNER_INPUT` | Endpoint có; response, mã lỗi chưa định nghĩa; chuyển trạng thái qua PATCH chưa ghi. Câu hỏi cho Hòa (D-OWN-02): response, mã lỗi và quy tắc chuyển trạng thái qua PATCH của các endpoint F04 là gì, để ghi vào `docs/modules/course-tracking.md`? |
| Database | `READY_FOR_IMPLEMENTATION` | `StudentCourse` §3.3, `UserSkill` §3.2 |
| Kiểm thử | `NEEDS_OWNER_INPUT` | Chưa có test case; P06-T08 bắt buộc. Câu hỏi cho Hòa (D-OWN-02): danh sách kịch bản kiểm thử của F04 là gì, dựa trên tiêu chí nghiệm thu nào? Chưa có `docs/modules/course-tracking.tests.md` |
| Phụ thuộc | `NOT_READY_BLOCKED` | P06-T04 chờ P01-T05 |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú.

## 5. Phase và Task

| Phase | File | Task quản lý tại thư mục này |
|---|---|---|
| P06 | [phase-06-bookmark-learning-progress.md](phase-06-bookmark-learning-progress.md) | P06-T01, P06-T02, P06-T03, P06-T04, P06-T06, P06-T07, P06-T08, P06-T09, P06-T11 |

Các Phase khác của khung chung (P00–P03, P13) là phần dùng chung, quản lý tại [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

Lấy từ cột Dependencies của các Task (không thêm phụ thuộc mới):

| Task | Phụ thuộc | Thuộc |
|---|---|---|
| P06-T04 | P01-T05 | dùng chung |
| P06-T04 | P02-T01 | dùng chung |
| P06-T04 | P04-T04 | F01 |
| P06-T06 | P04-T04 | F01 |
| P06-T08 | P06-T05 | F03 |
| P06-T08 | P01-T08 | dùng chung |
| P06-T09 | P03-T03 | dùng chung |

Quyết định còn chờ ảnh hưởng tính năng: ND-76, ND-80, ND-32, ND-28, ND-50.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Xác nhận đặc tả `docs/modules/course-tracking.md`.
2. Ghi rõ các chuyển trạng thái được phép qua `PATCH .../status` (có cho đặt `completed` không).
3. Thống nhất phạm vi "đề xuất khóa học liên quan đến node" với F07 (EP-043; workbook CK-02).
4. Bổ sung response, mã lỗi, quyền của `join`.
5. Soạn kịch bản kiểm thử chuyển trạng thái (P06-T03, P06-T08).

## 8. Điều kiện hoàn thành và bằng chứng

- Mọi Task bắt buộc của tính năng DONE, có Evidence và kết quả review (`plans/plan.md` PART 2 quy tắc 5, 6). Tạo file kế hoạch **không** phải DONE.
- Đặc tả `docs/modules/course-tracking.md` được người phụ trách xác nhận (DRAFT → SPEC CONFIRMED) trước khi code phần phụ thuộc đặc tả.
- Bằng chứng cần có: kết quả `pytest` chuyển trạng thái (P06-T08), ảnh MyCourses, CourseDetail.
- Task BLOCKED ghi rõ mã chặn; phần không phụ thuộc vẫn được làm.

## 9. Tài liệu nguồn

BA §6.4 (FR-18, FR-19), §10.4, UC-07, AC-05; SRS §6.4 (SRS-TRK-02 … 05); `docs/api-endpoints.md` §2, §4; `docs/database-design.md` §3.2, §3.3; `docs/modules/course-tracking.md`.
