---
name: auth-profile
description: Điểm vào cho module Xác thực & Hồ sơ người dùng (do Tuấn phụ trách) của project EduMentor AI — register, login, logout, forgot-password, reset-password, change-password, GET/PATCH /api/me, /api/me/avatar, /api/me/summary, GET/PATCH /api/me/skills, bảng User/UserSkill/PasswordResetToken, core/security.py, core/dependencies.py (get_current_user, require_admin). Dùng skill này mỗi khi implement, sửa, review hoặc viết test cho các phần trên, kể cả khi người dùng chỉ nói "làm đăng nhập", "sửa hồ sơ", "kỹ năng của tôi", "quên mật khẩu" hay mở routers/auth.py, routers/me.py, services/auth_service.py, services/user_service.py. Skill project này được ưu tiên hơn skill cấp user edumentor-auth-profile trong repo này.
---

# Auth & Profile — EduMentor AI

```text
Owner:          Tuấn                              (D-OWN-01)
Module:         Authentication & User Profile
Status:         SPEC CONFIRMED
Implementation: NOT IMPLEMENTED
Security/business decisions: một phần PENDING / BLOCKED (§6)
```

Skill này là điểm vào cho module Xác thực & Hồ sơ: phạm vi, trạng thái từng phần, nguồn cần đọc, điều cấm. Chi tiết nghiệp vụ nằm trong `docs/` — đọc ở đó, không làm theo trí nhớ.

**Ưu tiên:** skill project-local này và tài liệu trong repo được ưu tiên cho repository này. Không dùng skill EduMentor cấp user/chung (`edumentor-auth-profile`, `database-schema`) khi chúng mâu thuẫn với tài liệu project.

## 0. Trạng thái — luôn phân biệt

| Trạng thái | Nghĩa | Claude được làm gì |
|---|---|---|
| **SPEC CONFIRMED** | Phạm vi/quy tắc đã được nhóm xác nhận ("Nhóm đồng ý" / "Đã chốt" trong `docs/EduMentor_Checklist_Da_Sua_API.xlsx`, hoặc endpoint "Giữ" từ đặc tả gốc) | Hỗ trợ implement theo `docs/` |
| **IMPLEMENTED** | Đã có code chạy | Hiện **chưa** có endpoint nào ở trạng thái này |
| **PENDING** | Còn `ND-xx` chưa chốt | Không implement phần đó; làm phần còn lại và nói rõ chỗ chờ |
| **BLOCKED** | Phần bắt buộc phụ thuộc vào quyết định chưa chốt | Dừng, hỏi Tuấn trước khi code phần đó |
| **CONFLICT** | Hai nguồn mô tả khác nhau | Không tự chọn; yêu cầu nhóm quyết định |

Không dùng "DONE" cho phần chưa có code. Cột "Đã làm xong" trong sheet "Endpoint (bản mới)" hiện ☐ cho mọi endpoint.

## 1. Phân công

| Module | Owner | Status |
|---|---|---|
| Auth & Profile | **Tuấn** | SPEC CONFIRMED — NOT IMPLEMENTED |
| Review & Assessment | **Tuấn** | SPEC CONFIRMED — NOT IMPLEMENTED (skill `review-assessment`) |
| Course Tracking | Không phải Tuấn | OUT OF SCOPE |
| Feedback | Chưa rõ (Khôi/Tâm) | PENDING |
| Learning Path | Người khác | OUT OF SCOPE |
| Admin Questions | CONFLICT-SCOPE-01 | DO NOT ASSUME |

Nguồn đầy đủ: `docs/decisions.md` §2 "Phân công". Cột "Phụ trách = Hòa" của §2 trong Excel là thông tin cũ, đã được thay bằng D-OWN-01.

## 2. Nguồn sự thật (đọc theo thứ tự)

1. `docs/decisions.md` — D-OWN-01, **D-AUTH-01 … D-AUTH-05**, D06, D07, D08 (đã bị D-AUTH-03 thay một phần), D09, trạng thái T-item, `ND-xx`.
2. `docs/modules/auth-profile.md` — contract (§4), quy tắc `AP-Rxx` (§5), luồng (§6), transaction (§7), bảo mật (§8).
3. `docs/api-endpoints.md` §2, `docs/backend-rules.md`, `docs/database-design.md` §3.1, §3.2, §3.4.
4. `docs/modules/auth-profile.tests.md` — kịch bản test.
5. `docs/EduMentor_Checklist_Da_Sua_API.xlsx` — nguồn gốc trạng thái tick (đã chép vào `decisions.md`).

## 3. Phạm vi và trạng thái

### Authentication

| Method | Endpoint | Đặc tả | Nguồn | Phần còn PENDING / BLOCKED |
|---|---|---|---|---|
| POST | `/api/auth/register` | SPEC CONFIRMED | Giữ + T09 ☑, D-AUTH-05 | ND-46, ND-47, ND-07, ND-08, ND-18, ND-37 |
| POST | `/api/auth/login` | SPEC CONFIRMED | Giữ, D-AUTH-01, 02, 03 | ND-19, ND-41 |
| POST | `/api/auth/refresh` | SPEC CONFIRMED (hợp đồng là bản nháp) | D-AUTH-03 | ND-40, ND-41, ND-42, ND-43, ND-48 — **BLOCKED** cho tới khi ND-43 (bảng) và ND-41/ND-48 (hợp đồng) được chốt |
| POST | `/api/auth/logout` | SPEC CONFIRMED | Giữ, D-AUTH-03 (thay một phần D08) | ND-48; phụ thuộc bảng RefreshToken (ND-43) |
| POST | `/api/auth/forgot-password` | SPEC CONFIRMED | T01 ☑, D09 | ND-39 |
| POST | `/api/auth/reset-password` | SPEC CONFIRMED | T02 ☑, D-AUTH-05 | ND-46, ND-47, ND-36 |

### User Profile

| Method | Endpoint | Đặc tả | Nguồn | Phần còn PENDING / BLOCKED |
|---|---|---|---|---|
| GET | `/api/me` | SPEC CONFIRMED | Giữ | — |
| PATCH | `/api/me` | SPEC CONFIRMED | T04 ☑, T09 ☑, D06 | ND-12 (định dạng `avatar_url`), ND-18 |
| POST | `/api/me/avatar` | SPEC CONFIRMED (tùy chọn) | T04 ☑, D07 = B | **AUD-06 PENDING**: D07 chọn upload nhưng T04 xếp vào "giai đoạn 2" — chưa rõ có làm trong v1; ND-12 (dung lượng, định dạng, nơi lưu). Hỏi Tuấn trước khi implement |
| POST | `/api/me/change-password` | SPEC CONFIRMED | T03 ☑, D-AUTH-05 | ND-46, ND-47, ND-36 |
| GET | `/api/me/summary` | SPEC CONFIRMED (một phần) | T05 ☑ | ND-13 (cách đếm — ghi chú nhóm "chưa chốt") |
| GET | `/api/me/skills` | SPEC CONFIRMED | T07 ☑ | — |
| PATCH | `/api/me/skills` | SPEC CONFIRMED | T06 ☑ | ND-09, ND-11, AUD-12 |

Tất cả: **Implementation = NOT IMPLEMENTED**.

**Hạ tầng dùng chung:** cơ chế của `core/security.py` và `get_current_user` đã chốt (D-AUTH-01 JWT HS256 + Bearer + role từ DB; D-AUTH-02 30 phút; D-AUTH-04 Argon2id). Còn **chờ chọn thư viện** — ND-44 (JWT), ND-45 (Argon2id + tham số) — trước khi viết code; không tự thêm dependency.

**Không thuộc skill này:** `/api/me/courses*`, `/api/me/bookmarks*`, `join` (Course Tracking — kể cả T08 ☑); `/api/me/review-history*` (skill `review-assessment`); `/api/me/learning-paths`; mọi `/api/admin/*`; tạo admin qua API (chỉ có `scripts/create_admin.py`).

File thuộc module: `routers/auth.py`, `routers/me.py`, `schemas/auth.py`, `schemas/user.py`, `models/user.py`, `models/user_skill.py`, `models/password_reset_token.py`, `services/auth_service.py`, `services/user_service.py`, repository tương ứng, `core/security.py`, `core/dependencies.py`, `core/email.py` (dùng chung với `review-assessment`), `tests/test_auth.py`, migration cho 3 bảng.

## 4. Endpoint contract (chỉ phần đã xác nhận)

Chi tiết: `docs/modules/auth-profile.md` §4. Lỗi lấy từ cột "Lỗi thường gặp" của sheet "Endpoint (bản mới)".

| Endpoint | Xác thực | Request | Response đã xác nhận | Lỗi đã xác nhận |
|---|---|---|---|---|
| `POST /auth/register` | Công khai | `email`, `password`, `full_name` | 201 + thông tin người dùng | 409 email tồn tại; 422 |
| `POST /auth/login` | Công khai | `email`, `password` | 200 + access token + refresh token + thông tin người dùng (gồm `role`) — hình dạng: ND-19, ND-41 | 401 |
| `POST /auth/refresh` | Bằng refresh token | Refresh token (ND-41) | Access token mới + refresh token mới (ND-48) | Thất bại khi token hết hạn/thu hồi/đã xoay vòng/không hợp lệ — mã HTTP: ND-48 |
| `POST /auth/logout` | Người dùng (ND-48) | Refresh token cần thu hồi (ND-41, ND-48) | 200 | 401 |
| `POST /auth/forgot-password` | Công khai | `email` | 200 + thông báo chung, luôn giống nhau | 422 |
| `POST /auth/reset-password` | Công khai | `token`, `new_password` | 200 | 400 mã sai/hết hạn/đã dùng |
| `GET /me` | Người dùng | — | `user_id`, `email`, `full_name`, `avatar_url`, `role`, `created_at` | 401 |
| `PATCH /me` | Người dùng | `full_name`, `avatar_url` | 200 hồ sơ mới | 401; 422 |
| `POST /me/avatar` | Người dùng | File ảnh | 200 `avatar_url` | 413; 415 — chờ AUD-06 |
| `POST /me/change-password` | Người dùng | `current_password`, `new_password` | 200 | 400 sai mật khẩu hiện tại |
| `GET /me/summary` | Người dùng | — | `ongoing_courses`, `completed_courses`, `known_skills`, `ongoing_paths` | 401 |
| `GET /me/skills` | Người dùng | `?status=known\|learning` | `{skill_id, skill, status, updated_at}[]` | 401 |
| `PATCH /me/skills` | Người dùng | `add[]`, `update[]`, `remove[]` | 200 danh sách mới | 404 `skill_id` không tồn tại; 422 |

Lỗi validate khác ngoài bảng trên: theo quy ước dự án đã duyệt; không tự đặt mã mới (ND-15).

## 5. Quy tắc bắt buộc (SPEC CONFIRMED)

| Quy tắc | Nguồn |
|---|---|
| `register` luôn tạo `student`; không nhận `role` từ client; admin chỉ tạo bằng `scripts/create_admin.py` | T09, AP-R01, AP-R05 |
| Mỗi email một tài khoản; trùng → 409 | `.docx` 3.1, AP-R02 |
| Không đổi được email; `PATCH /me` chỉ nhận `full_name`, `avatar_url`, không sửa `role` | D06, T04, T09, AP-R03, AP-R04 |
| Không lưu mật khẩu gốc; chỉ lưu bản băm **Argon2id**; không trả `hashed_password` ở bất kỳ response nào | `.docx` 3.1, D-AUTH-04, AP-R06 |
| Access token: JWT **HS256** ký bằng `SECRET_KEY`, claim `sub`/`iat`/`exp`, **30 phút**, header `Authorization: Bearer`; chỉ chấp nhận HS256; vai trò lấy từ **database**, không tin claim | D-AUTH-01, D-AUTH-02, AP-R21 |
| Refresh token: chỉ lưu bản băm trong PostgreSQL; rotation khi làm mới; token đã xoay vòng/thu hồi/hết hạn không dùng được | D-AUTH-03, AP-R22 |
| Logout: thu hồi refresh token tương ứng, client xóa token, server trả 200; **không** khẳng định access token bị thu hồi tức thì | D-AUTH-03, AP-R08 |
| Chính sách mật khẩu (register, reset, change — cùng một hàm kiểm): ≥ 8 ký tự, ≤ 128 byte UTF-8, có `A-Z`, `a-z`, `0-9`, ký tự đặc biệt, không khoảng trắng; kiểm khớp `confirm_password` khi có; không lưu `confirm_password` | D-AUTH-05, AP-R19, AP-R20 |
| Không ghi mật khẩu, `confirm_password`, token gốc vào log | D-AUTH-05, AP-R23 |
| `forgot-password` trả cùng thông báo dù email có tồn tại hay không | T01, AP-R09 |
| Mã đặt lại: ngẫu nhiên, chỉ lưu bản băm, hạn `RESET_TOKEN_EXPIRE_MINUTES`, dùng một lần; đặt lại xong vô hiệu mã cũ chưa dùng | T01, T02, `.docx` 3.4, AP-R10, AP-R11 |
| Đổi mật khẩu phải đúng mật khẩu hiện tại; sai → 400 | T03, `.docx` 3.1, AP-R12 |
| `PATCH /me/skills`: một transaction; `skill_id` không tồn tại → 404 và rollback; `add` trùng = upsert | T06, G3, AP-R14 |
| `UserSkill` còn được module khác ghi (join → `learning`, ôn tập đạt → `known`) | D05, T13, AP-R15 |
| `/api/me*` lấy người dùng từ token, không nhận `user_id` | CONVENTIONS §1, AP-R18 |

## 6. [NEEDS DECISION]

Xác nhận ownership **không** có nghĩa các quyết định dưới đây đã chốt.

| Mã | Trạng thái | Nội dung |
|---|---|---|
ND-01 … ND-05 đã được chốt phần chính thành D-AUTH-01 … D-AUTH-05. Các chi tiết còn mở:

| Mã | Trạng thái | Nội dung |
|---|---|---|
| ND-44 | PENDING — chặn viết `core/security.py` | Thư viện JWT |
| ND-45 | PENDING — chặn viết `core/security.py` | Thư viện Argon2id và tham số |
| ND-43 | **BLOCKED** — chặn model/migration, refresh, logout | Thiết kế bảng RefreshToken (`database-design.md` §3.5 đang PROPOSED) |
| ND-40 | PENDING | Thời hạn refresh token (đề xuất 7 ngày — chưa chốt) |
| ND-41 | PENDING | Định dạng, cách gửi, nơi lưu refresh token; ý nghĩa "Ghi nhớ đăng nhập" khi dùng `sessionStorage` |
| ND-42 | PENDING | Xử lý khi phát hiện tái sử dụng refresh token |
| ND-48 | PENDING | Hợp đồng refresh/logout, mã lỗi khi làm mới thất bại |
| ND-46 | PENDING | Tập ký tự đặc biệt; định nghĩa khoảng trắng; ký tự non-ASCII |
| ND-47 | PENDING | Endpoint nào nhận `confirm_password` |
| ND-36 | PENDING | Thu hồi refresh token khi đổi/đặt lại mật khẩu |
| ND-08, ND-19 | PENDING | Response của register / login |
| ND-14, ND-15, ND-16 | PENDING | `error.code`; 400 hay 422; lớp commit transaction |
| AUD-06, ND-12 | PENDING | Upload avatar trong v1; giới hạn file |
| AUD-07 | PENDING | Kiểm tra định dạng email chưa có nguồn — không coi là rule đã chốt |
| AUD-12 | PENDING | `status` có bắt buộc trong phần tử `add` không |
| ND-06, 07, 09, 10, 11, 13, 17, 18, 36, 37, 38, 39 | PENDING | Xem `docs/decisions.md` §4.1, §4.3 |

## 7. Không được làm

- Không tự chọn phương án cho mục BLOCKED/PENDING/CONFLICT; không đặt giá trị mặc định thay nhóm.
- Không thêm endpoint, bảng, cột, ràng buộc ngoài `docs/`; không thêm cơ chế xác thực mới (OAuth, session server, blacklist token…).
- Không sửa `docs/decisions.md` hay Excel để biến ☐ thành ☑.
- Không mở rộng phạm vi sang Course Tracking, Feedback, Learning Path, Admin Questions.
- Không đổi hành vi `get_current_user`/`require_admin` mà không hỏi — mọi module dùng chung.

## 8. Quy trình implement

1. Xác định endpoint/quy tắc trong `auth-profile.md`; đối chiếu trạng thái §3, §6 ở skill này. BLOCKED/CONFLICT trên đường đi → hỏi Tuấn.
2. Model + migration khớp `database-design.md` (bảng thật `users`).
3. Schema: request chỉ chứa trường được phép; response không chứa trường nhạy cảm.
4. Repository → Service (quy tắc + transaction) → Router (`get_current_user`, lỗi theo `backend-rules.md` §4).
5. Test theo `auth-profile.tests.md`; bỏ qua kịch bản có cột "Chờ".
6. Chạy `pytest`, `black`, `ruff`. Chỉ khi code chạy và test qua mới coi là IMPLEMENTED.

## 9. Kỳ vọng kiểm thử

Kịch bản đã đặc tả và không phụ thuộc mục chưa chốt: AP-T01, T03, T05, T11, T12, T14, T20–T28, T32, T35–T37, T40–T47, T50, T51, T54–T57, T70, T71, T73–T78, T81, T90, T91, T101–T103, T105–T107, T112, T113. (Các ca refresh/logout cần bảng RefreshToken — chờ ND-43 trước khi viết.)

Phụ thuộc ND: AP-T06 (ND-45), T30, T31 (ND-48), T33 (ND-42), T34 (ND-40), T38 (ND-16), T100, T104, T108, T109 (ND-46), T110, T111 (ND-47), AP-T07 và mã lỗi chính sách mật khẩu (ND-15).

Kiểm được phần đã chốt, phần còn lại chờ: AP-T02, T52, T53 (role/email không đổi — mã phản hồi chờ ND-18); AP-T10 (có token + `role` — hình dạng chờ ND-19); AP-T04 (thiếu trường — phần "sai định dạng email" chờ AUD-07); AP-T48 (kỳ vọng rollback đã chốt — chỉ cơ chế commit chờ ND-16). AP-T13 chờ ND-15.

**TEST COVERAGE GAP** (chưa có kịch bản trong tài liệu — chưa tự thêm):

- AP-R16: upload avatar thành công (khi AUD-06 được chốt).
- `GET /api/me/summary` không có token → 401.
