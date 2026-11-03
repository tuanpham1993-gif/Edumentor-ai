# F13 — Quản trị — quản lý phản hồi

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở file `phase-NN-*.md` của thư mục này. Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F13 — Quản trị — quản lý phản hồi |
| Người phụ trách | **Hòa** (D-OWN-02, `docs/decisions.md` §2). Workbook V2 ghi Tâm — workbook không phải nguồn quyết định; chỉ giữ để truy vết |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/admin-feedback.md`](../../docs/modules/admin-feedback.md) — DRAFT, căn cứ BA rất ít |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (2026-11-03) | 1 Task: NOT_STARTED 1 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Admin xem, lọc, sắp xếp phản hồi và xem chi tiết một phản hồi (`docs/modules/admin-feedback.md` §1). Endpoint chưa có (ND-55, M2).

## 3. Phạm vi

Theo `docs/modules/admin-feedback.md` §1 ("Thuộc module", "Không thuộc module"). Tóm tắt: Màn AdminFeedback, AdminFeedback-Detail; backend dùng chung P10-T06 (quản lý ở F10).

## 4. Mức độ có căn cứ

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `NEEDS_OWNER_INPUT` | BA chỉ có §4.1.2 (Admin trả lời phản hồi). Câu hỏi cho Hòa (D-OWN-02): phần xem, lọc phản hồi của F13 lấy căn cứ nghiệp vụ nào ngoài BA §4.1.2? Cách admin trả lời là ND-35 — quyết định đang chờ riêng, không thuộc câu hỏi này |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | Chưa có; BA không có AC cho quản trị phản hồi. Câu hỏi cho Hòa (D-OWN-02): tiêu chí nghiệm thu của F13 là gì, để đưa vào `docs/modules/admin-feedback.md`? |
| UI | `READY_WITH_LIMITATIONS` | AdminFeedback, AdminFeedback-Detail dựng được với trạng thái "chưa khả dụng" (D-FE-08); giới hạn: chưa có endpoint xem, lọc phản hồi (ND-55, M2); cách admin trả lời phản hồi chưa chốt (ND-35) |
| API | `NOT_READY_BLOCKED` | ND-55 (M2), ND-35 |
| Database | `READY_WITH_LIMITATIONS` | Bảng `Feedback` (§7) hiện có dùng được cho phần xem phản hồi; giới hạn: không có cột trạng thái, câu trả lời — lưu câu trả lời của admin phụ thuộc ND-35 (CSDL chưa có cột/bảng; không tự thiết kế thêm) |
| Kiểm thử | `NEEDS_OWNER_INPUT` | Chưa có. Câu hỏi cho Hòa (D-OWN-02): danh sách kịch bản kiểm thử của F13 là gì, dựa trên tiêu chí nghiệm thu nào? Chưa có `docs/modules/admin-feedback.tests.md` |
| Phụ thuộc | `NOT_READY_BLOCKED` | ND-35, ND-55, ND-69 |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú.

## 5. Phase và Task

| Phase | File | Task quản lý tại thư mục này |
|---|---|---|
| P10 | [phase-10-feedback.md](phase-10-feedback.md) | P10-T05 |

Task dùng chung quản lý ở tính năng khác: P10-T01 (F10), P10-T02 (F10), P10-T06 (F10).

Các Phase khác của khung chung (P00–P03, P13) là phần dùng chung, quản lý tại [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

Lấy từ cột Dependencies của các Task (không thêm phụ thuộc mới):

| Task | Phụ thuộc | Thuộc |
|---|---|---|
| P10-T05 | P03-T04 | dùng chung |

Quyết định còn chờ ảnh hưởng tính năng: ND-35, ND-55, ND-69, D11, ND-81.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Đề xuất endpoint Admin xem, lọc phản hồi cho ND-55 (tham khảo đề xuất workbook EP-074, EP-101, chưa duyệt).
2. Làm rõ cách Admin trả lời (ND-35): trong hệ thống hay qua email ngoài.
3. Xác nhận đặc tả `docs/modules/admin-feedback.md` sau khi ND được chốt.
4. Soạn tiêu chí nghiệm thu và kịch bản kiểm thử.
5. Đã xử lý: người phụ trách (Hòa) được ghi ở D-OWN-02 (`docs/decisions.md` §2); `docs/modules/README.md` và `README.md` đã đồng bộ (commit `2133863`). Workbook V2 ghi Tâm — workbook không phải nguồn quyết định; chỉ giữ để truy vết. Quan hệ giữa D-OWN-02 và dòng "Feedback & liên hệ (T22–T25)" ở `docs/decisions.md` §2 (ND-35) vẫn chờ Tuấn xác nhận.

## 8. Điều kiện hoàn thành và bằng chứng

- Mọi Task bắt buộc của tính năng DONE, có Evidence và kết quả review (`plans/plan.md` PART 2 quy tắc 5, 6). Tạo file kế hoạch **không** phải DONE.
- Đặc tả `docs/modules/admin-feedback.md` được người phụ trách xác nhận (DRAFT → SPEC CONFIRMED) trước khi code phần phụ thuộc đặc tả.
- Bằng chứng cần có: ảnh AdminFeedback ở trạng thái "chưa khả dụng"; khi có M2: kết quả `pytest`.
- Task BLOCKED ghi rõ mã chặn; phần không phụ thuộc vẫn được làm.

## 9. Tài liệu nguồn

BA §4.1.2; SRS §6.14 (SRS-ADMF-01 … 03); `docs/database-design.md` §7; `docs/decisions.md` ND-35, ND-55, ND-69; `docs/modules/admin-feedback.md`.
