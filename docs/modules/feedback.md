# Module: Phản hồi và liên hệ (F10)

Đặc tả nghiệp vụ của tính năng. Schema ở `docs/database-design.md` §7, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `FB-YCnn`, mã quy tắc `FB-Rnn`.

> **DRAFT, chưa có căn cứ BA.** BA không có yêu cầu chức năng cho việc học viên gửi phản hồi; endpoint T22–T25 chưa được nhóm đồng ý (`docs/decisions.md` §3, ND-35). File này chỉ ghi những gì đã có trong CSDL và các điểm đang chờ; **không triển khai** khi các ND bên dưới chưa chốt.

---

## 1. Phạm vi

**Người phụ trách:** **Chờ nhóm chốt** — workbook V2 ghi Tâm; `docs/decisions.md` §2 ghi chưa rõ (Khôi hay Tâm, ND-35). · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Trang "Liên hệ & góp ý": người dùng đã đăng nhập gửi phản hồi về một khóa học hoặc về hệ thống, và xem thông tin liên hệ của khóa học.

**Thuộc module:** gửi phản hồi; xem liên hệ khóa học. Chưa có endpoint chính thức.

**Không thuộc module:** Admin xem, lọc phản hồi (F13, `admin-feedback.md`).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| FB-YC01 | Người dùng gửi phản hồi về khóa học hoặc về hệ thống | Không có trong BA. Căn cứ khác: `database-design.md` §7.1; UI Contact | ND-35; ND-55 (M2) |
| FB-YC02 | Xem thông tin liên hệ của khóa học (giảng viên, email, điện thoại) | Không có trong BA. Căn cứ khác: `database-design.md` §7.2; UI Contact | ND-55 (M2) |
| FB-YC03 | Phân loại phản hồi (`feedback_type`) | Không có trong BA. Căn cứ khác: `database-design.md` §7.1 | D11, ND-69 |
| FB-YC04 | Admin cập nhật phản hồi ("Update feedback") | Không có trong BA; chỉ có ở đề bài SRS v1.0 | ND-35, ND-81 |

### Màn hình UI

| Màn | Route | Endpoint |
|---|---|---|
| Contact | `/contact` | `GET /api/courses` (F02) để chọn khóa; gửi phản hồi và xem liên hệ: chưa có (M2) |
| ContactGuest | `/contact-guest` | Không gọi API; form khóa khi chưa đăng nhập. Route: ND-50 |

Theo D-FE-08, màn chưa có endpoint vẫn dựng giao diện và hiển thị "chưa khả dụng".

---

## 2. File liên quan

`docs/structure.md` §3: `feedback/FeedbackPage` (route `/contact`). File backend cho nhóm này chưa có trong `docs/structure.md`.

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §7. Endpoint cho nhóm bảng này chưa được nhóm đồng ý (`database-design.md` §7).

| Bảng | Dùng cho |
|---|---|
| `Feedback` | Phản hồi: `user_id`, `target_type`, `course_id`, `feedback_type`, `content`, `created_at` |
| `CourseContact` | Liên hệ của khóa: `contact_email`, `contact_phone` |
| `Course` | `instructor`; khóa học được phản hồi |

---

## 4. Endpoint

`docs/api-endpoints.md` **chưa có endpoint** cho tính năng này (ND-55, M2). Workbook V2 ghi các đề xuất **chưa duyệt** dưới đây; không phải endpoint đã tồn tại, không được triển khai theo bảng này (`CLAUDE.md`: không thêm endpoint ngoài tài liệu).

| Mã | Đề xuất trong workbook | Trạng thái |
|---|---|---|
| EP-057 | Gửi phản hồi (`POST /api/feedback`) | Chưa duyệt |
| EP-099 | Liên hệ khóa học (`GET /api/courses/{course_id}/contact`) | Chưa duyệt |
| EP-102 | Danh sách lựa chọn (`GET /api/feedback/options`) | Chưa duyệt; phụ thuộc ND-69, D11 |
| EP-103, EP-104 | Tùy chọn, không có màn hình bắt buộc | Chưa duyệt |

---

## 5. Quy tắc nghiệp vụ

Chỉ gồm ràng buộc đã có trong CSDL:

| Mã | Quy tắc | Nguồn |
|---|---|---|
| FB-R01 | `user_id` lấy từ tài khoản đăng nhập. | `database-design.md` §7.1 |
| FB-R02 | `target_type` là `course` hoặc `system`; `course` thì bắt buộc có `course_id`, `system` thì `course_id` trống. | `database-design.md` §7.1 |
| FB-R03 | `content` bắt buộc. | `database-design.md` §7.1 |
| FB-R04 | Mỗi khóa học có tối đa một dòng `CourseContact`; dataset chưa có email, điện thoại nên bảng có thể trống. | `database-design.md` §7.2 |

Giới hạn độ dài nội dung, danh sách `feedback_type`, quyền của khách: `[NEEDS DECISION]` (ND-69, ND-35).

---

## 6. Luồng nghiệp vụ

Chưa có: phụ thuộc ND-35, ND-55.

## 7. Transaction

Chưa có.

## 8. Bảo mật

Phản hồi gắn với người dùng đăng nhập (FB-R01). Khách xem liên hệ được hay không: chưa chốt.

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F13 Quản trị phản hồi | Đọc `Feedback` |
| F02 Danh mục | Chọn khóa học khi gửi phản hồi |
| Bong bóng chat | Lối tắt "Liên hệ" mở `/contact` |

---

## 10. Câu hỏi mở

`ND-35`, `ND-55` (M2), `ND-69`, `D11`, `ND-50`, `ND-77`, `ND-81` — `docs/decisions.md` §2, §4.4, §6.

Chưa có ND: người phụ trách (xung đột giữa workbook và `decisions.md` §2 nằm trong ND-35).

Đầu vào tham khảo ngoài repo, chưa duyệt: bản "Đặc tả đề xuất M2 Feedback". Nội dung lấy từ đó phải giữ ở trạng thái `[NEEDS DECISION]`.
