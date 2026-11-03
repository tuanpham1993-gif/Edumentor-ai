# Module: Quản trị khóa học, kỹ năng và liên kết khóa học–kỹ năng (F11)

Đặc tả nghiệp vụ của tính năng. Bảng tóm tắt endpoint ở `docs/api-endpoints.md` §11, schema ở `docs/database-design.md` §2, §8.1, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `AD-YCnn`, mã quy tắc `AD-Rnn`.

> **DRAFT** — dẫn xuất từ BA (bản Git HEAD) theo D-DOC-01, chưa được người phụ trách xác nhận.

---

## 1. Phạm vi

**Người phụ trách:** Khôi (workbook V2). Bốn endpoint kỹ năng (EP-063 … EP-066) được ghi Khôi ở sheet đối chiếu endpoint, nhưng màn AdminSkills ghi Hòa: **Chờ nhóm chốt**. · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Admin quản lý danh mục khóa học, danh mục kỹ năng và liên kết giữa khóa học với kỹ năng — dữ liệu nền dùng cho danh mục, gợi ý, lộ trình và ôn tập.

**Thuộc module:** `/api/admin/courses*` (5), `/api/admin/skills*` (4), `/api/admin/course-skill-relations*` (3).

**Không thuộc module:** quan hệ giữa kỹ năng `/api/admin/skill-relations*` (F12); ngân hàng câu hỏi `/api/admin/questions*` (`admin-question-bank.md`); mẫu lộ trình, dữ liệu lịch sử.

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| AD-YC01 | Admin thêm, xem, cập nhật và quản lý kỹ năng dùng chung | FR-30; UC-11 | Xóa kỹ năng: ND-71 |
| AD-YC02 | Admin thêm, xem, cập nhật, xóa khóa học | FR-32; UC-13 | — |
| AD-YC03 | Admin quản lý liên kết khóa học–kỹ năng | FR-33; UC-13 | — |
| AD-YC04 | Chỉ Admin được thay đổi dữ liệu nền; kiểm tra quyền ở server | FR-40; BR-32; BR-34; §4.3 | — |
| AD-YC05 | Kiểm tra ràng buộc trước khi thêm, sửa, xóa để giữ nhất quán | BR-33 | — |

### Màn hình UI

| Màn | Route | Endpoint của module dùng |
|---|---|---|
| AdminCourses | `/admin/courses` | `GET`, `POST`, `PATCH`, `DELETE /api/admin/courses*`; liên kết kỹ năng |
| AdminSkills | `/admin/skills` | `GET`, `POST`, `DELETE /api/admin/skills*` (người phụ trách màn: Chờ nhóm chốt) |

---

## 2. File liên quan

Theo `docs/structure.md` §2, §3:

| Lớp | File |
|---|---|
| Router | `backend/app/routers/admin/courses.py`, `skills.py`, `course_skill_relations.py` |
| Service | `course_service` (theo `structure.md` §2) |
| Frontend | `api/admin.api.js`; `admin/AdminCoursesPage`, `admin/AdminSkillsPage` |

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §2.1–§2.3, khóa ngoại §8.1.

| Bảng | Đọc / ghi | Ràng buộc chính |
|---|---|---|
| `Course` | Ghi | `url` UQ; `level` ∈ beginner, intermediate, advanced; `rating` 0–5 |
| `Skill` | Ghi | `skill` NN UQ; không có `is_active` |
| `CourseSkillRelation` | Ghi | PK (`course_id`, `skill_id`) |

---

## 4. Endpoint

Theo `docs/api-endpoints.md` §11. Request, response và mã lỗi **chưa được định nghĩa**: `[NEEDS DECISION]`. Quyền: Admin.

| Mã | Method | Endpoint | Mô tả |
|---|---|---|---|
| EP-058 | GET | `/api/admin/courses` | Danh sách khóa học |
| EP-059 | POST | `/api/admin/courses` | Thêm khóa học |
| EP-060 | GET | `/api/admin/courses/{course_id}` | Chi tiết |
| EP-061 | PATCH | `/api/admin/courses/{course_id}` | Cập nhật |
| EP-062 | DELETE | `/api/admin/courses/{course_id}` | Xóa khỏi danh mục |
| EP-063 | GET | `/api/admin/skills` | Danh sách kỹ năng |
| EP-064 | POST | `/api/admin/skills` | Thêm kỹ năng |
| EP-065 | PATCH | `/api/admin/skills/{skill_id}` | Cập nhật kỹ năng |
| EP-066 | DELETE | `/api/admin/skills/{skill_id}` | Xóa khi không gây ảnh hưởng không mong muốn (ND-71) |
| EP-067 | GET | `/api/admin/course-skill-relations` | Danh sách liên kết |
| EP-068 | POST | `/api/admin/course-skill-relations` | Liên kết khóa học với kỹ năng |
| EP-069 | DELETE | `/api/admin/course-skill-relations/{course_id}/{skill_id}` | Xóa liên kết |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| AD-R01 | `/api/admin/*` chỉ dành cho quản trị viên; backend kiểm tra quyền, frontend chỉ ẩn giao diện. | `api-endpoints.md` §11, §14; D-FE-06 |
| AD-R02 | Tên kỹ năng không được trùng. | `database-design.md` §2.2 |
| AD-R03 | Xóa kỹ năng chỉ khi không gây ảnh hưởng không mong muốn; mọi khóa ngoại tới `Skill` là RESTRICT. Xóa mềm hay chặn xóa: ND-71. | `api-endpoints.md` §11; `database-design.md` §8.1 |
| AD-R04 | Khóa học đang có `StudentCourse` không xóa được (RESTRICT); xóa khóa học thì xóa liên kết kỹ năng, `Feedback`, `CourseContact` của khóa (CASCADE). | `database-design.md` §8.1 |
| AD-R05 | `url` của khóa học là duy nhất; `level` chỉ nhận ba giá trị; `rating` trong 0–5. | `database-design.md` §2.1 |
| AD-R06 | Mỗi cặp khóa học–kỹ năng chỉ có một liên kết. | `database-design.md` §2.3 |

---

## 6. Luồng nghiệp vụ

Thao tác CRUD theo §4. Phản hồi khi xóa bị chặn bởi RESTRICT: `[NEEDS DECISION]`, chưa có ND.

## 7. Transaction

Chưa ghi riêng; áp dụng `api-endpoints.md` §14 cho thao tác sửa nhiều bản ghi.

## 8. Bảo mật

AD-R01; BA BR-34. Người dùng thường vào `/admin/*`: ND-52.

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F02, F07 | Đọc `Course`, `Skill`, `CourseSkillRelation` |
| F09 Ôn tập | Kỹ năng của khóa quyết định nguồn câu hỏi và kỹ năng được ghi nhận |
| F04 | `join` thêm kỹ năng của khóa vào `UserSkill` |
| F12 | Quan hệ kỹ năng mở từ màn AdminSkills |
| F01 | `UserSkill` tham chiếu `Skill` (ND-57) |

---

## 10. Câu hỏi mở

`ND-71` (xóa kỹ năng), `ND-57` (học viên chọn kỹ năng từ đâu), `ND-52` — `docs/decisions.md` §4.

Chưa có ND: người phụ trách EP-063 … EP-066 và màn AdminSkills; phản hồi khi xóa bị chặn; request, response, mã lỗi.
