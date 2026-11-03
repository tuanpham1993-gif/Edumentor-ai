# F10 — Phase P10: Feedback (F10, F13)

> Thuộc kế hoạch tính năng [F10 — Phản hồi (Feedback)](plan.md). Phase `P10` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

**1. Phase Information** — Phase ID: P10 · Objective: giao diện phản hồi và quản trị phản hồi; backend khi có quyết định · Related Features: F10, F13 · Responsible: theo từng tính năng — F10: Khôi, F13: Hòa (D-OWN-02) · Support: CXĐ · Reviewer: CPC · Dependencies: P03 (giao diện); ND-35, ND-55, ND-69 (backend) · Initial Status: NOT_STARTED

**2. Scope** — Trong: trang Contact, ContactGuest, AdminFeedback, AdminFeedback-Detail ở trạng thái "chưa khả dụng" (D-FE-08); rà soát nguồn. Ngoài: endpoint M2 cho tới khi có quyết định. Nguồn: `docs/database-design.md` §7; `docs/decisions.md` D11, ND-35, ND-55, ND-69; BA §4.1.2 (không có FR riêng); `ui-design`.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P10-T01 | Rà soát nguồn phản hồi | Tổng hợp D11, ND-35, ND-55, ND-69, BA §4.1.2, §7.1–§7.2 | Như Scope | Khôi (D-OWN-02; trước: CPC) | CXĐ | CPC | — | Ghi chú rà soát | NOT_STARTED | — | Người phụ trách (C3) |
| P10-T02 | Chuẩn bị đặc tả module | Chỉ phần đã chốt | Như trên | Khôi (D-OWN-02; trước: CPC) | CXĐ | CPC | P10-T01 | Đề xuất `docs/modules/…` | NOT_STARTED | — | Một phần: ND-35, ND-55 (M2), ND-69. Đặc tả được phần đã chốt (D11; `database-design.md` §7.1–§7.2) |
| P10-T03 | Trang Liên hệ và góp ý | FeedbackPage hiển thị "chưa khả dụng" cho phần chưa có endpoint | D-FE-08; `ui-design` Contact | Khôi (D-OWN-02; trước: CPC) | CXĐ | CPC | P03-T04, P03-T05 | Page | NOT_STARTED | — | Một phần: ND-69 (ô loại phản hồi) |
| P10-T04 | Trạng thái chưa đăng nhập | ContactGuest | `ui-design` ContactGuest | Khôi (D-OWN-02; trước: CPC) | CXĐ | CPC | P10-T03 | Trạng thái giao diện | NOT_STARTED | — | Một phần: ND-50 chỉ hỏi về route `/contact-guest`; trạng thái chưa đăng nhập có thể làm trong `/contact` |
| P10-T06 | Backend phản hồi (M2) | Endpoint gửi, xem liên hệ khóa học, quản trị | ND-55 (M2) | Khôi (D-OWN-02; trước: CPC) | CXĐ | CPC | P10-T02, P04-T03 | API | BLOCKED | — | ND-35, ND-55, ND-69 |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

## 3. Điều kiện hoàn thành, review, chặn

**4. Deliverables** — Giao diện "chưa khả dụng"; backend sau khi có quyết định.
**5. Review Checklist** — Không tạo endpoint hay API giả (D-FE-08); không khẳng định danh sách loại phản hồi khi ND-69 chưa chốt.
**6. Blockers & Open Issues** — C3; D11/ND-69; ND-35; ND-55 (M2); BA thiếu FR.
**7. Completion Criteria** — Giao diện "chưa khả dụng" DONE; phần backend theo quyết định.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
