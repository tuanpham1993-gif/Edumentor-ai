# CONVENTIONS — Quy ước phát triển EduMentor AI

Tài liệu này quy định các quy ước chung mà mọi thành viên cần tuân thủ để mã nguồn và API nhất quán.

---

## 1. Quy ước API

- Mọi endpoint bắt đầu bằng `/api/`.
- Dùng đúng HTTP method RESTful: `GET` (đọc), `POST` (tạo / thực hiện hành động), `PATCH` (cập nhật một phần), `DELETE` (xóa hoặc ngừng).
- `{id}` là mã định danh tài nguyên; ví dụ `{course_id}`, `{path_id}`, `{skill_id}`.
- Endpoint dành riêng cho người dùng (`/api/me/...`) chỉ thao tác trên dữ liệu của **người dùng đã xác thực**, không nhận `user_id` từ client.
- Endpoint quản trị bắt đầu bằng `/api/admin/` và chỉ dành cho quản trị viên.
- Tên đường dẫn: chữ thường, danh từ số nhiều, nối từ bằng dấu gạch ngang (`learning-paths`, `review-attempts`).
- Query parameter dùng `snake_case` (`skill_id`, `sort_by`). Có thể kết hợp nhiều bộ lọc.
- Chức năng tạo lộ trình (`/api/chat/learning-path`) và gia sư (`/api/chat/sessions`) cùng namespace `/api/chat/` nhưng dùng **endpoint và loại phiên riêng**.

### Cấu trúc lỗi thống nhất

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Mô tả lỗi dễ hiểu",
    "details": []
  }
}
```

| HTTP | Khi nào dùng |
|---|---|
| 400 / 422 | Dữ liệu đầu vào không hợp lệ |
| 401 | Chưa xác thực |
| 403 | Không đủ quyền (ví dụ không phải admin) |
| 404 | Tài nguyên không tồn tại |
| 409 | Chuyển trạng thái xung đột, dữ liệu trùng |

### Phân trang

Endpoint trả danh sách nhận `page` và `page_size`, trả về `items`, `total`, `page`, `page_size`.

---

## 2. Quy tắc nghiệp vụ bắt buộc

### Khóa học
- Khóa học trỏ tới nền tảng MOOC bên ngoài. EduMentor **không** lưu nội dung và **không** đăng ký thay người dùng.
- Trạng thái theo dõi: `bookmarked`, `ongoing`, `completed`, `abandoned`. Đây là trạng thái của EduMentor, không phải của nền tảng ngoài.
- `POST /api/courses/{course_id}/join` ghi nhận `ongoing` và trả URL ngoài.
- **Không** đánh dấu `completed` chỉ vì người dùng mở URL ngoài. `completed` chỉ đến từ việc hoàn tất bài ôn tập.
- Xóa bookmark chỉ xóa bản ghi bookmark, không tự chuyển `abandoned`.
- Danh sách mặc định loại trừ `abandoned`.
- Chỉ theo dõi tiến trình ở mức cơ bản; không theo dõi bài học, video hay mức độ hoàn thành nội dung.

### Lộ trình học tập
- Trạng thái: `ongoing`, `completed`, `abandoned`.
- `DELETE` lộ trình = chuyển sang `abandoned`, **không** xóa vĩnh viễn.
- Lộ trình do AI đề xuất **chưa** được chấp nhận cho đến khi người dùng xác nhận/lưu.
- Thay đổi nhỏ → cập nhật lộ trình hiện tại. Mục tiêu/lộ trình khác biệt đáng kể → tạo lộ trình mới, giữ lịch sử cũ.

### Node và cạnh
- Khóa chính node: `(path_id, skill_id)`; một kỹ năng chỉ xuất hiện một lần trong một lộ trình.
- `node_role` ∈ `prerequisite`, `optional`, `extension`, `NULL`. `added_by` ∈ `system`, `user`.
- `display_order` chỉ quyết định thứ tự hiển thị, **không** xác định tiên quyết.
- Hai đầu của cạnh phải là node trong cùng lộ trình. Với `prerequisite`, nguồn học trước đích.
- Xóa node phải xóa/cập nhật các cạnh liên quan **trong cùng transaction**, không để cạnh mồ côi.

### Gợi ý khóa học
- Chỉ truy xuất khi người dùng chọn một node, không gợi ý hàng loạt khi tạo lộ trình.
- Mức độ liên quan đến kỹ năng là yếu tố hàng đầu; rating không phải bằng chứng duy nhất.
- **Không** đưa điểm ôn tập vào xếp hạng khóa học.

### Ôn tập
- Mỗi bài ôn tập theo kỹ năng gồm **20 câu trắc nghiệm** lấy từ CSDL.
- Không trả đáp án đúng trước khi người dùng nộp bài.
- Sau khi hoàn tất: lưu lần làm → đánh dấu khóa học `completed` → cập nhật kỹ năng người dùng (backend tự làm, frontend không gửi request riêng).

### AI
- Mô hình AI chỉ diễn giải mục tiêu; backend chịu trách nhiệm ánh xạ kỹ năng, mở rộng quan hệ, tham khảo lộ trình lịch sử và lưu kết quả.
- Mọi mục tiêu/kỹ năng do AI sinh ra phải được **xác thực với danh mục kỹ năng** trước khi dùng.
- Dữ liệu lịch sử nhập vào không được tự ghi đè lộ trình đang dùng của người dùng.

---

## 3. Quy ước mã nguồn (Backend – Python)

- Tuân thủ PEP 8; định dạng bằng `black`, kiểm tra bằng `ruff`.
- Tên file/hàm/biến: `snake_case`; class: `PascalCase`; hằng số: `UPPER_SNAKE_CASE`.
- Phân lớp: **router → service → repository → model**. Router không viết truy vấn hay logic nghiệp vụ.
- Dùng **transaction** cho mọi thao tác sửa nhiều bản ghi liên quan.
- Kiểm tra request body, ID, giá trị trạng thái và tham chiếu trước khi ghi dữ liệu (Pydantic schema + kiểm tra trong service).
- Không hard-code bí mật; đọc từ biến môi trường (`.env`).
- Mọi thay đổi cấu trúc CSDL phải đi qua **Alembic migration**, không sửa tay trên DB.

## 4. Quy ước mã nguồn (Frontend)

- Component: `PascalCase.jsx`; hàm/biến: `camelCase`.
- Mỗi nhóm endpoint có một file trong `src/api/`; component không gọi `fetch` trực tiếp.
- Hiển thị thông báo lỗi dựa trên `error.message` từ cấu trúc lỗi thống nhất.

---

## 5. Quy ước Git

**Nhánh**
- `main`: ổn định, dùng để báo cáo/demo.
- `develop`: tích hợp.
- `feature/<nhóm>-<mô-tả>`: ví dụ `feature/learning-path-nodes`.
- `fix/<mô-tả>`: sửa lỗi.

**Commit** theo dạng `<loại>(<phạm vi>): <mô tả>`:

```
feat(courses): thêm lọc khóa học theo skill_id
fix(path): xóa cạnh liên quan khi xóa node
docs: cập nhật SETUP
```

Loại: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

**Pull Request**: ít nhất 1 người review; phải qua test trước khi merge vào `develop`.

---

## 6. Kiểm thử

- Mỗi nhóm endpoint có file test tương ứng trong `backend/tests/`.
- Bắt buộc có test cho: chuyển trạng thái khóa học, xóa node kèm cạnh, chấm điểm ôn tập, phân quyền admin, xác thực đầu ra AI.
- Chạy `pytest` trước khi tạo Pull Request.
