# FRONTEND SYNC AUDIT — Demo → Production (Phase A)

> Ngày audit: 2026-10-28 · Nhánh làm việc: `docs/initial-project-documentation` · Chỉ đọc, chưa sửa `frontend/`, backend hay CSDL.
> Báo cáo này là **đầu vào để duyệt Phase B**. Mọi điểm "CẦN QUYẾT ĐỊNH" (mục G) phải được chốt trước khi code.

---

## 0. Trạng thái nguồn — đọc trước

| Nguồn theo yêu cầu | Trạng thái thực tế | Đã dùng gì thay thế |
|---|---|---|
| `docs/ui-animation/demo/edumentor-demo-react/` | **KHÔNG TỒN TẠI** trong working tree, trong mọi nhánh local, `origin/main`, `origin/develop`, `origin/docs/initial-project-documentation`, `origin/Hoa` (đã `git fetch origin Hoa` để kiểm tra, không checkout) | Bản build một file **`EduMentor AI Demo.html`** do người dùng gửi kèm trong hội thoại (bundle Vite đã minify: React 18.3.1, react-router-dom 6.30.6, axios, CSS Modules đã hash). File này **không nằm trong repo** |
| `docs/ui-animation/demo/edumentor-ui-demo.html` | **KHÔNG TỒN TẠI** trong repo | Như trên (nhiều khả năng chính là file gửi kèm) |
| `docs/ui-animation/UX-UI-ANIMATION-PREVIEW.md` | **KHÔNG TỒN TẠI** | Không có thay thế — các token chuyển động lấy từ `:root` trong bundle |
| `README.md` | Có (bản repo). Người dùng gửi kèm **`README (1).md`** — bản khác, mô tả demo React, cấu trúc frontend mới, M1–M4, phân công | Đọc cả hai; bản gửi kèm **chưa có trong repo** |
| `STRUCTURE.md`, `CONVENTIONS.md` | Đã chuyển thành `docs/structure.md`, `docs/conventions.md` (task trước). Người dùng gửi kèm **`STRUCTURE (1).md`** — bản cũ (đặt ở root, ôn tập theo kỹ năng, trỏ frontend sang README) | Đọc bản repo + bản gửi kèm |
| `SETUP.md`, `docs/api-endpoints.md`, `docs/database-design.md`, `docs/decisions.md`, `docs/modules/*` | Có, đã đọc | — |
| `frontend/` | Có, **69/69 file rỗng (0 byte)** | — |
| `docs/EduMentor-UI-design/` | Có trong repo: 29 trang **HTML tĩnh** + PNG + `pages.json` (bản prototype khác, cũ hơn) | Ghi nhận ở mục G (hai nguồn UI) |

**Hệ quả:** không thể đối chiếu theo **file nguồn** của demo (tên file `.jsx`, `.module.css`, cách chia thư mục). Những gì dưới đây lấy từ bundle (đọc được: tên component, route, props, mock API, client, CSS đã hash, token) và từ `README (1).md`. Mục nào không kiểm chứng được ghi **[KHÔNG KIỂM CHỨNG]**.

---

## A. Cấu trúc demo (suy ra từ bundle + `README (1).md`)

### A1. Routes (đọc trực tiếp từ bundle, `<Routes>`)

| Route | Trang | Ghi chú |
|---|---|---|
| `/` → `/login` | redirect | |
| `/login`, `/register`, `/forgot-password`, `/forgot-sent`, `/reset-password`, `/reset-expired` | Auth | `forgot-sent`, `reset-expired` là màn trạng thái |
| `/me`, `/me/edit`, `/me/password`, `/me/skills` | Profile / Settings | |
| `/logout` | Profile + mở dialog đăng xuất | **deep-link cho demo** |
| `/courses`, `/courses/:courseId` | Catalog | |
| `/courses/:courseId/join` | Course detail + mở JoinDialog | **deep-link cho demo** |
| `/me/courses` | Tracking | |
| `/consultant`, `/me/learning-paths`, `/learning-paths/:pathId` | Path | |
| `/learning-paths/:pathId/edit` | Path detail + mở PathEditDialog | **deep-link cho demo** |
| `/tutor` | Tutor | |
| `/courses/:courseId/review`, `/courses/:courseId/review/attempt`, `/review-result/:attemptId`, `/me/review-history`, `/me/review-history/:attemptId` | Review | |
| `/contact`, `/contact-guest` | Feedback | `contact-guest` = biến thể chưa đăng nhập |
| `/admin` → `/admin/courses`, `/admin/courses`, `/admin/skills`, `/admin/base-paths`, `/admin/historical`, `/admin/feedback`, `/admin/user-paths` | Admin | |
| `*` → `/login` | fallback | |

Router: demo dùng **`MemoryRouter`** (`initialEntries: ["/login"]`) khi build một file; `README (1).md` nói biến `VITE_ROUTER`. → Production phải dùng `BrowserRouter`.

**Không có guard đăng nhập / admin nào** trong demo: mọi route (kể cả `/admin/*`) đều vào được.

### A2. Pages (tên lấy từ `README (1).md`, đối chiếu hành vi trong bundle)

| Nhóm | Trang |
|---|---|
| `pages/auth` | LoginPage, RegisterPage, ForgotPasswordPage, ForgotSentPage, ResetPasswordPage, ResetExpiredPage |
| `pages/profile` | ProfilePage, EditProfilePage, ChangePasswordPage, SkillsPage |
| `pages/catalog` | CatalogPage, CourseDetailPage |
| `pages/tracking` | MyCoursesPage |
| `pages/path` | ConsultantPage, MyPathsPage, PathDetailPage |
| `pages/tutor` | TutorPage |
| `pages/review` | ReviewStartPage, ReviewAttemptPage, ReviewResultPage, ReviewHistoryPage, ReviewDetailPage |
| `pages/feedback` | FeedbackPage (2 biến thể) |
| `pages/admin` | AdminCoursesPage, AdminSkillsPage (+ SkillRelationMap), AdminBasePathsPage, AdminHistoricalPage, AdminFeedbackPage, AdminUserPathsPage |

### A3. Components (README (1) + xác nhận hành vi trong bundle)

| Nhóm | Component | Hành vi chính (từ bundle) |
|---|---|---|
| layout | Header, PageLayout, AuthLayout (split/center), SettingsLayout, AdminLayout, HangingLamp, PullLamp, Logo | Header: nav 6 mục + avatar; PullLamp kéo/nhấn bật-tắt, `aria-pressed`, pointer + click; HangingLamp `aria-hidden`, ẩn < 720px |
| common | Button (`loading` spinner), Modal (portal, focus trap, Esc, khóa scroll), ConfirmDialog, Toast (ToastProvider, tối đa 3, 4 s), Tabs (pill trượt, phím ←/→), ErrorMessage, AnimatedNumber (rAF, tôn trọng reduced-motion), PasswordInput (ẩn/hiện), PasswordRules, ThemeToggle (View Transitions + fallback), Icons | |
| course | CourseCard, CourseCardFace, CourseCover (ảnh hoặc ảnh sinh từ hash tên), CourseFilters, CardOpening (CardOpeningProvider), JoinDialog | CardOpening: hiệu ứng "mở sách" 3D bằng **Web Animations API**, khóa scroll, bỏ qua khi reduced-motion, rồi `navigate` |
| path | PathGraph (SVG + node tuyệt đối, mũi tên, highlight node chọn), PathEditDialog | Có hàm tự xếp layout theo cấp (dùng khi node không có x,y) |
| profile | LogoutDialog | |
| chat | ChatBubble | FAB: GitHub, Zalo, Liên hệ, **AI tư vấn khóa học** (panel chat); ẩn ở `/admin`, `/tutor`, `/consultant`, trang làm bài |
| demo | DemoNav (`components/demo/`) | "33 màn hình demo", công tắc giảm chuyển động, **giả lập lỗi mạng** — **DEMO ONLY** |

### A4. API layer, mock, state, utils, config

| Hạng mục | Demo |
|---|---|
| `api/client.js` | `axios.create({ baseURL: "", timeout: 15000 })`; request interceptor đọc **`localStorage["access_token"]`** → `Authorization: Bearer`; response interceptor trả `res.data`, lỗi chuẩn hóa `{status, message}` (ưu tiên `error.message` → `detail` → `message`) |
| Các module `*.api.js` | Trong bản build, **mọi hàm đều đọc/ghi `mock/db.js`** (có `await delay`) — không có lời gọi HTTP thật nào tới backend |
| `mock/` | `db.js` (user, courses, tracking, userSkills, paths, sessions, attempts, inProgress, skillRelations, basePaths, historical), `feedback.js` |
| State | Không có store toàn cục; state cục bộ trong page; auth = `localStorage.access_token`; `ToastContext`, `CardOpeningContext` |
| `utils/theme.js` | `localStorage["em-theme"]` (`dark` mặc định), áp `data-theme` **trước khi render** (`main.jsx`) → không nháy theme |
| Motion | `localStorage["em-motion"]` → `data-motion="reduce|full"`; CSS global vô hiệu animation khi `prefers-reduced-motion` hoặc `data-motion=reduce`; JS có `prefersReducedMotion()` |
| `utils/formatters.js` | định dạng số `vi-VN`, rating 1 chữ số, nhãn trạng thái |
| `config/links.js` | URL GitHub, Zalo (đang là `https://github.com/`, `https://zalo.me/` — placeholder) |
| Styles | `index.css`: design tokens `:root` (dark) + `:root[data-theme=light]`, motion tokens (`--d-*`, `--e-*`), class dùng chung (`.btn`, `.card`, `.chip`, `.input`, `.table`, `.stagger`, `.enter`, `.page-in`…); mỗi component một `*.module.css` (bundle có class hash, xác nhận CSS Modules) |
| Assets | Không có ảnh; icon SVG inline; font **Be Vietnam Pro** từ Google Fonts |
| Thư viện thấy trong bundle | react 18.3.1, react-dom 18.3.1, react-router-dom 6.30.6, axios (chuỗi phiên bản trong bundle: 1.21.0) — **không** có thư viện animation |

---

## B. Frontend production hiện tại

`frontend/` có **69 file, tất cả 0 byte**: `package.json`, `vite.config.js`, `index.html`, `.env`, `src/main.jsx`, `App.jsx`, `index.css`; `routes/` (index, ProtectedRoute, AdminRoute); `api/` (client + 12 file); `store/authStore.js`; `hooks/` (useAuth, useCourseStatus, usePagination); `utils/` (constants, formatters); `pages/` (auth ×2, profile ×1, catalog ×2, learning-path ×3, tutor ×1, review ×3, admin ×5); `components/` (layout ×3, common ×4, course ×3, learning-path ×4, profile ×6, chat ×2, review ×2).

Cấu trúc này khớp `docs/structure.md` (bản repo), **không** khớp cấu trúc demo trong `README (1).md`. Không có code nào để giữ lại; chỉ có **tên file/thư mục**.

`frontend/.env` đang **được Git theo dõi** và `.gitignore` rỗng (đã ghi nhận ở task trước; nhánh `Hoa` có thêm `.gitignore` 19 dòng — chưa merge).

---

## C. Mapping demo → production

### C1. Thư mục

| Demo | Production hiện tại (`docs/structure.md`) | Đề xuất |
|---|---|---|
| `pages/path/` | `pages/learning-path/` | **CẦN QUYẾT ĐỊNH G2** |
| `pages/tracking/` | (không có; MyCourses nằm trong profile components) | tạo nếu chọn cấu trúc demo |
| `pages/feedback/` | (không có) | tạo — nhưng API pending (E) |
| `components/path/` | `components/learning-path/` | G2 |
| `components/review/` | `components/review/` (QuestionCard, ScoreSummary) | demo **không** có component review riêng (UI nằm trong page) |
| `config/` | (không có) | tạo |
| `mock/` | (không có) | tạo, tách hẳn khỏi `api/` (xem D) |
| `store/authStore.js`, `hooks/*` | có (rỗng) | demo không dùng store/hook riêng → G2 |
| `routes/ProtectedRoute.jsx`, `AdminRoute.jsx` | có (rỗng) | **giữ** — demo thiếu guard; yêu cầu Phase B bắt buộc có (mục 11–12 của task) |

### C2. Page

| Demo | Production file hiện có | Hành động |
|---|---|---|
| LoginPage, RegisterPage | `pages/auth/LoginPage.jsx`, `RegisterPage.jsx` | MODIFY |
| ForgotPasswordPage, ForgotSentPage, ResetPasswordPage, ResetExpiredPage | — | CREATE |
| ProfilePage | `pages/profile/ProfilePage.jsx` | MODIFY |
| EditProfilePage, ChangePasswordPage, SkillsPage | — (có `components/profile/ProfileEditForm`, `SkillList`) | CREATE page; component cũ → G2 |
| CatalogPage, CourseDetailPage | `pages/catalog/*` | MODIFY |
| MyCoursesPage | — (`components/profile/MyCoursesTabs`) | CREATE |
| ConsultantPage, MyPathsPage, PathDetailPage | `pages/learning-path/ConsultantChatPage`, `LearningPathListPage`, `LearningPathDetailPage` | MODIFY + đổi tên? (G2) |
| TutorPage | `pages/tutor/TutorPage.jsx` | MODIFY |
| ReviewStartPage, ReviewDetailPage | — | CREATE |
| ReviewAttemptPage, ReviewResultPage, ReviewHistoryPage | `pages/review/*` | MODIFY |
| FeedbackPage | — | CREATE (API pending) |
| AdminCoursesPage, AdminSkillsPage, AdminBasePathsPage, AdminHistoricalPage | `pages/admin/*` | MODIFY |
| (gộp trong AdminSkillsPage) | `pages/admin/AdminRelationsPage.jsx` | OBSOLETE nếu theo demo (G2) |
| AdminFeedbackPage, AdminUserPathsPage | — | CREATE (API pending) |

### C3. Component

| Demo | Production hiện có | Hành động |
|---|---|---|
| Header, PageLayout | `layout/Header`, `PageLayout` | MODIFY |
| AuthLayout, SettingsLayout, AdminLayout, HangingLamp, PullLamp, Logo | — | CREATE |
| (không có) | `layout/Sidebar.jsx` | OBSOLETE nếu theo demo |
| Button, Modal, ErrorMessage | `common/*` | MODIFY |
| ConfirmDialog, Toast, Tabs, AnimatedNumber, PasswordInput, PasswordRules, ThemeToggle, Icons | — | CREATE |
| (demo phân trang trong page) | `common/Pagination.jsx` | KEEP (API có `page/page_size`) |
| CourseCard, CourseFilters | `course/*` | MODIFY |
| CourseCardFace, CourseCover, CardOpening, JoinDialog | — | CREATE |
| (gộp vào CourseDetail/JoinDialog) | `course/CourseActions.jsx` | G2 |
| PathGraph | `learning-path/PathGraph.jsx` | MODIFY (+ vị trí thư mục G2) |
| PathEditDialog | — | CREATE |
| (gộp vào page) | `learning-path/NodeDetailPanel`, `NodeCoursePanel`, `ProposedPathPreview` | G2 |
| LogoutDialog | — | CREATE |
| (gộp vào ProfilePage) | `profile/ProfileHeader`, `ProfileEditForm`, `SkillList`, `CurrentPathCard`, `MyCoursesTabs`, `ReviewHistoryList` | G2 |
| ChatBubble | `chat/ChatWindow`, `MessageBubble` (cho Tutor) | CREATE ChatBubble; ChatWindow/MessageBubble → G2 |
| (gộp vào page) | `review/QuestionCard`, `ScoreSummary` | G2 |

### C4. CSS, API, state

| Demo | Production | Ghi chú |
|---|---|---|
| `index.css` (tokens, global classes, keyframes, reduced-motion) | `src/index.css` (rỗng) | CREATE theo demo — **giữ nguyên giá trị token** (đã đọc đủ từ bundle) |
| `*.module.css` theo từng page/component | chưa có | CREATE. **[KHÔNG KIỂM CHỨNG]** tên/phân chia file CSS gốc — chỉ có CSS đã hash trong bundle, có thể tái tạo nội dung nhưng không chắc khớp 1-1 file nguồn |
| `api/*.api.js` gọi mock | `api/*.api.js` (rỗng) | Viết lại bằng HTTP thật theo `docs/api-endpoints.md`; mock chuyển sang `mock/` và chỉ dùng khi `VITE_USE_MOCK=true` |
| `client.js` (localStorage token) | `api/client.js` | **CONFLICT G4** (D-AUTH-01: định hướng `sessionStorage`) |
| auth = localStorage | `store/authStore.js` | G2/G4 |
| `utils/theme.js`, `config/links.js` | — | CREATE |

---

## D. Phân loại file

| Phân loại | File |
|---|---|
| **EXISTING — KEEP** (giữ tên, chỉ điền code) | `package.json`, `vite.config.js`, `index.html`, `src/main.jsx`, `App.jsx`, `index.css`, `routes/index.jsx`, `routes/ProtectedRoute.jsx`, `routes/AdminRoute.jsx`, `api/client.js` + 11 module API khớp tên demo, `utils/constants.js`, `utils/formatters.js`, `common/Pagination.jsx` |
| **EXISTING — MODIFY** | các page/component ở C2/C3 có cột "MODIFY" |
| **PROPOSED — CREATE** | các page/component "CREATE" ở C2/C3; `config/links.js`, `utils/theme.js`, `mock/*`, `*.module.css`; API module mới chỉ khi có endpoint (xem E) |
| **DEMO ONLY — DO NOT COPY** | `components/demo/*` (DemoNav, 33 màn, giả lập lỗi mạng); `mock/db.js` vào luồng production; MemoryRouter; route deep-link `/logout`, `/courses/:id/join`, `/learning-paths/:id/edit`, `/contact-guest` (**G3**); email/mật khẩu demo điền sẵn ở Login ("nguyenvana@example.com", "Demo@123") và dòng "Mật khẩu hiện tại trong demo"; ngày tham gia/role hard-code ở Profile/EditProfile; link "Mở thử liên kết trong email (demo)"; câu trả lời AI soạn sẵn trong mock Consultant/Tutor/Advisor |
| **OBSOLETE — DO NOT USE** (nếu chọn cấu trúc demo, G2) | `layout/Sidebar.jsx`, `pages/admin/AdminRelationsPage.jsx`, `components/learning-path/*` (đổi sang `path/`), `profile/*` con, `review/*`, `chat/ChatWindow`, `MessageBubble`, `course/CourseActions`, `store/authStore.js`, `hooks/*` — **không xóa trong Phase B nếu chưa được duyệt** |

---

## E. API mismatch

Ký hiệu nguồn: **[API]** `docs/api-endpoints.md`, **[DB]** `docs/database-design.md`, **[D]** `docs/decisions.md`.

### E1. Endpoint chưa có trong [API]

| Demo cần | [API] | Ảnh hưởng | Mã |
|---|---|---|---|
| Lưu bài làm dở ("Tạm rời, làm tiếp sau") — demo lưu `answers` cục bộ | Không có endpoint lưu đáp án tạm; D03 chỉ trả lại bài dở | Đáp án chọn trước khi rời **mất** khi lên production | M1 |
| Gửi phản hồi, liên hệ khóa học, admin xem/lọc phản hồi (kèm `feedback_type`, từ khóa, `date_from/to`, sort) | Không có (T22–T25 chưa được tick, ND-35) | FeedbackPage, AdminFeedbackPage = **API PENDING** | M2 |
| Admin xem danh sách người dùng + lộ trình + trạng thái kỹ năng | Không có | AdminUserPathsPage = **API PENDING** | M3 |
| Chat "AI tư vấn khóa học" trong ChatBubble (khách + đã đăng nhập) | Không có (khác `/api/chat/learning-path` và `/api/chat/sessions`) | ChatBubble AI = **API PENDING** | M4 |
| Đổi tên lộ trình (`name`) | PATCH `/learning-paths/{id}` có, nhưng [DB] `LearningPath` **không có cột `name`** (chỉ `goal_text`) | Mismatch field | E-01 |
| Đếm "dùng N lần" của mẫu lộ trình (`used`) | [DB] `BaseLearningPath` không có | Mismatch field | E-02 |
| Dữ liệu lịch sử (`record_id`, `goal`, `skills`, `source`) | [API] §13 có, [DB] **không có bảng** (DB-2) | Mismatch | E-03 |

### E2. Endpoint có nhưng hợp đồng khác demo

| Demo | [API]/[DB]/[D] | Mismatch | Mã |
|---|---|---|---|
| `PATCH /me/skills` gửi `{add:[{skill, status}], update:[{skill,status}], remove:[skillName]}` — **theo tên kỹ năng** | T06: theo **`skill_id`** | Phải đổi sang `skill_id` | E-10 |
| `GET /me/skills` trả `{skill_id, skill, status, updated_at}` | khớp | — | |
| Login trả `{access_token, refresh_token, token_type, user}`, lưu `access_token` vào **localStorage** | D-AUTH-01: Bearer, frontend định hướng **sessionStorage**; ND-41/ND-48/ND-19 chưa chốt (refresh token body hay cookie) | **CONFLICT** lưu trữ + hợp đồng chưa chốt | E-11 |
| Demo **không có** `/api/auth/refresh` và không tự làm mới khi 401 | D-AUTH-02/03: bắt buộc refresh khi access token hết hạn | Thiếu luồng refresh | E-12 |
| Register gửi `{email, password, full_name}`; `confirm` chỉ kiểm phía client | ND-47 chưa chốt `confirm_password` | Có thể phải gửi thêm | E-13 |
| Reset password dùng token `"demo"` cố định | T02: token từ link email; **định dạng link (`?token=`) chưa có trong tài liệu** | Cần chốt dạng URL | E-14 |
| Upload avatar: tối đa **2 MB**, chỉ **JPG/PNG** (giá trị do demo tự đặt) | ND-12, AUD-06 **chưa chốt** | Không được coi là rule | E-15 |
| Khóa học có `platform`, `provider`, `level` tiếng Việt ("Cơ bản/Trung cấp/Nâng cao"), `skills[]` lồng | [DB] `Course`: `organization`, `level` ∈ `beginner/intermediate/advanced`, không có `platform`/`provider`; [API] chưa định nghĩa response list có kèm skills | Cần map field + nhãn | E-16 |
| Catalog lấy trạng thái từng khóa bằng **N lời gọi** `GET /me/courses/{id}/status` | [API] có endpoint đơn lẻ | Hiệu năng (không phải sai hợp đồng) | E-17 |
| `POST /courses/{id}/join` trả `url` (mock trả `null`) | [API] trả URL ngoài | Khớp ý; mock thiếu | |
| Câu hỏi khi làm bài có trường **`skill`** (hiện "Kỹ năng: X") | [API]/T15: chỉ `question_id, content, options, position` | Mismatch field (ND-27) | E-18 |
| Ngưỡng đạt **60 hard-code** trong frontend (`il=60`), điểm tính phía client trong mock | D02 = 60 nhưng đọc từ cấu hình server; điểm do server chấm | Frontend chỉ hiển thị giá trị server trả | E-19 |
| ReviewStart/Attempt/Result khẳng định "Câu bỏ trống được tính là sai", "Kết quả được gửi qua email" | T16 **BLOCKED** (RV-R10); ND-25 email mọi lần hay khi đạt **chưa chốt** | UI đang khẳng định rule chưa chốt | E-20 |
| Kết quả hiển thị `submitted_at`, `correct` | ND-31 (`submitted_at`) chưa chốt; [API] submit trả `score_percent, passed, số câu đúng` | Phụ thuộc ND-31 | E-21 |
| Review history phân trang **phía client** (6/trang) | [API] T17: `page`, `page_size` phía server | Đổi sang server | E-22 |
| `GET /courses/{id}/review` trả `{available, in_progress, reason: "not_joined"}` | [API]: `available` + lý do; `in_progress` **không có** trong [API] | Mismatch field (ND-33/ND-34 liên quan) | E-23 |
| Lộ trình: node có `x`, `y`; demo tự xếp layout nếu thiếu | [DB] node chỉ có `display_order` | Frontend phải tự xếp (demo đã có hàm) — OK nếu không gửi x,y | E-24 |
| Tutor: tin nhắn AI có `code`, `quiz` có cấu trúc; phiên có `title`, `when` | [DB] `ChatMessage.content` (text), `ChatSession.topic` | Mismatch (module Tutor) | E-25 |
| Profile/EditProfile hiển thị "Tham gia 12/10/2025", "Học viên" cố định | [API] `GET /me` có `created_at`, `role` | Phải lấy từ server | E-26 |
| Đổi mật khẩu: thêm rule "Khác mật khẩu hiện tại" | Không có trong D-AUTH-05 | Rule thêm ngoài tài liệu | E-27 |
| PasswordRules: ký tự đặc biệt = mọi ký tự không phải chữ/số (kể cả khoảng trắng, Unicode); không kiểm 128 byte, không kiểm khoảng trắng | D-AUTH-05 (≤128 byte UTF-8, không khoảng trắng); ND-46 chưa chốt tập ký tự | Lệch quy tắc đã chốt | E-28 |

---

## F. Xung đột với quy tắc / quyết định của project

| # | Xung đột | Nguồn | Mức |
|---|---|---|---|
| F-1 | **Phạm vi**: Phase B đồng bộ cả 14 tính năng, nhưng `CLAUDE.md` + D-OWN-01 giới hạn Claude ở Auth/Profile và Review của Tuấn; `README (1).md` giao Catalog/Admin cho Khôi, Bookmark/Tutor/Feedback cho Tâm, Path/Tracking/Admin quan hệ cho Hòa | CLAUDE.md, decisions §2 | **Cao** — cần xác nhận phạm vi (G1) |
| F-2 | **Hai cấu trúc frontend**: `docs/structure.md` (repo, có `ProtectedRoute/AdminRoute`, `store/`, `hooks/`, `learning-path/`) vs `README (1).md` (demo: `path/`, `tracking/`, `config/`, `mock/`, **bỏ** `ProtectedRoute/AdminRoute`) | structure.md vs README (1) | **Cao** (G2) |
| F-3 | **Hai bản README**: repo (đã cập nhật đường dẫn `docs/structure.md`, ôn tập theo khóa) vs `README (1).md` (trỏ `STRUCTURE.md`/`CONVENTIONS.md` ở root — đã bị chuyển) → merge sẽ xung đột | README | Trung bình |
| F-4 | **Hai nguồn UI**: `docs/EduMentor-UI-design/` (29 trang HTML trong repo) vs demo React (ngoài repo); `README (1).md` còn tuyên bố wireframe **không còn dùng**, trong khi nhiều ND tham chiếu wireframe (ND-05, 08, 09, 10, 27, 38) | README (1), decisions | Trung bình (G5) |
| F-5 | Token lưu **localStorage** (demo) vs **sessionStorage** (D-AUTH-01) | D-AUTH-01 | Cao (G4) |
| F-6 | Demo **không có guard** nào; task yêu cầu guard user/admin | task §11–12 | Thiết kế bắt buộc thêm, không phải redesign |
| F-7 | UI khẳng định rule BLOCKED/PENDING (E-20, E-15, E-27, E-28) | decisions | Cao — phải trung tính hóa câu chữ hoặc chờ chốt |
| F-8 | Nhánh `origin/Hoa` (PR #1) đổi backend: `routers/auth.py` → `routers/v1/__init__.py`, thêm `routers/v1/endpoints/health.py`, `docker-compose.yaml` bên cạnh `.yml` — lệch `docs/structure.md`; ảnh hưởng base URL API (`/api/v1`?) | origin/Hoa | Trung bình — ngoài frontend, nhưng quyết định prefix API ảnh hưởng `client.js` |

---

## G. Cần quyết định trước Phase B

| Mã | Câu hỏi |
|---|---|
| **G0** | **Commit mã nguồn demo** (`docs/ui-animation/demo/edumentor-demo-react/` + `edumentor-ui-demo.html` + `UX-UI-ANIMATION-PREVIEW.md`) vào repo, hay Phase B làm việc từ bundle đã build? Không có nguồn thì không thể "giữ nguyên" chính xác CSS Module và cấu trúc file. **Khuyến nghị: commit nguồn demo trước.** |
| **G1** | Phạm vi Phase B: chỉ Auth/Profile + Review (Tuấn), hay toàn bộ 14 tính năng? Nếu toàn bộ, cần đồng ý của các owner khác và cập nhật D-OWN-01/CLAUDE.md. |
| **G2** | Cấu trúc thư mục frontend chính thức: theo `docs/structure.md` hay theo demo (`README (1).md`)? Nếu theo demo: cập nhật `docs/structure.md` trước; giữ `ProtectedRoute/AdminRoute`; xử lý các file OBSOLETE (giữ hay xóa). |
| **G3** | Các route deep-link của demo (`/logout`, `/courses/:id/join`, `/learning-paths/:id/edit`, `/contact-guest`) và màn trạng thái (`/forgot-sent`, `/reset-expired`) có giữ trong production không? (Danh sách route trong task không có các route này.) |
| **G4** | Nơi lưu token: `sessionStorage` (D-AUTH-01) hay `localStorage` (demo)? Kèm ND-41/ND-48 (refresh token qua cookie hay body) — `client.js` không viết xong được nếu chưa chốt. |
| **G5** | Nguồn UI chính thức: demo React; `docs/EduMentor-UI-design/` và `docs/wireframes/` giữ làm lịch sử hay bỏ? Các ND đang dẫn wireframe xử lý thế nào? |
| **G6** | API prefix: `/api/...` ([API]) hay `/api/v1/...` (nhánh Hoa)? |
| **G7** | Với tính năng API PENDING (M1–M4, E-01…E-03): giữ UI + trạng thái "chưa khả dụng" (khuyến nghị) hay ẩn hẳn khỏi production? |

---

## H. Ghi chú cho Phase B (khi được duyệt)

- Thứ tự đề xuất giữ như task §27, nhưng **Auth (04) phụ thuộc G4 + ND-41/ND-48**; Review (11) phụ thuộc T16, ND-31, ND-25 cho câu chữ hiển thị.
- `package.json` hiện rỗng → Phase B sẽ phải **thêm dependency** (react, react-dom, react-router-dom, axios, vite, @vitejs/plugin-react): cần duyệt theo quy tắc "không thêm thư viện ngoài tài liệu" (CLAUDE.md).
- `npm run build` hiện **không chạy được** (package.json rỗng) — không có kết quả build trong Phase A.
- Không chép `mock/db.js` vào luồng production; `VITE_USE_MOCK` mặc định `false`.

---

## Kết quả Phase A

- File tạo mới: **`docs/ui-animation/FRONTEND-SYNC-AUDIT.md`** (file này) — thư mục `docs/ui-animation/` được tạo kèm.
- `frontend/`, backend, CSDL, dependency: **không thay đổi**.
- Thao tác Git: `git fetch origin Hoa` (thêm ref `origin/Hoa` để kiểm tra nguồn demo; không checkout, không merge, working tree không đổi).
