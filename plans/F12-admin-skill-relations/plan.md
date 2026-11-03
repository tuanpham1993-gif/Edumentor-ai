# F12 — Quản trị — các mối liên hệ giữa các kỹ năng

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở file `phase-NN-*.md` của thư mục này. Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F12 — Quản trị — các mối liên hệ giữa các kỹ năng |
| Người phụ trách | **Tâm** (D-OWN-02, `docs/decisions.md` §2). Workbook V2 ghi Hòa — workbook không phải nguồn quyết định; chỉ giữ để truy vết |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/admin-skill-relation.md`](../../docs/modules/admin-skill-relation.md) — DRAFT, chưa được người phụ trách xác nhận |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (2026-11-03) | 2 Task: NOT_STARTED 2 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Admin quản lý quan hệ dùng chung giữa kỹ năng (tiên quyết, mở rộng, liên quan) (`docs/modules/admin-skill-relation.md` §1).

## 3. Phạm vi

Theo `docs/modules/admin-skill-relation.md` §1 ("Thuộc module", "Không thuộc module"). Tóm tắt: `/api/admin/skill-relations*` (4 endpoint); hộp thoại sơ đồ quan hệ trên AdminSkills.

## 4. Mức độ có căn cứ

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `READY_FOR_IMPLEMENTATION` | BA FR-31, BR-06 … BR-08, BR-33 |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | BA AC-08; SRS-ADMS-03 — các mã này chưa có trong `docs/modules/admin-skill-relation.md`. Câu hỏi cho Tâm (D-OWN-02): AC-08, SRS-ADMS-03 có phải tiêu chí nghiệm thu chính thức của F12 để đưa vào đặc tả không? Việc tài liệu kiểm thử (riêng): chưa có `docs/modules/admin-skill-relation.tests.md`, cần tạo |
| UI | `READY_FOR_IMPLEMENTATION` | AdminSkills-Relations |
| API | `NEEDS_OWNER_INPUT` | Endpoint có; mã lỗi khi tạo vòng chưa định nghĩa. Câu hỏi cho Tâm (D-OWN-02): mã lỗi khi tạo quan hệ gây vòng của các endpoint F12 là gì, để ghi vào `docs/modules/admin-skill-relation.md`? |
| Database | `READY_FOR_IMPLEMENTATION` | `SkillRelation` §2.4 |
| Kiểm thử | `NEEDS_OWNER_INPUT` | Chưa có test case. Câu hỏi cho Tâm (D-OWN-02): danh sách kịch bản kiểm thử của F12 là gì, dựa trên tiêu chí nghiệm thu nào? Chưa có `docs/modules/admin-skill-relation.tests.md` |
| Phụ thuộc | `NOT_READY_BLOCKED` | P02-T04 chờ P01-T05; `require_admin` chờ ND-44 |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú.

## 5. Phase và Task

| Phase | File | Task quản lý tại thư mục này |
|---|---|---|
| P07 | [phase-07-roadmap-consultant-recommendations.md](phase-07-roadmap-consultant-recommendations.md) | P07-T09, P07-T16 |

Task dùng chung quản lý ở tính năng khác: P07-T01 (F05), P07-T02 (F05), P07-T03 (F05), P07-T10 (F05).

Các Phase khác của khung chung (P00–P03, P13) là phần dùng chung, quản lý tại [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

Lấy từ cột Dependencies của các Task (không thêm phụ thuộc mới):

| Task | Phụ thuộc | Thuộc |
|---|---|---|
| P07-T09 | P02-T04 | dùng chung |
| P07-T09 | P04-T03 | F01 |
| P07-T16 | P05-T14 | F11 |

Quyết định còn chờ ảnh hưởng tính năng: ND-71.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Xác nhận đặc tả `docs/modules/admin-skill-relation.md`.
2. Bổ sung mã lỗi khi tạo vòng tiên quyết hoặc trùng quan hệ.
3. Soạn kịch bản kiểm thử (kiểm vòng tiên quyết).
4. Đã xử lý: người phụ trách (Tâm) được ghi ở D-OWN-02 (`docs/decisions.md` §2); `docs/modules/README.md` và `README.md` đã đồng bộ (commit `2133863`). Workbook V2 ghi Hòa — workbook không phải nguồn quyết định; chỉ giữ để truy vết.

## 8. Điều kiện hoàn thành và bằng chứng

- Mọi Task bắt buộc của tính năng DONE, có Evidence và kết quả review (`plans/plan.md` PART 2 quy tắc 5, 6). Tạo file kế hoạch **không** phải DONE.
- Đặc tả `docs/modules/admin-skill-relation.md` được người phụ trách xác nhận (DRAFT → SPEC CONFIRMED) trước khi code phần phụ thuộc đặc tả.
- Bằng chứng cần có: kết quả `pytest` kiểm vòng, ảnh hộp thoại quan hệ.
- Task BLOCKED ghi rõ mã chặn; phần không phụ thuộc vẫn được làm.

## 9. Tài liệu nguồn

BA §6.7 (FR-31), §9.2 (BR-06 … BR-08), §10.11, UC-12, AC-08; SRS §6.11 (SRS-ADMS-03); `docs/api-endpoints.md` §11; `docs/database-design.md` §2.4; `docs/modules/admin-skill-relation.md`.
