# F05 — Phase P12: AI/ML Work

> Thuộc kế hoạch tính năng [F05 — Tư vấn viên AI và lộ trình học tập](plan.md). Phase `P12` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

Thông tin chung và phạm vi của Phase P12: xem [`plans/plan.md`](../plan.md). File này chỉ chứa các Task của F05.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P12-T02 | Đề xuất phương án AI Consultant | Từ BA §8.2 (bao gồm QLoRA §8.2.2) — chỉ đề xuất, chờ nhóm phê duyệt | BA §8.2; SRS FR-03 | CPC | CXĐ | CPC | P12-T01 | Đề xuất gửi P00 | NOT_STARTED | — | Công nghệ chưa phê duyệt; ND-60 |
| P12-T03 | Kiểm tra đầu ra AI | Kỹ năng AI trả về phải có trong danh mục; kiểm tra trước khi lưu | BA BR-07, FR-38, §8.2.4; `conventions.md` §2 | CPC | CXĐ | CPC | P07-T05 | Hàm kiểm tra + test | NOT_STARTED | — | Một phần: định dạng đầu ra cần P07-T05. Kiểm "kỹ năng phải có trong danh mục" (BR-07, FR-38, `conventions.md` §2) viết được |
| P12-T04 | Skill Graph | Đối chiếu BA §8.3 với SkillRelation và lộ trình đồ thị | BA §8.3; `database-design.md` §2.4, §4 | CPC | CXĐ | CPC | P12-T01 | Ghi chú đối chiếu | NOT_STARTED | — | Chiều SkillRelation chưa xác nhận |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

## 3. Điều kiện hoàn thành, review, chặn

Theo mục 4–7 của Phase P12 ở file quản lý chung của Phase (liên kết ở mục 1), áp dụng cho các Task trên. Quy tắc trạng thái và bằng chứng: `plans/plan.md` PART 2.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
