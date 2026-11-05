# Review-Auth — Kế hoạch code module Tài khoản & Hồ sơ (F01)

> Người thực hiện: **Tuấn** · Người review: **Claude** · Bắt đầu: **05/11/2026** · Dự kiến xong: **02/12/2026**
> Module tiếp theo: Ôn tập & Đánh giá — `docs/Review-Assessment.md` (03/12 → 22/12).
> Căn cứ: `EdumentorAi_BA_v3.md` (FR-01 → FR-04, FR-40 → FR-48, NFR-04 → NFR-08, bảng API mục 10), giao diện demo `docs/EduMentor-UI-design/ui-design/`.
> Cách dùng: làm xong việc nào thì tích `[x]` và điền **ngày thực tế**. Mỗi giai đoạn xong thì nhờ Claude review trước khi sang giai đoạn sau.

---

## Tổng quan tiến độ

| GĐ | Nội dung | Dự kiến | Thực tế bắt đầu | Thực tế xong | Xong |
|---|---|---|---|---|---|
| 0 | Chuẩn bị môi trường | 05/11 → 06/11 | 05/11 | 05/11 | [x] |
| 1 | Model User + nền bảo mật (`core/`) | 07/11 → 10/11 | 05/11 | 05/11 | [x] |
| 2 | Đăng ký, đăng nhập | 11/11 → 13/11 | __/__ | __/__ | [ ] |
| 3 | Hồ sơ `/me`, đổi mật khẩu | 14/11 → 17/11 | __/__ | __/__ | [ ] |
| 4 | Kỹ năng `/me/skills` | 18/11 → 20/11 | __/__ | __/__ | [ ] |
| 5 | Quên / đặt lại mật khẩu | 21/11 → 24/11 | __/__ | __/__ | [ ] |
| 6 | Refresh token, đăng xuất | 25/11 → 27/11 | __/__ | __/__ | [ ] |
| 7 | Ảnh đại diện, thống kê `/me/summary` | 28/11 → 30/11 | __/__ | __/__ | [ ] |
| 8 | Hoàn thiện, kiểm thử, gộp nhánh | 01/12 → 02/12 | __/__ | __/__ | [ ] |

Thứ tự được chọn để mỗi giai đoạn chạy và test được ngay; phần phụ thuộc module người khác (kỹ năng, thống kê) đặt sau.

---

## Giai đoạn 0 — Chuẩn bị môi trường (05/11 → 06/11)

- [x] **0.1 Chạy được server rỗng** — dự kiến 05/11 → 05/11 · thực tế 05/11 → 05/11
  - Bật Docker Desktop → `docker compose up -d` → `uvicorn app.main:app --reload`.
  - ✅ Xong khi: `GET /api/health/health` trả `"database": "connected"`.
- [x] **0.2 Commit khung cấu trúc trên nhánh `tuan/future-auth`** — dự kiến 05/11 → 05/11 · thực tế 05/11 → 05/11 (commit `580772c`, đã push)
  - Gồm: xóa tài liệu cũ, file khung mới, `CLAUDE.md` mới, ngắt seed của Hòa.
- [x] **0.3 Đọc BA** FR-01 → FR-04, FR-40 → FR-48, bảng API mục 10 (dòng ~1291–1303) — dự kiến 06/11 → 06/11 · thực tế 05/11 → 05/11
  - Ghi câu hỏi chưa rõ vào mục **Câu hỏi cần chốt** cuối file.
- [x] **0.4 Xem màn demo**: Register, Login (Main), ForgotPassword, ForgotSent, ResetPassword, ResetExpired, Profile, EditProfile, ChangePassword, Skills, Logout — dự kiến 06/11 → 06/11 · thực tế 05/11 → 05/11
  - Ghi lại: form có những trường gì, thông báo lỗi nào → đó là request/response cần làm.

## Giai đoạn 1 — Model User + nền bảo mật (07/11 → 10/11)

- [x] **1.1 `models/user.py`** — dự kiến 07/11 → 07/11 · thực tế 05/11 → 05/11 ✔ Claude đã review
  - Cột: `user_id`, `email` (unique), `hashed_password`, `full_name`, `avatar_url` (nullable), `role` (`student`/`admin`, mặc định `student`), `is_active`, `created_at`.
  - Thực tế: thêm `updated_at`; `full_name` tối đa 100 ký tự (schema GĐ2 phải khớp `max_length=100`); có `CheckConstraint ck_users_role`.
  - Import trong `models/__init__.py`.
  - ✅ Xong khi: pgAdmin thấy bảng `users`.
- [x] **1.2 `core/config.py`** thêm `SECRET_KEY` (đang bị comment), kiểm tra `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALGORITHM` — dự kiến 08/11 → 08/11 · thực tế 05/11 → 05/11 ✔ Claude đã review
- [x] **1.3 `core/security.py`** — dự kiến 08/11 → 09/11 · thực tế 05/11 → 05/11 ✔ Claude đã review
  - `hash_password`, `verify_password` (bcrypt — chú ý giới hạn 72 byte).
  - `create_access_token(user_id)`, `decode_access_token(token)` (pyjwt; `sub` là chuỗi; có `exp`).
  - `validate_password(password)` — một hàm dùng chung cho đăng ký, đặt lại, đổi mật khẩu (FR-48).
  - [x] Phần 1 — mật khẩu (`hash_password`, `verify_password`, `validate_password`): xong 05/11 ✔ Claude đã review
  - [x] Phần 2 — JWT (`create_access_token`, `decode_access_token`): xong 05/11 ✔ Claude đã review
  - ✅ Xong khi: thử trong Python shell băm → kiểm tra đúng/sai; tạo token → giải mã ra đúng `user_id`; token hết hạn bị từ chối.
- [x] **1.4 `core/dependencies.py`** — dự kiến 10/11 → 10/11 · thực tế 05/11 → 05/11 ✔ Claude đã review
  - `get_current_user`: đọc `Authorization: Bearer`, giải mã, **lấy user từ DB** (vai trò lấy từ DB), user không tồn tại/bị khóa → 401.
  - `require_admin`: role khác `admin` → 403.
- [x] **1.5 Nhờ Claude review GĐ1** — dự kiến 10/11 · thực tế 05/11 — GĐ1 đạt: T2–T6 qua hết

## Giai đoạn 2 — Đăng ký, đăng nhập (11/11 → 13/11)

- [ ] **2.1 `schemas/auth.py`, `schemas/user.py`** — dự kiến 11/11 → 11/11 · thực tế __/__ → __/__
  - `RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserResponse`.
  - Response **không** có `hashed_password`.
- [ ] **2.2 `repositories/user_repository.py`** — `get_by_email`, `get_by_id`, `create` — dự kiến 11/11 → 11/11 · thực tế __/__ → __/__
- [ ] **2.3 `services/auth_service.py`**: `register`, `login` — dự kiến 12/11 → 12/11 · thực tế __/__ → __/__
  - Đăng ký luôn tạo `student`, không nhận `role` từ client; email trùng → lỗi.
- [ ] **2.4 `endpoints/auth.py`** + gắn vào `api.py` (prefix `/auth`) — dự kiến 12/11 → 13/11 · thực tế __/__ → __/__
  - `POST /api/auth/register` → 201; email trùng → 409.
  - `POST /api/auth/login` → access token + thông tin user; sai → 401.
- [ ] **2.5 `tests/test_auth.py`** — đăng ký OK, email trùng, mật khẩu yếu, đăng nhập đúng/sai — dự kiến 13/11 · thực tế __/__
- [ ] **2.6 Thử trên Swagger** `/api/docs`: đăng ký → đăng nhập → bấm **Authorize** — dự kiến 13/11 · thực tế __/__
- [ ] **2.7 Nhờ Claude review GĐ2** — dự kiến 13/11 · thực tế __/__

## Giai đoạn 3 — Hồ sơ và đổi mật khẩu (14/11 → 17/11)

- [ ] **3.1 `GET /api/me`** — trả họ tên, email, vai trò, ngày tham gia, ảnh đại diện (FR-03) — dự kiến 14/11 · thực tế bắt đầu 05/11 (đã có `schemas/user.py` `UserMe` + `endpoints/me.py`, test tạm qua 200/401; chưa gắn vào `api.py`)
- [ ] **3.2 `PATCH /api/me`** — chỉ sửa `full_name`; email và role **không** đổi được — dự kiến 14/11 → 15/11 · thực tế __/__ → __/__
- [ ] **3.3 `POST /api/me/change-password`** — mật khẩu hiện tại, mới, xác nhận; sai mật khẩu hiện tại → lỗi; áp `validate_password` (FR-48) — dự kiến 16/11 → 16/11 · thực tế __/__ → __/__
- [ ] **3.4 `services/user_service.py`, `endpoints/me.py`** (prefix `/me`) — dự kiến 14/11 → 16/11 · thực tế __/__ → __/__
- [ ] **3.5 `tests/test_me.py`** — không token → 401; sửa họ tên; thử gửi `email`/`role` không có tác dụng; đổi mật khẩu đúng/sai — dự kiến 17/11 · thực tế __/__
- [ ] **3.6 Nhờ Claude review GĐ3** — dự kiến 17/11 · thực tế __/__

## Giai đoạn 4 — Kỹ năng của tôi (18/11 → 20/11)

> ⚠️ Phụ thuộc bảng `skills` (module của Hòa/Khôi, đang ngắt). Trước khi làm: thống nhất với nhóm dùng model `Skills` nào.

- [ ] **4.0 Chốt với nhóm về bảng `skills`** — dự kiến 18/11 · thực tế __/__
- [ ] **4.1 `models/user_skill.py`** — `user_id`, `skill_id`, `status` (`known`/`learning`), `updated_at`; một user–skill chỉ một dòng — dự kiến 18/11 · thực tế __/__
- [ ] **4.2 `GET /api/me/skills`** (lọc `?status=`) — dự kiến 19/11 · thực tế __/__
- [ ] **4.3 `PATCH /api/me/skills`** — thêm / đổi trạng thái / xóa, **lưu tất cả một lần** (FR-04); skill không có trong danh mục → lỗi và không lưu gì — dự kiến 19/11 → 20/11 · thực tế __/__ → __/__
- [ ] **4.4 Test + nhờ Claude review GĐ4** — dự kiến 20/11 · thực tế __/__

## Giai đoạn 5 — Quên / đặt lại mật khẩu (21/11 → 24/11)

- [ ] **5.1 Model `PasswordResetToken`** trong `models/auth_token.py` — lưu **bản băm** token, hạn dùng, đã dùng chưa — dự kiến 21/11 · thực tế __/__
- [ ] **5.2 `core/email.py`** — gửi email (lúc dev có thể in link ra console) — dự kiến 22/11 · thực tế __/__
- [ ] **5.3 `POST /api/auth/forgot-password`** — **luôn** trả cùng thông báo dù email có hay không (FR-47) — dự kiến 23/11 · thực tế __/__
- [ ] **5.4 `POST /api/auth/reset-password`** — token đúng, còn hạn, chưa dùng; dùng xong vô hiệu; áp `validate_password` — dự kiến 23/11 → 24/11 · thực tế __/__ → __/__
- [ ] **5.5 Test + nhờ Claude review GĐ5** — dự kiến 24/11 · thực tế __/__

## Giai đoạn 6 — Refresh token, đăng xuất (25/11 → 27/11)

- [ ] **6.1 Model `RefreshToken`** trong `models/auth_token.py` — bản băm token, `user_id`, hạn, `revoked` — dự kiến 25/11 · thực tế __/__
- [ ] **6.2 `repositories/token_repository.py`** — dự kiến 25/11 · thực tế __/__
- [ ] **6.3 Login trả thêm refresh token** — dự kiến 26/11 · thực tế __/__
- [ ] **6.4 `POST /api/auth/refresh`** — token hợp lệ → cấp access token mới (+ xoay vòng nếu nhóm chọn); hết hạn/thu hồi → 401 (FR-45, FR-46) — dự kiến 26/11 · thực tế __/__
- [ ] **6.5 `POST /api/auth/logout`** — thu hồi refresh token — dự kiến 27/11 · thực tế __/__
- [ ] **6.6 Test + nhờ Claude review GĐ6** — dự kiến 27/11 · thực tế __/__

## Giai đoạn 7 — Ảnh đại diện, thống kê (28/11 → 30/11)

- [ ] **7.1 `POST /api/me/avatar`** + `utils/files.py` — kiểm tra loại file, dung lượng; lưu file, cập nhật `avatar_url` — dự kiến 28/11 → 29/11 · thực tế __/__ → __/__
- [ ] **7.2 `GET /api/me/summary`** — khóa đang học, đã hoàn thành, kỹ năng đã biết, lộ trình đang theo — dự kiến 30/11 · thực tế __/__
  - ⚠️ Cần bảng của module khác (khóa học của tôi, lộ trình). Nếu chưa có: trả `known_skills` thật, các số còn lại chờ gộp.
- [ ] **7.3 Test + nhờ Claude review GĐ7** — dự kiến 30/11 · thực tế __/__

## Giai đoạn 8 — Hoàn thiện (01/12 → 02/12)

- [ ] **8.1 `scripts/create_admin.py`** — tạo tài khoản admin (không tạo qua API) — dự kiến 01/12 · thực tế __/__
- [ ] **8.2 Chạy toàn bộ** `pytest`, `black .`, `ruff check .` — dự kiến 01/12 · thực tế __/__
- [ ] **8.3 Rà bảo mật**: không trả `hashed_password`/token gốc, không log mật khẩu, `.env` không bị commit (NFR-04, NFR-08) — dự kiến 01/12 · thực tế __/__
- [ ] **8.4 Bật lại phần của Hòa, gộp với nhóm**, tạo Pull Request — dự kiến 02/12 · thực tế __/__

---

## Checklist 13 endpoint

| Method | Endpoint | GĐ | Code | Test | Review |
|---|---|---|---|---|---|
| POST | `/api/auth/register` | 2 | [ ] | [ ] | [ ] |
| POST | `/api/auth/login` | 2 | [ ] | [ ] | [ ] |
| POST | `/api/auth/refresh` | 6 | [ ] | [ ] | [ ] |
| POST | `/api/auth/logout` | 6 | [ ] | [ ] | [ ] |
| POST | `/api/auth/forgot-password` | 5 | [ ] | [ ] | [ ] |
| POST | `/api/auth/reset-password` | 5 | [ ] | [ ] | [ ] |
| GET | `/api/me` | 3 | [ ] | [ ] | [ ] |
| PATCH | `/api/me` | 3 | [ ] | [ ] | [ ] |
| POST | `/api/me/avatar` | 7 | [ ] | [ ] | [ ] |
| POST | `/api/me/change-password` | 3 | [ ] | [ ] | [ ] |
| GET | `/api/me/summary` | 7 | [ ] | [ ] | [ ] |
| GET | `/api/me/skills` | 4 | [ ] | [ ] | [ ] |
| PATCH | `/api/me/skills` | 4 | [ ] | [ ] | [ ] |

## Câu hỏi cần chốt (BA chưa nói rõ)

Điền câu trả lời khi nhóm chốt; chưa chốt thì làm phần không phụ thuộc trước.

| # | Câu hỏi | Cần trước GĐ | Trả lời | Ngày chốt |
|---|---|---|---|---|
| Q1 | Quy tắc mật khẩu cụ thể (độ dài, chữ hoa/thường/số/ký tự đặc biệt)? | 1 | Theo màn demo ChangePassword/ResetPassword: ≥ 8 ký tự, có chữ hoa, chữ thường, chữ số, ký tự đặc biệt; thêm ≤ 72 byte (giới hạn bcrypt). Còn mở: có cho dấu cách / chữ có dấu không? | 05/11 |
| Q2 | Access token sống bao lâu? (`.env` đang để 30 phút) | 1 | | |
| Q3 | Đăng ký có trường `confirm_password` không? | 2 | | |
| Q4 | Login trả về những gì (token + user)? | 2 | | |
| Q5 | Dùng model `Skills` nào khi gộp với nhóm? | 4 | | |
| Q6 | Link đặt lại mật khẩu sống bao lâu? Gửi email bằng SMTP nào? | 5 | | |
| Q7 | Refresh token sống bao lâu, có xoay vòng không, gửi qua body hay cookie? | 6 | | |
| Q8 | Ảnh đại diện: định dạng, dung lượng tối đa, lưu ở đâu? | 7 | | |
| Q9 | `/me/summary` đếm "đang học", "lộ trình đang theo" từ bảng nào? | 7 | | |

## Nhật ký

| Ngày | Đã làm | Vướng mắc |
|---|---|---|
| 05/11 | Cài môi trường, chuẩn hóa cấu trúc, viết lại `CLAUDE.md`, ngắt seed của Hòa, lập kế hoạch này | Docker Desktop tắt → server chưa chạy lại |
| 05/11 | Xong GĐ0; viết model `Users` (1.1), bật `SECRET_KEY` (1.2); bảng `users` đã tạo trong DB | Lỡ viết model vào `skill.py` của Hòa → đã chuyển sang `user.py` và `git restore` lại `skill.py` |
| | | |
