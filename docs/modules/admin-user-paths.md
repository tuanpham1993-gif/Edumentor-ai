# Module: Quản trị lộ trình người dùng (F14)

Đặc tả nghiệp vụ của tính năng. Schema ở `docs/database-design.md` §3, §4, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `AU-YCnn`, mã quy tắc `AU-Rnn`.

> **DRAFT, chưa có căn cứ BA.** BA không có chức năng này; BA §4.3, FR-41 và NFR-30 còn giới hạn việc xem dữ liệu cá nhân. Có giữ chức năng hay không: ND-79. Không triển khai khi ND-79, ND-55 chưa chốt.

---

## 1. Phạm vi

**Người phụ trách:** Hòa (workbook V2, sheet chi tiết tính năng). Màn AdminUserPaths và EP-100 ghi "Hòa, Tuấn": **Chờ nhóm chốt**. · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Admin xem, chỉ đọc, danh sách người dùng, các lộ trình của từng người, tiến độ kỹ năng và đồ thị lộ trình; tìm theo người dùng hoặc theo mục tiêu lộ trình.

**Thuộc module:** Admin đọc dữ liệu lộ trình của người dùng khác. Chưa có endpoint chính thức.

**Không thuộc module:** người dùng tự quản lý lộ trình (F05, F06); mẫu lộ trình (`admin-base-paths.md`).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| AU-YC01 | Admin xem, chỉ đọc, lộ trình và tiến độ kỹ năng của từng người dùng | Không có trong BA; BA §4.3, FR-41, NFR-30 giới hạn dữ liệu cá nhân. Căn cứ khác: `README.md` F14; UI AdminUserPaths | ND-79; ND-55 (M3) |
| AU-YC02 | Tìm người dùng theo tên, email; xem theo mục tiêu lộ trình | Không có trong BA. Căn cứ khác: UI AdminUserPaths | ND-79; ND-55 (M3) |

### Màn hình UI

| Màn | Route | Endpoint |
|---|---|---|
| AdminUserPaths | `/admin/user-paths` | Chưa có (M3): danh sách người dùng; lộ trình, node, cạnh và `UserSkill` của một người |

UI hiển thị tên lộ trình mà `LearningPath` chưa có cột (ND-54). Theo D-FE-08, màn vẫn dựng và hiển thị "chưa khả dụng".

---

## 2. File liên quan

`docs/structure.md` §3: `admin/AdminUserPathsPage`. File backend chưa có trong `docs/structure.md`.

---

## 3. Dữ liệu

Chỉ đọc (theo workbook V2). Chi tiết cột: `docs/database-design.md` §3.1, §3.2, §4.4–§4.6.

| Bảng | Dùng cho |
|---|---|
| `User` | Danh sách, tìm theo tên, email |
| `LearningPath`, `LearningPathNode`, `LearningPathEdge` | Lộ trình và đồ thị |
| `UserSkill` | Tiến độ kỹ năng |

---

## 4. Endpoint

`docs/api-endpoints.md` **chưa có endpoint** (ND-55, M3). Gợi ý trong workbook V2, **chưa duyệt**:

| Mã | Gợi ý | Trạng thái |
|---|---|---|
| EP-075 | Danh sách người dùng (`GET /api/admin/users?search=`) | Chưa duyệt |
| EP-100 | Lộ trình của một người dùng (`GET /api/admin/users/{id}/learning-paths`) | Chưa duyệt |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| AU-R01 | Chỉ quản trị viên được truy cập; backend kiểm tra quyền. | BA FR-40, BR-34; `api-endpoints.md` §14 |
| AU-R02 | Chức năng chỉ đọc; không sửa dữ liệu của người dùng. | `README.md` F14 ("chỉ đọc"); workbook V2 |

Quy tắc quyền riêng tư và ghi log khi Admin xem dữ liệu cá nhân: ND-79.

---

## 6. Luồng nghiệp vụ

Chưa có.

## 7. Transaction

Chỉ đọc.

## 8. Bảo mật

AU-R01, AU-R02; giới hạn dữ liệu cá nhân theo BA NFR-30 (ND-79).

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F05, F06 | Dữ liệu lộ trình |
| F01 | Dữ liệu người dùng, `UserSkill` |

---

## 10. Câu hỏi mở

`ND-79`, `ND-55` (M3), `ND-54` — `docs/decisions.md` §4.4, §6.

Chưa có ND: người phụ trách màn AdminUserPaths và EP-100.
