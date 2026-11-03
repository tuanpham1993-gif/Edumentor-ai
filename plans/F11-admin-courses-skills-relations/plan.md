# F11 — Quản trị — khóa học, kỹ năng và các mối liên hệ

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở file `phase-NN-*.md` của thư mục này. Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F11 — Quản trị — khóa học, kỹ năng và các mối liên hệ |
| Người phụ trách | **Hòa** (D-OWN-02, `docs/decisions.md` §2). Workbook V2 ghi Khôi — workbook không phải nguồn quyết định; chỉ giữ để truy vết |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/admin-course-skill.md`](../../docs/modules/admin-course-skill.md) — DRAFT, chưa được người phụ trách xác nhận |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (2026-11-03) | 6 Task: NOT_STARTED 6 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Admin quản lý danh mục khóa học, kỹ năng và liên kết khóa học–kỹ năng (`docs/modules/admin-course-skill.md` §1).

## 3. Phạm vi

Theo `docs/modules/admin-course-skill.md` §1 ("Thuộc module", "Không thuộc module"). Tóm tắt: `/api/admin/courses*`, `/api/admin/skills*`, `/api/admin/course-skill-relations*`; màn AdminCourses, AdminSkills.

## 4. Mức độ có căn cứ

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `READY_WITH_LIMITATIONS` | BA FR-30, FR-32, FR-33, BR-32 … BR-34; xóa kỹ năng ND-71 |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | BA AC-08; SRS-ADMC-01 … 04, SRS-ADMS-01, 02 — các mã này chưa có trong `docs/modules/admin-course-skill.md`. Câu hỏi cho Hòa (D-OWN-02): AC-08, SRS-ADMC-01 … 04, SRS-ADMS-01, 02 có phải tiêu chí nghiệm thu chính thức của F11 để đưa vào đặc tả không? Việc tài liệu kiểm thử (riêng): chưa có `docs/modules/admin-course-skill.tests.md`, cần tạo |
| UI | `READY_FOR_IMPLEMENTATION` | AdminCourses, AdminSkills |
| API | `NEEDS_OWNER_INPUT` | Endpoint có; request, response, mã lỗi chưa định nghĩa. Câu hỏi cho Hòa (D-OWN-02): request, response và mã lỗi của các endpoint F11 là gì, để ghi vào `docs/modules/admin-course-skill.md`? |
| Database | `READY_FOR_IMPLEMENTATION` | §2.1–§2.3, §8.1 |
| Kiểm thử | `NEEDS_OWNER_INPUT` | P05-T09 bắt buộc; chưa có test case. Câu hỏi cho Hòa (D-OWN-02): danh sách kịch bản kiểm thử của F11 là gì, dựa trên tiêu chí nghiệm thu nào? Chưa có `docs/modules/admin-course-skill.tests.md` |
| Phụ thuộc | `NOT_READY_BLOCKED` | `require_admin` (P04-T03) chờ ND-44; P02 chờ P01-T05 |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú.

## 5. Phase và Task

| Phase | File | Task quản lý tại thư mục này |
|---|---|---|
| P05 | [phase-05-course-catalog-admin-courses.md](phase-05-course-catalog-admin-courses.md) | P05-T06, P05-T07, P05-T08, P05-T09, P05-T13, P05-T14 |

Task dùng chung quản lý ở tính năng khác: P05-T01 (F02), P05-T02 (F02), P05-T03 (F02).

Các Phase khác của khung chung (P00–P03, P13) là phần dùng chung, quản lý tại [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

Lấy từ cột Dependencies của các Task (không thêm phụ thuộc mới):

| Task | Phụ thuộc | Thuộc |
|---|---|---|
| P05-T06 | P04-T03 | F01 |
| P05-T06 | P02-T01 | dùng chung |
| P05-T07 | P04-T03 | F01 |
| P05-T07 | P02-T02 | dùng chung |
| P05-T09 | P01-T08 | dùng chung |
| P05-T13 | P03-T04 | dùng chung |
| P05-T14 | P03-T04 | dùng chung |

Quyết định còn chờ ảnh hưởng tính năng: ND-71, ND-57, ND-52.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Xác nhận đặc tả `docs/modules/admin-course-skill.md`.
2. Bổ sung request, response, mã lỗi cho EP-058 … EP-069, gồm phản hồi khi xóa bị chặn (RESTRICT).
3. Đề xuất phương án ND-71 (xóa mềm hay chặn xóa kỹ năng).
4. Soạn kịch bản kiểm thử phân quyền admin (P05-T09).
5. Đã xử lý: người phụ trách (Hòa) được ghi ở D-OWN-02 (`docs/decisions.md` §2); `docs/modules/README.md` và `README.md` đã đồng bộ (commit `2133863`). Workbook V2 ghi Khôi — workbook không phải nguồn quyết định; chỉ giữ để truy vết.

## 8. Điều kiện hoàn thành và bằng chứng

- Mọi Task bắt buộc của tính năng DONE, có Evidence và kết quả review (`plans/plan.md` PART 2 quy tắc 5, 6). Tạo file kế hoạch **không** phải DONE.
- Đặc tả `docs/modules/admin-course-skill.md` được người phụ trách xác nhận (DRAFT → SPEC CONFIRMED) trước khi code phần phụ thuộc đặc tả.
- Bằng chứng cần có: kết quả `pytest` phân quyền admin (P05-T09), ảnh AdminCourses, AdminSkills.
- Task BLOCKED ghi rõ mã chặn; phần không phụ thuộc vẫn được làm.

## 9. Tài liệu nguồn

BA §6.7 (FR-30, FR-32, FR-33), §9.7, §10.11, UC-11, UC-13, AC-08; SRS §6.10, §6.11 (SRS-ADMC-01 … 04, SRS-ADMS-01, 02); `docs/api-endpoints.md` §11; `docs/database-design.md` §2, §8.1; `docs/modules/admin-course-skill.md`.
