# F07 — Phase P07: Roadmap, AI Consultant & Recommendations (F05, F06, F07, F12)

> Thuộc kế hoạch tính năng [F07 — Gợi ý khóa học cho một kỹ năng cụ thể](plan.md). Phase `P07` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

Thông tin chung và phạm vi của Phase P07: xem [F05](../F05-ai-consultant-learning-roadmap/phase-07-roadmap-consultant-recommendations.md). File này chỉ chứa các Task của F07.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P07-T08 | API gợi ý khóa học theo node | `GET …/nodes/{skill_id}/courses` | §8 | Tâm (D-OWN-02; trước: Hòa) | CXĐ | CPC | P07-T04, P02-T03 | API | NOT_STARTED | — | Một phần: chạy thật cần P07-T04; xếp hạng nâng cao ở P12-T05. `sort_by=rating` (§8) làm được |

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
| P07-T14 | Trang Chi tiết lộ trình và đồ thị | [F06](../F06-roadmap-nodes-edges/phase-07-roadmap-consultant-recommendations.md) |

## 3. Điều kiện hoàn thành, review, chặn

Theo mục 4–7 của Phase P07 ở file quản lý chung của Phase (liên kết ở mục 1), áp dụng cho các Task trên. Quy tắc trạng thái và bằng chứng: `plans/plan.md` PART 2.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
