# F05 — Tư vấn viên AI và lộ trình học tập

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở file `phase-NN-*.md` của thư mục này. Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F05 — Tư vấn viên AI và lộ trình học tập |
| Người phụ trách | **Hòa** (D-OWN-02, `docs/decisions.md` §2) |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/learning-path-consultant.md`](../../docs/modules/learning-path-consultant.md) — DRAFT, chưa được người phụ trách xác nhận |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (2026-11-03) | 13 Task: BLOCKED 1 · NOT_STARTED 12 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Nhận mục tiêu qua AI Consultant, phân tích, xác định kỹ năng, tạo lộ trình đề xuất dạng đồ thị; lưu lộ trình theo quy tắc thời điểm lưu được chủ dự án xác nhận sau khi giải quyết `SOURCE_CONFLICT` (mục 4); xem, sửa thông tin, từ bỏ lộ trình (`docs/modules/learning-path-consultant.md` §1).

## 3. Phạm vi

Theo `docs/modules/learning-path-consultant.md` §1 ("Thuộc module", "Không thuộc module"). Tóm tắt: `POST /api/chat/learning-path`, `/api/me/learning-paths`, `/api/learning-paths*` (trừ node, cạnh); màn Consultant, MyPaths; phần AI ở P12-T02 … T04.

## 4. Mức độ có căn cứ

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `READY_WITH_LIMITATIONS` | BA FR-05 … FR-09, BR-01 … BR-09; `SOURCE_CONFLICT`: thời điểm lưu lộ trình — BA UC-04 bước 7 và Postconditions ghi lưu khi tạo thành công; `api-endpoints.md` §5, `database-design.md` §4.4 và LP-R01 (`docs/modules/learning-path-consultant.md`) ghi chỉ lưu khi người dùng xác nhận. Chưa có ND (ND-74 không bao gồm điểm này); không tự chọn nguồn; cần chủ dự án xem xét một đề xuất ND mới |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | BA AC-02, AC-03; SRS-PATH-01 … 07 — các mã này chưa có trong `docs/modules/learning-path-consultant.md`. Câu hỏi cho Hòa (D-OWN-02): AC-02, AC-03, SRS-PATH-01 … 07 có phải tiêu chí nghiệm thu chính thức của F05 để đưa vào đặc tả không? Việc tài liệu kiểm thử (riêng): chưa có `docs/modules/learning-path-consultant.tests.md`, cần tạo |
| UI | `READY_WITH_LIMITATIONS` | Consultant, MyPaths; tên lộ trình ND-54 |
| API | `READY_WITH_LIMITATIONS` | CRUD `/api/learning-paths*`, `/api/me/learning-paths` làm được (P07-T06: schema, service; chạy thật cần P07-T04); giới hạn: `POST /api/chat/learning-path` chặn bởi hợp đồng tư vấn ND-74 và phương án AI chưa duyệt (P12-T02) |
| Database | `READY_WITH_LIMITATIONS` | §4.4–§4.6, §5 làm được; giới hạn: `LearningPath` chỉ có `goal_text`, chưa có tên lộ trình (`name`) mà UI hiển thị — ND-54 |
| Kiểm thử | `NEEDS_OWNER_INPUT` | Chưa có test case. Câu hỏi cho Hòa (D-OWN-02): danh sách kịch bản kiểm thử của F05 là gì, dựa trên tiêu chí nghiệm thu nào? Chưa có `docs/modules/learning-path-consultant.tests.md` |
| Phụ thuộc | `NOT_READY_BLOCKED` | P07-T04 chờ P01-T05; ND-60, ND-77 |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú.

## 5. Phase và Task

| Phase | File | Task quản lý tại thư mục này |
|---|---|---|
| P07 | [phase-07-roadmap-consultant-recommendations.md](phase-07-roadmap-consultant-recommendations.md) | P07-T01, P07-T02, P07-T03, P07-T04, P07-T05, P07-T06, P07-T10, P07-T11, P07-T12, P07-T13 |
| P12 | [phase-12-ai-ml.md](phase-12-ai-ml.md) | P12-T02, P12-T03, P12-T04 |

Task dùng chung quản lý ở tính năng khác: P07-T14 (F06).

Các Phase khác của khung chung (P00–P03, P13) là phần dùng chung, quản lý tại [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

Lấy từ cột Dependencies của các Task (không thêm phụ thuộc mới):

| Task | Phụ thuộc | Thuộc |
|---|---|---|
| P07-T04 | P01-T05 | dùng chung |
| P07-T04 | P02-T02 | dùng chung |
| P07-T04 | P04-T04 | F01 |
| P07-T10 | P01-T08 | dùng chung |
| P07-T11 | P03-T03 | dùng chung |
| P12-T02 | P12-T01 | dùng chung |
| P12-T04 | P12-T01 | dùng chung |

Quyết định còn chờ ảnh hưởng tính năng: ND-74, ND-60, ND-54, ND-24, ND-77, ND-81.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Xác nhận đặc tả `docs/modules/learning-path-consultant.md`.
2. Đề xuất hợp đồng `POST /api/chat/learning-path` cho ND-74.
3. Làm rõ thời điểm lưu lộ trình (BA UC-04 bước 7 so với `api-endpoints.md` §5).
4. Ghi có lưu hội thoại tư vấn vào `ChatSession` không.
5. Phối hợp với F06, F07, F12 về Task dùng chung P07-T01 … T04, T10, T11.
6. Soạn kịch bản kiểm thử.

## 8. Điều kiện hoàn thành và bằng chứng

- Mọi Task bắt buộc của tính năng DONE, có Evidence và kết quả review (`plans/plan.md` PART 2 quy tắc 5, 6). Tạo file kế hoạch **không** phải DONE.
- Đặc tả `docs/modules/learning-path-consultant.md` được người phụ trách xác nhận (DRAFT → SPEC CONFIRMED) trước khi code phần phụ thuộc đặc tả.
- Bằng chứng cần có: kết quả `pytest`, ảnh Consultant, MyPaths, báo cáo đánh giá AI (P12).
- Task BLOCKED ghi rõ mã chặn; phần không phụ thuộc vẫn được làm.

## 9. Tài liệu nguồn

BA §6.2 (FR-05 … FR-09), §8.2, §9.1, §9.2, §10.5, UC-03, UC-04, AC-02, AC-03; SRS §6.5 (SRS-PATH-01 … 07); `docs/api-endpoints.md` §5, §12; `docs/database-design.md` §4, §5; `docs/structure.md` §5; `docs/modules/learning-path-consultant.md`.
