# F08 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Hỏi đáp học tập | FR-20; UC-08 | SRS-TUT-01, 02 | S-20 |
| Giữ ngữ cảnh phiên | FR-21; BR-21 | SRS-TUT-03 | S-20 |
| Giải thích, phân tích mã, lỗi | FR-22; BR-24 | SRS-TUT-04 | S-20 |
| Bài tập củng cố | FR-23; §10.9 | SRS-TUT-05 | S-20 |
| Không đổi trạng thái học tập | BR-25 | SRS-TUT-06 | — |

Chi tiết yêu cầu (mã `TU-YCnn`) và chỗ BA khác quyết định: `docs/modules/ai-tutor.md` §1 "Yêu cầu".

## B. Quyết định đã chốt

Không có quyết định D/T riêng cho tính năng; áp dụng quyết định chung (D-DOC-01, D-FE-01 … D-FE-12).

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung |
|---|---|
| ND-59 | 6 tin nhắn gần nhất, chấm sao, bộ nhớ RAM/Redis (đề bài) — giữ hiện hành |
| ND-54 | Tin nhắn `code`, `quiz` có cấu trúc |
| ND-77, ND-81 | Đề bài khác hiện hành |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

Người phụ trách (Tâm) bổ sung tài liệu hoặc đề xuất ND qua người có thẩm quyền:

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Quy tắc chủ sở hữu khi truy cập phiên của người khác | API, bảo mật |
| 2 | Transaction gửi tin nhắn | API |
| 3 | Response, mã lỗi | API, test |

### C3. Mặc định an toàn có trong nguồn

| Mặc định | Nguồn | Điều kiện dùng |
|---|---|---|
| Frontend tạm bỏ phần `code`, `quiz` có cấu trúc | ND-54 | Tới khi ND-54 chốt |
