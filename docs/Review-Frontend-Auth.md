# Review-Frontend-Auth — Kế hoạch frontend React module Tài khoản & Hồ sơ (F01)

> Người thực hiện: **Tuấn** · Người review: **Claude** · Bắt đầu: **08/11/2026** · Dự kiến xong: **13/11/2026**
> Backend tương ứng: `docs/Review-Auth.md` (10/13 API xong — 70 test). Sau frontend này: Ôn tập (`docs/Review-Assessment.md`).
> Công nghệ (đã dựng sẵn trong `frontend/`): **React 18 + Vite 6**, **react-router-dom 6**, **axios**, JavaScript (`.jsx`). Không thêm thư viện giao diện — dùng `src/index.css` (class `.btn`, `.card`, `.field`, `.field-error`, `.alert`, `.shake`… + biến màu Tối/Sáng) và `src/utils/theme.js`.
> Chuẩn giao diện: bộ demo `docs/EduMentor-UI-design/ui-design/` (mở `index.html`, lọc "01 · Tuấn").
> Cách dùng: làm xong việc nào thì tích `[x]` và điền **ngày thực tế**. Hết mỗi giai đoạn, nhắn "review FĐ x" để Claude review.

---

## Tổng quan tiến độ

| FĐ | Nội dung | Dự kiến | Thực tế bắt đầu | Thực tế xong | Xong |
|---|---|---|---|---|---|
| 0 | Chuẩn bị: cài đặt, chạy Vite, kết nối backend | 08/11 → 08/11 | 07/11 | 07/11 | [x] |
| 1 | Nền gọi API: `client.js` (gắn token, tự refresh khi 401) | 08/11 → 08/11 | 07/11 | 07/11 | [x] |
| 2 | Trạng thái đăng nhập + route bảo vệ + layout | 09/11 → 09/11 | 07/11 | __/__ | [ ] |
| 3 | Đăng nhập, đăng ký (dây kéo đèn) | 10/11 → 10/11 | 07/11 | __/__ | [ ] |
| 4 | Quên / đặt lại mật khẩu | 11/11 → 11/11 | __/__ | __/__ | [ ] |
| 5 | Hồ sơ, sửa hồ sơ + ảnh đại diện, đổi mật khẩu, đăng xuất, Tối/Sáng | 12/11 → 12/11 | __/__ | __/__ | [ ] |
| 6 | Kỹ năng của tôi, thống kê hồ sơ (sau backend GĐ4, 7.2) | 13/11 → 13/11 | __/__ | __/__ | [ ] |
| 7 | Hoàn thiện, kiểm thử thủ công, build | 13/11 → 13/11 | __/__ | __/__ | [ ] |

📅 09/11: buổi thảo luận Ôn tập (xem `docs/Review-Assessment.md`) — FĐ2 vẫn làm trong ngày.

---

## Màn hình và API (module 01)

| Màn demo | Route | Trang (file) | API | Backend | FĐ |
|---|---|---|---|---|---|
| Main, Main-LampOff | `/login` | `pages/auth/LoginPage.jsx` | `POST /api/auth/login` | ✅ | 3 |
| Register | `/register` | `pages/auth/RegisterPage.jsx` | `POST /api/auth/register` | ✅ | 3 |
| ForgotPassword | `/forgot-password` | `pages/auth/ForgotPasswordPage.jsx` | `POST /api/auth/forgot-password` | ✅ | 4 |
| ForgotSent | `/forgot-sent` | `pages/auth/ForgotSentPage.jsx` | — | — | 4 |
| ResetPassword | `/reset-password?token=` | `pages/auth/ResetPasswordPage.jsx` | `POST /api/auth/reset-password` | ✅ | 4 |
| ResetExpired | `/reset-expired` | `pages/auth/ResetExpiredPage.jsx` | — | — | 4 |
| Profile, Profile-Light | `/me` | `pages/profile/ProfilePage.jsx` | `GET /api/me` (+ `/me/summary`, `/me/skills` sau) | ✅ / ⏳ | 5, 6 |
| EditProfile | `/me/edit` | `pages/profile/EditProfilePage.jsx` | `PATCH /api/me`, `POST /api/me/avatar` | ✅ | 5 |
| ChangePassword | `/me/password` | `pages/profile/ChangePasswordPage.jsx` | `POST /api/me/change-password` | ✅ | 5 |
| Logout (hộp thoại) | trên `/me` | `components/profile/LogoutDialog.jsx` | `POST /api/auth/logout` | ✅ | 5 |
| Skills | `/me/skills` | `pages/profile/SkillsPage.jsx` | `GET`/`PATCH /api/me/skills` | ⏳ GĐ4 | 6 |
| (tự động) | — | `api/client.js` | `POST /api/auth/refresh` | ✅ | 1 |

Đặt tên trang theo quy ước đã có trong repo: `XxxPage.jsx`.

---

## FĐ0 — Chuẩn bị (08/11)

- [x] **0.1 Cài thư viện, chạy Vite** — dự kiến 08/11 · thực tế 07/11 ✔ Claude đã review
  - `cd frontend` → `npm install` → `npm run dev` → mở `http://localhost:5173` thấy trang giữ chỗ "EduMentor AI".
- [x] **0.2 Kết nối backend** — dự kiến 08/11 · thực tế 07/11 ✔ Claude đã review — proxy `/api` + `/uploads` → :8000; health qua 5173 trả connected (FQ2: dùng proxy)
  - Cấu hình **proxy** trong `vite.config.js`: `/api` và `/uploads` → `http://localhost:8000` (trình duyệt coi như cùng nguồn → không vướng CORS; ảnh đại diện `/uploads/...` hiển thị được).
  - ✅ Xong khi: `fetch("/api/health/health")` trong Console trình duyệt trả `database: connected`.
- [ ] **0.3 Đọc nhanh `index.css` và `utils/theme.js`** — biết class nào dùng cho nút, thẻ, ô nhập, thông báo lỗi — dự kiến 08/11 · thực tế __/__
- [x] **0.4 Bài tập React đầu tiên: `components/common/BackendStatus.jsx`** (useState + useEffect, gọi `/api/health/health` qua proxy) — thực tế 07/11 ✔ Claude đã review. Claude sửa: các `if/return` nằm ngoài hàm (lỗi "return outside of function"), sai đường dẫn `/api/health` (404), class `.ok`/`.error` không có trong index.css → `.alert-ok`/`.alert`, chưa gắn vào `App.jsx`. `npm run build` OK.

## FĐ1 — Nền gọi API (08/11)

- [x] **1.1 `api/client.js`** — axios instance `baseURL: "/api"` — dự kiến 08/11 · thực tế 07/11 — Claude viết (theo yêu cầu) + `api/tokenStorage.js` (FQ1 gói một chỗ)
  - Interceptor **request**: gắn `Authorization: Bearer <access_token>`.
  - Interceptor **response**: gặp **401** → gọi `POST /auth/refresh` **một lần** → lưu cặp token mới → gửi lại request cũ. Refresh thất bại → xóa token, chuyển `/login`.
  - Nhiều request cùng 401 một lúc → chỉ refresh **một lần**, các request khác chờ (tránh tự kích hoạt "phát hiện dùng lại" của backend → bị đăng xuất mọi nơi).
- [x] **1.2 `utils/errors.js`** — đổi lỗi FastAPI thành câu tiếng Việt: `detail` dạng chuỗi (401/409/400…) hoặc danh sách (422, bỏ tiền tố "Value error, ") — dự kiến 08/11 · thực tế 07/11 — Claude viết: `parseApiError` → { status, message, fieldErrors }
- [x] **1.3 `api/auth.api.js`, `api/me.api.js`** — mỗi API backend một hàm — dự kiến 08/11 · thực tế 07/11 — Claude viết
- [x] **1.4 Nhờ Claude review FĐ1** — dự kiến 08/11 · thực tế 07/11 — 16/16 kịch bản chạy thật với backend (Node): tự gắn Bearer, 401 → refresh → gửi lại, 5 request song song chỉ refresh 1 lần (không kích hoạt thu hồi mọi phiên), logout → hết phiên, lỗi 409/422/415/mất mạng

## FĐ2 — Trạng thái đăng nhập, route, layout (09/11)

- [x] **2.1 `store/authStore.js`** — React Context: `user`, `login()`, `logout()`, `refreshUser()`; khi mở app có token → `GET /me` để biết ai đang đăng nhập — dự kiến 09/11 · thực tế 07/11 — Claude viết (theo yêu cầu); file .js nên dùng createElement; nối `setOnSessionExpired` của client.js → về /login
- [x] **2.2 `hooks/useAuth.js`** — lấy nhanh dữ liệu từ Context — dự kiến 09/11 · thực tế 07/11 — Claude viết
- [x] **2.3 `routes/index.jsx` + `PublicRoute` / `ProtectedRoute` / `AdminRoute`** — dự kiến 09/11 · thực tế 07/11 — Claude viết (+ `FullPageLoading`, `NotFoundPage`, trang quản trị giữ chỗ)
  - Chưa đăng nhập vào `/me` → về `/login`; đã đăng nhập vào `/login` → về `/me`; student vào `/admin/*` → chặn.
  - Bản demo **không** kiểm tra đăng nhập — bản thật phải có (và backend vẫn là lớp chặn chính — NFR-05).
- [x] **2.4 `components/layout/Header.jsx`, `PageLayout.jsx`** — tên + avatar người dùng, liên kết hồ sơ — dự kiến 09/11 · thực tế 07/11 — Claude viết (+ `Header.module.css`, `utils/formatters.js`: initials, formatDate, roleLabel)
- [x] **2.5 `App.jsx`** — bọc `AuthProvider` + router — dự kiến 09/11 · thực tế 07/11 — Claude viết. LoginPage / ProfilePage là BẢN TẠM để kiểm tra luồng (FĐ3, FĐ5 làm lại)
- [ ] **2.6 Nhờ Claude review FĐ2** — dự kiến 09/11 · thực tế __/__ — build OK; chờ Tuấn kiểm thử tay K1, K4, K6, K11 trên trình duyệt

## FĐ3 — Đăng nhập, đăng ký (10/11)

- [x] **3.1 `components/auth/AuthLayout.jsx` + `Lamp.jsx`** — dây kéo đèn: mở trang đèn tắt, form ẩn và khóa; kéo → sáng — dự kiến 10/11 · thực tế 07/11 — Claude viết (theo yêu cầu): CSS chép từ màn demo vào CSS Module; form bị khóa (inert) khi đèn tắt; điện thoại ẩn 2 đèn phụ
- [x] **3.2 `LoginPage.jsx`** — email, mật khẩu, hiện/ẩn mật khẩu; sai → "Lỗi 401: …" + rung form (`.shake`); đúng → `/me` (admin → trang quản trị khi có); liên kết Quên mật khẩu, Đăng ký — dự kiến 10/11 · thực tế 07/11 — Claude viết; + `TextField`, `PasswordField` (hiện/ẩn), `icons.jsx`; thông báo sau đăng ký / hết phiên; bỏ dòng "tài khoản demo"
- [x] **3.3 `RegisterPage.jsx`** — 4 ô; kiểm tra ngay trên form theo **cùng quy tắc mật khẩu với backend** (≥ 8 ký tự, hoa, thường, số, ký tự đặc biệt, ≤ 72 byte); hiện lỗi 409 / 422 từ server; thành công → `/login` điền sẵn email — dự kiến 10/11 · thực tế 07/11 — Claude viết; `utils/validators.js` khớp backend 13/13 mật khẩu thử; 409 → ô Email, 422 → đúng ô
- [ ] **3.4 Thử theo bảng kiểm thử FĐ3 + nhờ Claude review** — dự kiến 10/11 · thực tế __/__ — build OK; chờ Tuấn kiểm thử tay trên trình duyệt (K2, K3, K5)

## FĐ4 — Quên / đặt lại mật khẩu (11/11)

- [ ] **4.1 `ForgotPasswordPage.jsx` → `ForgotSentPage.jsx`** — luôn chuyển sang "đã gửi" (khớp backend luôn trả cùng thông báo) — dự kiến 11/11 · thực tế __/__
- [ ] **4.2 `ResetPasswordPage.jsx`** — lấy `token` từ URL (`useSearchParams`); hiện danh sách quy tắc mật khẩu; 400 → `/reset-expired`; thành công → `/login` + thông báo — dự kiến 11/11 · thực tế __/__
  - Link trong email (terminal backend khi dev) dạng `http://localhost:5173/reset-password?token=...`.
- [ ] **4.3 `ResetExpiredPage.jsx`** — nút gửi yêu cầu mới, quay lại đăng nhập — dự kiến 11/11 · thực tế __/__
- [ ] **4.4 Thử + nhờ Claude review FĐ4** — dự kiến 11/11 · thực tế __/__

## FĐ5 — Hồ sơ (12/11)

- [ ] **5.1 `ProfilePage.jsx`** — họ tên, email, vai trò, ngày tham gia, avatar (chữ cái đầu khi chưa có ảnh); phần thống kê / kỹ năng hiện "Đang cập nhật" đến FĐ6 — dự kiến 12/11 · thực tế __/__
- [ ] **5.2 Công tắc Tối / Sáng** (FR-49) — dùng `utils/theme.js`, lưu trên trình duyệt — dự kiến 12/11 · thực tế __/__
- [ ] **5.3 `EditProfilePage.jsx`** — sửa họ tên (`PATCH /me`); email, vai trò, ngày tham gia chỉ đọc; **bấm avatar để đổi ảnh**: kiểm tra trước PNG/JPEG ≤ 5 MB, hiện lỗi 413 / 415 từ server; thông báo "Đã lưu" — dự kiến 12/11 · thực tế __/__
- [ ] **5.4 `ChangePasswordPage.jsx`** — 3 ô + quy tắc; sai mật khẩu hiện tại → lỗi 400 trên form (không đăng xuất); thành công → backend đã thu hồi refresh token (Q10) → thông báo và **đăng xuất, về `/login`** — dự kiến 12/11 · thực tế __/__
- [ ] **5.5 `LogoutDialog.jsx`** — xác nhận → `POST /auth/logout` → xóa token → `/login` — dự kiến 12/11 · thực tế __/__
- [ ] **5.6 Thử + nhờ Claude review FĐ5** — dự kiến 12/11 · thực tế __/__

## FĐ6 — Kỹ năng, thống kê (13/11 — sau backend GĐ4, 7.2)

- [ ] **6.1 `SkillsPage.jsx`** — tìm kỹ năng trong danh mục, thêm, đổi Đã biết / Đang học, xóa, hoàn tác, **lưu tất cả một lần**, hiện "N thay đổi chưa lưu" — dự kiến 13/11 · thực tế __/__
- [ ] **6.2 Thống kê trên `ProfilePage`** — `GET /me/summary` — dự kiến 13/11 · thực tế __/__

## FĐ7 — Hoàn thiện (13/11)

- [ ] **7.1 Kiểm thử thủ công theo bảng dưới**, so với ảnh demo — dự kiến 13/11 · thực tế __/__
- [ ] **7.2 Giao diện hẹp (điện thoại)**, chế độ Sáng, trạng thái đang tải / lỗi mạng — dự kiến 13/11 · thực tế __/__
- [ ] **7.3 `npm run build`** không lỗi — dự kiến 13/11 · thực tế __/__
- [ ] **7.4 Commit, báo nhóm phần nền dùng chung** (`client.js`, `authStore`, route, layout) — dự kiến 13/11 · thực tế __/__

---

## Bảng kiểm thử thủ công

| # | Thao tác | Mong đợi | FĐ | Đạt |
|---|---|---|---|---|
| K1 | Vào `/me` khi chưa đăng nhập | Chuyển `/login` | 2 | [ ] |
| K2 | Đăng nhập sai | "Lỗi 401: …", form rung | 3 | [ ] |
| K3 | Đăng nhập đúng | Vào `/me`, header có tên | 3 | [ ] |
| K4 | Đã đăng nhập, vào `/login` | Chuyển `/me` | 2 | [ ] |
| K5 | Đăng ký email đã có / mật khẩu yếu / xác nhận lệch | Lỗi hiện đúng ô | 3 | [ ] |
| K6 | Tải lại trang (F5) khi đang đăng nhập | Vẫn đăng nhập | 2 | [ ] |
| K7 | Để access token hết hạn (hoặc sửa tạm `ACCESS_TOKEN_EXPIRE_MINUTES=1`) rồi thao tác | Tự refresh, không bị đá ra | 1 | [ ] |
| K8 | Quên mật khẩu → mở link trong terminal backend → đặt lại → dùng lại link | Lần 2 sang ResetExpired | 4 | [ ] |
| K9 | Sửa họ tên, đổi ảnh PNG/JPEG; thử file .txt và ảnh > 5 MB | Lưu được; báo lỗi 415 / 413 | 5 | [ ] |
| K10 | Đổi mật khẩu sai / đúng | Sai: lỗi trên form; đúng: về `/login` | 5 | [ ] |
| K11 | Đăng xuất, bấm Back của trình duyệt | Không vào lại được `/me` | 5 | [ ] |
| K12 | Đổi Tối / Sáng, tải lại trang | Giữ lựa chọn | 5 | [ ] |

---

## Câu hỏi cần chốt

| # | Câu hỏi | Cần trước FĐ | Đề xuất | Trả lời | Ngày chốt |
|---|---|---|---|---|---|
| FQ1 | Lưu token ở đâu trên trình duyệt? | 1 | `localStorage` (giữ đăng nhập khi đóng tab — đúng ý "refresh token 7 ngày"); rủi ro XSS chấp nhận ở đồ án (đã ghi ở Q7 backend) | | |
| FQ2 | Gọi backend bằng **proxy Vite** hay thêm `localhost:5173` vào `ALLOWED_ORIGINS` (CORS)? | 0 | **Proxy** — không sửa backend, ảnh `/uploads` cũng chạy | | |
| FQ3 | CSS: chỉ dùng class chung `index.css`, hay thêm **CSS Modules** (`*.module.css`) cho từng trang? | 3 | `index.css` + CSS Module riêng cho phần đặc thù (dây kéo đèn, avatar) | Áp dụng ở FĐ2–FĐ3 (Header, AuthLayout, Lamp, PasswordField) | 07/11 |
| FQ4 | Phần nền dùng chung (`client.js`, `authStore`, route, layout) — Tuấn làm, nhóm dùng theo? | 1 | Có — báo nhóm trước khi bắt đầu để không làm trùng | | |
| FQ5 | Đăng nhập bằng admin → chuyển trang nào? (trang quản trị là của Khôi / Tâm / Hòa) | 3 | Tạm về `/me` đến khi có trang quản trị | | |
| FQ6 | Có viết test tự động cho frontend (Vitest) không? | 7 | Không ở đồ án — kiểm thử thủ công theo bảng K1–K12 | | |

## Nhật ký

| Ngày | Đã làm | Vướng mắc |
|---|---|---|
| 07/11 | Lập kế hoạch frontend module 01 | — |
| | | |
