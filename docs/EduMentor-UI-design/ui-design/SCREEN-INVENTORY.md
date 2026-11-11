# UI Screen Inventory

**Kiểm tra trực tiếp:** 2026-11-01, chạy UI Demo trong Chrome (artifact `7xPJPGauwsXLG9keRNKcxe`, phiên bản `1793285378-8eed`) và thao tác trên từng luồng. **Phạm vi:** demo chạy bằng dữ liệu mẫu, không gọi backend; "có thao tác" không có nghĩa là đã có API (D-FE-08, D-FE-12).

**Số liệu:** 33 route trong mục lục demo; 41 màn hoặc trạng thái có ảnh trong `pages.json`. Bong bóng hỗ trợ là thành phần dùng chung (S-34), không có route riêng.

**Hạn chế chung của demo (đã thử):** không có kiểm tra đăng nhập hay vai trò: sau khi đăng xuất vẫn mở được `/me` và `/admin/courses`; đăng nhập luôn vào `/me`; không có tài khoản Admin riêng; AI Consultant và Tutor trả nội dung soạn sẵn.

| ID | Màn (ảnh trong `png/`) | Route | Vai trò | Mục đích | Chức năng, thao tác chính | Trường dữ liệu | Trạng thái, điều kiện | Màn liên quan |
|---|---|---|---|---|---|---|---|---|
| S-01 | Main, Main-LampOff | `/login` | Khách | Đăng nhập | Kéo dây bật/tắt 3 đèn; đăng nhập; Quên mật khẩu; Đăng ký | Email, Mật khẩu | Đèn tắt: form ẩn, bị khóa. Sai: "Lỗi 401: …", rung form | S-02, S-03, S-07 |
| S-02 | Register | `/register` | Khách | Đăng ký tài khoản | Kéo dây (1 dây); gửi đăng ký; kiểm tra từng trường | Họ và tên, Email, Mật khẩu, Xác nhận mật khẩu | Đèn tắt: form ẩn. Lỗi họ tên, mật khẩu, xác nhận | S-01 |
| S-03 | ForgotPassword | `/forgot-password` | Khách | Yêu cầu đặt lại mật khẩu | Nhập email, gửi | Email | Email sai: "Nhập email hợp lệ." | S-01, S-04 |
| S-04 | ForgotSent | `/forgot-sent` | Khách | Thông báo đã gửi | Gửi lại; liên kết thử (chỉ demo) | — | Thông báo chung | S-03, S-05 |
| S-05 | ResetPassword | `/reset-password` | Khách | Đặt mật khẩu mới | Nhập, xác nhận, hiện mật khẩu | Mật khẩu mới, Xác nhận mật khẩu mới | Danh sách quy tắc | S-04, S-06, S-01 |
| S-06 | ResetExpired | `/reset-expired` | Khách | Báo liên kết hết hiệu lực | Gửi yêu cầu mới; quay lại đăng nhập | — | — | S-03, S-01 |
| S-07 | Profile, Profile-Light | `/me` | Học viên | Hồ sơ, thống kê | Đổi Tối/Sáng; Đăng xuất; tab khóa học; kỹ năng; ôn tập gần đây | — | Rỗng theo tab | S-08, S-09, S-10, S-11 |
| S-08 | EditProfile | `/me/edit` | Học viên | Sửa hồ sơ | Sửa họ tên; đổi ảnh bằng avatar; email, vai trò, ngày tham gia chỉ đọc | Họ và tên, Email, Vai trò, Ngày tham gia | Toast lưu | S-07 |
| S-09 | ChangePassword | `/me/password` | Học viên | Đổi mật khẩu | Nhập 3 ô; hiện mật khẩu | Mật khẩu hiện tại, Mật khẩu mới, Xác nhận mật khẩu mới | Danh sách quy tắc | S-07 |
| S-10 | Skills | `/me/skills` | Học viên | Kỹ năng của tôi | Tìm, thêm, đổi trạng thái, xóa, hoàn tác, lưu một lần | Thêm kỹ năng, Trạng thái | "N thay đổi chưa lưu"; rỗng theo tab | S-07 |
| S-11 | Logout | `/logout` | Học viên | Xác nhận đăng xuất | Đăng xuất, Hủy | — | Hộp thoại trên Hồ sơ | S-07, S-01 |
| S-12 | Courses, Courses-Light | `/courses` | Chưa xác định (ND-70) | Danh mục khóa học | Tìm, lọc Cấp độ, Sắp xếp, Lưu; không có lọc kỹ năng | Tìm khóa học, Cấp độ, Sắp xếp | "Không tìm thấy khóa học phù hợp." | S-13 |
| S-13 | CourseDetail | `/courses/1` | Học viên | Chi tiết khóa học | Xem kỹ năng, trạng thái; nút theo trạng thái; Làm bài ôn tập | — | Khác nhau theo trạng thái khóa | S-12, S-14, S-21 |
| S-14 | JoinDialog | `/courses/5/join` | Học viên | Xác nhận tham gia | Tham gia và mở khóa học, Để sau | — | Hộp thoại trên Chi tiết | S-13, S-15 |
| S-15 | MyCourses | `/me/courses` | Học viên | Khóa học của tôi | 4 tab; Mở khóa học, Ngừng theo dõi, Tham gia, Bỏ lưu, Ôn lại, Học tiếp | — | Rỗng theo tab | S-13, S-21 |
| S-16 | Consultant | `/consultant` | Học viên | AI tư vấn lộ trình | Chat, câu mẫu; bản nháp đồ thị; Lưu lộ trình này; Bỏ đề xuất | Tin nhắn | Mock: luôn trả cùng bản nháp; không có trạng thái hỏi lại | S-17, S-18 |
| S-17 | MyPaths | `/me/learning-paths` | Học viên | Lộ trình của tôi | Lọc 3 trạng thái; tiến độ | — | Rỗng theo tab | S-16, S-18 |
| S-18 | PathDetail | `/learning-paths/1` | Học viên | Chi tiết lộ trình | Đồ thị, chọn node, khóa học gợi ý, sắp xếp, Lưu, Tham gia; Đổi tên; Từ bỏ; Xóa kỹ năng | Sắp xếp | Hộp thoại xác nhận xóa, từ bỏ | S-17, S-19 |
| S-19 | PathEdit | `/learning-paths/1/edit` | Học viên | Thêm kỹ năng, kết nối | Kỹ năng, Vai trò (Tiên quyết/Tùy chọn/Mở rộng), Thứ tự, Mục tiêu; Từ, Đến, Loại (Tiên quyết/Tùy chọn) | Sắp xếp | Hộp thoại | S-18 |
| S-20 | Tutor | `/tutor` | Học viên | AI Tutor | Phiên mới, chọn, xóa phiên; chat; khối mã; quiz 1 câu | [0, 1, 2], [1, 2, 3], [0, 1, 2, 3], Tin nhắn cho AI Tutor | Mock trả lời mẫu; lỗi có Gửi lại | — |
| S-21 | ReviewStart | `/courses/1/review` | Học viên | Bắt đầu ôn tập | Tiếp tục bài dở; Bắt đầu; các lần trước | — | Có mẫu "khi chưa thể ôn tập" | S-13, S-22 |
| S-22 | ReviewQuiz | `/courses/1/review/attempt` | Học viên | Làm bài | 4 lựa chọn, câu trước/tiếp, bảng 20 câu, Tạm rời, Nộp bài | A. func, B. function, C. def, D. lambda | Hộp thoại báo số câu chưa trả lời | S-21, S-23 |
| S-23 | ReviewResult | `/review-result/101` | Học viên | Kết quả | Xem điểm; xem đáp án; làm lại | — | Đạt, Chưa đạt | S-22, S-25 |
| S-24 | ReviewHistory | `/me/review-history` | Học viên | Lịch sử ôn tập | Lọc Khóa học, Kết quả; phân trang; xem chi tiết | Khóa học, Kết quả | Rỗng khi không khớp | S-25 |
| S-25 | ReviewDetail, ReviewDetail-Explanation | `/me/review-history/103` | Học viên | Chi tiết lần làm | Lọc câu sai; Xem giải thích; Hiện tất cả | — | Giải thích ẩn mặc định | S-24 |
| S-26 | Contact | `/contact` | Học viên | Gửi phản hồi | Chọn đối tượng; khóa học 2 nhóm; loại; nội dung 1000 ký tự | Một khóa học, Hệ thống EduMentor AI, Chọn khóa học, Loại phản hồi, Nội dung 0/1000 | Rỗng: "Nhập nội dung phản hồi."; thành công: "Đã gửi phản hồi" | S-27 |
| S-27 | ContactGuest | `/contact-guest` | Khách | Liên hệ khi chưa đăng nhập | Xem liên hệ; form bị khóa; Đăng nhập | Một khóa học, Hệ thống EduMentor AI, Chọn khóa học, Loại phản hồi, Nội dung 0/1000 | Banner yêu cầu đăng nhập | S-26, S-01 |
| S-28 | AdminCourses | `/admin/courses` | Admin | Quản trị khóa học | Tìm; thêm, sửa, xóa; liên kết kỹ năng sau khi lưu | Tìm khóa học | Rỗng khi không tìm thấy | S-29 |
| S-29 | AdminSkills, AdminSkills-Relations | `/admin/skills` | Admin | Kỹ năng và quan hệ | Tìm; thêm; xóa; bấm kỹ năng mở sơ đồ; tạo, đổi, xóa quan hệ | Tìm kỹ năng, Tên kỹ năng mới | Trùng tên, đang dùng: báo lỗi | S-28 |
| S-30 | AdminBasePaths | `/admin/base-paths` | Admin | Mẫu lộ trình | Tạo; sửa tên, mục tiêu; thêm kỹ năng, kết nối; ngừng dùng; lưu | Tên mẫu, Mục tiêu phù hợp, Thêm kỹ năng | "Có thay đổi chưa lưu" | S-29 |
| S-31 | AdminHistorical | `/admin/historical` | Admin | Dữ liệu lịch sử | Kéo thả file; đánh dấu tổng hợp; kết quả nhập; danh sách bản ghi | Đây là dữ liệu tổng hợp (synthetic) | "[Định dạng file nhóm chốt]" | — |
| S-32 | AdminFeedback, AdminFeedback-Detail | `/admin/feedback` | Admin | Quản trị phản hồi | Thẻ số liệu; tab; tìm; lọc loại, thời gian; sắp xếp; ngăn chi tiết; trả lời qua email | Tìm theo nội dung, người gửi, khóa học, Loại phản hồi, Từ ngày, Đến ngày | Rỗng khi không khớp | S-26 |
| S-33 | AdminUserPaths | `/admin/user-paths` | Admin | Lộ trình người dùng | Thẻ mục tiêu; tab Người dùng, Mục tiêu; tìm từ đồng nghĩa; lọc trạng thái; đồ thị chỉ xem | Tìm tên hoặc email | Chỉ xem | S-18 |
| S-34 | ChatBubble-Menu, ChatBubble-Advisor | (dùng chung) | Khách, Học viên | Bong bóng hỗ trợ | GitHub, Zalo (link tạm), Liên hệ, AI tư vấn khóa học | Ô hỏi AI | Không có ở Consultant, Tutor, làm bài, trang quản trị; khách và học viên có câu chào khác nhau | S-26 |

Bằng chứng: `docs/ui-design/png/<màn>.png`, `html/<màn>.html`. Chức năng chỉ dành cho demo, không đưa vào bản thật (D-FE-07): bảng chuyển màn, giả lập lỗi mạng, dòng tài khoản demo ở S-01, liên kết "Mở thử liên kết trong email" ở S-04.
