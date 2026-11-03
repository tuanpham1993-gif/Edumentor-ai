# F07 — Gợi ý khóa học cho một kỹ năng cụ thể

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở file `phase-NN-*.md` của thư mục này. Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F07 — Gợi ý khóa học cho một kỹ năng cụ thể |
| Người phụ trách | **Tâm** (D-OWN-02, `docs/decisions.md` §2). Workbook V2 ghi Hòa — workbook không phải nguồn quyết định; chỉ giữ để truy vết |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/skill-course-recommendation.md`](../../docs/modules/skill-course-recommendation.md) — DRAFT, chưa được người phụ trách xác nhận |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (2026-11-03) | 2 Task: NOT_STARTED 2 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Khi người dùng chọn một node kỹ năng, truy xuất và xếp hạng khóa học liên quan, trả liên kết khóa ngoài (`docs/modules/skill-course-recommendation.md` §1).

## 3. Phạm vi

Theo `docs/modules/skill-course-recommendation.md` §1 ("Thuộc module", "Không thuộc module"). Tóm tắt: `GET /api/learning-paths/{path_id}/nodes/{skill_id}/courses`; panel gợi ý trên PathDetail; xếp hạng ở P12-T05.

## 4. Mức độ có căn cứ

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `READY_FOR_IMPLEMENTATION` | BA FR-12 … FR-14, BR-12 … BR-16, §8.4 |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | BA AC-04; SRS-REC-01 … 03 — các mã này chưa có trong `docs/modules/skill-course-recommendation.md`. Câu hỏi cho Tâm (D-OWN-02): AC-04, SRS-REC-01 … 03 có phải tiêu chí nghiệm thu chính thức của F07 để đưa vào đặc tả không? Việc tài liệu kiểm thử (riêng): chưa có `docs/modules/skill-course-recommendation.tests.md`, cần tạo |
| UI | `READY_FOR_IMPLEMENTATION` | PathDetail (panel gợi ý) |
| API | `NEEDS_OWNER_INPUT` | Endpoint có; response, quyền chưa ghi. Câu hỏi cho Tâm (D-OWN-02): response và quyền truy cập của các endpoint F07 là gì, để ghi vào `docs/modules/skill-course-recommendation.md`? |
| Database | `READY_FOR_IMPLEMENTATION` | §2, §4.5 |
| Kiểm thử | `NEEDS_OWNER_INPUT` | Chưa có test case. Câu hỏi cho Tâm (D-OWN-02): danh sách kịch bản kiểm thử của F07 là gì, dựa trên tiêu chí nghiệm thu nào? Chưa có `docs/modules/skill-course-recommendation.tests.md` |
| Phụ thuộc | `NOT_READY_BLOCKED` | P07-T04 chờ P01-T05; nơi cấu hình trọng số chưa ghi |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú.

## 5. Phase và Task

| Phase | File | Task quản lý tại thư mục này |
|---|---|---|
| P07 | [phase-07-roadmap-consultant-recommendations.md](phase-07-roadmap-consultant-recommendations.md) | P07-T08 |
| P12 | [phase-12-ai-ml.md](phase-12-ai-ml.md) | P12-T05 |

Task dùng chung quản lý ở tính năng khác: P07-T01 (F05), P07-T02 (F05), P07-T03 (F05), P07-T04 (F05), P07-T10 (F05), P07-T11 (F05), P07-T14 (F06).

Các Phase khác của khung chung (P00–P03, P13) là phần dùng chung, quản lý tại [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

Lấy từ cột Dependencies của các Task (không thêm phụ thuộc mới):

| Task | Phụ thuộc | Thuộc |
|---|---|---|
| P07-T08 | P07-T04 | F05 |
| P07-T08 | P02-T03 | dùng chung |

Quyết định còn chờ ảnh hưởng tính năng: ND-61 (dùng ở P12-T05).

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Xác nhận đặc tả `docs/modules/skill-course-recommendation.md`.
2. Thống nhất phạm vi trùng với F04 (EP-043; workbook CK-02).
3. Ghi nơi cấu hình trọng số 0.7 / 0.3 (BA §8.4.3) và cách tính `level_fit`, `skill_match`.
4. Bổ sung response, quyền cho EP-043.
5. Soạn kịch bản kiểm thử.
6. Đã xử lý: người phụ trách (Tâm) được ghi ở D-OWN-02 (`docs/decisions.md` §2); `docs/modules/README.md` và `README.md` đã đồng bộ (commit `2133863`). Workbook V2 ghi Hòa — workbook không phải nguồn quyết định; chỉ giữ để truy vết.

## 8. Điều kiện hoàn thành và bằng chứng

- Mọi Task bắt buộc của tính năng DONE, có Evidence và kết quả review (`plans/plan.md` PART 2 quy tắc 5, 6). Tạo file kế hoạch **không** phải DONE.
- Đặc tả `docs/modules/skill-course-recommendation.md` được người phụ trách xác nhận (DRAFT → SPEC CONFIRMED) trước khi code phần phụ thuộc đặc tả.
- Bằng chứng cần có: kết quả `pytest` gợi ý, ảnh panel gợi ý, báo cáo đánh giá xếp hạng (P12-T08).
- Task BLOCKED ghi rõ mã chặn; phần không phụ thuộc vẫn được làm.

## 9. Tài liệu nguồn

BA §6.3 (FR-12 … FR-14), §8.4, §9.3, §10.8, UC-06, AC-04; SRS §6.6 (SRS-REC-01 … 03); `docs/api-endpoints.md` §8, §14; `docs/structure.md` §5; `docs/modules/skill-course-recommendation.md`.
