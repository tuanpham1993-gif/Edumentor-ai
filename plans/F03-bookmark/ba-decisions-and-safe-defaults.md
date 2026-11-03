# F03 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Lưu khóa học | FR-17; §10.4 | SRS-TRK-01 | S-12, S-13 |
| Xem danh sách đã lưu | FR-17; §10.4 | SRS-TRK-01 | S-15 |
| Bỏ lưu | §10.4 | SRS-TRK-01 | S-12, S-13, S-15 |

Chi tiết yêu cầu (mã `BM-YCnn`) và chỗ BA khác quyết định: `docs/modules/course-bookmark.md` §1 "Yêu cầu".

## B. Quyết định đã chốt

Không có quyết định D/T riêng cho tính năng; áp dụng quyết định chung (D-DOC-01, D-FE-01 … D-FE-12).

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung |
|---|---|
| ND-80 | Giữ một hay cả hai cách lấy danh sách đã lưu |
| ND-32 | Bảng Bookmark riêng hay dùng `StudentCourse` |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

Người phụ trách (Tâm) bổ sung tài liệu hoặc đề xuất ND qua người có thẩm quyền:

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Response, mã lỗi khi khóa không tồn tại hoặc đã có dòng `StudentCourse` | API, test |
| 2 | Người làm EP-020 … EP-022 | Phân công |

### C3. Mặc định an toàn có trong nguồn

Nguồn không ghi mặc định an toàn nào cho tính năng này. Không tự đặt mặc định.
