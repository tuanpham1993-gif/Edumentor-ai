# F09 — Phase P09: Review & Assessment (F09)

> Thuộc kế hoạch tính năng [F09 — Ôn tập và đánh giá kiến thức](plan.md). Phase `P09` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

**1. Phase Information** — Phase ID: P09 · Objective: bài ôn tập 20 câu theo khóa học, chấm điểm, ghi nhận kỹ năng · Related Features: F09 · Responsible: Tuấn (D-OWN-01, D-OWN-02) · Support: CXĐ · Reviewer: CPC · Dependencies: P04-T03, P05-T05, P06-T04 · Initial Status: NOT_STARTED

**2. Scope** — Trong: `/api/courses/{id}/review*`, `/api/review-attempts*`, `/api/me/review-history*`; bảng Question, ReviewAttempt, ReviewAnswer; trang ReviewStart, ReviewQuiz, ReviewResult, ReviewHistory, ReviewDetail (+Explanation). Ngoài: `/api/admin/questions*` (P11, CONFLICT-SCOPE-01); RAG (P12-T07). Nguồn: `docs/modules/review-assessment.md`, `.tests.md`; `docs/api-endpoints.md` §10; `docs/database-design.md` §6; D01–D04, D10; BA §6.6 (FR-24–29).

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P09-T01 | Đối chiếu đặc tả F09 với BA/SRS | So `review-assessment.md` với BA FR-24–29, §8.6, SRS FR-07 | BA §6.6, §8.6; ND-58 | Tuấn | CXĐ | CPC | — | Ghi chú đối chiếu | NOT_STARTED | — | ND-58 (PENDING) |
| P09-T02 | Model + migration ôn tập | Question, ReviewAttempt, ReviewAnswer | §6; RV-R01 | Tuấn | CXĐ | CPC | P01-T05, P02-T02, P06-T04 | Model + migration | NOT_STARTED | — | Một phần: migration chờ Alembic (P01-T05); cột `submitted_at` chờ ND-31. Class model viết được theo §6 |
| P09-T03 | Nguồn dữ liệu câu hỏi | Xác định nguồn ngân hàng câu hỏi để có ≥ 20 câu cho khóa học (D04) — **chưa có trong tài liệu** | D04; RV-R02 | Tuấn | CXĐ | CPC | — | Nguồn dữ liệu được xác nhận | NOT_STARTED | — | Nguồn câu hỏi chưa xác định; `/api/admin/questions*` CONFLICT-SCOPE-01 |
| P09-T04 | `GET /api/courses/{id}/review` | Kiểm tra khóa có bài ôn tập | §4.1; RV-R02 | Tuấn | CXĐ | CPC | P09-T02 | API | NOT_STARTED | — | Một phần: chạy thật cần P09-T02; T16 (☐), ND-28. RV-R02 đã chốt |
| P09-T05 | `POST …/review-attempts` | Tạo hoặc trả lại bài dở; ghi sẵn 20 câu | §4.2; D03, D04; RV-R04, R06 | Tuấn | CXĐ | CPC | P09-T02 | API | NOT_STARTED | — | Một phần: chạy thật cần P09-T02; T16 (☐), ND-20 (phần dư khi chia câu), ND-29, ND-33. D03, D04 đã chốt |
| P09-T06 | `GET /api/review-attempts/{id}` | Không trả đáp án trước khi nộp | §4.3; RV-R07 | Tuấn | CXĐ | CPC | P09-T05 | API | NOT_STARTED | — | Một phần: chạy thật cần P09-T05; ND-26. RV-R07 làm được |
| P09-T07 | `POST …/submit` (một transaction) | Chấm điểm, `completed`, UserSkill `known` | §4.4; §7; D02, D10 | Tuấn | CXĐ | CPC | P09-T05, P04-T04 | API | NOT_STARTED | — | Một phần: chạy thật cần P09-T05; T16 (☐; RV-R10, R13), ND-22, ND-23, ND-24. Chấm điểm RV-R11, D02, transaction §7 làm được |
| P09-T08 | Email kết quả | Gửi nền sau commit | RV-R18; T29 | Tuấn | CXĐ | CPC | P09-T07, P04-T08 | Email | NOT_STARTED | — | Một phần: ND-25 (gửi khi nào), ND-66 (route trong link); nội dung email chưa thống nhất giữa T29 và `.docx` 6.2 (chưa có ND). Gửi nền sau commit (RV-R18) làm được |
| P09-T09 | Lịch sử ôn tập | `GET /api/me/review-history*` | §4.5, §4.6 | Tuấn | CXĐ | CPC | P09-T07 | API | NOT_STARTED | — | Một phần: chạy thật cần P09-T07; ND-26, ND-27, ND-34. Phân trang, lọc (T17) làm được |
| P09-T10 | Test backend F09 | Kịch bản không có cột "Chờ" và không thuộc T16 | `review-assessment.tests.md`; skill `review-assessment` §7 | Tuấn | CXĐ | CPC | P09-T04…T09, P01-T08 | `tests/test_review.py`, kết quả `pytest` | NOT_STARTED | — | Một phần: chạy test cần P01-T08. Viết test cho kịch bản không có cột "Chờ" làm được |
| P09-T11 | API client ôn tập | `review.api.js`; ngưỡng đạt lấy từ server | D-FE-11 | Tuấn | CXĐ | CPC | P03-T03 | File API | NOT_STARTED | — | — |
| P09-T12 | Trang Bắt đầu ôn tập | ReviewStartPage | `ui-design` ReviewStart | Tuấn | CXĐ | CPC | P09-T11 | Page | NOT_STARTED | — | Một phần: ND-51, ND-54 |
| P09-T13 | Trang Làm bài | ReviewAttemptPage | `ui-design` ReviewQuiz | Tuấn | CXĐ | CPC | P09-T11 | Page | NOT_STARTED | — | Một phần: ND-55 (M1 lưu bài dở), ND-54, ND-51 |
| P09-T14 | Trang Kết quả | ReviewResultPage | `ui-design` ReviewResult | Tuấn | CXĐ | CPC | P09-T11 | Page | NOT_STARTED | — | — |
| P09-T15 | Trang Lịch sử, Chi tiết lần làm | ReviewHistoryPage, ReviewDetailPage (ẩn/hiện giải thích) | `ui-design` ReviewHistory, ReviewDetail | Tuấn | CXĐ | CPC | P09-T11 | 2 page | NOT_STARTED | — | Một phần: ND-27 |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

## 3. Điều kiện hoàn thành, review, chặn

**4. Deliverables** — API §10; 3 bảng; 6 màn; `test_review.py`.
**5. Review Checklist** — RV-R01…R20 (trừ phần BLOCKED); không lộ `correct_index`/`explanation` trước khi nộp; transaction nộp bài; frontend không gửi cập nhật kỹ năng sau khi nộp (RV-R20).
**6. Blockers & Open Issues** — T16; ND-20…34, 58, 66; nguồn câu hỏi; BA §8.6 (RAG).
**7. Completion Criteria** — Task không bị chặn DONE; test chấm điểm (bắt buộc) DONE.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.
