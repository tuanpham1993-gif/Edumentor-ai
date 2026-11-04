# Phase B0 — Demo Source Intake

> Ngày: 2026-10-28 · Nhánh: `docs/initial-project-documentation` · Chỉ đọc. Không sửa frontend, backend, CSDL, API contract, Skill hay tài liệu khác.
> Báo cáo liên quan: `docs/ui-animation/FRONTEND-SYNC-AUDIT.md` (Phase A), `docs/ui-animation/SKILL-DOC-DEMO-AUDIT.md`.

**Quy ước bằng chứng.** Mã nguồn React của demo **không có**. Mọi thông tin về demo trong báo cáo này lấy từ **bản build một file** `EduMentor AI Demo.html` (Vite đã minify, nằm ngoài repo). Thông tin đó được đánh dấu **[BUNDLE]**: giá trị là thật vì đọc trực tiếp từ bundle, nhưng **không kiểm chứng được theo file nguồn** (tên file `.jsx`/`.module.css`, cách chia thư mục, dependency khai báo). Không có thông tin nào được suy đoán khi không có bằng chứng.

---

## 1. Executive Summary

- **G0 vẫn chưa được giải quyết.** Không path demo nào trong §2 của task tồn tại trong working tree hay trong bất kỳ nhánh nào (`main`, `develop`, `docs/initial-project-documentation`, `origin/*`, kể cả `origin/Hoa`). Repo cũng không có stash.
- **Bản duy nhất tìm thấy là bản build** `C:\Users\PC\Downloads\EduMentor AI Demo.html` (568 040 byte, sửa lần cuối 2026-10-28 21:26), **ngoài repo**. Bản này không có `package.json`, `src/`, lockfile hay file nguồn nào. Theo task, file này không được di chuyển.
- **Bundle cho biết:**
  - Stack: React 18.3.1 + react-router-dom 6.30.6 + axios + CSS Modules.
  - Animation: viết tay bằng CSS keyframes/transition + Web Animations API; **không dùng thư viện animation**.
  - Token chuyển động: `--d-*` (thời lượng) và `--e-*` (easing).
  - Reduced motion: có `prefers-reduced-motion` và công tắc `data-motion`.
  - Dữ liệu: **toàn bộ API là mock**.
  - Auth: token lưu trong `localStorage`; không có route guard; không có luồng refresh.
- **Bảo mật:** form đăng ký trong bundle **không** cho chọn role (mock gán `role:"student"`), nên **không có SECURITY CONFLICT** về việc tự gán ADMIN. Còn lại hai rủi ro: không có guard `/admin/*`, và token ở `localStorage`.
- **Phase B readiness: BLOCKED** (G0 + BLOCKED — AUTH STORAGE CONTRACT + G2 chưa chốt).

---

## 2. Demo Source Location

| Path theo task | Tồn tại? | Ghi chú |
|---|---|---|
| `docs/ui-animation/demo/edumentor-demo-react/` | **KHÔNG** | Thư mục `docs/ui-animation/demo/` không tồn tại |
| `docs/ui-animation/demo/edumentor-ui-demo.html` | **KHÔNG** | |
| `docs/ui-animation/demo/UX-UI-ANIMATION-PREVIEW.md` | **KHÔNG** | Cũng không có ở `docs/ui-animation/` |
| Tìm toàn repo (`*demo*`, `UX-UI-ANIMATION*`) | Không có file demo | Chỉ khớp `SKILL-DOC-DEMO-AUDIT.md` |
| Tìm mọi nhánh (`git ls-tree -r` trên 8 ref) | Không có | |
| **Vị trí thực tế đã tìm thấy** | `C:\Users\PC\Downloads\EduMentor AI Demo.html` | Bản build, **không phải source React**. Chưa di chuyển |
| Tài liệu liên quan ngoài repo | `C:\Users\PC\Downloads\EduMentor-AI-29-trang-card-opening.mp4` | Video, không đọc trong B0 |

Nội dung `docs/ui-animation/` hiện có: `FRONTEND-SYNC-AUDIT.md`, `SKILL-DOC-DEMO-AUDIT.md`. Thư mục này **chưa được Git theo dõi**.

---

## 3. Project Structure

| Mục | Demo source | [BUNDLE] / bằng chứng phụ |
|---|---|---|
| `package.json` | **MISSING** | — |
| `src/` | **MISSING** | — |
| `public/`, `assets/` | **MISSING** | Bundle không có ảnh; icon là SVG inline; font Be Vietnam Pro tải từ Google Fonts |
| `components/`, `pages/`, `hooks/`, `utils/`, `styles/` | **MISSING** | Tên thư mục chỉ có trong `README (1).md` (ngoài repo): `pages/{auth,profile,catalog,tracking,path,tutor,review,feedback,admin}`, `components/{layout,common,course,path,profile,chat,demo}`, `api/`, `mock/`, `utils/`, `config/` |
| Package manager | **NOT VERIFIABLE** | Không có lockfile |
| React | NOT VERIFIABLE (source) | [BUNDLE] `version:"18.3.1"`, `react-dom.production.min.js` |
| Vite | NOT VERIFIABLE (source) | [BUNDLE] tên class CSS Module dạng `_name_hash_n` khớp với mặc định của Vite; không có chuỗi phiên bản Vite |
| JS / TS | NOT VERIFIABLE | — |
| Router | [BUNDLE] react-router-dom 6.30.6 | Single-file build dùng `MemoryRouter` (theo Phase A) |
| State management | [BUNDLE] state cục bộ + Context (`ToastContext`, `CardOpeningContext`) | Không có redux/zustand (đếm = 0) |
| CSS | [BUNDLE] CSS Modules + `index.css` global (token, `.btn`, `.card`, `.stagger`, `.page-in`, …) | |
| Animation library | [BUNDLE] **không có** | framer/gsap/react-spring = 0 |
| Icon library | [BUNDLE] không có (lucide = 0, SVG inline) | |
| UI library | [BUNDLE] không có | |
| Chart/graph | [BUNDLE] không có (recharts = 0). `PathGraph` vẽ bằng SVG thủ công | 3 lần khớp chuỗi "d3" đều là chuỗi con, không phải thư viện d3 |
| HTTP | [BUNDLE] axios (chuỗi phiên bản 1.21.0 trong bundle) | |

**Production hiện tại:** `frontend/` có 69 file, tất cả 0 byte, tổ chức theo `docs/structure.md`.

---

## 4. Dependencies

Không có `package.json`, `package-lock.json`, `yarn.lock` hay `pnpm-lock.yaml` của demo, nên toàn bộ danh sách dưới đây là **NOT VERIFIABLE**. Các dependency nhận diện được trong bundle:

| Dependency | Version [BUNDLE] | Used by | Production implication |
|---|---|---|---|
| react, react-dom | 18.3.1 | Toàn bộ UI | `CLAUDE.md` có ghi React; phiên bản chưa được ghi trong docs |
| react-router-dom | 6.30.6 | Routing | **Chưa có trong docs**, phải được duyệt (quy tắc "không thêm thư viện ngoài tài liệu") |
| axios | 1.21.0 (chuỗi trong bundle) | `api/client.js` | **Chưa có trong docs**, phải được duyệt |
| vite (+ plugin React) | NOT VERIFIABLE | Build | `CLAUDE.md` có ghi Vite |
| Animation dependency | **Không có** | — | Production không cần thêm thư viện animation |

Production `frontend/package.json` đang rỗng. Phase B0 không tạo và không sửa file này.

---

## 5. Animation System

### 5.1. Technology [BUNDLE]

| Kỹ thuật | Có? | Bằng chứng |
|---|---|---|
| CSS animation (`@keyframes`) | Có | Khoảng 90 keyframes, ví dụ: `sway`, `flick`, `rise`, `pop`, `dlg-in/out`, `drawer-in/out`, `t-in/out` (toast), `q-next/q-prev`, `node-in/out`, `draw`, `shimmer`, `shake`, `page-in`, `enter-up` |
| CSS transition | Có | Dùng `var(--d-*)` và `var(--e-*)` |
| React state | Có | Bật/tắt class theo state |
| Web Animations API | Có | 11 lần gọi `animate(`; `CardOpening` (hiệu ứng mở sách 3D) |
| View Transitions API | Có | 2 lần gọi `startViewTransition` (ThemeToggle, kèm fallback) |
| requestAnimationFrame | Có (theo Phase A) | `AnimatedNumber` |
| Framer Motion / GSAP / React Spring | **Không** | Đếm = 0 |

### 5.2. Tokens [BUNDLE]

| Token | Giá trị |
|---|---|
| `--d-instant` | 80ms |
| `--d-fast` | .15s |
| `--d-base` | .22s |
| `--d-slow` | .32s |
| `--d-emph` | .6s |
| `--e-std` | `cubic-bezier(.2, 0, 0, 1)` |
| `--e-in` | `cubic-bezier(0, 0, .2, 1)` |
| `--e-exit` | `cubic-bezier(.4, 0, 1, 1)` |
| `--e-spring` | `cubic-bezier(.34, 1.56, .64, 1)` |
| Lamp sway | `5.2s ease-in-out infinite alternate`, xoay ±2.5deg |
| Lamp flick | `.42s steps(1) 1` |
| Toast | Tối đa 3, tự đóng sau 4 s (Phase A) |
| Distance / scale / opacity / stagger / hover / press / modal / drawer / page transition | Có keyframes và class (`.stagger`, `.enter`, `.page-in`, `dlg-*`, `drawer-*`). Giá trị chi tiết của từng keyframe **không được trích hết trong B0**; cần đọc từ source khi có |

### 5.3. Accessibility [BUNDLE]

| Hạng mục | Trạng thái |
|---|---|
| `prefers-reduced-motion` | Có: 2 khối `@media` + kiểm tra trong JS (`matchMedia`) |
| Công tắc giảm chuyển động | Có: `localStorage["em-motion"]` → `data-motion="reduce\|full"`; CSS đặt `animation-duration:1ms` cho `*`, `::before`, `::after` |
| Keyboard | Có một phần: Modal (Esc, focus trap), Tabs (←/→), 8 lần dùng `tabIndex` |
| Focus | 18 rule `:focus-visible` |
| ARIA | 179 lần `aria-*` (ví dụ PullLamp `aria-pressed`, HangingLamp `aria-hidden`) |
| Touch | PullLamp dùng pointer events (Phase A). Mức hỗ trợ touch tổng thể: NOT VERIFIABLE |
| Responsive | 30 `@media`, breakpoint từ 520 tới 1100px; HangingLamp ẩn dưới 720px |

---

## 6. UI System

Baseline: `docs/EduMentor-UI-design/EduMentor-UI/` gồm 29 trang HTML tĩnh, `png/` và `pages.json`. `docs/ui-animation/UX-UI-ANIMATION-PREVIEW.md` **MISSING**.

| Hạng mục | Demo [BUNDLE] | UI baseline | Kết luận |
|---|---|---|---|
| Màu (dark) | `--bg #100e0c`, `--card #16171a`, `--text #f3efe8`, `--accent #f5a524`, `--accent-soft-fg #f5c46d`, `--on-accent #1a1206`, … | Màu xuất hiện nhiều nhất: `#f5a524`, `#c9c2b7`, `#f3efe8`, `#2c2b29`, `#a39d93`, `#3a3835`, `#16171a`, `#f5c46d`, `#1a1206` | Khớp bảng màu dark warm / amber |
| Theme sáng | Có (`:root[data-theme=light]`, `--bg #f6f1e9`, `--accent #dc8a0c`) | Không có | Demo có thêm; **không phải UI CONFLICT**, baseline không có phần này |
| Typography | Be Vietnam Pro | Be Vietnam Pro | Khớp |
| Hanging lamp / amber glow | Có (`_lamp`, `_glow` radial `#f5a5244d`) | Không có (0 trang) | Demo có thêm |
| Animation / transition | Có (§5) | 0 `@keyframes`, 0 `transition` | Baseline tĩnh |
| Responsive | 30 `@media` | 0 `@media` | Baseline không có responsive |
| Trang | 33 màn hình (Phase A) | 29 trang; **không có** Feedback/Contact, Admin Feedback, Admin User Paths | Demo có thêm 3 nhóm trang |
| Layout, card, modal, drawer, navigation, form, table, graph, chat, review, admin | Có trong bundle | Có trang tương ứng (trừ các trang thiếu nêu trên) | So sánh từng component: **NOT VERIFIABLE**, vì không có source để đối chiếu cấu trúc DOM/CSS theo file |

Không ghi nhận UI CONFLICT nào có bằng chứng. Mọi khác biệt ở bảng trên là phần demo bổ sung so với baseline tĩnh. Vấn đề còn lại là **ưu tiên nguồn UI**: `CLAUDE.md` trỏ `docs/wireframes/`, còn quyết định G5 xếp demo cao hơn (CONFLICT-006 trong `SKILL-DOC-DEMO-AUDIT.md`).

---

## 7. 14 Feature Mapping

Cột Status chấm theo **source demo**. Source không có, nên mọi dòng đều là NOT VERIFIABLE. Page, Component và Mock lấy từ [BUNDLE] / `README (1).md`. Cột "API dependency" đối chiếu với `docs/api-endpoints.md`.

| # | Feature | Demo page | Demo component | UI flow | Animation | State | Mock data | API dependency | Status |
|---|---|---|---|---|---|---|---|---|---|
| 01 | Xác thực & hồ sơ | Login, Register, ForgotPassword, ForgotSent, ResetPassword, ResetExpired, Profile, EditProfile, ChangePassword, Skills | AuthLayout, PasswordInput, PasswordRules, LogoutDialog, PullLamp, HangingLamp | Đăng nhập → `/courses`; quên/đặt lại mật khẩu; sửa hồ sơ, kỹ năng | lamp sway/flick, shake khi lỗi | local + `localStorage.access_token` | `db.user` | §2 có; `/api/auth/refresh` demo không gọi | NOT VERIFIABLE |
| 02 | Danh mục khóa học | Catalog, CourseDetail | CourseCard, CourseCardFace, CourseCover, CourseFilters, CardOpening | Lọc → mở thẻ → chi tiết | CardOpening (WAAPI), stagger | local | `db.courses` | §3 có | NOT VERIFIABLE |
| 03 | Bookmark | CourseDetail, MyCourses | (trong page) | Đánh dấu / bỏ đánh dấu | pop | local | `db.tracking` | §4 có | NOT VERIFIABLE |
| 04 | Theo dõi tiến trình | MyCourses, CourseDetail | JoinDialog, Tabs | Tham gia → in_progress | Tabs pill trượt | local | `db.tracking` | §4 có | NOT VERIFIABLE |
| 05 | AI Consultant + Lộ trình | Consultant, MyPaths, PathDetail | ChatBubble (ẩn ở trang này), PathEditDialog | Chat → đề xuất → lưu lộ trình | msg-in, panel | local | `db.paths`, `db.sessions` | §5, §12 có | NOT VERIFIABLE |
| 06 | Node / Edge | PathDetail | PathGraph (SVG) | Thêm/xóa node, cạnh | draw, node-in/out, node-flash | local | `db.paths[].nodes` (`x`, `y`, `role`, `added_by`) | §6–7 có | NOT VERIFIABLE |
| 07 | Gợi ý theo kỹ năng | PathDetail (node) | (trong page) | Chọn node → khóa học | rise | local | `db.courses` | §8 có | NOT VERIFIABLE |
| 08 | AI Tutor | Tutor | (trong page) | Phiên chat, tin nhắn có `code`/`quiz` | msg-in, dot (typing) | local | `db.sessions` | §9 có | NOT VERIFIABLE |
| 09 | Ôn tập & đánh giá | ReviewStart, ReviewAttempt, ReviewResult, ReviewHistory, ReviewDetail | AnimatedNumber | Bắt đầu → 20 câu → nộp → kết quả | q-next/q-prev, reveal, glow | local | `db.attempts`, `db.inProgress` | §10 có; lưu bài dở **MISSING** (M1) | NOT VERIFIABLE |
| 10 | Feedback | Feedback (2 biến thể) | ChatBubble | Gửi phản hồi / liên hệ | fab-in, panel-in | local | `mock/feedback.js` | **MISSING** (M2) | NOT VERIFIABLE |
| 11 | Admin khóa học / kỹ năng / liên kết | AdminCourses, AdminSkills, AdminBasePaths, AdminHistorical | AdminLayout, Modal, ConfirmDialog | CRUD | dlg-in/out | local | `db.courses`, `db.basePaths`, `db.historical` | §11, §13 có | NOT VERIFIABLE |
| 12 | Admin quan hệ kỹ năng | AdminSkills (SkillRelationMap) | (trong page) | CRUD quan hệ | draw | local | `db.skillRelations` | §11 có | NOT VERIFIABLE |
| 13 | Admin phản hồi | AdminFeedback | Tabs, table | Lọc, xem | rise | local | `mock/feedback.js` | **MISSING** (M2) | NOT VERIFIABLE |
| 14 | Admin lộ trình người dùng | AdminUserPaths | PathGraph | Xem lộ trình theo user | node-in | local | `db.paths` | **MISSING** (M3) | NOT VERIFIABLE |

---

## 8. Demo → API Mapping

Nguồn API chính thức: `docs/api-endpoints.md`. Trong bundle, mọi hàm `*.api.js` đều gọi `mock/db.js` (có `await delay`); **không có lời gọi HTTP thật nào**. Bảng dưới tóm tắt từ `FRONTEND-SYNC-AUDIT.md` §E (mã E-xx, M-x).

| Demo action | Expected endpoint | Method | Request (demo) | Response (demo) | API docs | Status |
|---|---|---|---|---|---|---|
| Đăng nhập | `/api/auth/login` | POST | `{email, password}` | `{access_token, refresh_token, token_type, user}` | §2 | MATCH (hình dạng); cách lưu token: CONFLICT với D-AUTH-01 |
| Làm mới token | `/api/auth/refresh` | POST | — (demo không gọi) | — | §2 | MISSING trong demo (E-12) |
| Đăng ký | `/api/auth/register` | POST | `{email, password, full_name}` | — | §2 | MATCH; `confirm_password` phụ thuộc ND-47 (E-13) |
| Đặt lại mật khẩu | `/api/auth/reset-password` | POST | token `"demo"` | — | §2 | NOT VERIFIABLE (dạng link chưa có trong tài liệu, E-14) |
| Cập nhật kỹ năng | `/api/me/skills` | PATCH | theo **tên** kỹ năng | — | T06: theo `skill_id` | MISMATCH (E-10) |
| Upload avatar | `/api/me/avatar` | POST | ≤2 MB, JPG/PNG (demo tự đặt) | — | ND-12 chưa chốt | MISMATCH (E-15) |
| Danh sách khóa học | `/api/courses` | GET | — | `platform`, `provider`, level tiếng Việt | DB: `organization`, level enum | MISMATCH (E-16) |
| Trạng thái khóa học | `/api/me/courses/{id}/status` | GET | N lời gọi | — | §4 | MATCH (vấn đề hiệu năng, E-17) |
| Đổi tên lộ trình | `/api/learning-paths/{id}` | PATCH | `name` | — | DB không có `name` | MISMATCH (E-01) |
| Bắt đầu ôn tập | `/api/courses/{id}/review` | GET | — | `{available, in_progress, reason}` | §10 không có `in_progress` | MISMATCH (E-23) |
| Câu hỏi | `/api/courses/{id}/review-attempts` | POST | — | câu hỏi có `skill` | T15 không có `skill` | MISMATCH (E-18) |
| Nộp bài | `/api/review-attempts/{id}/submit` | POST | điểm tính phía client, ngưỡng 60 hard-code | — | D02 lấy từ cấu hình server | MISMATCH (E-19) |
| Lưu bài dở | — | — | lưu cục bộ | — | không có | MISSING (M1) |
| Lịch sử ôn tập | `/api/me/review-history` | GET | phân trang phía client | — | T17: `page`/`page_size` | MISMATCH (E-22) |
| Tin nhắn Tutor | `/api/chat/sessions…` | — | `code`, `quiz`, `title` | — | DB `content`, `topic` | MISMATCH (E-25) |
| Feedback học viên / liên hệ / admin | — | — | `mock/feedback.js` | — | không có | MISSING (M2) |
| Admin lộ trình người dùng | — | — | `db.paths` | — | không có | MISSING (M3) |
| AI tư vấn khóa học (ChatBubble) | — | — | câu trả lời soạn sẵn | — | không có | MISSING (M4) |

Các field request/response chi tiết của từng endpoint còn lại (Catalog, Node/Edge, Admin): **NOT VERIFIABLE**, vì `api-endpoints.md` phần lớn chưa định nghĩa response schema.

---

## 9. Auth & Role Analysis

| Hạng mục | Demo [BUNDLE] | Kết luận |
|---|---|---|
| USER / ADMIN | Mock user `role:"student"`. Có trang admin. Không thấy chuỗi `"admin"` dùng làm giá trị role | — |
| Tự chọn ADMIN khi đăng ký | **Không**: register chỉ gửi `{email, password, full_name}` | **Không có SECURITY CONFLICT** |
| ProtectedRoute / AdminRoute | **Không có**: mọi route, kể cả `/admin/*`, vào được | GAP; production phải có guard (`docs/structure.md` §1, §3) |
| Role trong token | Mock trả `access_token:"demo"` | NOT VERIFIABLE |
| Access token | `localStorage["access_token"]` → `Authorization: Bearer` | CONFLICT với D-AUTH-01 (`sessionStorage`) |
| Refresh token | Mock trả `refresh_token:"demo"`, **không lưu, không gửi** | Không xác định được cách truyền |
| sessionStorage | Không dùng (đếm = 0) | — |
| Cookie | `document.cookie` / `withCredentials` chỉ xuất hiện trong mã nội bộ của axios, ứng dụng không dùng | Ứng dụng không dùng cookie |

Nguyên tắc cần kiểm tra trong production (**không triển khai ở B0**): *Public registration must not allow users to assign themselves ADMIN.* Tài liệu hiện có quy định điều này tại T09 và AP-R01; admin chỉ được tạo bằng `scripts/create_admin.py`.

---

## 10. Mock Data Inventory

Nguồn: [BUNDLE] + Phase A §A4. Tên file theo `README (1).md`.

| Mock | File | Purpose | Expected production API | Feature | Replacement status |
|---|---|---|---|---|---|
| user (+ mật khẩu demo `Demo@123`) | `mock/db.js` | Đăng nhập, hồ sơ | §2 auth, `GET/PATCH /api/me` | 01 | Có API; chờ ND-41/48 |
| userSkills | `mock/db.js` | Kỹ năng | `/api/me/skills` | 01 | Có API; phải đổi sang `skill_id` |
| courses | `mock/db.js` | Danh mục, gợi ý | §3, §8 | 02, 07 | Có API; cần map field |
| tracking | `mock/db.js` | Bookmark, tiến trình | §4 | 03, 04 | Có API |
| paths (nodes, edges, `x`, `y`) | `mock/db.js` | Lộ trình | §5–7, §12 | 05, 06, 14 | Có API (05, 06); 14 MISSING |
| sessions | `mock/db.js` | Consultant, Tutor | §5, §9 | 05, 08 | Có API; field lệch |
| attempts, inProgress | `mock/db.js` | Ôn tập | §10 | 09 | Có API; bài dở MISSING (M1) |
| skillRelations | `mock/db.js` | Admin quan hệ | §11 | 12 | Có API |
| basePaths | `mock/db.js` | Admin mẫu lộ trình | §12 | 11 | Có API; field `used` lệch |
| historical | `mock/db.js` | Admin dữ liệu lịch sử | §13 | 11 | Có API; DB không có bảng (E-03) |
| feedback | `mock/feedback.js` | Phản hồi, admin phản hồi | — | 10, 13 | **MISSING** API (M2) |
| Câu trả lời AI soạn sẵn | `mock/*` | Consultant, Tutor, Advisor | §5, §9; Advisor không có | 05, 08 | Advisor **MISSING** (M4) |
| Admin user list | `mock/db.js` | Admin lộ trình user | — | 14 | **MISSING** API (M3) |

---

## 11. Skill Alignment

Không có thư mục `skills/` hay `docs/skills/`.

| Skill | Purpose | Referenced architecture | Referenced UI | Referenced animation | Referenced API | Current status | Demo alignment |
|---|---|---|---|---|---|---|---|
| `.claude/skills/auth-profile` | Backend Auth/Profile | Router → Service → Repository → Model | Không có | Không có | `api-endpoints.md` §2 (có refresh) | SPEC CONFIRMED / NOT IMPLEMENTED | NOT VERIFIABLE; không mô tả UI |
| `.claude/skills/review-assessment` | Backend Review | Như trên | Chỉ có quy tắc "frontend không gửi request cập nhật kỹ năng" | Không có | §10 | SPEC CONFIRMED / NOT IMPLEMENTED | NOT VERIFIABLE |
| `.agents/skills/auth-profile` | Bản sao cho Codex | Như trên | Không có | Không có | **API cũ**: thiếu refresh, thiếu D-AUTH | Lỗi thời | CONFLICT (với `.claude`) |
| `.agents/skills/review-assessment` | Bản sao cho Codex | Như trên | Không có | Không có | Coi T16 là đã chốt | Lỗi thời | CONFLICT |

Không skill nào mô tả frontend cũ, animation cũ hay component không còn tồn tại. Phần frontend **chưa được mô tả** (SKILL GAP), chứ không phải mô tả sai. `AGENTS.md` dòng 59 trỏ tới `.Codex/skills/…`, một đường dẫn không tồn tại.

---

## 12. Documentation Alignment

| Document | Liên quan demo | Trạng thái |
|---|---|---|
| `docs/structure.md` §1, §3 | Cây frontend và route khác demo | CONFLICT (G2) |
| `docs/conventions.md` §4 | 3 dòng quy ước frontend; không có CSS Modules, token, motion | PARTIAL |
| `docs/api-endpoints.md` | Thiếu M1–M4 | PARTIAL |
| `docs/decisions.md` | D-AUTH-01 (`sessionStorage`); ND-41/48 mở; chưa ghi G0–G7 | PARTIAL |
| `CLAUDE.md` / `AGENTS.md` | Phạm vi 2 module; nguồn UI = `docs/wireframes/`; dependency frontend chưa liệt kê | CONFLICT (với G1/G5) |
| `README.md` | Không nhắc demo | PARTIAL |
| `SETUP.md` | Không có `VITE_USE_MOCK`, cách chạy demo | PARTIAL |
| Tài liệu UI/animation | Không có | MISSING |

Chi tiết: `SKILL-DOC-DEMO-AUDIT.md` §5, §12.

---

## 13. Known Blockers

| Blocker | Trạng thái | Chi tiết |
|---|---|---|
| **G0 — Demo source** | **BLOCKED** | Source React, `package.json` và preview không có trong repo |
| **AUTH STORAGE CONTRACT (ND-41 / ND-48)** | **BLOCKED — AUTH STORAGE CONTRACT** | Demo lưu access token ở `localStorage`. Refresh token: demo **không gửi**, nên cách truyền là **unknown**. D-AUTH-01 định hướng `sessionStorage`; cookie hay body cho refresh token chưa chốt |
| **G2 — Frontend structure** | BLOCKED (chờ quyết định) | Xem bảng dưới |
| G1 — Phạm vi 14 tính năng vs `CLAUDE.md` | Chưa ghi vào docs | |
| G6 — `/api` vs `/api/v1` (nhánh Hoa) | Chưa chốt | |

**G2 — so sánh hai cấu trúc (không chọn):**

| Khía cạnh | `docs/structure.md` | Demo (`README (1).md` + [BUNDLE]) |
|---|---|---|
| Lộ trình | `pages/learning-path/`, `components/learning-path/` | `pages/path/`, `components/path/` |
| Tiến trình | Không có page riêng (`components/profile/MyCoursesTabs`) | `pages/tracking/` |
| Phản hồi | Không có | `pages/feedback/` |
| Guard | `routes/ProtectedRoute`, `AdminRoute` | Không có |
| State | `store/authStore.js`, `hooks/*` | Không có store; Context |
| Layout | Header, Sidebar, PageLayout | Header, PageLayout, AuthLayout, SettingsLayout, AdminLayout, HangingLamp, PullLamp (không Sidebar) |
| Khác | — | `mock/`, `config/`, `components/demo/` |
| Route | `/profile`, `/learning-paths/new`, `/review/:courseId`, `/review/history` | `/me…`, `/consultant`, `/courses/:id/review…`, `/me/review-history…`, `/contact`, `/admin/*` (6 trang) |

---

## 14. Conflicts

| ID | A | B | Issue | Severity |
|---|---|---|---|---|
| B0-C01 | D-AUTH-01 (`sessionStorage`) | Demo (`localStorage`) | Nơi lưu token | HIGH |
| B0-C02 | `docs/structure.md` | Cấu trúc demo | G2 | HIGH |
| B0-C03 | `api-endpoints.md` | Field trong demo (E-01, E-10, E-16, E-18, E-19, E-22, E-23, E-25) | Hợp đồng lệch | HIGH |
| B0-C04 | `decisions.md` (T16 BLOCKED, ND-25, ND-12) | Câu chữ trong UI demo (E-15, E-20, E-27, E-28) | UI khẳng định các quy tắc chưa chốt | MEDIUM |
| B0-C05 | `CLAUDE.md` (2 module, nguồn UI wireframes) | G1 / G5 | Chỉ thị agent mâu thuẫn với quyết định | HIGH |
| B0-C06 | `.claude/skills/*` | `.agents/skills/*` | Bản sao lỗi thời | MEDIUM |

Không có SECURITY CONFLICT kiểu "ẩn UI admin = phân quyền" trong docs hay skill. Demo không cho tự chọn ADMIN.

---

## 15. Production Risks

1. Chép demo vào production sẽ mang theo `localStorage` token và **không có guard**.
2. Không có luồng refresh khi nhận 401, nên người dùng bị đăng xuất khi access token hết hạn sau 30 phút (D-AUTH-02).
3. Ngưỡng đạt 60% hard-code và điểm tính phía client: vi phạm quy định "điểm do server chấm" (D02).
4. Nội dung chỉ dành cho demo lọt vào production: DemoNav, giả lập lỗi mạng, `MemoryRouter`, email/mật khẩu điền sẵn, câu trả lời AI soạn sẵn, link "Mở thử liên kết trong email (demo)".
5. Bốn nhóm UI (M1–M4) không có API.
6. Tái tạo CSS từ bundle đã hash có thể không khớp 1-1 với file nguồn.
7. Thêm react-router-dom và axios khi chưa được duyệt sẽ vi phạm quy tắc dependency trong `CLAUDE.md`.

---

## 16. Phase B Readiness

| Điều kiện READY | Kết quả |
|---|---|
| React source tồn tại | **KHÔNG** |
| Package manifest tồn tại | **KHÔNG** |
| Source đọc được | Chỉ bundle minify |
| 14 feature map được hoặc có trạng thái rõ | Có trạng thái (NOT VERIFIABLE theo source) |
| Xác định được animation implementation | Có, theo [BUNDLE] |
| Xác định được UI structure | Không, theo source |
| Không còn blocker G0 | **KHÔNG** |

**Phase B readiness: BLOCKED**

---

## 17. Recommended Next Step

1. Người dùng commit mã nguồn demo React (gồm `package.json` và lockfile) vào `docs/ui-animation/demo/edumentor-demo-react/`, kèm `UX-UI-ANIMATION-PREVIEW.md` nếu có. Sau đó chạy lại B0 để đổi các dòng NOT VERIFIABLE thành kết luận.
2. Nhóm chốt ND-41/ND-48 (AUTH STORAGE CONTRACT) và G2 (cấu trúc frontend).
3. Ghi G0–G7 vào `docs/decisions.md` và cập nhật `CLAUDE.md` (phạm vi, nguồn UI, dependency frontend). Đây là task riêng, cần được duyệt.

---

## Final Verdict

| Area | Status | Evidence |
|---|---|---|
| Demo source | BLOCKED | Không có path nào trong §2; chỉ có bundle ở Downloads |
| UI | PARTIAL | Bảng màu và font khớp baseline; so sánh component NOT VERIFIABLE |
| Animation | PARTIAL | Token và kỹ thuật xác định được từ [BUNDLE]; source MISSING |
| 14 features | NOT VERIFIABLE | §7 |
| API mapping | PARTIAL | §8: nhiều MISMATCH; MISSING M1–M4 |
| Auth | BLOCKED | `localStorage` vs D-AUTH-01; ND-41/48 mở; không có luồng refresh |
| Role | PARTIAL | Không tự gán ADMIN; không có guard |
| Skills | PARTIAL | Không mô tả frontend; bản `.agents` lỗi thời |
| Documentation | PARTIAL | §12 |
| Frontend architecture | BLOCKED | G2 |
| Dependencies | NOT VERIFIABLE | Không có manifest |
| Overall | **BLOCKED** | G0 + AUTH STORAGE CONTRACT + G2 |

```text
PHASE B0 COMPLETE

Implementation started: NO
Frontend modified: NO
Backend modified: NO
Database modified: NO
API contract modified: NO
Production dependencies modified: NO

Next phase requires explicit approval.
```
