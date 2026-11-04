# F12 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Quản lý quan hệ kỹ năng | FR-31; UC-12 | SRS-ADMS-03 | S-29 |
| Phân biệt tiên quyết với quan hệ khác | BR-06, BR-07 | SRS-ADMS-03 | S-29 |
| Phát hiện vòng tiên quyết | BR-08 | — | — |

Chi tiết yêu cầu (mã `SR-YCnn`) và chỗ BA khác quyết định: `docs/modules/admin-skill-relation.md` §1 "Yêu cầu".

## B. Quyết định đã chốt

Không có quyết định D/T riêng cho tính năng; áp dụng quyết định chung (D-DOC-01, D-FE-01 … D-FE-12).

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung |
|---|---|
| ND-71 | Xóa kỹ năng đang có quan hệ |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

Người phụ trách (Tâm) bổ sung tài liệu hoặc đề xuất ND qua người có thẩm quyền:

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Mã lỗi khi tạo vòng, khi trùng quan hệ | API, test |
| 2 | Tên service cho nhóm endpoint | Cấu trúc code (`structure.md` §2) |

### C3. Mặc định an toàn có trong nguồn

Nguồn không ghi mặc định an toàn nào cho tính năng này. Không tự đặt mặc định.
