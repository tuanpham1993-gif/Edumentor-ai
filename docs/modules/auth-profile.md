# Module: Xác thực & Hồ sơ người dùng

Đặc tả nghiệp vụ và API contract của module. Đây là nguồn chi tiết duy nhất cho module này; bảng tóm tắt endpoint ở `docs/api-endpoints.md` §2, schema đầy đủ ở `docs/database-design.md` §3, quy tắc kỹ thuật chung ở `docs/backend-rules.md`, quyết định và điểm còn mở ở `docs/decisions.md`.

Mã quy tắc `AP-Rxx` dùng để tham chiếu từ `auth-profile.tests.md` và code review.

---

## 1. Phạm vi

**Thuộc module:**

| Nhóm | Endpoint |
|---|---|
| Xác thực | `POST /api/auth/register`, `/login`, `/logout`, `/forgot-password`, `/reset-password` |
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

Theo `STRUCTURE.md` (đã cập nhật):

| Lớp | File |
|---|---|
| Router | `backend/app/routers/auth.py`, `backend/app/routers/me.py` |
| Schema | `backend/app/schemas/auth.py`, `backend/app/schemas/user.py` |
| Model | `backend/app/models/user.py`, `backend/app/models/user_skill.py`, `backend/app/models/password_reset_token.py` |
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
| Validation | `email` bắt buộc, ≤ 255 ký tự, phải là địa chỉ email; `password` bắt buộc (chính sách: `[ND-05]`); `full_name` ≤ 100 (bắt buộc hay không: `[ND-37]`) |
| Response | **201** + thông tin người dùng (trả token hay không: `[ND-08]`) |
| Lỗi | **409** email đã tồn tại; **422** dữ liệu sai |
| Quy tắc | AP-R01, AP-R02, AP-R06 |

### 4.2. `POST /api/auth/login`

| Mục | Nội dung |
|---|---|
| Xác thực | Công khai |
| Body | `email`, `password` |
| Response | **200** + access token + thông tin người dùng (gồm `role`). Hình dạng chi tiết: `[ND-19]` |
| Lỗi | **401** sai thông tin đăng nhập |
| Quy tắc | AP-R06, AP-R07 |

### 4.3. `POST /api/auth/logout`

| Mục | Nội dung |
|---|---|
| Xác thực | Người dùng |
| Body | — |
| Response | **200** |
| Lỗi | **401** |
| Quy tắc | AP-R08 |

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
| Body | `token`, `new_password` |
| Validation | `new_password` theo chính sách mật khẩu `[ND-05]` |
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
| Body | `current_password`, `new_password` |
| Validation | `new_password` theo chính sách `[ND-05]` |
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
| AP-R06 | Không lưu mật khẩu gốc; không trả `hashed_password` (hay bất kỳ mật khẩu nào) trong response. | `.docx` 3.1, T03 |
| AP-R07 | Đăng nhập thành công trả access token và thông tin người dùng gồm `role`; sai → 401. | Sheet Endpoint |
| AP-R08 | Đăng xuất: JWT không lưu trạng thái — client xóa token, server trả 200; không có bảng thu hồi token. | D08 |
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

---

## 6. Luồng nghiệp vụ

### Đăng ký
```text
Client gửi email, password, full_name
 → kiểm tra dữ liệu (AP-R02, [ND-05, ND-07, ND-37])
 → email đã tồn tại? → 409
 → băm mật khẩu, tạo User role = student (AP-R01)
 → 201 + thông tin người dùng ([ND-08] token?)
 → (Frontend, wireframe 04) chọn kỹ năng hiện tại → PATCH /api/me/skills ([ND-08, ND-09])
```

### Đăng nhập / đăng xuất
```text
Login:  email + password → tìm User → so khớp mật khẩu băm
        → sai → 401 | đúng → 200 + access token + user (gồm role)
Logout: có token hợp lệ → 200 (server không lưu gì; client xóa token)
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

---

## 8. Bảo mật

| Chủ đề | Quy tắc | Nguồn |
|---|---|---|
| Mật khẩu | Chỉ lưu bản băm; không bao giờ trả về; thuật toán `[ND-04]`; chính sách `[ND-05]` | `.docx` 3.1 |
| Leo thang quyền | Không nhận `role` ở register và `PATCH /api/me` | T09 |
| Dò email | `forgot-password` trả cùng thông báo | T01 |
| Mã đặt lại | Chỉ lưu bản băm, có hạn, dùng một lần, vô hiệu mã cũ khi đặt lại thành công | T02, `.docx` 3.4 |
| IDOR | `/api/me*` chỉ dùng user từ token | CONVENTIONS §1 |
| Token | Cơ chế `[ND-01]`, thời hạn `[ND-02]`, refresh `[ND-03]`; token cũ sau khi đổi mật khẩu `[ND-36]` | D08 |
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

`ND-01`, `ND-02`, `ND-03`, `ND-04`, `ND-05`, `ND-06`, `ND-07`, `ND-08`, `ND-09`, `ND-10`, `ND-11`, `ND-12`, `ND-13`, `ND-18`, `ND-19`, `ND-36`, `ND-37`, `ND-38`, `ND-39` — chi tiết trong `docs/decisions.md` §4.1.
