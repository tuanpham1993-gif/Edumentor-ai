# Module: Ngân hàng câu hỏi ôn tập (ngoài 14 tính năng)

Đặc tả nghiệp vụ của phần quản trị câu hỏi. Bảng tóm tắt endpoint ở `docs/api-endpoints.md` §11, schema ở `docs/database-design.md` §6.1, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `QB-YCnn`, mã quy tắc `QB-Rnn`.

> **DRAFT.** Endpoint đã được nhóm tick (T19–T21), nhưng BA không có FR cho việc quản trị câu hỏi, giao diện không có màn hình (ND-53) và người phụ trách đang xung đột (CONFLICT-SCOPE-01).

---

## 1. Phạm vi

**Người phụ trách:** **Chờ nhóm chốt** — workbook V2 ghi Tuấn; `docs/decisions.md` §2 ghi CONFLICT-SCOPE-01 (Tuấn đã loại phần này khỏi phạm vi skill Ôn tập). · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Admin quản lý câu hỏi trắc nghiệm theo kỹ năng: danh sách, thêm, xem, sửa, xóa hoặc vô hiệu hóa, nhập hàng loạt. Đây là nguồn câu hỏi cho bài ôn tập (F09).

**Thuộc module:** `/api/admin/questions*` (6 endpoint).

**Không thuộc module:** chọn câu, chấm bài, lịch sử (F09, `review-assessment.md`; module đó chỉ đọc `Question`).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| QB-YC01 | Câu hỏi phải liên quan đến kỹ năng và đạt tiêu chí chất lượng của hệ thống câu hỏi | BR-27 | — |
| QB-YC02 | Câu hỏi ôn tập lấy từ ngân hàng câu hỏi theo kỹ năng | §8.6 | **BA khác:** BA dùng RAG để truy xuất; theo D04, T14 lấy câu `is_active` từ CSDL (ND-58) |
| QB-YC03 | Admin quản lý câu hỏi: danh sách, thêm, xem, sửa, xóa hoặc vô hiệu hóa, nhập hàng loạt | Không có FR trong BA | T19, T20, T21 ☑ |
| QB-YC04 | Hỗ trợ câu hỏi mở, câu hỏi lập trình | FR-25; BR-29 | ND-73 (hiện chỉ trắc nghiệm) |

### Màn hình UI

`docs/ui-design/` **không có màn** quản trị câu hỏi (ND-53).

---

## 2. File liên quan

Theo `docs/structure.md` §2:

| Lớp | File |
|---|---|
| Router | `backend/app/routers/admin/questions.py` |
| Service | Chưa đặt tên trong tài liệu |
| Model | `question.py` |

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §6.1.

| Bảng | Đọc / ghi | Ràng buộc chính |
|---|---|---|
| `Question` | Ghi | `skill_id` NN FK → Skill; `options` JSONB đúng 4 đáp án; `correct_index` 0–3; `is_active` NN DEFAULT TRUE |
| `ReviewAnswer` | Đọc | Câu đã dùng trong bài làm thì không xóa được (FK RESTRICT) |
| `Skill` | Đọc | Lọc theo kỹ năng |

---

## 4. Endpoint

Theo `docs/api-endpoints.md` §11. Quyền: Admin.

| Mã | Method | Endpoint | Mô tả | Nguồn |
|---|---|---|---|---|
| EP-076 | GET | `/api/admin/questions` | Danh sách, lọc `?skill_id=`, phân trang, kèm số câu đang hoạt động theo kỹ năng | T19 |
| EP-077 | POST | `/api/admin/questions` | Thêm: `skill_id`, `content`, `options` (4 đáp án), `correct_index` (0–3), `explanation` | T19 |
| EP-078 | GET | `/api/admin/questions/{question_id}` | Chi tiết, có đáp án đúng | T19 |
| EP-079 | PATCH | `/api/admin/questions/{question_id}` | Sửa | T19 |
| EP-080 | DELETE | `/api/admin/questions/{question_id}` | Chưa từng dùng → xóa thật; đã dùng → `is_active = false`; response nêu rõ | T20 |
| EP-081 | POST | `/api/admin/questions/import` | Tùy chọn: nhập từ CSV/JSON, báo cáo theo dòng | T21 |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| QB-R01 | Mỗi câu có đúng 4 đáp án; `correct_index` từ 0 đến 3. | T19; `database-design.md` §6.1 |
| QB-R02 | Xóa: câu chưa từng dùng thì xóa thật; câu đã dùng thì đặt `is_active = false`; response nói rõ đã làm gì. | T20; `database-design.md` §8.1 |
| QB-R03 | Chỉ câu `is_active = true` được dùng khi tạo bài ôn tập. | T26; RV-R02, RV-R06 |
| QB-R04 | Khóa học có bài ôn tập khi tổng câu đang hoạt động của các kỹ năng khóa dạy ≥ 20. | D04; RV-R02 |
| QB-R05 | Đáp án đúng chỉ trả ở endpoint quản trị, không lộ qua endpoint làm bài. | T15; RV-R07 |
| QB-R06 | Chỉ quản trị viên được dùng các endpoint này. | `api-endpoints.md` §11 |

---

## 6. Luồng nghiệp vụ

Định dạng file nhập và báo cáo theo dòng (EP-081): chưa ghi chi tiết; chưa có ND.

## 7. Transaction

Nhập hàng loạt ghi nhiều câu: áp dụng `api-endpoints.md` §14; xử lý khi một phần lỗi chưa ghi.

## 8. Bảo mật

QB-R05, QB-R06.

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F09 Ôn tập | Đọc `Question`; câu đã dùng phải giữ lại |
| F11 Kỹ năng | `Question.skill_id` tham chiếu `Skill` (RESTRICT) |

---

## 10. Câu hỏi mở

`ND-53`, CONFLICT-SCOPE-01, `ND-73`, `ND-58` — `docs/decisions.md` §2, §4.2, §6.

Chưa có ND: định dạng file nhập; xử lý lỗi một phần khi nhập; tên service.
