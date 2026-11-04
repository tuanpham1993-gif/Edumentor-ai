# F08 — Phase P12: AI/ML Work

> Thuộc kế hoạch tính năng [F08 — Trò chuyện với gia sư AI](plan.md). Phase `P12` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

Thông tin chung và phạm vi của Phase P12: xem [`plans/plan.md`](../plan.md). File này chỉ chứa các Task của F08.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P12-T06 | Hành vi AI Tutor | Prompt, ngữ cảnh hội thoại theo BA §8.5, §9.5 | BA §8.5, §9.5; SRS FR-05 | CPC | CXĐ | CPC | P08-T05 | Cấu hình + test | NOT_STARTED | — | Một phần: ND-59. Quy tắc hành vi ở BA §8.5, §9.5 dùng được |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

## 3. Điều kiện hoàn thành, review, chặn

Theo mục 4–7 của Phase P12 ở file quản lý chung của Phase (liên kết ở mục 1), áp dụng cho các Task trên. Quy tắc trạng thái và bằng chứng: `plans/plan.md` PART 2.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
