# F09 — Ôn tập và đánh giá kiến thức

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở [phase-09-review-assessment.md](phase-09-review-assessment.md) và [phase-12-ai-ml.md](phase-12-ai-ml.md). Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F09 — Ôn tập và đánh giá kiến thức |
| Người phụ trách | **Tuấn** (D-OWN-01, D-OWN-02, `docs/decisions.md` §2) |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/review-assessment.md`](../../docs/modules/review-assessment.md) — SPEC CONFIRMED, trừ RV-R03, RV-R10, RV-R13 BLOCKED (T16 ☐); kịch bản test [`review-assessment.tests.md`](../../docs/modules/review-assessment.tests.md) |
| Skill | `.claude/skills/review-assessment/SKILL.md` |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (03/11/2026) | 16 Task: NOT_STARTED 15 · BLOCKED 1 (P12-T07) — đếm từ file phase |

## 2. Mục tiêu

Bài ôn tập 20 câu trắc nghiệm **theo khóa học** (D01), chấm điểm, đạt ≥ `REVIEW_PASS_PERCENT` (60%, D02) thì khóa học thành `completed` và kỹ năng của khóa thành `known`; lịch sử ôn tập; email kết quả (`review-assessment.md` §1).

## 3. Phạm vi

**Trong:** `GET /api/courses/{course_id}/review`, `POST /api/courses/{course_id}/review-attempts`, `GET /api/review-attempts/{attempt_id}`, `POST /api/review-attempts/{attempt_id}/submit`, `GET /api/me/review-history`, `GET /api/me/review-history/{attempt_id}`; bảng `Question` (chỉ đọc), `ReviewAttempt`, `ReviewAnswer`; màn ReviewStart … ReviewDetail.

**Ngoài:** quản trị câu hỏi `/api/admin/questions*` (ngoài 14 tính năng, P11-T06, CONFLICT-SCOPE-01); `GET/PATCH /api/me/skills` (F01); `join` (F04); cập nhật lộ trình sau khi đạt (T18 ☐, ND-24).

## 4. Mức độ sẵn sàng

### 4.1. Theo phần

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `READY_WITH_LIMITATIONS` | D01 … D04, D10, T11 … T17, T29 đã chốt; BA FR-24, §8.6 khác D01 (ND-58); câu mở, điểm trung bình ND-73 |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | BA AC-07; SRS-REV-01 … 09 chưa đưa vào đặc tả. Câu hỏi cho Tuấn (D-OWN-01, D-OWN-02): có đưa SRS-REV-01 … 09 vào `docs/modules/review-assessment.md` §1 không? |
| UI | `READY_WITH_LIMITATIONS` | 6 màn; lưu bài dở chưa có endpoint (ND-55, M1); ND-51, ND-54 |
| API | `READY_WITH_LIMITATIONS` | §4 đủ cho 6 endpoint; ND-26, ND-33, ND-34; T16 ☐ |
| Database | `READY_WITH_LIMITATIONS` | §6.1 … §6.3; `submitted_at` chờ ND-31 (T27 ☐) |
| Kiểm thử | `READY_WITH_LIMITATIONS` | [`review-assessment.tests.md`](../../docs/modules/review-assessment.tests.md): 53 kịch bản; 39 viết được ngay; 14 có cột "Chờ" (phụ thuộc `[NEEDS DECISION]`, chỉ viết khi điểm đó đã chốt): RV-T06, T10, T13, T22, T33, T40, T47, T50, T64, T65, T66, T70, T77, T80 |
| **Dữ liệu câu hỏi** | **`BLOCKED_DATASET`** | Chưa có nguồn câu hỏi chính thức (mục 4.2) |
| Phụ thuộc | `NOT_READY_BLOCKED` | P01-T05 (Alembic), P06-T04 (`StudentCourse`), P04-T03 (`get_current_user`) |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú; `BLOCKED_DATASET` — bị chặn vì chưa có dữ liệu chính thức (mục 4.2).

### 4.2. Dữ liệu câu hỏi — `BLOCKED_DATASET`

FACT: repo không chứa bộ câu hỏi ôn tập. Dataset khóa học, kỹ năng nằm ngoài repo và chưa xác định vị trí dùng chung (P02-T05, `plans/plan.md` PART 6 "Dataset không có trong repo"); dataset đó không có câu hỏi. `P09-T03` ghi "Nguồn câu hỏi chưa xác định".

**Không** tự tạo câu hỏi, đáp án hay dữ liệu đánh giá để thay dataset chính thức.

| Mục | Nội dung |
|---|---|
| Dataset cần bổ sung | Ngân hàng câu hỏi trắc nghiệm theo kỹ năng, đủ để mỗi khóa học có bài ôn tập: tổng câu `is_active` của các kỹ năng khóa dạy ≥ 20 (D04, RV-R02) |
| Trường đã được nguồn xác nhận | `skill_id`, `content`, `options` (đúng 4 đáp án), `correct_index` (0–3), `explanation`, `is_active` (`database-design.md` §6.1; T19, T21, T26) |
| Trường hoặc điểm chưa rõ | Nguồn và người soạn câu hỏi; số câu tối thiểu cho từng kỹ năng (D04 chỉ quy định tổng theo khóa); `explanation` có bắt buộc không (CSDL cho NULL); ngôn ngữ; định dạng file nhập (T21 ghi CSV/JSON, tùy chọn, chưa có cấu trúc cột); dạng câu hỏi khác trắc nghiệm (ND-73); có dùng RAG không (ND-58) |
| Nơi nạp dữ liệu | Quản trị câu hỏi `/api/admin/questions*` (P11-T06, BLOCKED: ND-53, CONFLICT-SCOPE-01) hoặc script nạp dữ liệu (P02-T06 dùng chung) — chưa chốt |

| Task | Phụ thuộc dataset? | Làm trước được |
|---|---|---|
| P09-T03 Nguồn dữ liệu câu hỏi | **Có — `BLOCKED_DATASET`** | Không |
| P09-T04 `GET .../review` | Chạy với dữ liệu thật: có | Logic đếm câu, lý do `available = false` (RV-R02) |
| P09-T05 Bắt đầu bài | Chạy với dữ liệu thật: có | Chọn 20 câu, tạo sẵn ReviewAnswer (RV-R06; phần dư chờ ND-20) |
| P09-T06, T07, T09 | Chạy với dữ liệu thật: có | Logic chấm điểm, transaction, ẩn đáp án, lịch sử |
| P09-T08 Email kết quả | Không | Theo T29; ND-25, ND-66 |
| P09-T10 Test backend | Test cần câu hỏi trong CSDL test | Dữ liệu giả **chỉ trong test**, không phải dataset — cần người phụ trách xác nhận (`NEEDS_OWNER_CONFIRMATION`) |
| P09-T11 … T15 Frontend | Không (mock D-FE-07) | Làm được sau P03-T03 … T05 |
| P09-T01, P09-T02 | Không | Đối chiếu; model, migration (migration chờ P01-T05) |
| P12-T07 RAG | Có | BLOCKED (mâu thuẫn D01, RV-R01; ND-58) |

Chức năng F09 **không** được coi là hoàn thành khi chưa có dataset câu hỏi.

## 5. Phase và Task

| Phase | File | Task |
|---|---|---|
| P09 | [phase-09-review-assessment.md](phase-09-review-assessment.md) | P09-T01 … P09-T15 |
| P12 | [phase-12-ai-ml.md](phase-12-ai-ml.md) | P12-T07 |

Phase dùng chung P00–P03, P13 và quản trị câu hỏi (P11-T06): [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

| Task F09 | Phụ thuộc | Thuộc |
|---|---|---|
| P09-T02 | P01-T05, P02-T02, P06-T04 | dùng chung, F04 |
| P09-T07 | P04-T04 | F01 |
| P09-T08 | P04-T08 (`core/email.py`) | F01 |
| P09-T10 | P01-T08 | dùng chung |
| P09-T11 | P03-T03 | dùng chung |

Nguồn câu hỏi phụ thuộc P11-T06 (quản trị câu hỏi, ngoài 14 tính năng) hoặc P02-T06 (nạp dữ liệu), cả hai chưa chốt.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Xác định nguồn và người soạn bộ câu hỏi; bổ sung dataset theo mục 4.2.
2. Đưa T16 ra nhóm tick (RV-R03, R10, R13 đang BLOCKED).
3. Xác nhận việc dùng dữ liệu giả trong test (không phải dataset chính thức).
4. Đưa mã SRS-REV-01 … 09 vào `review-assessment.md` §1.
5. Theo dõi ND-58 (RAG, theo kỹ năng) và ND-77 (đề bài 10 câu) với giảng viên — ND-77 ưu tiên cao, cần trước khi code F09.

## 8. Điều kiện hoàn thành và bằng chứng

- Task không bị chặn DONE có Evidence và kết quả review; Task BLOCKED ghi mã chặn.
- Không DONE phần phụ thuộc dataset khi chưa có dataset chính thức.
- Bằng chứng: kết quả `pytest tests/test_review.py`; kiểm tra chống lộ đáp án (`.tests.md` §7); ảnh 6 màn; email thử không chứa đáp án.

## 9. Tài liệu nguồn

BA §6.6 (FR-24 … FR-29), §8.6, §9.6 (BR-26 … BR-31), §10.10, UC-09, UC-10, AC-07; SRS §6.8 (SRS-REV-01 … 09); `docs/decisions.md` D01 … D04, D10, T11 … T29, §4.2; `docs/modules/review-assessment.md`, `.tests.md`; `docs/api-endpoints.md` §10; `docs/database-design.md` §6; `docs/ui-design/` S-21 … S-25.
