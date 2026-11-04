# Module: Danh mục khóa học (F02)

Đặc tả nghiệp vụ của tính năng. Bảng tóm tắt endpoint ở `docs/api-endpoints.md` §3, schema ở `docs/database-design.md` §2, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `CC-YCnn`, mã quy tắc `CC-Rnn`.

> **DRAFT** — dẫn xuất từ BA (bản Git HEAD) theo D-DOC-01, chưa được người phụ trách xác nhận. Chỗ BA khác `docs/decisions.md` viết theo `decisions.md` và ghi "BA khác".

---

## 1. Phạm vi

**Người phụ trách:** Khôi (workbook V2) · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Danh mục khóa học MOOC bên ngoài. Người dùng tìm kiếm, lọc, sắp xếp, xem chi tiết và các kỹ năng của một khóa học, rồi đi tới trang khóa học gốc. EduMentor chỉ lưu thông tin và đường link.

**Thuộc module:** `GET /api/courses` (kèm query), `GET /api/courses/{course_id}`, `GET /api/courses/{course_id}/skills`.

**Không thuộc module:** lưu khóa học (F03, `course-bookmark.md`); tham gia và trạng thái theo dõi (F04, `course-tracking.md`); quản trị khóa học (F11, `admin-course-skill.md`); bài ôn tập của khóa (F09); thông tin liên hệ của khóa (F10).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| CC-YC01 | Hiển thị thông tin khóa học: tên, nhà cung cấp, mô tả, liên kết truy cập và thông tin bổ sung nếu có lưu | FR-15 | — |
| CC-YC02 | Cung cấp liên kết tới trang khóa học bên ngoài; đăng ký, thanh toán và học diễn ra trên nền tảng đó | FR-16; §4.3; BR-05 (§5.5) | — |
| CC-YC03 | Tìm theo từ khóa, lọc theo cấp độ, sắp xếp theo điểm đánh giá hoặc số lượt đánh giá | §10.3 | — |
| CC-YC04 | Lọc theo kỹ năng | §10.3 | ND-72 (UI không có bộ lọc kỹ năng) |
| CC-YC05 | Xem các kỹ năng liên quan đến một khóa học | §10.3 | — |
| CC-YC06 | Người dùng đã đăng nhập mới xem được danh mục | UC-06 (tiền điều kiện) | ND-70 (quyền chưa chốt) |
| CC-YC07 | Lọc theo Budget, Tags, thời lượng, danh mục | Không có trong BA; chỉ có ở đề bài SRS v1.0 §2 | ND-61, ND-81: giữ hiện hành, chưa làm |

### Màn hình UI

`docs/ui-design/` (D-FE-12), chỉ mô tả giao diện:

| Màn | Route | Endpoint của module dùng | Ghi chú |
|---|---|---|---|
| Courses, Courses-Light | `/courses` | `GET /api/courses?search=&level=&sort_by=` | Có nút lưu của F03; không có bộ lọc kỹ năng (ND-72) |
| CourseDetail | `/courses/:courseId` | `GET /api/courses/{course_id}`, `GET /api/courses/{course_id}/skills` | Có trạng thái theo dõi của F04 |
| JoinDialog | `/courses/:courseId/join` | — (dùng `join` của F04) | Người phụ trách màn: **Chờ nhóm chốt** (workbook ghi Khôi, Tâm; endpoint của Hòa). Route: ND-50 |

---

## 2. File liên quan

Theo `docs/structure.md` §2, §3:

| Lớp | File |
|---|---|
| Router | `backend/app/routers/courses.py` |
| Service | `course_service` |
| Model (dùng) | `course.py`, `skill.py`, `course_skill.py` |
| Frontend | `api/courses.api.js`; `catalog/CatalogPage`, `catalog/CourseDetailPage` |

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §2.1–§2.3. Module chỉ đọc.

| Bảng | Dùng cho |
|---|---|
| `Course` | Danh sách, chi tiết, tìm, lọc `level`, sắp xếp `rating`, `num_reviews` |
| `Skill` | Tên kỹ năng của khóa |
| `CourseSkillRelation` | Kỹ năng của khóa; lọc theo `skill_id` |

---

## 4. Endpoint

Theo `docs/api-endpoints.md` §3. Request, response và mã lỗi **chưa được định nghĩa** trong tài liệu: `[NEEDS DECISION]`.

| Mã | Method | Endpoint | Mô tả | Quyền |
|---|---|---|---|---|
| EP-017 | GET | `/api/courses` | Danh mục; query `search`, `skill_id`, `level`, `sort_by=rating\|num_reviews`, có thể kết hợp | Chưa chốt (ND-70) |
| EP-018 | GET | `/api/courses/{course_id}` | Chi tiết một khóa học | Chưa chốt (ND-70) |
| EP-019 | GET | `/api/courses/{course_id}/skills` | Kỹ năng liên quan đến khóa học | Chưa chốt (ND-70) |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| CC-R01 | EduMentor chỉ lưu thông tin và đường link khóa học; không lưu nội dung, không quản lý việc đăng ký trên nền tảng ngoài. | `api-endpoints.md` §1; `database-design.md` §2.1; BA §4.3 |
| CC-R02 | Có thể kết hợp nhiều bộ lọc và tùy chọn sắp xếp bằng query parameter. | `api-endpoints.md` §3 |
| CC-R03 | `level` chỉ nhận `beginner`, `intermediate`, `advanced`; frontend chỉ đổi nhãn hiển thị. | `database-design.md` §2.1; D-FE-11 |
| CC-R04 | Danh sách có thể lớn thì hỗ trợ phân trang. | `api-endpoints.md` §14 |

---

## 6. Luồng nghiệp vụ

Không có luồng riêng ngoài đọc dữ liệu. Luồng khám phá khóa học từ lộ trình (BA UC-06) thuộc F07.

## 7. Transaction

Không có thao tác ghi.

## 8. Bảo mật

Quyền đọc danh mục: ND-70. Quy tắc xác thực chung: `docs/backend-rules.md`.

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F03 Lưu khóa học | Nút lưu, bỏ lưu trên Courses, CourseDetail |
| F04 Theo dõi tiến trình | Trạng thái của tôi và `join` trên CourseDetail, JoinDialog |
| F09 Ôn tập | Bài ôn tập tính theo khóa học (D01) |
| F10 Phản hồi | Màn Contact dùng `GET /api/courses` để chọn khóa |
| F11 Quản trị | Dữ liệu `Course`, `Skill`, `CourseSkillRelation` do Admin quản lý |

---

## 10. Câu hỏi mở

`ND-70` (quyền), `ND-72` (lọc kỹ năng), `ND-61`, `ND-77`, `ND-81` (yêu cầu của đề bài), `ND-50` (route JoinDialog) — chi tiết ở `docs/decisions.md` §4.4, §6.

Chưa có ND: người phụ trách màn JoinDialog; request, response, mã lỗi của §4.
