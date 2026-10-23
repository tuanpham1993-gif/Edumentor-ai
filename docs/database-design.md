# EduMentor AI — Thiết kế cơ sở dữ liệu

> **Nguồn:** chép từ `docs/EduMentor_Database_Design_Da_Sua.docx` (bản đã sửa, các quyết định D01–D11 đã chốt). Đây là tài liệu CSDL chính thức của project. Không thêm bảng, cột, ràng buộc hay quan hệ ngoài nội dung dưới đây; mọi thay đổi phải ghi vào `docs/decisions.md` trước rồi mới sửa file này và tạo Alembic migration.
>
> Mã trong ngoặc như *(T13, D05)* trỏ tới hạng mục trong `docs/EduMentor_Checklist_Da_Sua_API.xlsx`. Điểm còn mở được đánh dấu `[NEEDS DECISION ND-xx]`, chi tiết ở `docs/decisions.md`.

Hệ quản trị: **PostgreSQL**. Ký hiệu: **PK** khóa chính, **FK** khóa ngoại, **UQ** không được trùng, **NN** không được để trống.

Tên bảng viết theo kiểu đặc tả (ví dụ `LearningPathNode`); khi tạo bảng thật có thể đổi sang chữ thường có gạch dưới (`learning_path_node`). Riêng `User` trùng từ khóa của PostgreSQL nên bảng thật đặt là `users`.

---

## 1. Tổng quan

Cơ sở dữ liệu gồm **21 bảng** chia thành 6 nhóm. Hai nguyên tắc thiết kế:

1. Các bảng liên quan tới dataset giữ đúng tên bảng và tên cột của dataset (riêng `Course` có thêm 1 cột ảnh).
2. Các bảng còn lại bám theo đặc tả API và SRS của nhóm (`LearningPathNode`, `LearningPathEdge`, `ReviewAttempt`…).

| Nhóm | Bảng | Thiết kế theo | Vai trò chung |
|---|---|---|---|
| A. Theo dataset | Course, Skill, CourseSkillRelation, SkillRelation | 4 file dataset | Kho khóa học, kỹ năng, khóa học dạy kỹ năng nào, kỹ năng nào học trước kỹ năng nào |
| B. Người dùng | User, UserSkill, StudentCourse, PasswordResetToken | Đặc tả API (mục 2, 4) | Tài khoản, kỹ năng đã có, theo dõi khóa học với 4 trạng thái, mã đặt lại mật khẩu qua email |
| C. Lộ trình | BaseLearningPath, BaseLearningPathNode, BaseLearningPathEdge, LearningPath, LearningPathNode, LearningPathEdge | SRS và API mục 5, 6, 7, 12 | Mẫu lộ trình do admin quản lý và lộ trình cá nhân dạng đồ thị kỹ năng |
| D. Chatbot | ChatSession, ChatMessage | API mục 9 | Phiên trò chuyện (gia sư AI, tư vấn lộ trình) và tin nhắn |
| E. Ôn tập | Question, ReviewAttempt, ReviewAnswer | SRS (ReviewAttempt) và API mục 10 | Ngân hàng câu hỏi, các lần làm bài ôn tập và kết quả từng câu |
| F. Phản hồi và liên hệ | Feedback, CourseContact | Màn hình "Liên hệ & góp ý" | Phản hồi của học viên và thông tin liên hệ từng khóa học |

### Nguồn dữ liệu

| Dataset | Bảng | Ghi chú xử lý khi nạp |
|---|---|---|
| course_table | Course | Giữ đủ 12 cột, thêm `image_url` (để trống tới khi bổ sung). Chuyển `num_enrolled` ("5,710") và `rating` (chuỗi) sang số, `num_reviews` (27.0) sang số nguyên, lấy số từ "4 modules" cho `modules`, sửa `intermidiate` thành `intermediate` |
| skill_table | Skill | Giữ nguyên 2 cột |
| course_skill_relation | CourseSkillRelation | Giữ `course_id`, `skill_id`. Hai cột `title`, `skill` là bản sao tên (lấy bằng JOIN) nên không lưu |
| skill_relation | SkillRelation | Giữ `from_skill_id`, `to_skill_id`, `relation_type`. Hai cột tên kỹ năng là bản sao nên không lưu. Cần xác nhận chiều của quan hệ |

---

## 2. Nhóm A — Bảng theo dataset

Chỉ có một cột thêm ngoài dataset là `Course.image_url`.

### 2.1. Course

Kho khóa học: tìm kiếm, lọc theo kỹ năng và level, sắp xếp theo rating hoặc num_reviews; nguồn khóa học để gợi ý cho từng nút kỹ năng. EduMentor chỉ lưu thông tin và đường link, không lưu nội dung khóa học.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| course_id | INT | PK | Mã khóa học (giữ nguyên mã trong dataset) |
| title | VARCHAR(500) | NN | Tên khóa học |
| num_enrolled | INT | DEFAULT 0 | Số người đã đăng ký học |
| rating | NUMERIC(2,1) | CHECK 0–5 | Điểm đánh giá trung bình |
| num_reviews | INT | DEFAULT 0 | Số lượt đánh giá |
| instructor | VARCHAR(255) | | Tên giảng viên |
| organization | VARCHAR(255) | | Đơn vị cung cấp khóa học |
| description | TEXT | | Mô tả nội dung khóa học |
| modules | INT | | Số chương (lấy số từ "4 modules") |
| level | VARCHAR(20) | CHECK (beginner, intermediate, advanced) | Độ khó |
| schedule | VARCHAR(255) | | Thời gian học, chép nguyên văn từ dataset |
| url | VARCHAR(500) | UQ | Link khóa học gốc trên Coursera |
| image_url | VARCHAR(500) | NULL | Ảnh đại diện khóa học (cột thêm ngoài dataset) |

### 2.2. Skill

Danh mục kỹ năng — "ngôn ngữ chung" nối khóa học, hồ sơ học viên, lộ trình và câu hỏi ôn tập.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| skill_id | INT | PK | Mã kỹ năng (giữ nguyên mã trong dataset) |
| skill | VARCHAR(255) | NN, UQ | Tên kỹ năng, không được trùng |

### 2.3. CourseSkillRelation

Mỗi khóa học dạy những kỹ năng nào (N–N). Dùng để tìm khóa học cho một kỹ năng và để xác định kỹ năng của một khóa khi ôn tập.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| course_id | INT | PK, FK → Course | Khóa học |
| skill_id | INT | PK, FK → Skill | Kỹ năng mà khóa học dạy |

### 2.4. SkillRelation

Quan hệ giữa các kỹ năng, dùng chung toàn hệ thống (khác `LearningPathEdge` là kết nối trong một lộ trình cụ thể).

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| from_skill_id | INT | PK, FK → Skill | Kỹ năng cần học trước (đầu mũi tên) |
| to_skill_id | INT | PK, FK → Skill, CHECK khác from_skill_id | Kỹ năng học sau |
| relation_type | VARCHAR(15) | NN, DEFAULT 'prerequisite', CHECK (prerequisite, extension, related) | prerequisite có trong dataset; extension, related do admin thêm qua API |

Lưu ý: quy ước hướng cạnh là kỹ năng bắt đầu được học trước kỹ năng đích. Chỉ quan hệ `prerequisite` phải tạo thành đồ thị không có vòng, kiểm tra khi nạp dữ liệu và khi admin thêm quan hệ. Cần kiểm tra dataset có cùng chiều này không.

---

## 3. Nhóm B — Người dùng

EduMentor chỉ theo dõi tiến trình học ở mức cơ bản, không theo dõi từng bài học hay tiến độ xem video.

### 3.1. User

Lưu tài khoản và vai trò. Là gốc của mọi dữ liệu cá nhân. Phục vụ đăng ký, đăng nhập, đăng xuất, `GET/PATCH /api/me`, `POST /api/me/change-password`, `POST /api/me/avatar`, `GET /api/me/summary`. *(T03, T04, T05)*

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| user_id | SERIAL | PK | Mã tài khoản |
| email | VARCHAR(255) | NN, UQ | Email đăng nhập; mỗi email một tài khoản. **Không cho đổi email**: `PATCH /api/me` không nhận trường này *(D06, T10)* |
| hashed_password | VARCHAR(255) | NN | Mật khẩu đã băm. Không lưu mật khẩu gốc, không trả trong response. Đổi bằng `POST /api/me/change-password` (sai mật khẩu hiện tại → 400) hoặc luồng `POST /api/auth/reset-password` *(T02, T03)* |
| full_name | VARCHAR(100) | | Tên hiển thị |
| avatar_url | VARCHAR(500) | NULL | Ảnh đại diện. Đặt bằng `PATCH /api/me` (nhập đường dẫn) hoặc `POST /api/me/avatar` (tải file; quá lớn → 413, sai định dạng → 415) *(T04, D07)* |
| role | VARCHAR(10) | NN, DEFAULT 'student', CHECK (student, admin) | `POST /api/auth/register` luôn tạo student (không nhận role từ client); admin chỉ tạo bằng `scripts/create_admin.py`; `PATCH /api/me` không cho sửa role *(T09)* |
| created_at | TIMESTAMP | DEFAULT now() | Ngày tạo tài khoản |

Quy tắc *(D08, T04, T05)*:
- Đăng xuất (`POST /api/auth/logout`): JWT không lưu trạng thái, client xóa token, server trả 200. Không có bảng lưu token bị thu hồi.
- `PATCH /api/me` chỉ nhận `full_name` và `avatar_url`.
- `GET /api/me/summary` trả `ongoing_courses`, `completed_courses` (đếm StudentCourse theo status), `known_skills` (UserSkill status = known), `ongoing_paths` (LearningPath status = ongoing). `[NEEDS DECISION ND-13]`

### 3.2. UserSkill

Hồ sơ kỹ năng của học viên. Phục vụ `GET /api/me/skills` (lọc `?status=known|learning`) và `PATCH /api/me/skills`. Backend tự cập nhật khi học viên tham gia khóa học và khi làm đạt bài ôn tập; học viên cũng có thể tự thêm, sửa, xóa. Lộ trình dùng bảng này để biết kỹ năng nào học viên đã có. *(T07, D05)*

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| user_id | INT | PK, FK → User | Học viên |
| skill_id | INT | PK, FK → Skill | Kỹ năng |
| status | VARCHAR(10) | NN, DEFAULT 'known', CHECK (learning, known) | learning: ghi khi học viên bấm tham gia một khóa dạy kỹ năng này (nếu chưa known) hoặc tự đặt; known: ghi khi làm đạt bài ôn tập của khóa hoặc tự đặt. Một nút lộ trình chỉ tính là xong khi kỹ năng ở trạng thái known *(D05)* |
| updated_at | TIMESTAMP | DEFAULT now() | Lần cập nhật gần nhất |

Quy tắc *(T06, D05, T13)*:
- `PATCH /api/me/skills` nhận `{"add":[{"skill_id":12,"status":"known"}], "update":[{"skill_id":5,"status":"learning"}], "remove":[7]}`. Ba khóa đều tùy chọn; status chỉ nhận `learning` hoặc `known`.
- Cả request chạy trong **một transaction**: một phần lỗi thì hủy toàn bộ. `skill_id` phải có trong Skill (không có → 404). `add` một kỹ năng đã có thì coi là cập nhật (upsert theo `(user_id, skill_id)`), không báo lỗi trùng.
- Tham gia khóa (`POST /api/courses/{course_id}/join`): thêm các kỹ năng của khóa (qua CourseSkillRelation) ở trạng thái learning; kỹ năng đã known giữ nguyên.
- Nộp bài ôn tập đạt: thêm hoặc cập nhật known cho mọi kỹ năng của khóa (xem 6.2).

### 3.3. StudentCourse

Theo dõi quan hệ học viên – khóa học cho cả 4 trạng thái (`bookmarked`, `ongoing`, `completed`, `abandoned`), nên không cần bảng riêng cho danh sách đã lưu. Đây là trạng thái theo dõi của EduMentor, không phải trạng thái trên nền tảng MOOC.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| student_course_id | SERIAL | PK | Mã bản ghi theo dõi |
| user_id | INT | NN, FK → User | Học viên |
| course_id | INT | NN, FK → Course | Khóa học |
| status | VARCHAR(12) | NN, CHECK (bookmarked, ongoing, completed, abandoned) | completed chỉ tính khi làm xong bài ôn tập, không phải vì mở link |
| joined_at | TIMESTAMP | NULL | Lúc bấm tham gia |
| completed_at | TIMESTAMP | NULL | Lúc hoàn thành |
| updated_at | TIMESTAMP | DEFAULT now() | Lần đổi trạng thái gần nhất |

Ràng buộc bổ sung: **UNIQUE (user_id, course_id)**.

Quy tắc:
- Lưu khóa học: tạo dòng `bookmarked`; đã có dòng (bất kỳ trạng thái) thì không tạo thêm.
- Bỏ lưu: chỉ xóa dòng khi đang `bookmarked`; trạng thái khác thì không xóa, không đổi.
- Tham gia: `bookmarked → ongoing` và ghi `joined_at`; chưa có dòng thì tạo mới ở `ongoing`. Đồng thời thêm kỹ năng của khóa vào UserSkill ở `learning` (3.2). *(D05)*
- `DELETE /api/me/courses/{course_id}` chỉ chuyển sang `abandoned`, không xóa dòng.
- `GET /api/me/courses` mặc định loại `abandoned`; lọc `?status=ongoing|bookmarked|completed|abandoned`. *(T08)*
- Chuyển trạng thái: `bookmarked → ongoing`; `ongoing → completed | abandoned`; `abandoned → ongoing`; `completed` giữ nguyên. Được làm bài ôn tập khi khóa đang `ongoing`, hoặc đã `completed` (ôn lại); ôn lại chỉ lưu thêm vào lịch sử, không đổi status và completed_at. *(D10)*

### 3.4. PasswordResetToken

Hỗ trợ quên mật khẩu bằng email (làm trong phiên bản đầu). Mỗi mã chỉ dùng một lần và có thời hạn. Phục vụ `POST /api/auth/forgot-password` và `POST /api/auth/reset-password`. *(D09, T01, T02)*

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| reset_id | SERIAL | PK | Mã yêu cầu |
| user_id | INT | NN, FK → User | Tài khoản yêu cầu |
| token_hash | VARCHAR(255) | NN, UQ | Bản băm của mã đặt lại; không lưu mã gốc |
| expires_at | TIMESTAMP | NN | Lúc tạo + `RESET_TOKEN_EXPIRE_MINUTES` (cấu hình .env, đề xuất 15–30 phút) *(T28)* |
| used_at | TIMESTAMP | NULL | Lúc đã dùng; trống = chưa dùng |
| created_at | TIMESTAMP | DEFAULT now() | Lúc tạo |

Luồng xử lý:
1. `POST /api/auth/forgot-password` `{"email": "..."}`: tìm User theo email; nếu có thì tạo mã ngẫu nhiên, lưu bản băm vào `token_hash`, gửi email chứa link kèm mã (dùng `FRONTEND_URL` và `app/core/email.py`). Dù email có tồn tại hay không đều trả **cùng một thông báo**. *(T01)*
2. `POST /api/auth/reset-password` `{"token": "...", "new_password": "..."}`: băm mã nhận được, tìm dòng khớp `token_hash`, kiểm tra chưa hết hạn và `used_at` trống. Sai, hết hạn hoặc đã dùng → 400. *(T02)*
3. Hợp lệ: cập nhật `User.hashed_password`, ghi `used_at`, vô hiệu các mã cũ chưa dùng của tài khoản.

Cấu hình cần có: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `FRONTEND_URL`, `RESET_TOKEN_EXPIRE_MINUTES`. *(T28)*

---

## 4. Nhóm C — Lộ trình

Lộ trình là một đồ thị kỹ năng: mỗi nút (`LearningPathNode`) là một kỹ năng, mỗi cạnh (`LearningPathEdge`) là kết nối "học trước, học sau". Ba bảng `BaseLearningPath*` là mẫu do admin quản lý.

### 4.1. BaseLearningPath

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| template_id | SERIAL | PK | Mã mẫu |
| name | VARCHAR(100) | NN, UQ | Tên mẫu, ví dụ "Backend AI" |
| description | TEXT | | Mô tả mẫu dành cho ai |
| is_active | BOOLEAN | NN, DEFAULT TRUE | Mẫu đã có người dùng thì chỉ tắt, không xóa |
| created_at | TIMESTAMP | DEFAULT now() | |
| updated_at | TIMESTAMP | DEFAULT now() | |

### 4.2. BaseLearningPathNode

Cấu trúc giống `LearningPathNode`, bỏ cột `added_by` vì mẫu luôn do admin tạo.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| template_id | INT | PK, FK → BaseLearningPath | |
| skill_id | INT | PK, FK → Skill | |
| node_role | VARCHAR(15) | NULL, CHECK (prerequisite, optional, extension) | Để trống nếu nút là kỹ năng mục tiêu |
| is_target | BOOLEAN | NN, DEFAULT FALSE | Kỹ năng mục tiêu chính của mẫu |
| is_required | BOOLEAN | NN, DEFAULT TRUE | Bắt buộc phải học |
| display_order | INT | NN | Thứ tự hiển thị (1000, 2000… để chèn giữa) |

### 4.3. BaseLearningPathEdge

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| template_id | INT | PK | |
| from_skill_id | INT | PK | Học trước |
| to_skill_id | INT | PK | Học sau |
| relation_type | VARCHAR(15) | NN, CHECK (prerequisite, optional) | |

Ràng buộc bổ sung: FK tổng hợp `(template_id, from_skill_id)` và `(template_id, to_skill_id)` cùng tham chiếu `BaseLearningPathNode(template_id, skill_id)`.

### 4.4. LearningPath

Lưu khi học viên chấp nhận bản đề xuất (`POST /api/learning-paths`); bản đề xuất từ `POST /api/chat/learning-path` chưa lưu.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| path_id | SERIAL | PK | |
| user_id | INT | NN, FK → User | |
| template_id | INT | NULL, FK → BaseLearningPath | Mẫu đã dùng (nếu có) |
| goal_text | TEXT | NN | Câu mục tiêu học viên nhập |
| status | VARCHAR(10) | NN, DEFAULT 'ongoing', CHECK (ongoing, completed, abandoned) | completed = tất cả nút bắt buộc đã hoàn thành hoặc được công nhận đã biết |
| created_at | TIMESTAMP | DEFAULT now() | |
| updated_at | TIMESTAMP | DEFAULT now() | |

Quy tắc: `DELETE /api/learning-paths/{path_id}` chỉ chuyển sang `abandoned`.

### 4.5. LearningPathNode

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| path_id | INT | PK, FK → LearningPath | |
| skill_id | INT | PK, FK → Skill | Một kỹ năng chỉ xuất hiện một lần trong một lộ trình |
| node_role | VARCHAR(15) | NULL, CHECK (prerequisite, optional, extension) | Để trống nếu nút chỉ là kỹ năng mục tiêu |
| is_target | BOOLEAN | NN, DEFAULT FALSE | Kỹ năng được chọn trực tiếp từ mục tiêu; tách khỏi node_role |
| added_by | VARCHAR(10) | NN, DEFAULT 'system', CHECK (system, user) | |
| is_required | BOOLEAN | NN, DEFAULT TRUE | Bắt buộc để hoàn thành lộ trình |
| display_order | INT | NN | Chỉ để sắp xếp, không quyết định tiên quyết |

Quy tắc: xóa một nút phải xóa luôn các cạnh liên quan, trong cùng một transaction.

### 4.6. LearningPathEdge

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| path_id | INT | PK | |
| from_skill_id | INT | PK | Học trước; phải là nút trong cùng lộ trình |
| to_skill_id | INT | PK | Học sau; phải là nút trong cùng lộ trình |
| relation_type | VARCHAR(15) | NN, CHECK (prerequisite, optional) | |

Ràng buộc bổ sung:
- FK tổng hợp `(path_id, from_skill_id)` và `(path_id, to_skill_id)` cùng tham chiếu `LearningPathNode(path_id, skill_id)`.
- Với `prerequisite`, kỹ năng bắt đầu được học trước kỹ năng đích.
- Hoàn thành lộ trình dựa trên tiến độ các nút bắt buộc, không dựa vào việc đi tới một nút kết thúc.

---

## 5. Nhóm D — Chatbot

### 5.1. ChatSession

Luôn gắn với người dùng đã đăng nhập; học viên A không đọc được phiên của học viên B.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| session_id | UUID | PK | Mã phiên (khó đoán) |
| user_id | INT | NN, FK → User | |
| session_type | VARCHAR(15) | NN, DEFAULT 'tutor', CHECK (tutor, learning_path) | |
| topic | VARCHAR(255) | | |
| status | VARCHAR(10) | NN, DEFAULT 'active', CHECK (active, archived) | `DELETE /api/chat/sessions/{session_id}` chuyển sang archived |
| created_at | TIMESTAMP | DEFAULT now() | |
| updated_at | TIMESTAMP | DEFAULT now() | |

### 5.2. ChatMessage

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| message_id | BIGSERIAL | PK | |
| session_id | UUID | NN, FK → ChatSession | |
| role | VARCHAR(10) | NN, CHECK (user, assistant) | |
| content | TEXT | NN | |
| created_at | TIMESTAMP | DEFAULT now() | |

Lưu ý: API chưa có endpoint chấm sao/phản hồi tin nhắn nên chưa có cột cho việc này.

---

## 6. Nhóm E — Ôn tập

Bài ôn tập tính **theo khóa học** *(D01 = A, T11)*: mỗi bài gồm **20 câu trắc nghiệm** lấy từ các kỹ năng mà khóa đó dạy; làm đạt thì khóa chuyển `completed`. Endpoint: `GET /api/courses/{course_id}/review`, `POST /api/courses/{course_id}/review-attempts`, `GET /api/review-attempts/{attempt_id}`, `POST /api/review-attempts/{attempt_id}/submit` (thay cho các endpoint cũ theo kỹ năng `/api/skills/{skill_id}/review…`).

### 6.1. Question

Ngân hàng câu hỏi trắc nghiệm theo kỹ năng. Một khóa có bài ôn tập khi **tổng số câu `is_active = true` của tất cả kỹ năng khóa dạy** (qua CourseSkillRelation) **≥ 20**; không cần mỗi kỹ năng đủ 20 câu riêng *(D04 = A)*. `GET /api/courses/{course_id}/review` kiểm tra điều kiện này và trả `available = false` kèm lý do nếu thiếu. Admin quản lý câu hỏi qua `/api/admin/questions`. *(T11, T19)*

> Tên model trong code: `question.py` (thay cho `review_question.py` cũ trong STRUCTURE).

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| question_id | SERIAL | PK | |
| skill_id | INT | NN, FK → Skill | Kỹ năng câu hỏi kiểm tra |
| content | TEXT | NN | Nội dung câu hỏi |
| options | JSONB | NN | Danh sách đáp án — **đúng 4 đáp án** *(T19, T21)* |
| correct_index | SMALLINT | NN, CHECK 0–3 | Đáp án đúng (0 là đáp án đầu). **Không trả ở bất kỳ endpoint làm bài nào trước khi nộp**; chỉ xuất hiện ở `GET /api/me/review-history/{attempt_id}` sau khi nộp *(T15)* |
| explanation | TEXT | | Giải thích; như correct_index, chỉ trả sau khi nộp *(T15)* |
| is_active | BOOLEAN | NN, DEFAULT TRUE | TRUE = được chọn vào bài mới; câu đã dùng không xóa được, chỉ đặt FALSE *(T26)* |

Quy tắc quản trị câu hỏi (chỉ admin) *(T19, T20, T21)*: CRUD `/api/admin/questions`; `DELETE` câu chưa từng có trong ReviewAnswer → xóa thật, đã có → `is_active = false` (FK ReviewAnswer → Question là RESTRICT); import CSV/JSON tùy chọn.

### 6.2. ReviewAttempt

Lưu mọi lần học viên làm bài: đã làm chưa, làm mấy lần, điểm bao nhiêu, đạt hay chưa. Phục vụ `GET /api/me/review-history` (lọc `?course_id=`, `?passed=true|false`, phân trang `?page=&page_size=`). *(T17)*

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| attempt_id | SERIAL | PK | |
| student_course_id | INT | NN, FK → StudentCourse | Qua đây biết học viên và khóa học |
| score_percent | NUMERIC(5,2) | NULL, CHECK 0–100 | Điểm phần trăm; trống khi chưa nộp |
| passed | BOOLEAN | NULL | Đạt khi `score_percent ≥ REVIEW_PASS_PERCENT` (nhóm chốt **60%**, đọc từ cấu hình). Lưu riêng để đổi mức đạt không làm đổi kết quả cũ. Trống khi chưa nộp *(D02, T28)* |
| attempted_at | TIMESTAMP | NN, DEFAULT now() | Lúc bắt đầu (gọi `POST /api/courses/{course_id}/review-attempts`) *(T27)* |
| submitted_at | TIMESTAMP | NULL | Lúc nộp; trống = đang làm dở *(T27 — nhóm chưa tick đồng ý: `[NEEDS DECISION ND-31]`)* |

Cách dùng:
- **Số lần làm bài**: đếm theo `student_course_id`. Làm lại **không giới hạn**; mỗi khóa tối đa **một bài đang dở**; gọi bắt đầu lại thì trả về bài dở đó. *(D03 = A)*
- **Nộp bài** (`POST /api/review-attempts/{attempt_id}/submit`, body `answers: [{question_id, selected_index}]`) chạy trong **một transaction** *(T13)*:
  1. Chấm từng câu, ghi ReviewAnswer.
  2. Ghi `score_percent`, `passed`, `submitted_at`.
  3. Nếu đạt: `StudentCourse.status → completed` và ghi `completed_at` (khóa đã completed thì giữ nguyên).
  4. Nếu đạt: thêm/cập nhật `UserSkill = known` cho mọi kỹ năng của khóa (qua CourseSkillRelation).
  
  Bước nào lỗi thì hủy toàn bộ.
- Bước (5) kiểm tra lại các LearningPath `ongoing` chứa kỹ năng vừa đạt (mọi nút `is_required` đã known → `completed`): **nhóm chưa chốt** `[NEEDS DECISION ND-24]`. *(T13, T18)*
- Sau khi commit thành công: trả ngay `score_percent`, `passed`, số câu đúng; rồi chạy nền (FastAPI BackgroundTasks) gửi email kết quả tới `User.email` gồm tên khóa học, điểm %, Đạt/Không đạt, số câu đúng/20, thời gian nộp, link `FRONTEND_URL/review/history/{attempt_id}` (không kèm đáp án). Gửi email nằm ngoài transaction: lỗi chỉ ghi log, không rollback, không báo lỗi cho học viên. Dùng chung `app/core/email.py`. *(T29)*
- **Điều kiện bắt đầu**: phải có StudentCourse ở `ongoing` hoặc `completed` (ôn lại). Chưa có hoặc chưa tham gia → 409 (hướng dẫn bấm "Tham gia"); khóa thiếu câu hỏi → 409; nộp lần hai → 409. *(T16, D10)*
- Chỉ chủ sở hữu xem được attempt; attempt của người khác → **404** (không phải 403). *(T15)*

### 6.3. ReviewAnswer

Danh sách 20 câu của một lần làm bài và câu trả lời từng câu. **Tạo sẵn khi bắt đầu**: server gom các câu `is_active = true` của mọi kỹ năng khóa dạy, chia đều giữa các kỹ năng, chọn ngẫu nhiên 20 câu và ghi 20 dòng (position 1–20, `selected_index` trống) cùng ReviewAttempt trong một transaction. Khi nộp, server chỉ chấm đúng 20 dòng này. Phục vụ `GET /api/me/review-history/{attempt_id}`. *(T14, D04)*

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| attempt_id | INT | PK, FK → ReviewAttempt | |
| question_id | INT | PK, FK → Question | |
| position | SMALLINT | NN, CHECK 1–20 | Vị trí câu trong bài |
| selected_index | SMALLINT | NULL, CHECK 0–3 | Đáp án đã chọn; trống nếu bỏ qua — câu bỏ trống khi nộp tính là sai *(T16)* |
| is_correct | BOOLEAN | NULL | Server chấm; trống tới khi nộp; câu bỏ trống ghi FALSE *(T16)* |

Lưu ý: trước khi nộp, các endpoint làm bài chỉ trả `question_id`, `content`, `options`, `position`. *(T15)*

---

## 7. Nhóm F — Phản hồi và liên hệ

> Endpoint cho nhóm này (T22–T25) **chưa được nhóm đồng ý** trong file checklist; xem `docs/decisions.md`.

### 7.1. Feedback

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| feedback_id | SERIAL | PK | |
| user_id | INT | NN, FK → User | Lấy từ tài khoản đăng nhập |
| target_type | VARCHAR(10) | NN, CHECK (course, system) | |
| course_id | INT | NULL, FK → Course | Trống khi phản hồi về hệ thống |
| feedback_type | VARCHAR(50) | NN | Danh sách loại do nhóm quy định |
| content | TEXT | NN | |
| created_at | TIMESTAMP | DEFAULT now() | |

Ràng buộc bổ sung: `CHECK ((target_type = 'course' AND course_id IS NOT NULL) OR (target_type = 'system' AND course_id IS NULL))`.

### 7.2. CourseContact

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| course_id | INT | PK, FK → Course | Mỗi khóa tối đa một dòng |
| contact_email | VARCHAR(255) | NULL | |
| contact_phone | VARCHAR(30) | NULL | |

Dataset không có email/số điện thoại nên bảng để trống tới khi có dữ liệu.

---

## 8. Quan hệ giữa các bảng

### 8.1. Danh sách khóa ngoại

| # | Bảng cha (1) | Bảng con (N) | Khóa ngoại | Kiểu | ON DELETE |
|---|---|---|---|---|---|
| 1 | User | UserSkill | user_id | 1–N | CASCADE |
| 2 | Skill | UserSkill | skill_id | 1–N | RESTRICT |
| 3 | User | StudentCourse | user_id | 1–N | CASCADE |
| 4 | Course | StudentCourse | course_id | 1–N | RESTRICT |
| 5 | Course | CourseSkillRelation | course_id | 1–N | CASCADE |
| 6 | Skill | CourseSkillRelation | skill_id | 1–N | RESTRICT |
| 7 | Skill | SkillRelation | from_skill_id | 1–N | RESTRICT |
| 8 | Skill | SkillRelation | to_skill_id | 1–N | RESTRICT |
| 9 | BaseLearningPath | BaseLearningPathNode | template_id | 1–N | CASCADE |
| 10 | Skill | BaseLearningPathNode | skill_id | 1–N | RESTRICT |
| 11 | BaseLearningPathNode | BaseLearningPathEdge | (template_id, from_skill_id) | 1–N | CASCADE |
| 12 | BaseLearningPathNode | BaseLearningPathEdge | (template_id, to_skill_id) | 1–N | CASCADE |
| 13 | User | LearningPath | user_id | 1–N | CASCADE |
| 14 | BaseLearningPath | LearningPath | template_id | 1–N (0..1) | SET NULL |
| 15 | LearningPath | LearningPathNode | path_id | 1–N | CASCADE |
| 16 | Skill | LearningPathNode | skill_id | 1–N | RESTRICT |
| 17 | LearningPathNode | LearningPathEdge | (path_id, from_skill_id) | 1–N | CASCADE |
| 18 | LearningPathNode | LearningPathEdge | (path_id, to_skill_id) | 1–N | CASCADE |
| 19 | User | ChatSession | user_id | 1–N | CASCADE |
| 20 | ChatSession | ChatMessage | session_id | 1–N | CASCADE |
| 21 | Skill | Question | skill_id | 1–N | RESTRICT |
| 22 | StudentCourse | ReviewAttempt | student_course_id | 1–N | CASCADE |
| 23 | ReviewAttempt | ReviewAnswer | attempt_id | 1–N | CASCADE |
| 24 | Question | ReviewAnswer | question_id | 1–N | RESTRICT |
| 25 | User | PasswordResetToken | user_id | 1–N | CASCADE |
| 26 | User | Feedback | user_id | 1–N | CASCADE |
| 27 | Course | Feedback | course_id | 1–N (0..1) | CASCADE |
| 28 | Course | CourseContact | course_id | 1–1 (0..1) | CASCADE |

CASCADE = xóa cha thì xóa con; RESTRICT = còn con thì không cho xóa cha; SET NULL = xóa cha thì ô tham chiếu để trống. FK tới Skill dùng RESTRICT để không mất dữ liệu khi admin xóa kỹ năng. FK StudentCourse → Course là RESTRICT: không xóa được khóa học đang có học viên theo dõi.

### 8.2. Quan hệ nhiều–nhiều

| Quan hệ | Bảng trung gian | Ý nghĩa |
|---|---|---|
| Course ↔ Skill | CourseSkillRelation | Một khóa dạy nhiều kỹ năng và ngược lại |
| Skill ↔ Skill | SkillRelation | Tiên quyết, mở rộng hoặc liên quan |
| User ↔ Skill | UserSkill | Học viên đã có những kỹ năng nào |
| User ↔ Course | StudentCourse | Khóa đã lưu, đang học, hoàn thành hoặc đã bỏ |
| BaseLearningPath ↔ Skill | BaseLearningPathNode | Mẫu gồm những kỹ năng nào |
| LearningPath ↔ Skill | LearningPathNode | Lộ trình gồm những kỹ năng nào |
| ReviewAttempt ↔ Question | ReviewAnswer | Mỗi lần làm bài gồm những câu nào |

### 8.3. Theo luồng nghiệp vụ

- **Tạo lộ trình:** AI hiểu mục tiêu; backend tìm mẫu trong BaseLearningPath, ánh xạ vào Skill, mở rộng tiên quyết bằng SkillRelation, trả đề xuất (chưa lưu). Khi chấp nhận, `POST /api/learning-paths` tạo LearningPath, LearningPathNode, LearningPathEdge.
- **Gợi ý khóa học:** chỉ khi chọn một nút. CourseSkillRelation JOIN Course, xếp hạng theo mức liên quan, rating, num_reviews. Không dùng điểm ôn tập.
- **Theo dõi khóa học:** lưu → StudentCourse `bookmarked`; tham gia → `ongoing`, ghi joined_at, trả URL; từ bỏ → `abandoned`.
- **Gia sư AI:** mỗi phiên là một ChatSession (`session_type = 'tutor'`), tin nhắn ở ChatMessage.
- **Ôn tập (theo khóa học):** `POST /api/courses/{course_id}/review-attempts` tạo ReviewAttempt gắn StudentCourse và 20 ReviewAnswer từ Question (`is_active = true`) của các kỹ năng khóa dạy; khi nộp, chấm trong một transaction, nếu đạt (≥ 60%) cập nhật UserSkill và StudentCourse, rồi gửi email kết quả chạy nền. *(T11, T13, T29)*
- **Quên mật khẩu:** `POST /api/auth/forgot-password` tạo PasswordResetToken và gửi link; `POST /api/auth/reset-password` kiểm tra mã, cập nhật `User.hashed_password`, ghi used_at. *(T01, T02)*
- **Gửi phản hồi:** lưu một dòng Feedback gắn User (và Course nếu về khóa học); khung liên hệ lấy từ Course.instructor và CourseContact.
