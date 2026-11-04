# F01 — Phase P04: Authentication & Profile (F01)

> Thuộc kế hoạch tính năng [F01 — Xác thực và hồ sơ người dùng](plan.md). Phase `P04` là Phase của khung kế hoạch chung (`plans/plan.md` PART 3, D-DOC-05). File này là **nơi quản lý duy nhất** trạng thái, người làm, phụ thuộc và bằng chứng của các Task trong bảng dưới. Task ID giữ nguyên từ `plans/plan.md` (chuyển ngày 2026-11-03).

## 1. Mục tiêu và phạm vi

**1. Phase Information** — Phase ID: P04 · Objective: F01 đầy đủ backend và frontend theo đặc tả · Related Features: F01 · Responsible: Tuấn (D-OWN-01, D-OWN-02) · Support: CXĐ · Reviewer: CPC · Dependencies: P01, P02-T02, P03-T02/T03/T05 · Initial Status: NOT_STARTED

**2. Scope** — Trong: `/api/auth/*`, `/api/me*` (trừ courses, bookmarks, review-history, learning-paths), bảng User, UserSkill, PasswordResetToken, `core/security.py`, `core/dependencies.py`, `core/email.py`, `scripts/create_admin.py`, trang `/login` … `/me/skills`. Ngoài: RefreshToken (chờ ND-43); Course Tracking; Learning Path. Nguồn: `docs/modules/auth-profile.md`, `.tests.md`; `docs/api-endpoints.md` §2; `docs/database-design.md` §3.1, §3.2, §3.4; BA §6.1 (FR-01–04), §6.9 (FR-40–46); `ui-design` Main, Main-LampOff, Register, ForgotPassword, ForgotSent, ResetPassword, ResetExpired, Profile, Profile-Light, EditProfile, ChangePassword, Skills, Logout.

## 2. Task

| Task ID | Task Name | Description | Source Reference | Responsible | Support | Reviewer | Dependencies | Deliverable | Status | Evidence | Blocker |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P04-T01 | Đối chiếu đặc tả F01 với BA | So `auth-profile.md` với BA FR-01–04, FR-40–46, AC-01; ghi điểm lệch | BA §6.1, §6.9, §11.2 | Tuấn | CXĐ | CPC | — | Ghi chú đối chiếu | NOT_STARTED | — | — |
| P04-T02 | `core/security.py` | Băm Argon2id; JWT HS256 (`sub`, `iat`, `exp`), 30 phút; chỉ chấp nhận HS256 | D-AUTH-01, 02, 04; AP-R21 | Tuấn | CXĐ | CPC | P01-T02, P00-T04 | `security.py` + test | BLOCKED | — | ND-44, ND-45 — băm Argon2id và JWT là phần cốt lõi. Phần làm được: hàm kiểm chính sách mật khẩu (D-AUTH-05, AP-R19) |
| P04-T03 | `core/dependencies.py` | `get_current_user` (vai trò lấy từ DB), `require_admin` — dùng chung mọi module | AP-R18, AP-R21; `backend-rules.md` §2 | Tuấn | CXĐ | CPC | P04-T02, P04-T04 | `dependencies.py` + test 401/403 | BLOCKED | — | Theo P04-T02 |
| P04-T04 | Model + migration User, UserSkill, PasswordResetToken | Đúng §3.1, §3.2, §3.4; không tạo RefreshToken | `database-design.md` §3; `auth-profile.md` §3 | Tuấn | CXĐ | CPC | P01-T05, P02-T02 | Model + migration | NOT_STARTED | — | Một phần: migration chờ Alembic (P01-T05). Class model viết được theo §3.1, §3.2, §3.4 |
| P04-T05 | `POST /api/auth/register` | Luôn tạo `student`; trùng email 409; chính sách mật khẩu | AP-R01, 02, 06, 19; §4.1 | Tuấn | CXĐ | CPC | P04-T02, P04-T04 | Router, service, schema, repository | NOT_STARTED | — | Một phần: hàm băm chờ ND-45 (P04-T02); ND-07, 08, 18, 37, 46, 47. Schema, repository, kiểm trùng email (AP-R02) làm được |
| P04-T06 | `POST /api/auth/login` (access token) | Xác thực, cấp access token; response gồm `role` | AP-R06, 07, 21; §4.2 | Tuấn | CXĐ | CPC | P04-T02, P04-T04 | Router, service | BLOCKED | — | Cốt lõi (xác minh mật khẩu, cấp JWT) chờ P04-T02 (ND-44, ND-45); hình dạng response ND-19; refresh token ND-41 |
| P04-T07 | Refresh token và logout | `POST /api/auth/refresh`, `/logout`; bảng RefreshToken | D-AUTH-03; §4.3, §4.3a | Tuấn | CXĐ | CPC | P04-T06 | API + bảng | BLOCKED | — | ND-40, 41, 42, 43, 48 |
| P04-T08 | Quên và đặt lại mật khẩu, `core/email.py` | Thông báo luôn giống nhau; mã băm, có hạn, dùng một lần | AP-R09, 10, 11; §4.4, §4.5; T28 | Tuấn | CXĐ | CPC | P04-T04 | API + `send_email` | NOT_STARTED | — | Một phần: chạy thật cần P04-T04; ND-39 (cách gửi), ND-36, ND-46, ND-47; định dạng link chứa mã chưa có (`structure.md` §3) |
| P04-T09 | `GET/PATCH /api/me`, đổi mật khẩu | Chỉ nhận `full_name`, `avatar_url`; đổi mật khẩu cần mật khẩu hiện tại | AP-R03, 04, 12; §4.6, §4.7, §4.9 | Tuấn | CXĐ | CPC | P04-T03, P04-T04 | API | NOT_STARTED | — | Một phần: xác thực request chờ P04-T03; ND-12, ND-18, ND-36, ND-62. Schema, service, repository làm được |
| P04-T10 | `POST /api/me/avatar` | Upload ảnh | D07; §4.8 | Tuấn | CXĐ | CPC | P04-T09 | API | BLOCKED | — | ND-62, ND-12 |
| P04-T11 | `GET /api/me/summary` | Đếm khóa học, kỹ năng, lộ trình | AP-R17; §4.10 | Tuấn | CXĐ | CPC | P04-T03, P06-T04, P07-T04 | API | BLOCKED | — | ND-13; theo P06-T04, P07-T04 |
| P04-T12 | `GET/PATCH /api/me/skills` | Một transaction; `skill_id` không tồn tại 404 + rollback; upsert `add` | AP-R13, 14; §4.11, §4.12 | Tuấn | CXĐ | CPC | P04-T03, P04-T04 | API | NOT_STARTED | — | Một phần: xác thực request chờ P04-T03; ND-09, 11, 64. Quy tắc chính AP-R14 đã chốt |
| P04-T13 | `scripts/create_admin.py` | Tạo admin, không qua API | AP-R05 | Tuấn | CXĐ | CPC | P04-T02, P04-T04 | Script | BLOCKED | — | Theo P04-T02 |
| P04-T14 | Test backend F01 | Các kịch bản không có cột "Chờ" trong `auth-profile.tests.md` | `auth-profile.tests.md`; skill `auth-profile` §9 | Tuấn | CXĐ | CPC | P01-T08, P04-T05, P04-T08, P04-T09, P04-T12 | `tests/test_auth.py`, kết quả `pytest` | NOT_STARTED | — | Một phần: chạy test cần P01-T08. Viết test cho kịch bản không có cột "Chờ" làm được. Test cho P04-T06, T07, T10, T11, T13 viết khi các task đó hết chặn |
| P04-T15 | API client F01 | `auth.api.js`, `me.api.js` theo §2 | D-FE-10, D-FE-11 | Tuấn | CXĐ | CPC | P03-T03 | 2 file API | NOT_STARTED | — | — |
| P04-T16 | Trang Đăng nhập, Đăng ký | Theo `ui-design` Main, Main-LampOff, Register; không hiện tài khoản demo | D-FE-07, D-FE-12 | Tuấn | CXĐ | CPC | P03-T04, P03-T05, P04-T15 | `LoginPage`, `RegisterPage` | NOT_STARTED | — | Một phần: ND-56 (đèn ở Đăng ký, khả năng tiếp cận), ND-47, ND-51 |
| P04-T17 | Trang Quên/đặt lại mật khẩu | ForgotPassword, ForgotSent, ResetPassword, ResetExpired | `structure.md` §3; `ui-design` | Tuấn | CXĐ | CPC | P04-T15 | 4 page | NOT_STARTED | — | Một phần: định dạng link chứa mã chưa có |
| P04-T18 | Trang Hồ sơ | Profile, Profile-Light; số liệu, kỹ năng, khóa học, ôn tập gần đây; công tắc Sáng/Tối | `structure.md` §3; `ui-design` | Tuấn | CXĐ | CPC | P04-T15 | `ProfilePage` | NOT_STARTED | — | Một phần: dữ liệu từ P04-T11, P06, P09; ND-10 |
| P04-T19 | Trang Sửa hồ sơ, Đổi mật khẩu | EditProfile, ChangePassword | `ui-design`; AP-R03 | Tuấn | CXĐ | CPC | P04-T15 | 2 page | NOT_STARTED | — | Một phần: ND-62 (avatar), ND-12, ND-47, ND-51 |
| P04-T20 | Trang Kỹ năng | Xem, sửa trạng thái, thêm, xóa kỹ năng | `ui-design` Skills; AP-R14 | Tuấn | CXĐ | CPC | P04-T15 | `SkillsPage` | NOT_STARTED | — | Một phần: ND-57 (danh mục kỹ năng cho học viên), ND-64 |
| P04-T21 | Đăng xuất | LogoutDialog; gọi logout rồi xóa token | `ui-design` Logout | Tuấn | CXĐ | CPC | P04-T15 | `LogoutDialog` | NOT_STARTED | — | Một phần: ND-48, ND-50 |
| P04-T22 | Test giao diện F01 | Kiểm thử các trang F01 | ND-67, ND-68 | Tuấn | CXĐ | CPC | P04-T16…T21 | Kết quả test | BLOCKED | — | ND-67, ND-68 |

Cột Responsible: Task có ghi "D-OWN-02" đã đổi theo D-OWN-02 (`docs/decisions.md` §2); giá trị cũ ghi trong ngoặc ("trước: …") để truy vết. Trạng thái, phụ thuộc, bằng chứng, ghi chú chặn giữ nguyên.

## 3. Điều kiện hoàn thành, review, chặn

**4. Deliverables** — API §2 (trừ phần bị chặn); 3 bảng; 10+ trang F01; `test_auth.py`.
**5. Review Checklist** — AP-R01…R23; không trả `hashed_password`; vai trò từ DB; không nhận `role`/`email` khi sửa; transaction `PATCH /me/skills`; không log mật khẩu/token; giao diện ẩn câu chữ khẳng định quy tắc chưa chốt (ND-51).
**6. Blockers & Open Issues** — ND-07…13, 18, 19, 36…48, 56, 57, 62, 64; ND-14, 15, 16.
**7. Completion Criteria** — Task không bị chặn DONE có evidence; Task BLOCKED ghi rõ mã chặn.

## 4. Điểm cần review

- Task chuyển REVIEW phải có Evidence (PART 2 quy tắc 6); DONE cần kết quả review.
- Không tự đổi BLOCKED khi mã chặn (ND, T, Task) chưa được giải quyết trong `docs/decisions.md`.
- Câu hỏi chưa có ND: ghi vào [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) mục C, đánh dấu `NEEDS_OWNER_INPUT`.

## 5. Hướng dẫn chi tiết từng Task

Phần này chỉ hướng dẫn, **không** có trạng thái (trạng thái ở bảng mục 2). Đường dẫn file theo `docs/structure.md` §1, §2; tên repository chưa được đặt trong tài liệu. Mục đặc tả: `docs/modules/auth-profile.md` (viết tắt §x). Kịch bản test: `docs/modules/auth-profile.tests.md` (AP-Txx). "Sẵn sàng" theo [plan.md](plan.md) mục 4.

### Nhóm A — Nền tảng của F01

#### P04-T01 — Đối chiếu đặc tả F01 với BA
- **Mục tiêu:** xác nhận `auth-profile.md` khớp BA và SRS; ghi điểm lệch.
- **File:** chỉ tài liệu (ghi chú đối chiếu; điểm lệch đề xuất thành ND qua người có thẩm quyền).
- **Đầu vào:** BA FR-01 … 04, FR-40 … 46, AC-01; SRS-AUTH-01 … 07, SRS-PROF-01 … 05; `auth-profile.md` §1 "Yêu cầu".
- **Kết quả:** danh sách điểm lệch có nguồn; không sửa BA, SRS.
- **Hoàn thành khi:** mọi mã FR và SRS ở trên có dòng đối chiếu.
- **Evidence:** đường dẫn ghi chú đối chiếu.
- **Sẵn sàng:** làm được ngay.

#### P04-T02 — `core/security.py`
- **Mục tiêu:** băm, xác minh mật khẩu Argon2id; tạo, xác minh JWT HS256; hàm kiểm chính sách mật khẩu dùng chung.
- **File:** `backend/app/core/security.py`; cấu hình `backend/app/core/config.py` (`SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Đầu vào:** D-AUTH-01, 02, 04, 05; AP-R06, R19, R21, R23; `backend-rules.md`.
- **Kết quả:** hàm băm, xác minh; tạo token có `sub`, `iat`, `exp` 30 phút; từ chối thuật toán khác HS256; hàm kiểm mật khẩu dùng cho register, reset, change.
- **Hoàn thành khi:** test đơn vị cho AP-T101 … T103, T105 … T107, T112, T113 (không có cột Chờ) đạt; không log mật khẩu.
- **Evidence:** `pytest` cho security, commit.
- **Sẵn sàng:** chỉ hàm kiểm mật khẩu (trừ ký tự đặc biệt, khoảng trắng — ND-46). Băm, JWT chờ ND-44, ND-45.

#### P04-T03 — `core/dependencies.py`
- **Mục tiêu:** `get_current_user` (tải user và vai trò từ DB) và `require_admin`, dùng chung mọi module.
- **File:** `backend/app/core/dependencies.py`.
- **Đầu vào:** AP-R18, R21; `backend-rules.md` §2.
- **Kết quả:** token sai, hết hạn → 401; không phải admin → 403.
- **Hoàn thành khi:** AP-T20 … T28 đạt.
- **Evidence:** `pytest` 401, 403.
- **Sẵn sàng:** chờ P04-T02 (ND-44) và session DB (P01-T03).

#### P04-T04 — Model và migration `User`, `UserSkill`, `PasswordResetToken`
- **Mục tiêu:** bảng của F01 đúng thiết kế.
- **File:** `backend/app/models/user.py`, `user_skill.py`, `password_reset_token.py`; migration trong `backend/alembic/versions/`.
- **Đầu vào:** `database-design.md` §3.1, §3.2, §3.4, §8.1; `auth-profile.md` §3. Không tạo RefreshToken (ND-43).
- **Kết quả:** model khớp kiểu, ràng buộc, CHECK, FK (User CASCADE, Skill RESTRICT); migration tạo 3 bảng.
- **Hoàn thành khi:** `alembic upgrade head` chạy được; review khớp §3.
- **Evidence:** commit; kết quả migration.
- **Sẵn sàng:** viết class model làm được ngay; migration chờ P01-T05; `UserSkill` cần model `Skill` (P02-T02).

### Nhóm B — API xác thực

#### P04-T05 — `POST /api/auth/register`
- **Mục tiêu:** đăng ký tài khoản `student`.
- **File:** `backend/app/routers/auth.py`, `schemas/auth.py`, `services/auth_service.py`, repository người dùng.
- **Đầu vào:** §4.1; AP-R01, R02, R06, R19, R20; T09.
- **Kết quả:** 201 + thông tin người dùng; trùng email 409; dữ liệu sai 422; không nhận `role`.
- **Hoàn thành khi:** AP-T01, T03 … T05 đạt; các kịch bản có cột Chờ (AP-T02, T06 … T09) chỉ viết khi ND tương ứng chốt.
- **Evidence:** `pytest`.
- **Sẵn sàng:** schema, kiểm trùng email làm được; băm chờ ND-45; ND-07, 08, 18, 37, 46, 47.

#### P04-T06 — `POST /api/auth/login` (access token)
- **Mục tiêu:** xác thực, cấp access token, trả thông tin người dùng gồm `role`.
- **File:** `routers/auth.py`, `services/auth_service.py`.
- **Đầu vào:** §4.2; AP-R06, R07, R21.
- **Kết quả:** 200 + access token 30 phút; sai thông tin 401 với thông báo chung.
- **Hoàn thành khi:** AP-T11 … T14 đạt.
- **Evidence:** `pytest`.
- **Sẵn sàng:** BLOCKED — P04-T02 (ND-44, ND-45); hình dạng response ND-19, ND-41.

#### P04-T07 — Refresh token và logout
- **Mục tiêu:** `POST /api/auth/refresh` (rotation), `POST /api/auth/logout` (thu hồi refresh token); bảng RefreshToken.
- **File:** `routers/auth.py`, `services/auth_service.py`, model RefreshToken (tên file ghi vào `structure.md` khi ND-43 duyệt).
- **Đầu vào:** §4.3, §4.3a; AP-R08, R22; D-AUTH-03; `database-design.md` §3.5 (PROPOSED).
- **Kết quả:** theo D-AUTH-03 sau khi các ND chốt.
- **Hoàn thành khi:** AP-T30 … T38 đạt.
- **Evidence:** `pytest`.
- **Sẵn sàng:** BLOCKED — ND-40, 41, 42, 43, 48.

#### P04-T08 — Quên và đặt lại mật khẩu, `core/email.py`
- **Mục tiêu:** gửi link đặt lại; đặt mật khẩu mới bằng mã dùng một lần.
- **File:** `routers/auth.py`, `services/auth_service.py`, `backend/app/core/email.py`.
- **Đầu vào:** §4.4, §4.5; AP-R09 … R11; T01, T02, T28; transaction §7.
- **Kết quả:** forgot luôn trả cùng thông báo; mã chỉ lưu bản băm, có hạn, dùng một lần; đặt lại thành công thì vô hiệu mã cũ trong cùng transaction.
- **Hoàn thành khi:** AP-T40 … T47 đạt.
- **Evidence:** `pytest`; ảnh email thử (không chứa mã gốc trong log).
- **Sẵn sàng:** làm được phần mã đặt lại; ND-39 (cách gửi), ND-36, ND-46, ND-47; định dạng link chứa mã chưa có.

#### P04-T13 — `scripts/create_admin.py`
- **Mục tiêu:** tạo tài khoản admin không qua API.
- **File:** `backend/scripts/create_admin.py`.
- **Đầu vào:** AP-R05; T09.
- **Kết quả:** admin được tạo với mật khẩu băm Argon2id.
- **Hoàn thành khi:** chạy script tạo được admin, đăng nhập được.
- **Evidence:** lệnh chạy, kết quả.
- **Sẵn sàng:** BLOCKED — P04-T02.

### Nhóm C — API hồ sơ và kỹ năng

#### P04-T09 — `GET/PATCH /api/me`, đổi mật khẩu
- **Mục tiêu:** xem, sửa hồ sơ; đổi mật khẩu khi đã đăng nhập.
- **File:** `backend/app/routers/me.py`, `schemas/user.py`, `services/user_service.py`.
- **Đầu vào:** §4.6, §4.7, §4.9; AP-R03, R04, R12, R18.
- **Kết quả:** `GET` trả `user_id`, `email`, `full_name`, `avatar_url`, `role`, `created_at`; `PATCH` chỉ nhận `full_name`, `avatar_url`; đổi mật khẩu sai mật khẩu hiện tại → 400.
- **Hoàn thành khi:** AP-T50, T51, T54 … T57 đạt.
- **Evidence:** `pytest`.
- **Sẵn sàng:** schema, service làm được; xác thực request chờ P04-T03; ND-12, ND-18, ND-36, ND-62.

#### P04-T10 — `POST /api/me/avatar`
- **Mục tiêu:** tải ảnh đại diện.
- **File:** `routers/me.py`, `services/user_service.py`.
- **Đầu vào:** §4.8; D07, T04.
- **Kết quả:** 200 `avatar_url`; 413, 415.
- **Hoàn thành khi:** kịch bản avatar trong `.tests.md` §6 đạt.
- **Evidence:** `pytest`.
- **Sẵn sàng:** BLOCKED — ND-62, ND-12.

#### P04-T11 — `GET /api/me/summary`
- **Mục tiêu:** số liệu tổng hợp trang hồ sơ.
- **File:** `routers/me.py`, `services/user_service.py`.
- **Đầu vào:** §4.10; AP-R17; T05.
- **Kết quả:** `ongoing_courses`, `completed_courses`, `known_skills`, `ongoing_paths`.
- **Hoàn thành khi:** kịch bản summary trong `.tests.md` §6 đạt.
- **Evidence:** `pytest`.
- **Sẵn sàng:** BLOCKED — ND-13; cần bảng của F04 (P06-T04), F05 (P07-T04).

#### P04-T12 — `GET/PATCH /api/me/skills`
- **Mục tiêu:** xem, thêm, sửa, xóa kỹ năng của người dùng trong một transaction.
- **File:** `routers/me.py`, `schemas/user.py` (hoặc `skill.py`), `services/user_service.py`.
- **Đầu vào:** §4.11, §4.12; AP-R13, R14; T06, T07.
- **Kết quả:** lọc `status`; `skill_id` không tồn tại → 404 và rollback; `add` kỹ năng đã có là upsert.
- **Hoàn thành khi:** AP-T70, T71, T73 … T78, T81 đạt.
- **Evidence:** `pytest`.
- **Sẵn sàng:** logic AP-R14 làm được; xác thực chờ P04-T03; ND-09, 11, 64.

#### P04-T14 — Test backend F01
- **Mục tiêu:** `tests/test_auth.py` cho các kịch bản không có cột "Chờ".
- **File:** `backend/tests/test_auth.py`, `backend/tests/conftest.py`.
- **Đầu vào:** `auth-profile.tests.md` §1 … §8; skill `auth-profile` §9.
- **Kết quả:** test cho Task đã làm; test của T06, T07, T10, T11, T13 viết khi Task hết chặn.
- **Hoàn thành khi:** `pytest` đạt trên môi trường test.
- **Evidence:** kết quả `pytest`.
- **Sẵn sàng:** viết được; chạy chờ P01-T08 (DB test chưa quy định).

### Nhóm D — Frontend

#### P04-T15 — API client F01
- **Mục tiêu:** hàm gọi API xác thực, hồ sơ.
- **File:** `frontend/src/api/auth.api.js`, `frontend/src/api/me.api.js` (dùng `api/client.js`).
- **Đầu vào:** `api-endpoints.md` §2; D-FE-05, D-FE-10, D-FE-11.
- **Kết quả:** hàm cho mọi endpoint §2; không làm refresh (D-FE-05).
- **Hoàn thành khi:** trang F01 dùng được ở chế độ mock và thật.
- **Evidence:** commit; `npm run build`.
- **Sẵn sàng:** chờ P03-T03 (Chưa phân công).

#### P04-T16 — Trang Đăng nhập, Đăng ký
- **File:** `frontend/src/pages/auth/LoginPage.jsx`, `RegisterPage.jsx` (+ `.module.css`).
- **Đầu vào:** `ui-design` Main, Main-LampOff, Register; D-FE-07, D-FE-12; `structure.md` §3.
- **Kết quả:** đúng giao diện; không hiện tài khoản mẫu; không hiển thị câu chữ khẳng định quy tắc chưa chốt (ND-51).
- **Hoàn thành khi:** chạy được với mock; gọi được API khi backend có.
- **Evidence:** ảnh màn, `npm run build`.
- **Sẵn sàng:** chờ P03-T04, T05, P04-T15; ND-56 (Đăng ký), ND-47.

#### P04-T17 — Trang Quên, đặt lại mật khẩu
- **File:** `pages/auth/ForgotPasswordPage.jsx`, `ForgotSentPage.jsx`, `ResetPasswordPage.jsx`, `ResetExpiredPage.jsx`.
- **Đầu vào:** `ui-design` ForgotPassword, ForgotSent, ResetPassword, ResetExpired; `structure.md` §3.
- **Kết quả:** 4 trang theo giao diện.
- **Hoàn thành khi:** luồng chạy được với mock.
- **Evidence:** ảnh màn.
- **Sẵn sàng:** chờ P04-T15; định dạng link chứa mã chưa có (`NEEDS_OWNER_INPUT`).

#### P04-T18 — Trang Hồ sơ
- **File:** `pages/profile/ProfilePage.jsx`.
- **Đầu vào:** `ui-design` Profile, Profile-Light; `structure.md` §3.
- **Kết quả:** thông tin, số liệu, kỹ năng, khóa học, ôn tập gần đây; công tắc Sáng/Tối.
- **Hoàn thành khi:** chạy được với mock; số liệu thật khi P04-T11, F04, F09 có API.
- **Evidence:** ảnh màn.
- **Sẵn sàng:** chờ P04-T15; ô "Mục tiêu học tập" chờ ND-10.

#### P04-T19 — Trang Sửa hồ sơ, Đổi mật khẩu
- **File:** `pages/profile/EditProfilePage.jsx`, `ChangePasswordPage.jsx`.
- **Đầu vào:** `ui-design` EditProfile, ChangePassword; AP-R03 (email chỉ đọc).
- **Kết quả:** sửa `full_name`; đổi mật khẩu.
- **Hoàn thành khi:** chạy được với mock.
- **Evidence:** ảnh màn.
- **Sẵn sàng:** chờ P04-T15; avatar ND-62, ND-12; ND-47, ND-51.

#### P04-T20 — Trang Kỹ năng
- **File:** `pages/profile/SkillsPage.jsx`.
- **Đầu vào:** `ui-design` Skills; AP-R14; D-FE-11 (theo `skill_id`).
- **Kết quả:** xem, đổi trạng thái, thêm, xóa kỹ năng.
- **Hoàn thành khi:** chạy được với mock.
- **Evidence:** ảnh màn.
- **Sẵn sàng:** chờ P04-T15; nguồn danh mục kỹ năng cho học viên ND-57; ND-64.

#### P04-T21 — Đăng xuất
- **File:** `frontend/src/components/profile/LogoutDialog.jsx`.
- **Đầu vào:** `ui-design` Logout; D-FE-05.
- **Kết quả:** xác nhận đăng xuất; xóa token phía client; gọi logout khi API có.
- **Hoàn thành khi:** sau đăng xuất về `/login`.
- **Evidence:** ảnh màn.
- **Sẵn sàng:** phần xóa token làm được (D-FE-05); gọi API chờ ND-48; route `/logout` ND-50.

#### P04-T22 — Test giao diện F01
- **Mục tiêu:** kiểm thử các trang F01.
- **Sẵn sàng:** BLOCKED — ND-67, ND-68 (chưa có quy định công cụ, mức kiểm thử).
