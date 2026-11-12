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
| 4 | Quên / đặt lại mật khẩu | 11/11 → 11/11 | 07/11 | __/__ | [ ] |
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
- [x] **2.6 Nhờ Claude review FĐ2** — dự kiến 09/11 · thực tế 11/11 🤖 — K1, K4, K6, K7, K11 đạt (Chrome thật, script `scratchpad/shots/k_tests.mjs` — tạo tài khoản tạm qua form Đăng ký, xóa sau khi chạy)

## FĐ3 — Đăng nhập, đăng ký (10/11)

- [x] **3.1 `components/auth/AuthLayout.jsx` + `Lamp.jsx`** — dây kéo đèn: mở trang đèn tắt, form ẩn và khóa; kéo → sáng — dự kiến 10/11 · thực tế 07/11 — Claude viết (theo yêu cầu): CSS chép từ màn demo vào CSS Module; form bị khóa (inert) khi đèn tắt; điện thoại ẩn 2 đèn phụ
- [x] **3.2 `LoginPage.jsx`** — email, mật khẩu, hiện/ẩn mật khẩu; sai → "Lỗi 401: …" + rung form (`.shake`); đúng → `/me` (admin → trang quản trị khi có); liên kết Quên mật khẩu, Đăng ký — dự kiến 10/11 · thực tế 07/11 — Claude viết; + `TextField`, `PasswordField` (hiện/ẩn), `icons.jsx`; thông báo sau đăng ký / hết phiên; bỏ dòng "tài khoản demo"
- [x] **3.3 `RegisterPage.jsx`** — 4 ô; kiểm tra ngay trên form theo **cùng quy tắc mật khẩu với backend** (≥ 8 ký tự, hoa, thường, số, ký tự đặc biệt, ≤ 72 byte); hiện lỗi 409 / 422 từ server; thành công → `/login` điền sẵn email — dự kiến 10/11 · thực tế 07/11 — Claude viết; `utils/validators.js` khớp backend 13/13 mật khẩu thử; 409 → ô Email, 422 → đúng ô
- [x] **3.4 Thử theo bảng kiểm thử FĐ3 + nhờ Claude review** — dự kiến 10/11 · thực tế 11/11 🤖 — K2, K3, K5 đạt (Chrome thật). Lưu ý: trang Đăng nhập / Đăng ký có màn "kéo dây đèn để mở trang" (nhớ trong `sessionStorage`)

## FĐ4 — Quên / đặt lại mật khẩu (11/11)

- [x] **4.1 `ForgotPasswordPage.jsx` → `ForgotSentPage.jsx`** — luôn chuyển sang "đã gửi" (khớp backend luôn trả cùng thông báo) — dự kiến 11/11 · thực tế 07/11 — Claude viết (theo yêu cầu); `CenterLayout` (thanh trên + 2 đèn trang trí + thẻ giữa, theo demo); ForgotSent: gửi lại có đếm ngược 30 giây; bỏ link "mở thử (demo)"
- [x] **4.2 `ResetPasswordPage.jsx`** — lấy `token` từ URL (`useSearchParams`); hiện danh sách quy tắc mật khẩu; 400 → `/reset-expired`; thành công → `/login` + thông báo — dự kiến 11/11 · thực tế 07/11 — Claude viết; `PasswordRules` tích xanh khi gõ; thành công → logout phiên cũ trên máy (Q10) → /login kèm thông báo
  - Link trong email (terminal backend khi dev) dạng `http://localhost:5173/reset-password?token=...`.
- [x] **4.3 `ResetExpiredPage.jsx`** — nút gửi yêu cầu mới, quay lại đăng nhập — dự kiến 11/11 · thực tế 07/11 — Claude viết
**4.4 Thử + nhờ Claude review FĐ4** — dự kiến 11/11 · thực tế __/__ — build OK; chờ Tuấn kiểm thử tay (K8)

## FĐ5 — Hồ sơ (12/11)

- [x] **5.1 `ProfilePage.jsx`** — họ tên, email, vai trò, ngày tham gia, avatar (chữ cái đầu khi chưa có ảnh); phần thống kê / kỹ năng hiện "Đang cập nhật" đến FĐ6 — dự kiến 12/11 · thực tế 07/11 — Claude viết (theo yêu cầu): theo màn demo Profile; 4 ô thống kê tạm hiện "—" (chờ `/me/summary`); khối Khóa học / Kỹ năng / Ôn tập gần đây để module khác & FĐ6
- [x] **5.2 Công tắc Tối / Sáng** (FR-49) — dùng `utils/theme.js`, lưu trên trình duyệt — dự kiến 12/11 · thực tế 07/11 — Claude viết: `components/profile/ThemeToggle.jsx` (radio, phím ← →, theme lan từ điểm bấm); có ở trang Hồ sơ và menu Cài đặt
- [x] **5.3 `EditProfilePage.jsx`** — sửa họ tên (`PATCH /me`); email, vai trò, ngày tham gia chỉ đọc; **bấm avatar để đổi ảnh**: kiểm tra trước PNG/JPEG ≤ 5 MB, hiện lỗi 413 / 415 từ server; thông báo "Đã lưu" — dự kiến 12/11 · thực tế 07/11 — Claude viết; khung chung `SettingsLayout.jsx` (← Hồ sơ, menu trái, khung phải); chọn ảnh là tải lên ngay; lưu xong cập nhật Header
- [x] **5.4 `ChangePasswordPage.jsx`** — 3 ô + quy tắc; sai mật khẩu hiện tại → lỗi 400 trên form (không đăng xuất); thành công → backend đã thu hồi refresh token (Q10) → thông báo và **đăng xuất, về `/login`** — dự kiến 12/11 · thực tế 07/11 — Claude viết; thêm quy tắc "Khác mật khẩu hiện tại" (prop `notSameAs` của `PasswordRules`) — 08/11: backend cũng chặn (400 "Mật khẩu này đã được sử dụng." → hiện dưới ô Mật khẩu mới)
- [x] **5.5 `LogoutDialog.jsx`** — xác nhận → `POST /auth/logout` → xóa token → `/login` — dự kiến 12/11 · thực tế 07/11 — Claude viết: hộp thoại xác nhận (Esc / bấm nền / Hủy để đóng; con trỏ đặt sẵn ở Hủy)
- [x] **5.6 Thử + nhờ Claude review FĐ5** — dự kiến 12/11 · thực tế 11/11 🤖 — K9–K12 đạt (Chrome thật): ảnh PNG lưu; .txt và ảnh > 5 MB chặn ngay trên trình duyệt; .txt đổi đuôi .png → server 415

## FĐ6 — Kỹ năng, thống kê (13/11 — sau backend GĐ4, 7.2) — làm sớm 08/11 (GĐ4 xong 08/11)

- [x] **6.1 `SkillsPage.jsx`** — tìm kỹ năng trong danh mục, thêm, đổi Đã biết / Đang học, xóa, hoàn tác, **lưu tất cả một lần**, hiện "N thay đổi chưa lưu" — dự kiến 13/11 · thực tế 08/11 — Claude viết (theo yêu cầu): `features/profile/pages/SkillsPage.jsx` + `components/SkillSearch.jsx` (tìm qua `GET /api/skills` của Hòa, chờ 250 ms, ẩn kỹ năng đã có, ↑↓ Enter Esc) + `skillDraft.js` (bản nháp: thêm / đổi / gỡ / khôi phục → body PATCH) + `common/components/Tabs.jsx` (dùng chung, nền trượt). Lỗi 404/409 → nút "Tải lại"; báo lỗi bằng TÊN kỹ năng; đóng tab khi chưa lưu → trình duyệt hỏi lại; điện thoại ẩn cột Cập nhật. **08/11 thêm danh sách sổ xuống** (Tuấn yêu cầu — người dùng không nhớ hết tên kỹ năng): bấm ô / nút ▾ → "Gợi ý cho bạn" 3 nhóm Học tiếp / Liên quan / Phổ biến từ API mới `GET /api/me/skills/suggestions` (backend module 01, chỉ ĐỌC `skill_relation`, `course_skill` của Hòa; 4 test); gõ → kết quả tìm + "Xem thêm kết quả"; gợi ý tự cập nhật sau khi Lưu. Demo trình duyệt thật 11 bước (thêm 3, lưu, đổi + gỡ, tab, hoàn tác, gợi ý ẩn kỹ năng đã có, dữ liệu cũ → 404 không lưu gì → Tải lại, lưu lại, Hồ sơ cập nhật) — không lỗi console
- [x] **6.1b Trang "Khám phá kỹ năng" theo danh mục** (`/me/skills/browse`, gợi ý của thầy 08/11) — **Tuấn chốt giữ cách này (08/11)**: bỏ ô tìm có danh sách sổ xuống trên trang Kỹ năng (xóa `SkillSearch.jsx`, `api/skills.api.js`), thay bằng nút "Khám phá & thêm kỹ năng →". **Dải "Gợi ý cho bạn"** (Tuấn chọn 08/11) ở màn đầu trang Khám phá: 6 kỹ năng từ `GET /api/me/skills/suggestions` (Học tiếp / Liên quan / Phổ biến), chọn chung với lưới danh mục, tự đổi theo hồ sơ sau khi thêm — thực tế 08/11 — Claude viết (theo yêu cầu): bảng `skills` không có danh mục → backend tự phân loại theo từ khóa tên (`app/utils/skill_categories.py`, 14 danh mục + Khác, ~69% vào danh mục cụ thể, có cache); API `GET /api/me/skills/catalog/categories`, `GET /api/me/skills/catalog` (lọc danh mục, tìm, sắp Phổ biến / A–Z, phân trang, đánh dấu "Đã có"); 5 test. Frontend: chip danh mục + số lượng, lưới thẻ, chọn Đã biết / Đang học nhiều kỹ năng qua nhiều trang → "Thêm vào hồ sơ" một lần; danh mục / trang / chữ tìm trên URL (nút Back đúng); `common/components/Pagination.jsx` dùng chung; điện thoại: chip 1 hàng vuốt ngang, tự cuộn tới chip đang chọn. Demo trình duyệt thật: thêm 3 kỹ năng qua 3 màn → DB đúng, không lỗi console
- [ ] **6.2 Thống kê trên `ProfilePage`** — `GET /me/summary` — dự kiến 13/11 · thực tế __/__ — 08/11 làm trước phần có thể: ô "Kỹ năng đã biết" + khối "Kỹ năng của tôi" (`SkillsSummary.jsx`) dùng `GET /me/skills`; 3 ô còn lại chờ backend 7.2

## FĐ7 — Hoàn thiện (13/11)

- [x] **7.0a Trang "Tạm thời chưa khả dụng" cho `/me/skills`** (+ mục "Kỹ năng của tôi" trong menu Cài đặt) — thực tế 08/11 — Claude viết (theo yêu cầu): `components/common/ComingSoon.jsx` (icon, "Tính năng Kỹ năng của tôi đang được phát triển, sẽ sớm có", nút ← Về hồ sơ + Thử lại, dòng nhỏ "Mã: 501 · Chưa hỗ trợ"); chốt với Tuấn: KHÔNG dùng 500/503 cho tính năng chưa làm; FĐ6 thay bằng SkillsPage
- [x] **7.0b Trang 503 "Máy chủ tạm thời không phục vụ"** — thực tế 08/11 — Claude viết: `pages/ServerErrorPage.jsx` + `StatusPanel.jsx` dùng chung (404 cũng dùng); **sửa lỗi**: trước đây backend tắt → `GET /me` lỗi → bị xóa token (đăng xuất oan). Nay: 401/403 → về khách; mất mạng / 5xx → giữ token, hiện 503 + Thử lại (`authStore.retry`). `client.js`: refresh lỗi mạng / 5xx không còn đăng xuất. Đã thử: backend tắt → proxy Vite trả 500 rỗng → vào nhánh 503
- [x] **7.0c Cảnh 3D ánh sáng chuyển động** (Đăng nhập / Đăng ký / Quên mật khẩu, theo ảnh demo Tuấn gửi) — thực tế 08/11 — Claude viết (theo yêu cầu): `components/auth/AuthScene.jsx` CSS + SVG thuần (không GIF, không thư viện): 3 ô kính nổi 3D (mũ, sách, play) nghiêng + vệt sáng lướt, sóng ánh sáng chạy, hạt bụi sáng bay, bàn sách + chậu cây đung đưa; viền thẻ form sáng chạy vòng. Giữ dây kéo đèn: tắt đèn → cảnh tối mờ. Màn thấp / điện thoại tự bớt ô để không đè chữ. Chờ Tuấn xem chuyển động thật trên trình duyệt
- [x] **7.0d 3 khối "Đang cập nhật" trên Hồ sơ** — thực tế 08/11 — Claude viết (theo yêu cầu): `components/profile/PendingBlock.jsx`; Khóa học của tôi (chờ module khóa học), Kỹ năng của tôi + link Quản lý (chờ GĐ4 → FĐ6), Ôn tập gần đây (chờ module 09); bố cục theo demo (trái rộng / phải 320px, màn hẹp 1 cột). Có API → thay PendingBlock bằng dữ liệu thật
- [x] **7.0e Header + Footer** — thực tế 08/11 — Claude viết (theo yêu cầu), Tuấn sẽ chỉnh theo ý: Header theo demo (logo, menu Khóa học / Lộ trình / Khóa học của tôi / Ôn tập / AI Tutor / Liên hệ, gạch chân vàng mục đang mở, admin thêm Quản trị, avatar + tên; điện thoại menu vuốt ngang). Footer (demo chưa có → bản đề xuất): giới thiệu + 3 cột liên kết + bản quyền + Lên đầu trang. Menu khai báo 1 chỗ `components/layout/nav.js`; trang nhóm khác chưa làm → route tạm "Tạm thời chưa khả dụng"
- [x] **7.0f Trang chủ cho khách `/`** (theo mockup Tuấn gửi) — thực tế 08/11 — Claude viết (theo yêu cầu): `pages/home/` — header khách (neo #, mục đang xem tô vàng), hero + thẻ bắt đầu nhanh (Đăng ký / Đăng nhập: nhận họ tên + email rồi chuyển sang trang đầy đủ, điền sẵn), 3 bước, 6 tính năng, lộ trình mẫu, Khóa học nổi bật, Tin nổi bật, kêu gọi đăng ký, Footer dùng chung (`guest`). Khối hiện dần khi cuộn. **Khóa học / Tin nổi bật là DỮ LIỆU MẪU** (`homeContent.js`) — chờ API khóa học. Đã đăng nhập vào `/` → `/me`; logo trang Đăng nhập / Đăng ký / Quên mật khẩu dẫn về `/`. Header khách dùng chung `components/layout/PublicHeader.jsx` cho cả trang chủ, Đăng nhập, Đăng ký, Quên mật khẩu (trang khác bấm mục → về `/#id`)
- [x] **7.0g Đồng bộ nền + chuyển động** — thực tế 08/11 — Claude viết (theo yêu cầu): Đăng nhập / Đăng ký dùng nền liền + quầng sáng như trang chủ, khung 1200px thẳng hàng header (màn rộng), sửa màu ô khi trình duyệt tự điền (autofill); trang đã đăng nhập: `PageBackdrop` (quầng sáng thở, vầng sáng trôi, hạt bụi), header khung 1200px + vệt sáng chạy + vòng sáng avatar, Hồ sơ: khối trượt lên lần lượt, viền sáng chạy quanh thẻ hồ sơ, ô thống kê nhấp nháy chờ dữ liệu, khối "Đang cập nhật" icon lơ lửng + vệt sáng lướt
- [x] **7.0h Sắp xếp lại CSS / thư mục (phương án A)** — thực tế 08/11 — Claude làm (theo yêu cầu): `src/styles/` (CSS dùng chung tách 9 file) + `src/features/<tính năng>/{pages,components,styles}`; giao diện kiểm chứng giống hệt (xem `SetUp-CSS.md` §7); hướng dẫn `frontend/src/features/README.md`
- [ ] **7.1 Kiểm thử thủ công theo bảng dưới**, so với ảnh demo — dự kiến 13/11 · thực tế __/__ — 11/11 🤖 chạy **K1–K15 + W1, W8, W10 = 18/18 đạt** trên Chrome thật, không lỗi JS. 👤 Còn: Tuấn **so giao diện với ảnh demo** (ảnh chụp từng bước trong `scratchpad/shots/k/`)
  - 11/11 🤖 **So 13 màn với ảnh demo** (khổ 1440, ảnh ghép demo | app thật: `scratchpad/shots/ui/cmp/`). Khác biệt **có chủ đích** (đã quyết trước): header khách + nền hiệu ứng + Footer; bỏ dòng "tài khoản demo / mật khẩu demo"; 6 quy tắc mật khẩu; ảnh tối đa 5 MB (Q8); thêm kỹ năng qua trang Khám phá; hộp Đăng xuất 2 nút ngang, con trỏ ở Hủy; nút Back dạng icon.
  - ✅ **11/11 Tuấn quyết + Claude sửa** (1) theo demo, (2) nối dữ liệu thật, (3) thêm hết, (4) **để sau**. Đã làm: `AuthLayout` thêm `variant="register"` (câu chào riêng, không danh sách tính năng); `RecentReviews.jsx` (3 lượt mới nhất từ `GET /me/review-history?size=3`: khóa · ngày · Đạt/Chưa đạt · điểm /10, bấm → trang kết quả, "Xem tất cả" → Lịch sử); icon Bút chì / Khóa / Đăng xuất trên 3 nút Hồ sơ (`PencilIcon`, `LogoutIcon` mới trong `icons.jsx`); mũi tên → trên "Gửi yêu cầu", 2 nút "Lưu thay đổi"; nhãn "Ảnh đại diện". Kiểm: ảnh ghép `scratchpad/shots/ui2/cmp/`, build OK, K1–K15 chạy lại 18/18. **Còn (4) Footer — để sau.** Chi tiết lệch ban đầu: (1) Trang **Đăng ký** dùng lại câu chào của Đăng nhập — demo: "Bắt đầu hành trình học tập của bạn." + "Tạo tài khoản học viên miễn phí để lưu khóa học, theo dõi lộ trình và ghi nhận kỹ năng."; (2) Hồ sơ → khối **"Ôn tập gần đây"** còn "Đang cập nhật" — module 09 đã có dữ liệu (`GET /me/review-history?size=3`), hiện điểm **/10** thay cho "85% · 17/20 câu" của demo; (3) thiếu icon trên nút Chỉnh sửa hồ sơ / Đổi mật khẩu / Đăng xuất (Hồ sơ), mũi tên → trên "Gửi yêu cầu", "Lưu thay đổi", nhãn "Ảnh đại diện" (Sửa hồ sơ); (4) Footer: liên hệ / địa chỉ còn chữ giữ chỗ ("Cập nhật tên trường / đơn vị") — cần Tuấn cung cấp.
  - Chờ module khác: "Khóa học của tôi" + 3 ô thống kê (Khôi, Hòa — bước 6.2/7.2); nút chat nổi (Tâm).
- [x] **7.2 Giao diện hẹp (điện thoại)**, chế độ Sáng, trạng thái đang tải / lỗi mạng — dự kiến 13/11 · thực tế 08/11 — Claude kiểm bằng Chrome headless ở 375 / 768 / 1280 px (8 trang): **không trang nào tràn ngang**; sửa: menu Cài đặt trên điện thoại bị che mục (cuộn ngang ẩn) → xuống dòng; Đổi mật khẩu trên điện thoại: quy tắc nằm dưới nút Lưu → đưa lên ngay dưới ô nhập; thống kê Hồ sơ 1 → 2 cột; Header thêm `-webkit-backdrop-filter` (Safari < 18); font dự phòng có dấu tiếng Việt khi không tải được Google Fonts; reset `img max-width`, `text-size-adjust`. Còn chờ: Tuấn thử trên điện thoại thật + Firefox / Safari (nếu có)
- [x] **7.3 `npm run build`** không lỗi — dự kiến 13/11 · thực tế 11/11 🤖 (sửa chữ "Ôn tập 20 câu" → **15 câu** theo quyết định 09/11 ở trang Đăng nhập / Đăng ký và trang chủ)
- [ ] **7.4 Commit, báo nhóm phần nền dùng chung** (`client.js`, `authStore`, route, layout) — dự kiến 13/11 · thực tế __/__

## FĐ8 — Header mới + trang cài đặt (11–12/11) — chi tiết ở `Review-Auth.md` GĐ9 (9.1–9.11)

- [x] **8.1 Chuông thông báo** `layout/components/NotificationBell.jsx` — số chưa đọc (99+), khung 2 tab Tất cả / Chưa đọc, đọc 1 / đọc hết, hỏi lại 60 giây; điện thoại trải ngang — thực tế 11/11 🤖
- [x] **8.2 Menu avatar** `layout/components/UserMenu.jsx` — rê chuột / bấm / bàn phím; mục: Hồ sơ của tôi · Cài đặt tài khoản (→ `/me/password`) · Giao diện · Thông báo qua email · (admin) Quản trị · Đăng xuất (nút riêng ở giữa). Logo → `/courses` — thực tế 11–12/11 🤖
- [x] **8.3 Trang Giao diện** `/me/appearance` — Tối / Sáng / Theo hệ thống, cỡ chữ (`--reading-scale`, chỉ nội dung câu hỏi ôn tập), giảm chuyển động; lưu localStorage (`utils/theme.js`) — thực tế 12/11 🤖
- [x] **8.4 Trang Thông báo qua email** `/me/email-notifications` — 3 công tắc lưu ngay lên máy chủ — thực tế 12/11 🤖
- [x] **8.5 Trang Sửa hồ sơ** thêm ngày sinh, giới tính, quê quán, SĐT, CCCD (chỉ hiện bản che) — thực tế 12/11 🤖
- [x] **8.6 Trang Hồ sơ gọn lại** — chỉ còn nút Chỉnh sửa hồ sơ (bỏ công tắc giao diện, Đổi mật khẩu, Đăng xuất); "Ôn tập gần đây" dữ liệu thật — thực tế 11–12/11 🤖
- Kiểm thử Chrome thật (script trong scratchpad): `bell_menu.mjs` 11/11 · `prefs.mjs` 8/8 · `profile_info.mjs` 5/5 · `k_tests.mjs` (K1–K15) 18/18. K12 nay đổi giao diện ở trang Giao diện.

---

## Bảng kiểm thử thủ công

| # | Thao tác | Mong đợi | FĐ | Đạt |
|---|---|---|---|---|
| K1 | Vào `/me` khi chưa đăng nhập | Chuyển `/login` | 2 | ✅ 11/11 |
| K2 | Đăng nhập sai | "Lỗi 401: …", form rung | 3 | ✅ 11/11 |
| K3 | Đăng nhập đúng | Vào `/me`, header có tên | 3 | ✅ 11/11 |
| K4 | Đã đăng nhập, vào `/login` | Chuyển `/me` | 2 | ✅ 11/11 |
| K5 | Đăng ký email đã có / mật khẩu yếu / xác nhận lệch | Lỗi hiện đúng ô | 3 | ✅ 11/11 |
| K6 | Tải lại trang (F5) khi đang đăng nhập | Vẫn đăng nhập | 2 | ✅ 11/11 |
| K7 | Để access token hết hạn (hoặc sửa tạm `ACCESS_TOKEN_EXPIRE_MINUTES=1`) rồi thao tác | Tự refresh, không bị đá ra | 1 | ✅ 11/11 (token hỏng → tự refresh, xoay refresh token) |
| K8 | Quên mật khẩu → mở link trong terminal backend → đặt lại → dùng lại link | Lần 2 sang ResetExpired | 4 | ✅ 11/11 (link lấy từ service, không qua email) |
| K9 | Sửa họ tên, đổi ảnh PNG/JPEG; thử file .txt và ảnh > 5 MB; thử file .txt đổi đuôi thành .png | Lưu được; báo lỗi trên trình duyệt; file giả .png → server báo 415 | 5 | ✅ 11/11 |
| K10 | Đổi mật khẩu sai / đúng | Sai: lỗi trên form; đúng: về `/login` | 5 | ✅ 11/11 |
| K11 | Đăng xuất, bấm Back của trình duyệt | Không vào lại được `/me` | 5 | ✅ 11/11 |
| K12 | Đổi Tối / Sáng, tải lại trang | Giữ lựa chọn | 5 | ✅ 11/11 |
| K13 | Cài đặt → "Kỹ năng của tôi": thêm 2 kỹ năng, đổi 1, gỡ 1, bấm Hoàn tác; làm lại rồi Lưu tất cả; F5 | Thanh "N thay đổi chưa lưu" đúng số; Hoàn tác về như cũ; lưu xong F5 vẫn còn; Hồ sơ hiện đúng kỹ năng + số "Kỹ năng đã biết" | 6 | ✅ 11/11 (thêm kỹ năng qua trang Khám phá chưa kiểm — script thêm bằng API) |
| K14 | Đang đăng nhập → tắt backend (Ctrl+C) → F5 → bật lại backend → bấm "Thử lại" | Trang 503, KHÔNG bị đăng xuất; Thử lại → vào lại `/me` | 7 | ✅ 11/11 (chặn `/api` trong trình duyệt thay cho tắt backend) |
| K15 | Gõ URL lạ, vd `/abc` | Trang 404 "Không tìm thấy trang" | 7 | ✅ 11/11 |

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
| 11/11 | K1–K15 chạy trên Chrome thật 18/18; so 13 màn với ảnh demo, sửa theo quyết định Tuấn (Footer để sau); chuông + menu avatar (FĐ8) | Trang Đăng nhập / Đăng ký có màn "kéo dây đèn" — script kiểm phải bật đèn trước |
| 12/11 | Trang Giao diện, Thông báo qua email, thông tin cá nhân; Hồ sơ chỉ còn nút Chỉnh sửa hồ sơ | — |
| | | |
