# Module: Quản trị phản hồi (F13)

Đặc tả nghiệp vụ của tính năng. Schema ở `docs/database-design.md` §7, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `AF-YCnn`, mã quy tắc `AF-Rnn`.

> **DRAFT, căn cứ BA rất ít.** BA chỉ có một dòng về quyền của Admin (§4.1.2); không có FR, UC hay endpoint. Không triển khai khi ND-35, ND-55 chưa chốt.

---

## 1. Phạm vi

**Người phụ trách:** Hòa (D-OWN-02; workbook V2 ghi Tâm — workbook không phải nguồn quyết định). Dòng Feedback & liên hệ ở `docs/decisions.md` §2 (ND-35) chưa được đối chiếu với D-OWN-02. · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Admin xem phản hồi của học viên, lọc theo đối tượng, loại và thời gian, sắp xếp theo thời gian, xem chi tiết một phản hồi.

**Thuộc module:** Admin đọc `Feedback`. Chưa có endpoint chính thức.

**Không thuộc module:** học viên gửi phản hồi (F10, `feedback.md`).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| AF-YC01 | Admin trả lời, quản lý feedback của học viên; câu trả lời có thể được gửi qua email | §4.1.2 | ND-35 (trả lời trong hệ thống hay qua email ngoài; UI chỉ có `mailto:`) |
| AF-YC02 | Admin xem, lọc phản hồi theo loại, đối tượng, thời gian và sắp xếp theo thời gian | Không có trong BA. Căn cứ khác: `README.md` F13; UI AdminFeedback | ND-55 (M2), ND-69 |

### Màn hình UI

| Màn | Route | Endpoint |
|---|---|---|
| AdminFeedback | `/admin/feedback` | Chưa có (M2) |
| AdminFeedback-Detail | `/admin/feedback` | Chưa có (M2); nút trả lời mở `mailto:`, không qua API |

Theo D-FE-08, màn vẫn dựng giao diện và hiển thị "chưa khả dụng".

---

## 2. File liên quan

`docs/structure.md` §3: `admin/AdminFeedbackPage`. File backend chưa có trong `docs/structure.md`.

---

## 3. Dữ liệu

| Bảng | Đọc / ghi | Ghi chú |
|---|---|---|
| `Feedback` | Đọc | Không có cột trạng thái xử lý hay câu trả lời (`database-design.md` §7.1); trả lời trong hệ thống cần cột hoặc bảng mới (ND-35) |
| `User`, `Course`, `CourseContact` | Đọc | Người gửi, khóa học, liên hệ của khóa |

---

## 4. Endpoint

`docs/api-endpoints.md` **chưa có endpoint** (ND-55, M2). Đề xuất trong workbook V2, **chưa duyệt**:

| Mã | Đề xuất | Trạng thái |
|---|---|---|
| EP-074 | Danh sách phản hồi (`GET /api/admin/feedback`) | Chưa duyệt |
| EP-101 | Chi tiết phản hồi (`GET /api/admin/feedback/{feedback_id}`) | Chưa duyệt |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| AF-R01 | Chỉ quản trị viên được xem dữ liệu quản trị; backend kiểm tra quyền. | BA FR-40, BR-34; `api-endpoints.md` §14 |

Bộ lọc, phân trang, cách trả lời: `[NEEDS DECISION]` (ND-35, ND-55, ND-69).

---

## 6. Luồng nghiệp vụ

Chưa có.

## 7. Transaction

Chỉ đọc, nếu không làm chức năng trả lời trong hệ thống (ND-35).

## 8. Bảo mật

AF-R01. Phản hồi chứa thông tin người gửi (tên, email): chỉ hiển thị cho Admin.

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F10 Phản hồi | Nguồn dữ liệu `Feedback` |
| F01 | Thông tin người gửi |

---

## 10. Câu hỏi mở

`ND-35`, `ND-55` (M2), `ND-69`, `D11`, `ND-81` — `docs/decisions.md` §2, §4.4, §6.
