# F06 — Các nút (Node) và liên kết (Edge) trong lộ trình học tập

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở file `phase-NN-*.md` của thư mục này. Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F06 — Các nút (Node) và liên kết (Edge) trong lộ trình học tập |
| Người phụ trách | **Hòa** (D-OWN-02, `docs/decisions.md` §2) |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/learning-path-graph.md`](../../docs/modules/learning-path-graph.md) — DRAFT, chưa được người phụ trách xác nhận |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (2026-11-03) | 3 Task: NOT_STARTED 3 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Quản lý node kỹ năng và cạnh của một lộ trình: xem cấu trúc, thêm, sửa, xóa node và cạnh, xóa node kèm cạnh trong một transaction (`docs/modules/learning-path-graph.md` §1).

## 3. Phạm vi

Theo `docs/modules/learning-path-graph.md` §1 ("Thuộc module", "Không thuộc module"). Tóm tắt: `/api/learning-paths/{path_id}/nodes*`, `/edges*`; màn PathDetail, PathEdit.

## 4. Mức độ có căn cứ

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `READY_FOR_IMPLEMENTATION` | BA FR-10, FR-11, BR-08, BR-10, §10.6, §10.7 |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | BA AC-03; SRS-PATH-08 — các mã này chưa có trong `docs/modules/learning-path-graph.md`. Câu hỏi cho Hòa (D-OWN-02): AC-03, SRS-PATH-08 có phải tiêu chí nghiệm thu chính thức của F06 để đưa vào đặc tả không? Việc tài liệu kiểm thử (riêng): chưa có `docs/modules/learning-path-graph.tests.md`, cần tạo |
| UI | `READY_WITH_LIMITATIONS` | PathDetail, PathEdit (route ND-50) |
| API | `NEEDS_OWNER_INPUT` | Endpoint có; response, mã lỗi, quyền chưa ghi. Câu hỏi cho Hòa (D-OWN-02): response, mã lỗi và quyền truy cập của các endpoint F06 là gì, để ghi vào `docs/modules/learning-path-graph.md`? |
| Database | `READY_FOR_IMPLEMENTATION` | §4.5, §4.6 |
| Kiểm thử | `NEEDS_OWNER_INPUT` | Chưa có test case. Câu hỏi cho Hòa (D-OWN-02): danh sách kịch bản kiểm thử của F06 là gì, dựa trên tiêu chí nghiệm thu nào? Chưa có `docs/modules/learning-path-graph.tests.md` |
| Phụ thuộc | `NOT_READY_BLOCKED` | P07-T04 chờ P01-T05 |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú.

## 5. Phase và Task

| Phase | File | Task quản lý tại thư mục này |
|---|---|---|
| P07 | [phase-07-roadmap-consultant-recommendations.md](phase-07-roadmap-consultant-recommendations.md) | P07-T07, P07-T14, P07-T15 |

Task dùng chung quản lý ở tính năng khác: P07-T01 (F05), P07-T02 (F05), P07-T03 (F05), P07-T04 (F05), P07-T10 (F05), P07-T11 (F05).

Các Phase khác của khung chung (P00–P03, P13) là phần dùng chung, quản lý tại [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

Lấy từ cột Dependencies của các Task (không thêm phụ thuộc mới):

| Task | Phụ thuộc | Thuộc |
|---|---|---|
| P07-T07 | P07-T04 | F05 |
| P07-T14 | P07-T11 | F05 |

Quyết định còn chờ ảnh hưởng tính năng: ND-54, ND-50, ND-24.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Xác nhận đặc tả `docs/modules/learning-path-graph.md`.
2. Ghi có kiểm vòng tiên quyết cho cạnh trong một lộ trình không (BA BR-08).
3. Bổ sung response, mã lỗi, quyền cho EP-034 … EP-042.
4. Soạn kịch bản kiểm thử (gồm xóa node kèm cạnh).

## 8. Điều kiện hoàn thành và bằng chứng

- Mọi Task bắt buộc của tính năng DONE, có Evidence và kết quả review (`plans/plan.md` PART 2 quy tắc 5, 6). Tạo file kế hoạch **không** phải DONE.
- Đặc tả `docs/modules/learning-path-graph.md` được người phụ trách xác nhận (DRAFT → SPEC CONFIRMED) trước khi code phần phụ thuộc đặc tả.
- Bằng chứng cần có: kết quả `pytest` (xóa node kèm cạnh), ảnh PathDetail, PathEdit.
- Task BLOCKED ghi rõ mã chặn; phần không phụ thuộc vẫn được làm.

## 9. Tài liệu nguồn

BA §6.2 (FR-10, FR-11), §8.3, BR-08, BR-10, §10.6, §10.7, UC-05; SRS §6.5 (SRS-PATH-08); `docs/api-endpoints.md` §6, §7; `docs/database-design.md` §4.5, §4.6; `docs/modules/learning-path-graph.md`.
