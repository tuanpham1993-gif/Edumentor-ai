# F06 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Xem cấu trúc lộ trình | FR-10; UC-05 | SRS-PATH-07 | S-18 |
| Khám phá kỹ năng tự do | FR-11; BR-10 | SRS-PATH-07 | S-18 |
| Thêm, sửa, xóa node và cạnh | §10.6, §10.7 | SRS-PATH-08 | S-18, S-19 |
| Cấu trúc hợp lệ | BR-08 | SRS-PATH-08 | — |

Chi tiết yêu cầu (mã `LG-YCnn`) và chỗ BA khác quyết định: `docs/modules/learning-path-graph.md` §1 "Yêu cầu".

## B. Quyết định đã chốt

Không có quyết định D/T riêng cho tính năng; áp dụng quyết định chung (D-DOC-01, D-FE-01 … D-FE-12).

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung |
|---|---|
| ND-54 | Dữ liệu UI chưa có |
| ND-50 | Route `/learning-paths/:pathId/edit` |
| ND-24 | Dùng `is_required` khi cập nhật lộ trình sau ôn tập |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

Người phụ trách (Hòa) bổ sung tài liệu hoặc đề xuất ND qua người có thẩm quyền:

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Kiểm vòng tiên quyết cho cạnh trong lộ trình | API, test |
| 2 | Quyền, response, mã lỗi của 9 endpoint | API |

### C3. Mặc định an toàn có trong nguồn

Nguồn không ghi mặc định an toàn nào cho tính năng này. Không tự đặt mặc định.
