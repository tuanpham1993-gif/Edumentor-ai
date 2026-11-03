# Đặc tả theo tính năng

Mục lục các file đặc tả trong `docs/modules/`. Mỗi file dẫn xuất từ BA (`docs/EdumentorAi_BA.md`, bản Git HEAD) theo thứ tự ưu tiên D-DOC-01 (`docs/decisions.md` §1). Khi BA khác `docs/decisions.md`, đặc tả viết theo `decisions.md` và ghi "BA khác".

Người phụ trách 14 tính năng lấy theo D-OWN-02 (`docs/decisions.md` §2); hai module của Tuấn còn có D-OWN-01. Workbook V2 (`EduMentor_AI_Ke_Hoach_14_Tinh_Nang_UPDATED_V2.xlsx`, sổ nguồn ở `docs/decisions.md` §1) ghi khác ở F07 (Hòa), F10 (Tâm), F11 (Khôi), F12 (Hòa), F13 (Tâm) — workbook không phải nguồn quyết định; các tên đó chỉ giữ để truy vết. Phần chưa có quyết định mà các nguồn ghi khác nhau thì ghi **Chờ nhóm chốt**. Bảng này chỉ là mục lục.

Quy ước trạng thái: `docs/decisions.md` §2. **DRAFT** = bản soạn từ nguồn, chưa được người phụ trách xác nhận. Không dùng "DONE" cho phần chưa có code.

## 14 tính năng

| Mã | Tính năng | Người phụ trách | File | Đặc tả | Kiểm thử |
|---|---|---|---|---|---|
| F01 | Tài khoản và hồ sơ | Tuấn | [auth-profile.md](auth-profile.md) | SPEC CONFIRMED (còn PENDING) | [auth-profile.tests.md](auth-profile.tests.md) |
| F02 | Danh mục khóa học | Khôi | [course-catalog.md](course-catalog.md) | DRAFT | Chưa có |
| F03 | Lưu khóa học (bookmark) | Tâm; endpoint: Chờ nhóm chốt | [course-bookmark.md](course-bookmark.md) | DRAFT | Chưa có |
| F04 | Theo dõi tiến trình khóa học | Hòa | [course-tracking.md](course-tracking.md) | DRAFT | Chưa có |
| F05 | AI Consultant và lộ trình học tập | Hòa | [learning-path-consultant.md](learning-path-consultant.md) | DRAFT | Chưa có |
| F06 | Node và cạnh trong lộ trình | Hòa | [learning-path-graph.md](learning-path-graph.md) | DRAFT | Chưa có |
| F07 | Gợi ý khóa học theo kỹ năng | Tâm | [skill-course-recommendation.md](skill-course-recommendation.md) | DRAFT | Chưa có |
| F08 | AI Tutor | Tâm | [ai-tutor.md](ai-tutor.md) | DRAFT | Chưa có |
| F09 | Ôn tập và đánh giá kiến thức | Tuấn | [review-assessment.md](review-assessment.md) | SPEC CONFIRMED (còn BLOCKED/PENDING) | [review-assessment.tests.md](review-assessment.tests.md) |
| F10 | Phản hồi | Khôi | [feedback.md](feedback.md) | DRAFT, chưa có căn cứ BA | Chưa có |
| F11 | Quản trị khóa học, kỹ năng | Hòa | [admin-course-skill.md](admin-course-skill.md) | DRAFT | Chưa có |
| F12 | Quản trị quan hệ kỹ năng | Tâm | [admin-skill-relation.md](admin-skill-relation.md) | DRAFT | Chưa có |
| F13 | Quản trị phản hồi | Hòa | [admin-feedback.md](admin-feedback.md) | DRAFT, căn cứ BA rất ít | Chưa có |
| F14 | Quản trị lộ trình người dùng | Hòa; một phần: Chờ nhóm chốt | [admin-user-paths.md](admin-user-paths.md) | DRAFT, chưa có căn cứ BA | Chưa có |

## Ngoài 14 tính năng

| Phần | Người phụ trách | File | Đặc tả |
|---|---|---|---|
| Ngân hàng câu hỏi ôn tập | Chờ nhóm chốt | [admin-question-bank.md](admin-question-bank.md) | DRAFT |
| Mẫu lộ trình cơ sở | Chờ nhóm chốt (workbook: Hòa) | [admin-base-paths.md](admin-base-paths.md) | DRAFT |
| Dữ liệu lộ trình lịch sử (tùy chọn) | Chờ nhóm chốt | [admin-historical-data.md](admin-historical-data.md) | DRAFT |
| Bong bóng chat và AI tư vấn khóa học | Chờ nhóm chốt | [chat-advisor.md](chat-advisor.md) | DRAFT, chưa có căn cứ BA |

## Cấu trúc một file

Giữ cùng số mục với hai file đã xác nhận, để skill và tài liệu khác trỏ theo số mục không bị lệch:

1. Phạm vi — người phụ trách, trạng thái, mô tả, thuộc và không thuộc module, **yêu cầu** (mỗi dòng có nguồn BA và mã D/T/ND), **màn hình UI**.
2. File liên quan — theo `docs/structure.md`.
3. Dữ liệu — bảng thuộc module và bảng chỉ đọc; chi tiết cột ở `docs/database-design.md`.
4. Endpoint — theo `docs/api-endpoints.md`; mã `EP-xxx` theo workbook.
5. Quy tắc nghiệp vụ — mã `XX-Rnn`, mỗi dòng có nguồn.
6. Luồng nghiệp vụ.
7. Transaction.
8. Bảo mật.
9. Phụ thuộc với module khác.
10. Câu hỏi mở — chỉ trỏ tới `ND-xx`; điểm chưa có ND ghi "chưa có ND".

Quy tắc soạn:

- Không có nguồn thì không viết thành quy tắc; ghi `[NEEDS DECISION]`.
- Màn hình trong `docs/ui-design/` chỉ mô tả giao diện, không tạo quy tắc (D-FE-12).
- Mã yêu cầu `XX-YCnn` và mã quy tắc `XX-Rnn` dùng cho file `.tests.md` sau này. File `.tests.md` chỉ viết khi đặc tả đã được người phụ trách xác nhận.

| Tiền tố | File | Tiền tố | File |
|---|---|---|---|
| `AP` | auth-profile | `AD` | admin-course-skill |
| `CC` | course-catalog | `SR` | admin-skill-relation |
| `BM` | course-bookmark | `AF` | admin-feedback |
| `CT` | course-tracking | `AU` | admin-user-paths |
| `LP` | learning-path-consultant | `QB` | admin-question-bank |
| `LG` | learning-path-graph | `BP` | admin-base-paths |
| `RC` | skill-course-recommendation | `HD` | admin-historical-data |
| `TU` | ai-tutor | `CA` | chat-advisor |
| `RV` | review-assessment | `FB` | feedback |

## Mục BA không gán cho một tính năng

Các mục sau áp dụng chung, không nằm trong file tính năng nào; file tính năng chỉ trích mã khi cần:

- Tổng quan: BA §1–§3, §4.1, §4.2, §5.1, §5.4, §12, §13.
- Phân quyền và quy tắc chung: BA §4.3, §5.5 (BR-01 … BR-08 của §5.5, khác nghĩa với BR-01 … BR-08 của §9), FR-40 … FR-43, §10.1, §10.14. Quy tắc kỹ thuật dùng chung: `docs/backend-rules.md`, `docs/conventions.md`.
- Phi chức năng: BA §7 (NFR-01 … NFR-39), trừ các NFR được trích trong từng file.
- AI/ML chung: BA §8.1, §8.7, §8.8, AC-10, AC-11.

Bảng ánh xạ RTM ở BA §13.2 có dải mã FR sai so với §6; các file ở đây dùng mã theo BA §6.
