# F08 — Phase P08: AI Tutor (F08)

> Thuộc kế hoạch tính năng [F08 — Trò chuyện với gia sư AI](plan.md). Phase `P08` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

**1. Phase Information** — Phase ID: P08 · Objective: phiên hội thoại AI Tutor · Related Features: F08 · Responsible: Tâm (D-OWN-02) · Support: CXĐ · Reviewer: CPC · Dependencies: P04-T03 · Initial Status: NOT_STARTED

**2. Scope** — Trong: `/api/chat/sessions*`; bảng ChatSession, ChatMessage; trang Tutor. Ngoài: thiết kế mô hình và prompt (P12-T06). Nguồn: `docs/api-endpoints.md` §9; `docs/database-design.md` §5; BA §6.5 (FR-20–23); SRS FR-04–06, FR-08.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P08-T01 | Rà soát nguồn F08 | Đối chiếu BA FR-20–23, SRS FR-04–06, 08 với §9, §5 | BA §6.5; SRS §3 | Tâm | CXĐ | CPC | — | Ghi chú rà soát | NOT_STARTED | — | — |
| P08-T02 | Chuẩn bị đặc tả module | AI Tutor | Như trên | Tâm | CXĐ | CPC | P08-T01 | Đề xuất `docs/modules/…` | NOT_STARTED | — | Một phần: ND-59 |
| P08-T03 | Chuẩn bị test case | Chỉ chủ phiên xem được; xóa = archived | §9; `database-design.md` §5 | Tâm | CXĐ | CPC | P08-T02 | Đề xuất `*.tests.md` | NOT_STARTED | — | — |
| P08-T04 | Model + migration ChatSession, ChatMessage | `session_id` UUID | §5.1, §5.2 | Tâm | CXĐ | CPC | P01-T05, P04-T04 | Model + migration | NOT_STARTED | — | Một phần: migration chờ Alembic (P01-T05). Class model viết được theo §5 |
| P08-T05 | API phiên và tin nhắn | Tạo, liệt kê, xem, xóa (archived) phiên; gửi, liệt kê tin nhắn | §9 | Tâm | CXĐ | CPC | P08-T04 | API | NOT_STARTED | — | Một phần: chạy thật cần P08-T04; ND-59 (ngữ cảnh, chấm sao, bộ nhớ), ND-54. CRUD phiên (§9) làm được |
| P08-T06 | Test backend F08 | Theo P08-T03 | `conventions.md` §6 | Tâm | CXĐ | CPC | P08-T05, P01-T08 | Kết quả `pytest` | NOT_STARTED | — | Một phần: chạy test cần P01-T08. Viết test làm được |
| P08-T07 | API client Tutor | `tutor.api.js` | `structure.md` §1 | Tâm | CXĐ | CPC | P03-T03 | File API | NOT_STARTED | — | — |
| P08-T08 | Trang AI Tutor | TutorPage | `ui-design` Tutor | Tâm | CXĐ | CPC | P08-T07 | Page | NOT_STARTED | — | Một phần: ND-54 (code/quiz có cấu trúc) |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

## 3. Điều kiện hoàn thành, review, chặn

**4. Deliverables** — API §9; 2 bảng; trang Tutor.
**5. Review Checklist** — Kiểm quyền chủ phiên; xử lý lỗi AI trả thông báo rõ; không gửi thông tin cá nhân không cần thiết cho dịch vụ AI (BA NFR-31).
**6. Blockers & Open Issues** — ND-54, ND-59.
**7. Completion Criteria** — Task không bị chặn DONE.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
