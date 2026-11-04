# F02 — Phase P05: Course Catalog & Admin Courses (F02, F11)

> Thuộc kế hoạch tính năng [F02 — Danh mục khóa học](plan.md). Phase `P05` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

**1. Phase Information** — Phase ID: P05 · Objective: danh mục khóa học cho học viên và quản trị khóa học, kỹ năng, liên kết · Related Features: F02, F11 · Responsible: theo từng tính năng — F02: Khôi, F11: Hòa (D-OWN-02) · Support: CXĐ · Reviewer: CPC · Dependencies: P02, P03, P04-T03 · Initial Status: NOT_STARTED

**2. Scope** — Trong: `/api/courses*`, `/api/admin/courses`, `/api/admin/skills`, `/api/admin/course-skill-relations`; trang Courses, Courses-Light, CourseDetail, JoinDialog (giao diện), AdminCourses, AdminSkills (phần danh mục). Ngoài: `join` backend (P06); quan hệ kỹ năng (P07); quản trị câu hỏi (P11). Nguồn: `docs/api-endpoints.md` §3, §11; `docs/database-design.md` §2; BA §6.3 (FR-12–16), §6.7 (FR-30, 32, 33); SRS FR-02.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P05-T01 | Rà soát nguồn F02, F11 | Đối chiếu BA FR-12–16, FR-30, 32, 33, SRS FR-02 với `api-endpoints.md` §3, §11; ghi điểm chưa rõ | BA §6.3, §6.7; SRS §3 | Khôi | CXĐ | CPC | — | Ghi chú rà soát | NOT_STARTED | — | — |
| P05-T02 | Chuẩn bị đặc tả module | Đặc tả F02, F11 chỉ từ nguồn đã có | Như trên | Khôi | CXĐ | CPC | P05-T01 | Đề xuất `docs/modules/…` | NOT_STARTED | — | — |
| P05-T03 | Chuẩn bị test case | Kịch bản test; expected result chỉ lấy từ nguồn | `conventions.md` §6 | Khôi | CXĐ | CPC | P05-T02 | Đề xuất `*.tests.md` | NOT_STARTED | — | — |
| P05-T04 | `GET /api/courses` | Tìm kiếm, lọc `skill_id`, `level`, `sort_by`, phân trang | §3; `conventions.md` §1 | Khôi | CXĐ | CPC | P02-T01, P02-T03 | API | NOT_STARTED | — | Một phần: migration và dữ liệu chờ P02; quyền truy cập `GET /api/courses` chưa ghi trong §3 (chưa có ND); ND-61 chỉ là tiêu chí lọc thêm. Bộ lọc `search`, `skill_id`, `level`, `sort_by` làm được |
| P05-T05 | `GET /api/courses/{id}`, `/skills` | Chi tiết và kỹ năng của khóa | §3 | Khôi | CXĐ | CPC | P02-T01, P02-T03 | API | NOT_STARTED | — | Một phần: migration và dữ liệu chờ P02; quyền truy cập §3 chưa ghi (chưa có ND). Schema, service làm được |
| P05-T10 | API client khóa học | `courses.api.js`; nhãn cấp độ chỉ đổi khi hiển thị | D-FE-11 | Khôi | CXĐ | CPC | P03-T03 | File API | NOT_STARTED | — | — |
| P05-T11 | Trang Danh mục | CatalogPage, CourseCard, CourseCover, CardOpening | `ui-design` Courses, Courses-Light | Khôi | CXĐ | CPC | P05-T10, P03-T05 | Page + component | NOT_STARTED | — | Một phần: UI2-03 (bộ lọc kỹ năng) |
| P05-T12 | Trang Chi tiết khóa học, hộp thoại Tham gia | CourseDetailPage, JoinDialog (gọi API join của P06) | `ui-design` CourseDetail, JoinDialog | Khôi | CXĐ | CPC | P05-T10 | Page + component | NOT_STARTED | — | Một phần: ND-50 (`/courses/:id/join`) |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

## 3. Điều kiện hoàn thành, review, chặn

**4. Deliverables** — API §3, §11 (khóa học, kỹ năng, liên kết); 6 màn; đặc tả và test case đề xuất.
**5. Review Checklist** — Đúng `api-endpoints.md`; phân trang theo `conventions.md` §1; admin kiểm quyền ở backend; giao diện theo API contract.
**6. Blockers & Open Issues** — Quyền `GET /api/courses*` chưa ghi; ND-61; UI2-03; thiếu đặc tả module.
**7. Completion Criteria** — Task không bị chặn DONE; test phân quyền admin DONE.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
