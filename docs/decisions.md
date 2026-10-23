# Quyết định & điểm chưa chốt — Xác thực/Hồ sơ và Ôn tập/Đánh giá

Đây là **nơi duy nhất** ghi quyết định nghiệp vụ và các điểm còn mở của 2 module:

- Xác thực & Hồ sơ người dùng (`docs/modules/auth-profile.md`)
- Ôn tập & Đánh giá kiến thức (`docs/modules/review-assessment.md`)

Các tài liệu khác chỉ tham chiếu mã (`D05`, `T13`, `ND-24`…), không chép lại nội dung. Khi một `ND-xx` được chốt: chuyển nó sang mục 2, sửa tài liệu bị ảnh hưởng, rồi mới code.

---

## 1. Nguồn sự thật

Thứ tự ưu tiên khi các nguồn khác nhau, cho 2 module trên:

1. `docs/EduMentor_Database_Design_Da_Sua.docx` và `docs/EduMentor_Checklist_Da_Sua_API.xlsx` (bản đã sửa, D01–D11 đã chốt) — **nguồn nghiệp vụ mới nhất**. Đã được chép vào `docs/database-design.md` và `docs/api-endpoints.md`.
2. `STRUCTURE.md` — nguồn kiến trúc nền (phân lớp Router → Service → Repository → Model, cây thư mục).
3. `CONVENTIONS.md`, `SETUP.md`, `README.md`.
4. Wireframe trong `docs/wireframes/` — chỉ mô tả giao diện; **không** tạo quy tắc API khi chưa có trong 1–3.

Không tự tạo quy tắc khi tài liệu chưa quy định → ghi `[NEEDS DECISION]` ở mục 4.

Hạng mục trong file `.xlsx` mà nhóm **chưa tick đồng ý** (☐) không được coi là đã chốt, kể cả khi file `.docx` đã ghi nội dung đó — xem mục 3.

---

## 2. Quyết định đã chốt (D01–D11)

Nguồn: sheet "Quyết định cần chốt" — tất cả đã tick "Đã chốt".

| Mã | Câu hỏi | Đã chọn | Ảnh hưởng tới module |
|---|---|---|---|
| D01 | Ôn tập theo khóa học hay kỹ năng? | **A — theo khóa học**: `/api/courses/{course_id}/review…`; 20 câu lấy từ các kỹ năng của khóa | Review |
| D02 | Điểm đạt tối thiểu? | **Khác — ≥ 60%** (biến `REVIEW_PASS_PERCENT`) | Review |
| D03 | Làm lại? Tiếp tục bài dở? | **A — không giới hạn**; mỗi khóa tối đa 1 bài đang dở; bắt đầu lại trả bài dở đó | Review |
| D04 | 20 câu lấy từ đâu khi khóa dạy nhiều kỹ năng? | **A — gộp câu của tất cả kỹ năng khóa dạy, tổng ≥ 20; chia đều giữa các kỹ năng** | Review |
| D05 | `UserSkill.status = learning` đặt khi nào? | **A — khi bấm Tham gia khóa (join)**: thêm kỹ năng của khóa ở `learning` nếu chưa `known` | Auth/Profile (bảng UserSkill) ↔ Course Tracking |
| D06 | Cho đổi email? | **A — không** (ô email chỉ đọc) | Auth/Profile |
| D07 | Ảnh đại diện: upload hay URL? | **B — tải file lên server** (`POST /api/me/avatar`); T04 ghi: giai đoạn 1 nhập URL qua `PATCH /api/me`, giai đoạn 2 upload | Auth/Profile |
| D08 | Đăng xuất hoạt động thế nào? | **A — JWT không lưu trạng thái**: client xóa token, server trả 200; không có bảng thu hồi token | Auth/Profile |
| D09 | Làm quên mật khẩu trong bản đầu? | **A — có** (T01, T02, T28) | Auth/Profile |
| D10 | Khóa đã completed có cho ôn lại? | **B — có**: kết quả mới chỉ lưu thêm vào lịch sử, không đổi `completed` | Review |
| D11 | Danh sách "Loại phản hồi" | A (ghi "không làm") | Ngoài phạm vi |

### Mâu thuẫn đã được giải quyết bằng quyết định trên

| Mã | Mâu thuẫn | Cách giải quyết |
|---|---|---|
| X1 | STRUCTURE/api-endpoints cũ: ôn tập theo kỹ năng; bản sửa: theo khóa học | D01 → theo khóa học. STRUCTURE và api-endpoints đã cập nhật |
| X2 | STRUCTURE cũ: `review_question.py`, `user_course.py`; CSDL: `Question`, `StudentCourse`, thêm `ReviewAnswer`, `PasswordResetToken` | Theo CSDL bản sửa. STRUCTURE đã cập nhật tên model |
| X3 | STRUCTURE §2 chỉ có register/login/logout, `/me`, `/me/skills` | Thêm forgot/reset/change-password, avatar, summary (T01–T05, đã tick) |
| X4 | STRUCTURE không có module email | Thêm `core/email.py` (T29, T01) |
| X5 | Sheet Endpoint ghi `POST .../review-attempts` → 409 khi "đã completed" | D10 = B thắng: khóa `completed` **được** ôn lại |
| X6 | T03 ghi sai mật khẩu hiện tại → "400/401"; `.docx` ghi 400 | Theo `.docx`: **400** |

---

## 3. Trạng thái hạng mục T (2 module)

Nguồn: sheet "Danh sách thay đổi". ☑ = nhóm đã đồng ý; ☐ = chưa.

| Mã | Hạng mục | Module | Nhóm đồng ý |
|---|---|---|---|
| T01 | `POST /api/auth/forgot-password` | Auth | ☑ |
| T02 | `POST /api/auth/reset-password` | Auth | ☑ |
| T03 | `POST /api/me/change-password` | Auth | ☑ |
| T04 | `PATCH /api/me` nhận `avatar_url`; `POST /api/me/avatar` | Auth | ☑ |
| T05 | `GET /api/me/summary` | Auth | ☑ (ghi chú nhóm: phần đếm "nhóm chưa chốt" → ND-13) |
| T06 | Body `PATCH /api/me/skills` | Auth | ☑ |
| T07 | `GET /api/me/skills?status=` | Auth | ☑ |
| T08 | `GET /api/me/courses?status=abandoned` | Course Tracking | ☑ |
| T09 | register không nhận role | Auth | ☑ |
| T10 | Sửa mẫu trang Profile (email chỉ đọc, đổi mật khẩu, quên mật khẩu) | Frontend | ☑ |
| T11 | Đổi endpoint ôn tập sang theo khóa học | Review | ☑ |
| T12 | Xóa `GET/PATCH /api/me/skills` khỏi §10 | Review | **☐** → ND-30 |
| T13 | Nộp bài trong một transaction | Review | ☑ (bước 5 "tạm thời chưa quyết định" → ND-24) |
| T14 | Chọn 20 câu, tạo sẵn 20 ReviewAnswer | Review | ☑ (thuật toán chi tiết → ND-20) |
| T15 | Không lộ đáp án; chỉ chủ sở hữu xem attempt (404) | Review | ☑ |
| T16 | Điều kiện bắt đầu và lỗi 409 | Review | **☐** — nhưng nội dung đã được D03, D10 và `.docx` 6.2 xác định; áp dụng theo `.docx` |
| T17 | review-history: bộ lọc và phân trang | Review | ☑ |
| T18 | Cập nhật LearningPath sau khi ôn tập đạt | Learning Path (Tâm) | **☐** → ND-24 |
| T19–T21 | Quản trị câu hỏi `/api/admin/questions*` | Admin | ☑ — **ngoài phạm vi skill Review**, chỉ là dependency dữ liệu |
| T26 | `Question.is_active` | Review (dữ liệu) | ☑ |
| T27 | `ReviewAttempt.submitted_at` | Review | **☐** → ND-31 |
| T28 | Biến môi trường SMTP_*, FRONTEND_URL, RESET_TOKEN_EXPIRE_MINUTES, REVIEW_PASS_PERCENT | Chung | ☑ |
| T29 | Email kết quả sau khi nộp bài | Review | ☑ (gửi mọi lần hay chỉ khi đạt → ND-25) |
| T22–T25 | Feedback & liên hệ | Ngoài phạm vi | ☐ → ND-35 |

---

## 4. Điểm chưa chốt — `[NEEDS DECISION]`

Không được tự chọn phương án cho các mục dưới đây. Khi gặp lúc implement: dừng lại và hỏi, hoặc chỉ làm phần không phụ thuộc vào mục đó.

### 4.1. Xác thực & Hồ sơ

| Mã | Câu hỏi | Bối cảnh / nguồn |
|---|---|---|
| ND-01 | Thuật toán ký JWT, payload (ví dụ có `role` không), cách gửi token (header `Authorization: Bearer` hay cookie)? | STRUCTURE chỉ ghi `security.py` "tạo/kiểm tra token"; frontend `client.js` "gắn token", `authStore (user, token)` |
| ND-02 | Thời hạn access token? `SETUP.md` có ví dụ `ACCESS_TOKEN_EXPIRE_MINUTES=60` — đây có phải giá trị chính thức? Ô "Ghi nhớ đăng nhập" (wireframe 01) có ảnh hưởng thời hạn không? | SETUP §3, wireframe 01 |
| ND-03 | Có refresh token không? | Không tài liệu nào nhắc |
| ND-04 | Thuật toán băm mật khẩu (bcrypt, argon2…)? | `.docx` 3.1 chỉ ghi "đã mã hóa" |
| ND-05 | Chính sách mật khẩu ở API (độ dài, độ phức tạp) cho register, reset-password, change-password? Wireframe 02 ghi "Tối thiểu 8 ký tự" và có ô "Nhập lại mật khẩu" — có phải rule của API không, hay chỉ kiểm tra ở giao diện? | Wireframe 02 |
| ND-06 | Có giới hạn số lần thử đăng nhập / gửi forgot-password không? | Không tài liệu nào nhắc |
| ND-07 | Email có chuẩn hóa (chữ thường, bỏ khoảng trắng) trước khi lưu/so sánh không? | `.docx`: email UQ |
| ND-08 | Register trả token (đăng nhập luôn) hay chỉ "201 + thông tin người dùng"? Wireframe 04 cho chọn kỹ năng ngay sau đăng ký — việc này cần đã xác thực. | Sheet Endpoint, wireframe 04 |
| ND-09 | Wireframe 04 "Chọn tối đa 3 kỹ năng" — có phải giới hạn của API (`PATCH /api/me/skills`) không? | Wireframe 04 |
| ND-10 | Wireframe Profile có ô "Mục tiêu học tập", nhưng `User` không có cột này và `PATCH /api/me` chỉ nhận `full_name`, `avatar_url`. Bỏ ô này hay lấy từ LearningPath.goal_text? | Wireframe Profile, `.docx` 3.1 |
| ND-11 | `PATCH /api/me/skills`: `update` hoặc `remove` một kỹ năng mà user chưa có → lỗi gì hay bỏ qua? Cùng `skill_id` xuất hiện ở nhiều khóa (`add` và `remove`)? User có được tự hạ kỹ năng do ôn tập ghi nhận từ `known` xuống `learning`? | T06 chỉ quy định skill không tồn tại → 404 |
| ND-12 | `POST /api/me/avatar`: dung lượng tối đa, định dạng cho phép, nơi lưu file, URL công khai? `avatar_url` nhập tay có kiểm tra định dạng URL không? | T04, `.docx` chỉ có mã 413/415 |
| ND-13 | `GET /api/me/summary`: ghi chú của nhóm ở T05 "Đếm từ StudentCourse, UserSkill, LearningPath (nhóm chưa chốt)" — cách đếm chính thức? | T05 |
| ND-18 | Client gửi trường không được phép (`role` ở register; `email`/`role` ở `PATCH /api/me`): bỏ qua hay trả 422? | T09, `.docx` 3.1: "không nhận" — chưa nói cách xử lý |
| ND-19 | Hình dạng response của login (tên trường token, có `token_type` không) và các trường thông tin người dùng đi kèm? | Sheet Endpoint: "access token + thông tin người dùng (gồm role)" |
| ND-36 | Do D08 (JWT stateless), token đã cấp vẫn hợp lệ sau khi đổi/đặt lại mật khẩu cho tới khi hết hạn. Nhóm có chấp nhận hệ quả này không? | Hệ quả của D08 + T02/T03 |
| ND-37 | `full_name` có bắt buộc khi đăng ký không? CSDL cho phép NULL, nhưng sheet Endpoint liệt kê nó trong body register và wireframe 02 có ô "Họ và tên". | `.docx` 3.1, sheet Endpoint |
| ND-38 | Wireframe Profile hiển thị nguồn của kỹ năng ("Từ bài ôn tập khóa học" / "Thêm thủ công"), nhưng `UserSkill` không có cột nguồn. Bỏ nhãn này trên giao diện hay bổ sung cột? | Wireframe Profile, `.docx` 3.2 |
| ND-39 | `forgot-password`: gửi email đồng bộ hay chạy nền? Nếu gửi lỗi thì vẫn trả thông báo chung (để không lộ email) và chỉ ghi log? Mã đã tạo có giữ lại không? | T01 chỉ quy định thông báo luôn giống nhau |

### 4.2. Ôn tập & Đánh giá

| Mã | Câu hỏi | Bối cảnh / nguồn |
|---|---|---|
| ND-20 | Thuật toán "chia đều giữa các kỹ năng": phần dư chia cho kỹ năng nào? Kỹ năng không đủ câu cho phần của nó thì bù từ kỹ năng khác thế nào? T14 ghi "lấy 60 câu ngẫu nhiên" — mâu thuẫn với `.docx` 6.3 ("chọn ngẫu nhiên 20 câu"). | G5 ví dụ 7 + 7 + 6; T14 |
| ND-21 | Có giới hạn thời gian làm bài không? Bài đang dở có hết hạn không? | Không tài liệu nào nhắc |
| ND-22 | `answers` khi nộp chứa `question_id` không thuộc attempt, hoặc trùng `question_id`: bỏ qua hay trả lỗi? | G5: "câu_id lạ bị bỏ qua hoặc báo lỗi" |
| ND-23 | Ôn lại khóa đã `completed` mà đạt: có upsert `UserSkill = known` lần nữa không? | `.docx` 6.2 bước 4 không phân biệt; D10 chỉ nói không đổi status/completed_at |
| ND-24 | Bước 5 của submit — kiểm tra LearningPath `ongoing` chứa kỹ năng vừa đạt và chuyển `completed` nếu mọi nút `is_required` đã known: có làm không, có nằm trong transaction submit không? Hàm do Tâm viết trong `learning_path_service` (T18 ☐). | T13, T18, G8 |
| ND-25 | Email kết quả gửi **mọi lần nộp** hay **chỉ khi đạt**? (Đề xuất trong ghi chú T29: mọi lần — chưa chốt.) | T29 |
| ND-26 | `GET /api/review-attempts/{attempt_id}` sau khi đã nộp trả gì (chỉ điểm, hay cả chi tiết)? `GET /api/me/review-history/{attempt_id}` với attempt chưa nộp trả gì (404, 409, hay chỉ trạng thái)? | Sheet Endpoint: "hoặc kết quả nếu đã nộp"; "(chỉ sau khi nộp)" |
| ND-27 | Wireframe 11/12 hiển thị "Mức: Mạnh ≥80% / Trung bình 50–79% / Yếu <50%", điểm dạng "x/20" và cột "Kỹ năng" (trong khi bài tính theo khóa học). Có phải trường của API không? Ngưỡng mức không khớp ngưỡng đạt 60%. | Wireframe 11, 12 |
| ND-28 | StudentCourse chuyển `abandoned` khi đang có bài dở: còn được nộp không? Khóa không có kỹ năng nào trong CourseSkillRelation: `GET .../review` trả lý do gì? | Không tài liệu nào nhắc |
| ND-29 | Đồng thời: hai request bắt đầu cùng lúc (có thể tạo hai bài dở), hai request nộp cùng lúc — dùng khóa dòng, unique index một phần, hay cách khác? | D03 "tối đa 1 bài dở", T16 "nộp lần hai → 409" |
| ND-30 | T12 (xóa `GET/PATCH /api/me/skills` lặp ở §10) chưa được tick. Tạm thời §10 chỉ ghi "xem §2". | T12 ☐ |
| ND-31 | T27 (`ReviewAttempt.submitted_at`) chưa được tick, nhưng `.docx` đã đưa cột vào và dùng nó cho email kết quả. Giữ cột này không? | T27 ☐, `.docx` 6.2 |
| ND-33 | `POST /api/courses/{course_id}/review-attempts` khi đã có bài dở và trả lại bài đó: mã 200 hay 201? Response có `attempted_at`, tên khóa học…? | D03 |
| ND-34 | `GET /api/me/review-history` có liệt kê cả bài đang dở (chưa có điểm) không? | `.docx` 6.2, T17 |

### 4.3. Kiến trúc dùng chung

| Mã | Câu hỏi | Bối cảnh / nguồn |
|---|---|---|
| ND-14 | Danh mục giá trị `error.code` (ngoài ví dụ `VALIDATION_ERROR`)? | CONVENTIONS §1 |
| ND-15 | Lỗi dữ liệu đầu vào dùng 400 hay 422? (Riêng các ca tài liệu đã ghi rõ mã — ví dụ reset-password 400, PATCH /me/skills 422 — thì theo tài liệu.) | CONVENTIONS: "400 / 422" |
| ND-16 | Lớp nào gọi `commit`/`rollback`: service, hay helper transaction trong `core/database.py`? | STRUCTURE: "service quản lý transaction"; `database.py` "transaction helper" |
| ND-17 | Index ngoài PK/UQ (ví dụ `ReviewAttempt(student_course_id)`, `Question(skill_id, is_active)`, `PasswordResetToken(user_id)`)? | `.docx` không liệt kê index |

### 4.4. Ngoài phạm vi 2 module (chỉ ghi nhận)

| Mã | Nội dung |
|---|---|
| ND-32 | STRUCTURE có `models/bookmark.py`, nhưng `.docx` 3.3 nói StudentCourse dùng cho cả bookmark, "không cần bảng riêng". Thuộc module Course Tracking. |
| ND-35 | Feedback & liên hệ (T22–T25) chưa được nhóm đồng ý; bảng Feedback/CourseContact có trong CSDL nhưng chưa có endpoint chính thức. |

---

## 5. Việc tồn đọng ngoài tài liệu (chưa làm ở giai đoạn này)

Theo sheet "File cần sửa" — chưa thực hiện vì không thuộc danh sách file của giai đoạn chuẩn bị tri thức:

- `.env.example` (đang rỗng) và `SETUP.md`: thêm `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `FRONTEND_URL`, `RESET_TOKEN_EXPIRE_MINUTES`, `REVIEW_PASS_PERCENT`. *(T28)*
- `README.md`: bảng "Tổng quan API" vẫn ghi `/api/skills/{id}/review*`.
- File code rỗng đã có sẵn trong `backend/` theo tên cũ (`models/review_question.py`, `models/user_course.py`) — đổi tên/tạo mới khi bắt đầu implement, theo `STRUCTURE.md`.
- `TASKS.md`, mẫu giao diện Profile (T10).
