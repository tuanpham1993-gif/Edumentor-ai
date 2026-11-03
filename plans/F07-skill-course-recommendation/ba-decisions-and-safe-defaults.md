# F07 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Thông tin kỹ năng đang chọn | FR-12 | SRS-REC-01 | S-18 |
| Khóa học liên quan kỹ năng | FR-13; BR-12 | SRS-REC-01 | S-18 |
| Xếp hạng theo độ phù hợp | FR-14; BR-13, BR-14; §8.4.3 | SRS-REC-02 | S-18 |
| Không dùng điểm ôn tập | BR-15 | SRS-REC-02 | — |
| Không có khóa phù hợp thì báo | BR-16 | SRS-REC-03 | S-18 |

Chi tiết yêu cầu (mã `RC-YCnn`) và chỗ BA khác quyết định: `docs/modules/skill-course-recommendation.md` §1 "Yêu cầu".

## B. Quyết định đã chốt

Không có quyết định D/T riêng cho tính năng; áp dụng quyết định chung (D-DOC-01, D-FE-01 … D-FE-12).

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung |
|---|---|
| ND-61 | Budget (đề bài) — giữ hiện hành |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

Người phụ trách (Tâm) bổ sung tài liệu hoặc đề xuất ND qua người có thẩm quyền:

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Phạm vi trùng với F04 | Phạm vi |
| 2 | Nơi cấu hình trọng số; cách tính `level_fit`, `skill_match` | Xếp hạng, test |
| 3 | Quyền, response của EP-043 | API |

### C3. Mặc định an toàn có trong nguồn

Nguồn không ghi mặc định an toàn nào cho tính năng này. Không tự đặt mặc định.
