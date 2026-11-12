# ĐẶC TẢ YÊU CẦU PHẦN MỀM (SOFTWARE REQUIREMENTS SPECIFICATION - SRS)

**Hệ thống Đào tạo Lập trình viên Quốc tế FPT Aptech · Chương trình Học kỳ 2**

Tài liệu Đặc tả Kỹ thuật Đồ án Tốt nghiệp Cuối kỳ (Capstone Project) · Phiên bản 3.0 (05/11/2026)

**ĐỀ TÀI 03: TRỢ LÝ HỌC TẬP THÔNG MINH & HỆ THỐNG GỢI Ý KHÓA HỌC CÁ NHÂN HÓA**
(AI Educational Assistant, Hybrid Course Recommender & Stateful Chatbot Backend API)

Hệ thống web kết hợp gợi ý lộ trình học tập theo mục tiêu học viên, gợi ý khóa học MOOC, Chatbot gia sư AI có bộ nhớ phiên và hệ thống ôn tập theo khóa học.

| Mục | Nội dung |
|---|---|
| Chuyên mục | Hệ thống gợi ý (Recommender System) · Trợ lý hội thoại (Conversational Chatbot) · Web App + Backend API |
| Môn học tích hợp | Python · AI Fundamental · NLP · FastAPI · Docker |
| Sinh viên thực hiện | Nguyễn Lê Nhật Hòa, Phạm Thanh Tuấn, Tống Quyết Tâm, Đỗ Lê Khôi |
| Thời lượng | 4 đến 6 tuần (báo cáo và bảo vệ trước Hội đồng) |
| Chuẩn giao diện | Bộ giao diện demo `docs/EduMentor-UI-design/ui-design`; SRS này và tài liệu BA được viết lại để khớp với demo |

## Mục lục

1. Bối cảnh thực tế và sự cần thiết của ứng dụng
2. Giải pháp đề xuất và kiến trúc hệ thống
3. Vai trò người dùng và phân quyền
4. Yêu cầu chức năng chi tiết
5. Tóm tắt API RESTful
6. Phân luồng hệ thống theo vai trò
7. Thiết kế cơ sở dữ liệu (các bảng chính)

---

## 1. Bối cảnh thực tế và sự cần thiết của ứng dụng

### 1.1. Bối cảnh ngành EdTech và khủng hoảng định hướng học tập

Sự bùng nổ của các khóa học trực tuyến (Coursera, Udemy, edX) mang lại kho tri thức lớn, nhưng cũng đẩy người học vào "ma trận" thông tin. Người mới bắt đầu thường không biết nên học kỹ năng nào trước, các kỹ năng có quan hệ tiên quyết ra sao để đạt mục tiêu việc làm (ví dụ: Kỹ sư Backend AI, Chuyên viên Phân tích Dữ liệu).

Trong quá trình tự học lập trình, sinh viên thường gặp lỗi cú pháp hoặc khái niệm trừu tượng (con trỏ, Async/Await, Docker Network). Không có trợ lý giải đáp tức thì khiến nhiều người bỏ dở khóa học.

### 1.2. Mục tiêu hệ thống EduMentor AI

EduMentor AI giải quyết ba bài toán:

1. **Gợi ý lộ trình và khóa học (Hybrid Recommender):** Phân tích mục tiêu nghề nghiệp viết bằng ngôn ngữ tự nhiên, kết hợp mô hình ngôn ngữ lớn, đồ thị kỹ năng, kỹ năng hiện có của học viên và lộ trình của học viên tương tự để tạo lộ trình học tập dạng đồ thị kỹ năng, rồi gợi ý khóa học cho từng kỹ năng.
2. **Trợ lý Gia sư AI (Stateful Chatbot):** Nhớ ngữ cảnh hội thoại nhiều lượt theo phiên, giải thích code mẫu, phân tích lỗi và giao câu hỏi củng cố.
3. **Ôn tập theo khóa học:** Bài 20 câu trắc nghiệm từ ngân hàng câu hỏi theo các kỹ năng của khóa học; đạt bài thì khóa học được ghi nhận hoàn thành và kỹ năng được cập nhật.

EduMentor AI không lưu nội dung khóa học và không đăng ký hay thanh toán thay người dùng trên nền tảng bên ngoài.

---

## 2. Giải pháp đề xuất và kiến trúc hệ thống

| Tầng kiến trúc | Trách nhiệm và chức năng |
|---|---|
| Web Frontend (React + Vite) | Giao diện theo bộ demo: trang công khai cho Khách, khu vực học viên, khu vực quản trị; giao diện Tối/Sáng; bong bóng hỗ trợ. |
| API Gateway (FastAPI) | Tiếp nhận request, xác thực JWT (access token và refresh token), phân quyền Khách, Học viên, Admin, chuyển tới các module nghiệp vụ. |
| Session Memory Manager | Lưu lịch sử hội thoại theo phiên trong cơ sở dữ liệu; khi trả lời chỉ nạp các tin nhắn gần nhất (cửa sổ trượt, mặc định 6 tin) để không vượt giới hạn token. |
| Hybrid Recommender Engine | Tầng 1: lọc khóa học ứng viên theo ánh xạ khóa học và kỹ năng do Admin quản lý, kết hợp cấp độ. Tầng 2: LLM diễn giải mục tiêu; backend ánh xạ kỹ năng, mở rộng quan hệ tiên quyết, tham khảo mẫu lộ trình và lộ trình lịch sử (collaborative filtering), xếp hạng khóa học theo độ phù hợp, điểm và số lượt đánh giá. |
| AI Inference & Tutoring Service | Mô hình ngôn ngữ lớn với system prompt riêng cho AI Consultant, AI Tutor và AI tư vấn khóa học. |
| Review Engine | Lấy 20 câu trắc nghiệm từ ngân hàng câu hỏi, lưu bài làm dở, chấm theo đáp án lưu sẵn (đạt từ 60%), cập nhật khóa học và kỹ năng, gửi email kết quả. |
| Database Layer (PostgreSQL) | Người dùng, kỹ năng, khóa học, lộ trình, theo dõi khóa học, phiên chat, câu hỏi và bài ôn tập, phản hồi, dữ liệu lộ trình lịch sử. |
| Email Service | Gửi liên kết đặt lại mật khẩu và email kết quả ôn tập. |

---

## 3. Vai trò người dùng và phân quyền

| Vai trò | Mô tả | Được phép |
|---|---|---|
| Khách | Người chưa đăng nhập; không có tài khoản, không lưu trong cơ sở dữ liệu | Đăng ký, đăng nhập, quên và đặt lại mật khẩu; xem danh mục khóa học; xem trang Liên hệ ở chế độ chỉ đọc; bong bóng hỗ trợ và AI tư vấn khóa học |
| Học viên (`student`) | Tài khoản tạo khi đăng ký | Mọi chức năng học tập trên dữ liệu của chính mình: hồ sơ, kỹ năng, khóa học của tôi, lộ trình, AI Tutor, ôn tập, gửi phản hồi |
| Admin (`admin`) | Tài khoản tạo bằng script quản trị, không đăng ký qua giao diện | Quản lý khóa học, kỹ năng và quan hệ, câu hỏi ôn tập, mẫu lộ trình, dữ liệu lịch sử; xem phản hồi; xem lộ trình người dùng (chỉ đọc) |

Khi Khách bấm một chức năng cần đăng nhập, hệ thống chuyển tới trang Đăng nhập. Quyền được kiểm tra ở phía máy chủ; vai trò lấy từ cơ sở dữ liệu, không chỉ dựa vào token.

---

## 4. Yêu cầu chức năng chi tiết

| Mã | Chức năng | Mô tả nghiệp vụ | Vai trò |
|---|---|---|---|
| FR-01 | Xác thực | Đăng ký (họ tên, email, mật khẩu, xác nhận), đăng nhập cấp JWT, làm mới phiên bằng refresh token, đăng xuất thu hồi refresh token. Màn đăng nhập và đăng ký có hiệu ứng dây kéo đèn: mở trang thì đèn tắt và form ẩn, kéo dây thì form hiện. | Khách, Học viên |
| FR-02 | Quên và đặt lại mật khẩu | Nhập email nhận liên kết; luôn báo "đã gửi" chung; liên kết có hạn và dùng một lần; liên kết hết hạn có màn riêng. Quy tắc mật khẩu giống nhau cho đăng ký, đặt lại, đổi. | Khách |
| FR-03 | Hồ sơ học viên | Xem hồ sơ và thống kê (khóa đang học, đã hoàn thành, kỹ năng đã biết, lộ trình đang theo); sửa họ tên; đổi ảnh đại diện bằng tải file; email chỉ đọc; đổi mật khẩu; chọn giao diện Tối/Sáng. | Học viên |
| FR-04 | Kỹ năng của tôi | Thêm kỹ năng từ danh mục, đổi trạng thái Đã biết/Đang học, xóa, hoàn tác, lưu một lần. | Học viên |
| FR-05 | Danh mục khóa học | Tìm theo từ khóa, lọc cấp độ, sắp xếp theo điểm hoặc số lượt đánh giá; chi tiết khóa học với kỹ năng và trạng thái theo dõi. | Khách (danh mục), Học viên |
| FR-06 | Theo dõi khóa học | Lưu khóa học, tham gia (ghi nhận Đang học và mở trang ngoài), ngừng theo dõi, bỏ lưu; Khóa học của tôi theo 4 trạng thái Đã lưu, Đang học, Đã hoàn thành, Đã bỏ. Hoàn thành chỉ có được khi đạt bài ôn tập. | Học viên |
| FR-07 | AI tư vấn lộ trình | Học viên nhập mục tiêu; AI hỏi lại nếu chưa rõ; hệ thống trả bản nháp lộ trình dạng đồ thị kỹ năng (node và cạnh tiên quyết); chỉ lưu khi học viên bấm Lưu lộ trình này. | Học viên |
| FR-08 | Quản lý lộ trình | Lộ trình của tôi lọc theo Đang theo, Hoàn thành, Đã từ bỏ; chi tiết lộ trình với đồ thị, đổi tên, từ bỏ; thêm, xóa kỹ năng (vai trò Tiên quyết, Tùy chọn, Mở rộng) và kết nối. | Học viên |
| FR-09 | Gợi ý khóa học theo kỹ năng | Chọn một kỹ năng trong lộ trình để xem khóa học gợi ý, sắp xếp theo điểm hoặc số lượt đánh giá; lưu hoặc tham gia ngay. | Học viên |
| FR-10 | AI Tutor | Tạo, chọn, xóa phiên chat; hội thoại nhiều lượt nhớ ngữ cảnh theo phiên; giải thích code, phân tích lỗi; trả về khối mã và câu hỏi trắc nghiệm củng cố; báo lỗi có nút Gửi lại. | Học viên |
| FR-11 | Ôn tập theo khóa học | 20 câu trắc nghiệm (4 lựa chọn) chia đều theo kỹ năng của khóa; cần đã tham gia khóa và đủ 20 câu; tạm rời và làm tiếp; câu bỏ trống tính sai; đạt từ 60%; làm lại không giới hạn; đạt thì khóa thành Hoàn thành và kỹ năng thành Đã biết; gửi email kết quả. | Học viên |
| FR-12 | Lịch sử ôn tập | Lọc theo khóa học và kết quả, phân trang; chi tiết từng câu, lọc câu sai; giải thích ẩn mặc định, có Xem giải thích và Hiện tất cả. | Học viên |
| FR-13 | Liên hệ và phản hồi | Gửi phản hồi về một khóa học hoặc hệ thống, chọn loại phản hồi, nội dung tối đa 1000 ký tự, tự gắn tài khoản; xem thông tin liên hệ của khóa học và EduMentor. Khách chỉ xem, form bị khóa. | Học viên, Khách (chỉ xem) |
| FR-14 | Bong bóng hỗ trợ và AI tư vấn khóa học | Bong bóng góc phải dưới: GitHub, Zalo, Liên hệ, AI tư vấn khóa học. Không hiển thị ở AI tư vấn lộ trình, AI Tutor, màn làm bài và trang quản trị. AI chỉ gợi ý khóa học trong danh mục. | Khách, Học viên |
| FR-15 | Quản trị khóa học | Tìm, thêm, sửa, xóa khóa học; liên kết kỹ năng sau khi lưu khóa học. | Admin |
| FR-16 | Quản trị kỹ năng và quan hệ | Tìm, thêm, xóa kỹ năng (không trùng tên, không xóa kỹ năng đang dùng); bấm kỹ năng mở sơ đồ quan hệ Học trước/Mở ra; tạo, đổi loại, xóa quan hệ. | Admin |
| FR-17 | Quản trị câu hỏi ôn tập | Thêm, sửa, xóa câu hỏi trắc nghiệm theo kỹ năng: nội dung, 4 lựa chọn, đáp án, giải thích. | Admin |
| FR-18 | Mẫu lộ trình | Tạo mẫu; sửa tên và mục tiêu phù hợp; thêm kỹ năng và kết nối; ngừng dùng; lưu thay đổi. | Admin |
| FR-19 | Dữ liệu lịch sử | Kéo thả file nhập dữ liệu lộ trình lịch sử, đánh dấu dữ liệu tổng hợp, xem kết quả nhập và danh sách bản ghi. | Admin |
| FR-20 | Quản trị phản hồi | Thẻ số liệu, tab theo đối tượng, tìm kiếm, lọc loại và thời gian, sắp xếp, ngăn chi tiết, trả lời qua email. Không có trạng thái xử lý. | Admin |
| FR-21 | Lộ trình người dùng | Xem chỉ đọc danh sách người dùng, mục tiêu phổ biến, lộ trình và tiến độ kỹ năng của từng người, đồ thị chỉ xem. | Admin |

---

## 5. Tóm tắt API RESTful

Mọi endpoint bắt đầu bằng `/api/`. Chi tiết request, response và quy tắc nằm ở tài liệu BA mục 10.

| Nhóm | Endpoint chính | Quyền |
|---|---|---|
| Xác thực | `POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/forgot-password`, `/auth/reset-password` | Công khai (logout cần đăng nhập) |
| Hồ sơ | `GET/PATCH /me`, `POST /me/avatar`, `POST /me/change-password`, `GET /me/summary`, `GET/PATCH /me/skills` | Học viên |
| Khóa học | `GET /courses`, `GET /courses/{id}`, `GET /courses/{id}/skills`, `GET /courses/{id}/contact` | Công khai |
| Theo dõi khóa học | `POST/GET/DELETE /me/bookmarks`, `POST /courses/{id}/join`, `GET /me/courses`, `GET/PATCH /me/courses/{id}/status`, `DELETE /me/courses/{id}` | Học viên |
| Lộ trình | `POST /chat/learning-path`, `POST /learning-paths`, `GET /me/learning-paths`, `GET/PATCH/DELETE /learning-paths/{id}`, node và cạnh `/learning-paths/{id}/nodes`, `/edges`, gợi ý `/learning-paths/{id}/nodes/{skill_id}/courses` | Học viên |
| AI Tutor | `GET/POST /chat/sessions`, `GET/DELETE /chat/sessions/{id}`, `POST /chat/sessions/{id}/messages` | Học viên |
| Ôn tập | `GET /courses/{id}/review`, `POST /courses/{id}/review-attempts`, `GET /review-attempts/{id}`, `PATCH /review-attempts/{id}/answers`, `POST /review-attempts/{id}/submit`, `GET /me/review-history`, `GET /me/review-history/{id}` | Học viên |
| Phản hồi | `POST /feedback` | Học viên |
| AI tư vấn khóa học | `POST /chat/course-advisor` | Công khai |
| Quản trị | `/admin/courses`, `/admin/skills`, `/admin/skill-relations`, `/admin/course-skill-relations`, `/admin/questions`, `/admin/base-learning-paths`, `/admin/historical-learning-paths`, `/admin/feedback`, `/admin/users`, `/admin/users/{id}/learning-paths`, `/admin/learning-path-goals` | Admin |

---

## 6. Phân luồng hệ thống theo vai trò

### 6.1. Truy cập hệ thống

1. Người truy cập mở trang. Chưa đăng nhập thì là Khách.
2. Khách xem danh mục khóa học, trang Liên hệ chỉ đọc, bong bóng hỗ trợ.
3. Khách đăng ký hoặc đăng nhập (quên mật khẩu thì nhận liên kết qua email).
4. Sau khi đăng nhập: Học viên vào trang Hồ sơ; Admin vào trang Quản trị khóa học.
5. Bấm chức năng cần đăng nhập khi đang là Khách thì chuyển tới Đăng nhập.

### 6.2. Luồng học viên

1. Cập nhật hồ sơ và kỹ năng hiện có.
2. Mở AI tư vấn lộ trình, nhập mục tiêu, xem bản nháp đồ thị kỹ năng, lưu lộ trình.
3. Trong chi tiết lộ trình, chọn một kỹ năng để xem khóa học gợi ý; lưu hoặc tham gia khóa học.
4. Tham gia khóa học: trạng thái Đang học, mở trang khóa học bên ngoài, kỹ năng của khóa thành Đang học.
5. Trong lúc học, hỏi AI Tutor theo từng phiên.
6. Làm bài ôn tập của khóa: đạt từ 60% thì khóa thành Hoàn thành, kỹ năng thành Đã biết, nhận email kết quả.
7. Xem lịch sử ôn tập, gửi phản hồi qua trang Liên hệ khi cần.

### 6.3. Luồng Admin

1. Quản lý kỹ năng và quan hệ kỹ năng.
2. Quản lý khóa học và liên kết khóa học với kỹ năng.
3. Nhập câu hỏi ôn tập cho từng kỹ năng (tối thiểu đủ 20 câu cho mỗi khóa).
4. Tạo mẫu lộ trình cho mục tiêu phổ biến; nhập dữ liệu lộ trình lịch sử.
5. Xem phản hồi của học viên và trả lời qua email.
6. Xem lộ trình người dùng để theo dõi mục tiêu phổ biến (chỉ đọc).

---

## 7. Thiết kế cơ sở dữ liệu (các bảng chính)

| Bảng | Nội dung chính |
|---|---|
| User | Họ tên, email (duy nhất), mật khẩu đã băm, vai trò (`student`, `admin`), ảnh đại diện, ngày tham gia |
| RefreshToken | Bản băm refresh token, hạn dùng, thời điểm thu hồi, người dùng |
| PasswordResetToken | Bản băm token đặt lại mật khẩu, hạn dùng, đã dùng chưa |
| Skill | Tên kỹ năng (duy nhất), mô tả, đang dùng |
| SkillRelation | Kỹ năng nguồn, kỹ năng đích, loại quan hệ (tiên quyết, mở rộng, liên quan) |
| Course | Tên, nhà cung cấp, mô tả, cấp độ, điểm đánh giá, số lượt đánh giá, liên kết ngoài, thông tin liên hệ |
| CourseSkill | Liên kết khóa học và kỹ năng |
| UserSkill | Người dùng, kỹ năng, trạng thái (`known`, `learning`), thời điểm cập nhật |
| StudentCourse | Người dùng, khóa học, trạng thái (`bookmarked`, `ongoing`, `completed`, `abandoned`) |
| LearningPath, PathNode, PathEdge | Lộ trình của người dùng, mục tiêu, nguồn (mẫu hoặc tự tạo), trạng thái; node kỹ năng với vai trò; cạnh giữa các node |
| BaseLearningPath (+ node, cạnh) | Mẫu lộ trình do Admin quản lý |
| HistoricalLearningPath, HistoricalImport | Dữ liệu lộ trình lịch sử và các lần nhập |
| ChatSession, ChatMessage | Phiên AI Tutor và tin nhắn |
| ReviewQuestion | Kỹ năng, nội dung, 4 lựa chọn, đáp án đúng, giải thích |
| ReviewAttempt, ReviewAnswer | Lần làm bài (khóa học, trạng thái làm dở/đã nộp, điểm, đạt hay không, thời điểm nộp) và câu trả lời từng câu |
| Feedback | Người gửi, đối tượng (khóa học hoặc hệ thống), khóa học, loại phản hồi, nội dung, thời gian |

Sơ đồ ERD chi tiết và các ràng buộc khóa ngoại được vẽ lại theo bảng trên trước khi viết migration.
