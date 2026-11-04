# F05 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Nhận mục tiêu | FR-05; UC-03 | SRS-PATH-01 | S-16 |
| Phân tích mục tiêu, đối chiếu kỹ năng | FR-06; BR-01, BR-02 | SRS-PATH-02 | S-16 |
| Hỏi lại, báo ngoài phạm vi | FR-07; BR-04 | SRS-PATH-03, 04 | S-16 (chưa có trạng thái — ND-74) |
| Tạo lộ trình | FR-08; BR-05 … BR-09 | SRS-PATH-02 | S-16 |
| Lưu lộ trình | FR-09; FR-36 | SRS-PATH-05 | S-16 |
| Xem danh sách, chi tiết | FR-10; UC-05 | SRS-PATH-06, 07 | S-17, S-18 |

Chi tiết yêu cầu (mã `LP-YCnn`) và chỗ BA khác quyết định: `docs/modules/learning-path-consultant.md` §1 "Yêu cầu".

## B. Quyết định đã chốt

Không có quyết định D/T riêng cho tính năng; áp dụng quyết định chung (D-DOC-01, D-FE-01 … D-FE-12).

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung |
|---|---|
| ND-74 | Hợp đồng `POST /api/chat/learning-path` |
| ND-60 | Lộ trình 3–5 môn (đề bài) — giữ đồ thị kỹ năng (ND-81) |
| ND-54 | Tên lộ trình |
| ND-24 | Cập nhật lộ trình sau ôn tập (T18 ☐) |
| ND-77, ND-81 | Đề bài khác hiện hành |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

Người phụ trách (Hòa) bổ sung tài liệu hoặc đề xuất ND qua người có thẩm quyền:

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Thời điểm lưu lộ trình | API, DB |
| 2 | Có lưu hội thoại tư vấn không | DB |
| 3 | Quyền của EP-028, EP-030 … EP-033 | API |
| 4 | Người làm T18 (`decisions.md` §2 ghi Tâm) | Phân công |

### C3. Mặc định an toàn có trong nguồn

| Mặc định | Nguồn | Điều kiện dùng |
|---|---|---|
| Frontend tạm bỏ dữ liệu demo chưa có trong API (tên lộ trình) | ND-54 | Tới khi ND-54 chốt |
