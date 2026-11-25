# Danh sách thay đổi BA / SRS cho bản Word — 19/11/2026

Người giữ bản Word (`docs/Features/EdumentorAi_BA_v3.docx`, `AI_Learning_Assistant_Recommender_SRS_v3`) chép các thay đổi dưới đây sang. Bản .md ở thư mục gốc repo đã sửa sẵn, có thể mở để chép nguyên văn.

Phạm vi: chỉ phần của Tuấn (module 01 tài khoản / hồ sơ, module 09 ôn tập). Lý do thay đổi:

1. **Sửa hồ sơ** (19/11): form một cột — họ tên, ngày sinh, giới tính, số điện thoại; bỏ CCCD và quê quán khỏi giao diện.
2. **Giới hạn đăng nhập sai** (19/11): chống dò mật khẩu, mã 429.
3. **Trang Kết Quả - AI Chấm** (17/11): Admin xem lại câu tự luận AI chấm bị gắn cờ.
4. **Kết quả đo AI chấm bài** (B10, 18/11).

> **Lưu ý:** bản Word cũng **chưa có** đợt sửa phần ôn tập ngày 16/11 (15 câu, tự luận AI chấm theo barem, đạt 6/10). Nếu bản Word vẫn ghi "20 câu trắc nghiệm, đạt 60%" thì chép luôn các mục UC-09, FR-24 – FR-29, FR-54, BR-28, BR-29, 8.6, 8.7, 10.10 từ bản .md (commit `71af104`).

## EdumentorAi_BA_v3

| # | Vị trí | Loại | Câu cũ | Câu mới / phần thêm |
|---|---|---|---|---|
| 1 | 4.1.2 Quản trị viên — danh sách quyền | thêm | — | - Xem lại câu tự luận do AI chấm bị gắn cờ (trang Kết Quả - AI Chấm) và chấm lại từng ý khi cần. |
| 2 | 5.2 bảng Use Case — UC-02 | sửa | Xem hồ sơ và thống kê học tập, sửa họ tên, đổi ảnh đại diện, | Xem hồ sơ và thống kê học tập, sửa thông tin cá nhân (họ tên, ngày sinh, giới tính, số điện thoại), đổi ảnh đại diện, |
| 3 | 5.2 bảng Use Case — thêm UC-22 sau UC-21 | thêm | — | \| UC-22 \| Review AI-Graded Essays \| Admin \| Xem câu tự luận AI chấm bị gắn cờ cần xem lại, chấm lại từng ý (Đạt / Không đạt); điểm và kết quả bài được tính lại. \| |
| 4 | UC-09 — Alternative Flow | thêm | — | - Câu tự luận bị gắn cờ cần xem lại: điểm tạm tính; Admin chấm lại trên trang Kết Quả - AI Chấm (UC-22), nếu điểm đổi thì người dùng nhận lại thông báo kết quả. |
| 5 | 5.4 Quy trình quản trị — thêm hoạt động 5 | thêm | — | 5. **Xem lại kết quả AI chấm:** Kiểm tra các câu tự luận bị gắn cờ và chấm lại khi AI chấm chưa đúng. |
| 6 | FR-02 — Đăng nhập và đăng xuất | sửa | Hệ thống phải cho phép người dùng đăng nhập bằng thông tin xác thực hợp lệ và đăng xuất khỏi phiên làm việc hiện tại. | Hệ thống phải cho phép người dùng đăng nhập bằng thông tin xác thực hợp lệ và đăng xuất khỏi phiên làm việc hiện tại. Đăng nhập sai 5 lần trong 15 phút với cùng một email thì email đó bị khóa tạm 15 phút (đăng nhập đúng thì bộ đếm về 0); hệ thống đếm như nhau cho email có và không có tài khoản để không lộ email nào đã đăng ký. |
| 7 | FR-03 — Quản lý hồ sơ cá nhân | sửa | Người dùng được sửa họ tên và đổi ảnh đại diện bằng cách bấm vào ảnh để tải file lên. Email chỉ đọc, không được đổi. | Người dùng được sửa thông tin cá nhân trên một form một cột: họ và tên (bắt buộc), ngày sinh, giới tính (Nam / Nữ), số điện thoại (10 chữ số, bắt đầu bằng 0); các trường ngoài họ tên không bắt buộc. Người dùng đổi ảnh đại diện bằng cách bấm vào ảnh để tải file lên. Email chỉ đọc, không được đổi. |
| 8 | FR-26 — Chấm điểm (cuối gạch Tự luận) | sửa | câu được đánh dấu "đang xem lại" và điểm tạm tính. | câu được đánh dấu "đang xem lại", điểm tạm tính cho tới khi Admin xem lại (FR-57). |
| 9 | FR-27 — Cung cấp kết quả và phản hồi | sửa | Hệ thống gửi email kết quả cho người dùng. **FR-28 | Câu đã được giáo viên chấm lại hiển thị nhãn "Giáo viên đã xem lại". Hệ thống gửi email kết quả cho người dùng. **FR-28 |
| 10 | 6.12 — thêm FR-57 sau FR-54 | thêm | — | **FR-57 — Xem lại kết quả AI chấm (Kết Quả - AI Chấm)** Admin xem danh sách câu tự luận do AI chấm cần xem lại, lọc theo trạng thái (chưa xem / đã xem), lý do và khóa học. Lý do gắn cờ: điểm AI lệch xa cách chấm từ khóa sau khi chấm lại; điểm cả bài sát ngưỡng đạt (±0,5); bài làm có câu ra lệnh cho AI; ý chấm Đạt nhưng thiếu câu trích; AI lỗi nên chấm theo từ khóa. Với mỗi câu, Admin thấy đề, barem, bài làm, kết quả và lý do AI từng ý, rồi chọn lại Đạt / Không đạt cho từng ý. Hệ thống tính lại điểm câu, điểm bài và kết quả Đạt / Chưa đạt trong một giao dịch, ghi lại người xem, thời điểm, kết quả trước và sau vào nhật ký chấm. Nếu kết quả bài đổi, hệ thống hỏi xác nhận trước khi lưu. Bài chuyển thành Đạt thì khóa học thành Hoàn thành và kỹ năng thành Đã biết; bài chuyển thành Chưa đạt thì **không kéo lùi** tiến độ đã ghi nhận. Khi điểm đổi, người học nhận lại thông báo kết quả (email nếu bài chuyển thành Đạt). |
| 11 | NFR-04 — Bảo mật xác thực | sửa | Mật khẩu không được lưu dưới dạng văn bản thuần (plaintext) mà phải được lưu dưới dạng băm an toàn. | Mật khẩu không được lưu dưới dạng văn bản thuần (plaintext) mà phải được lưu dưới dạng băm an toàn. Hệ thống giới hạn số lần thử để chống dò mật khẩu và gửi thư hàng loạt: đăng nhập sai 5 lần / 15 phút mỗi email, 30 lần thử đăng nhập / 15 phút mỗi địa chỉ IP, 5 lần đăng ký / giờ mỗi IP, quên mật khẩu 3 lần / 15 phút mỗi email và 10 lần / giờ mỗi IP, đặt lại mật khẩu 10 lần / 15 phút mỗi IP. Vượt giới hạn trả mã 429 kèm thời gian chờ (Retry-After). |
| 12 | 8.6 Course Review — quy trình, bước 5 | thêm | — | 6. Câu tự luận bị gắn cờ được đưa lên trang Kết Quả - AI Chấm để Admin xem lại và chấm lại nếu cần (FR-57). |
| 13 | 8.7 Đánh giá AI/ML — gạch Course Review | sửa | so sánh với baseline chấm từ khóa bằng paired bootstrap. | so sánh với baseline chấm từ khóa bằng paired bootstrap. Kết quả đo ngày 18/11/2026 trên phần test (30 bài, 108 ý): pipeline khớp người chấm 94,4% (chấm từ khóa 80,6%), QWK 0,95, không bài sai nào bị chấm Đạt; kappa với từng người chấm 0,81–0,85, cao hơn mức hai người chấm khớp nhau (0,77). Chưa đạt mục tiêu độ trễ và lệch ≤ 1 điểm; chi tiết và hạn chế trong `docs/ai-grading/BAO_CAO_AI_CHAM_BAI.md`. |
| 14 | 10.2 bảng API — PATCH /api/me | sửa | \| PATCH \| `/api/me` \| Cập nhật họ tên (email không đổi được). \| | \| PATCH \| `/api/me` \| Cập nhật họ tên, ngày sinh, giới tính, số điện thoại (email không đổi được). \| |
| 15 | 10.2 — ghi chú sau bảng API | thêm | — | Các API `register`, `login`, `forgot-password`, `reset-password` có giới hạn tần suất (NFR-04); vượt giới hạn trả `429 Too Many Requests` kèm header `Retry-After` (số giây phải chờ). |
| 16 | 10.10 — thêm bảng API quản trị xem lại (trước Quy trình nộp bài) | thêm | — | API quản trị xem lại bài AI chấm (Admin, FR-57): \| Method \| Endpoint \| Mô tả \| \|---\|---\|---\| \| GET \| `/api/admin/review/flags` \| Danh sách câu tự luận cần xem lại; lọc `status` (open / resolved / all), `reason`, `course_id`, có phân trang và số lượng theo từng lý do. \| \| POST \| `/api/admin/review/flags/{attempt_id}/{position}/resolve` \| Admin chọn lại Đạt / Không đạt cho từng ý (kèm ghi chú); trả điểm mới, kết quả bài có đổi không, khóa học có chuyển Hoàn thành không. \| |
| 17 | 11.2 AC-01 — thêm tiêu chí | thêm | — | - Đăng nhập sai 5 lần trong 15 phút thì email bị khóa tạm (mã 429); đăng nhập đúng xóa bộ đếm. |
| 18 | 11.5 AC-07 — thêm tiêu chí | thêm | — | - Admin chấm lại câu bị gắn cờ thì điểm và kết quả bài được tính lại đúng; đổi sang Chưa đạt không kéo lùi tiến độ. |
| 19 | 11.7 AC-10 — thêm tiêu chí | sửa | - Kết quả đánh giá phải được ghi nhận; không tuyên bố mô hình vượt trội nếu chưa có bằng chứng. | - AI chấm tự luận được so với người chấm trên bộ bài chuẩn (MAE, RMSE, QWK, khớp từng ý, kappa) và so với chấm từ khóa. - Kết quả đánh giá phải được ghi nhận; không tuyên bố mô hình vượt trội nếu chưa có bằng chứng. |
| 20 | 13.2 Ma trận truy vết — dòng Course Review | sửa | \| FR-24–FR-29, FR-54 \| Ôn tập theo khóa học, bài làm dở, lịch sử, ngân hàng câu hỏi \| | \| FR-24–FR-29, FR-54, FR-57 \| Ôn tập theo khóa học, bài làm dở, lịch sử, ngân hàng câu hỏi, xem lại kết quả AI chấm \| |

## AI_Learning_Assistant_Recommender_SRS_v3

| # | Vị trí | Loại | Câu cũ | Câu mới / phần thêm |
|---|---|---|---|---|
| 1 | 4. bảng FR — FR-01 | sửa | đăng xuất thu hồi refresh token. | đăng xuất thu hồi refresh token. Đăng nhập sai 5 lần / 15 phút thì email bị khóa tạm 15 phút; đăng ký, quên và đặt lại mật khẩu cũng giới hạn số lần (mã 429). |
| 2 | 4. bảng FR — FR-03 | sửa | lộ trình đang theo); sửa họ tên; đổi ảnh đại diện | lộ trình đang theo); sửa thông tin cá nhân (họ tên, ngày sinh, giới tính Nam / Nữ, số điện thoại); đổi ảnh đại diện |
| 3 | 4. bảng FR — FR-11 | sửa | làm lại không giới hạn; đạt thì khóa thành Hoàn thành và kỹ năng thành Đã biết; gửi email kết quả. \| Học viên \| | làm lại không giới hạn; đạt thì khóa thành Hoàn thành và kỹ năng thành Đã biết; gửi email kết quả; câu tự luận bị gắn cờ được Admin xem lại (FR-22). \| Học viên \| |
| 4 | 4. bảng FR — thêm FR-22 sau FR-21 | thêm | — | \| FR-22 \| Kết Quả - AI Chấm \| Danh sách câu tự luận AI chấm bị gắn cờ (lệch chấm từ khóa, sát ngưỡng đạt, có câu ra lệnh cho AI, thiếu câu trích, chấm dự phòng); lọc theo trạng thái, lý do, khóa học; chấm lại từng ý Đạt / Không đạt, hệ thống tính lại điểm và kết quả, hỏi xác nhận khi kết quả bài đổi, không kéo lùi tiến độ, gửi lại thông báo kết quả. \| Admin \| |
| 5 | 5. Tóm tắt API — nhóm Quản trị | sửa | `/admin/users/{id}/learning-paths`, `/admin/learning-path-goals` \| Admin \| | `/admin/users/{id}/learning-paths`, `/admin/learning-path-goals`, `/admin/review/flags` \| Admin \| |
| 6 | 6.3 Luồng Admin — thêm bước 7 | thêm | — | 7. Xem lại câu tự luận AI chấm bị gắn cờ và chấm lại khi cần (Kết Quả - AI Chấm). |
| 7 | 7. Thiết kế CSDL — thêm bảng UserProfile sau User | thêm | — | \| UserProfile \| Thông tin cá nhân không bắt buộc (một-một với User): ngày sinh, giới tính, số điện thoại \| |
| 8 | 5. Tóm tắt API — ghi chú sau bảng | thêm | — | Các API đăng ký, đăng nhập, quên và đặt lại mật khẩu có giới hạn tần suất; vượt giới hạn trả `429` kèm `Retry-After`. |

## Bổ sung 19/11 (tối) — ôn tập: tối đa 5 bài làm dở, Bỏ bài dở, chờ 2 phút giữa 2 lần nộp

Ôn tập vẫn **không giới hạn số lần**. Thêm BR-35 và API `DELETE /api/review-attempts/{id}`.

| # | Tài liệu | Vị trí | Loại | Câu cũ | Câu mới / phần thêm |
|---|---|---|---|---|---|
| 1 | BA | UC-09 — Alternative Flow (bài dở) | sửa | - Mỗi khóa học chỉ có tối đa một bài đang làm dở cho mỗi người dùng. | - Mỗi khóa học chỉ có tối đa một bài đang làm dở cho mỗi người dùng; tổng cộng tối đa 5 bài làm dở. Đủ 5 bài mà bắt đầu bài ở khóa khác: hệ thống báo "Bạn đang có 5 bài ôn tập làm dở. Hãy hoàn thành hoặc bỏ bớt một bài để bắt đầu bài mới." và liệt kê các bài dở với nút Tiếp tục / Bỏ bài (BR-35). - Người dùng chọn Bỏ bài: bài làm dở bị xóa, không có điểm, không vào lịch sử. - Nộp bài khi chưa đủ 2 phút kể từ lần nộp trước: hệ thống báo "Bạn vừa nộp bài, vui lòng chờ. Còn … để nộp lần sau."; bài vẫn giữ nguyên để nộp lại (BR-35). |
| 2 | BA | FR-24 — cuối đoạn | sửa | Người dùng được làm lại không giới hạn; mỗi khóa có tối đa một bài đang làm dở. | Người dùng được làm lại không giới hạn; mỗi khóa có tối đa một bài đang làm dở và tổng cộng tối đa 5 bài làm dở (BR-35). |
| 3 | BA | FR-29 — Lưu bài ôn tập làm dở | sửa | và mở lại đúng bài đó khi người dùng quay lại. Hồ sơ người dùng hiển thị các lần ôn tập gần đây. | và mở lại đúng bài đó khi người dùng quay lại. Hồ sơ người dùng hiển thị các lần ôn tập gần đây. Người dùng có thể Bỏ bài làm dở: bài bị xóa hẳn, không có điểm, không vào lịch sử, không gọi AI chấm. Khi đã có 5 bài làm dở, người dùng phải nộp hoặc bỏ bớt một bài mới bắt đầu được bài ở khóa khác; mở lại bài dở đã có vẫn được. |
| 4 | BA | 9.6 — thêm BR-35 sau BR-31 | thêm | — | **BR-35 — Ôn tập không giới hạn số lần, nhưng giới hạn bài làm dở và nộp dồn dập** Người dùng được ôn tập không giới hạn số lần. Để bảo vệ lượt AI chấm dùng chung: (1) hai lần nộp bài của một người phải cách nhau ít nhất 2 phút — chặn công cụ nộp tự động, người học thật làm 15 câu mất vài phút nên không bị ảnh hưởng; lần nộp lỗi không tính; (2) mỗi người có tối đa 5 bài làm dở cùng lúc (tính theo khóa học; khi ôn tập theo kỹ năng trên đồ thị thì tính theo kỹ năng). Hai ngưỡng là cấu hình hệ thống (`REVIEW_SUBMIT_COOLDOWN`, `REVIEW_MAX_UNFINISHED`). |
| 5 | BA | 10.10 bảng API — thêm DELETE | thêm | — | \| DELETE \| `/api/review-attempts/{attempt_id}` \| Bỏ bài làm dở: xóa hẳn, không điểm, không vào lịch sử. Bài đã nộp → 409. \| |
| 6 | BA | 10.10 Quy trình nộp bài — bước 1 | sửa | 1. Kiểm tra bài thuộc người dùng hiện tại và chưa nộp. | 1. Kiểm tra bài thuộc người dùng hiện tại và chưa nộp; lần nộp trước của người này đã cách ít nhất 2 phút (chưa đủ → `429` kèm `Retry-After`, bài giữ nguyên). |
| 7 | BA | 11.5 AC-07 — bài làm dở | sửa | - Bài làm dở được lưu và mở lại đúng; mỗi khóa có tối đa một bài dở. | - Bài làm dở được lưu và mở lại đúng; mỗi khóa có tối đa một bài dở, tổng cộng tối đa 5 bài dở; bỏ bài dở thì bài bị xóa, không vào lịch sử. - Hai lần nộp cách nhau dưới 2 phút thì lần sau bị chặn với thông báo thời gian chờ. |
| 8 | SRS | 4. bảng FR — FR-11 | sửa | tạm rời và làm tiếp; câu bỏ trống 0 điểm; | tạm rời và làm tiếp; tối đa 5 bài làm dở (đủ thì phải nộp hoặc Bỏ bài dở mới bắt đầu bài mới); hai lần nộp cách nhau ít nhất 2 phút; câu bỏ trống 0 điểm; |
| 9 | SRS | 5. Tóm tắt API — nhóm Ôn tập | sửa | `PATCH /review-attempts/{id}/answers`, `POST /review-attempts/{id}/submit` | `PATCH /review-attempts/{id}/answers`, `DELETE /review-attempts/{id}`, `POST /review-attempts/{id}/submit` |

## Bổ sung 20/11 — ôn tập trên đồ thị lộ trình

| # | Tài liệu | Vị trí | Loại | Câu mới |
|---|---|---|---|---|
| 1 | BA | 10.10 bảng API (sau dòng DELETE) | thêm | \| GET \| `/api/me/review/skills?skill_ids=1,2,3` \| Ôn tập trên đồ thị lộ trình: mỗi kỹ năng → các khóa đã tham gia ôn tập được, kèm lần làm gần nhất. \| |

## Bổ sung 20/11 (tối) — đồng hồ chờ nộp, màu node và huy hiệu ôn tập trên lộ trình

| # | Tài liệu | Vị trí | Loại | Câu cũ | Câu mới / phần thêm |
|---|---|---|---|---|---|
| 1 | BA | UC-09 — Alternative Flow (nộp khi chưa đủ 2 phút) | sửa | hệ thống báo "Bạn vừa nộp bài, vui lòng chờ. Còn … để nộp lần sau."; bài vẫn giữ nguyên để nộp lại (BR-35). | hệ thống báo "Bạn vừa nộp bài, vui lòng chờ." kèm đồng hồ đếm ngược thời gian còn lại (phút:giây) và khóa nút Nộp bài tới khi hết giờ rồi tự mở lại; bài vẫn giữ nguyên để nộp lại (BR-35). |
| 2 | BA | FR-10 — Xem và quản lý lộ trình đã lưu (cuối đoạn) | thêm | — | Trong chi tiết lộ trình, mỗi kỹ năng trên đồ thị thể hiện trạng thái của người dùng bằng màu nền (Đã biết / Đang học / Chưa học, theo hồ sơ kỹ năng) và vai trò bằng viền (Mục tiêu / Mở rộng), kèm chú thích màu. Kỹ năng Đã biết / Đang học có huy hiệu Ôn tập: bấm vào thấy các khóa đã tham gia có thể ôn tập cho kỹ năng đó, điểm lần trước và nút Ôn tập; vào ôn tập từ huy hiệu thì màn ôn tập có nút quay lại lộ trình. |
| 3 | SRS | 4. bảng FR — FR-08 (cuối ô mô tả) | thêm | thêm, xóa kỹ năng (vai trò Tiên quyết, Tùy chọn, Mở rộng) và kết nối. | thêm, xóa kỹ năng (vai trò Tiên quyết, Tùy chọn, Mở rộng) và kết nối; node tô màu theo trạng thái kỹ năng (Đã biết / Đang học / Chưa học), viền theo vai trò (Mục tiêu / Mở rộng), có chú thích; node Đã biết / Đang học có huy hiệu Ôn tập. |
| 4 | SRS | 4. bảng FR — FR-11 | sửa | hai lần nộp cách nhau ít nhất 2 phút; | hai lần nộp cách nhau ít nhất 2 phút (hiện đồng hồ đếm ngược); |

Không đổi yêu cầu: menu "My learning path" đổi tên thành "Lộ trình" (giao diện); ngân hàng đề khóa 1855, 743 (dữ liệu — BA 10.10 / FR-24 đã ghi khóa chỉ ôn được khi ngân hàng đủ câu ráp đề).

## Bổ sung 21/11 — Đến hạn ôn

| # | Tài liệu | Vị trí | Loại | Câu cũ | Câu mới / phần thêm |
|---|---|---|---|---|---|
| 1 | BA | 9.6 — thêm BR-36 sau BR-35 | thêm | — | **BR-36 — Đến hạn ôn (nhắc ôn lại kỹ năng)** Kỹ năng Đã biết của người dùng mà đã từng ôn tập đạt ít nhất một lần được nhắc ôn lại theo khoảng giãn dần: đạt lần 1 → sau 7 ngày, đạt liên tiếp lần 2 → 30 ngày, từ lần 3 → 90 ngày; lần ôn gần nhất chưa đạt → 7 ngày tính từ lần đó. Đạt bài ôn tập của một khóa được tính là đã ôn mọi kỹ năng của khóa. Kỹ năng Đang học hoặc Đã biết do người dùng tự khai mà chưa ôn lần nào không được nhắc. Quá hạn chỉ nhắc, không đổi trạng thái Đã biết. Hệ thống nhắc bằng chấm cam trên huy hiệu Ôn tập ở đồ thị lộ trình, thông báo trên chuông (gom các kỹ năng đến hạn, tối đa một lần mỗi 24 giờ) và email (tối đa một lần mỗi tuần, chỉ khi người dùng bật "Nhắc ôn tập"); mỗi lần đến hạn của một kỹ năng chỉ nhắc một lần. Các khoảng nhắc là cấu hình hệ thống (`REVIEW_DUE_INTERVALS`). |
| 2 | SRS | 4. bảng FR — FR-11 (cuối ô mô tả) | sửa | gửi email kết quả; câu tự luận bị gắn cờ được Admin xem lại (FR-22). | gửi email kết quả; câu tự luận bị gắn cờ được Admin xem lại (FR-22); kỹ năng Đã biết đã từng ôn đạt được nhắc ôn lại sau 7 → 30 → 90 ngày (chấm cam trên huy hiệu, chuông tối đa 1 lần/ngày, email tối đa 1 lần/tuần theo cài đặt Nhắc ôn tập). |

## Bổ sung 25/11 — vai trò Mentor duyệt câu ôn tập AI soạn (NHÁP — Tuấn duyệt trước khi chép)

Căn cứ: `docs/Review-AI-Tu-Soan-On-Tap.md` D19–D23 (chốt 25/11). Số FR / UC / BR là **số tạm** nối tiếp các mục trên —
kiểm số cuối trong bản Word trước khi chép.

| # | Tài liệu | Vị trí | Loại | Câu cũ | Câu mới / phần thêm |
|---|---|---|---|---|---|
| 1 | BA | 4.1 Vai trò — thêm 4.1.3 Mentor sau Quản trị viên | thêm | — | **Mentor:** người có chuyên môn được Admin gán vai trò (từ một tài khoản đã đăng ký). Mentor vẫn học như Học viên; thêm quyền: xem câu hỏi ôn tập do AI soạn (câu, đáp án, giải thích / barem, đoạn tài liệu AI dựa vào), bấm **Đạt** hoặc **Phản ánh lỗi**. Mentor **không** sửa, xóa, bật / tắt câu hỏi. |
| 2 | BA | 4.1.2 Quản trị viên — danh sách quyền | thêm | — | - Gán / thu hồi vai trò Mentor; xử lý câu hỏi bị Mentor phản ánh (sửa câu, giữ tắt, bác phản ánh). |
| 3 | BA | 5.2 bảng Use Case — thêm UC-23 sau UC-22 | thêm | — | \| UC-23 \| Review AI-Generated Questions \| Mentor, Admin \| Mentor duyệt câu ôn tập AI soạn: Đạt, hoặc Phản ánh lỗi (lý do + ghi chú) → câu tắt ngay; Admin sửa câu / giữ tắt / bác phản ánh; Mentor nhận thông báo kết quả xử lý. \| |
| 4 | BA | 6.12 — thêm FR-58 sau FR-57 | thêm | — | **FR-58 — Mentor duyệt câu ôn tập AI soạn** Câu hỏi do AI soạn đã qua kiểm tra tự động được dùng ngay trong đề ôn tập và đưa vào hàng chờ của Mentor (chỉ câu AI soạn; câu soạn tay không vào). Hàng chờ có 3 nhóm: Chờ duyệt, Đã Đạt, Đã phản ánh; kỹ năng có nhiều lượt ôn được xếp trước. Mentor xem câu, đáp án, giải thích hoặc barem và đoạn tài liệu AI đã dựa vào, rồi chọn **Đạt** hoặc **Phản ánh lỗi** với một lý do (đáp án đúng bị sai; câu mơ hồ / có 2 đáp án đúng; sai kiến thức; barem tự luận không hợp lý — chỉ câu tự luận; khác — bắt buộc ghi chú). Câu bị phản ánh **tắt ngay** (không vào đề mới) và chờ Admin; mỗi câu chỉ có một phản ánh đang chờ. Câu đã Đạt vẫn phản ánh được khi phát hiện lỗi sau. Học viên không phản ánh câu hỏi. |
| 5 | BA | 6.12 — thêm FR-59 sau FR-58 | thêm | — | **FR-59 — Admin xử lý phản ánh và quản lý Mentor** Admin xem danh sách câu bị Mentor phản ánh (lọc trạng thái, lý do, kỹ năng) và chọn: **Sửa câu** (lưu xong phản ánh tự đóng, câu bật lại và coi như đã duyệt Đạt); **Giữ tắt** (câu không dùng nữa); **Bác phản ánh** (câu bật lại, coi như Đạt). Xử lý xong, Mentor đã phản ánh nhận thông báo trên chuông. Admin gán vai trò Mentor cho tài khoản có sẵn theo email và thu hồi về Học viên; không đổi được vai trò của tài khoản Admin. |
| 6 | BA | 9.6 — thêm BR-37 sau BR-36 | thêm | — | **BR-37 — Duyệt câu AI soạn** Câu AI soạn dùng ngay sau kiểm tra tự động; Mentor duyệt sau. Một phản ánh của Mentor đủ để tắt câu ngay; chỉ Admin bật lại (bác phản ánh hoặc sửa câu). Câu sinh sẵn theo lịch (D24) chỉ đưa vào đề khi Mentor đã bấm Đạt (D26). |
| 7 | BA | 10.10 — thêm bảng API mentor | thêm | — | \| Method \| Endpoint \| Mô tả \| \|---\|---\|---\| \| GET \| `/api/mentor/review-questions` \| Hàng chờ câu AI soạn; `status` (pending / passed / reported), `skill_id`, phân trang (Mentor, Admin). \| \| POST \| `/api/mentor/review-questions/{id}/pass` \| Đạt. \| \| POST \| `/api/mentor/review-questions/{id}/report` \| Phản ánh lỗi `{reason, note}` — câu tắt ngay. \| \| GET \| `/api/admin/review/reports` \| Câu bị phản ánh (Admin). \| \| POST \| `/api/admin/review/reports/{question_id}/resolve` \| `dismiss` (bác) / `keep_disabled` (giữ tắt). \| \| GET / POST / DELETE \| `/api/admin/review/mentors[/{user_id}]` \| Danh sách / gán theo email / thu hồi Mentor. \| |
| 8 | BA | 11.5 AC-07 — thêm tiêu chí | thêm | — | - Mentor phản ánh lỗi thì câu không xuất hiện trong đề mới; Admin bác phản ánh thì câu dùng lại được. Học viên gọi API mentor bị từ chối (403). |
| 9 | BA | 13.2 Ma trận truy vết — dòng Course Review | sửa | FR-24–FR-29, FR-54, FR-57 | FR-24–FR-29, FR-54, FR-57–FR-59 (thêm "Mentor duyệt câu AI soạn") |
| 10 | SRS | 3. Vai trò người dùng | thêm | — | \| Mentor \| Học như Học viên; duyệt câu ôn tập AI soạn (Đạt / Phản ánh lỗi). Do Admin gán. \| |
| 11 | SRS | 4. bảng FR — thêm FR-23 sau FR-22 | thêm | — | \| FR-23 \| Mentor duyệt câu AI soạn \| Hàng chờ câu AI soạn (chờ duyệt / đã Đạt / đã phản ánh) kèm đáp án, barem, đoạn tài liệu; Đạt hoặc Phản ánh lỗi (5 lý do) → câu tắt ngay; Admin sửa / giữ tắt / bác (bật lại), báo Mentor bằng chuông; Admin gán / thu hồi Mentor theo email. \| Mentor, Admin \| |
| 12 | SRS | 7. Thiết kế CSDL | sửa / thêm | User.role: student / admin | User.role: student / **mentor** / admin. Thêm bảng **ReviewQuestionReport** (câu, mentor, lý do, ghi chú, trạng thái open / resolved / dismissed, người và thời điểm xử lý); ReviewQuestionMeta thêm `mentor_status`, `mentor_by`, `mentor_at`, `disabled_reason`. |
