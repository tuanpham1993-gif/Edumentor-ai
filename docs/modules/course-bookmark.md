# Module: Lưu khóa học — bookmark (F03)

Đặc tả nghiệp vụ của tính năng. Bảng tóm tắt endpoint ở `docs/api-endpoints.md` §4, schema ở `docs/database-design.md` §3.3, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `BM-YCnn`, mã quy tắc `BM-Rnn`.

> **DRAFT** — dẫn xuất từ BA (bản Git HEAD) theo D-DOC-01, chưa được người phụ trách xác nhận.

---

## 1. Phạm vi

**Người phụ trách:** Tâm (workbook V2, sheet chi tiết tính năng). Ba endpoint ở sheet đối chiếu endpoint lại ghi Khôi: **Chờ nhóm chốt**. · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Người dùng lưu khóa học quan tâm để xem lại, xem danh sách đã lưu và bỏ lưu. Bookmark là một trạng thái của bản ghi theo dõi khóa học, dùng chung bảng với F04.

**Thuộc module:** `POST /api/me/bookmarks`, `GET /api/me/bookmarks`, `DELETE /api/me/bookmarks/{course_id}`.

**Không thuộc module:** `GET /api/me/courses?status=bookmarked` và các trạng thái khác (F04, `course-tracking.md`); danh mục khóa học (F02).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| BM-YC01 | Lưu khóa học quan tâm để truy cập lại | FR-17; UC-07; §10.4 | — |
| BM-YC02 | Xem danh sách khóa học đã lưu | FR-17; §10.4 | ND-80 (hai cách lấy danh sách) |
| BM-YC03 | Bỏ lưu một khóa học | §10.4 | — |

### Màn hình UI

| Màn | Route | Endpoint của module dùng |
|---|---|---|
| Courses | `/courses` | `POST /api/me/bookmarks`, `DELETE /api/me/bookmarks/{course_id}` |
| CourseDetail | `/courses/:courseId` | `POST /api/me/bookmarks`, `DELETE /api/me/bookmarks/{course_id}` |
| MyCourses | `/me/courses` | `GET /api/me/bookmarks`, `DELETE /api/me/bookmarks/{course_id}`. Người phụ trách màn: **Chờ nhóm chốt** (workbook ghi Khôi, Hòa; `README.md` ghi Tâm, Hòa) |

---

## 2. File liên quan

Theo `docs/structure.md` §2:

| Lớp | File |
|---|---|
| Router | `backend/app/routers/me_courses.py` (dùng chung với F04) |
| Service | `course_tracking_service` (dùng chung với F04) |
| Model | `student_course.py` — không có bảng Bookmark riêng (ND-32) |
| Frontend | `api/courseTracking.api.js`; `tracking/MyCoursesPage` |

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §3.3.

| Bảng | Đọc / ghi | Dùng cho |
|---|---|---|
| `StudentCourse` | Ghi | Dòng `status = bookmarked` là một bookmark |
| `Course` | Đọc | Kiểm tra khóa tồn tại, thông tin hiển thị |

---

## 4. Endpoint

Theo `docs/api-endpoints.md` §4. Request, response và mã lỗi **chưa được định nghĩa**: `[NEEDS DECISION]`.

| Mã | Method | Endpoint | Mô tả | Quyền |
|---|---|---|---|---|
| EP-020 | POST | `/api/me/bookmarks` | Lưu một khóa học bằng `course_id` | Người dùng (`api-endpoints.md` §1, §14) |
| EP-021 | GET | `/api/me/bookmarks` | Danh sách khóa học đã lưu | Người dùng |
| EP-022 | DELETE | `/api/me/bookmarks/{course_id}` | Bỏ lưu | Người dùng |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| BM-R01 | Bookmark là dòng `StudentCourse` có `status = bookmarked`; không có bảng riêng. | `database-design.md` §3.3; ND-32 |
| BM-R02 | Mỗi người dùng và khóa học chỉ có một dòng `StudentCourse` (UNIQUE `user_id`, `course_id`). | `database-design.md` §3.3 |
| BM-R03 | Lưu: tạo dòng `bookmarked`; đã có dòng ở bất kỳ trạng thái nào thì không tạo thêm. | `database-design.md` §3.3 |
| BM-R04 | Bỏ lưu: chỉ xóa dòng khi đang `bookmarked`; trạng thái khác thì không xóa, không đổi. | `database-design.md` §3.3 |
| BM-R05 | Bỏ lưu không tự chuyển khóa học sang `abandoned`. | `api-endpoints.md` §4 quy tắc 3 |

---

## 6. Luồng nghiệp vụ

```text
Lưu:     POST /me/bookmarks {course_id} → đã có dòng StudentCourse? → giữ nguyên : tạo dòng bookmarked
Bỏ lưu:  DELETE /me/bookmarks/{course_id} → dòng đang bookmarked? → xóa dòng : không đổi
```

Phản hồi khi khóa không tồn tại hoặc khi lưu một khóa đã có dòng: `[NEEDS DECISION]`, chưa có ND.

## 7. Transaction

Mỗi thao tác ghi một dòng; không có ghi nhiều bảng.

## 8. Bảo mật

Chỉ thao tác trên dữ liệu của người dùng hiện tại (BA §4.3, FR-41).

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F04 Theo dõi tiến trình | Dùng chung bảng, router, service; `join` chuyển `bookmarked → ongoing` |
| F02 Danh mục | Nút lưu trên màn danh mục và chi tiết |
| F01 Hồ sơ | `GET /api/me/summary` đếm từ `StudentCourse` (ND-13) |

---

## 10. Câu hỏi mở

`ND-80` (giữ một hay cả hai cách lấy danh sách đã lưu), `ND-32` (bảng Bookmark) — `docs/decisions.md` §4.4.

Chưa có ND: người phụ trách EP-020 … EP-022 và màn MyCourses; request, response, mã lỗi của §4.
