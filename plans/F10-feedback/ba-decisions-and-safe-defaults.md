# F10 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Gửi phản hồi khóa học hoặc hệ thống | Không có | SRS-FB-01, 02 (bổ sung theo UI) | S-26 |
| Xem liên hệ khóa học | Không có | SRS-FB-03 | S-26, S-27 |
| Khách không gửi được | Không có | SRS-FB-04 | S-27 |

Chi tiết yêu cầu (mã `FB-YCnn`) và chỗ BA khác quyết định: `docs/modules/feedback.md` §1 "Yêu cầu".

## B. Quyết định đã chốt

| Mã | Nội dung |
|---|---|
| D11 | Danh sách "Loại phản hồi": phương án A (ghi "không làm") — phạm vi chính xác chờ ND-69 |
| D-FE-08 | Màn chưa có endpoint vẫn dựng, hiển thị "chưa khả dụng"; không tạo API giả |

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung |
|---|---|
| ND-35 | Phạm vi phản hồi, trả lời của Admin; T22–T25 ☐ |
| ND-55 (M2) | Endpoint gửi phản hồi, liên hệ khóa học |
| ND-69 | `feedback_type` |
| ND-50 | Route `/contact-guest` |
| ND-77, ND-81 | Update feedback (đề bài) |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

Người phụ trách (Khôi) bổ sung tài liệu hoặc đề xuất ND qua người có thẩm quyền:

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Yêu cầu nghiệp vụ trong BA | Toàn tính năng |
| 2 | Giới hạn độ dài nội dung; quyền của khách xem liên hệ | API, UI |
| 3 | Đã xử lý: người phụ trách là Khôi theo D-OWN-02 (`docs/decisions.md` §2). Phần còn mở (quan hệ giữa D-OWN-02 và dòng "Feedback & liên hệ (T22–T25)" ở `docs/decisions.md` §2) thuộc ND-35 — quyết định đang chờ riêng, theo dõi ở P00-T07 | Phân công |

### C3. Mặc định an toàn có trong nguồn

| Mặc định | Nguồn | Điều kiện dùng |
|---|---|---|
| Màn dựng giao diện, hiển thị "chưa khả dụng" | D-FE-08 | Tới khi có endpoint M2 |
