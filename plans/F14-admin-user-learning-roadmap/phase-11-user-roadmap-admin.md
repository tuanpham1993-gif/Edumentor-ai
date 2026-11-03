# F14 — Phase P11: User Roadmap Admin & Related Functionality (F14)

> Thuộc kế hoạch tính năng [F14 — Quản trị — xem lộ trình học tập của người dùng](plan.md). Phase `P11` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

Thông tin chung và phạm vi của Phase P11: xem [`plans/plan.md`](../plan.md). File này chỉ chứa các Task của F14.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P11-T01 | Rà soát nguồn F14 | F14 chỉ có trong README và `ui-design`; không có FR, không có endpoint | `README.md`; ND-55 (M3) | Hòa | CXĐ | CPC | — | Ghi chú rà soát | NOT_STARTED | — | — |
| P11-T02 | Trang Lộ trình người dùng | AdminUserPathsPage "chưa khả dụng" (D-FE-08) | `ui-design` AdminUserPaths | Hòa | CXĐ | CPC | P03-T04, P07-T14 (PathGraph) | Page | NOT_STARTED | — | Một phần: ND-55 (M3) |
| P11-T03 | Backend lộ trình người dùng (M3) | Endpoint xem danh sách người dùng và lộ trình | ND-55 (M3) | Hòa | CXĐ | CPC | P07-T04, P04-T03 | API | BLOCKED | — | ND-55 (M3) |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

## 3. Điều kiện hoàn thành, review, chặn

Theo mục 4–7 của Phase P11 ở file quản lý chung của Phase (liên kết ở mục 1), áp dụng cho các Task trên. Quy tắc trạng thái và bằng chứng: `plans/plan.md` PART 2.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
