---
name: auth-profile
description: Điểm vào cho mọi việc thuộc module Xác thực & Hồ sơ người dùng của project EduMentor AI — register, login, logout, JWT, forgot-password, reset-password, change-password, GET/PATCH /api/me, /api/me/avatar, /api/me/summary, GET/PATCH /api/me/skills, bảng User/UserSkill/PasswordResetToken, core/security.py, core/dependencies.py (get_current_user, require_admin). Dùng skill này mỗi khi implement, sửa, review hoặc viết test cho các phần trên, kể cả khi người dùng chỉ nói "làm đăng nhập", "sửa hồ sơ", "kỹ năng của tôi", "quên mật khẩu" hay mở các file routers/auth.py, routers/me.py, services/auth_service.py, services/user_service.py. Ưu tiên skill này hơn skill cấp user edumentor-auth-profile khi làm việc trong repo này.
---

# Auth & Profile — EduMentor AI

Skill này là **điểm vào**: nó cho biết phạm vi, cần đọc gì và không được làm gì. Nội dung nghiệp vụ nằm trong tài liệu dưới đây — đọc chúng, đừng làm theo trí nhớ, vì quy tắc đã được nhóm chốt và có thể khác với cách làm "thông thường".

## 1. Đọc trước khi làm (theo thứ tự)

1. `docs/modules/auth-profile.md` — phạm vi, file, dữ liệu, API contract (§4), quy tắc `AP-Rxx` (§5), luồng, transaction, bảo mật. **Nguồn chi tiết chính.**
2. `docs/decisions.md` — quyết định đã chốt (D06, D07, D08, D09…) và danh sách `[NEEDS DECISION]` §4.1, §4.3.
3. `docs/backend-rules.md` — phân lớp, cấu trúc lỗi, 401/403/404, transaction, cấu hình, email.
4. `docs/database-design.md` §3.1, §3.2, §3.4 — khi đụng tới model hoặc migration.
5. `docs/modules/auth-profile.tests.md` — khi viết hoặc sửa test.

Chỉ đọc phần liên quan tới việc đang làm; không cần đọc hết mọi file cho một thay đổi nhỏ.

## 2. Phạm vi

**Được làm:** `routers/auth.py`, `routers/me.py`, `schemas/auth.py`, `schemas/user.py`, `models/user.py`, `models/user_skill.py`, `models/password_reset_token.py`, `services/auth_service.py`, `services/user_service.py`, repository tương ứng, `core/security.py`, `core/dependencies.py`, `core/email.py` (dùng chung với module Ôn tập), `tests/test_auth.py`, migration Alembic cho 3 bảng của module.

**Không thuộc phạm vi — không tự sửa:** `/api/me/courses*`, `/api/me/bookmarks*`, `join` (Course Tracking); `/api/me/review-history*` (skill `review-assessment`); `/api/me/learning-paths`; mọi `/api/admin/*`. Nếu việc đang làm cần thay đổi ở đó, nêu ra cho người dùng thay vì tự sửa.

## 3. Quy tắc bắt buộc

Chi tiết và nguồn ở `auth-profile.md` §5; đây là những điểm hay bị làm sai:

- `register` luôn tạo `student`; không bao giờ nhận `role` từ client (AP-R01). Admin chỉ tạo bằng `scripts/create_admin.py`.
- `PATCH /api/me` chỉ nhận `full_name`, `avatar_url` — không đổi được `email`, `role` (AP-R03, AP-R04).
- Không lưu mật khẩu gốc; không trả `hashed_password` ở bất kỳ response nào (AP-R06).
- Logout = JWT stateless, server trả 200, **không** tạo bảng thu hồi token (D08).
- `forgot-password` trả **cùng một** thông báo dù email có tồn tại hay không (AP-R09). Mã đặt lại chỉ lưu bản băm, có hạn, dùng một lần; đặt lại xong thì vô hiệu mã cũ (AP-R10, AP-R11).
- `PATCH /api/me/skills` theo đúng body `add`/`update`/`remove`, một transaction, upsert khi `add` trùng, `skill_id` không tồn tại → 404 và rollback (AP-R14).
- `/api/me*` lấy người dùng từ token, không nhận `user_id` (AP-R18).
- Router không chứa truy vấn hay nghiệp vụ; service giữ transaction; mọi thay đổi schema qua Alembic.

## 4. Không được làm

- Không tự chọn phương án cho mục `[NEEDS DECISION]` (thuật toán JWT/hash, thời hạn token, refresh token, chính sách mật khẩu, rate-limit, chuẩn hóa email, giới hạn 3 kỹ năng, upload avatar…). Gặp chúng thì **dừng và hỏi người dùng**, hoặc chỉ làm phần không phụ thuộc rồi ghi rõ chỗ còn chờ.
- Không thêm endpoint, bảng, cột, ràng buộc ngoài `docs/`. Wireframe không phải nguồn quy tắc API.
- Không thêm cơ chế xác thực mới (OAuth, session server, blacklist token…).
- Không coi hạng mục ☐ trong `docs/decisions.md` §3 là đã chốt.

## 5. Quy trình implement

1. Xác định endpoint/quy tắc liên quan trong `auth-profile.md`; liệt kê các `ND-xx` ảnh hưởng. Nếu có ND chặn đường → hỏi trước.
2. Model + migration khớp `database-design.md` (bảng thật `users`).
3. Schema Pydantic: request chỉ chứa trường được phép; response không chứa trường nhạy cảm.
4. Repository (chỉ truy vấn) → Service (quy tắc + transaction) → Router (dependency `get_current_user`, gọi service, trả response/lỗi theo `backend-rules.md` §4).
5. Viết test theo `auth-profile.tests.md`; kịch bản có cột "Chờ" thì bỏ qua cho tới khi ND được chốt.
6. Chạy `pytest`, `black`, `ruff`.
7. Nếu phát hiện tài liệu thiếu/mâu thuẫn: không tự vá bằng code — đề xuất thêm `ND-xx` vào `docs/decisions.md`.

## 6. Kỳ vọng kiểm thử

Tối thiểu phải có test cho: register (thành công, trùng email, không nhận role), login (đúng/sai), 401 khi thiếu/sai token, 403 cho endpoint admin với student, forgot-password trả cùng thông báo, reset-password (thành công, hết hạn, đã dùng, mã sai), change-password sai mật khẩu hiện tại, `PATCH /api/me` không đổi email/role, `PATCH /api/me/skills` rollback khi một `skill_id` không tồn tại, và không response nào chứa `hashed_password`.

## 7. Liên hệ với module khác

- Module Ôn tập ghi `UserSkill = known` khi học viên làm đạt (T13) và dùng chung `core/email.py` — giữ chữ ký `send_email` ổn định.
- Course Tracking ghi `UserSkill = learning` khi `join` (D05) — ownership vẫn thuộc Course Tracking.
- Mọi module dùng `get_current_user`/`require_admin` — đổi hành vi của chúng là thay đổi toàn hệ thống, cần hỏi trước.
