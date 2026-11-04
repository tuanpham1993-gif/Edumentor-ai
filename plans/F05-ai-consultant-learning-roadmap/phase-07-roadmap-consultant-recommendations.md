# F05 — Phase P07: Roadmap, AI Consultant & Recommendations (F05, F06, F07, F12)

> Thuộc kế hoạch tính năng [F05 — Tư vấn viên AI và lộ trình học tập](plan.md). Phase `P07` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

**1. Phase Information** — Phase ID: P07 · Objective: tư vấn mục tiêu, lộ trình đồ thị, node/cạnh, gợi ý khóa học theo node, quan hệ kỹ năng · Related Features: F05, F06, F07, F12 · Responsible: theo từng tính năng — F05, F06: Hòa; F07, F12: Tâm (D-OWN-02) · Support: CXĐ · Reviewer: CPC · Dependencies: P02, P04-T03 · Initial Status: NOT_STARTED

**2. Scope** — Trong: `/api/chat/learning-path`, `/api/learning-paths*`, `/api/me/learning-paths`, node, edge, gợi ý §8, `/api/admin/skill-relations*`; bảng LearningPath, Node, Edge; trang Consultant, MyPaths, PathDetail, PathEdit, AdminSkills-Relations. Ngoài: thành phần mô hình AI (P12); mẫu lộ trình cơ sở (P11). Nguồn: `docs/api-endpoints.md` §5–§8, §11; `docs/database-design.md` §4.4–§4.6, §2.4; BA §6.2 (FR-05–11), §6.3 (FR-12–14), §6.7 (FR-31); SRS FR-03.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P07-T01 | Rà soát nguồn F05–F07, F12 | Đối chiếu BA FR-05–14, FR-31, SRS FR-03 với §5–§8, §11 | BA §6.2, §6.3, §6.7 | Hòa | CXĐ | CPC | — | Ghi chú rà soát | NOT_STARTED | — | — |
| P07-T02 | Chuẩn bị đặc tả module | Learning Path, gợi ý, quan hệ kỹ năng | Như trên | Hòa | CXĐ | CPC | P07-T01 | Đề xuất `docs/modules/…` | NOT_STARTED | — | Một phần: ND-60 |
| P07-T03 | Chuẩn bị test case | Gồm test xóa node kèm cạnh (bắt buộc) | `conventions.md` §6 | Hòa | CXĐ | CPC | P07-T02 | Đề xuất `*.tests.md` | NOT_STARTED | — | — |
| P07-T04 | Model + migration lộ trình | LearningPath, LearningPathNode, LearningPathEdge | §4.4–§4.6 | Hòa | CXĐ | CPC | P01-T05, P02-T02, P04-T04 | Model + migration | NOT_STARTED | — | Một phần: migration chờ Alembic (P01-T05). Class model viết được theo §4.4–§4.6 |
| P07-T05 | API AI Consultant | `POST /api/chat/learning-path`; xử lý việc lưu lộ trình đề xuất theo quy tắc thời điểm lưu được chủ dự án xác nhận sau khi giải quyết `SOURCE_CONFLICT` của F05 (`plan.md` mục 4, mục 7) | §5; `structure.md` §3 | Hòa | CXĐ | CPC | P07-T04 | API | BLOCKED | — | Cần làm rõ: hình dạng đầu ra phụ thuộc phương án AI (P12-T02) và ND-60; ND-54; chạy thật cần P07-T04 |
| P07-T06 | API lộ trình | CRUD `/api/learning-paths*`, `/api/me/learning-paths` | §5 | Hòa | CXĐ | CPC | P07-T04 | API | NOT_STARTED | — | Một phần: chạy thật cần P07-T04. Schema, service làm được |
| P07-T10 | Test backend (gồm xóa node kèm cạnh) | Theo test case P07-T03 | `conventions.md` §6 | Hòa | CXĐ | CPC | P07-T05…T09, P01-T08 | Kết quả `pytest` | NOT_STARTED | — | Một phần: chạy test cần P01-T08. Viết test làm được |
| P07-T11 | API client | `consultant.api.js`, `learningPaths.api.js`, `pathGraph.api.js`, `nodeSuggestions.api.js` | `structure.md` §1 | Hòa | CXĐ | CPC | P03-T03 | 4 file API | NOT_STARTED | — | — |
| P07-T12 | Trang AI tư vấn lộ trình | ConsultantPage | `ui-design` Consultant | Hòa | CXĐ | CPC | P07-T11 | Page | NOT_STARTED | — | — |
| P07-T13 | Trang Lộ trình của tôi | MyPathsPage | `ui-design` MyPaths | Hòa | CXĐ | CPC | P07-T11 | Page | NOT_STARTED | — | Một phần: ND-54 (tên lộ trình) |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

### Task dùng chung, quản lý ở tính năng khác

| Task ID | Task Name | Quản lý tại |
|---|---|---|
| P07-T14 | Trang Chi tiết lộ trình và đồ thị | [F06](../F06-roadmap-nodes-edges/phase-07-roadmap-consultant-recommendations.md) |

## 3. Điều kiện hoàn thành, review, chặn

**4. Deliverables** — API §5–§8 và skill-relations; 3 bảng; 5 màn; đặc tả và test case đề xuất.
**5. Review Checklist** — Thời điểm lưu lộ trình đề xuất theo quy tắc được chủ dự án xác nhận sau khi giải quyết `SOURCE_CONFLICT` của F05; xóa node không để cạnh mồ côi; gợi ý chỉ tải khi chọn node (`structure.md` §3).
**6. Blockers & Open Issues** — ND-24, ND-54, ND-60; phần AI ở P12.
**7. Completion Criteria** — Test xóa node kèm cạnh DONE; Task không bị chặn DONE.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
