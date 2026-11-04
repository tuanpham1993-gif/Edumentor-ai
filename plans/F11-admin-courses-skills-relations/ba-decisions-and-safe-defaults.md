# F11 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Quản lý kỹ năng | FR-30; UC-11 | SRS-ADMS-01, 02 | S-29 |
| Quản lý khóa học | FR-32; UC-13 | SRS-ADMC-01 … 03 | S-28 |
| Liên kết khóa học–kỹ năng | FR-33; UC-13 | SRS-ADMC-04 | S-28 |
| Chỉ Admin, kiểm quyền ở server | FR-40; BR-32, BR-34 | SRS §4.2 | — |

Chi tiết yêu cầu (mã `AD-YCnn`) và chỗ BA khác quyết định: `docs/modules/admin-course-skill.md` §1 "Yêu cầu".

## B. Quyết định đã chốt

| Mã | Nội dung |
|---|---|
| D-FE-06 | `AdminRoute` chỉ ẩn giao diện; backend kiểm quyền |

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung |
|---|---|
| ND-71 | Xóa kỹ năng: xóa mềm hay chặn xóa |
| ND-57 | Học viên chọn kỹ năng từ đâu |
| ND-52 | User thường vào `/admin/*` |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

Người phụ trách (Hòa) bổ sung tài liệu hoặc đề xuất ND qua người có thẩm quyền:

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Phản hồi khi xóa bị chặn bởi RESTRICT | API, test |
| 2 | Request, response, mã lỗi của 12 endpoint | API |
| 3 | Người làm EP-063 … EP-066 và màn AdminSkills | Phân công |

### C3. Mặc định an toàn có trong nguồn

Nguồn không ghi mặc định an toàn nào cho tính năng này. Không tự đặt mặc định.
