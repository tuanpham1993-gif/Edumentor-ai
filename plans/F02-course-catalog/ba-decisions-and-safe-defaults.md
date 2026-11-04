# F02 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Hiển thị thông tin khóa học | FR-15 | SRS-CAT-02 | S-13 |
| Liên kết tới trang khóa học ngoài | FR-16; §4.3 | SRS-CAT-02 | S-13 |
| Tìm, lọc cấp độ, sắp xếp | §10.3 | SRS-CAT-01 | S-12 |
| Lọc theo kỹ năng | §10.3 | SRS-CAT-01 | S-12 (UI không có — ND-72) |
| Kỹ năng của khóa học | §10.3 | SRS-CAT-02 | S-13 |
| Cần đăng nhập để xem | UC-06 tiền điều kiện | SRS-CAT-03 | S-12 (quyền: ND-70) |

Chi tiết yêu cầu (mã `CC-YCnn`) và chỗ BA khác quyết định: `docs/modules/course-catalog.md` §1 "Yêu cầu".

## B. Quyết định đã chốt

| Mã | Nội dung |
|---|---|
| D-FE-11 | Frontend theo API contract, chỉ đổi nhãn (ví dụ cấp độ `beginner/intermediate/advanced`) |
| D-FE-12 | Giao diện theo `docs/ui-design/`, không tạo quy tắc |

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung |
|---|---|
| ND-70 | Quyền xem danh mục khóa học |
| ND-72 | Lọc theo kỹ năng: thêm vào UI hay chỉ giữ ở API |
| ND-61 | Budget, Tags (đề bài) — giữ hiện hành (ND-81) |
| ND-77, ND-81 | Điểm đề bài khác hiện hành |
| ND-50 | Route `/courses/:courseId/join` |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

Người phụ trách (Khôi) bổ sung tài liệu hoặc đề xuất ND qua người có thẩm quyền:

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Request, response, mã lỗi của EP-017 … EP-019 | Chặn viết test và frontend theo hợp đồng |
| 2 | Người phụ trách màn JoinDialog | Phân công màn hình |

### C3. Mặc định an toàn có trong nguồn

| Mặc định | Nguồn | Điều kiện dùng |
|---|---|---|
| Màn chưa có endpoint hiển thị "chưa khả dụng" | D-FE-08 | Chỉ cho màn chưa có endpoint |
