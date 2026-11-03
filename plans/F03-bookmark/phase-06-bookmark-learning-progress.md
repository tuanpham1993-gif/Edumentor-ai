# F03 — Phase P06: Bookmark & Learning Progress (F03, F04)

> Thuộc kế hoạch tính năng [F03 — Đánh dấu (Bookmark)](plan.md). Phase `P06` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

Thông tin chung và phạm vi của Phase P06: xem [F04](../F04-course-progress/phase-06-bookmark-learning-progress.md). File này chỉ chứa các Task của F03.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P06-T05 | API bookmark | Lưu, bỏ lưu (chỉ khi `bookmarked`), danh sách | §4; §3.3 | Tâm | CXĐ | CPC | P06-T04 | API | NOT_STARTED | — | Một phần: chạy thật cần P06-T04. Ghi chú: ND-32 (`decisions.md` §4.4) chỉ ghi nhận file `models/bookmark.py`, không chặn — thiết kế dùng StudentCourse |
| P06-T10 | Nút Lưu | Trên CourseCard, CourseDetail, danh sách gợi ý | `ui-design` Courses, CourseDetail | Tâm | CXĐ | CPC | P06-T09, P05-T11 | Component | NOT_STARTED | — | — |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

### Task dùng chung, quản lý ở tính năng khác

| Task ID | Task Name | Quản lý tại |
|---|---|---|
| P06-T01 | Rà soát nguồn F03, F04 | [F04](../F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T02 | Chuẩn bị đặc tả module | [F04](../F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T03 | Chuẩn bị test case | [F04](../F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T04 | Model + migration StudentCourse | [F04](../F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T09 | API client theo dõi | [F04](../F04-course-progress/phase-06-bookmark-learning-progress.md) |
| P06-T11 | Trang Khóa học của tôi | [F04](../F04-course-progress/phase-06-bookmark-learning-progress.md) |

## 3. Điều kiện hoàn thành, review, chặn

Theo mục 4–7 của Phase P06 ở file quản lý chung của Phase (liên kết ở mục 1), áp dụng cho các Task trên. Quy tắc trạng thái và bằng chứng: `plans/plan.md` PART 2.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
