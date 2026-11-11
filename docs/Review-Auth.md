# Review-Auth — Kế hoạch code module Tài khoản & Hồ sơ (F01)

> Người thực hiện: **Tuấn** · Người review: **Claude** · Bắt đầu: **05/11/2026** · Dự kiến xong: **15/11/2026**
> Module tiếp theo: Ôn tập & Đánh giá — `docs/Review-Assessment.md` (16/11 → 25/11).
> **Tổng thời gian 2 module (01 + 09): 05/11 → 25/11/2026.**
> Căn cứ: `EdumentorAi_BA_v3.md` (FR-01 → FR-04, FR-40 → FR-48, NFR-04 → NFR-08, bảng API mục 10), giao diện demo `docs/EduMentor-UI-design/ui-design/`.
> Cách dùng: làm xong việc nào thì tích `[x]` và điền **ngày thực tế**. Mỗi giai đoạn xong thì nhờ Claude review trước khi sang giai đoạn sau.

---

## Tổng quan tiến độ

| GĐ | Nội dung | Dự kiến | Thực tế bắt đầu | Thực tế xong | Xong |
|---|---|---|---|---|---|
| 0 | Chuẩn bị môi trường | 05/11 → 05/11 | 05/11 | 05/11 | [x] |
| 1 | Model User + nền bảo mật (`core/`) | 05/11 → 05/11 | 05/11 | 05/11 | [x] |
| 2 | Đăng ký, đăng nhập | 05/11 → 05/11 | 05/11 | 05/11 | [x] |
| 3 | Hồ sơ `/me`, đổi mật khẩu | 06/11 → 07/11 | 06/11 | 06/11 | [x] |
| 4 | Kỹ năng `/me/skills` | 08/11 → 09/11 | __/__ | __/__ | [ ] |
| 5 | Quên / đặt lại mật khẩu | 10/11 → 11/11 | 06/11 | 06/11 | [x] |
| 6 | Refresh token, đăng xuất | 12/11 → 13/11 | 07/11 | 07/11 | [x] |
| 7 | Ảnh đại diện, thống kê `/me/summary` | 14/11 → 14/11 | 07/11 | __/__ | [ ] |
| 8 | Hoàn thiện, kiểm thử, gộp nhánh | 15/11 → 15/11 | 07/11 | __/__ | [ ] |

Thứ tự được chọn để mỗi giai đoạn chạy và test được ngay; phần phụ thuộc module người khác (kỹ năng, thống kê) đặt sau.

---

## Giai đoạn 0 — Chuẩn bị môi trường (05/11)

- [x] **0.1 Chạy được server rỗng** — dự kiến 05/11 · thực tế 05/11 → 05/11
  - Bật Docker Desktop → `docker compose up -d` → `uvicorn app.main:app --reload`.
  - ✅ Xong khi: `GET /api/health/health` trả `"database": "connected"`.
- [x] **0.2 Commit khung cấu trúc trên nhánh `tuan/future-auth`** — dự kiến 05/11 · thực tế 05/11 → 05/11 (commit `580772c`, đã push)
  - Gồm: xóa tài liệu cũ, file khung mới, `CLAUDE.md` mới, ngắt seed của Hòa.
- [x] **0.3 Đọc BA** FR-01 → FR-04, FR-40 → FR-48, bảng API mục 10 (dòng ~1291–1303) — dự kiến 05/11 · thực tế 05/11 → 05/11
  - Ghi câu hỏi chưa rõ vào mục **Câu hỏi cần chốt** cuối file.
- [x] **0.4 Xem màn demo**: Register, Login (Main), ForgotPassword, ForgotSent, ResetPassword, ResetExpired, Profile, EditProfile, ChangePassword, Skills, Logout — dự kiến 05/11 · thực tế 05/11 → 05/11
  - Ghi lại: form có những trường gì, thông báo lỗi nào → đó là request/response cần làm.

## Giai đoạn 1 — Model User + nền bảo mật (05/11)

- [x] **1.1 `models/user.py`** — dự kiến 05/11 · thực tế 05/11 → 05/11 ✔ Claude đã review
  - Cột: `user_id`, `email` (unique), `hashed_password`, `full_name`, `avatar_url` (nullable), `role` (`student`/`admin`, mặc định `student`), `is_active`, `created_at`.
  - Thực tế: thêm `updated_at`; `full_name` tối đa 100 ký tự (schema GĐ2 phải khớp `max_length=100`); có `CheckConstraint ck_users_role`.
  - Import trong `models/__init__.py`.
  - ✅ Xong khi: pgAdmin thấy bảng `users`.
- [x] **1.2 `core/config.py`** thêm `SECRET_KEY` (đang bị comment), kiểm tra `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALGORITHM` — dự kiến 05/11 · thực tế 05/11 → 05/11 ✔ Claude đã review
- [x] **1.3 `core/security.py`** — dự kiến 05/11 · thực tế 05/11 → 05/11 ✔ Claude đã review
  - `hash_password`, `verify_password` (bcrypt — chú ý giới hạn 72 byte).
  - `create_access_token(user_id)`, `decode_access_token(token)` (pyjwt; `sub` là chuỗi; có `exp`).
  - `validate_password(password)` — một hàm dùng chung cho đăng ký, đặt lại, đổi mật khẩu (FR-48).
  - [x] Phần 1 — mật khẩu (`hash_password`, `verify_password`, `validate_password`): xong 05/11 ✔ Claude đã review
  - [x] Phần 2 — JWT (`create_access_token`, `decode_access_token`): xong 05/11 ✔ Claude đã review
  - ✅ Xong khi: thử trong Python shell băm → kiểm tra đúng/sai; tạo token → giải mã ra đúng `user_id`; token hết hạn bị từ chối.
- [x] **1.4 `core/dependencies.py`** — dự kiến 05/11 · thực tế 05/11 → 05/11 ✔ Claude đã review
  - `get_current_user`: đọc `Authorization: Bearer`, giải mã, **lấy user từ DB** (vai trò lấy từ DB), user không tồn tại/bị khóa → 401.
  - `require_admin`: role khác `admin` → 403.
- [x] **1.5 Nhờ Claude review GĐ1** — dự kiến 05/11 · thực tế 05/11 — GĐ1 đạt: T2–T6 qua hết

## Giai đoạn 2 — Đăng ký, đăng nhập (05/11)

- [x] **2.1 `schemas/auth.py`, `schemas/user.py`** — dự kiến 05/11 · thực tế 05/11 → 05/11 ✔ Claude đã review
  - `RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserResponse`.
  - Response **không** có `hashed_password`.
- [x] **2.2 `repositories/user_repository.py`** — `get_by_email`, `get_by_id`, `create` — dự kiến 05/11 · thực tế 05/11 → 05/11 ✔ Claude đã review
- [x] **2.3 `services/auth_service.py`**: `register`, `login` — dự kiến 05/11 · thực tế 05/11 → 05/11 ✔ Claude đã review (có bắt IntegrityError khi 2 người đăng ký cùng lúc)
  - Đăng ký luôn tạo `student`, không nhận `role` từ client; email trùng → lỗi.
- [x] **2.4 `endpoints/auth.py`** + gắn vào `api.py` (prefix `/auth`) — dự kiến 05/11 · thực tế 05/11 → 05/11 ✔ Claude đã review (đã sửa lỗi gắn `me` 2 lần)
  - `POST /api/auth/register` → 201; email trùng → 409.
  - `POST /api/auth/login` → access token + thông tin user; sai → 401.
- [x] **2.5 `tests/test_auth.py`** — đăng ký OK, email trùng, mật khẩu yếu, đăng nhập đúng/sai — dự kiến 05/11 · thực tế 05/11 — 13 test PASSED (`pytest tests/test_auth.py -v`) ✔ Claude đã review
- [x] **2.6 Thử trên Swagger** `/api/docs`: đăng ký → đăng nhập → bấm **Authorize** — dự kiến 05/11 · thực tế 05/11 — S1–S8 qua (201/409/409/422/401/200/200/băm)
- [x] **2.7 Nhờ Claude review GĐ2** — dự kiến 05/11 · thực tế 05/11 — GĐ2 đạt

## Giai đoạn 3 — Hồ sơ và đổi mật khẩu (06/11 → 07/11)

- [x] **3.1 `GET /api/me`** — trả họ tên, email, vai trò, ngày tham gia, ảnh đại diện (FR-03) — dự kiến 06/11 · thực tế 05/11 → 06/11 ✔ Claude đã review (đã gắn vào `api.py`, có test trong `test_auth.py`)
- [x] **3.2 `PATCH /api/me`** — chỉ sửa `full_name`; email và role **không** đổi được — dự kiến 06/11 · thực tế 06/11 → 06/11 ✔ Claude đã review (Claude sửa: thiếu `UpdateMeRequest`, thiếu import) — P1–P4 qua
- [x] **3.3 `POST /api/me/change-password`** — mật khẩu hiện tại, mới, xác nhận; sai mật khẩu hiện tại → lỗi; áp `validate_password` (FR-48) — dự kiến 07/11 · thực tế 06/11 → 06/11 ✔ Claude đã review (Claude sửa: thiếu hàm service, thiếu `MessageResponse`) — C1–C6 qua; 08/11 thêm: mật khẩu mới trùng mật khẩu cũ → 400 "Mật khẩu này đã được sử dụng." (Claude viết theo yêu cầu, +2 test)
- [x] **3.4 `services/user_service.py`, `endpoints/me.py`** (prefix `/me`) — dự kiến 06/11 → 07/11 · thực tế 06/11 → 06/11 ✔ Claude đã review (Claude sửa: code router bị dán nhầm vào service)
- [x] **3.5 `tests/test_me.py`** — không token → 401; sửa họ tên; thử gửi `email`/`role` không có tác dụng; đổi mật khẩu đúng/sai — dự kiến 07/11 · thực tế 06/11 — 13 test PASSED (Tuấn tự viết, thêm helper `login`); tổng `test_auth` + `test_me` = 26 passed ✔ Claude đã review
- [x] **3.6 Nhờ Claude review GĐ3** — dự kiến 07/11 · thực tế 06/11 — GĐ3 đạt

## Giai đoạn 4 — Kỹ năng của tôi (08/11 → 09/11)

> ⚠️ Phụ thuộc bảng `skills` (module của Hòa/Khôi, đang ngắt). Trước khi làm: thống nhất với nhóm dùng model `Skills` nào.

- [x] **4.0 Chốt với nhóm về bảng `skills`** — dự kiến 08/11 · thực tế 07/11 — dùng model `Skills` của Hòa; seed từ `datajson/` (5.893 kỹ năng, 4.509 khóa học)
- [x] **Chốt S1–S5 (08/11, Tuấn đồng ý đề xuất):** S1 body PATCH `{"add":[{skill_id,status}],"update":[{skill_id,status}],"remove":[skill_id]}` · S2 `add` kỹ năng đã có → 409 · S3 `update`/`remove` kỹ năng chưa có → 404 · S4 kỹ năng không tồn tại / `is_active=False` → 422 · S5 thêm cột `source` (`manual`/`course`/`review`). Mọi lỗi → không lưu gì (rollback cả request)
- [x] **4.1 `models/user_skill.py`** — `user_id`, `skill_id`, `status` (`known`/`learning`), `updated_at`; một user–skill chỉ một dòng — dự kiến 08/11 · thực tế 08/11 — Claude viết (theo yêu cầu): bảng `user_skills`, khóa chính kép (user_id, skill_id), `source` mặc định `manual`, CHECK status/source, FK → users / skills ON DELETE CASCADE, index skill_id; đã thêm vào `models/__init__.py`. Kiểm tra trên PostgreSQL thật (trong transaction rồi rollback): trùng user–skill → lỗi khóa chính, status/source lạ → lỗi CHECK, skill không tồn tại → lỗi FK; 74 test cũ vẫn passed
- [x] **4.2 `GET /api/me/skills`** (lọc `?status=`) — dự kiến 08/11 · thực tế 08/11 — Claude viết (theo yêu cầu): `schemas/user_skill.py` (SkillStatus, UserSkillOut kèm tên kỹ năng + `source`), `repositories/user_skill_repository.py` (join bảng `skills` của Hòa, sắp theo tên), `services/user_skill_service.py`, route trong `endpoints/me.py` (tham số `status_filter` alias `?status=` — tránh che module `status`); `tests/test_me_skills.py` 6 test (401, rỗng, tên + sắp xếp + source mặc định, lọc, 422, chỉ thấy của mình). Demo backend thật: 401 / [] / 3 kỹ năng thật / lọc known–learning / 422 — dọn sạch dữ liệu thử
- [x] **S6 — thầy chốt (08/11):** người dùng được thay đổi MỌI kỹ năng trong hồ sơ của mình (thêm / đổi trạng thái / gỡ), kể cả kỹ năng đạt qua bài ôn tập; **admin không sửa dữ liệu người dùng**. Người dùng tự đổi trạng thái → `source` chuyển `manual`
- [x] **S7, S8 — Tuấn chốt (08/11):** S7 **bỏ khóa học** → tự gỡ kỹ năng "Đang học" có từ khóa đó (`source='course'`), trừ kỹ năng khóa đang học khác cũng dạy; học lại → tham gia lại → tự thêm lại. S8 **hoàn thành khóa** (chưa ôn tập) → kỹ năng thành "Đã biết". ⚠️ Theo `api-endpoints.md` (dòng 79, 100–101) khóa chỉ `completed` khi **làm đạt ôn tập** → S8 chỉ có tác dụng nếu module 04 (Hòa) cho người dùng tự đánh dấu hoàn thành — **cần nhóm chốt**
- [x] **Hàm cho module khác gọi** (`services/user_skill_service.py`, không commit — chạy trong transaction của module gọi; 5 test): `add_learning_from_course(db, user_id, skill_ids)` (D05 — Hòa gọi khi tham gia khóa), `remove_learning_from_course(db, user_id, skill_ids, keep_skill_ids=...)` (S7 — Hòa gọi khi bỏ khóa), `mark_known(db, user_id, skill_ids, source='course'|'review')` (S8 / T13 — module 09 của Tuấn gọi khi đạt ôn tập)
- [x] **4.3 `PATCH /api/me/skills`** — thêm / đổi trạng thái / xóa, **lưu tất cả một lần** (FR-04); skill không có trong danh mục → lỗi và không lưu gì — dự kiến 09/11 · thực tế 08/11 — Claude viết (theo yêu cầu): `UpdateSkillsRequest` (add / update / remove; chặn rỗng, trùng id, status sai, > 200 thay đổi → 422), service kiểm tra hết rồi mới ghi + commit một lần (S4 → 422, S2 → 409, S3 → 404; tranh chấp 2 tab → IntegrityError → 409), trả danh sách sau khi lưu. Demo backend thật 9 bước: thêm, lưu gộp 3 loại thay đổi, đổi kỹ năng nguồn `review`, 409 / 404 / 422, 2 đúng + 1 sai → hồ sơ y nguyên; dọn sạch dữ liệu thử
- [ ] **4.4 Test + nhờ Claude review GĐ4** — dự kiến 09/11 · thực tế 08/11 (test) — `tests/test_me_skills.py` 23 test (6 GET + 17 PATCH, gồm "có 1 lỗi → không lưu gì" 3 kiểu, không sửa được hồ sơ người khác); tổng backend 97 passed. **Còn: Tuấn đọc lại code GĐ4 + tự thử trên Swagger `/api/docs`**

## Giai đoạn 5 — Quên / đặt lại mật khẩu (10/11 → 11/11)

- [x] **5.1 Model `PasswordResetToken`** trong `models/auth_token.py` — lưu **bản băm** token, hạn dùng, đã dùng chưa — dự kiến 10/11 · thực tế 06/11 ✔ Claude đã review (+ `generate_token`, `hash_token` SHA-256 trong security.py; bảng có FK → users ON DELETE CASCADE)
- [x] **5.2 `core/email.py`** — gửi email (lúc dev có thể in link ra console) — dự kiến 10/11 · thực tế 06/11 ✔ Claude đã review (dev: SMTP_HOST chứa example.com → in link ra terminal; biến .env khai báo trong config.py)
- [x] **5.3 `POST /api/auth/forgot-password`** — **luôn** trả cùng thông báo dù email có hay không (FR-47) — dự kiến 11/11 · thực tế 06/11 ✔ Claude đã review (gửi email bằng BackgroundTasks — không dò được email qua thời gian phản hồi)
- [x] **5.4 `POST /api/auth/reset-password`** — token đúng, còn hạn, chưa dùng; dùng xong vô hiệu; áp `validate_password` — dự kiến 11/11 · thực tế 06/11 → 06/11 ✔ Claude đã review (Claude sửa: thiếu hàm `invalidate_unused_reset_tokens` gây 500)
- [x] **5.5 Test + nhờ Claude review GĐ5** — dự kiến 11/11 · thực tế 06/11 — `tests/test_password_reset.py` 10 test (Claude viết); tổng 36 passed; F1–F8 qua trên PostgreSQL thật

## Giai đoạn 6 — Refresh token, đăng xuất (12/11 → 13/11)

- [x] **6.1 Model `RefreshToken`** trong `models/auth_token.py` — bản băm token, `user_id`, hạn, `revoked` — dự kiến 12/11 · thực tế 07/11 ✔ Claude đã review
- [x] **6.2 `repositories/token_repository.py`** — dự kiến 12/11 · thực tế 07/11 ✔ Claude đã review (+ `revoke_all_refresh_tokens`)
- [x] **6.3 Login trả thêm refresh token** — dự kiến 12/11 · thực tế 07/11 ✔ Claude đã review (login giờ commit vì ghi refresh token vào DB)
- [x] **6.4 `POST /api/auth/refresh`** — token hợp lệ → cấp access token mới (+ xoay vòng nếu nhóm chọn); hết hạn/thu hồi → 401 (FR-45, FR-46) — dự kiến 13/11 · thực tế 07/11 ✔ Claude đã review — xoay vòng + phát hiện dùng lại → thu hồi mọi phiên (FR-46). Claude sửa: thiếu import model, thiếu class lỗi, router thiếu import schema
- [x] **6.5 `POST /api/auth/logout`** — thu hồi refresh token — dự kiến 13/11 · thực tế 07/11 ✔ Claude đã review — luôn 200, không bắt buộc access token
- [x] **6.6 Test + nhờ Claude review GĐ6** — dự kiến 13/11 · thực tế 07/11 — `tests/test_refresh.py` 17 test (Tuấn viết 16, Claude thêm 1); tổng 53 passed; R1–R9 qua trên PostgreSQL thật; đổi/đặt lại mật khẩu thu hồi refresh token (Q10)

## Giai đoạn 7 — Ảnh đại diện, thống kê (14/11)

- [x] **7.1 `POST /api/me/avatar`** + `utils/files.py` — kiểm tra loại file, dung lượng; lưu file, cập nhật `avatar_url` — dự kiến 14/11 · thực tế 07/11 → 07/11 ✔ Claude đã review — 9 test (Claude viết); tổng 62 passed; A1–A7 qua trên app thật (mở được ảnh qua /uploads). Claude sửa: giới hạn 2→5 MB theo Q8, thông báo 413 ghi cứng, import lặp, thiếu .gitignore
  - Quyết định Q8 (07/11): PNG + JPEG · tối đa 5 MB (413) · sai định dạng 415 · lưu `backend/uploads/avatars/` · sau này chuyển lên đám mây.
- [ ] **7.2 `GET /api/me/summary`** — khóa đang học, đã hoàn thành, kỹ năng đã biết, lộ trình đang theo — dự kiến 14/11 · thực tế __/__
  - ⚠️ Cần bảng của module khác (khóa học của tôi, lộ trình). Nếu chưa có: trả `known_skills` thật, các số còn lại chờ gộp.
- [ ] **7.3 Test + nhờ Claude review GĐ7** — dự kiến 14/11 · thực tế __/__

## Giai đoạn 8 — Hoàn thiện (15/11)

- [x] **8.1 `scripts/create_admin.py`** — tạo tài khoản admin (không tạo qua API) — dự kiến 15/11 · thực tế 07/11 ✔ Claude đã review — gọi lại auth_service.register + đổi role; mật khẩu nhập bằng getpass; 8 test (Claude viết, có test main() S1–S4); S5 admin đăng nhập trên PostgreSQL OK. Claude sửa: main() thiếu in kết quả + return 0
- [x] **8.2 Chạy toàn bộ** `pytest`, `black .`, `ruff check .` — dự kiến 15/11 · thực tế 07/11 — black (16 file định dạng, lần 2 unchanged) + ruff chỉ trên file của Tuấn; 70 passed. Còn UP017 (timezone.utc), E501 comment dài: chấp nhận
- [x] **8.3 Rà bảo mật**: không trả `hashed_password`/token gốc, không log mật khẩu, `.env` không bị commit (NFR-04, NFR-08) — dự kiến 15/11 · thực tế 07/11 — B1–B6 (xem Nhật ký 07/11)
**8.4 Bật lại phần của Hòa, gộp với nhóm**, tạo Pull Request — dự kiến 15/11 · thực tế __/__
  - [x] 07/11: merge `origin/Hoa` (878a984); bật seed + model + router learning-paths/nodes/skills. Seed PostgreSQL ~9 giây: 5.893 skills · 4.509 courses · 1.300 learning_paths. 70 test của Tuấn + 2 test của Hòa passed.
  - [ ] Router `recommendation_service` còn tắt — cần `pip install` sentence-transformers (+ PyTorch ~1–2 GB).
  - [ ] Bảng `learning_paths` trong DB tạo từ model cũ (CHECK goal_type chưa có `template`) — dữ liệu hiện tại không dùng `template` nên chưa lỗi; khi Hòa dùng `template` cần xóa bảng để tạo lại.
  - [ ] Tạo Pull Request gộp với nhóm.

---

## Giai đoạn 9 — Chuông thông báo + menu tài khoản (11/11)

> Tuấn chốt 11/11: chuông đặt **trước** avatar · khung thông báo kiểu Facebook, 2 tab **Tất cả / Chưa đọc** · logo → `/courses` (trang của Khôi; chưa xong thì hiện "Tạm thời chưa khả dụng", Khôi làm xong tự chuyển tới) · rê chuột vào avatar → menu sổ xuống · công tắc **Giao diện giữ trong trang Hồ sơ / Cài đặt**, không đưa vào menu.

- [x] **9.1 Bảng `notifications`** (`models/notification.py`) — thực tế 11/11 🤖
  - Cột: `notification_id`, `user_id` (FK users, **xóa tài khoản → xóa thông báo**), `type`, `title` (≤ 200), `body`, `link`, `is_read`, `read_at`, `created_at`, `source_id`.
  - Ràng buộc: `type` thuộc danh sách `TYPES`; `link` phải bắt đầu bằng `/` (chặn link ra ngoài); **UNIQUE (user_id, type, source_id)** khi có `source_id` → một đối tượng chỉ sinh 1 thông báo mỗi loại.
  - Index `(user_id, is_read, created_at)` cho truy vấn chuông (~60 giây/lần).
  - Không lưu: mật khẩu, token, link đặt lại mật khẩu, nội dung bài làm; `title`/`body` là chữ thuần.
  - Giữ tối đa **100** thông báo / người và không quá **90 ngày** — dọn ngay khi tạo thông báo mới.
- [x] **9.2 `services/notification_service.py`** — `notify()` **chỉ flush** (gọi trong transaction của module khác), `list_notifications`, `unread_count`, `mark_read`, `mark_all_read` — thực tế 11/11 🤖
- [x] **9.3 API** (`routers/v1/endpoints/notifications.py`, prefix `/api/me/notifications`) — thực tế 11/11 🤖
  - `GET ?unread_only=&page=&size=` (danh sách + `unread_count`) · `GET /unread-count` · `PATCH /{id}/read` · `POST /read-all`. Thông báo của người khác → 404; chưa đăng nhập → 401.
- [x] **9.4 Bốn loại thông báo ban đầu** (gắn vào đúng chỗ, cùng commit với thao tác gốc) — thực tế 11/11 🤖

  | `type` | Khi nào | Nội dung | Bấm vào |
  |---|---|---|---|
  | `welcome` | Đăng ký (`auth_service.register`) | "Chào mừng bạn đến với EduMentor AI" | `/me/skills` |
  | `password_changed` | Đổi mật khẩu (`user_service`) / đặt lại mật khẩu (`auth_service`) | "Mật khẩu của bạn vừa được thay đổi / đặt lại" + "Nếu không phải bạn…" | `/me/password` |
  | `review_graded` | Nộp bài ôn tập (`review_service.submit_attempt`) | "Kết quả ôn tập: 8/10 — Đạt" + tên khóa | `/review/{id}/result` |
  | `course_completed` | Đạt ôn tập lần đầu | "Chúc mừng! Bạn đã hoàn thành khóa …" | `/me/skills` |

- [x] **9.5 Frontend** — thực tế 11/11 🤖
  - `NotificationBell.jsx`: chuông + số chưa đọc (99+), hỏi lại mỗi 60 giây (chỉ khi tab đang mở) và khi quay lại tab; khung 2 tab, "Đánh dấu đã đọc tất cả", chấm vàng = chưa đọc, "5 phút trước" (`utils/formatters.timeAgo`); bấm thông báo → đánh dấu đã đọc + mở link; Esc / bấm ra ngoài để đóng; điện thoại: khung trải ngang màn hình.
  - `UserMenu.jsx`: rê chuột → sổ xuống (rời chuột chờ 150ms mới đóng); bấm / chạm / Enter cũng mở; Esc đóng. Mục: Hồ sơ của tôi · Cài đặt tài khoản · Kỹ năng của tôi · Lịch sử ôn tập · (admin) Quản trị · Đăng xuất (hộp xác nhận sẵn có).
  - `Header.jsx`: logo → `/courses`; chuông trước avatar.
- [x] **9.6 Kiểm thử** — thực tế 11/11 🤖
  - Backend `tests/test_notifications.py` **14 test** (4 sự kiện, đổi mật khẩu sai không tạo, chống trùng, chặn loại lạ + link ngoài, 2 tab, phân trang, đọc 1 / đọc hết, không xem/sửa được của người khác, giữ 100 + 90 ngày). Toàn bộ **499 passed**.
  - Chrome thật (`scratchpad/shots/bell_menu.mjs`) **11/11**: số trên chuông, chuông trước avatar, 2 tab, bấm thông báo → mở link + giảm số, đọc hết, Esc, menu rê chuột (không có "Giao diện"), rời chuột đóng, bấm mục menu, logo → `/courses`, điện thoại 375px không tràn. Đã dọn dữ liệu thử.
  - Sửa trong lúc kiểm: máy có chuột, rê vào (menu mở) rồi **bấm** avatar thì menu bị đóng ngay → giờ bấm giữ menu mở.
- [x] **9.8 Đổi menu avatar + 2 trang cài đặt mới** (Tuấn gửi thiết kế 11/11) — thực tế 12/11 🤖
  - Menu avatar: **bỏ** "Kỹ năng của tôi", "Lịch sử ôn tập" → **thay bằng** "Giao diện", "Thông báo qua email". Menu còn: Hồ sơ của tôi · Cài đặt tài khoản · Giao diện · Thông báo qua email · (admin) Quản trị · Đăng xuất. (Kỹ năng vẫn vào từ Hồ sơ / Cài đặt; Lịch sử ôn tập vẫn ở menu "Ôn tập".)
  - Cột trái Cài đặt: thêm "Giao diện", "Thông báo qua email"; **bỏ công tắc giao diện nhỏ** (đã có trang riêng). Công tắc Tối / Sáng trên trang Hồ sơ **giữ nguyên**.
  - **Trang Giao diện** `/me/appearance` (`AppearancePage.jsx`) — nhãn "Lưu trên trình duyệt" (localStorage, `utils/theme.js`):
    - Chế độ màu **Tối / Sáng / Theo hệ thống** — "Theo hệ thống" tự đổi khi Windows / điện thoại đổi sáng ↔ tối.
    - Cỡ chữ **Nhỏ / Vừa / Lớn** (0.9 / 1 / 1.18) — chỉ phóng **nội dung câu hỏi ôn tập** (đề, phương án, bài làm, đáp án) qua biến CSS `--reading-scale`; giao diện giữ nguyên. Trang bài học (nhóm khác) dùng: `font-size: calc(15px * var(--reading-scale, 1))`.
    - Giảm chuyển động (công tắc) — dùng sẵn `styles/reduced-motion.css`.
  - **Trang Thông báo qua email** `/me/email-notifications` (`EmailNotificationsPage.jsx`) — bấm là **lưu ngay lên máy chủ**, lỗi thì trả công tắc về như cũ:
    - Bảng mới **`email_preferences`** (1 dòng / người; chưa có dòng = mặc định): `review_reminder` (bật), `course_suggestions` (tắt), `feedback_replies` (bật). Bảng **riêng** vì `create_all()` không thêm cột vào bảng `users` đã có.
    - API `GET` / `PATCH /api/me/email-preferences` (khóa lạ → 422). Hàm `email_preference_service.wants_email(db, user_id, key)` cho nơi gửi email hỏi trước.
    - Email **bảo mật** (quên / đổi mật khẩu) và email **kết quả ôn tập** luôn gửi, không có công tắc.
    - ⚠️ **Mới là TÙY CHỌN — 3 loại email này CHƯA được gửi:** nhắc ôn tập đến hạn cần quy tắc "đến hạn" (module 09 bước 5.6, đang chờ bàn) + gửi định kỳ tối đa 1 email/tuần; khóa gợi ý mới → Khôi / Hòa; phản hồi góp ý → module góp ý (`models/feedback.py` còn TODO).
  - Kiểm: backend `tests/test_email_preferences.py` 5 test, toàn bộ backend xanh; Chrome thật `scratchpad/shots/prefs.mjs` **8/8** (menu, Theo hệ thống tự đổi, Sáng + F5, cỡ chữ câu hỏi 21px → 24.8px còn menu giữ 14px, giảm chuyển động, email mặc định, bật → F5 vẫn giữ + DB đúng); chạy lại chuông/menu 11/11, K1–K15 18/18.
- [x] **9.9 Chỉnh nút Đăng xuất** (Tuấn 12/11) — bỏ nút Đăng xuất trên thẻ đầu trang **Hồ sơ** (chỉ còn Chỉnh sửa hồ sơ + Đổi mật khẩu); trong **menu avatar**, Đăng xuất thành nút riêng ở cuối, **nằm giữa**, viền đỏ. Đăng xuất còn ở: menu avatar + cột trái Cài đặt. Kiểm lại: K1–K15 18/18, chuông/menu 11/11, giao diện/email 8/8.
- [x] **9.10 Bỏ công tắc Giao diện trên trang Hồ sơ + thêm thông tin cá nhân** (Tuấn 12/11) — thực tế 12/11 🤖
  - Trang Hồ sơ: bỏ công tắc Tối / Sáng (đã có trang **Giao diện** trong menu avatar).
  - Trang Sửa hồ sơ thêm: **Ngày tháng năm sinh** (1900 → hôm nay) · **Giới tính** Nam / Nữ (bấm lại để bỏ chọn) · **Quê quán** (≤ 100 ký tự) · **Số CCCD** (12 số) · **Số điện thoại** (10 số, bắt đầu 0; nhận cả "+84", dấu cách, dấu chấm). Email, Vai trò, Ngày tham gia vẫn chỉ xem.
  - Bảng mới **`user_profiles`** (1 dòng / người, xóa tài khoản → xóa theo). Bảng riêng vì `create_all()` không thêm cột vào `users`.
  - **CCCD bảo mật:** lưu **mã hóa** (Fernet, khóa suy từ `SECRET_KEY` — `core/security.encrypt_pii`) + **bản che** `345*********` (chỉ lộ 3 số đầu) + **dấu vân tay HMAC** (UNIQUE → một CCCD không dùng cho 2 tài khoản, 409). API **không bao giờ trả số đầy đủ**; ô CCCD để trống = giữ số cũ. ⚠️ Đổi `SECRET_KEY` → CCCD cũ không giải mã được (người dùng nhập lại); triển khai thật nên dùng khóa riêng `PII_ENCRYPTION_KEY`. Thêm `cryptography>=42.0` vào `requirements.txt` (máy đã có sẵn).
  - API: `GET /api/me` thêm `date_of_birth`, `gender`, `hometown`, `phone`, `citizen_id_masked`; `PATCH /api/me` nhận thêm các trường trên + `citizen_id` (chỉ ghi) — **không gửi = giữ nguyên, null = xóa**.
  - Kiểm: backend `tests/test_me_profile.py` **16 test** (lưu đủ, mã hóa trong DB, không lộ số, giữ / xóa từng trường, +84, 7 kiểu dữ liệu sai, CCCD trùng 409, không đổi được email / role); toàn bộ **518 passed**. Chrome thật `scratchpad/shots/profile_info.mjs` **5/5** (không còn công tắc ở Hồ sơ, đủ ô, báo lỗi, lưu + F5 giữ, API / DB không chứa số CCCD đầy đủ); K1–K15 vẫn 18/18.
- [x] **9.11 "Cài đặt tài khoản" → Đổi mật khẩu** (Tuấn 12/11) — mục "Cài đặt tài khoản" trong menu avatar mở thẳng `/me/password`; **bỏ nút Đổi mật khẩu** trên thẻ đầu trang Hồ sơ (chỉ còn Chỉnh sửa hồ sơ). Kiểm: chuông/menu 11/11 (M3 → `/me/password`), thông tin cá nhân 5/5, K1–K15 18/18.
- [ ] **9.7 Tuấn xem lại — đã đủ ý chưa?** (Claude liệt kê điểm có thể bổ sung)
  - [ ] Ai gửi 3 loại email ở 9.8 và khi nào (nhắc ôn tập cần chốt quy tắc "đến hạn" — 5.6 module 09).
  - [ ] Trang **"Xem tất cả thông báo"** riêng (`/me/notifications`) — hiện chỉ có khung trên chuông, xem được 20 thông báo mới nhất mỗi tab.
  - [ ] Xóa từng thông báo / menu "…" trên mỗi thông báo (Facebook có) — hiện chưa có.
  - [ ] Thông báo **đẩy ngay** (websocket) — hiện hỏi lại mỗi 60 giây.
  - [ ] Âm thanh / hiệu ứng khi có thông báo mới.
  - [ ] Loại thông báo của nhóm khác: Khôi (`course_recommended`?), Hòa (`path_updated`?), Tâm (`tutor_reply`?) — thêm vào `TYPES` rồi gọi `notification_service.notify()` (ví dụ ở đầu file service).
  - [ ] Khi có **RealAI** chấm lâu (trạng thái `grading`): thông báo "Kết quả ôn tập" lúc chấm xong là lối báo chính → làm cùng 5.1 (module 09).
  - [ ] Báo nhóm: header giờ có chuông + menu avatar; logo trỏ `/courses` (Khôi).

## Checklist 13 endpoint

| Method | Endpoint | GĐ | Code | Test | Review |
|---|---|---|---|---|---|
| POST | `/api/auth/register` | 2 | [x] | [x] | [x] |
| POST | `/api/auth/login` | 2 | [x] | [x] | [x] |
| POST | `/api/auth/refresh` | 6 | [x] | [x] | [x] |
| POST | `/api/auth/logout` | 6 | [x] | [x] | [x] |
| POST | `/api/auth/forgot-password` | 5 | [x] | [x] | [x] |
| POST | `/api/auth/reset-password` | 5 | [x] | [x] | [x] |
| GET | `/api/me` | 3 | [x] | [x] | [x] |
| PATCH | `/api/me` | 3 | [x] | [x] | [x] |
| POST | `/api/me/avatar` | 7 | [x] | [x] | [x] |
| POST | `/api/me/change-password` | 3 | [x] | [x] | [x] |
| GET | `/api/me/summary` | 7 | [ ] | [ ] | [ ] |
| GET | `/api/me/skills` | 4 | [ ] | [ ] | [ ] |
| PATCH | `/api/me/skills` | 4 | [ ] | [ ] | [ ] |

## Câu hỏi cần chốt (BA chưa nói rõ)

Điền câu trả lời khi nhóm chốt; chưa chốt thì làm phần không phụ thuộc trước.

| # | Câu hỏi | Cần trước GĐ | Trả lời | Ngày chốt |
|---|---|---|---|---|
| Q1 | Quy tắc mật khẩu cụ thể (độ dài, chữ hoa/thường/số/ký tự đặc biệt)? | 1 | Theo màn demo ChangePassword/ResetPassword: ≥ 8 ký tự, có chữ hoa, chữ thường, chữ số, ký tự đặc biệt; thêm ≤ 72 byte (giới hạn bcrypt). Còn mở: có cho dấu cách / chữ có dấu không? | 05/11 |
| Q2 | Access token sống bao lâu? (`.env` đang để 30 phút) | 1 | | |
| Q3 | Đăng ký có trường `confirm_password` không? | 2 | Có — màn demo Register: Họ và tên, Email, Mật khẩu, Xác nhận mật khẩu. Chỉ dùng để so khớp, không lưu. | 05/11 |
| Q4 | Login trả về những gì (token + user)? | 2 | `{access_token, token_type: "bearer", user: {user_id, full_name, email, role, avatar_url, created_at}}`; sai → 401 (demo Main: "Lỗi 401: …"). Refresh token bổ sung ở GĐ6. | 05/11 |
| Q5 | Dùng model `Skills` nào khi gộp với nhóm? | 4 | | |
| Q6 | Link đặt lại mật khẩu sống bao lâu? Gửi email bằng SMTP nào? | 5 | **Đề xuất (chờ nhóm xác nhận):** 30 phút (`RESET_TOKEN_EXPIRE_MINUTES`); dev in link ra terminal, khi có SMTP thật dùng `smtplib` (không thêm thư viện) | 06/11 |
| Q7 | Refresh token sống bao lâu, có xoay vòng không, gửi qua body hay cookie? | 6 | **Đề xuất (chờ nhóm xác nhận):** 7 ngày (`REFRESH_TOKEN_EXPIRE_DAYS`); có xoay vòng (mỗi refresh token dùng 1 lần); gửi trong JSON body | 06/11 |
| Q8 | Ảnh đại diện: định dạng, dung lượng tối đa, lưu ở đâu? | 7 | **Tuấn chốt:** định dạng **PNG + JPEG** (khớp `accept` màn demo; kiểm tra chữ ký byte đầu file, không tin content_type; không nhận SVG/GIF/HEIC); tối đa **5 MB** (`AVATAR_MAX_BYTES`); lưu **thư mục server** `backend/uploads/avatars/` (không commit; Docker cần volume) — **mở rộng sau lên dịch vụ đám mây** (Cloudinary/S3…): chỉ viết lại `utils/files.py`, cột `avatar_url` chứa được URL đầy đủ. Thu nhỏ ảnh phía frontend: chưa chốt | 07/11 |
| Q9 | `/me/summary` đếm "đang học", "lộ trình đang theo" từ bảng nào? | 7 | | |
| Q10 | Đổi mật khẩu xong có hủy các phiên đăng nhập khác không? (access token cũ vẫn sống tối đa 30 phút; refresh token ở GĐ6) | 6 | **Đề xuất (chờ nhóm xác nhận):** có — đổi/đặt lại mật khẩu thì thu hồi mọi refresh token của user | 06/11 |

## Nhật ký

| Ngày | Đã làm | Vướng mắc |
|---|---|---|
| 05/11 | Cài môi trường, chuẩn hóa cấu trúc, viết lại `CLAUDE.md`, ngắt seed của Hòa, lập kế hoạch này | Docker Desktop tắt → server chưa chạy lại |
| 05/11 | Xong GĐ0; viết model `Users` (1.1), bật `SECRET_KEY` (1.2); bảng `users` đã tạo trong DB | Lỡ viết model vào `skill.py` của Hòa → đã chuyển sang `user.py` và `git restore` lại `skill.py` |
| 05/11 | Xong GĐ1 (security, dependencies); GĐ2: register/login + `GET /me`; tự chạy trên Swagger: đăng ký → đăng nhập → Authorize → `/me` ra 200 | Đăng nhập 401 vì chưa đăng ký; đăng ký 422 vì `password` và `confirm_password` lệch dấu `!` — validator chặn đúng |
| 07/11 | GĐ6 refresh/logout; GĐ7.1 avatar; merge nhánh Hòa (datajson); GĐ8.1–8.3 | **Rà bảo mật:** B1 ✅ không response nào có hashed_password/token_hash · B2 ⚠️ `.env` từng bị commit (9372a94, 30/10, đã xóa ở d40509d) — chỉ chứa giá trị dev/mẫu, SECRET_KEY hiện tại KHÔNG bị lộ · B3 ✅ SECRET_KEY 86 ký tự · B4 ⚠️ email.py in link chứa token khi chưa cấu hình SMTP (chỉ chấp nhận khi dev) · B5 ✅ JWT khóa HS256 · B6 ⚠️ `SQL_ECHO=True` in cả GIÁ TRỊ tham số (email, bản băm) ra log → đặt SQL_ECHO=False khi không debug, hoặc báo Hòa thêm `hide_parameters=True` trong database.py. **Hạn chế đã biết:** chưa giới hạn số lần đăng nhập sai (brute force); access token sống tới 30 phút sau đổi mật khẩu; refresh token qua JSON body |
| | | |
