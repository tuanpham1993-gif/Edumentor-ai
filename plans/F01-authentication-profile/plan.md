# F01 — Xác thực và hồ sơ người dùng

> Kế hoạch tính năng. Vai trò: hướng dẫn và theo dõi công việc (D-DOC-05), **không** là nguồn yêu cầu hay quyết định. Trạng thái từng Task chỉ ghi ở [phase-04-authentication-profile.md](phase-04-authentication-profile.md). Lập 2026-11-03.

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Mã, tên | F01 — Xác thực và hồ sơ người dùng |
| Người phụ trách | **Tuấn** (D-OWN-01, D-OWN-02, `docs/decisions.md` §2) |
| Reviewer | Chưa phân công (không có căn cứ) |
| Đặc tả | [`docs/modules/auth-profile.md`](../../docs/modules/auth-profile.md) — SPEC CONFIRMED, còn PENDING (§10); kịch bản test [`auth-profile.tests.md`](../../docs/modules/auth-profile.tests.md) |
| Skill | `.claude/skills/auth-profile/SKILL.md` |
| Căn cứ, quyết định, điểm chờ | [ba-decisions-and-safe-defaults.md](ba-decisions-and-safe-defaults.md) |
| Trạng thái tổng hợp (03/11/2026) | 22 Task: NOT_STARTED 14 · BLOCKED 8 — đếm từ file phase, không phải nguồn trạng thái |

## 2. Mục tiêu

Tài khoản, xác thực (đăng ký, đăng nhập, làm mới phiên, đăng xuất, quên, đặt lại, đổi mật khẩu), hồ sơ và kỹ năng hiện có của người dùng, theo `docs/modules/auth-profile.md` §1. Kết quả: API §2 (`docs/api-endpoints.md`), 3 bảng (`User`, `UserSkill`, `PasswordResetToken`), các trang `/login` … `/me/skills`, `tests/test_auth.py`.

## 3. Phạm vi

**Trong:** `/api/auth/*`, `/api/me`, `/api/me/avatar`, `/api/me/change-password`, `/api/me/summary`, `/api/me/skills`; `core/security.py`, `core/dependencies.py` (dùng chung mọi module), `core/email.py`; `scripts/create_admin.py`.

**Ngoài:** `/api/me/courses*`, `/api/me/bookmarks*`, `join` (F03, F04); `/api/me/review-history*` (F09); `/api/me/learning-paths` (F05); bảng RefreshToken chỉ tạo khi ND-43 được duyệt.

## 4. Mức độ sẵn sàng triển khai (kiểm tra 03/11/2026)

### 4.1. Điều kiện nền dùng chung (không thuộc F01, quản lý ở `plans/plan.md`)

| Task | Nội dung | Status | Chặn bởi | Ảnh hưởng tới F01 |
|---|---|---|---|---|
| P00-T02 | Chốt cổng, tên database | NOT_STARTED | — (cần nhóm quyết định) | Không chạy được migration, test |
| P00-T03 | Chốt sync/async, lớp commit | NOT_STARTED | ND-16 | Chữ ký repository, service |
| P00-T04 | Chốt thư viện JWT, Argon2id | NOT_STARTED | ND-44, ND-45 | Chặn `security.py` → login, `get_current_user`, admin |
| P01-T03 | `core/database.py` | BLOCKED | ND-16 | Không có session DB |
| P01-T05 | Alembic | BLOCKED | P01-T03, P00-T02 | Không có migration |
| P01-T08 | Hạ tầng test backend | BLOCKED | P01-T03, P01-T05; DB test chưa quy định | Viết được test, chưa chạy được |
| P03-T03, T04, T05 | API client, layout, component dùng chung (Chưa phân công) | NOT_STARTED | — | Trang F01 cần các phần này |

**Kết luận:** không có phần nào của F01 chạy được **đầu-cuối** (API + DB + test) cho tới khi P00-T02, P00-T03, P00-T04 được quyết định và P01-T03, P01-T05, P01-T08 xong. Phần **viết code không phụ thuộc** các mục trên làm được ngay (mục 4.3).

### 4.2. Đánh giá theo từng phần

Cột tiêu chí: ✓ có căn cứ · ◐ có nhưng còn điểm chờ · ✗ thiếu hoặc bị chặn. Cột "Kết luận backend/frontend" dùng nhãn mức sẵn sàng triển khai theo D-DOC-07 (`NOT_READY_BLOCKED` khác trạng thái Task `BLOCKED`); giới hạn của từng dòng nằm ở các cột tiêu chí ◐, ✗ cùng dòng.

| Phần | Nghiệp vụ | AC | UI | API | DB | Bảo mật | Validation | Test | Phụ thuộc | Kết luận backend | Kết luận frontend |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Login** (`POST /api/auth/login`) | ✓ FR-02, UC-01 | ✓ AC-01 | ✓ Main, Main-LampOff | ◐ hình dạng response ND-19, ND-41 | ◐ User ✓; RefreshToken PROPOSED (ND-43) | ◐ D-AUTH-01, 02, 04 ✓; thư viện ND-44, ND-45 | ✓ (không áp chính sách mật khẩu) | ✓ AP-T11 … T14 (AP-T10 chờ) | ✗ P04-T02 | `NOT_READY_BLOCKED` | `READY_WITH_LIMITATIONS` |
| **Logout** (`POST /api/auth/logout`) | ✓ FR-02, FR-46 | ✓ AC-01 | ◐ Logout (route ND-50) | ✗ ND-48, ND-41 | ✗ RefreshToken (ND-43) | ◐ D-AUTH-03 ✓; chi tiết ND-40 … 43, 48 | — | ✗ AP-T30, T31 đều chờ | ✗ P04-T06, T07 | `NOT_READY_BLOCKED` | `READY_WITH_LIMITATIONS` |
| **Profile — xem** (`GET /api/me`) | ✓ FR-03 | ◐ AC-01 (xác thực) | ✓ Profile, Profile-Light | ✓ §4.6 đủ | ✓ §3.1 | ◐ cần `get_current_user` (ND-44) | — | ✓ AP-T50, T51 | ✗ P04-T03 | `READY_WITH_LIMITATIONS` | `READY_WITH_LIMITATIONS` |
| **Profile — sửa** (`PATCH /api/me`) | ◐ FR-03 khác dữ liệu (ND-10) | ◐ | ✓ EditProfile | ◐ ND-18 (trường thừa), ND-12 (URL) | ✓ | ◐ như trên | ◐ ND-12, ND-18 | ◐ AP-T52, T53 chờ | ✗ P04-T03 | `READY_WITH_LIMITATIONS` | `READY_WITH_LIMITATIONS` |
| Profile — số liệu (`GET /api/me/summary`) | ◐ T05 | — | ✓ Profile | ✓ §4.10 | ✗ cần `StudentCourse`, `LearningPath` (F04, F05) | — | — | — | ✗ ND-13; P06-T04, P07-T04 | `NOT_READY_BLOCKED` | `READY_WITH_LIMITATIONS` (mock) |
| Profile — ảnh đại diện (`POST /api/me/avatar`) | ◐ D07, T04 | — | ✓ EditProfile | ✗ ND-12, ND-62 | ✓ `avatar_url` | ◐ | ✗ ND-12 | — | ✗ ND-62 | `NOT_READY_BLOCKED` | `NOT_READY_BLOCKED` (ND-62, ND-12; mục 4.3 xếp avatar vào phần "chờ") |
| Đổi mật khẩu | ✓ T03 | — | ✓ ChangePassword | ✓ §4.9 | ✓ | ◐ cần băm (ND-45) | ◐ ND-46, ND-47 | ✓ trong §6 | ✗ P04-T02, T03 | `READY_WITH_LIMITATIONS` | `READY_WITH_LIMITATIONS` |
| Kỹ năng của tôi | ✓ FR-04 | — | ✓ Skills | ✓ §4.11, §4.12 | ✓ §3.2 | ◐ | ◐ ND-09, 11, 64 | ✓ AP-T70 … 81 (3 chờ) | ✗ P04-T03; danh mục cho học viên ND-57 | `READY_WITH_LIMITATIONS` | `READY_WITH_LIMITATIONS` |
| Đăng ký | ✓ FR-01 | ✓ AC-01 | ◐ Register (ND-56) | ◐ ND-08 (trả token?), ND-37, ND-47 | ✓ | ◐ băm ND-45 | ◐ ND-46 | ✓ AP-T01, 03 … 05; AP-T101 … | ✗ P04-T02 | `READY_WITH_LIMITATIONS` | `READY_WITH_LIMITATIONS` |
| Quên, đặt lại mật khẩu | ✓ D09, T01, T02 | — | ✓ 4 màn | ✓ §4.4, §4.5 | ✓ §3.4 | ✓ AP-R09 … R11 | ◐ ND-46, ND-47 | ✓ AP-T40 … 47 | ◐ ND-39; định dạng link chứa mã chưa có | `READY_WITH_LIMITATIONS` | `NEEDS_OWNER_INPUT` (định dạng link chứa mã chưa có — câu hỏi cho Tuấn (D-OWN-01, D-OWN-02): route và tham số của liên kết đặt lại mật khẩu là gì?) |
| Làm mới phiên (`refresh`) | ✓ FR-45, FR-46 | ✓ AC-01 | — | ✗ bản nháp (ND-48) | ✗ ND-43 | ◐ D-AUTH-03 | — | ◐ AP-T32, 35 … 37 | ✗ ND-40 … 43, 48 | `NOT_READY_BLOCKED` | `NOT_READY_BLOCKED` (D-FE-05: chưa triển khai refresh cho tới khi ND-41, ND-48 được chốt) |
| Tạo admin (`scripts/create_admin.py`) | ✓ T09, AP-R05 | — | — | — | ✓ | ◐ băm ND-45 | — | — | ✗ P04-T02 | `NOT_READY_BLOCKED` | — (không áp dụng: admin tạo bằng script, không qua giao diện — T09; SRS v2.0 §1.4) |

**Không có phần nào `READY_FOR_IMPLEMENTATION` đầy đủ.** Lý do chung: nền P01 và thư viện bảo mật chưa chốt.

### 4.3. Phần làm được ngay (không phụ thuộc quyết định đang chờ)

Theo cột Blocker "Phần làm được" của các Task (không đổi Status):

| Thứ tự | Task | Phần làm được ngay | Không làm (chờ) |
|---|---|---|---|
| 1 | P04-T01 | Đối chiếu đặc tả với BA FR-01 … 04, FR-40 … 46, AC-01 và SRS-AUTH, SRS-PROF; ghi điểm lệch | — |
| 2 | P04-T04 | Class model `User`, `UserSkill`, `PasswordResetToken` theo `database-design.md` §3.1, §3.2, §3.4 | Migration (P01-T05); RefreshToken (ND-43) |
| 3 | P04-T02 (BLOCKED) | Hàm kiểm chính sách mật khẩu AP-R19 (1)–(5); (7) theo cách hiểu hẹp phải chờ | Ký tự đặc biệt, định nghĩa khoảng trắng (ND-46); băm, JWT (ND-44, ND-45) |
| 4 | P04-T05, T09, T12 | Schema Pydantic vào/ra theo §4.1, §4.6, §4.7, §4.9, §4.11, §4.12; kiểm trùng email (AP-R02) | Chữ ký repository, service theo sync/async (ND-16); xác thực request (P04-T03) |
| 5 | P04-T14 | Viết test cho kịch bản không có cột "Chờ" | Chạy test (P01-T08) |
| 6 | P04-T15 … T21 | Sau khi có P03-T03 … T05: trang dùng chế độ mock (D-FE-07), không làm refresh (D-FE-05) | Câu chữ khẳng định quy tắc chưa chốt (ND-51); avatar (ND-62) |

### 4.4. Quyết định cần có để mở khóa

| Quyết định | Mở khóa |
|---|---|
| ND-44 (thư viện JWT), ND-45 (thư viện, tham số Argon2id) — qua P00-T04 | P04-T02 → P04-T03, T06, T13; chạy P04-T05, T08, T09, T12 |
| ND-16 (sync/async), cổng, tên DB — qua P00-T02, P00-T03 | P01-T03, T05, T08 → migration, chạy test |
| ND-19, ND-41 | Hình dạng response login |
| ND-40, 41, 42, 43, 48 | P04-T07 (refresh, logout) |
| ND-46, ND-47 | Hoàn thiện chính sách mật khẩu, `confirm_password` |
| ND-13 | P04-T11 |
| ND-12, ND-62 | P04-T10 |

## 5. Phase và Task

| Phase | File | Task |
|---|---|---|
| P04 | [phase-04-authentication-profile.md](phase-04-authentication-profile.md) | P04-T01 … P04-T22 (bảng Task + hướng dẫn chi tiết từng Task) |

Phase dùng chung P00–P03, P13: [`plans/plan.md`](../plan.md).

## 6. Phụ thuộc ra ngoài tính năng

| Task F01 | Phụ thuộc | Thuộc |
|---|---|---|
| P04-T02 | P01-T02, P00-T04 | dùng chung |
| P04-T04 | P01-T05, P02-T02 | dùng chung |
| P04-T11 | P06-T04, P07-T04 | F04, F05 |
| P04-T14 | P01-T08 | dùng chung |
| P04-T15 | P03-T03 | dùng chung |
| P04-T16 | P03-T04, P03-T05 | dùng chung |

Tính năng khác phụ thuộc F01: `get_current_user`, `require_admin` (P04-T03) dùng cho F02 … F14; `UserSkill` được F04 (`join`), F09 (nộp bài) ghi.

## 7. Việc người phụ trách cần làm (`NEEDS_OWNER_INPUT`)

1. Đưa ND-44, ND-45 (P00-T04) và ND-16, cổng, tên DB (P00-T02, P00-T03) ra nhóm quyết định — đây là điểm mở khóa lớn nhất.
2. Chốt định dạng link chứa mã đặt lại mật khẩu (`structure.md` §3 chưa có) — ảnh hưởng P04-T08, P04-T17.
3. Quyết định ai làm P03-T03 … T05 (Chưa phân công), vì các trang F01 phụ thuộc.
4. Đưa mã SRS-AUTH-01 … 07, SRS-PROF-01 … 05 vào đặc tả (`auth-profile.md` §1).

## 8. Điều kiện hoàn thành và bằng chứng

- Task không bị chặn DONE có Evidence và kết quả review; Task BLOCKED ghi rõ mã chặn (P04 mục 7).
- Kiểm tra AP-R01 … R23 theo Review Checklist ở file phase.
- Bằng chứng: commit hoặc PR; kết quả `pytest tests/test_auth.py`; ảnh các trang F01; với migration: kết quả `alembic upgrade head`.

## 9. Tài liệu nguồn

BA §6.1 (FR-01 … 04), §6.9 (FR-40 … 46), §10.2, UC-01, UC-02, AC-01, NFR-04, NFR-37 … 39; SRS §6.1, §6.2 (SRS-AUTH-01 … 07, SRS-PROF-01 … 05); `docs/decisions.md` D06 … D09, D-AUTH-01 … 05, T01 … T10, T28, §4.1; `docs/modules/auth-profile.md`, `.tests.md`; `docs/api-endpoints.md` §2; `docs/database-design.md` §3; `docs/backend-rules.md`; `docs/structure.md` §2, §3, §5; `docs/ui-design/` S-01 … S-11.
