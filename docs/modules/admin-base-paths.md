# Module: Mẫu lộ trình cơ sở (ngoài 14 tính năng)

Đặc tả nghiệp vụ của phần quản trị mẫu lộ trình. Bảng tóm tắt endpoint ở `docs/api-endpoints.md` §12, schema ở `docs/database-design.md` §4.1–§4.3, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `BP-YCnn`, mã quy tắc `BP-Rnn`.

> **DRAFT** — dẫn xuất từ BA (bản Git HEAD) theo D-DOC-01, chưa được người phụ trách xác nhận.

---

## 1. Phạm vi

**Người phụ trách:** **Chờ nhóm chốt** — workbook V2 ghi Hòa cho các endpoint, nhưng màn AdminBasePaths ở trạng thái "Chờ quyết định"; `plans/plan.md` P11 ghi chưa phân công. · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Admin quản lý các mẫu lộ trình dùng lại cho mục tiêu phổ biến: kỹ năng mục tiêu ban đầu và quan hệ giữa chúng. AI Consultant dùng mẫu làm điểm xuất phát trước khi mở rộng lộ trình.

**Thuộc module:** `/api/admin/base-learning-paths*` (13 endpoint, gồm node và cạnh của mẫu).

**Không thuộc module:** tạo lộ trình cho người dùng (F05); quan hệ kỹ năng dùng chung (F12).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| BP-YC01 | Admin quản lý lộ trình mẫu và cấu trúc kỹ năng nền dùng để tham khảo hoặc hỗ trợ đề xuất | FR-34; UC-14; §4.1.2 | — |
| BP-YC02 | Chỉ Admin được thay đổi mẫu lộ trình | BR-32; BR-34 | — |
| BP-YC03 | Mẫu giúp AI Consultant có điểm xuất phát nhất quán, nhưng không ép cùng một lộ trình | §10.12 | — |

### Màn hình UI

| Màn | Route | Endpoint của module dùng |
|---|---|---|
| AdminBasePaths | `/admin/base-paths` | `GET /api/admin/base-learning-paths`, `PATCH /api/admin/base-learning-paths/{template_id}` (bật, tắt, sửa mẫu) |

UI hiển thị số lần dùng mẫu (`used`) mà API chưa có (ND-54).

---

## 2. File liên quan

Theo `docs/structure.md` §2:

| Lớp | File |
|---|---|
| Router | `backend/app/routers/admin/base_learning_paths.py` |
| Service | `base_path_service` |
| Frontend | `api/admin.api.js`; `admin/AdminBasePathsPage` |

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §4.1–§4.4.

| Bảng | Đọc / ghi | Ràng buộc chính |
|---|---|---|
| `BaseLearningPath` | Ghi | `name` NN UQ; `is_active` |
| `BaseLearningPathNode` | Ghi | PK (`template_id`, `skill_id`); `node_role`, `is_target`, `is_required`, `display_order` |
| `BaseLearningPathEdge` | Ghi | `relation_type` ∈ prerequisite, optional; hai đầu là node của mẫu |
| `LearningPath` | Đọc | `template_id` ghi mẫu đã dùng |

---

## 4. Endpoint

Theo `docs/api-endpoints.md` §12. Request, response và mã lỗi **chưa được định nghĩa**: `[NEEDS DECISION]`. Quyền: Admin.

| Mã | Method | Endpoint | Mô tả |
|---|---|---|---|
| EP-082 | GET | `/api/admin/base-learning-paths` | Danh sách mẫu |
| EP-083 | POST | `/api/admin/base-learning-paths` | Tạo mẫu |
| EP-084 | GET | `/api/admin/base-learning-paths/{template_id}` | Chi tiết, gồm kỹ năng mục tiêu và kết nối |
| EP-085 | PATCH | `/api/admin/base-learning-paths/{template_id}` | Cập nhật thông tin hoặc cấu hình |
| EP-086 | DELETE | `/api/admin/base-learning-paths/{template_id}` | Vô hiệu hóa hoặc xóa |
| EP-087 … EP-090 | GET, POST, PATCH, DELETE | `/api/admin/base-learning-paths/{template_id}/nodes*` | Kỹ năng trong mẫu |
| EP-091 … EP-094 | GET, POST, PATCH, DELETE | `/api/admin/base-learning-paths/{template_id}/edges*` | Kết nối trong mẫu (PATCH, DELETE tùy chọn) |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| BP-R01 | Tên mẫu không được trùng. | `database-design.md` §4.1 |
| BP-R02 | Mẫu đã có người dùng thì chỉ tắt (`is_active = false`), không xóa. | `database-design.md` §4.1; `api-endpoints.md` §12 |
| BP-R03 | Node của mẫu: `node_role` là `prerequisite`, `optional`, `extension` hoặc trống; `is_target`, `is_required`, `display_order`; không có `added_by`. | `database-design.md` §4.2 |
| BP-R04 | Cạnh của mẫu: `relation_type` là `prerequisite` hoặc `optional`; hai đầu phải là node của cùng mẫu. | `database-design.md` §4.3 |
| BP-R05 | Mẫu chỉ là điểm xuất phát; không bắt buộc mọi người cùng mục tiêu nhận lộ trình giống hệt nhau. | `api-endpoints.md` §12 |
| BP-R06 | Xóa mẫu thì `LearningPath.template_id` của lộ trình đã dùng mẫu được để trống (SET NULL). | `database-design.md` §8.1 |

---

## 6. Luồng nghiệp vụ

Cách AI Consultant dùng mẫu: `learning-path-consultant.md` LP-R06.

## 7. Transaction

Chưa ghi riêng; áp dụng `api-endpoints.md` §14.

## 8. Bảo mật

Chỉ Admin (BA BR-32, BR-34).

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F05 Lộ trình | Dùng mẫu làm điểm xuất phát |
| F11 Kỹ năng | Node tham chiếu `Skill` (RESTRICT) |

---

## 10. Câu hỏi mở

`ND-54` — `docs/decisions.md` §6.

Chưa có ND: người phụ trách; request, response, mã lỗi.
