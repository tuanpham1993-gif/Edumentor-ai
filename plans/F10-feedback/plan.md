# F10 — Phản hồi (Feedback)

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở file `phase-NN-*.md` của thư mục này. Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F10 — Phản hồi (Feedback) |
| Người phụ trách | **Khôi** (D-OWN-02, `docs/decisions.md` §2). Workbook V2 ghi Tâm — workbook không phải nguồn quyết định; chỉ giữ để truy vết |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/feedback.md`](../../docs/modules/feedback.md) — DRAFT, chưa có căn cứ BA |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (2026-11-03) | 5 Task: BLOCKED 1 · NOT_STARTED 4 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Người dùng đăng nhập gửi phản hồi về khóa học hoặc hệ thống và xem thông tin liên hệ của khóa (`docs/modules/feedback.md` §1). Endpoint chưa có (ND-55, M2).

## 3. Phạm vi

Theo `docs/modules/feedback.md` §1 ("Thuộc module", "Không thuộc module"). Tóm tắt: Màn Contact, ContactGuest; backend phản hồi M2 (P10-T06, BLOCKED).

## 4. Mức độ có căn cứ

| Phần | Tình trạng | Ghi chú |
|---|---|---|
| Yêu cầu nghiệp vụ | `NOT_READY_BLOCKED` | BA không có FR; SRS-FB-01 … 04 ghi "bổ sung theo UI, chờ BA". Chặn bởi quyết định đang chờ: mục Feedback & liên hệ T22–T25 ☐ (mục quyết định ở `docs/decisions.md` §3, không phải Task) và ND-35. Câu hỏi riêng cho Khôi (D-OWN-02), không thay các quyết định trên: có đề nghị bổ sung BA theo SRS-FB-01 … 04 không? |
| Tiêu chí nghiệm thu | `NEEDS_OWNER_INPUT` | Chưa có; BA không có AC cho phản hồi. Câu hỏi cho Khôi (D-OWN-02): tiêu chí nghiệm thu của F10 là gì, để đưa vào `docs/modules/feedback.md`? |
| UI | `READY_WITH_LIMITATIONS` | Contact, ContactGuest; hiển thị "chưa khả dụng" (D-FE-08); ô loại phản hồi ND-69 |
| API | `NOT_READY_BLOCKED` | ND-35, ND-55 (M2), ND-69; T22–T25 ☐ |
| Database | `READY_WITH_LIMITATIONS` | `Feedback`, `CourseContact` §7; `feedback_type` NN mâu thuẫn D11 (ND-69) |
| Kiểm thử | `NEEDS_OWNER_INPUT` | Chưa có. Câu hỏi cho Khôi (D-OWN-02): danh sách kịch bản kiểm thử của F10 là gì, dựa trên tiêu chí nghiệm thu nào? Chưa có `docs/modules/feedback.tests.md` |
| Phụ thuộc | `NOT_READY_BLOCKED` | ND-35, ND-55, ND-69 |

Ký hiệu (mức sẵn sàng triển khai, D-DOC-07): `READY_FOR_IMPLEMENTATION` — nguồn đủ để bắt đầu, không ND/T chưa chốt liên quan (không có nghĩa đặc tả đã xác nhận); `READY_WITH_LIMITATIONS` — làm được phần đã đủ căn cứ, giới hạn ghi ở cột Ghi chú; `NOT_READY_BLOCKED` — chưa làm được phần nào, ND hoặc Task chặn ghi ở cột Ghi chú (khác trạng thái Task `BLOCKED`); `NEEDS_OWNER_INPUT` — cần người phụ trách bổ sung hoặc xác nhận tài liệu; câu hỏi ghi ở cột Ghi chú.

## 5. Phase và Task

| Phase | File | Task quản lý tại thư mục này |
|---|---|---|
| P10 | [phase-10-feedback.md](phase-10-feedback.md) | P10-T01, P10-T02, P10-T03, P10-T04, P10-T06 |

Các Phase khác của khung chung (P00–P03, P13) là phần dùng chung, quản lý tại [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

Lấy từ cột Dependencies của các Task (không thêm phụ thuộc mới):

| Task | Phụ thuộc | Thuộc |
|---|---|---|
| P10-T03 | P03-T04 | dùng chung |
| P10-T03 | P03-T05 | dùng chung |
| P10-T06 | P04-T03 | F01 |

Quyết định còn chờ ảnh hưởng tính năng: ND-35, ND-55, ND-69, D11, ND-50, ND-77, ND-81.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Bổ sung yêu cầu nghiệp vụ vào BA qua người có thẩm quyền (BA chưa có FR cho phản hồi).
2. Đề xuất endpoint M2 (gửi phản hồi, liên hệ khóa học) cho ND-55; đầu vào tham khảo: đề xuất trong workbook EP-057, EP-099, EP-102 (chưa duyệt).
3. Đề xuất phương án cho ND-69 (`feedback_type`) và ND-35.
4. Xác nhận đặc tả `docs/modules/feedback.md` sau khi ND được chốt.
5. Soạn tiêu chí nghiệm thu và kịch bản kiểm thử.
6. Đã xử lý: người phụ trách (Khôi) được ghi ở D-OWN-02 (`docs/decisions.md` §2); `docs/modules/README.md` và `README.md` đã đồng bộ (commit `2133863`). Workbook V2 ghi Tâm — workbook không phải nguồn quyết định; chỉ giữ để truy vết. Quan hệ giữa D-OWN-02 và dòng "Feedback & liên hệ (T22–T25)" ở `docs/decisions.md` §2 (ND-35) vẫn chờ Tuấn xác nhận.

## 8. Điều kiện hoàn thành và bằng chứng

- Mọi Task bắt buộc của tính năng DONE, có Evidence và kết quả review (`plans/plan.md` PART 2 quy tắc 5, 6). Tạo file kế hoạch **không** phải DONE.
- Đặc tả `docs/modules/feedback.md` được người phụ trách xác nhận (DRAFT → SPEC CONFIRMED) trước khi code phần phụ thuộc đặc tả.
- Bằng chứng cần có: ảnh Contact, ContactGuest ở trạng thái "chưa khả dụng"; khi có M2: kết quả `pytest`.
- Task BLOCKED ghi rõ mã chặn; phần không phụ thuộc vẫn được làm.

## 9. Tài liệu nguồn

BA §4.1.2 (chỉ phần Admin); SRS §6.9 (SRS-FB-01 … 04); `docs/database-design.md` §7; `docs/decisions.md` D11, ND-35, ND-55, ND-69; `docs/modules/feedback.md`.
