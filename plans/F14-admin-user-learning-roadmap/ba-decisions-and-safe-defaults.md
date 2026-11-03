# F14 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Admin xem lộ trình người dùng (chỉ đọc) | Không có (BA §4.3 giới hạn) | SRS-ADMU-01 … 03 (bổ sung theo UI) | S-33 |
| Tìm người dùng, xem theo mục tiêu | Không có | SRS-ADMU-02, 04 | S-33 |

Chi tiết yêu cầu (mã `AU-YCnn`) và chỗ BA khác quyết định: `docs/modules/admin-user-paths.md` §1 "Yêu cầu".

## B. Quyết định đã chốt

| Mã | Nội dung |
|---|---|
| D-FE-08 | Màn chưa có endpoint hiển thị "chưa khả dụng" |

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung |
|---|---|
| ND-79 | Có giữ chức năng; quyền, ghi log |
| ND-55 (M3) | Endpoint danh sách người dùng, lộ trình người dùng |
| ND-54 | Tên lộ trình |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

Người phụ trách (Hòa) bổ sung tài liệu hoặc đề xuất ND qua người có thẩm quyền:

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Người phụ trách màn AdminUserPaths, EP-100 (workbook ghi "Hòa, Tuấn") | Phân công |

### C3. Mặc định an toàn có trong nguồn

| Mặc định | Nguồn | Điều kiện dùng |
|---|---|---|
| Màn dựng giao diện, hiển thị "chưa khả dụng" | D-FE-08 | Tới khi có endpoint M3 |
