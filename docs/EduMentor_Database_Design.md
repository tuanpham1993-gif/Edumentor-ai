# EduMentor AI – Thiết kế cơ sở dữ liệu

Tài liệu mô tả các bảng, các trường, mục đích của từng bảng và quan hệ giữa các bảng. Hệ quản trị: PostgreSQL. Ký hiệu: **PK** khóa chính, **FK** khóa ngoại, **UQ** giá trị không được trùng, **NN** không được để trống. Tên bảng viết theo kiểu đặc tả (ví dụ `LearningPathNode`); khi tạo bảng thật có thể đổi sang chữ thường có gạch dưới (`learning_path_node`). Riêng `User` trùng từ khóa của PostgreSQL nên bảng thật nên đặt là `users`.

## 1. Tổng quan

Cơ sở dữ liệu gồm **21 bảng** chia thành 6 nhóm. Hai nguyên tắc thiết kế: (1) các bảng liên quan tới dataset giữ đúng tên bảng và tên cột của dataset (riêng bảng Course có thêm 1 cột ảnh); (2) các bảng còn lại bám theo đặc tả API và SRS của nhóm (`LearningPathNode`, `LearningPathEdge`, `ReviewAttempt`…).

| Nhóm | Bảng | Thiết kế theo | Vai trò chung |
|---|---|---|---|
| A. Theo dataset | `Course`, `Skill`, `CourseSkillRelation`, `SkillRelation` | 4 file dataset | Kho khóa học, kỹ năng, khóa học dạy kỹ năng nào, kỹ năng nào học trước kỹ năng nào |
| B. Người dùng | `User`, `UserSkill`, `StudentCourse`, `PasswordResetToken` | Đặc tả API (mục 2, 4) | Tài khoản, kỹ năng đã có, theo dõi khóa học với 4 trạng thái (đã lưu, đang học, hoàn thành, đã bỏ), và mã đặt lại mật khẩu qua email |
| C. Lộ trình | `BaseLearningPath`, `BaseLearningPathNode`, `BaseLearningPathEdge`, `LearningPath`, `LearningPathNode`, `LearningPathEdge` | SRS (`LearningPath*`) và API mục 5, 6, 7, 12 | Mẫu lộ trình do admin quản lý và lộ trình cá nhân của học viên dạng đồ thị kỹ năng |
| D. Chatbot | `ChatSession`, `ChatMessage` | API mục 9 | Phiên trò chuyện (gia sư AI, tư vấn lộ trình) và tin nhắn |
| E. Ôn tập | `Question`, `ReviewAttempt`, `ReviewAnswer` | SRS (`ReviewAttempt`) và API mục 10 | Ngân hàng câu hỏi, các lần làm bài ôn tập và kết quả từng câu |
| F. Phản hồi và liên hệ | `Feedback`, `CourseContact` | Màn hình "Liên hệ & góp ý" | Phản hồi của học viên về khóa học hoặc hệ thống, và thông tin liên hệ của từng khóa học |

### Nguồn dữ liệu

| Dataset | Bảng tương ứng | Ghi chú xử lý khi nạp |
|---|---|---|
| course_table | `Course` | Giữ đủ 12 cột của dataset, thêm 1 cột `image_url` (dataset chưa có ảnh nên để trống tới khi bổ sung). Chuyển `num_enrolled` ("5,710") và `rating` (chuỗi) sang số, `num_reviews` (27.0) sang số nguyên, lấy số từ "4 modules" cho `modules`, sửa `intermidiate` thành `intermediate` |
| skill_table | `Skill` | Giữ nguyên 2 cột |
| course_skill_relation | `CourseSkillRelation` | Giữ `course_id` và `skill_id`. Hai cột `title`, `skill` trong file chỉ là bản sao tên (lấy được bằng JOIN) nên không lưu lại |
| skill_relation | `SkillRelation` | Giữ `from_skill_id`, `to_skill_id`, `relation_type`. Hai cột tên kỹ năng là bản sao nên không lưu lại. Cần xác nhận chiều của quan hệ |

## 2. Nhóm A – Bảng theo dataset

Bốn bảng này được thiết kế đúng theo 4 file dataset: giữ nguyên tên bảng và tên cột. Chỉ có một cột thêm ngoài dataset là image_url của bảng Course (ảnh khóa học).

### 2.1. `Course` (từ course_table)

**Mục đích:** Kho khóa học. Dùng cho danh mục khóa học: tìm kiếm theo từ khóa, lọc theo kỹ năng và `level`, sắp xếp theo `rating` hoặc `num_reviews`; đồng thời là nguồn khóa học để gợi ý cho từng nút kỹ năng. EduMentor chỉ lưu thông tin và đường link, không lưu nội dung khóa học.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `course_id` | INT | PK | Mã số của khóa học (giữ nguyên mã trong dataset) |
| `title` | VARCHAR(500) | NN | Tên khóa học, hiển thị cho học viên và dùng khi tìm kiếm |
| `num_enrolled` | INT | DEFAULT 0 | Số người đã đăng ký học khóa này. Càng đông thì khóa càng phổ biến |
| `rating` | NUMERIC(2,1) | CHECK 0–5 | Điểm đánh giá trung bình (tối đa 5 sao), dùng để lọc và sắp xếp các khóa tốt |
| `num_reviews` | INT | DEFAULT 0 | Số lượt đánh giá. Cần cột này vì 5 sao từ 3 người kém đáng tin hơn 4,6 sao từ 3.000 người |
| `instructor` | VARCHAR(255) |  | Tên giảng viên |
| `organization` | VARCHAR(255) |  | Trường đại học hoặc công ty cung cấp khóa học, ví dụ University of California, Davis |
| `description` | TEXT |  | Đoạn mô tả nội dung khóa học. Hệ thống đọc đoạn này để hiểu khóa học nói về gì |
| `modules` | INT |  | Số chương (học phần) của khóa học. Trong dataset ghi dạng "4 modules", khi nạp chỉ lấy số 4 |
| `level` | VARCHAR(20) | CHECK (beginner, intermediate, advanced) | Độ khó: beginner = người mới, intermediate = trung cấp, advanced = nâng cao |
| `schedule` | VARCHAR(255) |  | Thời gian học, chép nguyên văn từ dataset, ví dụ "10 hours to complete (3 weeks at 3 hours a week)" |
| `url` | VARCHAR(500) | UQ | Đường link tới khóa học gốc trên Coursera. EduMentor chỉ dẫn link, không chứa nội dung khóa học |
| `image_url` | VARCHAR(500) | NULL | Đường dẫn tới ảnh đại diện của khóa học, hiển thị trên thẻ khóa học. Đây là cột thêm ngoài dataset; để trống cho tới khi có ảnh |

### 2.2. `Skill` (từ skill_table)

**Mục đích:** Danh mục kỹ năng. Là "ngôn ngữ chung" nối khóa học, hồ sơ học viên, lộ trình và câu hỏi ôn tập với nhau.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `skill_id` | INT | PK | Mã số của kỹ năng (giữ nguyên mã trong dataset) |
| `skill` | VARCHAR(255) | NN, UQ | Tên kỹ năng, ví dụ "web interactivity". Không được trùng tên |
| `is_active` | BOOLEAN | NN, DEFAULT TRUE | Trạng thái kĩ năng đang sống hay chết|

### 2.3. `CourseSkillRelation` (từ course_skill_relation)

**Mục đích:** Cho biết mỗi khóa học dạy những kỹ năng nào (một khóa dạy nhiều kỹ năng, một kỹ năng có nhiều khóa dạy). Khi lộ trình cần một kỹ năng, hệ thống dùng bảng này để tìm các khóa học phù hợp.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `course_id` | INT | PK, FK → Course | Khóa học đang xét |
| `skill_id` | INT | PK, FK → Skill | Kỹ năng mà khóa học đó dạy. Mỗi dòng đọc là: "khóa học này dạy kỹ năng này" |

### 2.4. `SkillRelation` (từ skill_relation)

**Mục đích:** Quan hệ giữa các kỹ năng, dùng chung cho toàn hệ thống (khác với `LearningPathEdge` là các kết nối nằm trong một lộ trình cụ thể). Quan hệ `prerequisite` tạo thành đồ thị để biết cần học gì trước khi học kỹ năng khác.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `from_skill_id` | INT | PK, FK → Skill | Kỹ năng cần học trước (đầu mũi tên) |
| `to_skill_id` | INT | PK, FK → Skill, CHECK khác `from_skill_id` | Kỹ năng học sau (cuối mũi tên). Hai đầu không được là cùng một kỹ năng |
| `relation_type` | VARCHAR(15) | NN, DEFAULT 'prerequisite', CHECK (prerequisite, extension, related) | Loại quan hệ: `prerequisite` = phải học trước (giá trị có trong dataset); `extension` = học tiếp để đào sâu; `related` = có liên quan. Hai loại sau do admin thêm qua API |

**Lưu ý:** Quy ước hướng cạnh là kỹ năng bắt đầu được học trước kỹ năng đích. Chỉ quan hệ `prerequisite` phải tạo thành đồ thị không có vòng, kiểm tra khi nạp dữ liệu và khi admin thêm quan hệ. Cần kiểm tra dataset có cùng chiều này không.

## 3. Nhóm B – Người dùng

Các bảng này thiết kế theo đặc tả API (mục 2 và mục 4). EduMentor chỉ theo dõi tiến trình học ở mức cơ bản, không theo dõi từng bài học hay tiến độ xem video.

### 3.1. `User`

**Mục đích:** Lưu tài khoản và vai trò (học viên hoặc admin). Là gốc của mọi dữ liệu cá nhân: kỹ năng, khóa học đang theo dõi, lộ trình, chat. Phục vụ đăng ký, đăng nhập và `GET/PATCH /api/me`.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `user_id` | SERIAL | PK | Mã số của tài khoản |
| `email` | VARCHAR(255) | NN, UQ | Email dùng để đăng nhập; mỗi email chỉ đăng ký được một tài khoản |
| `hashed_password` | VARCHAR(255) | NN | Mật khẩu đã được mã hóa. Hệ thống không bao giờ lưu mật khẩu gốc |
| `full_name` | VARCHAR(100) |  | Tên hiển thị của học viên |
| `avatar_url` | VARCHAR(500) | NULL | Đường dẫn tới ảnh đại diện (ảnh profile) của học viên, hiển thị ở trang cá nhân. Để trống nếu học viên chưa đặt ảnh |
| `role` | VARCHAR(10) | NN, DEFAULT 'student', CHECK (student, admin) | Vai trò: `student` = học viên, `admin` = quản trị viên. Hệ thống dựa vào đây để quyết định ai được dùng các chức năng quản trị |
| `created_at` | TIMESTAMP | DEFAULT now() | Ngày giờ tạo tài khoản |

### 3.2. `UserSkill`

**Mục đích:** Hồ sơ kỹ năng của học viên: các kỹ năng đã được ghi nhận. Phục vụ `GET/PATCH /api/me/skills`. Sau khi học viên hoàn thành bài ôn tập, backend tự cập nhật bảng này; học viên cũng có thể tự thêm, sửa, xóa. Lộ trình dùng bảng này để biết kỹ năng nào học viên đã có.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `user_id` | INT | PK, FK → User | Học viên nào |
| `skill_id` | INT | PK, FK → Skill | Kỹ năng nào. Mỗi dòng đọc là: "học viên này có kỹ năng này" |
| `status` | VARCHAR(10) | NN, DEFAULT 'known', CHECK (learning, known) | `learning` = đang học; `known` = đã biết. Một nút trong lộ trình chỉ được tính là xong khi kỹ năng ở trạng thái `known` |
| `updated_at` | TIMESTAMP | DEFAULT now() | Lần cập nhật gần nhất |

### 3.3. `StudentCourse`

**Mục đích:** Theo dõi quan hệ giữa một học viên và một khóa học, gồm cả việc **lưu khóa học để học sau** lẫn việc **học**. Một bảng này dùng cho cả 4 trạng thái (`bookmarked`, `ongoing`, `completed`, `abandoned`) nên không cần bảng riêng cho danh sách đã lưu. Bản ghi được tạo khi học viên lưu khóa học (`/api/me/bookmarks`, trạng thái `bookmarked`) hoặc khi bấm tham gia (`POST /api/courses/{course_id}/join`, trạng thái `ongoing`, hệ thống trả về URL khóa học bên ngoài). Đây là trạng thái theo dõi của EduMentor, không phải trạng thái đăng ký trên nền tảng MOOC.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `student_course_id` | SERIAL | PK | Mã số của bản ghi theo dõi |
| `user_id` | INT | NN, FK → User | Học viên nào |
| `course_id` | INT | NN, FK → Course | Khóa học nào |
| `status` | VARCHAR(12) | NN, CHECK (bookmarked, ongoing, completed, abandoned) | Tình trạng của khóa học đối với học viên: `bookmarked` = đã lưu để học sau, chưa học; `ongoing` = đang học (đã bấm tham gia); `completed` = đã xong (chỉ tính khi làm xong bài ôn tập, không phải chỉ vì mở link); `abandoned` = đã bỏ |
| `joined_at` | TIMESTAMP | NULL | Lúc học viên bấm tham gia học. Mặc định để trống: khóa mới chỉ được lưu (`bookmarked`) thì chưa có giờ tham gia |
| `completed_at` | TIMESTAMP | NULL | Lúc học viên hoàn thành (để trống nếu chưa xong) |
| `updated_at` | TIMESTAMP | DEFAULT now() | Lần đổi trạng thái gần nhất. Với khóa chỉ mới lưu, đây cũng chính là lúc lưu |

**Ràng buộc bổ sung:** UNIQUE `(user_id, course_id)`, mỗi học viên chỉ có một bản ghi theo dõi cho mỗi khóa.

**Quy tắc:**

- Lưu khóa học: tạo dòng `bookmarked`. Nếu học viên đã có dòng cho khóa đó (dù trạng thái nào) thì không tạo thêm.
- Bỏ lưu: chỉ xóa dòng khi trạng thái đang là `bookmarked`. Nếu khóa đã `ongoing`, `completed` hoặc `abandoned` thì không xóa và không đổi trạng thái.
- Bấm tham gia (`POST /api/courses/{course_id}/join`): chuyển `bookmarked` → `ongoing` và ghi `joined_at`; nếu chưa có dòng thì tạo mới ở trạng thái `ongoing`.
- `DELETE /api/me/courses/{course_id}` chỉ chuyển `status` sang `abandoned`, không xóa dòng, để giữ lịch sử.
- Danh sách mặc định (`GET /api/me/courses`) loại các khóa `abandoned`; xem lại bằng bộ lọc trạng thái.
- Chuyển trạng thái đề xuất: `bookmarked` → `ongoing`; `ongoing` → `completed` hoặc `abandoned`; `abandoned` → `ongoing` (theo dõi lại); `completed` giữ nguyên. Chỉ cho làm bài ôn tập khi khóa đang `ongoing`. Cần nhóm xác nhận.

### 3.4. `PasswordResetToken`

**Mục đích:** Hỗ trợ chức năng **quên mật khẩu bằng email**. Khi học viên yêu cầu đặt lại mật khẩu, hệ thống tạo một mã đặt lại, gửi qua email, và lưu lại ở đây để kiểm tra khi học viên bấm vào link và nhập mật khẩu mới. Mỗi mã chỉ dùng được một lần và có thời hạn.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `reset_id` | SERIAL | PK | Mã số của một yêu cầu đặt lại mật khẩu |
| `user_id` | INT | NN, FK → User | Yêu cầu này của tài khoản nào (hệ thống tìm theo email học viên nhập) |
| `token_hash` | VARCHAR(255) | NN, UQ | Mã đặt lại đã được mã hóa. Mã gốc chỉ nằm trong email gửi cho học viên, hệ thống không lưu mã gốc (giống cách lưu mật khẩu) |
| `expires_at` | TIMESTAMP | NN | Hạn dùng của mã (đề xuất 15–30 phút kể từ lúc tạo). Quá hạn thì mã không còn dùng được |
| `used_at` | TIMESTAMP | NULL | Lúc học viên đã dùng mã để đổi mật khẩu. Để trống = chưa dùng. Mã đã dùng thì không dùng lại được |
| `created_at` | TIMESTAMP | DEFAULT now() | Lúc tạo yêu cầu |

**Luồng xử lý:**

- Học viên nhập email ở màn hình quên mật khẩu. Hệ thống tìm `User` theo `email`; nếu có thì tạo một dòng mới ở bảng này và gửi email chứa link kèm mã. Dù email có tồn tại hay không, hệ thống đều trả cùng một thông báo (ví dụ "Nếu email đúng, bạn sẽ nhận được hướng dẫn") để người lạ không dò được email nào đã đăng ký.
- Học viên mở link và nhập mật khẩu mới. Hệ thống mã hóa mã nhận được rồi tìm dòng có `token_hash` khớp, kiểm tra chưa hết hạn (`expires_at`) và chưa dùng (`used_at` còn trống).
- Nếu hợp lệ: cập nhật `User.hashed_password`, ghi `used_at`, và vô hiệu các mã cũ chưa dùng của tài khoản đó.
- API hiện chưa có endpoint cho chức năng này; cần bổ sung endpoint yêu cầu đặt lại và endpoint xác nhận đặt lại.

## 4. Nhóm C – Lộ trình

Lộ trình học tập được tạo qua hội thoại với AI Consultant: mô hình AI hiểu mục tiêu của học viên, còn backend ánh xạ kỹ năng, mở rộng các kỹ năng học trước và lưu kết quả. Lộ trình là một **đồ thị kỹ năng**: mỗi nút (`LearningPathNode`) là một kỹ năng, mỗi cạnh (`LearningPathEdge`) là một kết nối "học trước, học sau". Ba bảng `BaseLearningPath*` là các mẫu có sẵn do admin quản lý.

### 4.1. `BaseLearningPath`

**Mục đích:** Mẫu lộ trình cơ sở do admin quản lý (`/api/admin/base-learning-paths`): điểm xuất phát dùng lại được cho các mục tiêu phổ biến (Backend AI, Data Analyst…). AI Consultant tìm mẫu phù hợp rồi mở rộng bằng đồ thị kỹ năng chung. Mẫu không bắt buộc mọi người cùng mục tiêu nhận lộ trình giống hệt nhau.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `template_id` | SERIAL | PK | Mã số của mẫu lộ trình |
| `name` | VARCHAR(100) | NN, UQ | Tên mẫu, ví dụ "Backend AI" |
| `description` | TEXT |  | Mô tả mẫu dành cho ai, giúp hệ thống chọn đúng mẫu khớp với mục tiêu học viên nhập |
| `is_active` | BOOLEAN | NN, DEFAULT TRUE | Công tắc bật/tắt. Mẫu đã có người dùng thì chỉ tắt đi, không xóa |
| `created_at` | TIMESTAMP | DEFAULT now() | Ngày tạo |
| `updated_at` | TIMESTAMP | DEFAULT now() | Lần sửa gần nhất |

### 4.2. `BaseLearningPathNode`

**Mục đích:** Các kỹ năng (nút) của một mẫu lộ trình, gồm cả kỹ năng mục tiêu (`/api/admin/base-learning-paths/{template_id}/nodes`). Cấu trúc giống `LearningPathNode`, chỉ bỏ cột `added_by` vì mẫu luôn do admin tạo.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `template_id` | INT | PK, FK → BaseLearningPath | Mẫu lộ trình mà nút này thuộc về |
| `skill_id` | INT | PK, FK → Skill | Kỹ năng mà nút đại diện (mỗi nút là một kỹ năng cần học) |
| `node_role` | VARCHAR(15) | NULL, CHECK (prerequisite, optional, extension) | Nút này đóng vai gì: `prerequisite` = phải học trước; `optional` = nên học thêm; `extension` = để đào sâu. Để trống nếu nút chính là kỹ năng mục tiêu |
| `is_target` | BOOLEAN | NN, DEFAULT FALSE | TRUE nếu đây là kỹ năng mục tiêu chính của mẫu |
| `is_required` | BOOLEAN | NN, DEFAULT TRUE | TRUE = bắt buộc phải học; FALSE = có thể bỏ qua |
| `display_order` | INT | NN | Thứ tự hiện trên màn hình. Dùng số cách xa nhau (1000, 2000…) để chèn thêm nút ở giữa mà không phải đánh số lại |

### 4.3. `BaseLearningPathEdge`

**Mục đích:** Các kết nối giữa nút trong mẫu lộ trình (`/api/admin/base-learning-paths/{template_id}/edges`). Khi tạo lộ trình từ mẫu, các kết nối này được sao chép sang `LearningPathEdge`.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `template_id` | INT | PK | Mẫu lộ trình chứa mũi tên (kết nối) này |
| `from_skill_id` | INT | PK | Kỹ năng ở đầu mũi tên: học trước |
| `to_skill_id` | INT | PK | Kỹ năng ở cuối mũi tên: học sau |
| `relation_type` | VARCHAR(15) | NN, CHECK (prerequisite, optional) | `prerequisite` = bắt buộc học trước; `optional` = nên học trước nhưng không bắt buộc |

**Ràng buộc bổ sung:** cả hai kỹ năng ở hai đầu phải là nút trong cùng mẫu, thực hiện bằng khóa ngoại tổng hợp `(template_id, from_skill_id)` và `(template_id, to_skill_id)` cùng tham chiếu `BaseLearningPathNode(template_id, skill_id)`.

### 4.4. `LearningPath`

**Mục đích:** Lộ trình học tập của một học viên, lưu khi học viên chấp nhận bản đề xuất (`POST /api/learning-paths`). Bản đề xuất do `POST /api/chat/learning-path` trả về chưa lưu vào cơ sở dữ liệu cho tới khi được chấp nhận. Nếu học viên chỉ sửa nhỏ thì cập nhật lộ trình hiện tại; nếu đổi sang mục tiêu khác hẳn thì tạo lộ trình mới và giữ lại lộ trình cũ.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `path_id` | SERIAL | PK | Mã số của lộ trình |
| `user_id` | INT | NN, FK → User | Lộ trình này của học viên nào |
| `template_id` | INT | NULL, FK → BaseLearningPath | Lộ trình được xây từ mẫu nào (để trống nếu không dùng mẫu) |
| `goal_text` | TEXT | NN | Câu mục tiêu học viên đã nhập, ví dụ "Em muốn làm app bán đồ ăn" |
| `status` | VARCHAR(10) | NN, DEFAULT 'ongoing', CHECK (ongoing, completed, abandoned) | `ongoing` = đang theo; `completed` = tất cả nút bắt buộc đã hoàn thành hoặc được công nhận là đã biết; `abandoned` = đã bỏ |
| `created_at` | TIMESTAMP | DEFAULT now() | Lúc tạo |
| `updated_at` | TIMESTAMP | DEFAULT now() | Lần sửa gần nhất |

**Quy tắc:** `DELETE /api/learning-paths/{path_id}` chỉ chuyển `status` sang `abandoned`, không xóa dòng, để giữ lịch sử.

### 4.5. `LearningPathNode`

**Mục đích:** Lưu các kỹ năng (nút) được chọn cho từng lộ trình. Phân biệt kỹ năng mục tiêu, kỹ năng học trước, tùy chọn và mở rộng; theo dõi nút do hệ thống hay người dùng thêm; xác định nút nào bắt buộc phải hoàn thành để kết thúc lộ trình.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `path_id` | INT | PK, FK → LearningPath | Lộ trình mà nút này thuộc về |
| `skill_id` | INT | PK, FK → Skill | Kỹ năng mà nút đại diện. Một kỹ năng chỉ xuất hiện một lần trong cùng một lộ trình |
| `node_role` | VARCHAR(15) | NULL, CHECK (prerequisite, optional, extension) | Nút này đóng vai gì: `prerequisite` = kỹ năng hỗ trợ được thêm vào vì các quan hệ học trước; `optional` = hữu ích nhưng không bắt buộc; `extension` = do sinh viên thêm thủ công hoặc là phần mở rộng của lộ trình ban đầu. Để trống nếu nút chỉ là kỹ năng mục tiêu |
| `is_target` | BOOLEAN | NN, DEFAULT FALSE | TRUE nếu kỹ năng được Layer 1 chọn trực tiếp từ mục tiêu của học viên. Tách riêng khỏi `node_role` vì một kỹ năng mục tiêu vẫn có thể là điều kiện học trước của một kỹ năng mục tiêu khác |
| `added_by` | VARCHAR(10) | NN, DEFAULT 'system', CHECK (system, user) | Ai thêm nút: `system` = hệ thống tự thêm (khớp mục tiêu, mở rộng kỹ năng học trước, đề xuất bằng Collaborative Filtering); `user` = học viên tự thêm |
| `is_required` | BOOLEAN | NN, DEFAULT TRUE | Nút có bắt buộc để hoàn thành lộ trình hay không |
| `display_order` | INT | NN | Thứ tự hiển thị ưu tiên (chỉ để sắp xếp, không quyết định kỹ năng nào học trước; quan hệ đó nằm ở `LearningPathEdge`). Dùng số cách xa nhau (1000, 2000, 3000) để chèn nút ở giữa (1500) mà không phải đánh số lại |

**Quy tắc:** khi xóa một nút (`DELETE /api/learning-paths/{path_id}/nodes/{skill_id}`), hệ thống phải xóa luôn các cạnh liên quan, thực hiện trong cùng một transaction.

### 4.6. `LearningPathEdge`

**Mục đích:** Lưu các kết nối giữa những nút trong lộ trình của một sinh viên. `SkillRelation` là quan hệ dùng chung toàn hệ thống, còn bảng này lưu các kết nối thực tế đưa vào một lộ trình cụ thể. Dùng để vẽ đồ thị, tìm nút bắt đầu (không có cạnh đi vào) và nút kết thúc (không có cạnh đi ra), và chỉ cập nhật các cạnh bị ảnh hưởng khi sinh viên thêm hoặc xóa nút.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `path_id` | INT | PK | Lộ trình chứa mũi tên (kết nối) này |
| `from_skill_id` | INT | PK | Kỹ năng ở đầu mũi tên: học trước. Phải là một nút trong cùng lộ trình |
| `to_skill_id` | INT | PK | Kỹ năng ở cuối mũi tên: học sau. Phải là một nút trong cùng lộ trình |
| `relation_type` | VARCHAR(15) | NN, CHECK (prerequisite, optional) | `prerequisite` = bắt buộc học trước; `optional` = nên học trước nhưng không bắt buộc |

**Ràng buộc bổ sung:**

- Khóa ngoại tổng hợp: `(path_id, from_skill_id)` và `(path_id, to_skill_id)` cùng tham chiếu `LearningPathNode(path_id, skill_id)`, nên cạnh không thể trỏ tới nút ngoài lộ trình và không có cạnh mồ côi.
- Với quan hệ `prerequisite`, kỹ năng bắt đầu được học trước kỹ năng đích.
- Việc hoàn thành lộ trình dựa trên tiến độ các nút bắt buộc, không chỉ dựa vào việc đi tới một nút kết thúc, vì đồ thị có nhánh có thể có nhiều nút kết thúc.

## 5. Nhóm D – Chatbot

Thiết kế theo đặc tả API mục 9. Chức năng tạo lộ trình và chức năng gia sư cùng dùng nhóm `/api/chat/` nhưng là hai loại phiên riêng biệt.

### 5.1. `ChatSession`

**Mục đích:** Một phiên trò chuyện, luôn gắn với người dùng đã đăng nhập: học viên A không đọc được phiên của học viên B.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `session_id` | UUID | PK | Mã của phiên chat (một chuỗi ngẫu nhiên dài, khó đoán), cũng dùng làm khóa để nhớ nội dung đang trò chuyện |
| `user_id` | INT | NN, FK → User | Phiên chat này của ai |
| `session_type` | VARCHAR(15) | NN, DEFAULT 'tutor', CHECK (tutor, learning_path) | Loại phiên: `tutor` = hỏi bài với gia sư AI; `learning_path` = trò chuyện để nhờ tư vấn lộ trình |
| `topic` | VARCHAR(255) |  | Chủ đề của cuộc trò chuyện |
| `status` | VARCHAR(10) | NN, DEFAULT 'active', CHECK (active, archived) | `active` = đang dùng; `archived` = đã cất đi. `DELETE /api/chat/sessions/{session_id}` chuyển sang `archived` theo chính sách lưu trữ dữ liệu |
| `created_at` | TIMESTAMP | DEFAULT now() | Lúc bắt đầu phiên |
| `updated_at` | TIMESTAMP | DEFAULT now() | Lần trò chuyện gần nhất |

### 5.2. `ChatMessage`

**Mục đích:** Lưu mọi tin nhắn của một phiên (`GET /api/chat/sessions/{session_id}/messages`). Gia sư AI nhớ ngữ cảnh trong phiên bằng cách đọc lại các tin nhắn gần nhất.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `message_id` | BIGSERIAL | PK | Mã số của tin nhắn |
| `session_id` | UUID | NN, FK → ChatSession | Tin nhắn thuộc phiên chat nào |
| `role` | VARCHAR(10) | NN, CHECK (user, assistant) | Ai nói: `user` = học viên, `assistant` = AI |
| `content` | TEXT | NN | Nội dung tin nhắn |
| `created_at` | TIMESTAMP | DEFAULT now() | Lúc gửi tin nhắn |

**Lưu ý:** API hiện chưa có endpoint chấm sao hoặc phản hồi cho tin nhắn nên chưa có cột cho việc này. Nếu nhóm bổ sung chức năng đó thì thêm cột vào bảng này.

## 6. Nhóm E – Ôn tập

Hệ thống ôn tập lấy câu hỏi có sẵn trong cơ sở dữ liệu và ghi lại các lần làm bài. Mỗi bài ôn tập gồm 20 câu trắc nghiệm. Bảng `ReviewAttempt` thiết kế đúng theo SRS của nhóm.

### 6.1. `Question`

**Mục đích:** Ngân hàng câu hỏi trắc nghiệm theo kỹ năng. Mỗi kỹ năng cần ít nhất 20 câu thì mới có bài ôn tập; `GET /api/skills/{skill_id}/review` kiểm tra điều kiện này.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `question_id` | SERIAL | PK | Mã số của câu hỏi |
| `skill_id` | INT | NN, FK → Skill | Câu hỏi này kiểm tra kỹ năng nào. Bài ôn tập của một khóa học lấy câu hỏi từ các kỹ năng mà khóa đó dạy |
| `content` | TEXT | NN | Nội dung câu hỏi |
| `options` | JSONB | NN | Danh sách các đáp án để chọn (4 đáp án) |
| `correct_index` | SMALLINT | NN, CHECK 0–3 | Đáp án đúng là đáp án thứ mấy (0 là đáp án đầu tiên). Chỉ server biết, không gửi cho học viên trước khi nộp bài |
| `explanation` | TEXT |  | Lời giải thích vì sao đáp án đó đúng, hiện ra khi học viên làm sai |

### 6.2. `ReviewAttempt`

**Mục đích:** Lưu lại mọi lần sinh viên thực hiện bài đánh giá để vượt qua bài kiểm tra của EduMentor. Trả lời được các câu hỏi: học viên đã làm bài chưa, làm mấy lần, điểm bao nhiêu, đạt hay chưa. Phục vụ `/api/me/review-history`.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `attempt_id` | SERIAL | PK | Mã số của một lần làm bài |
| `student_course_id` | INT | NN, FK → StudentCourse | Lần làm bài này thuộc về việc học khóa nào của học viên nào (qua đây biết được cả học viên và khóa học) |
| `score_percent` | NUMERIC(5,2) | NULL, CHECK 0–100 | Điểm tính theo phần trăm (ví dụ 85 là đúng 85%). Để trống khi chưa nộp bài |
| `passed` | BOOLEAN | NULL | Kết quả có đạt theo quy tắc đạt hay không. Ghi riêng ra để sau này đổi mức điểm đạt thì kết quả cũ không bị đổi theo. Để trống khi chưa nộp bài |
| `attempted_at` | TIMESTAMP | NN, DEFAULT now() | Thời điểm thực hiện bài đánh giá |

**Cách dùng:**

- Số lần làm bài: đếm các dòng theo `student_course_id`. Lần chưa nộp có `score_percent` để trống.
- Khi nộp bài, server chấm điểm và ghi `score_percent`, `passed`. Nếu đạt theo chính sách hoàn thành đã thống nhất: chuyển `StudentCourse.status` sang `completed` và thêm các kỹ năng của khóa học vào `UserSkill`.
- Học viên cần có bản ghi `StudentCourse` ở trạng thái `ongoing` (đã bấm tham gia khóa) trước khi làm bài ôn tập.

### 6.3. `ReviewAnswer`

**Mục đích:** Danh sách 20 câu hỏi của một lần làm bài và câu trả lời từng câu. Được tạo sẵn khi bắt đầu lần làm bài (để server biết đúng 20 câu cần chấm) và cập nhật khi nộp bài. Phục vụ `GET /api/me/review-history/{attempt_id}`. Đây là bảng bổ sung vì `ReviewAttempt` chỉ lưu điểm tổng.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `attempt_id` | INT | PK, FK → ReviewAttempt | Thuộc lần làm bài nào |
| `question_id` | INT | PK, FK → Question | Là câu hỏi nào |
| `position` | SMALLINT | NN, CHECK 1–20 | Câu này đứng thứ mấy trong bài (từ 1 đến 20) |
| `selected_index` | SMALLINT | NULL, CHECK 0–3 | Đáp án học viên đã chọn (0 là đáp án đầu tiên). Để trống nếu chưa trả lời hoặc bỏ qua |
| `is_correct` | BOOLEAN | NULL | Học viên trả lời đúng hay sai, do server chấm. Để trống cho tới khi nộp bài |

## 7. Nhóm F – Phản hồi và liên hệ

Thiết kế theo màn hình "Liên hệ & góp ý". Học viên đã đăng nhập nên hệ thống tự gắn tài khoản vào phản hồi, không cần nhập họ tên hay email. Học viên chọn phản hồi về **một khóa học** hoặc về **hệ thống EduMentor AI**. Bên phải màn hình hiển thị thông tin liên hệ: của khóa học đang chọn (lấy từ `Course` và `CourseContact`) và email hỗ trợ của EduMentor AI (là giá trị cấu hình chung của hệ thống, không cần bảng).

### 7.1. `Feedback`

**Mục đích:** Lưu mỗi phản hồi mà học viên gửi từ màn hình "Liên hệ & góp ý".

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `feedback_id` | SERIAL | PK | Mã số của phản hồi |
| `user_id` | INT | NN, FK → User | Ai gửi phản hồi. Hệ thống tự lấy từ tài khoản đang đăng nhập nên học viên không phải nhập họ tên hay email |
| `target_type` | VARCHAR(10) | NN, CHECK (course, system) | Ô "Bạn muốn phản hồi về": `course` = một khóa học; `system` = hệ thống EduMentor AI |
| `course_id` | INT | NULL, FK → Course | Ô "Chọn khóa học": khóa học được phản hồi. Để trống khi phản hồi về hệ thống |
| `feedback_type` | VARCHAR(50) | NN | Ô "Loại phản hồi", ví dụ "Nội dung bài giảng". Danh sách các loại do nhóm quy định |
| `content` | TEXT | NN | Ô "Nội dung": lời phản hồi của học viên |
| `created_at` | TIMESTAMP | DEFAULT now() | Lúc gửi phản hồi |

**Ràng buộc bổ sung:** CHECK `(target_type = 'course' AND course_id IS NOT NULL) OR (target_type = 'system' AND course_id IS NULL)`, để phản hồi về khóa học luôn có khóa học và phản hồi về hệ thống thì không gắn khóa học.

**Lưu ý:** Danh sách "Loại phản hồi" cần nhóm chốt (ví dụ "Nội dung bài giảng" cho khóa học); có thể khác nhau giữa phản hồi về khóa học và phản hồi về hệ thống.

### 7.2. `CourseContact`

**Mục đích:** Thông tin liên hệ của từng khóa học, hiển thị ở khung "Thông tin liên hệ của khóa học" cạnh form phản hồi và đổi theo khóa học đã chọn. Tên người đăng hoặc giảng viên đã có ở `Course.instructor` nên bảng này chỉ lưu email và số điện thoại. Bảng được tách riêng để `Course` giữ đúng cột của dataset.

| Trường | Kiểu | Ràng buộc | Công dụng |
|---|---|---|---|
| `course_id` | INT | PK, FK → Course | Khóa học nào (mỗi khóa có tối đa một dòng liên hệ) |
| `contact_email` | VARCHAR(255) | NULL | Email liên hệ của người đăng hoặc giảng viên |
| `contact_phone` | VARCHAR(30) | NULL | Số điện thoại liên hệ |

**Lưu ý:** Dataset không có email và số điện thoại, nên bảng này để trống cho tới khi có dữ liệu.

## 8. Quan hệ giữa các bảng

### 8.1. Danh sách khóa ngoại

| # | Bảng cha (phía 1) | Bảng con (phía N) | Khóa ngoại | Kiểu | ON DELETE |
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

Ý nghĩa: CASCADE = xóa dòng cha thì dòng con xóa theo; RESTRICT = còn dòng con thì không cho xóa dòng cha; SET NULL = xóa dòng cha thì ô tham chiếu ở dòng con để trống. Các khóa ngoại tới `Skill` dùng RESTRICT để không vô tình mất dữ liệu khi admin xóa kỹ năng. Khóa ngoại từ `StudentCourse` tới `Course` cũng RESTRICT: không xóa được khóa học đang có học viên theo dõi (API trả lỗi để admin xử lý).

### 8.2. Các quan hệ nhiều–nhiều (qua bảng trung gian)

| Quan hệ | Bảng trung gian | Ý nghĩa |
|---|---|---|
| Course ↔ Skill | `CourseSkillRelation` | Một khóa dạy nhiều kỹ năng, một kỹ năng được nhiều khóa dạy |
| Skill ↔ Skill (tự tham chiếu) | `SkillRelation` | Kỹ năng A là tiên quyết, mở rộng hoặc liên quan tới kỹ năng B |
| User ↔ Skill | `UserSkill` | Học viên đã có những kỹ năng nào |
| User ↔ Course | `StudentCourse` | Khóa học học viên đã lưu, đang học, đã hoàn thành hoặc đã bỏ |
| BaseLearningPath ↔ Skill | `BaseLearningPathNode` | Mẫu lộ trình gồm những kỹ năng nào |
| LearningPath ↔ Skill | `LearningPathNode` | Lộ trình của học viên gồm những kỹ năng nào |
| ReviewAttempt ↔ Question | `ReviewAnswer` | Mỗi lần làm bài gồm những câu hỏi nào |

### 8.3. Mô tả theo luồng nghiệp vụ

- **Tạo lộ trình:** AI Consultant hiểu mục tiêu; backend tìm mẫu trong `BaseLearningPath`, ánh xạ kỹ năng vào `Skill`, mở rộng kỹ năng học trước bằng `SkillRelation`, rồi trả bản đề xuất (chưa lưu). Khi học viên chấp nhận, `POST /api/learning-paths` tạo `LearningPath`, các `LearningPathNode` và `LearningPathEdge`.
- **Gợi ý khóa học:** chỉ chạy khi học viên chọn một nút. Backend truy vấn `CourseSkillRelation` JOIN `Course`, xếp hạng theo mức liên quan tới kỹ năng, `rating` và `num_reviews`. Kết quả không lưu sẵn và không dùng điểm ôn tập để xếp hạng.
- **Theo dõi khóa học:** lưu khóa học tạo dòng `StudentCourse` ở trạng thái `bookmarked`; bấm tham gia chuyển sang `ongoing`, ghi `joined_at` và trả URL ngoài; từ bỏ chuyển sang `abandoned`.
- **Gia sư AI:** mỗi phiên là một dòng `ChatSession` (`session_type = 'tutor'`), tin nhắn nằm ở `ChatMessage`.
- **Ôn tập:** tạo `ReviewAttempt` gắn với `StudentCourse` và 20 dòng `ReviewAnswer` lấy từ `Question`; khi nộp bài, server chấm điểm, nếu đạt thì cập nhật `UserSkill` và `StudentCourse`.
- **Quên mật khẩu:** học viên nhập email, hệ thống tạo một dòng `PasswordResetToken` và gửi link qua email; khi học viên đặt mật khẩu mới thì kiểm tra mã, cập nhật `User.hashed_password` và ghi `used_at`.
- **Gửi phản hồi:** học viên chọn phản hồi về khóa học hoặc về hệ thống, hệ thống lưu một dòng `Feedback` gắn với `User` (và với `Course` nếu phản hồi về khóa học); khung liên hệ bên phải lấy từ `Course.instructor` và `CourseContact`.
