# Kịch bản kiểm thử — Xác thực & Hồ sơ người dùng

Mô tả **kịch bản** (chưa phải test code) cho `backend/tests/test_auth.py`. Mỗi kịch bản trỏ tới quy tắc trong `docs/modules/auth-profile.md` (`AP-Rxx`) hoặc mục API (`§4.x`).

Kịch bản có cột "Chờ" = phụ thuộc một `[NEEDS DECISION]`: chỉ viết test khi điểm đó đã chốt, không tự đoán kết quả mong đợi.

Tiền điều kiện chung: CSDL test có bảng `Skill` với ít nhất vài kỹ năng; người dùng mẫu `student` (đã đăng nhập khi cần).

---

## 1. Đăng ký — `POST /api/auth/register`

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| AP-T01 | Email chưa tồn tại | Đăng ký hợp lệ | 201; trả thông tin người dùng; `role = student`; response không có `hashed_password`/`password` | AP-R01, AP-R06 | |
| AP-T02 | — | Đăng ký kèm `"role": "admin"` | Không có tài khoản admin nào được tạo (nếu tạo thì `role = student`) | AP-R01 | Mã phản hồi (bỏ qua hay 422): ND-18 |
| AP-T03 | Email đã tồn tại | Đăng ký lại cùng email | 409, đúng cấu trúc lỗi | AP-R02 | |
| AP-T04 | — | Thiếu `email` / `password`, hoặc email sai định dạng | 422 | §4.1 | |
| AP-T05 | — | `full_name` > 100 ký tự | 422 | §4.1 | |
| AP-T06 | — | Đăng ký thành công | Mật khẩu trong CSDL là bản băm, khác mật khẩu gốc | AP-R06 | |
| AP-T07 | — | Mật khẩu ngắn / yếu | Theo chính sách | — | ND-05 |
| AP-T08 | — | Email khác hoa/thường so với tài khoản có sẵn | Theo quyết định chuẩn hóa | — | ND-07 |
| AP-T09 | — | Thiếu `full_name` | Theo quyết định | — | ND-37 |

## 2. Đăng nhập — `POST /api/auth/login`

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| AP-T10 | Tài khoản tồn tại | Đăng nhập đúng | 200; có access token; thông tin người dùng gồm `role` | AP-R07 | Hình dạng chi tiết: ND-19 |
| AP-T11 | Tài khoản tồn tại | Sai mật khẩu | 401 | AP-R07 | |
| AP-T12 | — | Email không tồn tại | 401 | AP-R07 | |
| AP-T13 | — | Thiếu trường | 422 | backend-rules §4 | |
| AP-T14 | Token từ AP-T10 | Gọi `GET /api/me` với token | 200 | backend-rules §2 | |

## 3. Token và phân quyền

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| AP-T20 | — | Gọi `GET /api/me` không có token | 401 | backend-rules §2 | |
| AP-T21 | — | Gọi `GET /api/me` với token sai chữ ký / chuỗi rác | 401 | backend-rules §2 | ND-01 (cách gửi token) |
| AP-T22 | — | Token đã hết hạn | 401 | backend-rules §2 | ND-01, ND-02 |
| AP-T23 | Người dùng `student` | Gọi một endpoint `/api/admin/*` | 403 | backend-rules §2 | |
| AP-T24 | Hai người dùng A, B | A gọi `/api/me*` | Chỉ thấy/sửa dữ liệu của A; không có tham số nào chọn được B | AP-R18 | |

## 4. Đăng xuất — `POST /api/auth/logout`

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| AP-T30 | Đã đăng nhập | Logout | 200 | AP-R08 | |
| AP-T31 | — | Logout không có token | 401 | §4.3 | |

## 5. Quên / đặt lại mật khẩu

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| AP-T40 | Email tồn tại | `forgot-password` | 200 + thông báo chung; tạo 1 dòng PasswordResetToken với `token_hash` (không phải mã gốc), `expires_at` = lúc tạo + `RESET_TOKEN_EXPIRE_MINUTES`; gọi `send_email` (giả lập) | AP-R09, AP-R10 | |
| AP-T41 | Email không tồn tại | `forgot-password` | 200 + **cùng** thông báo như AP-T40; không tạo token; không gửi email | AP-R09 | |
| AP-T42 | — | `forgot-password` thiếu/sai email | 422 | §4.4 | |
| AP-T43 | Mã hợp lệ từ AP-T40 | `reset-password` | 200; `hashed_password` đổi; `used_at` được ghi; đăng nhập bằng mật khẩu mới được, mật khẩu cũ → 401 | AP-R10, AP-R11 | |
| AP-T44 | Mã đã dùng | `reset-password` lần nữa | 400 | AP-R10 | |
| AP-T45 | Mã quá `expires_at` | `reset-password` | 400 | AP-R10 | |
| AP-T46 | — | Mã sai | 400 | AP-R10 | |
| AP-T47 | Người dùng có 2 mã chưa dùng | Đặt lại bằng mã thứ hai | Mã thứ nhất không còn dùng được (400) | AP-R11 | |
| AP-T48 | Giả lập lỗi khi ghi `used_at` | `reset-password` | Rollback: mật khẩu không đổi | §7 | ND-16 |
| AP-T49 | Giả lập gửi email lỗi | `forgot-password` | Theo quyết định | — | ND-39 |

## 6. Hồ sơ — `GET/PATCH /api/me`, avatar, đổi mật khẩu, summary

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| AP-T50 | Đã đăng nhập | `GET /api/me` | 200 với `user_id`, `email`, `full_name`, `avatar_url`, `role`, `created_at`; không có `hashed_password` | §4.6, AP-R06 | |
| AP-T51 | Đã đăng nhập | `PATCH /api/me` đổi `full_name`, `avatar_url` | 200 hồ sơ mới; CSDL cập nhật | AP-R04 | |
| AP-T52 | Đã đăng nhập | `PATCH /api/me` kèm `email` | Email **không** đổi | AP-R03 | Mã phản hồi: ND-18 |
| AP-T53 | Đã đăng nhập | `PATCH /api/me` kèm `role: admin` | Role **không** đổi | AP-R04 | Mã phản hồi: ND-18 |
| AP-T54 | — | `full_name` > 100 hoặc `avatar_url` > 500 ký tự | 422 | §4.7 | |
| AP-T55 | Đã đăng nhập | `change-password` đúng mật khẩu hiện tại | 200; đăng nhập bằng mật khẩu mới được | AP-R12 | |
| AP-T56 | Đã đăng nhập | `change-password` sai mật khẩu hiện tại | 400; mật khẩu không đổi | AP-R12 | |
| AP-T57 | — | `change-password` không có token | 401 | §4.9 | |
| AP-T58 | Đã đăng nhập | Upload avatar quá lớn | 413 | §4.8 | ND-12 (ngưỡng) |
| AP-T59 | Đã đăng nhập | Upload sai định dạng | 415 | §4.8 | ND-12 (định dạng) |
| AP-T60 | 2 khóa ongoing, 1 completed, 1 abandoned; 3 kỹ năng known, 1 learning; 1 lộ trình ongoing | `GET /api/me/summary` | `ongoing_courses = 2`, `completed_courses = 1`, `known_skills = 3`, `ongoing_paths = 1` | AP-R17 | ND-13 |

## 7. Kỹ năng — `GET/PATCH /api/me/skills`

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc | Chờ |
|---|---|---|---|---|---|
| AP-T70 | Có kỹ năng known và learning | `GET /api/me/skills` | Danh sách `{skill_id, skill, status, updated_at}` của người dùng hiện tại | §4.11 | |
| AP-T71 | Như trên | `?status=known` / `?status=learning` | Chỉ trả kỹ năng đúng trạng thái | AP-R13 | |
| AP-T72 | — | `?status=abc` | Lỗi dữ liệu đầu vào | §4.11 | ND-15 (400 hay 422) |
| AP-T73 | Chưa có kỹ năng 12 | `add [{12, known}]` | 200; có dòng (user, 12, known) | AP-R14 | |
| AP-T74 | Đã có kỹ năng 12 (learning) | `add [{12, known}]` | 200; cập nhật thành known, không báo trùng (upsert) | AP-R14 | |
| AP-T75 | Có kỹ năng 5 (learning), 7 | `update [{5, known}]`, `remove [7]` | 200; 5 = known; 7 bị xóa | AP-R14 | |
| AP-T76 | Có kỹ năng 7 | `add [{40, known}]` (40 không tồn tại), `remove [7]` | 404; **không** thay đổi gì (kỹ năng 7 vẫn còn) — rollback | AP-R14 | |
| AP-T77 | — | `status` ngoài `learning`/`known` | 422 | AP-R14 | |
| AP-T78 | — | Body rỗng `{}` | Không lỗi; trả danh sách hiện tại | AP-R14 (ba khóa tùy chọn) | |
| AP-T79 | — | `update`/`remove` kỹ năng người dùng chưa có; một skill vừa add vừa remove | Theo quyết định | — | ND-11 |
| AP-T80 | — | Thêm hơn 3 kỹ năng | Theo quyết định | — | ND-09 |
| AP-T81 | Hai người dùng A, B | A `PATCH /api/me/skills` | Kỹ năng của B không đổi | AP-R18 | |

## 8. Tương tác với module khác (kiểm thử tích hợp)

| ID | Tiền điều kiện | Hành động | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| AP-T90 | Khóa dạy kỹ năng A (chưa có), B (đã known) | `POST /api/courses/{id}/join` (module Course Tracking) | UserSkill: A = learning, B vẫn known | AP-R15, D05 |
| AP-T91 | Người dùng làm đạt bài ôn tập | Nộp bài (module Ôn tập) | `GET /api/me/skills` thấy mọi kỹ năng của khóa = known | AP-R15, T13 |
