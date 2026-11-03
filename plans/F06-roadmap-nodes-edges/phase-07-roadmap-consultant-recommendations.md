# F06 — Phase P07: Roadmap, AI Consultant & Recommendations (F05, F06, F07, F12)

> Thuộc kế hoạch tính năng [F06 — Các nút (Node) và liên kết (Edge) trong lộ trình học tập](plan.md). Phase `P07` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

Thông tin chung và phạm vi của Phase P07: xem [F05](../F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md). File này chỉ chứa các Task của F06.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P07-T07 | API node và cạnh | Thêm/sửa/xóa; xóa node kèm cạnh | §6, §7 | Hòa | CXĐ | CPC | P07-T04 | API | NOT_STARTED | — | Một phần: chạy thật cần P07-T04. Logic xóa node kèm cạnh viết được |
| P07-T14 | Trang Chi tiết lộ trình và đồ thị | PathDetailPage, PathGraph, panel gợi ý | `ui-design` PathDetail | Hòa | CXĐ | CPC | P07-T11 | Page + component | NOT_STARTED | — | Một phần: ND-54 |
| P07-T15 | Hộp thoại sửa lộ trình | PathEditDialog (thêm node, cạnh) | `ui-design` PathEdit | Hòa | CXĐ | CPC | P07-T14 | Component | NOT_STARTED | — | Một phần: ND-50 (`/edit`) |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

### Task dùng chung, quản lý ở tính năng khác

| Task ID | Task Name | Quản lý tại |
|---|---|---|
| P07-T01 | Rà soát nguồn F05–F07, F12 | [F05](../F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T02 | Chuẩn bị đặc tả module | [F05](../F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T03 | Chuẩn bị test case | [F05](../F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T04 | Model + migration lộ trình | [F05](../F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T10 | Test backend (gồm xóa node kèm cạnh) | [F05](../F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |
| P07-T11 | API client | [F05](../F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md) |

## 3. Điều kiện hoàn thành, review, chặn

Theo mục 4–7 của Phase P07 ở file quản lý chung của Phase (liên kết ở mục 1), áp dụng cho các Task trên. Quy tắc trạng thái và bằng chứng: `plans/plan.md` PART 2.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
