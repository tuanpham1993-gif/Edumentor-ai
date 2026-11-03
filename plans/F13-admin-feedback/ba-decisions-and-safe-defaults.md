# F13 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Admin trả lời, quản lý feedback | §4.1.2 | SRS-ADMF-03 (bổ sung theo UI) | S-32 |
| Xem, lọc, sắp xếp phản hồi | Không có | SRS-ADMF-01, 02 | S-32 |

Chi tiết yêu cầu (mã `AF-YCnn`) và chỗ BA khác quyết định: `docs/modules/admin-feedback.md` §1 "Yêu cầu".

## B. Quyết định đã chốt

| Mã | Nội dung |
|---|---|
| D11 | Danh sách "Loại phản hồi": phương án A — phạm vi chờ ND-69 |
| D-FE-08 | Màn chưa có endpoint hiển thị "chưa khả dụng" |

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung |
|---|---|
| ND-35 | Cách Admin trả lời phản hồi |
| ND-55 (M2) | Endpoint Admin xem, lọc phản hồi |
| ND-69 | `feedback_type` và bộ lọc loại |
| ND-81 | Update feedback (đề bài) |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

Người phụ trách (Hòa) bổ sung tài liệu hoặc đề xuất ND qua người có thẩm quyền:

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Bộ lọc, phân trang của danh sách phản hồi | API |
| 2 | Đã xử lý: người phụ trách là Hòa theo D-OWN-02 (`docs/decisions.md` §2); workbook V2 ghi Tâm — chỉ để truy vết, workbook không phải nguồn quyết định. Phần còn mở (quan hệ giữa D-OWN-02 và dòng "Feedback & liên hệ (T22–T25)" ở `docs/decisions.md` §2) thuộc ND-35 — quyết định đang chờ riêng, theo dõi ở P00-T07 | Phân công |

### C3. Mặc định an toàn có trong nguồn

| Mặc định | Nguồn | Điều kiện dùng |
|---|---|---|
| Màn dựng giao diện, hiển thị "chưa khả dụng" | D-FE-08 | Tới khi có endpoint M2 |
