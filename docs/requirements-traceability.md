# Ma trận truy vết yêu cầu (RTM)

> **Cảnh báo (2026-11-02):** ma trận này được dựng từ bản SRS v2.0 do AI hiệu đính (`archive/2026-11-reset/sources-not-selected/`), không phải bản gốc hiện ở `docs/`. Mã yêu cầu không đổi, nhưng các câu trích và Q-23 có thể lệch. Sẽ dựng lại ở phase sau.

**Cập nhật:** 2026-11-01. **Phương pháp:** tạo lại từ [BA](EdumentorAi_BA.md) §6, các bảng trong [SRS v2.0](EduMentor_AI_SRS_v2.0.docx), [`decisions.md`](decisions.md) và kiểm tra trực tiếp UI Demo ([`ui-design/SCREEN-INVENTORY.md`](ui-design/SCREEN-INVENTORY.md)); không lấy từ báo cáo audit cũ.

File này chỉ để đối chiếu, không chứa quy tắc. "Phù hợp" nghĩa là có căn cứ và có giao diện tương ứng, không có nghĩa là đã có API hay đã kiểm thử: backend chưa có code. Nội dung PENDING vẫn chờ quyết định.

## 1. Số liệu

| Nguồn | Số lượng |
|---|---|
| BA FR | 46 |
| BA NFR | 39 |
| BA UC (có đặc tả chi tiết) | 15 (6) |
| BA BR | 42 (§5.5: 8; §9: 34, trùng mã BR-01 … 08) |
| BA AC | 11 |
| Yêu cầu chức năng SRS | 76 |
| SRS NFR, AC, điểm chờ | 19, 15, 23 |
| Route UI Demo; màn trong `ui-design` | 33; 41 |

Phân loại yêu cầu SRS:

| Trạng thái | Số yêu cầu |
|---|---|
| Phù hợp | 36 |
| PENDING | 34 |
| SRS có, UI chưa có | 3 |
| Đã sửa theo APPROVED | 2 |
| Backend, không kiểm được từ UI | 1 |

## 2. BA → SRS → UI

| BA ID | BA Requirement | SRS ID | SRS Requirement | UI Screen ID | UI Evidence | Status | Finding |
|---|---|---|---|---|---|---|---|
| FR-01 | Đăng ký tài khoản | SRS-AUTH-01 | Đăng ký tài khoản bằng họ tên, email, mật khẩu, xác nhận mật khẩu. | S-02 | `png/Register.png` | PENDING | D-AUTH-05 đã sửa; ND-37, 46, 47 |
| FR-02 | Đăng nhập và đăng xuất | SRS-AUTH-02 | Đăng nhập bằng email và mật khẩu; nhận access token và refresh token; chuyển trang theo va | S-01 | `png/Main.png` | PENDING | ND-19, ND-78; UI luôn vào /me |
| FR-02 | Đăng nhập và đăng xuất | SRS-AUTH-03 | Đăng xuất: xác nhận trong hộp thoại; backend thu hồi refresh token tương ứng, client xóa t | S-11 | `png/Logout.png` | Đã sửa theo APPROVED | D-AUTH-03; ND-48 |
| FR-03 | Quản lý hồ sơ cá nhân | SRS-PROF-01 | Xem hồ sơ: họ tên, email, vai trò, ngày tham gia, ảnh đại diện; thẻ thống kê; khóa học của | S-07 | `png/Profile.png` | Phù hợp | T05; ND-13 |
| FR-03 | Quản lý hồ sơ cá nhân | SRS-PROF-02 | Sửa họ tên. | S-08 | `png/EditProfile.png` | Phù hợp | D06, T04 |
| FR-04 | Quản lý kỹ năng hiện có | SRS-PROF-04 | Quản lý kỹ năng của tôi: tìm trong danh mục, thêm với trạng thái Đã biết hoặc Đang học, đổ | S-10 | `png/Skills.png` | PENDING | T06; ND-57, ND-64 |
| FR-05 | Tiếp nhận mục tiêu học tập | SRS-PATH-01 | Trò chuyện với AI Consultant: nhập mục tiêu bằng ngôn ngữ tự nhiên, có câu gợi ý mẫu; gửi  | S-16 | `png/Consultant.png` | Phù hợp | UI mock |
| FR-06 | Phân tích mục tiêu và xác định kỹ năng | SRS-PATH-02 | AI trả lời và trả về bản nháp lộ trình dạng đồ thị kỹ năng (node, cạnh), hiện ở khung bên  | S-16 | `png/Consultant.png` | PENDING | ND-74; UI mock trả bản nháp cố định |
| FR-07 | Làm rõ yêu cầu chưa đầy đủ | SRS-PATH-04 | AI hỏi lại khi mục tiêu chưa rõ; báo giới hạn khi ngoài phạm vi. | S-16 | `png/Consultant.png` | SRS có, UI chưa có | ND-74 |
| FR-08 | Tạo lộ trình học tập cá nhân hóa | SRS-PATH-02 | AI trả lời và trả về bản nháp lộ trình dạng đồ thị kỹ năng (node, cạnh), hiện ở khung bên  | S-16 | `png/Consultant.png` | PENDING | ND-74; UI mock trả bản nháp cố định |
| FR-08 | Tạo lộ trình học tập cá nhân hóa | SRS-PATH-03 | Tiếp tục trò chuyện để chỉnh bản nháp, ví dụ thêm Machine Learning. | S-16 | `png/Consultant.png` | Phù hợp | UI mock |
| FR-09 | Lưu trữ lộ trình học tập | SRS-PATH-05 | Lưu lộ trình (chỉ khi bấm "Lưu lộ trình này") hoặc Bỏ đề xuất. | S-16 | `png/Consultant.png` | Phù hợp | — |
| FR-10 | Xem và quản lý lộ trình đã lưu | SRS-PATH-06 | Lộ trình của tôi: lọc Đang theo / Hoàn thành / Đã từ bỏ, tiến độ (số kỹ năng đã biết / tổn | S-17 | `png/MyPaths.png` | Phù hợp | — |
| FR-11 | Hỗ trợ khám phá lộ trình linh hoạt | SRS-PATH-07 | Chi tiết lộ trình: đồ thị, mục tiêu, bấm node bất kỳ để xem vai trò, người thêm và khóa họ | S-18 | `png/PathDetail.png` | Phù hợp | — |
| FR-11 | Hỗ trợ khám phá lộ trình linh hoạt | SRS-TUT-06 | AI lỗi hoặc quá thời gian → hiện lỗi trong luồng chat và nút Gửi lại, giữ nội dung đã gõ. | S-20 | `png/Tutor.png` | Phù hợp | — |
| FR-12 | Hiển thị thông tin kỹ năng | SRS-PATH-07 | Chi tiết lộ trình: đồ thị, mục tiêu, bấm node bất kỳ để xem vai trò, người thêm và khóa họ | S-18 | `png/PathDetail.png` | Phù hợp | — |
| FR-13 | Truy xuất khóa học theo kỹ năng | SRS-CAT-03 | Header học viên có mục: Khóa học, Lộ trình, Khóa học của tôi, Ôn tập, AI Tutor, Liên hệ; a | — | — | Phù hợp | Nút Đăng nhập thấy ở ContactGuest |
| FR-13 | Truy xuất khóa học theo kỹ năng | SRS-REC-01 | Khi chọn một node, hiện danh sách khóa học gợi ý cho kỹ năng đó, sắp xếp: Phù hợp nhất (mặ | S-18 | `png/PathDetail.png` | Phù hợp | Thuật toán không kiểm được từ UI |
| FR-13 | Truy xuất khóa học theo kỹ năng | SRS-UX-01 | Công tắc giao diện Tối / Sáng (tông kem ấm) ở trang Hồ sơ, ghi nhớ lựa chọn trên trình duy | S-07, S-12 | `png/Profile.png`, `png/Profile-Light.png` | Phù hợp | — |
| FR-14 | Xếp hạng khóa học được đề xuất | SRS-REC-01 | Khi chọn một node, hiện danh sách khóa học gợi ý cho kỹ năng đó, sắp xếp: Phù hợp nhất (mặ | S-18 | `png/PathDetail.png` | Phù hợp | Thuật toán không kiểm được từ UI |
| FR-15 | Hiển thị thông tin khóa học | SRS-CAT-01 | Danh sách khóa học từ nền tảng MOOC: tìm theo từ khóa, lọc theo kỹ năng và cấp độ, sắp xếp | S-12 | `png/Courses.png`, `png/Courses-Light.png` | PENDING | ND-70, ND-72; UI không có lọc kỹ năng |
| FR-15 | Hiển thị thông tin khóa học | SRS-CAT-02 | Chi tiết khóa học: tên, nền tảng, giảng viên, mô tả, cấp độ, điểm, số lượt đánh giá, kỹ nă | S-13 | `png/CourseDetail.png` | PENDING | ND-70 |
| FR-15 | Hiển thị thông tin khóa học | SRS-UX-02 | Trang đăng nhập/đăng ký: mở trang thì 3 đèn tắt, form ẩn và bị khóa; chỉ 1 dây kéo làm côn | S-01, S-02 | `png/Main.png`, `png/Main-LampOff.png` | PENDING | ND-56 |
| FR-15 | Hiển thị thông tin khóa học | SRS-UX-03 | Trạng thái tải (skeleton, "Đang tải…"), thông báo toast thành công / lỗi, hộp thoại xác nh | — | — | Phù hợp | — |
| FR-16 | Truy cập khóa học bên ngoài | SRS-TRK-02 | Tham gia học: hộp thoại xác nhận, ghi ongoing, mở URL khóa học ở tab mới. | S-14 | `png/JoinDialog.png` | Phù hợp | D05 |
| FR-16 | Truy cập khóa học bên ngoài | SRS-REC-02 | Mỗi khóa gợi ý có nút Lưu và Tham gia học, hiện trạng thái nếu đã theo dõi. | S-18 | `png/PathDetail.png` | Phù hợp | — |
| FR-16 | Truy cập khóa học bên ngoài | SRS-UX-02 | Trang đăng nhập/đăng ký: mở trang thì 3 đèn tắt, form ẩn và bị khóa; chỉ 1 dây kéo làm côn | S-01, S-02 | `png/Main.png`, `png/Main-LampOff.png` | PENDING | ND-56 |
| FR-17 | Lưu khóa học để xem lại | SRS-TRK-01 | Lưu / bỏ lưu khóa học để học sau. | S-12, S-13, S-15 | `png/Courses.png`, `png/CourseDetail.png` | PENDING | ND-80 |
| FR-17 | Lưu khóa học để xem lại | SRS-REC-02 | Mỗi khóa gợi ý có nút Lưu và Tham gia học, hiện trạng thái nếu đã theo dõi. | S-18 | `png/PathDetail.png` | Phù hợp | — |
| FR-18 | Cập nhật trạng thái học tập | SRS-TRK-02 | Tham gia học: hộp thoại xác nhận, ghi ongoing, mở URL khóa học ở tab mới. | S-14 | `png/JoinDialog.png` | Phù hợp | D05 |
| FR-18 | Cập nhật trạng thái học tập | SRS-TRK-03 | Khóa học của tôi: 4 tab theo trạng thái; thao tác theo trạng thái: Đang học (Mở khóa học,  | S-15 | `png/MyCourses.png` | Phù hợp | T08 |
| FR-18 | Cập nhật trạng thái học tập | SRS-TRK-04 | Ngừng theo dõi: hộp thoại xác nhận, chuyển abandoned. Học tiếp: chuyển lại ongoing. | S-15 | `png/MyCourses.png` | Phù hợp | — |
| FR-18 | Cập nhật trạng thái học tập | SRS-UX-04 | Bố cục đáp ứng màn hình máy tính và di động; không cuộn ngang. | — | — | PENDING | ND-68 |
| FR-19 | Xem lịch sử học tập | SRS-PROF-01 | Xem hồ sơ: họ tên, email, vai trò, ngày tham gia, ảnh đại diện; thẻ thống kê; khóa học của | S-07 | `png/Profile.png` | Phù hợp | T05; ND-13 |
| FR-19 | Xem lịch sử học tập | SRS-TRK-03 | Khóa học của tôi: 4 tab theo trạng thái; thao tác theo trạng thái: Đang học (Mở khóa học,  | S-15 | `png/MyCourses.png` | Phù hợp | T08 |
| FR-20 | Hỗ trợ hội thoại học tập | SRS-TUT-01 | Danh sách phiên gần đây, tạo phiên mới, chọn phiên, xóa phiên (có xác nhận). | S-20 | `png/Tutor.png` | Phù hợp | DELETE archived theo CSDL |
| FR-20 | Hỗ trợ hội thoại học tập | SRS-TUT-02 | Gửi câu hỏi, nhận trả lời; trả lời mới hiện dần; có khối mã nguồn. | S-20 | `png/Tutor.png` | PENDING | ND-54 |
| FR-21 | Duy trì ngữ cảnh hội thoại | SRS-TUT-03 | Duy trì ngữ cảnh trong phiên (cửa sổ trượt các tin gần nhất). | S-20 | `png/Tutor.png` | PENDING | ND-59 |
| FR-22 | Giải thích kiến thức và hỗ trợ lập trình | SRS-TUT-02 | Gửi câu hỏi, nhận trả lời; trả lời mới hiện dần; có khối mã nguồn. | S-20 | `png/Tutor.png` | PENDING | ND-54 |
| FR-22 | Giải thích kiến thức và hỗ trợ lập trình | SRS-TUT-04 | Giải thích mã và gỡ lỗi: chỉ nguyên nhân, đề xuất cách sửa kèm giải thích. | S-20 | `png/Tutor.png` | Phù hợp | UI mock |
| FR-23 | Tạo bài tập củng cố | SRS-TUT-05 | Bài tập củng cố trắc nghiệm theo chủ đề vừa trao đổi, có nút Kiểm tra đáp án. | S-20 | `png/Tutor.png` | PENDING | ND-54; UI 1 câu, BA 3 câu |
| FR-24 | Tạo bài đánh giá kỹ năng | SRS-REV-01 | Trang bắt đầu ôn tập: tên khóa, kỹ năng khóa dạy, 3 thông số (20 câu chia đều theo kỹ năng | S-21 | `png/ReviewStart.png` | PENDING | T16 BLOCKED |
| FR-24 | Tạo bài đánh giá kỹ năng | SRS-REV-02 | Bắt đầu bài: server chọn ngẫu nhiên 20 câu, chia đều giữa các kỹ năng, tạo lần làm bài. | S-22 | `png/ReviewQuiz.png` | Phù hợp | D03, D04, T14, T15; ND-20 |
| FR-25 | Hỗ trợ các dạng câu hỏi đánh giá | SRS-REV-03 | Làm bài: từng câu 4 lựa chọn, câu trước / câu tiếp, bảng điều hướng 20 câu (đã trả lời, ch | S-22 | `png/ReviewQuiz.png` | Phù hợp | — |
| FR-26 | Đánh giá câu trả lời | SRS-REV-05 | Nộp bài: hộp thoại xác nhận; chấm theo đáp án lưu sẵn. Câu bỏ trống tính sai: T16 BLOCKED. | S-22 | `png/ReviewQuiz.png` | PENDING | D02, T13; T16 BLOCKED |
| FR-27 | Cung cấp kết quả và phản hồi | SRS-REV-06 | Kết quả: điểm %, số câu đúng / 20, Đạt / Chưa đạt; nếu đạt báo khóa đã chuyển Hoàn thành;  | S-23 | `png/ReviewResult.png` | PENDING | T29; ND-25 |
| FR-27 | Cung cấp kết quả và phản hồi | SRS-REV-08 | Chi tiết lần làm: từng câu, đáp án đã chọn, đáp án đúng; giải thích ẩn mặc định, có nút Xe | S-25 | `png/ReviewDetail.png`, `png/ReviewDetail-Explanation.png` | Phù hợp | — |
| FR-28 | Lưu lịch sử đánh giá | SRS-REV-07 | Lịch sử ôn tập: lọc theo khóa học và Đạt / Chưa đạt, phân trang, Xem chi tiết, Làm lại. | S-24 | `png/ReviewHistory.png` | Phù hợp | T15, T17 |
| FR-29 | Tổng hợp kết quả đánh giá | SRS-REV-08 | Chi tiết lần làm: từng câu, đáp án đã chọn, đáp án đúng; giải thích ẩn mặc định, có nút Xe | S-25 | `png/ReviewDetail.png`, `png/ReviewDetail-Explanation.png` | Phù hợp | — |
| FR-29 | Tổng hợp kết quả đánh giá | SRS-REV-09 | Điểm trung bình các lần làm hợp lệ. | — | — | SRS có, UI chưa có | ND-73 |
| FR-30 | Quản lý danh mục kỹ năng | SRS-ADMS-01 | Danh mục kỹ năng chiếm toàn bộ chiều rộng, tìm kiếm, thêm kỹ năng, xóa kỹ năng. | S-29 | `png/AdminSkills.png` | PENDING | ND-71 |
| FR-30 | Quản lý danh mục kỹ năng | SRS-ADMS-02 | Sửa tên kỹ năng. | — | — | SRS có, UI chưa có | BA FR-30; API có |
| FR-31 | Quản lý mối quan hệ giữa các kỹ năng | SRS-ADMS-03 | Bấm một kỹ năng để mở hộp thoại sơ đồ quan hệ: học trước, mở ra; tạo, đổi loại, xóa quan h | S-29 | `png/AdminSkills-Relations.png` | Phù hợp | — |
| FR-32 | Quản lý danh mục khóa học | SRS-ADMC-01 | Danh sách khóa học (tìm kiếm): tên, cấp độ, đánh giá, kỹ năng liên kết. | S-28 | `png/AdminCourses.png` | Phù hợp | — |
| FR-32 | Quản lý danh mục khóa học | SRS-ADMC-02 | Thêm / sửa khóa học: tên, đường dẫn, nền tảng, cấp độ (Cơ bản, Trung cấp, Nâng cao), mô tả | S-28 | `png/AdminCourses.png` | Phù hợp | — |
| FR-32 | Quản lý danh mục khóa học | SRS-ADMC-03 | Xóa khóa học có xác nhận. | S-28 | `png/AdminCourses.png` | Phù hợp | — |
| FR-33 | Quản lý liên kết giữa khóa học và kỹ năng | SRS-ADMC-04 | Liên kết / bỏ liên kết kỹ năng cho khóa học. | S-28 | `png/AdminCourses.png` | Phù hợp | — |
| FR-34 | Quản lý lộ trình học tập mẫu | SRS-ADMT-01 | Danh sách mẫu (Đang dùng / Đã tắt), tạo mẫu mới. | S-30 | `png/AdminBasePaths.png` | Phù hợp | — |
| FR-34 | Quản lý lộ trình học tập mẫu | SRS-ADMT-02 | Sửa mẫu: tên, mục tiêu phù hợp, thêm kỹ năng (đánh dấu Mục tiêu / Tùy chọn), thêm kết nối, | S-30 | `png/AdminBasePaths.png` | Phù hợp | — |
| FR-34 | Quản lý lộ trình học tập mẫu | SRS-ADMT-03 | Ngừng dùng mẫu (is_active = false). | S-30 | `png/AdminBasePaths.png` | Phù hợp | — |
| FR-35 | Kiểm tra dữ liệu lịch sử | SRS-ADMH-01 | Nhập file dữ liệu lịch sử (kéo thả hoặc chọn file), theo dõi trạng thái lần nhập (Đang xử  | S-31 | `png/AdminHistorical.png` | PENDING | ND-75 |
| FR-35 | Kiểm tra dữ liệu lịch sử | SRS-ADMH-02 | Danh sách bản ghi: mã, mục tiêu, số kỹ năng, nguồn; xem từng bản ghi. | S-31 | `png/AdminHistorical.png` | Phù hợp | Tùy chọn |
| FR-36 | Lưu trữ lộ trình được tạo | Chương 5 | Lưu lộ trình và cấu trúc | — | — | Backend, không kiểm được từ UI | — |
| FR-37 | Cung cấp dữ liệu cho hệ thống đề xuất | Chương 5 | Dữ liệu cho gợi ý | — | — | Backend, không kiểm được từ UI | — |
| FR-38 | Kiểm tra tính hợp lệ của kết quả AI | SRS-AUTH-04 | Làm mới phiên bằng refresh token khi access token hết hạn; xoay vòng refresh token. | — | — | Đã sửa theo APPROVED | D-AUTH-03; UI chưa có luồng; ND-40–43, 48 |
| FR-39 | Hỗ trợ cập nhật dữ liệu phục vụ đề xuất | §5.3 | Bổ sung dữ liệu lịch sử | — | — | BA có, SRS chưa đặc tả riêng | — |
| FR-40 | Phân quyền theo vai trò | SRS-AUTH-02 | Đăng nhập bằng email và mật khẩu; nhận access token và refresh token; chuyển trang theo va | S-01 | `png/Main.png` | PENDING | ND-19, ND-78; UI luôn vào /me |
| FR-41 | Bảo vệ dữ liệu cá nhân | §4.3; SRS-NFR-04 | Bảo vệ dữ liệu | — | — | Backend, không kiểm được từ UI | ND-79 |
| FR-42 | Kiểm tra dữ liệu đầu vào | Quy tắc từng yêu cầu | Kiểm tra đầu vào | — | — | Phù hợp | Form Đăng ký, Quên mật khẩu, Liên hệ đã thử |
| FR-43 | Thông báo lỗi nghiệp vụ | SRS-PATH-05 | Lưu lộ trình (chỉ khi bấm "Lưu lộ trình này") hoặc Bỏ đề xuất. | S-16 | `png/Consultant.png` | Phù hợp | — |
| FR-44 | Quản lý Access Token | SRS-AUTH-02 | Đăng nhập bằng email và mật khẩu; nhận access token và refresh token; chuyển trang theo va | S-01 | `png/Main.png` | PENDING | ND-19, ND-78; UI luôn vào /me |
| FR-45 | Quản lý Refresh Token | SRS-AUTH-04 | Làm mới phiên bằng refresh token khi access token hết hạn; xoay vòng refresh token. | — | — | Đã sửa theo APPROVED | D-AUTH-03; UI chưa có luồng; ND-40–43, 48 |
| FR-46 | Làm mới Token và kết thúc phiên đăng nhập | SRS-AUTH-03 | Đăng xuất: xác nhận trong hộp thoại; backend thu hồi refresh token tương ứng, client xóa t | S-11 | `png/Logout.png` | Đã sửa theo APPROVED | D-AUTH-03; ND-48 |
| FR-46 | Làm mới Token và kết thúc phiên đăng nhập | SRS-AUTH-04 | Làm mới phiên bằng refresh token khi access token hết hạn; xoay vòng refresh token. | — | — | Đã sửa theo APPROVED | D-AUTH-03; UI chưa có luồng; ND-40–43, 48 |

## 3. SRS → BA → UI → API

| SRS ID | Truy vết BA (theo SRS) | UI Screen ID | Endpoint (SRS Chương 7) | Status | Finding |
|---|---|---|---|---|---|
| SRS-AUTH-01 | FR-01, UC-01 | S-02 | `POST /api/auth/register` | PENDING | D-AUTH-05 đã sửa; ND-37, 46, 47 |
| SRS-AUTH-02 | FR-02, FR-44, FR-40 | S-01 | `POST /api/auth/login` | PENDING | ND-19, ND-78; UI luôn vào /me |
| SRS-AUTH-03 | FR-02, FR-46 | S-11 | `POST /api/auth/logout` | Đã sửa theo APPROVED | D-AUTH-03; ND-48 |
| SRS-AUTH-04 | FR-45, FR-46, NFR-38 | — | `POST /api/auth/refresh` | Đã sửa theo APPROVED | D-AUTH-03; UI chưa có luồng; ND-40–43, 48 |
| SRS-AUTH-05 | D09, T01 | S-03, S-04 | `POST /api/auth/forgot-password` | Phù hợp | D09, T01; ND-39 |
| SRS-AUTH-06 | D09, T02 | S-05, S-06 | `POST /api/auth/reset-password` | Phù hợp | D09, T02 |
| SRS-AUTH-07 | T03 | S-09 | `POST /api/me/change-password` | PENDING | T03; ND-47, ND-51 |
| SRS-PROF-01 | FR-03, FR-19, UC-02 | S-07 | `GET /api/me`; `GET /api/me/summary` | Phù hợp | T05; ND-13 |
| SRS-PROF-02 | FR-03 | S-08 | `PATCH /api/me` | Phù hợp | D06, T04 |
| SRS-PROF-03 | Bổ sung theo UI; API T04 | S-08 | `POST /api/me/avatar` | PENDING | D07; ND-12, ND-62 |
| SRS-PROF-04 | FR-04 | S-10 | `GET /api/me/skills`; `PATCH /api/me/skills` | PENDING | T06; ND-57, ND-64 |
| SRS-PROF-05 | BA §10.2; API D05 | S-10 | — | Phù hợp | D05, T13 |
| SRS-CAT-01 | FR-15, UC-06 | S-12 | `GET /api/courses` | PENDING | ND-70, ND-72; UI không có lọc kỹ năng |
| SRS-CAT-02 | FR-15, BR-16 | S-13 | `GET /api/courses/{course_id}`; `GET /api/courses/{course_id}/skills` | PENDING | ND-70 |
| SRS-CAT-03 | NFR-13 | — | — | Phù hợp | Nút Đăng nhập thấy ở ContactGuest |
| SRS-TRK-01 | FR-17 | S-12, S-13, S-15 | `POST /api/me/bookmarks`; `GET /api/me/bookmarks`; `DELETE /api/me/bookmarks/{course_id}` | PENDING | ND-80 |
| SRS-TRK-02 | FR-16, FR-18 | S-14 | `POST /api/courses/{course_id}/join` | Phù hợp | D05 |
| SRS-TRK-03 | FR-18, FR-19 | S-15 | `GET /api/me/courses`; `GET /api/me/courses/{course_id}/status` | Phù hợp | T08 |
| SRS-TRK-04 | FR-18 | S-15 | `PATCH /api/me/courses/{course_id}/status`; `DELETE /api/me/courses/{course_id}` | Phù hợp | — |
| SRS-TRK-05 | BA §10.4 quy tắc 5 | S-13, S-23 | — | Phù hợp | D02, T13; lời văn FR-18: ND-76 |
| SRS-PATH-01 | FR-05, UC-03 | S-16 | `POST /api/chat/learning-path` | Phù hợp | UI mock |
| SRS-PATH-02 | FR-06, FR-08, BR-02, BR-03 | S-16 | `POST /api/chat/learning-path` | PENDING | ND-74; UI mock trả bản nháp cố định |
| SRS-PATH-03 | FR-08 | S-16 | `POST /api/chat/learning-path` | Phù hợp | UI mock |
| SRS-PATH-04 | FR-07, BR-04, UC-03 | S-16 | `POST /api/chat/learning-path` | SRS có, UI chưa có | ND-74 |
| SRS-PATH-05 | FR-09, UC-04, FR-43 | S-16 | `POST /api/learning-paths` | Phù hợp | — |
| SRS-PATH-06 | FR-10, UC-05 | S-17 | `GET /api/me/learning-paths` | Phù hợp | — |
| SRS-PATH-07 | FR-11, FR-12, BR-10 | S-18 | `GET /api/learning-paths/{path_id}` | Phù hợp | — |
| SRS-PATH-08 | BA §10.6, §10.7 | S-19 | `PATCH /api/learning-paths/{path_id}`; `DELETE /api/learning-paths/{path_id}`; `GET/POST /api/learning-paths/{path_id}/nodes`; `GET/PATCH/DELETE /api/learning-paths/{path_id}/nodes/{skill_id}`; `GET/POST /api/learning-paths/{path_id}/edges`; `PATCH/DELETE /api/learning-paths/{path_id}/edges/{from_skill_id}/{to_skill_id}` | PENDING | ND-54 (tên lộ trình) |
| SRS-REC-01 | FR-13, FR-14, UC-06 | S-18 | `GET /api/learning-paths/{path_id}/nodes/{skill_id}/courses` | Phù hợp | Thuật toán không kiểm được từ UI |
| SRS-REC-02 | FR-16, FR-17 | S-18 | — | Phù hợp | — |
| SRS-REC-03 | BR-16, AC-04 | S-18 | — | Phù hợp | — |
| SRS-TUT-01 | FR-20; BA §10.9 | S-20 | `POST /api/chat/sessions`; `GET /api/chat/sessions`; `GET /api/chat/sessions/{session_id}`; `DELETE /api/chat/sessions/{session_id}` | Phù hợp | DELETE archived theo CSDL |
| SRS-TUT-02 | FR-20, FR-22 | S-20 | `GET /api/chat/sessions/{session_id}/messages`; `POST /api/chat/sessions/{session_id}/messages` | PENDING | ND-54 |
| SRS-TUT-03 | FR-21, AC-06 | S-20 | `POST /api/chat/sessions/{session_id}/messages` | PENDING | ND-59 |
| SRS-TUT-04 | FR-22, BR-23, BR-24 | S-20 | `POST /api/chat/sessions/{session_id}/messages` | Phù hợp | UI mock |
| SRS-TUT-05 | FR-23 | S-20 | `POST /api/chat/sessions/{session_id}/messages` | PENDING | ND-54; UI 1 câu, BA 3 câu |
| SRS-TUT-06 | UC-08, NFR-11 | S-20 | `POST /api/chat/sessions/{session_id}/messages` | Phù hợp | — |
| SRS-TUT-07 | BR-25 | — | — | Backend, không kiểm được từ UI | BA BR-25 |
| SRS-REV-01 | FR-24, BR-26 | S-21 | `GET /api/courses/{course_id}/review` | PENDING | T16 BLOCKED |
| SRS-REV-02 | FR-24, API T14, T15 | S-22 | `POST /api/courses/{course_id}/review-attempts` | Phù hợp | D03, D04, T14, T15; ND-20 |
| SRS-REV-03 | FR-25 | S-22 | `GET /api/review-attempts/{attempt_id}` | Phù hợp | — |
| SRS-REV-04 | UC-09 luồng thay thế | S-22, S-21 | — | PENDING | ND-55 (M1) |
| SRS-REV-05 | FR-26, BR-28, API D02, T13 | S-22 | `POST /api/review-attempts/{attempt_id}/submit` | PENDING | D02, T13; T16 BLOCKED |
| SRS-REV-06 | FR-27, API T29 | S-23 | — | PENDING | T29; ND-25 |
| SRS-REV-07 | FR-28 | S-24 | `GET /api/me/review-history` | Phù hợp | T15, T17 |
| SRS-REV-08 | FR-27, NFR-29 | S-25 | `GET /api/me/review-history/{attempt_id}` | Phù hợp | — |
| SRS-REV-09 | FR-29, BR-31 | — | — | SRS có, UI chưa có | ND-73 |
| SRS-FB-01 | BA §4.1.2; DB Feedback | S-26 | — | PENDING | ND-35, 55, 69; D11 |
| SRS-FB-02 | DB §7.2 | S-26, S-27 | — | PENDING | ND-35, 55 |
| SRS-FB-03 | — | S-27 | — | PENDING | ND-35, ND-50 |
| SRS-FB-04 | — | S-26 | — | PENDING | ND-55 (M2) |
| SRS-ADMC-01 | FR-32, UC-13 | S-28 | `GET/POST /api/admin/courses` | Phù hợp | — |
| SRS-ADMC-02 | FR-32 | S-28 | `GET/POST /api/admin/courses`; `GET/PATCH/DELETE /api/admin/courses/{course_id}` | Phù hợp | — |
| SRS-ADMC-03 | FR-32, BR-33 | S-28 | `GET/PATCH/DELETE /api/admin/courses/{course_id}` | Phù hợp | — |
| SRS-ADMC-04 | FR-33 | S-28 | `GET/POST /api/admin/course-skill-relations`; `DELETE /api/admin/course-skill-relations/{course_id}/{skill_id}` | Phù hợp | — |
| SRS-ADMS-01 | FR-30, UC-11 | S-29 | `GET/POST /api/admin/skills`; `PATCH/DELETE /api/admin/skills/{skill_id}` | PENDING | ND-71 |
| SRS-ADMS-02 | FR-30 | — | `PATCH/DELETE /api/admin/skills/{skill_id}` | SRS có, UI chưa có | BA FR-30; API có |
| SRS-ADMS-03 | FR-31, BR-08, UC-12 | S-29 | `GET/POST /api/admin/skill-relations`; `PATCH/DELETE /api/admin/skill-relations/{from_skill_id}/{to_skill_id}` | Phù hợp | — |
| SRS-ADMT-01 | FR-34, UC-14 | S-30 | `GET/POST /api/admin/base-learning-paths` | Phù hợp | — |
| SRS-ADMT-02 | FR-34 | S-30 | `GET/PATCH/DELETE /api/admin/base-learning-paths/{template_id}`; `GET/POST/PATCH/DELETE /api/admin/base-learning-paths/{template_id}/nodes[/{skill_id}]`; `GET/POST/PATCH/DELETE /api/admin/base-learning-paths/{template_id}/edges[/{from}/{to}]` | Phù hợp | — |
| SRS-ADMT-03 | FR-34 | S-30 | `GET/PATCH/DELETE /api/admin/base-learning-paths/{template_id}` | Phù hợp | — |
| SRS-ADMH-01 | FR-35, UC-15 | S-31 | `POST /api/admin/historical-learning-path-imports`; `GET /api/admin/historical-learning-path-imports/{import_id}` | PENDING | ND-75 |
| SRS-ADMH-02 | FR-35 | S-31 | `GET /api/admin/historical-learning-paths[/{record_id}]` | Phù hợp | Tùy chọn |
| SRS-ADMF-01 | BA §4.1.2 | S-32 | — | PENDING | ND-35, 55 |
| SRS-ADMF-02 | — | S-32 | — | PENDING | ND-55, ND-69 |
| SRS-ADMF-03 | BA §4.1.2 (Q-07) | S-32 | — | PENDING | ND-35 |
| SRS-ADMU-01 | Q-09 | S-33 | — | PENDING | ND-55, ND-79 |
| SRS-ADMU-02 | Q-09 | S-33 | — | PENDING | ND-55, ND-79 |
| SRS-ADMU-03 | Q-09 | S-33 | — | PENDING | ND-55, ND-79 |
| SRS-ADMU-04 | Q-09 | S-33 | — | PENDING | ND-55, ND-79 |
| SRS-SUP-01 | Q-10 | S-34 | — | PENDING | UI2-04; link tạm |
| SRS-SUP-02 | Q-10 | S-34 | — | PENDING | ND-55 (M4) |
| SRS-UX-01 | NFR-13 | S-07, S-12 | — | Phù hợp | — |
| SRS-UX-02 | NFR-15, NFR-16 (Q-19) | S-01, S-02 | — | PENDING | ND-56 |
| SRS-UX-03 | NFR-15 | — | — | Phù hợp | — |
| SRS-UX-04 | NFR-18 | — | — | PENDING | ND-68 |

## 4. UI → SRS

| Screen ID | Màn | Yêu cầu SRS |
|---|---|---|
| S-01 | Main | SRS-AUTH-02, SRS-UX-02 |
| S-01 | Main-LampOff | SRS-UX-02 |
| S-02 | Register | SRS-AUTH-01, SRS-UX-02 |
| S-03 | ForgotPassword | SRS-AUTH-05 |
| S-04 | ForgotSent | SRS-AUTH-05 |
| S-05 | ResetPassword | SRS-AUTH-06 |
| S-06 | ResetExpired | SRS-AUTH-06 |
| S-07 | Profile | SRS-PROF-01, SRS-UX-01 |
| S-07 | Profile-Light | SRS-UX-01 |
| S-08 | EditProfile | SRS-PROF-02, SRS-PROF-03 |
| S-09 | ChangePassword | SRS-AUTH-07 |
| S-10 | Skills | SRS-PROF-04, SRS-PROF-05 |
| S-11 | Logout | SRS-AUTH-03 |
| S-12 | Courses | SRS-CAT-01, SRS-TRK-01 |
| S-12 | Courses-Light | SRS-CAT-01, SRS-UX-01 |
| S-34 | ChatBubble-Menu | SRS-SUP-01 |
| S-34 | ChatBubble-Advisor | SRS-SUP-02 |
| S-13 | CourseDetail | SRS-CAT-02, SRS-TRK-01, SRS-TRK-05 |
| S-14 | JoinDialog | SRS-TRK-02 |
| S-15 | MyCourses | SRS-TRK-01, SRS-TRK-03, SRS-TRK-04 |
| S-16 | Consultant | SRS-PATH-01, SRS-PATH-02, SRS-PATH-03, SRS-PATH-04, SRS-PATH-05 |
| S-17 | MyPaths | SRS-PATH-06 |
| S-18 | PathDetail | SRS-PATH-07, SRS-REC-01, SRS-REC-02, SRS-REC-03 |
| S-19 | PathEdit | SRS-PATH-08 |
| S-20 | Tutor | SRS-TUT-01, SRS-TUT-02, SRS-TUT-03, SRS-TUT-04, SRS-TUT-05, SRS-TUT-06 |
| S-21 | ReviewStart | SRS-REV-01, SRS-REV-04 |
| S-22 | ReviewQuiz | SRS-REV-02, SRS-REV-03, SRS-REV-04, SRS-REV-05 |
| S-23 | ReviewResult | SRS-TRK-05, SRS-REV-06 |
| S-24 | ReviewHistory | SRS-REV-07 |
| S-25 | ReviewDetail | SRS-REV-08 |
| S-25 | ReviewDetail-Explanation | SRS-REV-08 |
| S-26 | Contact | SRS-FB-01, SRS-FB-02, SRS-FB-04 |
| S-27 | ContactGuest | SRS-FB-02, SRS-FB-03 |
| S-28 | AdminCourses | SRS-ADMC-01, SRS-ADMC-02, SRS-ADMC-03, SRS-ADMC-04 |
| S-29 | AdminSkills | SRS-ADMS-01 |
| S-29 | AdminSkills-Relations | SRS-ADMS-03 |
| S-30 | AdminBasePaths | SRS-ADMT-01, SRS-ADMT-02, SRS-ADMT-03 |
| S-31 | AdminHistorical | SRS-ADMH-01, SRS-ADMH-02 |
| S-32 | AdminFeedback | SRS-ADMF-01, SRS-ADMF-02 |
| S-32 | AdminFeedback-Detail | SRS-ADMF-03 |
| S-33 | AdminUserPaths | SRS-ADMU-01, SRS-ADMU-02, SRS-ADMU-03, SRS-ADMU-04 |

**Có trên UI nhưng không phải yêu cầu:** dòng tài khoản demo, bảng chuyển màn, giả lập lỗi mạng, liên kết thử email (đều loại khỏi bản thật theo D-FE-07).

**Có quyết định nhưng chưa có màn hay yêu cầu SRS:** quản trị câu hỏi `/api/admin/questions*` (T19–T21; ND-53, Q-23 chỉ có ở bản hiệu đính).

## 5. BA NFR → SRS

| Nhóm | Mã |
|---|---|
| Có mã SRS-NFR hoặc yêu cầu UX | NFR-01, 02, 04–14, 15 (SRS-UX-03), 16–18, 23, 25–27, 31, 34, 37, 38 |
| Áp dụng nguyên văn từ BA, chưa có mã SRS riêng | NFR-03, 19–22, 24, 28–30, 32, 33, 35, 36, 39 |

## 6. Điểm chờ của SRS → tài liệu dự án

| SRS Chương 13 | Nội dung | Trạng thái trong dự án |
|---|---|---|
| Q-01 | Ôn tập theo kỹ năng (BA UC-09, FR-24, §10.10) hay theo khóa học | D01 đã chốt; lời văn BA: ND-58 |
| Q-02 | Đầu ra lộ trình: "3–5 môn học kèm giải thích" (SRS 1.0) hay đồ thị kỹ năng | ND-60, ND-77 |
| Q-03 | Học viên có tự đánh dấu Hoàn thành không (BA FR-18) | D02, T13 đã chốt; lời văn BA: ND-76 |
| Q-04 | Thu hồi refresh token khi đăng xuất (BA FR-46, NFR-38, AC-01) | Đã giải quyết: D-AUTH-03; còn ND-40–43, 48 |
| Q-05 | Khách có xem danh mục khóa học không | ND-70 |
| Q-06 | Trạng thái AI hỏi lại / ngoài phạm vi | ND-74 |
| Q-07 | Phản hồi: danh sách loại phản hồi (D11 "không làm") và phạm vi Admin | ND-35, 55, 69 |
| Q-08 | Số tin nhắn nạp lại làm ngữ cảnh AI Tutor (SRS 1.0: 6) | ND-59 |
| Q-09 | Admin xem lộ trình người dùng (BA giới hạn dữ liệu cá nhân) | ND-55, ND-79 |
| Q-10 | Bong bóng hỗ trợ và AI tư vấn khóa học | ND-55, UI2-04 |
| Q-11 | Lưu bài làm dở phía server | ND-55 |
| Q-12 | Hai cách lấy danh sách đã lưu (bookmarks và ?status=bookmarked) | ND-80 |
| Q-13 | Câu hỏi tự luận / lập trình (BA FR-25, 26) | ND-73 |
| Q-14 | Điểm trung bình ôn tập (BA FR-29) | ND-73 |
| Q-15 | Định dạng file nhập dữ liệu lịch sử | ND-75 |
| Q-16 | Cập nhật lộ trình sau khi đạt ôn tập (T13 bước 5) | ND-24 |
| Q-17 | Enum relation_type cạnh lộ trình (đã có trong thiết kế CSDL) | Đã có: `database-design.md` §4.6 |
| Q-18 | Xóa phiên chat (đã có trong thiết kế CSDL) | Đã có: `database-design.md` §5 |
| Q-19 | Hiệu ứng đèn che form đăng nhập | ND-56 |
| Q-20 | Trường mục tiêu nghề nghiệp trong hồ sơ (BA FR-03) | ND-10 |
| Q-21 | Chấm sao câu trả lời AI (SRS 1.0 FR-08) | ND-59, ND-77 |
| Q-22 | Thời lượng, danh mục, tiên quyết giữa khóa học (SRS 1.0 FR-02); lọc Budget/Tags (SRS 1.0 §2) | ND-61, ND-77 |
| Q-23 (chỉ có ở bản hiệu đính) | Quản trị câu hỏi /api/admin/questions* (T19–T21 đã đồng ý) | ND-53 |
