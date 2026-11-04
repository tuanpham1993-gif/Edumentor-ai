# SKILL + DOCUMENTATION + DEMO AUDIT

> Ngày audit: 2026-10-28 · Nhánh: `docs/initial-project-documentation` · Chỉ đọc. Không sửa Skill, README, docs, frontend, backend, CSDL.
> Trạng thái dùng trong báo cáo: **PASS · PARTIAL · FAIL · MISSING · CONFLICT · BLOCKED · NOT VERIFIABLE** (theo định nghĩa của task).

---

## 1. Executive Summary

1. **Tầng DEMO = BLOCKED.** `docs/ui-animation/demo/edumentor-demo-react/`, `docs/ui-animation/demo/edumentor-ui-demo.html`, `docs/ui-animation/UX-UI-ANIMATION-PREVIEW.md` **không tồn tại** trong working tree và trong mọi nhánh đã biết (`main`, `develop`, `docs/initial-project-documentation`, `origin/Hoa` — kiểm tra ngày 2026-10-28). Mọi so khớp "có giống demo không" vì vậy **không thể kết luận**. Bản build minify do người dùng gửi trong hội thoại (ngoài repo) chỉ được dùng làm **bằng chứng phụ** — đúng quyết định G0, không suy cấu trúc demo từ bản minify.
2. **Tầng SKILL** chỉ có 2 skill nghiệp vụ backend/API (`auth-profile`, `review-assessment`) + 2 bản sao cũ cho Codex. **Không có skill frontend / UI / UX / animation nào.** So với yêu cầu đồng bộ UI cho 14 tính năng: **FAIL (thiếu hoàn toàn)**.
3. **Tầng DOCUMENTATION** mạnh ở API/CSDL/quyết định cho 2 module của Tuấn, có quy ước frontend cơ bản (`conventions.md` §4, `structure.md` §3), nhưng **không có tài liệu UI/UX/animation/theme/component nào**, không nhắc tới demo React, và **route frontend trong `structure.md` mâu thuẫn với danh sách route đã duyệt cho Phase B**.
4. **Tầng IMPLEMENTATION** = MISSING: `frontend/` 69/69 file rỗng, `backend/` toàn bộ file rỗng trên nhánh hiện tại.
5. **Không có xung đột bảo mật** trong docs/skill hiện tại: cả `structure.md` §3 và `backend-rules.md` §2 đều ghi rõ guard frontend không phải phân quyền. Bản sao Codex (`.agents/skills/*`) đã cũ và chứa rule chưa chốt (T16) như rule bắt buộc — **rủi ro nghiệp vụ**, không phải bảo mật.

**Kết luận: NOT READY** — xem §15.

---

## 2. Sources Audited

| Nguồn | Đường dẫn | Trạng thái |
|---|---|---|
| Demo React | `docs/ui-animation/demo/edumentor-demo-react/` | **MISSING** → tầng Demo BLOCKED |
| Demo HTML | `docs/ui-animation/demo/edumentor-ui-demo.html` | **MISSING** |
| UX preview | `docs/ui-animation/UX-UI-ANIMATION-PREVIEW.md` | **MISSING** |
| Bằng chứng phụ (ngoài repo) | `EduMentor AI Demo.html`, `README (1).md`, `STRUCTURE (1).md` do người dùng gửi trong hội thoại; phân tích ở `docs/ui-animation/FRONTEND-SYNC-AUDIT.md` | Chỉ dùng để chỉ ra **rủi ro**, không để chấm PASS/FAIL |
| README | `README.md` | Đã đọc |
| Hướng dẫn agent | `CLAUDE.md`, `AGENTS.md` | Đã đọc |
| Docs | `SETUP.md`, `docs/api-endpoints.md`, `docs/database-design.md`, `docs/structure.md`, `docs/conventions.md`, `docs/backend-rules.md`, `docs/decisions.md`, `docs/modules/auth-profile(.tests).md`, `docs/modules/review-assessment(.tests).md`, `docs/ui-animation/FRONTEND-SYNC-AUDIT.md` | Đã đọc |
| Thiết kế cũ | `docs/EduMentor-UI-design/` (29 HTML + PNG), `docs/wireframes/` (19 PNG) | Có trong repo; người dùng đã xếp **dưới** demo React (G5) |
| Skill | `.claude/skills/auth-profile/SKILL.md`, `.claude/skills/review-assessment/SKILL.md`, `.agents/skills/auth-profile/SKILL.md`, `.agents/skills/review-assessment/SKILL.md` | Đã đọc. Không có `skills/`, `docs/skills/`, `*.skill.md` |
| Implementation | `frontend/` (69 file), `backend/` | Tất cả 0 byte |

---

## 3. Demo Analysis

**Trạng thái: BLOCKED** — thiếu nguồn demo trong repo.

Bằng chứng phụ (bundle ngoài repo, ghi lại từ `FRONTEND-SYNC-AUDIT.md`) cho thấy demo có, **chưa được xác nhận bằng mã nguồn**:
- 33 màn hình, 14 tính năng; route `/me…`, `/consultant`, `/courses/:id/review…`, `/contact`, `/admin/*` (6 trang).
- Component: Header, AuthLayout, SettingsLayout, AdminLayout, HangingLamp, PullLamp, Button, Modal, ConfirmDialog, Toast, Tabs, PasswordInput, PasswordRules, ThemeToggle, CourseCard, CourseCardFace, CourseCover, CardOpening, JoinDialog, PathGraph, PathEditDialog, LogoutDialog, ChatBubble.
- Theme Tối/Sáng, token CSS, reduced-motion, Web Animations API, CSS Modules.
- Mock API, MemoryRouter, không có route guard, token trong `localStorage`.

Các mục trên đều được đánh **NOT VERIFIABLE** ở các bảng dưới.

---

## 4. Skill Audit

### 4.1. Bảng tổng hợp

| Skill | Demo Alignment | Architecture | API | Animation | Documentation | Overall |
|---|---|---|---|---|---|---|
| `.claude/skills/auth-profile` | BLOCKED (demo thiếu) · nội dung **không có phần UI** → MISSING đối với UI | PASS (backend: Router → Service → Repository → Model; không có quy tắc frontend) | PASS (khớp `api-endpoints.md` §2 gồm `/api/auth/refresh`; ghi rõ phần chờ ND-41/ND-48) | MISSING | PASS (trỏ đúng `decisions.md`, module doc, `database-design.md`) | **PARTIAL** — đúng cho backend Auth/Profile, không phục vụ đồng bộ UI |
| `.claude/skills/review-assessment` | BLOCKED · không có phần UI | PASS (backend) | PASS (khớp §10; endpoint theo kỹ năng ghi là đã bỏ) | MISSING | PASS | **PARTIAL** — như trên |
| `.agents/skills/auth-profile` (Codex) | BLOCKED | PARTIAL (đúng phân lớp) | **CONFLICT** — không có refresh token, D-AUTH-01…05, D-OWN-01 | MISSING | **CONFLICT** — lệch bản `.claude` | **FAIL** |
| `.agents/skills/review-assessment` (Codex) | BLOCKED | PARTIAL | **CONFLICT** — ghi RV-R10–R13 (T16) là bắt buộc, trái `decisions.md` §3 (T16 BLOCKED) | MISSING | **CONFLICT** | **FAIL** |
| Skill frontend / UI / animation / 12 tính năng còn lại | — | — | — | — | — | **MISSING** |

### 4.2. Ghi chú theo tiêu chí task §7

- **A. Scope:** 2 skill `.claude` đúng phạm vi đã ghi (Auth/Profile, Review), có bảng phân công và cấm mở rộng sang module khác. Nhưng phạm vi này **mâu thuẫn với G1** (Phase B = 14 tính năng) → CONFLICT-004.
- **B. Demo alignment:** không skill nào nhắc demo, layout, component, theme, responsive, accessibility, routing frontend → **SKILL GAP** toàn bộ.
- **C. Architecture:** không có skill nào hướng dẫn "Component → axios trực tiếp" → **không có CONFLICT**. Nhưng cũng không có skill nào nêu luồng `Page → Component → api/*.api.js → client.js` → **SKILL GAP**.
- **D. API:** không skill nào tự định nghĩa endpoint ngoài `api-endpoints.md` (bản `.claude`). Bản `.agents` cũ thiếu `/api/auth/refresh`.
- **E. Mock:** không skill nào yêu cầu `mock/db.js` → PASS.
- **F. Animation:** không skill nào mô tả animation → **SKILL GAP**; không có over-specification.

---

## 5. Documentation Audit

| Document | Mục đích | Demo Alignment | API Alignment | Skill Alignment | Conflict | Overall |
|---|---|---|---|---|---|---|
| `README.md` | Tổng quan, tính năng, API, tài liệu liên quan | BLOCKED · không nhắc demo React (bản `README (1).md` ngoài repo có nhắc) | PASS (prefix ôn tập theo khóa học) | PASS | CONFLICT-003 (với `README (1).md` ngoài repo) | **PARTIAL** |
| `CLAUDE.md` | Chỉ thị agent | BLOCKED · bảng nguồn sự thật trỏ `docs/wireframes/` làm giao diện tham khảo, không nhắc demo | PASS | PASS | CONFLICT-004 (phạm vi 2 module vs G1), CONFLICT-006 (nguồn UI) | **PARTIAL** |
| `AGENTS.md` | Chỉ thị Codex | BLOCKED | PARTIAL | **CONFLICT** (trỏ `.Codex/skills/…` không tồn tại; thiếu bảng phân công) | CONFLICT-005 | **FAIL** |
| `SETUP.md` | Cài đặt, biến môi trường | BLOCKED · không có `VITE_USE_MOCK`, `VITE_ROUTER`, lệnh chạy demo | PASS | — | — | **PARTIAL** |
| `docs/api-endpoints.md` | Nguồn sự thật API | BLOCKED · thiếu endpoint cho UI mà bằng chứng phụ cho thấy (M1–M4) | PASS (là API truth) | PASS | — | **PARTIAL** (thiếu Feedback, Admin user paths, AI advisor, lưu bài dở) |
| `docs/database-design.md` | Nguồn sự thật CSDL | BLOCKED | PASS | PASS | Feedback/CourseContact có bảng nhưng không có API (ND-35) | **PASS** cho phạm vi CSDL |
| `docs/structure.md` | Cây thư mục, endpoint → file, route frontend | BLOCKED | PASS | PASS | **CONFLICT-001** (route), **CONFLICT-002** (cấu trúc frontend) | **CONFLICT** |
| `docs/conventions.md` | Quy ước API/code/Git/test | BLOCKED · §4 frontend chỉ 3 dòng, không có CSS Modules, theme, animation, a11y | PASS | PASS | — | **PARTIAL** |
| `docs/backend-rules.md` | Quy tắc backend dùng chung | không áp dụng UI | PASS | PASS | — | **PASS** (trong phạm vi) |
| `docs/decisions.md` | Quyết định, ND | BLOCKED · nhiều ND dẫn wireframe (ND-05, 08, 09, 10, 27, 38) trong khi G5 xếp wireframe dưới demo; **chưa ghi** các quyết định G0–G7 của Phase A/B | PASS | PASS | CONFLICT-004, CONFLICT-006 | **PARTIAL** |
| `docs/modules/auth-profile(.tests).md` | Đặc tả + test Auth/Profile | BLOCKED · không có đặc tả UI | PASS | PASS | — | **PARTIAL** |
| `docs/modules/review-assessment(.tests).md` | Đặc tả + test Review | BLOCKED · không có đặc tả UI | PASS | PASS | — | **PARTIAL** |
| `docs/ui-animation/FRONTEND-SYNC-AUDIT.md` | Audit Phase A | Dựa trên bundle ngoài repo — NOT VERIFIABLE theo nguồn | PASS (đối chiếu đúng `api-endpoints.md`) | — | — | **NOT VERIFIABLE** |
| Tài liệu UI/UX/animation/component | — | — | — | — | — | **MISSING** |

---

## 6. 14 Feature Audit

Cột **Documentation** chỉ xét tài liệu API/CSDL/nghiệp vụ có trong repo (không có tài liệu UI cho feature nào). Cột **Skill** = có skill dự án cho feature hay không.

| # | Feature | Demo | Documentation | Skill | Implementation | Overall |
|---|---|---|---|---|---|---|
| 01 | Xác thực & hồ sơ | BLOCKED | PASS — API §2, module doc, D-AUTH-01…05; UI: MISSING | PARTIAL — `auth-profile` (backend, không UI) | MISSING | **BLOCKED** |
| 02 | Danh mục khóa học | BLOCKED | PARTIAL — API §3, DB `Course`; response schema chưa định nghĩa | MISSING | MISSING | **BLOCKED** |
| 03 | Bookmark | BLOCKED | PARTIAL — API §4 (`/me/bookmarks*`), DB `StudentCourse` | MISSING | MISSING | **BLOCKED** |
| 04 | Theo dõi tiến trình | BLOCKED | PARTIAL — API §4, quy tắc chuyển trạng thái DB §3.3 | MISSING | MISSING | **BLOCKED** |
| 05 | AI Consultant + Learning Path | BLOCKED | PARTIAL — API §5, §12 | MISSING | MISSING | **BLOCKED** |
| 06 | Node + Edge | BLOCKED | PARTIAL — API §6–7, DB §4.5–4.6 | MISSING | MISSING | **BLOCKED** |
| 07 | Gợi ý khóa học theo kỹ năng | BLOCKED | PARTIAL — API §8 | MISSING | MISSING | **BLOCKED** |
| 08 | AI Tutor | BLOCKED | PARTIAL — API §9, DB §5 | MISSING | MISSING | **BLOCKED** |
| 09 | Ôn tập / đánh giá | BLOCKED | PASS — API §10, module doc (còn T16 BLOCKED, ND-20…34) | PARTIAL — `review-assessment` (backend, không UI) | MISSING | **BLOCKED** |
| 10 | Phản hồi (học viên) | BLOCKED | **MISSING** API (T22–T25 ☐, ND-35); DB có bảng `Feedback`, `CourseContact` | MISSING | MISSING | **BLOCKED** |
| 11 | Admin khóa học / kỹ năng / liên kết | BLOCKED | PARTIAL — API §11 (+ `/api/admin/questions*`) | MISSING (questions: CONFLICT-SCOPE-01) | MISSING | **BLOCKED** |
| 12 | Admin quan hệ kỹ năng | BLOCKED | PARTIAL — API §11 `skill-relations` | MISSING | MISSING | **BLOCKED** |
| 13 | Admin phản hồi | BLOCKED | **MISSING** API | MISSING | MISSING | **BLOCKED** |
| 14 | Admin lộ trình người dùng | BLOCKED | **MISSING** API | MISSING | MISSING | **BLOCKED** |

Bảng tổng hợp theo mẫu task §19:

| Feature | Demo | Documentation | Skill | Implementation | Overall |
|---|---|---|---|---|---|
| Auth/Profile | BLOCKED | PASS (API) / MISSING (UI) | PARTIAL | MISSING | BLOCKED |
| Catalog | BLOCKED | PARTIAL | MISSING | MISSING | BLOCKED |
| Bookmark | BLOCKED | PARTIAL | MISSING | MISSING | BLOCKED |
| Tracking | BLOCKED | PARTIAL | MISSING | MISSING | BLOCKED |
| AI Consultant | BLOCKED | PARTIAL | MISSING | MISSING | BLOCKED |
| Learning Path | BLOCKED | PARTIAL | MISSING | MISSING | BLOCKED |
| Recommendation | BLOCKED | PARTIAL | MISSING | MISSING | BLOCKED |
| AI Tutor | BLOCKED | PARTIAL | MISSING | MISSING | BLOCKED |
| Review | BLOCKED | PASS (API) / MISSING (UI) | PARTIAL | MISSING | BLOCKED |
| Feedback | BLOCKED | MISSING (API) | MISSING | MISSING | BLOCKED |
| Admin | BLOCKED | PARTIAL (11–12) / MISSING (13–14) | MISSING | MISSING | BLOCKED |

---

## 7. UI Component Audit

| Component | Demo | Documentation | Skill | Implementation |
|---|---|---|---|---|
| Header | BLOCKED | PARTIAL — chỉ tên file trong `structure.md` | MISSING | MISSING (file rỗng) |
| Sidebar | BLOCKED | PARTIAL — có trong `structure.md` (bằng chứng phụ: demo không có) | MISSING | MISSING (file rỗng) |
| Navigation | BLOCKED | CONFLICT — route `structure.md` khác route đã duyệt (CONFLICT-001) | MISSING | MISSING |
| Hanging Lamp / Pull Lamp | BLOCKED | MISSING | MISSING | MISSING |
| Theme Tối/Sáng | BLOCKED | MISSING | MISSING | MISSING |
| Card / Course Card / Card opening | BLOCKED | PARTIAL — chỉ tên `CourseCard.jsx` | MISSING | MISSING |
| Modal / ConfirmDialog | BLOCKED | PARTIAL — chỉ tên `Modal.jsx` | MISSING | MISSING |
| Drawer | BLOCKED | MISSING | MISSING | MISSING |
| Toast | BLOCKED | MISSING | MISSING | MISSING |
| Button / Input / Form / PasswordInput | BLOCKED | PARTIAL — `Button.jsx`; quy tắc mật khẩu ở D-AUTH-05 (nghiệp vụ, không UI) | MISSING | MISSING |
| Chat (Tutor, Consultant, ChatBubble) | BLOCKED | PARTIAL — `ChatWindow`, `MessageBubble`; ChatBubble MISSING | MISSING | MISSING |
| Learning Path / Node / Edge (PathGraph) | BLOCKED | PARTIAL — `PathGraph.jsx`, quy tắc node/cạnh (nghiệp vụ) | MISSING | MISSING |
| Review (làm bài, kết quả, lịch sử) | BLOCKED | PARTIAL — quy tắc không lộ đáp án, không gửi request cập nhật kỹ năng (`structure.md` §3) | PARTIAL — skill review có quy tắc response/không lộ đáp án | MISSING |
| Progress | BLOCKED | MISSING | MISSING | MISSING |
| Admin Table / Admin Panel | BLOCKED | PARTIAL — tên trang admin; không có `AdminLayout` | MISSING | MISSING |

---

## 8. Animation Audit

| Hạng mục | Demo | Documentation | Skill | Implementation |
|---|---|---|---|---|
| Duration / easing tokens | BLOCKED (bằng chứng phụ: `--d-*`, `--e-*`) | MISSING | MISSING | MISSING |
| Transition / hover / press | BLOCKED | MISSING | MISSING | MISSING |
| Entrance / exit / stagger | BLOCKED | MISSING | MISSING | MISSING |
| Modal / toast | BLOCKED | MISSING | MISSING | MISSING |
| Progress | BLOCKED | MISSING | MISSING | MISSING |
| Card opening | BLOCKED | MISSING | MISSING | MISSING |
| Chat (typing, gửi) | BLOCKED | MISSING | MISSING | MISSING |
| Learning path (vẽ cạnh, node vào/ra) | BLOCKED | MISSING | MISSING | MISSING |
| Review (chuyển câu, vòng điểm) | BLOCKED | MISSING | MISSING | MISSING |
| Reduced motion | BLOCKED | MISSING | MISSING | MISSING |
| Quy tắc "animation không đổi business state" | BLOCKED | PARTIAL — `structure.md` §3: "Trạng thái `completed` chỉ hiển thị sau khi nộp…; frontend chỉ tải lại dữ liệu" | PARTIAL — skill review: frontend không gửi request cập nhật kỹ năng | MISSING |

Không có SKILL OVER-SPECIFICATION (không skill/doc nào mô tả animation).

---

## 9. API Audit

API truth: `docs/api-endpoints.md`.

| Hạng mục | Demo API | Documentation API | Skill API | Implementation API | Kết luận |
|---|---|---|---|---|---|
| Auth/Profile (§2) | BLOCKED | PASS | PASS (`.claude`) · CONFLICT (`.agents` thiếu refresh) | MISSING | PARTIAL |
| Review (§10) | BLOCKED | PASS | PASS (`.claude`) · CONFLICT (`.agents` coi T16 là chốt) | MISSING | PARTIAL |
| Catalog, Bookmark, Tracking, Path, Node/Edge, Recommendation, Tutor, Admin (§3–§9, §11–§13) | BLOCKED | PASS (có endpoint) · response schema phần lớn chưa định nghĩa | MISSING | MISSING | PARTIAL |
| Feedback học viên, Admin feedback, Admin user paths, AI advisor, lưu bài dở (M1–M4) | BLOCKED (bằng chứng phụ cho thấy UI có) | **MISSING** | MISSING | MISSING | **API GAP** |
| Prefix `/api` vs `/api/v1` (nhánh `origin/Hoa`) | — | `/api` | `/api` | MISSING (nhánh hiện tại) | Nhánh Hoa chưa merge — NOT VERIFIABLE ảnh hưởng |

Không có skill/doc nào tự tạo endpoint ngoài `api-endpoints.md`.

---

## 10. User/Admin Role Audit

| Hạng mục | Documentation | Skill | Implementation | Kết luận |
|---|---|---|---|---|
| Register luôn tạo `student`, không nhận role | PASS (T09, AP-R01) | PASS (`auth-profile`) | MISSING | PASS (spec) |
| Admin chỉ tạo bằng `scripts/create_admin.py` | PASS | PASS | MISSING | PASS (spec) |
| Role lấy từ DB, không tin claim | PASS (D-AUTH-01, AP-R21) | PASS | MISSING | PASS (spec) |
| Login trả `role` | PASS (sheet Endpoint, AP-R07) | PASS | MISSING | PASS (spec) |
| Route guard frontend (`ProtectedRoute`, `AdminRoute`) | PASS (`structure.md` §1, §3) | MISSING | MISSING (file rỗng) | PARTIAL |
| "Ẩn nút admin không phải phân quyền" | PASS — `structure.md` §3: "backend vẫn kiểm tra quyền, frontend chỉ ẩn giao diện"; `backend-rules.md` §2 | MISSING (không nhắc) | MISSING | **Không có SECURITY CONFLICT** |
| Trang 403 / Unauthorized cho user vào `/admin/*` | MISSING | MISSING | MISSING | GAP |
| Demo (bằng chứng phụ): không có guard | NOT VERIFIABLE | — | — | Rủi ro khi sao chép demo |

---

## 11. Architecture Audit

| Hạng mục | Demo | Documentation | Skill | Implementation |
|---|---|---|---|---|
| Backend: Router → Service → Repository → Model | — | PASS (`structure.md` §4, `backend-rules.md` §1, `conventions.md` §3) | PASS | MISSING |
| Frontend: Page → Component → `api/*.api.js` → client | BLOCKED | PARTIAL — `conventions.md` §4 ("component không gọi `fetch` trực tiếp"), `structure.md` §3; không nêu axios/client interceptor/refresh | MISSING | MISSING |
| Cấu trúc thư mục frontend | BLOCKED (bằng chứng phụ: `pages/path`, `tracking`, `config`, `mock`) | `structure.md`: `pages/learning-path`, `store/`, `hooks/`, `Sidebar` | MISSING | 69 file rỗng theo `structure.md` → CONFLICT-002 |
| Mock tách khỏi production (`VITE_USE_MOCK`) | BLOCKED | MISSING | MISSING | MISSING |
| CSS Modules / design tokens | BLOCKED | MISSING | MISSING | MISSING |
| Thư viện frontend được phép (react-router-dom, axios) | BLOCKED | MISSING — `CLAUDE.md` chỉ ghi React + Vite; quy tắc "không thêm thư viện ngoài tài liệu" | MISSING | MISSING (`package.json` rỗng) → GAP |
| Lưu token | BLOCKED (bằng chứng phụ: `localStorage`) | `sessionStorage` (D-AUTH-01); cách gửi refresh token chưa chốt (ND-41/ND-48) | PASS (ghi PENDING) | MISSING |

---

## 12. Conflict Matrix

| ID | Source A | Source B | Issue | Impact | Severity |
|---|---|---|---|---|---|
| CONFLICT-001 | `docs/structure.md` §3 (route: `/profile`, `/learning-paths/new`, `/learning-paths`, `/review/:courseId`, `/review/history`) | Danh sách route đã duyệt cho Phase B (`/me…`, `/consultant`, `/me/learning-paths`, `/courses/:id/review…`, `/review-result/:id`, `/me/review-history…`, `/contact`, `/admin/*` 6 trang) | Hai bộ route khác nhau | Developer/agent đọc `structure.md` sẽ dựng sai route | **HIGH** |
| CONFLICT-002 | `docs/structure.md` §1 (frontend tree: `pages/learning-path`, `components/learning-path`, `store/`, `hooks/`, `Sidebar`, `AdminRelationsPage`) | Cấu trúc demo theo `README (1).md` (ngoài repo: `pages/path`, `tracking`, `feedback`, `config`, `mock`, không `Sidebar`) | Hai cấu trúc thư mục; G2 chưa chốt | Tạo trùng/thừa thư mục | **HIGH** |
| CONFLICT-003 | `README.md` (repo) | `README (1).md` (ngoài repo) | Bản ngoài repo có demo, 14 tính năng + phân công, M1–M4, route map; bản repo không có, và trỏ `docs/structure.md` trong khi bản ngoài repo trỏ `STRUCTURE.md` ở root | Merge sẽ xung đột; nguồn README không thống nhất | MEDIUM |
| CONFLICT-004 | `CLAUDE.md` "Phạm vi đang phụ trách" + `decisions.md` D-OWN-01 + 2 skill (chỉ Auth/Profile + Review; "không tự sửa file module khác") | Quyết định G1 của người dùng (Phase B = 14 tính năng) | Chỉ thị agent cấm đúng việc đã được duyệt | Agent sẽ từ chối hoặc vi phạm chỉ thị project | **HIGH** |
| CONFLICT-005 | `.agents/skills/*`, `AGENTS.md` | `.claude/skills/*`, `CLAUDE.md`, `decisions.md` | Bản Codex cũ: coi T16 là chốt, thiếu refresh token/D-AUTH, đường dẫn `.Codex/skills` sai | Codex có thể implement rule chưa chốt | **HIGH** |
| CONFLICT-006 | `CLAUDE.md` (giao diện tham khảo = `docs/wireframes/`), `decisions.md` (ND dẫn wireframe) | G5 / thứ tự nguồn UI của người dùng (demo React > HTML > preview > `EduMentor-UI-design`) | Nguồn UI chính thức chưa được ghi vào docs | Agent dùng sai nguồn thiết kế | MEDIUM |
| CONFLICT-007 | `decisions.md` D-AUTH-01 (định hướng `sessionStorage`) | Demo (bằng chứng phụ: `localStorage`) | Lưu token khác nhau | Sao chép demo sẽ vi phạm quyết định | MEDIUM (NOT VERIFIABLE theo nguồn) |
| CONFLICT-008 | `docs/api-endpoints.md` (không có Feedback/User paths/AI advisor/lưu bài dở) | UI demo (bằng chứng phụ, `README (1).md` M1–M4) | UI có nhưng API không có | 4 nhóm màn hình chỉ có thể làm UI, API PENDING | HIGH |

---

## 13. Gap Matrix

| ID | Loại | Source | Location | Current | Expected | Impact | Severity |
|---|---|---|---|---|---|---|---|
| GAP-001 | DOCUMENTATION GAP | Demo | `docs/ui-animation/demo/…`, `UX-UI-ANIMATION-PREVIEW.md` | Không có trong repo | Có mã nguồn demo + preview | Mọi đối chiếu demo bị BLOCKED | **CRITICAL** |
| GAP-002 | SKILL GAP | Skill | `.claude/skills/` | Không có skill frontend/UI | Skill frontend: phạm vi, nguồn demo, kiến trúc Page→API, token, theme, animation, reduced-motion, guard | Agent không có chỉ dẫn UI | **HIGH** |
| GAP-003 | SKILL GAP | Skill | 12 tính năng ngoài Auth/Profile, Review | Không có skill | Skill hoặc mục trong skill frontend cho từng nhóm | Thiếu điểm vào cho 12 tính năng | HIGH |
| GAP-004 | DOCUMENTATION GAP | Docs | `docs/` | Không có tài liệu UI/UX/component/design system | Tài liệu design system (token, component, layout) dẫn tới demo | Không truy vết được UI | HIGH |
| GAP-005 | ANIMATION GAP | Docs + Skill | — | Không mô tả animation, reduced-motion | Tài liệu motion (token, quy tắc, reduced-motion, animation ≠ business state) | Không kiểm chứng được animation | HIGH |
| GAP-006 | API GAP | `api-endpoints.md` | §2, §10, mới | Thiếu Feedback (POST, GET liên hệ, admin list), Admin user paths, AI advisor, lưu bài dở | Nhóm quyết định thêm endpoint hoặc bỏ UI | 4 nhóm UI chỉ ở trạng thái API PENDING | HIGH |
| GAP-007 | ARCHITECTURE GAP | Docs | `conventions.md` §4 | 3 dòng quy ước frontend | Quy ước: axios client, interceptor, refresh, CSS Modules, `VITE_USE_MOCK`, cấu trúc thư mục chốt | Dễ lệch kiến trúc khi code | MEDIUM |
| GAP-008 | ARCHITECTURE GAP | `CLAUDE.md` | Công nghệ | Không liệt kê react-router-dom, axios | Danh sách dependency frontend được phép | Quy tắc "không thêm thư viện" chặn Phase B | MEDIUM |
| GAP-009 | SECURITY GAP | Docs | Route guard | Không có hành vi khi user thường vào `/admin/*` (403/Unauthorized page) | Mô tả luồng guard: chưa đăng nhập → `/login`; user → Unauthorized; admin → trang | Hành vi không thống nhất | MEDIUM |
| GAP-010 | UX GAP | Docs | Trạng thái loading/empty/error | Không mô tả | Quy ước hiển thị loading/empty/error/API PENDING | UI không đồng nhất | MEDIUM |
| GAP-011 | DOCUMENTATION GAP | `decisions.md` | §2 | Chưa ghi G0–G7 (nguồn UI, phạm vi 14 tính năng, cấu trúc, router…) | Ghi quyết định Phase A/B | Agent không thấy quyết định đã chốt | HIGH |
| GAP-012 | DOCUMENTATION GAP | `SETUP.md` | §3, §6 | Không có `VITE_USE_MOCK`, cách chạy demo | Bổ sung khi demo vào repo | Không chạy được demo | LOW |
| GAP-013 | COMPONENT GAP | Docs | `structure.md` | Không có AuthLayout, SettingsLayout, AdminLayout, Toast, Tabs, ThemeToggle, ChatBubble, CardOpening… | Danh sách component chốt theo demo | Thiếu component khi code | MEDIUM (NOT VERIFIABLE theo nguồn) |

---

## 14. Priority Fixes

Không thực hiện trong task này — chỉ đề xuất thứ tự:

1. **GAP-001** — đưa mã nguồn demo + `UX-UI-ANIMATION-PREVIEW.md` vào repo. Mọi bước sau phụ thuộc bước này.
2. **CONFLICT-004 + GAP-011** — ghi G0–G7 vào `decisions.md`; cập nhật `CLAUDE.md` (phạm vi 14 tính năng cho frontend, nguồn UI = demo React).
3. **CONFLICT-001, CONFLICT-002** — chốt G2 và cập nhật `structure.md` §1, §3 theo demo (giữ `ProtectedRoute`, `AdminRoute`).
4. **GAP-002, GAP-003** — tạo skill frontend (sau khi có demo), trỏ về tài liệu thay vì chép lại.
5. **GAP-004, GAP-005, GAP-007, GAP-008** — tài liệu design system/motion; bổ sung quy ước frontend và dependency được phép.
6. **CONFLICT-005** — đồng bộ hoặc loại bỏ `AGENTS.md`, `.agents/skills/*`.
7. **GAP-006, CONFLICT-008** — nhóm quyết định API cho M1–M4 (hoặc chấp nhận UI ở trạng thái API PENDING).
8. **ND-41, ND-48** — chốt cách gửi refresh token để viết được `client.js`.

---

## 15. Final Verdict

```text
SKILL STATUS:            FAIL
DOCUMENTATION STATUS:    PARTIAL
DEMO ALIGNMENT:          FAIL  (không chứng minh được — nguồn demo BLOCKED)
ARCHITECTURE ALIGNMENT:  PARTIAL
API ALIGNMENT:           PARTIAL
OVERALL:                 NOT READY
```

- **Đã giống demo ở đâu?** Không xác nhận được điểm nào — nguồn demo không có trong repo (BLOCKED). Các quy tắc nghiệp vụ mà UI phải tôn trọng (không lộ đáp án trước khi nộp, `completed` chỉ đến từ bài ôn tập đạt, frontend không gửi request cập nhật kỹ năng, guard frontend không phải phân quyền) đã có trong docs.
- **Chưa giống demo ở đâu?** Toàn bộ tầng UI/UX/animation: không có tài liệu, không có skill, không có code. Route và cấu trúc frontend trong `structure.md` khác bộ route đã duyệt (CONFLICT-001, 002).
- **Skill nào cần cập nhật?** Tạo mới skill frontend (GAP-002/003). Đồng bộ hoặc bỏ `.agents/skills/*` (CONFLICT-005). Hai skill `.claude` cần nêu rõ chúng chỉ phủ backend/API, và tham chiếu skill frontend khi có.
- **DOC nào cần cập nhật?** `decisions.md` (G0–G7), `CLAUDE.md` (phạm vi, nguồn UI, dependency), `structure.md` (route, cây frontend), `conventions.md` §4, `README.md` (hợp nhất với `README (1).md`), `SETUP.md` (demo, `VITE_USE_MOCK`), `api-endpoints.md` (M1–M4 khi nhóm chốt).
- **Conflict nguy hiểm?** CONFLICT-004 (chỉ thị agent cấm đúng phạm vi đã duyệt), CONFLICT-005 (Codex skill coi T16 là chốt), CONFLICT-001/002 (route và cấu trúc).
- **API mismatch?** Thiếu endpoint cho Feedback, Admin feedback, Admin user paths, AI advisor, lưu bài dở (GAP-006). Không có skill/doc nào tự tạo endpoint.
- **Security issue?** Không có xung đột bảo mật trong docs/skill hiện tại. GAP-009: chưa mô tả hành vi khi user thường vào `/admin/*`. Rủi ro khi sao chép demo (bằng chứng phụ: không có guard, token ở `localStorage`).
- **Có thể bắt đầu implementation chưa?** **Chưa** — thiếu nguồn demo (G0) và các xung đột HIGH ở §12 chưa được xử lý.
