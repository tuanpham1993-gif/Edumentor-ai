# F04 — Phase P06: Bookmark & Learning Progress (F03, F04)

> Thuộc kế hoạch tính năng [F04 — Theo dõi tiến trình khóa học, đề xuất khóa học liên quan đến nút của tiến trình](plan.md). Phase `P06` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

**1. Phase Information** — Phase ID: P06 · Objective: lưu khóa học và theo dõi 4 trạng thái học · Related Features: F03 (Tâm), F04 (Hòa) · Responsible: theo từng task — F03: Tâm, F04: Hòa (D-OWN-02); task gồm cả hai tính năng: CPC · Support: CXĐ · Reviewer: CPC · Dependencies: P04-T03, P05-T05 · Initial Status: NOT_STARTED

**2. Scope** — Trong: `/api/me/bookmarks*`, `/api/me/courses*`, `/api/courses/{id}/join`, bảng StudentCourse; trang MyCourses; nút Lưu. Ngoài: gợi ý theo node (P07). Nguồn: `docs/api-endpoints.md` §4; `docs/database-design.md` §3.3; D05; BA §6.4 (FR-17–19); `ui-design` MyCourses.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P06-T01 | Rà soát nguồn F03, F04 | Đối chiếu BA FR-17–19 với §4 và §3.3 | BA §6.4 | CPC (F03: Tâm; F04: Hòa — task gồm cả hai) | CXĐ | CPC | — | Ghi chú rà soát | NOT_STARTED | — | — |
| P06-T02 | Chuẩn bị đặc tả module | Course Tracking | Như trên | CPC (F03: Tâm; F04: Hòa — task gồm cả hai) | CXĐ | CPC | P06-T01 | Đề xuất `docs/modules/…` | NOT_STARTED | — | — |
| P06-T03 | Chuẩn bị test case | Gồm test chuyển trạng thái (bắt buộc) | `conventions.md` §6 | CPC (F03: Tâm; F04: Hòa — task gồm cả hai) | CXĐ | CPC | P06-T02 | Đề xuất `*.tests.md` | NOT_STARTED | — | — |
| P06-T04 | Model + migration StudentCourse | UNIQUE (`user_id`, `course_id`); 4 trạng thái | §3.3 | CPC (F03: Tâm; F04: Hòa — bảng dùng chung) | CXĐ | CPC | P01-T05, P02-T01, P04-T04 | Model + migration | NOT_STARTED | — | Một phần: migration chờ Alembic (P01-T05). Class model viết được theo §3.3 |
| P06-T06 | API tham gia khóa học | `bookmarked → ongoing`; thêm kỹ năng `learning` nếu chưa `known` | §4; D05 | Hòa | CXĐ | CPC | P06-T04, P04-T04 | API | NOT_STARTED | — | Một phần: chạy thật cần P06-T04. Logic D05 viết được |
| P06-T07 | API trạng thái khóa học của tôi | `GET /api/me/courses`, đổi trạng thái, `abandoned`; `completed` chỉ qua ôn tập | §4; §3.3 | Hòa | CXĐ | CPC | P06-T04 | API | NOT_STARTED | — | Một phần: chạy thật cần P06-T04. Logic chuyển trạng thái §3.3 viết được |
| P06-T08 | Test chuyển trạng thái (bắt buộc) | Hợp lệ/không hợp lệ; mở URL không thành `completed` | `conventions.md` §6 | Hòa | CXĐ | CPC | P06-T05…T07, P01-T08 | Kết quả `pytest` | NOT_STARTED | — | Một phần: chạy test cần P01-T08. Viết test làm được |
| P06-T09 | API client theo dõi | `courseTracking.api.js` — chia theo hàm giữa F03, F04 | `structure.md` §1 | CPC (F03: Tâm; F04: Hòa — task gồm cả hai) | CXĐ | CPC | P03-T03 | File API | NOT_STARTED | — | — |
| P06-T11 | Trang Khóa học của tôi | MyCoursesPage: Đang học, Đã lưu, Hoàn thành, Đã bỏ | `ui-design` MyCourses | CPC (`ui-design/pages.json`: "03–04 · Tâm, Hòa") | CXĐ | CPC | P06-T09 | Page | NOT_STARTED | — | — |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

## 3. Điều kiện hoàn thành, review, chặn

**4. Deliverables** — API §4; bảng StudentCourse; MyCourses; nút Lưu.
**5. Review Checklist** — Đúng chuyển trạng thái §3.3; D05; không coi mở link là hoàn thành.
**6. Blockers & Open Issues** — ND-32; người phụ trách StudentCourse.
**7. Completion Criteria** — Test chuyển trạng thái DONE; Task không bị chặn DONE.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
