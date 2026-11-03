# Module: Theo dõi tiến trình khóa học (F04)

Đặc tả nghiệp vụ của tính năng. Bảng tóm tắt endpoint ở `docs/api-endpoints.md` §2 (nhóm `/api/me/courses`) và §4, schema ở `docs/database-design.md` §3.2, §3.3, quy ước chung ở `docs/conventions.md` và `docs/backend-rules.md` (hiện viết cho F01, F09), quyết định và điểm còn mở ở `docs/decisions.md`. Mục lục: `docs/modules/README.md`.

Mã yêu cầu `CT-YCnn`, mã quy tắc `CT-Rnn`.

> **DRAFT** — dẫn xuất từ BA (bản Git HEAD) theo D-DOC-01, chưa được người phụ trách xác nhận. Chỗ BA khác `docs/decisions.md` viết theo `decisions.md` và ghi "BA khác".

---

## 1. Phạm vi

**Người phụ trách:** Hòa (workbook V2) · **Đặc tả:** DRAFT · **Implementation:** NOT IMPLEMENTED

**Mô tả:** Theo dõi trạng thái học của người dùng với từng khóa học (`bookmarked`, `ongoing`, `completed`, `abandoned`): tham gia khóa học và mở trang khóa ngoài, xem trạng thái, đổi trạng thái được phép, ngừng theo dõi, xem lịch sử. Đây là trạng thái theo dõi của EduMentor, không phải trạng thái do nền tảng ngoài báo về.

**Thuộc module:** `GET /api/me/courses` (kèm `?status=`), `POST /api/courses/{course_id}/join`, `GET /api/me/courses/{course_id}/status`, `PATCH /api/me/courses/{course_id}/status`, `DELETE /api/me/courses/{course_id}`.

**Không thuộc module:** bookmark (F03, `course-bookmark.md`); ghi `completed` sau khi ôn tập đạt (F09, `review-assessment.md` RV-R14); gợi ý khóa học theo node (F07).

### Yêu cầu

| Mã | Yêu cầu | Nguồn BA | Quyết định |
|---|---|---|---|
| CT-YC01 | Cập nhật trạng thái khóa học theo các trạng thái được hỗ trợ | FR-18; UC-07 | **BA khác:** BA (FR-18, §4.1.1) cho người dùng tự đặt "đã hoàn thành"; theo D02, T13, khóa học chỉ thành `completed` khi làm đạt bài ôn tập (ND-76) |
| CT-YC02 | Xem thông tin tiến độ học tập của chính mình | FR-19 | T08 (xem cả `abandoned`) |
| CT-YC03 | Tham gia khóa học: ghi nhận `ongoing` và trả URL khóa ngoài | §10.4; FR-16 | D05 |
| CT-YC04 | Ngừng theo dõi: chuyển sang `abandoned`, không xóa lịch sử | §10.4 | — |
| CT-YC05 | Mở khóa học hay khai báo không đồng nghĩa đã thành thạo | BR-11; §10.4 quy tắc 6 | — |
| CT-YC06 | Đề xuất khóa học liên quan đến node của lộ trình | Không có trong BA §6.4; tên tính năng F04 trong `README.md` và workbook | Dùng chung endpoint của F07 (EP-043): **Chờ nhóm chốt**, chưa có ND |

### Màn hình UI

| Màn | Route | Endpoint của module dùng |
|---|---|---|
| CourseDetail | `/courses/:courseId` | `GET /api/me/courses/{course_id}/status` |
| JoinDialog | `/courses/:courseId/join` | `POST /api/courses/{course_id}/join` (người phụ trách màn: Chờ nhóm chốt; route: ND-50) |
| MyCourses | `/me/courses` | `GET /api/me/courses?status=`, `PATCH /api/me/courses/{course_id}/status`, `DELETE /api/me/courses/{course_id}` (người phụ trách màn: Chờ nhóm chốt) |
| Profile | `/me` | `GET /api/me/courses?status=` (màn của F01) |

---

## 2. File liên quan

Theo `docs/structure.md` §2, §3:

| Lớp | File |
|---|---|
| Router | `backend/app/routers/me_courses.py` (`/api/me/courses*`), `backend/app/routers/course_tracking.py` (`join`) |
| Service | `course_tracking_service` |
| Model | `student_course.py`; dùng `user_skill.py`, `course.py`, `course_skill.py` |
| Frontend | `api/courseTracking.api.js`; `tracking/MyCoursesPage` |

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §3.2, §3.3.

| Bảng | Đọc / ghi | Dùng cho |
|---|---|---|
| `StudentCourse` | Ghi | `status`, `joined_at`, `completed_at`, `updated_at` |
| `UserSkill` | Ghi (`learning`) | Khi `join` (bảng của F01) |
| `CourseSkillRelation` | Đọc | Kỹ năng của khóa khi `join` |
| `Course` | Đọc | URL khóa ngoài trả về khi `join` |

---

## 4. Endpoint

Theo `docs/api-endpoints.md` §2, §4. Request, response và mã lỗi **chưa được định nghĩa**: `[NEEDS DECISION]`.

| Mã | Method | Endpoint | Mô tả | Quyền |
|---|---|---|---|---|
| EP-023 | GET | `/api/me/courses` | Khóa đang theo dõi, mặc định loại `abandoned`; lọc `?status=ongoing\|bookmarked\|completed\|abandoned` | Người dùng |
| EP-024 | POST | `/api/courses/{course_id}/join` | Ghi `ongoing`, trả URL ngoài | Chưa ghi trong `api-endpoints.md` |
| EP-025 | GET | `/api/me/courses/{course_id}/status` | Trạng thái hiện tại | Người dùng |
| EP-026 | PATCH | `/api/me/courses/{course_id}/status` | Chuyển sang trạng thái được phép | Người dùng |
| EP-027 | DELETE | `/api/me/courses/{course_id}` | Chuyển `abandoned` | Người dùng |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| CT-R01 | Bốn trạng thái `bookmarked`, `ongoing`, `completed`, `abandoned` là trạng thái theo dõi của EduMentor. | `api-endpoints.md` §4; `database-design.md` §3.3 |
| CT-R02 | `join`: `bookmarked → ongoing` và ghi `joined_at`; chưa có dòng thì tạo mới ở `ongoing`. | `database-design.md` §3.3 |
| CT-R03 | `join` thêm các kỹ năng của khóa vào `UserSkill` ở `learning`; kỹ năng đã `known` giữ nguyên. | D05; `api-endpoints.md` §2; `database-design.md` §3.2 |
| CT-R04 | `join` không đăng ký khóa học thay người dùng trên nền tảng ngoài. | `api-endpoints.md` §4 quy tắc 2 |
| CT-R05 | Chuyển trạng thái: `bookmarked → ongoing`; `ongoing → completed \| abandoned`; `abandoned → ongoing`; `completed` giữ nguyên. | `database-design.md` §3.3 |
| CT-R06 | `completed` chỉ có khi làm đạt bài ôn tập của khóa (≥ `REVIEW_PASS_PERCENT`); việc ghi do F09 thực hiện. | D02, T13; `api-endpoints.md` §4 quy tắc 5; RV-R14, RV-R22 |
| CT-R07 | Không đánh dấu hoàn thành chỉ vì người dùng đã mở URL ngoài. | `api-endpoints.md` §4 quy tắc 6 |
| CT-R08 | `DELETE /api/me/courses/{course_id}` chỉ chuyển sang `abandoned`, không xóa dòng. | `api-endpoints.md` §4; `database-design.md` §3.3 |
| CT-R09 | `GET /api/me/courses` mặc định loại `abandoned`; xem lại bằng `?status=abandoned`. | T08; `database-design.md` §3.3 |
| CT-R10 | Ưu tiên đổi trạng thái thay vì xóa, để giữ lịch sử. | `api-endpoints.md` §14 |

`PATCH .../status` có được đặt `completed` không: CT-R05 liệt kê `ongoing → completed`, còn CT-R06 chỉ cho `completed` đến từ ôn tập. Danh sách chuyển trạng thái được phép **qua PATCH** chưa ghi riêng: `[NEEDS DECISION]`, chưa có ND.

---

## 6. Luồng nghiệp vụ

```text
Tham gia:   POST /courses/{id}/join
            → [transaction] StudentCourse: chưa có → tạo ongoing | bookmarked → ongoing (joined_at)
                            UserSkill: kỹ năng của khóa chưa known → learning
            → trả URL khóa ngoài; frontend mở URL
Ngừng:      DELETE /me/courses/{id} → status = abandoned
Hoàn thành: chỉ qua nộp bài ôn tập đạt (F09)
```

## 7. Transaction

| Thao tác | Các ghi trong cùng transaction | Nguồn |
|---|---|---|
| `join` | `StudentCourse` + `UserSkill` | `api-endpoints.md` §14 (thao tác sửa nhiều bản ghi liên quan) |

## 8. Bảo mật

Chỉ đọc, ghi dữ liệu theo dõi của người dùng hiện tại (BA §4.3, FR-41).

---

## 9. Phụ thuộc với module khác

| Module | Nội dung |
|---|---|
| F03 Lưu khóa học | Dùng chung bảng, router, service |
| F09 Ôn tập | Đọc trạng thái để cho bắt đầu bài; ghi `completed` khi đạt |
| F01 Hồ sơ | Ghi `UserSkill` khi `join`; `GET /api/me/summary` đếm `StudentCourse` (ND-13) |
| F07 Gợi ý khóa học | CT-YC06 dùng chung EP-043 |

---

## 10. Câu hỏi mở

`ND-76` (lời văn BA về `completed`), `ND-80`, `ND-32`, `ND-28` (chuyển `abandoned` khi đang có bài ôn dở), `ND-50` — `docs/decisions.md` §4.

Chưa có ND: chuyển trạng thái được phép qua PATCH; phạm vi CT-YC06 và người làm; quyền của `join`; người phụ trách màn JoinDialog, MyCourses; request, response, mã lỗi của §4.
