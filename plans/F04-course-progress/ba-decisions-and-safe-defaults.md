# F04 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Cập nhật trạng thái khóa học | FR-18 (khác D02, T13) | SRS-TRK-04 | S-15 |
| Xem tiến độ của mình | FR-19 | SRS-TRK-03 | S-15 |
| Tham gia khóa học, mở URL ngoài | §10.4; FR-16 | SRS-TRK-02 | S-14 |
| Ngừng theo dõi → abandoned | §10.4 | SRS-TRK-04 | S-15 |
| Hoàn thành chỉ khi đạt ôn tập | §10.4 quy tắc 5 | SRS-TRK-05 | S-13, S-23 |

Chi tiết yêu cầu (mã `CT-YCnn`) và chỗ BA khác quyết định: `docs/modules/course-tracking.md` §1 "Yêu cầu".

## B. Quyết định đã chốt

| Mã | Nội dung |
|---|---|
| D05 | `join` thêm kỹ năng của khóa vào `UserSkill` ở `learning` nếu chưa `known` |
| D02, T13 | `completed` chỉ khi làm đạt bài ôn tập; ghi trong transaction nộp bài (F09) |
| T08 | `GET /api/me/courses?status=abandoned` |

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung |
|---|---|
| ND-76 | Lời văn BA FR-18 về `completed` |
| ND-80 | Hai cách lấy khóa đã lưu |
| ND-32 | Bảng Bookmark |
| ND-28 | Chuyển `abandoned` khi có bài ôn dở |
| ND-50 | Route `/courses/:courseId/join` |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

Người phụ trách (Hòa) bổ sung tài liệu hoặc đề xuất ND qua người có thẩm quyền:

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Chuyển trạng thái được phép qua PATCH | API, test |
| 2 | Phạm vi "đề xuất khóa liên quan node" (trùng EP-043 của F07) | Phạm vi F04, F07 |
| 3 | Quyền của `join`; response, mã lỗi | API |
| 4 | Người phụ trách màn JoinDialog, MyCourses | Phân công |

### C3. Mặc định an toàn có trong nguồn

Nguồn không ghi mặc định an toàn nào cho tính năng này. Không tự đặt mặc định.
