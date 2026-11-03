# F11 — Phase P05: Course Catalog & Admin Courses (F02, F11)

> Thuộc kế hoạch tính năng [F11 — Quản trị — khóa học, kỹ năng và các mối liên hệ](plan.md). Phase `P05` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

Thông tin chung và phạm vi của Phase P05: xem [F02](../F02-course-catalog/phase-05-course-catalog-admin-courses.md). File này chỉ chứa các Task của F11.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P05-T06 | Quản trị khóa học | CRUD `/api/admin/courses` | §11 | Hòa (D-OWN-02; trước: Khôi) | CXĐ | CPC | P04-T03, P02-T01 | API | NOT_STARTED | — | Một phần: kiểm quyền admin chờ P04-T03. Schema, service, repository làm được |
| P05-T07 | Quản trị kỹ năng | `/api/admin/skills` | §11 | Hòa (D-OWN-02; trước: Khôi) | CXĐ | CPC | P04-T03, P02-T02 | API | NOT_STARTED | — | Một phần: kiểm quyền admin chờ P04-T03. Schema, service, repository làm được |
| P05-T08 | Quản trị liên kết khóa học–kỹ năng | `/api/admin/course-skill-relations` | §11 | Hòa (D-OWN-02; trước: Khôi) | CXĐ | CPC | P05-T06, P05-T07 | API | NOT_STARTED | — | Một phần: kiểm quyền admin chờ P04-T03. Schema, service, repository làm được |
| P05-T09 | Test phân quyền admin (bắt buộc) | Học viên gọi `/api/admin/*` → 403; chưa đăng nhập → 401 | `conventions.md` §6 | Hòa (D-OWN-02; trước: Khôi) | CXĐ | CPC | P05-T06…T08, P01-T08 | Kết quả `pytest` | NOT_STARTED | — | Một phần: chạy test cần P01-T08. Viết test làm được |
| P05-T13 | Trang Quản trị khóa học | AdminCoursesPage | `ui-design` AdminCourses | Hòa (D-OWN-02; trước: Khôi) | CXĐ | CPC | P03-T04 | Page | NOT_STARTED | — | — |
| P05-T14 | Trang Quản trị kỹ năng (danh mục) | AdminSkillsPage — phần danh mục | `ui-design` AdminSkills | Hòa (D-OWN-02; trước: Khôi) | CXĐ | CPC | P03-T04 | Page | NOT_STARTED | — | — |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

### Task dùng chung, quản lý ở tính năng khác

| Task ID | Task Name | Quản lý tại |
|---|---|---|
| P05-T01 | Rà soát nguồn F02, F11 | [F02](../F02-course-catalog/phase-05-course-catalog-admin-courses.md) |
| P05-T02 | Chuẩn bị đặc tả module | [F02](../F02-course-catalog/phase-05-course-catalog-admin-courses.md) |
| P05-T03 | Chuẩn bị test case | [F02](../F02-course-catalog/phase-05-course-catalog-admin-courses.md) |

## 3. Điều kiện hoàn thành, review, chặn

Theo mục 4–7 của Phase P05 ở file quản lý chung của Phase (liên kết ở mục 1), áp dụng cho các Task trên. Quy tắc trạng thái và bằng chứng: `plans/plan.md` PART 2.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
