# Module: Xác thực & Hồ sơ người dùng

Đặc tả nghiệp vụ và API contract của module. Đây là nguồn chi tiết duy nhất cho module này; bảng tóm tắt endpoint ở `docs/api-endpoints.md` §2, schema đầy đủ ở `docs/database-design.md` §3, quy tắc kỹ thuật chung ở `docs/backend-rules.md`, quyết định và điểm còn mở ở `docs/decisions.md`.

Mã quy tắc `AP-Rxx` dùng để tham chiếu từ `auth-profile.tests.md` và code review.

---

## 1. Phạm vi

**Owner: Tuấn** (D-OWN-01) · **Đặc tả: SPEC CONFIRMED** (các điểm còn mở ở §10) · **Implementation: NOT IMPLEMENTED**

**Thuộc module:**

| Nhóm | Endpoint |
|---|---|
| Xác thực | `POST /api/auth/register`, `/login`, `/refresh`, `/logout`, `/forgot-password`, `/reset-password` |
| Hồ sơ | `GET /api/me`, `PATCH /api/me`, `POST /api/me/avatar`, `POST /api/me/change-password`, `GET /api/me/summary` |
| Kỹ năng | `GET /api/me/skills`, `PATCH /api/me/skills` |
| Hạ tầng dùng chung | `core/security.py`, `core/dependencies.py` (`get_current_user`, `require_admin`), `core/email.py` |

**Không thuộc module** (chỉ là dependency, xem mục 9):

- `/api/me/courses*`, `/api/me/bookmarks*`, `POST /api/courses/{id}/join` — module Course Tracking.
- `/api/me/review-history*` — module Ôn tập (`docs/modules/review-assessment.md`).
- `/api/me/learning-paths` — module Learning Path.
- Tạo tài khoản admin — `scripts/create_admin.py`, không qua API.

---

## 2. File liên quan

Theo `docs/structure.md` (đã cập nhật):

| Lớp | File |
|---|---|
| Router | `backend/app/routers/auth.py`, `backend/app/routers/me.py` |
| Schema | `backend/app/schemas/auth.py`, `backend/app/schemas/user.py` |
| Model | `backend/app/models/user.py`, `backend/app/models/user_skill.py`, `backend/app/models/password_reset_token.py`; model cho bảng RefreshToken — **chỉ tạo sau khi ND-43 được duyệt** (tên file sẽ ghi vào `docs/structure.md` lúc đó) |
| Service | `backend/app/services/auth_service.py`, `backend/app/services/user_service.py` |
| Core | `backend/app/core/security.py`, `backend/app/core/dependencies.py`, `backend/app/core/email.py` (dùng chung với module Ôn tập) |
| Repository | `backend/app/repositories/` (STRUCTURE chưa đặt tên file) |
| Script | `backend/scripts/create_admin.py` |
| Test | `backend/tests/test_auth.py` |

Frontend tương ứng (tham khảo): `api/auth.api.js`, `api/me.api.js`, `pages/auth/*`, `pages/profile/ProfilePage.jsx`, `components/profile/*`.

---

## 3. Dữ liệu

Chi tiết cột: `docs/database-design.md` §3.1, §3.2, §3.4. Dưới đây chỉ là các điểm module phải tôn trọng.

### Bảng thuộc module (đọc + ghi)

| Bảng | Khóa | Ràng buộc quan trọng |
|---|---|---|
| `User` (tên thật `users`) | PK `user_id` | `email` NN UQ; `hashed_password` NN; `role` NN DEFAULT `student` CHECK (`student`, `admin`); `full_name` ≤ 100; `avatar_url` ≤ 500 NULL |
| `UserSkill` | PK (`user_id`, `skill_id`) | `status` NN DEFAULT `known` CHECK (`learning`, `known`); `updated_at` |
| `PasswordResetToken` | PK `reset_id` | `token_hash` NN UQ; `expires_at` NN; `used_at` NULL = chưa dùng |
| `RefreshToken` — **PROPOSED** (ND-43) | PK `refresh_token_id` | `user_id` NN FK → User CASCADE; `token_hash` NN UQ; `expires_at` NN; `revoked_at` NULL = còn hiệu lực. Chi tiết: `database-design.md` §3.5 |

### Bảng chỉ đọc

| Bảng | Dùng cho |
|---|---|
| `Skill` | Kiểm tra `skill_id` tồn tại; trả tên kỹ năng trong `GET /api/me/skills` |
| `StudentCourse` | Đếm cho `GET /api/me/summary` |
| `LearningPath` | Đếm cho `GET /api/me/summary` |

### Quan hệ

```text
User 1 ──< UserSkill >── 1 Skill          (User CASCADE, Skill RESTRICT)
User 1 ──< PasswordResetToken             (CASCADE)
User 1 ──< RefreshToken                   (CASCADE — PROPOSED)
User 1 ──< StudentCourse, LearningPath    (thuộc module khác)
```

---

## 4. API contract

Quy ước chung (xác thực, cấu trúc lỗi, 401/403/404): `docs/backend-rules.md`. "Người dùng" = yêu cầu xác thực, mọi role.

### 4.1. `POST /api/auth/register`

| Mục | Nội dung |
|---|---|
| Xác thực | Công khai |
| Body | `email`, `password`, `full_name` |
| Validation | `email` bắt buộc, ≤ 255 ký tự, phải là địa chỉ email (kiểm định dạng: AUD-07); `password` bắt buộc, theo chính sách AP-R19; `confirm_password` nếu endpoint nhận trường này (`[ND-47]`) phải khớp `password` (AP-R20); `full_name` ≤ 100 (bắt buộc hay không: `[ND-37]`) |
| Response | **201** + thông tin người dùng (trả token hay không: `[ND-08]`) |
| Lỗi | **409** email đã tồn tại; **422** dữ liệu sai |
| Quy tắc | AP-R01, AP-R02, AP-R06 |

### 4.2. `POST /api/auth/login`

| Mục | Nội dung |
|---|---|
| Xác thực | Công khai |
| Body | `email`, `password` |
| Response | **200** + access token (JWT, 30 phút) + refresh token + thông tin người dùng (gồm `role`). Hình dạng chi tiết, refresh token nằm trong body hay cookie: `[ND-19, ND-41]` |
| Lỗi | **401** sai thông tin đăng nhập |
| Quy tắc | AP-R06, AP-R07, AP-R21 |

### 4.3. `POST /api/auth/logout`

| Mục | Nội dung |
|---|---|
| Xác thực | Người dùng (có bắt buộc access token còn hạn không: `[ND-48]`) |
| Body | Refresh token cần thu hồi — cách gửi và phạm vi thu hồi (một phiên / mọi phiên): `[ND-41, ND-48]` |
| Response | **200** |
| Lỗi | **401** |
| Quy tắc | AP-R08 |

### 4.3a. `POST /api/auth/refresh` *(D-AUTH-03 — hợp đồng là BẢN NHÁP)*

| Mục | Nội dung |
|---|---|
| Xác thực | Công khai; xác thực bằng chính refresh token (không cần access token còn hạn) |
| Request | Refresh token — định dạng và cách gửi (JSON body hay cookie `httpOnly`): `[ND-41]` |
| Response | Access token mới (30 phút) + refresh token mới (rotation). Tên trường, có `token_type` không, có trả kèm thông tin người dùng không: `[ND-48, ND-19]` |
| Lỗi | Refresh token hết hạn / bị thu hồi / đã bị xoay vòng / không hợp lệ → làm mới thất bại, frontend yêu cầu đăng nhập lại. **Mã HTTP chưa chốt** `[ND-48, ND-15]` |
| Quy tắc | AP-R21, AP-R22 |

### 4.4. `POST /api/auth/forgot-password`

| Mục | Nội dung |
|---|---|
| Xác thực | Công khai |
| Body | `email` |
| Response | **200** + thông báo chung, **luôn giống nhau** dù email có tồn tại hay không (ví dụ "Nếu email đúng, bạn sẽ nhận được hướng dẫn") |
| Lỗi | **422** dữ liệu sai |
| Quy tắc | AP-R09, AP-R10 |

### 4.5. `POST /api/auth/reset-password`

| Mục | Nội dung |
|---|---|
| Xác thực | Công khai (mã trong email là bằng chứng sở hữu) |
| Body | `token`, `new_password` (+ `confirm_password` nếu ND-47 chọn) |
| Validation | `new_password` theo chính sách AP-R19; khớp `confirm_password` nếu có (AP-R20) |
| Response | **200** |
| Lỗi | **400** mã sai, hết hạn hoặc đã dùng |
| Quy tắc | AP-R10, AP-R11 |

### 4.6. `GET /api/me`

| Mục | Nội dung |
|---|---|
| Xác thực | Người dùng |
| Response | **200** `user_id`, `email`, `full_name`, `avatar_url`, `role`, `created_at` |
| Lỗi | **401** |
| Quy tắc | AP-R06, AP-R18 |

### 4.7. `PATCH /api/me`

| Mục | Nội dung |
|---|---|
| Xác thực | Người dùng |
| Body | `full_name`, `avatar_url` — chỉ hai trường này (không có `email`, `role`) |
| Validation | `full_name` ≤ 100; `avatar_url` ≤ 500 (kiểm tra định dạng URL: `[ND-12]`). Gửi kèm `email`/`role`: `[ND-18]` |
| Response | **200** hồ sơ mới (cùng hình dạng `GET /api/me`) |
| Lỗi | **401**; **422** |
| Quy tắc | AP-R03, AP-R04, AP-R16 |

### 4.8. `POST /api/me/avatar` *(tùy chọn — giai đoạn 2, T04/D07)*

| Mục | Nội dung |
|---|---|
| Xác thực | Người dùng |
| Body | File ảnh |
| Response | **200** `avatar_url` |
| Lỗi | **413** file quá lớn; **415** sai định dạng; **401** |
| Chưa chốt | Dung lượng tối đa, định dạng cho phép, nơi lưu file `[ND-12]` |
| Quy tắc | AP-R16 |

### 4.9. `POST /api/me/change-password`

| Mục | Nội dung |
|---|---|
| Xác thực | Người dùng |
| Body | `current_password`, `new_password` (+ `confirm_password` nếu ND-47 chọn) |
| Validation | `new_password` theo chính sách AP-R19; khớp `confirm_password` nếu có (AP-R20) |
| Response | **200** (không chứa mật khẩu) |
| Lỗi | **400** sai mật khẩu hiện tại; **401** chưa xác thực |
| Quy tắc | AP-R06, AP-R12 |

### 4.10. `GET /api/me/summary`

| Mục | Nội dung |
|---|---|
| Xác thực | Người dùng |
| Response | **200** `{"ongoing_courses", "completed_courses", "known_skills", "ongoing_paths"}` (số nguyên) |
| Lỗi | **401** |
| Quy tắc | AP-R17 |

### 4.11. `GET /api/me/skills`

| Mục | Nội dung |
|---|---|
| Xác thực | Người dùng |
| Query | `status` (tùy chọn) ∈ `known`, `learning` |
| Response | **200** danh sách `{skill_id, skill, status, updated_at}` |
| Lỗi | **401**; giá trị `status` sai → lỗi dữ liệu đầu vào (400/422: `[ND-15]`) |
| Quy tắc | AP-R13 |

### 4.12. `PATCH /api/me/skills`

| Mục | Nội dung |
|---|---|
| Xác thực | Người dùng |
| Body | `{"add": [{"skill_id": int, "status": "known"\|"learning"}], "update": [{"skill_id": int, "status": "known"\|"learning"}], "remove": [int]}` — cả ba khóa đều tùy chọn |
| Validation | `status` chỉ nhận `learning` hoặc `known`; mọi `skill_id` phải tồn tại trong `Skill`. Trường hợp biên: `[ND-09, ND-11]` |
| Response | **200** danh sách kỹ năng mới (cùng hình dạng `GET /api/me/skills`) |
| Lỗi | **404** `skill_id` không tồn tại; **422** dữ liệu sai; **401** |
| Quy tắc | AP-R14 |

---

## 5. Quy tắc nghiệp vụ

| Mã | Quy tắc | Nguồn |
|---|---|---|
| AP-R01 | `register` luôn tạo `role = student`; không nhận `role` từ client. | T09 |
| AP-R02 | Mỗi email chỉ một tài khoản; đăng ký trùng → 409. | `.docx` 3.1, sheet Endpoint |
| AP-R03 | Không cho đổi email: `PATCH /api/me` không nhận `email`. | D06, T10 |
| AP-R04 | `PATCH /api/me` chỉ nhận `full_name`, `avatar_url`; không cho sửa `role`. | T04, T09 |
| AP-R05 | Tài khoản admin chỉ tạo bằng `scripts/create_admin.py`. | T09 |
| AP-R06 | Không lưu mật khẩu gốc; chỉ lưu bản băm **Argon2id** trong `User.hashed_password`; đăng nhập dùng hàm xác minh của thư viện; không trả `hashed_password` (hay bất kỳ mật khẩu nào) trong response. | `.docx` 3.1, T03, D-AUTH-04 |
| AP-R07 | Đăng nhập thành công trả access token, refresh token và thông tin người dùng gồm `role`; sai → 401. | Sheet Endpoint, D-AUTH-03 |
| AP-R08 | Đăng xuất: backend thu hồi refresh token tương ứng (ghi `revoked_at`); client xóa token; server trả 200. Access token vẫn stateless — **không** bị thu hồi tức thì, còn hiệu lực tối đa tới `exp`. | D-AUTH-03 (thay một phần D08) |
| AP-R09 | `forgot-password` luôn trả cùng một thông báo, dù email có tồn tại hay không. | T01 |
| AP-R10 | Mã đặt lại: ngẫu nhiên; chỉ lưu bản băm (`token_hash`); hạn = lúc tạo + `RESET_TOKEN_EXPIRE_MINUTES`; dùng một lần. Mã sai/hết hạn/đã dùng → 400. | T01, T02, `.docx` 3.4 |
| AP-R11 | Đặt lại thành công: cập nhật `User.hashed_password`, ghi `used_at`, vô hiệu các mã cũ chưa dùng của tài khoản đó. | T02, `.docx` 3.4 |
| AP-R12 | Đổi mật khẩu phải nhập đúng mật khẩu hiện tại; sai → 400. | T03, `.docx` 3.1 |
| AP-R13 | `GET /api/me/skills` lọc được theo `status`. | T07 |
| AP-R14 | `PATCH /api/me/skills`: một transaction cho cả `add`/`update`/`remove`; lỗi một phần → hủy toàn bộ; `skill_id` không tồn tại → 404; `add` kỹ năng đã có = cập nhật (upsert theo `(user_id, skill_id)`), không báo trùng. | T06, G3 |
| AP-R15 | `UserSkill` còn được module khác ghi: tham gia khóa → thêm kỹ năng của khóa ở `learning` (kỹ năng đã `known` giữ nguyên); làm đạt bài ôn tập → `known` cho mọi kỹ năng của khóa. Frontend không gửi request cập nhật kỹ năng riêng trong các luồng này. | D05, T13 |
| AP-R16 | Ảnh đại diện: nhập đường dẫn qua `PATCH /api/me` (giai đoạn 1) hoặc tải file qua `POST /api/me/avatar` (giai đoạn 2). | T04, D07 |
| AP-R17 | `GET /api/me/summary`: `ongoing_courses`, `completed_courses` đếm StudentCourse theo status; `known_skills` đếm UserSkill `known`; `ongoing_paths` đếm LearningPath `ongoing`. Cách đếm chính thức: `[ND-13]`. | T05 |
| AP-R18 | Mọi endpoint `/api/me*` lấy người dùng từ token, không nhận `user_id` từ client. | CONVENTIONS §1 |
| AP-R19 | **Chính sách mật khẩu** — áp dụng giống nhau cho `register` (`password`), `reset-password` và `change-password` (`new_password`); **không** áp cho `login`: (1) ≥ 8 ký tự (đếm theo ký tự Unicode); (2) ≤ 128 byte khi mã hóa UTF-8 (đếm độ dài chuỗi byte sau khi encode UTF-8 — ký tự có dấu chiếm 2–3 byte, nên 128 byte có thể ít hơn 128 ký tự); (3) ≥ 1 chữ hoa ASCII `A-Z`; (4) ≥ 1 chữ thường ASCII `a-z`; (5) ≥ 1 chữ số `0-9`; (6) ≥ 1 ký tự đặc biệt (tập ký tự: `[ND-46]`); (7) không chứa khoảng trắng (định nghĩa khoảng trắng: `[ND-46]`). Mọi endpoint dùng **cùng một** hàm kiểm. Mã lỗi: `[ND-15]`. | D-AUTH-05 |
| AP-R20 | Khi request có `confirm_password` (endpoint nào: `[ND-47]`): backend kiểm khớp với mật khẩu; không lưu `confirm_password`. | D-AUTH-05 |
| AP-R21 | **Token**: access token là JWT ký HS256 bằng `SECRET_KEY`, chứa `sub` (user_id), `iat`, `exp`; hết hạn sau `ACCESS_TOKEN_EXPIRE_MINUTES` = 30 phút; gửi qua `Authorization: Bearer`. Backend xác minh chữ ký, thời hạn, **chỉ chấp nhận HS256**; tải người dùng và **vai trò từ database** (không tin claim vai trò). Token hết hạn/sai → 401. | D-AUTH-01, D-AUTH-02 |
| AP-R22 | **Refresh token**: cấp khi đăng nhập; chỉ lưu bản băm trong PostgreSQL; làm mới qua `POST /api/auth/refresh` với **rotation** (token cũ bị vô hiệu, cấp token mới); token hết hạn / bị thu hồi / đã bị xoay vòng / không hợp lệ → làm mới thất bại; token đã xoay vòng hoặc thu hồi không được dùng lại. Thời hạn: `[ND-40]`; định dạng và cách gửi: `[ND-41]`; xử lý khi phát hiện tái sử dụng: `[ND-42]`. | D-AUTH-03 |
| AP-R23 | Không ghi mật khẩu, `confirm_password`, access token, refresh token hay mã đặt lại mật khẩu (dạng gốc) vào log. | D-AUTH-05 |

---

## 6. Luồng nghiệp vụ

### Đăng ký
```text
Client gửi email, password, full_name
 → kiểm tra dữ liệu (chính sách mật khẩu AP-R19, confirm_password AP-R20 [ND-47], [ND-07, ND-37])
 → email đã tồn tại? → 409
 → băm mật khẩu Argon2id, tạo User role = student (AP-R01, AP-R06)
 → 201 + thông tin người dùng ([ND-08] token?)
 → (Frontend, wireframe 04) chọn kỹ năng hiện tại → PATCH /api/me/skills ([ND-08, ND-09])
```

### Đăng nhập / làm mới / đăng xuất
```text
Login:   email + password → tìm User → xác minh mật khẩu (Argon2id)
         → sai → 401
         → đúng → tạo access token (JWT HS256, 30 phút)
                 + tạo refresh token, lưu bản băm vào RefreshToken
                 → 200 + access token + refresh token + user (gồm role)   ([ND-19, ND-41])

Request: Authorization: Bearer <access_token>
         → xác minh chữ ký + exp + alg = HS256 → tải User từ DB (role từ DB)
         → sai / hết hạn → 401

Refresh: access token hết hạn → frontend gọi POST /api/auth/refresh với refresh token
         → băm → tìm token_hash
         → không thấy / hết hạn / đã thu hồi / đã xoay vòng → thất bại → frontend yêu cầu đăng nhập lại
           (mã HTTP: [ND-48]; xử lý tái sử dụng: [ND-42])
         → hợp lệ → [một transaction] thu hồi token cũ + lưu token mới
         → trả access token mới + refresh token mới

Logout:  → thu hồi refresh token tương ứng (ghi revoked_at) ([ND-48]: phạm vi)
         → 200; client xóa token khỏi sessionStorage
         (access token đã cấp vẫn hợp lệ tới exp — tối đa 30 phút)
```

### Quên mật khẩu
```text
POST /forgot-password {email}
 → tìm User theo email
   ├─ có: tạo mã ngẫu nhiên → lưu token_hash + expires_at → gửi email link FRONTEND_URL + mã
   └─ không: không làm gì
 → luôn trả 200 + cùng một thông báo (AP-R09)
 (gửi email lỗi thì xử lý ra sao: [ND-39])

POST /reset-password {token, new_password}
 → băm token → tìm dòng khớp token_hash
 → không thấy / expires_at đã qua / used_at có giá trị → 400
 → [một transaction] cập nhật hashed_password + ghi used_at + vô hiệu mã cũ chưa dùng (AP-R11)
 → 200
```

### Đổi mật khẩu
```text
Đã xác thực → kiểm tra current_password → sai → 400
 → băm new_password → cập nhật → 200
```

### Cập nhật kỹ năng
```text
PATCH /api/me/skills {add, update, remove}
 → [một transaction]
     kiểm tra mọi skill_id tồn tại → thiếu → rollback, 404
     add: upsert (user_id, skill_id, status)
     update: đổi status
     remove: xóa dòng
 → 200 danh sách kỹ năng mới
```

---

## 7. Transaction

| Thao tác | Các ghi trong cùng transaction | Nguồn |
|---|---|---|
| `PATCH /api/me/skills` | Mọi thao tác add/update/remove | T06 |
| `POST /api/auth/reset-password` | Cập nhật `hashed_password`, ghi `used_at`, vô hiệu mã cũ | `.docx` 3.4 + CONVENTIONS §3 (sửa nhiều bản ghi liên quan) |
| `POST /api/auth/forgot-password` | Tạo `PasswordResetToken` — gửi email nằm ngoài transaction (`backend-rules.md` §3); xử lý khi gửi lỗi: `[ND-39]` | T01 |
| `POST /api/auth/refresh` | Thu hồi refresh token cũ + lưu refresh token mới (rotation) | D-AUTH-03 |
| `POST /api/auth/reset-password`, `change-password` | Có thu hồi mọi refresh token của người dùng trong cùng transaction không: `[ND-36]` | D-AUTH-03 |

---

## 8. Bảo mật

| Chủ đề | Quy tắc | Nguồn |
|---|---|---|
| Mật khẩu | Chỉ lưu bản băm Argon2id (thư viện/tham số `[ND-45]`); không bao giờ trả về; chính sách AP-R19; không ghi log (AP-R23) | `.docx` 3.1, D-AUTH-04, D-AUTH-05 |
| Leo thang quyền | Không nhận `role` ở register và `PATCH /api/me` | T09 |
| Dò email | `forgot-password` trả cùng thông báo | T01 |
| Mã đặt lại | Chỉ lưu bản băm, có hạn, dùng một lần, vô hiệu mã cũ khi đặt lại thành công | T02, `.docx` 3.4 |
| IDOR | `/api/me*` chỉ dùng user từ token | CONVENTIONS §1 |
| Access token | JWT HS256, `sub`/`iat`/`exp`, 30 phút, Bearer header; chỉ chấp nhận HS256; vai trò lấy từ DB (AP-R21). `SECRET_KEY` ngẫu nhiên, đủ mạnh, không commit. Thư viện JWT `[ND-44]`. Access token **không** thu hồi tức thì được | D-AUTH-01, D-AUTH-02 |
| Refresh token | Lưu bản băm trong PostgreSQL; rotation; logout thu hồi; token cũ không dùng lại (AP-R22). Chi tiết `[ND-40, ND-41, ND-42, ND-43, ND-48]`; token sau khi đổi mật khẩu `[ND-36]` | D-AUTH-03 |
| Lưu token phía client | Frontend định hướng lưu trong `sessionStorage` (chưa thay đổi khi chưa được duyệt). **Rủi ro đã ghi nhận:** JavaScript đọc được `sessionStorage`, nên một lỗi XSS có thể đánh cắp token — đặc biệt nghiêm trọng với refresh token (sống lâu hơn access token). Giảm thiểu cần cân nhắc: chống XSS ở frontend (không render HTML thô), Content-Security-Policy, thời hạn refresh token hợp lý (ND-40), cân nhắc cookie `httpOnly` cho refresh token (ND-41). `sessionStorage` mất khi đóng tab → ảnh hưởng ý nghĩa ô "Ghi nhớ đăng nhập" (ND-41) | D-AUTH-01 |
| Brute force | Giới hạn tần suất `[ND-06]` | — |
| Upload | 413/415; chi tiết `[ND-12]` | T04 |

---

## 9. Phụ thuộc với module khác

| Module | Chiều | Nội dung |
|---|---|---|
| Ôn tập | Ôn tập → Auth/Profile | Ôn tập dùng `get_current_user`; khi làm đạt, ghi `UserSkill = known` (bảng thuộc module này) trong transaction nộp bài; dùng chung `core/email.py` |
| Course Tracking | Course Tracking → Auth/Profile | `POST /api/courses/{id}/join` ghi `UserSkill = learning` nếu chưa `known` (D05). Ownership vẫn thuộc Course Tracking |
| Course Tracking, Learning Path | Auth/Profile → (đọc) | `GET /api/me/summary` đếm `StudentCourse`, `LearningPath` |
| Mọi module | → Auth/Profile | `get_current_user`, `require_admin` trong `core/dependencies.py` |

---

## 10. Điểm còn mở

Đã chốt từ ND-01 … ND-05: D-AUTH-01 … D-AUTH-05. Còn mở: `ND-40`, `ND-41`, `ND-42`, `ND-43`, `ND-44`, `ND-45`, `ND-46`, `ND-47`, `ND-48`, `ND-06`, `ND-07`, `ND-08`, `ND-09`, `ND-10`, `ND-11`, `ND-12`, `ND-13`, `ND-18`, `ND-19`, `ND-36`, `ND-37`, `ND-38`, `ND-39` — chi tiết trong `docs/decisions.md` §4.1.
