# Bộ giao diện EduMentor AI (`docs/ui-design/`)

**Nguồn giao diện chính thức** của dự án — `docs/decisions.md` D-FE-12 (2026-10-29). Trước đây bộ này có tên `EduMentor-UI-design (2)`.

Bộ ảnh giao diện chụp lại từ bản demo React của nhóm. Mã nguồn bản demo này **chưa có trong repo** (đường dẫn `docs/ui-animation/demo/edumentor-demo-react` không tồn tại), và CSS của nó khác một phần với bản build `EduMentor AI Demo.html` (D-FE-02). Bố cục 29 màn gốc được giữ nguyên.

**Cập nhật gần nhất:** 2026-11-01, chụp lại toàn bộ 41 màn từ bản demo mới nhất (artifact `https://claude.ai/artifact/7xPJPGauwsXLG9keRNKcxe`, phiên bản `1793285378-8eed`). Ngày trong dữ liệu mẫu của màn phản hồi tính theo ngày chụp.

Đây là **prototype tĩnh** (HTML + ảnh chụp), không phải mã React của `frontend/`. Màn nào có ở đây **không** có nghĩa là đã được triển khai, đã gọi API thật hay đã kiểm thử. Bộ này cập nhật những gì nhóm đã sửa, thêm 4 màn mới, và gắn endpoint vào từng ảnh.

## Thư mục

| Thư mục / file | Nội dung |
|---|---|
| `index.html` | Trang xem nhanh. Mỗi thẻ có ảnh, route, trạng thái (Giữ / Đã sửa / Mới), mô tả thay đổi và danh sách endpoint. Có nút lọc theo trạng thái. |
| `png/` | Ảnh màn hình, rộng 1440px. Màn dài chụp cả trang. Ảnh trạng thái (hộp thoại, bong bóng chat, tắt đèn) chụp đúng khung 1440×1000. |
| `png-endpoints/` | Cùng ảnh như `png/`, có in thêm bảng endpoint ở cuối ảnh: phương thức, đường dẫn, mục đích. |
| `html/` | Bản HTML tĩnh của từng màn, dùng chung `html/app.css` (CSS của demo, có animation khi mở trang). Không có JavaScript nên các nút không bấm được, trừ `Main.html`, `Main-LampOff.html` và `Register.html` có đoạn script nhỏ để bấm thử dây kéo đèn. Cần mạng để tải font. |
| `pages.json` | Danh sách ảnh, mỗi mục có `name`, `title`, `route`, `feature`, `status`, `change`, `endpoints[]`. |
| `SCREEN-INVENTORY.md` | Danh sách màn hình kiểm tra trực tiếp trên UI Demo: mã màn, vai trò, chức năng, trường dữ liệu, trạng thái. |

## Màu phương thức trong ảnh

`GET` xanh dương · `POST` xanh lá · `PATCH` cam · `DELETE` đỏ · `CHƯA CÓ` tím (API MISMATCH, `api-endpoints.md` chưa định nghĩa) · `—` không gọi API.

## Thay đổi so với bản 29 màn

Bản 29 màn cũ (`docs/EduMentor-UI-design/`) đã bị xóa khỏi repo ngày 2026-10-29; xem lại trong lịch sử Git.

**Đã sửa**

- **Main:** thêm bong bóng chat. Chỉ còn **1 dây kéo** điều khiển cả 3 đèn. Mở trang thì đèn **tắt sẵn**: form ẩn và bị khóa (ảnh `Main-LampOff`); kéo dây thì cả 3 đèn sáng và form hiện, kéo lần nữa thì tắt cả 3. File HTML của hai màn này có đoạn script nhỏ để bấm thử dây kéo.
- **Register:** thêm bong bóng chat. Đổi theo Đăng nhập: **1 dây kéo** điều khiển cả 3 đèn, mở trang thì đèn tắt sẵn, form ẩn và bị khóa. Ảnh `Register` chụp ở trạng thái đã bật đèn. Về mặt nghiệp vụ, ND-56 vẫn chờ nhóm xác nhận.
- **Profile:** thêm công tắc giao diện Tối / Sáng.
- **EditProfile:** bỏ nút "Tải ảnh lên" và ô đường dẫn ảnh. Bấm thẳng vào avatar (có icon camera) để đổi ảnh qua `POST /api/me/avatar`. "Lưu thay đổi" chỉ gửi `full_name`.
- **Courses:** header thêm mục "Liên hệ".
- **ReviewDetail:** giải thích ẩn mặc định. Mỗi câu có nút "Xem giải thích", và có nút "Hiện tất cả giải thích" (ảnh `ReviewDetail-Explanation`).
- **AdminCourses:** sidebar quản trị thêm "Phản hồi" và "Lộ trình người dùng".
- **AdminSkills:** danh mục kỹ năng chiếm toàn bộ chiều rộng. Bấm một kỹ năng để mở hộp thoại sơ đồ quan hệ (ảnh `AdminSkills-Relations`).

**Mới**

- **Contact, ContactGuest** (tính năng 10): gửi phản hồi về khóa học hoặc hệ thống, có thẻ liên hệ của khóa học. Bản chưa đăng nhập có form bị khóa.
- **AdminFeedback, AdminFeedback-Detail** (tính năng 13): số liệu, tab, tìm kiếm, lọc loại và thời gian, sắp xếp theo thời gian, ngăn chi tiết.
- **AdminUserPaths** (tính năng 14): thẻ mục tiêu phổ biến, xem theo Người dùng hoặc Mục tiêu lộ trình, lọc theo trạng thái, mục đích lộ trình, tiến độ và đồ thị chỉ xem.
- **ChatBubble-Menu, ChatBubble-Advisor:** bong bóng chat góc phải dưới, có GitHub, Zalo, Liên hệ và AI tư vấn khóa học.
- **Profile-Light, Courses-Light:** giao diện Sáng, tông kem ấm.

## API MISMATCH

- **M1:** lưu bài ôn tập làm dở.
- **M2:** gửi phản hồi, liên hệ khóa học, danh sách phản hồi cho admin.
- **M3:** admin xem người dùng và lộ trình của họ.
- **M4:** chat AI tư vấn khóa học.

Theo dõi tại `docs/decisions.md` ND-55 (phản hồi: thêm ND-35).
