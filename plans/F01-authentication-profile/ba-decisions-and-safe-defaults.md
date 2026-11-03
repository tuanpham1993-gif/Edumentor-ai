# F01 — Căn cứ, quyết định và mặc định an toàn

> Tổng hợp từ nguồn, **không** tạo yêu cầu hay quyết định mới. Thứ bậc nguồn: D-DOC-01 (`docs/decisions.md` §1). Nội dung ở mục C chưa được duyệt; mặc định an toàn (nếu có) chỉ lấy từ nguồn và **không** phải quyết định. Lập 2026-11-03.

## A. BA, SRS đã có căn cứ

| Nội dung | BA | SRS v2.0 | UI (S-xx) |
|---|---|---|---|
| Đăng ký, kiểm hợp lệ, chặn trùng | FR-01; UC-01 | SRS-AUTH-01 | S-02 |
| Đăng nhập | FR-02; UC-01 | SRS-AUTH-02 | S-01 |
| Đăng xuất | FR-02; FR-46 | SRS-AUTH-03 | S-11 |
| Làm mới phiên bằng refresh token | FR-45; FR-46 | SRS-AUTH-04 | — |
| Quên, đặt lại mật khẩu | Không có FR riêng (BA §10.2 chưa liệt kê; ND-76) | SRS-AUTH-05, 06 | S-03 … S-06 |
| Đổi mật khẩu | Không có FR riêng | SRS-AUTH-07 | S-09 |
| Xem, sửa hồ sơ | FR-03; UC-02 | SRS-PROF-01, 02 | S-07, S-08 |
| Ảnh đại diện | Không có trong BA §10.2 | SRS-PROF-03 | S-08 |
| Kỹ năng hiện có | FR-04; UC-02 | SRS-PROF-04, 05 | S-10 |
| Access token, kiểm quyền | FR-44; FR-40; FR-41 | SRS-AUTH-02 | — |
| Tiêu chí nghiệm thu | AC-01 (BA §11.2) | SRS-AC (chương 11) | — |
| Bảo mật token, mật khẩu | NFR-04, NFR-37 … NFR-39 | SRS-NFR | — |

Mã yêu cầu `AP-YC01 … AP-YC10`, chỗ BA khác quyết định: `docs/modules/auth-profile.md` §1 "Yêu cầu".

BA khác `docs/decisions.md` (theo `decisions.md`, D-DOC-01):

- BA FR-03 có thông tin mục tiêu nghề nghiệp; `User` không có cột này và `PATCH /api/me` chỉ nhận `full_name`, `avatar_url` (T04, ND-10).
- BA §10.2 thiếu refresh, quên, đặt lại, đổi mật khẩu, avatar, summary (ND-76).

## B. Quyết định đã chốt

| Mã | Nội dung |
|---|---|
| D-OWN-01 | Tuấn phụ trách Xác thực và Hồ sơ |
| D-AUTH-01 | JWT access token ký HS256 bằng `SECRET_KEY`; `Authorization: Bearer`; claim `sub`, `iat`, `exp`; chỉ chấp nhận HS256; vai trò lấy từ DB |
| D-AUTH-02 | Access token 30 phút (`ACCESS_TOKEN_EXPIRE_MINUTES=30`); hết hạn thì frontend thử làm mới, thất bại mới yêu cầu đăng nhập lại |
| D-AUTH-03 | Có refresh token; `POST /api/auth/refresh`; rotation; lưu bản băm trong PostgreSQL; logout thu hồi; access token không thu hồi tức thì |
| D-AUTH-04 | Băm mật khẩu Argon2id; chỉ lưu bản băm trong `User.hashed_password` |
| D-AUTH-05 | Chính sách mật khẩu 7 điều kiện cho register, reset-password, change-password; kiểm `confirm_password` khi có; không log mật khẩu, token |
| D06 | Không cho đổi email |
| D07 | Ảnh đại diện: tải file lên server (T04: giai đoạn 1 nhập URL, giai đoạn 2 upload) |
| D08 | Phần logout stateless **đã bị D-AUTH-03 thay một phần** |
| D09 | Có quên mật khẩu trong bản đầu |
| T01 … T07, T09, T10 ☑ | forgot, reset, change-password, avatar_url, summary, body `PATCH /me/skills`, lọc `status`, register không nhận role, mẫu Profile |
| T28 ☑ | Biến `SMTP_*`, `FRONTEND_URL`, `RESET_TOKEN_EXPIRE_MINUTES` |
| D-FE-05 | Access token ở `sessionStorage`; chưa làm refresh tới khi ND-41, ND-48 chốt; 401 → xóa token, về `/login` |
| D-FE-06 | `ProtectedRoute`, `AdminRoute` chỉ ẩn giao diện; backend kiểm quyền |
| D-FE-07 | Mock chỉ khi `VITE_USE_MOCK=true`; không hiện tài khoản, mật khẩu mẫu (ví dụ `Demo@123`) |
| D-FE-11 | Frontend theo API contract (ví dụ `PATCH /api/me/skills` theo `skill_id`) |

## C. Chưa quyết định

### C1. Điểm chờ đã có ND (PENDING)

| Mã | Nội dung | Task bị ảnh hưởng |
|---|---|---|
| ND-44 | Thư viện JWT | P04-T02 → T03, T06, T13 |
| ND-45 | Thư viện, tham số Argon2id | P04-T02, T05, T08, T09 |
| ND-46 | Tập ký tự đặc biệt, định nghĩa khoảng trắng | P04-T02 (một phần), T05, T08, T09 |
| ND-47 | Endpoint nào nhận `confirm_password` | P04-T05, T08, T09, T16, T19 |
| ND-40, ND-41, ND-42, ND-43, ND-48 | Refresh token: thời hạn, định dạng, tái sử dụng, bảng, hợp đồng refresh/logout | P04-T06 (một phần), T07, T21 |
| ND-19 | Hình dạng response login | P04-T06 |
| ND-08 | Register trả token hay chỉ thông tin người dùng | P04-T05 |
| ND-37 | `full_name` bắt buộc khi đăng ký | P04-T05 |
| ND-07 | Chuẩn hóa email | P04-T05 |
| ND-18 | Trường không được phép: bỏ qua hay 422 | P04-T05, T09 |
| ND-10 | Ô "Mục tiêu học tập" trên Profile | P04-T18 |
| ND-12, ND-62 | Avatar: giới hạn file, giai đoạn | P04-T10, T19 |
| ND-13 | Cách đếm `summary` | P04-T11 |
| ND-09, ND-11, ND-64 | Biên của `PATCH /api/me/skills` | P04-T12 |
| ND-57 | Học viên chọn kỹ năng từ đâu | P04-T20 |
| ND-36 | Thu hồi refresh token sau khi đổi, đặt lại mật khẩu | P04-T08, T09 |
| ND-39 | Gửi email quên mật khẩu đồng bộ hay nền | P04-T08 |
| ND-06 | Giới hạn số lần thử | — (chưa có Task) |
| ND-14, ND-15, ND-16 | Mã lỗi, 400/422, sync/async (dùng chung) | Mọi Task backend |
| ND-50, ND-51, ND-52, ND-56, ND-78 | Route demo, câu chữ UI, chuyển hướng quyền, trang Đăng ký, trang đích sau đăng nhập | P04-T16, T21 |
| ND-67, ND-68 | Kiểm thử frontend, responsive | P04-T22 |

### C2. Câu hỏi chưa có ND (`NEEDS_OWNER_INPUT`)

| # | Câu hỏi hoặc tài liệu còn thiếu | Ảnh hưởng |
|---|---|---|
| 1 | Định dạng link chứa mã đặt lại mật khẩu (`docs/structure.md` §3 chưa có) | P04-T08, P04-T17 |
| 2 | Database dùng cho test (`plans/plan.md` PART 6) | P04-T14 (chạy test) |
| 3 | Người làm P03-T03 … T05 (Chưa phân công) | P04-T15 … T21 |
| 4 | Mã SRS chưa được đưa vào `docs/modules/auth-profile.md` | Truy vết |

### C3. Mặc định an toàn có trong nguồn

| Mặc định | Nguồn | Điều kiện dùng |
|---|---|---|
| Frontend chưa làm refresh; nhận 401 thì xóa token, chuyển `/login` | D-FE-05 (đã chốt) | Tới khi ND-41, ND-48 chốt |
| Frontend không hiển thị câu chữ khẳng định quy tắc chưa chốt (ví dụ "JPG/PNG, tối đa 2 MB", "khác mật khẩu hiện tại") | ND-51 (ghi "tạm thời") | Tới khi ND-51 chốt — không phải quyết định |
| Chạy giao diện với dữ liệu mẫu khi chưa có backend | D-FE-07 (đã chốt) | Chỉ khi `VITE_USE_MOCK=true` |
| Ô `avatar_url` nhập tay qua `PATCH /api/me` (giai đoạn 1) | T04, AP-R16 (đã chốt) | Giai đoạn upload chờ ND-62 |
