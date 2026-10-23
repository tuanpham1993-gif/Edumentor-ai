# EduMentor AI — Đặc tả API Endpoint

## 1. Quy ước API

- Tất cả endpoint đều bắt đầu bằng `/api/`.
- Sử dụng các HTTP method theo chuẩn RESTful: `GET`, `POST`, `PATCH` và `DELETE`.
- `{id}` đại diện cho mã định danh của một tài nguyên.
- Các endpoint dành riêng cho người dùng sẽ thao tác trên dữ liệu của người dùng đã xác thực.
- Liên kết khóa học trỏ đến các nền tảng MOOC bên ngoài. EduMentor không lưu trữ nội dung khóa học và không trực tiếp quản lý việc đăng ký khóa học trên các nền tảng đó.
- Xóa một lộ trình học tập có nghĩa là chuyển trạng thái sang `abandoned`, thay vì xóa vĩnh viễn lịch sử.
- EduMentor chỉ theo dõi tiến trình học tập ở mức cơ bản, không theo dõi từng bài học, tiến độ xem video hoặc mức độ hoàn thành nội dung khóa học.

---

## 2. Xác thực và hồ sơ người dùng

> Cập nhật theo sheet "Endpoint (bản mới)" của `docs/EduMentor_Checklist_Da_Sua_API.xlsx`. Contract chi tiết (request, response, lỗi, quy tắc): `docs/modules/auth-profile.md`.

| Method | Endpoint | Mô tả | Quyền |
|---|---|---|---|
| POST | `/api/auth/register` | Đăng ký tài khoản mới. `role` luôn là `student`, không nhận từ client. *(T09)* | Công khai |
| POST | `/api/auth/login` | Xác thực và trả access token kèm thông tin người dùng (gồm `role`). | Công khai |
| POST | `/api/auth/logout` | Đăng xuất. JWT không lưu trạng thái: client xóa token, server trả 200. *(D08)* | Người dùng |
| POST | `/api/auth/forgot-password` | Yêu cầu đặt lại mật khẩu qua email; luôn trả cùng một thông báo. *(T01)* | Công khai |
| POST | `/api/auth/reset-password` | Đặt mật khẩu mới bằng mã trong email (dùng một lần, có hạn). *(T02)* | Công khai |
| GET | `/api/me` | Lấy hồ sơ của người dùng đã xác thực. | Người dùng |
| PATCH | `/api/me` | Cập nhật hồ sơ: chỉ `full_name`, `avatar_url` (không có `email`, `role`). *(T04, D06, T09)* | Người dùng |
| POST | `/api/me/avatar` | Tải ảnh đại diện lên (tùy chọn, giai đoạn 2). *(T04, D07)* | Người dùng |
| POST | `/api/me/change-password` | Đổi mật khẩu khi đã đăng nhập. *(T03)* | Người dùng |
| GET | `/api/me/summary` | Số liệu tổng hợp cho trang Profile. *(T05)* | Người dùng |
| GET | `/api/me/skills` | Kỹ năng trong hồ sơ; lọc `?status=known\|learning`. *(T07)* | Người dùng |
| PATCH | `/api/me/skills` | Thêm/sửa/xóa kỹ năng (`add`, `update`, `remove`) trong một transaction. *(T06)* | Người dùng |
| GET | `/api/me/courses` | Khóa học đang theo dõi, mặc định loại trừ `abandoned`. | Người dùng |
| GET | `/api/me/courses?status=ongoing` | Khóa học đã tham gia và đang theo dõi. | Người dùng |
| GET | `/api/me/courses?status=bookmarked` | Khóa học đã lưu để học sau. | Người dùng |
| GET | `/api/me/courses?status=completed` | Khóa học đã hoàn thành. | Người dùng |
| GET | `/api/me/courses?status=abandoned` | Khóa học đã bỏ (xem lịch sử). *(T08)* | Người dùng |

> `/api/me/courses*` thuộc module theo dõi khóa học (`routers/me_courses.py`, `course_tracking_service`), không thuộc module Xác thực & Hồ sơ.

### Quy tắc cập nhật kỹ năng người dùng

- Khi người dùng **làm đạt** bài ôn tập của một khóa học, backend tự thêm hoặc cập nhật `known` cho mọi kỹ năng của khóa đó (qua `CourseSkillRelation`), trong cùng transaction nộp bài. Frontend **không** gửi request cập nhật kỹ năng riêng. *(T13)*
- Khi người dùng bấm tham gia khóa học (`POST /api/courses/{course_id}/join`), backend thêm các kỹ năng của khóa ở trạng thái `learning`; kỹ năng đã `known` giữ nguyên. *(D05)*
- Frontend có thể dùng `PATCH /api/me/skills` để cập nhật thủ công. *(T06)*

---

## 3. Danh mục khóa học

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/courses` | Lấy danh mục khóa học. |
| GET | `/api/courses/{course_id}` | Lấy thông tin chi tiết của một khóa học. |
| GET | `/api/courses?search={keyword}` | Tìm kiếm khóa học theo từ khóa. |
| GET | `/api/courses?skill_id={skill_id}` | Lọc khóa học theo kỹ năng. |
| GET | `/api/courses?level={level}` | Lọc khóa học theo cấp độ. |
| GET | `/api/courses?sort_by=rating` | Sắp xếp khóa học theo điểm đánh giá. |
| GET | `/api/courses?sort_by=num_reviews` | Sắp xếp khóa học theo số lượng lượt đánh giá. |
| GET | `/api/courses/{course_id}/skills` | Lấy danh sách kỹ năng liên quan đến một khóa học. |

Có thể kết hợp nhiều bộ lọc và tùy chọn sắp xếp bằng các query parameter.

---

## 4. Lưu khóa học và theo dõi trạng thái

EduMentor sử dụng bốn trạng thái theo dõi khóa học:

- `bookmarked`: Đã lưu để học sau.
- `ongoing`: Người dùng đã chọn truy cập và học khóa học bên ngoài.
- `completed`: Người dùng đã hoàn thành bài kiểm tra ôn tập liên quan.
- `abandoned`: Người dùng đã ngừng theo dõi khóa học.

Đây là các trạng thái theo dõi của EduMentor, không phải trạng thái đăng ký hoặc hoàn thành được báo cáo từ nền tảng MOOC bên ngoài.

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/me/bookmarks` | Lưu một khóa học để học sau bằng `course_id`. |
| GET | `/api/me/bookmarks` | Lấy danh sách khóa học đã lưu. |
| DELETE | `/api/me/bookmarks/{course_id}` | Xóa khóa học khỏi danh sách đã lưu. |
| POST | `/api/courses/{course_id}/join` | Ghi nhận khóa học ở trạng thái `ongoing` và trả về URL bên ngoài để chuyển hướng người dùng. |
| GET | `/api/me/courses/{course_id}/status` | Lấy trạng thái theo dõi hiện tại của người dùng đối với khóa học. |
| PATCH | `/api/me/courses/{course_id}/status` | Cập nhật trạng thái theo dõi khi cần chuyển sang một trạng thái được phép. |
| DELETE | `/api/me/courses/{course_id}` | Ngừng theo dõi khóa học bằng cách chuyển trạng thái sang `abandoned`. |

### Quy tắc theo dõi khóa học

1. Lưu khóa học sẽ tạo một bản ghi bookmark.
2. Tham gia khóa học sẽ ghi nhận trạng thái `ongoing` và trả về URL khóa học bên ngoài. Thao tác này không đăng ký khóa học thay người dùng trên nền tảng bên ngoài.
3. Xóa bookmark sẽ xóa bản ghi bookmark. Thao tác này không tự động chuyển khóa học sang `abandoned`, trừ khi đã có bản ghi theo dõi khóa học và người dùng chủ động từ bỏ khóa học.
4. Các khóa học ở trạng thái `abandoned` bị loại khỏi danh sách mặc định, nhưng có thể được xem thông qua bộ lọc lịch sử nếu cần.
5. Làm **đạt** bài ôn tập của khóa học (≥ `REVIEW_PASS_PERCENT`, xem §10) sẽ đánh dấu khóa học là `completed` và cập nhật các kỹ năng liên quan trong hồ sơ người dùng. *(T13, D02)*
6. Không đánh dấu khóa học là hoàn thành chỉ vì người dùng đã mở URL bên ngoài.

---

## 5. Tạo lộ trình học tập và AI Consultant

Lộ trình học tập được tạo thông qua cuộc hội thoại với AI Consultant. Mô hình diễn giải mục tiêu của người dùng, trong khi backend chịu trách nhiệm ánh xạ kỹ năng, mở rộng các quan hệ liên quan, tham khảo những lộ trình lịch sử tương tự và lưu lộ trình kết quả.

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/chat/learning-path` | Gửi mục tiêu để AI Consultant tạo lộ trình học tập đề xuất. |
| GET | `/api/me/learning-paths` | Lấy các lộ trình học tập của người dùng đã xác thực. |
| GET | `/api/learning-paths/{path_id}` | Lấy thông tin chi tiết của lộ trình, bao gồm trạng thái và các node. |
| POST | `/api/learning-paths` | Lưu hoặc chấp nhận một lộ trình học tập được đề xuất. |
| PATCH | `/api/learning-paths/{path_id}` | Cập nhật thông tin hoặc trạng thái lộ trình. |
| DELETE | `/api/learning-paths/{path_id}` | Từ bỏ lộ trình bằng cách chuyển trạng thái sang `abandoned`. |

### Trạng thái lộ trình học tập

- `ongoing`: Người dùng đang theo đuổi lộ trình.
- `completed`: Tất cả node bắt buộc đã hoàn thành hoặc được công nhận là đã biết.
- `abandoned`: Người dùng đã ngừng theo đuổi lộ trình.

Lộ trình được đề xuất không nên tự động trở thành lộ trình đã được chấp nhận cho đến khi người dùng xác nhận hoặc lưu lại.

Nếu người dùng chỉ thực hiện các thay đổi nhỏ, hệ thống nên cập nhật lộ trình hiện tại. Nếu họ thay thế lộ trình bằng một mục tiêu hoặc lộ trình khác biệt đáng kể, hệ thống nên tạo lộ trình mới và giữ lại lịch sử của lộ trình cũ.

---

## 6. Các node trong lộ trình học tập

Mỗi node đại diện cho một kỹ năng thuộc một lộ trình học tập cụ thể.

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/learning-paths/{path_id}/nodes` | Lấy tất cả node kỹ năng trong lộ trình. |
| POST | `/api/learning-paths/{path_id}/nodes` | Thêm một node kỹ năng vào lộ trình. |
| GET | `/api/learning-paths/{path_id}/nodes/{skill_id}` | Lấy thông tin chi tiết của một node. |
| PATCH | `/api/learning-paths/{path_id}/nodes/{skill_id}` | Cập nhật thuộc tính node như `node_role`, `added_by` hoặc `display_order`. |
| DELETE | `/api/learning-paths/{path_id}/nodes/{skill_id}` | Xóa node kỹ năng và các cạnh liên quan trong lộ trình. |

### Quy tắc node

- Khóa chính tổng hợp là `(path_id, skill_id)`.
- Một kỹ năng chỉ được xuất hiện một lần trong cùng một lộ trình.
- `node_role` có thể là `prerequisite`, `optional`, `extension` hoặc `NULL`.
- `added_by` có giá trị `system` hoặc `user`.
- `display_order` quyết định thứ tự hiển thị, không xác định quan hệ tiên quyết.
- Vai trò kỹ năng mục tiêu cần được lưu riêng, không gộp chung với `node_role`.
- Nếu xóa một node đang được tham chiếu bởi các cạnh trong lộ trình, hệ thống phải xóa hoặc cập nhật những cạnh đó.

**Lưu ý:** Thiết kế bảng hiện tại cũng cần một trường như `is_required` nếu muốn phân biệt node bắt buộc với node tùy chọn khi xác định lộ trình đã hoàn thành hay chưa.

---

## 7. Các cạnh trong lộ trình học tập

Các cạnh đại diện cho mối liên kết giữa những node kỹ năng trong một lộ trình cụ thể.

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/learning-paths/{path_id}/edges` | Lấy tất cả kết nối trong lộ trình. |
| POST | `/api/learning-paths/{path_id}/edges` | Thêm kết nối giữa hai node hiện có. |
| PATCH | `/api/learning-paths/{path_id}/edges/{from_skill_id}/{to_skill_id}` | Cập nhật loại quan hệ của một cạnh. |
| DELETE | `/api/learning-paths/{path_id}/edges/{from_skill_id}/{to_skill_id}` | Xóa một kết nối. |

### Quy tắc cạnh

- Cả hai kỹ năng ở hai đầu cạnh phải tồn tại dưới dạng node trong cùng một lộ trình.
- Khi quan hệ là `prerequisite`, kỹ năng nguồn được học trước kỹ năng đích.
- `relation_type` phải nhất quán với thiết kế bảng cạnh đã thống nhất.
- Xóa node không được để lại các cạnh mồ côi.

---

## 8. Gợi ý khóa học theo kỹ năng trong lộ trình

Hệ thống chỉ truy xuất gợi ý khi người dùng chọn một node kỹ năng, thay vì tự động gợi ý khóa học cho tất cả node ngay khi tạo lộ trình.

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/learning-paths/{path_id}/nodes/{skill_id}/courses` | Lấy các khóa học được đề xuất cho kỹ năng đã chọn. |
| GET | `/api/learning-paths/{path_id}/nodes/{skill_id}/courses?sort_by=rating` | Sắp xếp khóa học được đề xuất theo điểm đánh giá. |
| GET | `/api/learning-paths/{path_id}/nodes/{skill_id}/courses?sort_by=num_reviews` | Sắp xếp khóa học được đề xuất theo số lượt đánh giá. |

### Quy trình gợi ý

Backend cần thực hiện các bước sau:

1. Xác minh kỹ năng được chọn thuộc lộ trình tương ứng.
2. Truy xuất các khóa học có liên quan đến kỹ năng đó.
3. Xếp hạng hoặc lọc khóa học dựa trên mức độ liên quan đến kỹ năng, điểm đánh giá, số lượt đánh giá và các tín hiệu gợi ý đã thống nhất.
4. Trả về thông tin khóa học cùng URL bên ngoài.

API không nên xem điểm đánh giá cao là bằng chứng duy nhất cho thấy khóa học phù hợp nhất. Mức độ liên quan đến kỹ năng phải tiếp tục là yếu tố quan trọng hàng đầu.

---

## 9. Chat với AI Tutor

AI Tutor duy trì ngữ cảnh hội thoại trong từng phiên và hỗ trợ giải thích kiến thức, gỡ lỗi và tạo bài tập củng cố.

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/chat/sessions` | Tạo một phiên hội thoại mới với gia sư AI. |
| GET | `/api/chat/sessions` | Lấy danh sách phiên hội thoại của người dùng. |
| GET | `/api/chat/sessions/{session_id}` | Lấy thông tin phiên và lịch sử hội thoại. |
| POST | `/api/chat/sessions/{session_id}/messages` | Gửi tin nhắn và nhận phản hồi từ AI. |
| GET | `/api/chat/sessions/{session_id}/messages` | Lấy danh sách tin nhắn trong một phiên. |
| DELETE | `/api/chat/sessions/{session_id}` | Xóa hoặc lưu trữ phiên hội thoại theo chính sách lưu trữ dữ liệu. |

### Hành vi của AI Tutor

- Duy trì ngữ cảnh hội thoại trong phiên.
- Hỗ trợ giải thích khái niệm, cung cấp ví dụ mã nguồn và phân tích lỗi.
- Tạo bài tập củng cố, bao gồm ba câu hỏi trắc nghiệm dựa trên chủ đề vừa thảo luận khi phù hợp.
- Liên kết mỗi phiên hội thoại với người dùng đã xác thực.

Chức năng tạo lộ trình và chức năng gia sư có thể cùng sử dụng namespace `/api/chat/`, nhưng cần có endpoint và loại phiên riêng biệt.

---

## 10. Hệ thống ôn tập và đánh giá kiến thức

Hệ thống ôn tập truy xuất các câu hỏi có sẵn từ cơ sở dữ liệu và ghi nhận các lần làm bài của người dùng. Bài ôn tập tính **theo khóa học** *(D01 = A, T11)*: mỗi bài gồm **20 câu trắc nghiệm** lấy từ các kỹ năng mà khóa học đó dạy.

> Cập nhật theo sheet "Endpoint (bản mới)" của `docs/EduMentor_Checklist_Da_Sua_API.xlsx`. Contract chi tiết: `docs/modules/review-assessment.md`.

### API ôn tập theo khóa học

| Method | Endpoint | Mô tả | Quyền |
|---|---|---|---|
| GET | `/api/courses/{course_id}/review` | Kiểm tra khóa học có bài ôn tập khả dụng không (`available` và lý do nếu không). | Người dùng |
| POST | `/api/courses/{course_id}/review-attempts` | Bắt đầu một lần ôn tập: tạo lần làm bài và 20 câu (không kèm đáp án đúng). | Người dùng |
| GET | `/api/review-attempts/{attempt_id}` | Lấy trạng thái và câu hỏi của lần ôn tập. Không phải chủ sở hữu → 404. | Người dùng |
| POST | `/api/review-attempts/{attempt_id}/submit` | Nộp bài, chấm điểm, cập nhật hồ sơ trong một transaction; trả kết quả ngay rồi gửi email kết quả chạy nền. *(T13, T29)* | Người dùng |
| GET | `/api/me/review-history` | Lịch sử ôn tập; lọc `?course_id=`, `?passed=true\|false`; phân trang. *(T17)* | Người dùng |
| GET | `/api/me/review-history/{attempt_id}` | Chi tiết một lần: từng câu, đáp án đã chọn, đáp án đúng, giải thích (chỉ sau khi nộp). | Người dùng |

Các endpoint cũ **đã bỏ** *(T11)*:
- `GET /api/skills/{skill_id}/review` → thay bằng `GET /api/courses/{course_id}/review`.
- `POST /api/skills/{skill_id}/review-attempts` → thay bằng `POST /api/courses/{course_id}/review-attempts`.

`GET/PATCH /api/me/skills`: xem §2. *(Đề xuất T12 xóa hai dòng lặp này khỏi §10 chưa được nhóm tick — xem `docs/decisions.md`, ND-30.)*

### Quy trình ôn tập

1. Kiểm tra khóa học có bài ôn tập: tổng số câu `is_active` của các kỹ năng khóa dạy ≥ 20. *(D04)*
2. Bắt đầu: người dùng phải đang theo dõi khóa ở `ongoing` hoặc `completed` (ôn lại). Mỗi khóa tối đa một bài đang dở; bắt đầu lại thì trả bài dở đó. *(D03, D10)*
3. Server chọn 20 câu (chia đều giữa các kỹ năng, ngẫu nhiên) và lưu sẵn danh sách câu của lần làm bài. *(T14)*
4. Trả nội dung câu hỏi và các lựa chọn, **không** để lộ đáp án đúng hay giải thích trước khi nộp. *(T15)*
5. Chấm đúng 20 câu đã lưu; câu bỏ trống tính là sai. *(T16)*
6. Lưu điểm phần trăm và kết quả đạt (`≥ REVIEW_PASS_PERCENT`, nhóm chốt 60%). *(D02)*
7. Nếu đạt: đánh dấu khóa học `completed` (ôn lại không đổi trạng thái) và cập nhật kỹ năng `known` cho mọi kỹ năng của khóa — cùng một transaction với bước 5–6. *(T13)*
8. Sau khi lưu thành công: trả kết quả ngay, rồi gửi email kết quả chạy nền (lỗi gửi không ảnh hưởng kết quả). *(T29)*
9. Cung cấp kết quả qua lịch sử ôn tập.

Chính sách: làm lại **không giới hạn** *(D03)*; điểm đạt **60%** *(D02)*.

---

## 11. Quản trị — Danh mục khóa học và kỹ năng

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/admin/courses` | Lấy danh sách khóa học để quản trị. |
| POST | `/api/admin/courses` | Thêm khóa học mới. |
| GET | `/api/admin/courses/{course_id}` | Lấy chi tiết khóa học. |
| PATCH | `/api/admin/courses/{course_id}` | Cập nhật thông tin khóa học. |
| DELETE | `/api/admin/courses/{course_id}` | Xóa khóa học khỏi danh mục. |
| GET | `/api/admin/skills` | Lấy danh sách kỹ năng. |
| POST | `/api/admin/skills` | Thêm kỹ năng mới. |
| PATCH | `/api/admin/skills/{skill_id}` | Cập nhật thông tin kỹ năng. |
| DELETE | `/api/admin/skills/{skill_id}` | Xóa kỹ năng khi việc xóa không gây ảnh hưởng không mong muốn. |
| GET | `/api/admin/course-skill-relations` | Lấy danh sách liên kết giữa khóa học và kỹ năng. |
| POST | `/api/admin/course-skill-relations` | Liên kết một khóa học với một kỹ năng. |
| DELETE | `/api/admin/course-skill-relations/{course_id}/{skill_id}` | Xóa liên kết giữa khóa học và kỹ năng. |
| GET | `/api/admin/skill-relations` | Lấy danh sách quan hệ giữa các kỹ năng. |
| POST | `/api/admin/skill-relations` | Tạo quan hệ `prerequisite`, `extension` hoặc `related` giữa các kỹ năng. |
| PATCH | `/api/admin/skill-relations/{from_skill_id}/{to_skill_id}` | Cập nhật quan hệ giữa hai kỹ năng. |
| DELETE | `/api/admin/skill-relations/{from_skill_id}/{to_skill_id}` | Xóa quan hệ giữa hai kỹ năng. |
| GET | `/api/admin/questions` | Danh sách câu hỏi ôn tập (lọc `?skill_id=`, phân trang), kèm số câu đang hoạt động theo kỹ năng. *(T19)* |
| POST | `/api/admin/questions` | Thêm câu hỏi: `skill_id`, `content`, `options` (đúng 4 đáp án), `correct_index` (0–3), `explanation`. *(T19)* |
| GET | `/api/admin/questions/{question_id}` | Chi tiết câu hỏi (có đáp án đúng). *(T19)* |
| PATCH | `/api/admin/questions/{question_id}` | Sửa câu hỏi. *(T19)* |
| DELETE | `/api/admin/questions/{question_id}` | Chưa từng dùng trong bài làm → xóa thật; đã dùng → `is_active = false`. Response nêu rõ đã xóa hay vô hiệu hóa. *(T20)* |
| POST | `/api/admin/questions/import` | (Tùy chọn) Nhập hàng loạt từ CSV/JSON, trả báo cáo theo dòng. *(T21)* |

Các endpoint quản trị chỉ được phép sử dụng bởi quản trị viên đã được cấp quyền.

---

## 12. Quản trị admin — Lộ trình học tập cơ bản (Base Learning Paths)

Base learning path là các mẫu lộ trình có thể tái sử dụng, mô tả những kỹ năng mục tiêu ban đầu và mối quan hệ giữa chúng cho các mục tiêu phổ biến. Chúng giúp AI Consultant tạo ra điểm xuất phát nhất quán trước khi mở rộng lộ trình bằng đồ thị kỹ năng chung và các lộ trình lịch sử tương tự.

### API admin quản lý mẫu lộ trình

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/admin/base-learning-paths` | Lấy danh sách mẫu lộ trình học tập cơ sở. |
| POST | `/api/admin/base-learning-paths` | Tạo mẫu lộ trình mới. |
| GET | `/api/admin/base-learning-paths/{template_id}` | Lấy chi tiết mẫu, bao gồm kỹ năng mục tiêu và các kết nối. |
| PATCH | `/api/admin/base-learning-paths/{template_id}` | Cập nhật thông tin hoặc cấu hình mẫu. |
| DELETE | `/api/admin/base-learning-paths/{template_id}` | Vô hiệu hóa hoặc xóa mẫu theo quy tắc sử dụng và lưu trữ lịch sử. |
| GET | `/api/admin/base-learning-paths/{template_id}/nodes` | Lấy các kỹ năng trong mẫu lộ trình. |
| POST | `/api/admin/base-learning-paths/{template_id}/nodes` | Thêm kỹ năng vào mẫu. |
| PATCH | `/api/admin/base-learning-paths/{template_id}/nodes/{skill_id}` | Cập nhật node trong mẫu. |
| DELETE | `/api/admin/base-learning-paths/{template_id}/nodes/{skill_id}` | Xóa kỹ năng khỏi mẫu. |
| GET | `/api/admin/base-learning-paths/{template_id}/edges` | Lấy các kết nối giữa kỹ năng trong mẫu. |
| POST | `/api/admin/base-learning-paths/{template_id}/edges` | Thêm kết nối giữa các kỹ năng trong mẫu. |
| PATCH | `/api/admin/base-learning-paths/{template_id}/edges/{from_skill_id}/{to_skill_id}` | Cập nhật kết nối trong mẫu (tùy chọn). |
| DELETE | `/api/admin/base-learning-paths/{template_id}/edges/{from_skill_id}/{to_skill_id}` | Xóa kết nối trong mẫu (tùy chọn). |

### Quy trình tạo lộ trình từ mẫu cơ sở

Khi người học gửi mục tiêu:

1. Mô hình AI diễn giải yêu cầu và xác định mục tiêu cùng các kỹ năng đích.
2. Backend tìm mẫu lộ trình cơ sở phù hợp nếu có.
3. Backend ánh xạ các kỹ năng vào danh mục kỹ năng.
4. Mở rộng các quan hệ tiên quyết liên quan bằng đồ thị kỹ năng chung.
5. Truy xuất các lộ trình lịch sử tương tự và sử dụng chúng làm dữ liệu tham khảo bổ sung.
6. Tạo lộ trình đề xuất để người dùng xem xét và chấp nhận.

Mẫu lộ trình cơ sở cung cấp điểm xuất phát có thể tái sử dụng, nhưng không bắt buộc tất cả người dùng có cùng mục tiêu phải nhận một lộ trình giống hệt nhau.

---

## 13. Quản trị — Dữ liệu lộ trình học tập lịch sử (tùy chọn)

Các endpoint này không bắt buộc đối với phiên bản thử nghiệm ban đầu, nhưng hữu ích nếu quản trị viên cần kiểm tra hoặc nhập dữ liệu lịch sử phục vụ Collaborative Filtering.

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/admin/historical-learning-paths` | Lấy danh sách bản ghi lộ trình lịch sử. |
| GET | `/api/admin/historical-learning-paths/{record_id}` | Lấy chi tiết một bản ghi lịch sử. |
| POST | `/api/admin/historical-learning-path-imports` | Nhập một nhóm bản ghi lịch sử đã được kiểm tra. |
| GET | `/api/admin/historical-learning-path-imports/{import_id}` | Kiểm tra trạng thái và kết quả của một lần nhập dữ liệu. |

Quá trình nhập dữ liệu lịch sử cần kiểm tra các tham chiếu kỹ năng, quan hệ giữa các bản ghi, dữ liệu trùng lặp và sự phân biệt giữa dữ liệu tổng hợp với dữ liệu người dùng thực tế. Dữ liệu được nhập không được tự động ghi đè lên lộ trình đang sử dụng của người dùng.

---

## 14. Quy tắc chung cho API

- **Xác thực:** Các endpoint dành cho người dùng yêu cầu xác thực; endpoint quản trị yêu cầu quyền quản trị viên.
- **Kiểm tra dữ liệu:** Kiểm tra request body, ID, giá trị trạng thái được phép và các tham chiếu trước khi sửa dữ liệu.
- **Tính nhất quán:** Sử dụng transaction cho các thao tác sửa nhiều bản ghi liên quan, chẳng hạn như xóa node cùng các cạnh của nó.
- **Lịch sử:** Ưu tiên thay đổi trạng thái thay vì xóa vĩnh viễn đối với lộ trình và bản ghi theo dõi khóa học khi lịch sử cần được giữ lại để phân tích.
- **Xử lý lỗi:** Trả về cấu trúc lỗi nhất quán cho dữ liệu đầu vào không hợp lệ, truy cập trái phép, tài nguyên không tồn tại và chuyển trạng thái xung đột.
- **Phân trang:** Các endpoint trả về danh sách nên hỗ trợ phân trang khi số lượng kết quả có thể lớn.
- **Kiểm tra đầu ra AI:** Xác thực mục tiêu và kỹ năng do mô hình tạo ra bằng danh mục kỹ năng trước khi tạo lộ trình.
- **Gợi ý:** Không đưa điểm ôn tập vào xếp hạng khóa học, trừ khi quy tắc nghiệp vụ này được thay đổi rõ ràng sau đó.