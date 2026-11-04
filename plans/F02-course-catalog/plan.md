# F02 — Danh mục khóa học

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở file `phase-NN-*.md` của thư mục này. Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F02 — Danh mục khóa học |
| Người phụ trách | **Khôi** (D-OWN-02, `docs/decisions.md` §2) |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/course-catalog.md`](../../docs/modules/course-catalog.md) — DRAFT, chưa được người phụ trách xác nhận |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (2026-11-03) | 8 Task: NOT_STARTED 8 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Danh mục khóa học MOOC bên ngoài: xem danh sách, tìm, lọc, sắp xếp, xem chi tiết và kỹ năng của khóa học, đi tới trang khóa học gốc (`docs/modules/course-catalog.md` §1).

## 3. Phạm vi

Theo `docs/modules/course-catalog.md` §1 ("Thuộc module", "Không thuộc module"). Tóm tắt: `GET /api/courses` (kèm query), `GET /api/courses/{course_id}`, `GET /api/courses/{course_id}/skills`; màn Courses, CourseDetail, JoinDialog. Không gồm bookmark (F03), `join` và trạng thái (F04), quản trị (F11).

## 4. Mức độ có căn cứ

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `READY_WITH_LIMITATIONS` | BA FR-15, FR-16, §10.3; quyền xem chờ ND-70 |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | BA không có AC riêng cho danh mục; SRS-CAT-01 … 03 chưa đưa vào đặc tả. Câu hỏi cho Khôi (D-OWN-02): tiêu chí nghiệm thu của F02 là gì — có dùng SRS-CAT-01 … 03 làm căn cứ để đưa vào `docs/modules/course-catalog.md` không? |
| UI | `READY_WITH_LIMITATIONS` | Courses, CourseDetail, JoinDialog; bộ lọc kỹ năng ND-72 |
| API | `NEEDS_OWNER_INPUT` | Có endpoint; request, response, mã lỗi chưa định nghĩa. Câu hỏi cho Khôi (D-OWN-02): request, response và mã lỗi của các endpoint F02 là gì, để ghi vào `docs/modules/course-catalog.md`? |
| Database | `READY_FOR_IMPLEMENTATION` | `database-design.md` §2.1–§2.3 (model ở P02 dùng chung) |
| Kiểm thử | `NEEDS_OWNER_INPUT` | Chưa có `course-catalog.tests.md`. Câu hỏi cho Khôi (D-OWN-02): danh sách kịch bản kiểm thử của F02 là gì, dựa trên tiêu chí nghiệm thu nào? Chưa có `docs/modules/course-catalog.tests.md` |
| Phụ thuộc | `NOT_READY_BLOCKED` | P02 (model, dataset) chờ P01-T05 (Alembic, ND-16) |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú.

## 5. Phase và Task

| Phase | File | Task quản lý tại thư mục này |
|---|---|---|
| P05 | [phase-05-course-catalog-admin-courses.md](phase-05-course-catalog-admin-courses.md) | P05-T01, P05-T02, P05-T03, P05-T04, P05-T05, P05-T10, P05-T11, P05-T12 |

Các Phase khác của khung chung (P00–P03, P13) là phần dùng chung, quản lý tại [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

Lấy từ cột Dependencies của các Task (không thêm phụ thuộc mới):

| Task | Phụ thuộc | Thuộc |
|---|---|---|
| P05-T04 | P02-T01 | dùng chung |
| P05-T04 | P02-T03 | dùng chung |
| P05-T05 | P02-T01 | dùng chung |
| P05-T05 | P02-T03 | dùng chung |
| P05-T10 | P03-T03 | dùng chung |
| P05-T11 | P03-T05 | dùng chung |

Quyết định còn chờ ảnh hưởng tính năng: ND-70, ND-72, ND-61, ND-77, ND-81, ND-50.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Xác nhận đặc tả `docs/modules/course-catalog.md` (DRAFT).
2. Bổ sung request, response, mã lỗi, phân trang cho EP-017 … EP-019.
3. Đưa SRS-CAT-01 … 03 và tiêu chí nghiệm thu vào đặc tả.
4. Soạn kịch bản kiểm thử (P05-T03) sau khi đặc tả được xác nhận.
5. Chốt người phụ trách màn JoinDialog (workbook ghi Khôi, Tâm; endpoint của Hòa).

## 8. Điều kiện hoàn thành và bằng chứng

- Mọi Task bắt buộc của tính năng DONE, có Evidence và kết quả review (`plans/plan.md` PART 2 quy tắc 5, 6). Tạo file kế hoạch **không** phải DONE.
- Đặc tả `docs/modules/course-catalog.md` được người phụ trách xác nhận (DRAFT → SPEC CONFIRMED) trước khi code phần phụ thuộc đặc tả.
- Bằng chứng cần có: kết quả `pytest` cho `/api/courses*`, ảnh màn Courses, CourseDetail, commit hoặc PR.
- Task BLOCKED ghi rõ mã chặn; phần không phụ thuộc vẫn được làm.

## 9. Tài liệu nguồn

BA §6.3 (FR-15, FR-16), §10.3, UC-06; SRS §6.3 (SRS-CAT-01 … 03); `docs/api-endpoints.md` §3; `docs/database-design.md` §2.1–§2.3; `docs/ui-design/` S-12, S-13, S-14; `docs/modules/course-catalog.md`.
