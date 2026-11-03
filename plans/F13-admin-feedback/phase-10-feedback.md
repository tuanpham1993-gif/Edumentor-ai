# F13 — Phase P10: Feedback (F10, F13)

> Thuộc kế hoạch tính năng [F13 — Quản trị — quản lý phản hồi](plan.md). Phase `P10` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

Thông tin chung và phạm vi của Phase P10: xem [F10](../F10-feedback/phase-10-feedback.md). File này chỉ chứa các Task của F13.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P10-T05 | Trang Quản trị phản hồi | AdminFeedbackPage, ngăn chi tiết; "chưa khả dụng" | D-FE-08; `ui-design` AdminFeedback | Hòa (D-OWN-02; trước: CPC) | CXĐ | CPC | P03-T04 | Page | NOT_STARTED | — | Một phần: ND-69, UI2-06 |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

### Task dùng chung, quản lý ở tính năng khác

| Task ID | Task Name | Quản lý tại |
|---|---|---|
| P10-T01 | Rà soát nguồn phản hồi | [F10](../F10-feedback/phase-10-feedback.md) |
| P10-T02 | Chuẩn bị đặc tả module | [F10](../F10-feedback/phase-10-feedback.md) |
| P10-T06 | Backend phản hồi (M2) | [F10](../F10-feedback/phase-10-feedback.md) |

## 3. Điều kiện hoàn thành, review, chặn

Theo mục 4–7 của Phase P10 ở file quản lý chung của Phase (liên kết ở mục 1), áp dụng cho các Task trên. Quy tắc trạng thái và bằng chứng: `plans/plan.md` PART 2.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
