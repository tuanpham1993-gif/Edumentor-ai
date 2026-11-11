# SetUp CSS — cấu trúc frontend & CSS cho cả nhóm

> Áp dụng từ 08/11/2026 · Người lập: Tuấn (Claude hỗ trợ) · Hướng dẫn ngắn trong code: `frontend/src/features/README.md`
>
> **Đọc trước khi bắt đầu code giao diện cho tính năng của mình.**

---

## 1. Hai loại CSS — đặt đúng chỗ

| Loại | Đặt ở đâu | Ví dụ | Cách nạp |
|---|---|---|---|
| **CSS dùng chung** cho cả app (từ 2 tính năng trở lên cùng dùng) | `frontend/src/styles/` | màu theme, `.btn`, `.input`, `.card`, `.container` | `styles/index.css` `@import` — `main.jsx` đã import sẵn |
| **CSS riêng của 1 tính năng** | `frontend/src/features/<tính-năng>/styles/` | đèn trang Đăng nhập, đồ thị lộ trình, khung chat Tutor | **Tự nạp** khi component `import styles from '../styles/X.module.css'` |

> ⚠ `src/styles/` **không phải** CSS của riêng ai. CSS của tính năng nào để trong thư mục tính năng đó.

## 2. Cấu trúc thư mục

```
frontend/src/
├── main.jsx                 import './styles/index.css' (một lần duy nhất)
├── styles/                  CSS DÙNG CHUNG
│   ├── index.css            chỉ chứa @import, ĐÚNG THỨ TỰ
│   ├── tokens.css           màu theme Tối / Sáng, tốc độ chuyển động, bo góc
│   ├── base.css             reset, body, font, link, focus
│   ├── animations.css       keyframes + .page-in, .enter, .stagger, .shake
│   ├── buttons.css          .btn, .btn-primary, .btn-danger, .btn-sm
│   ├── forms.css            .field, .input, .input.invalid, .field-error
│   ├── surfaces.css         .card, .chip, .alert, .muted, .small
│   ├── tables.css           bảng, skeleton đang tải
│   ├── layout.css           .container, .page-head, .row, .stack, .between
│   └── reduced-motion.css   tắt hiệu ứng khi người dùng chọn "giảm chuyển động" — LUÔN CUỐI
├── features/                MỖI TÍNH NĂNG MỘT THƯ MỤC (mục 3)
│   └── <tính-năng>/
│       ├── pages/           trang — gắn vào routes/index.jsx
│       ├── components/      component chỉ dùng trong tính năng này
│       └── styles/          CSS Module: <Component>.module.css
├── api/                     gọi backend: <tính-năng>.api.js (dùng client.js chung)
├── routes/  store/  hooks/  utils/
```

## 3. 14 tính năng — thư mục của từng người

Phân công theo `README.md`. Thư mục `features/` dưới đây là **quy ước**: tạo khi bắt đầu code tính năng đó.

| # | Tính năng | Người phụ trách | Thư mục frontend | Trạng thái |
|---|---|---|---|---|
| 01 | Tài khoản & hồ sơ — đăng ký, đăng nhập, quên/đặt lại mật khẩu, hồ sơ, ảnh đại diện, đổi mật khẩu, kỹ năng cá nhân | **Tuấn** | `features/auth/` + `features/profile/` | ✅ Đã có (kỹ năng cá nhân: FĐ6) |
| 02 | Danh mục khóa học — tìm kiếm, lọc theo kỹ năng/cấp độ, sắp xếp | **Khôi** | `features/courses/` | Chưa |
| 03 | Đánh dấu (bookmark) — lưu khóa học để học sau | **Tâm** | `features/bookmark/` | Chưa |
| 04 | Theo dõi tiến trình — `bookmarked` / `ongoing` / `completed` / `abandoned`, "Khóa học của tôi" | **Hòa** | `features/course-tracking/` | Chưa |
| 05 | AI Consultant — trò chuyện về mục tiêu để tạo lộ trình | **Hòa** | `features/consultant/` | Chưa |
| 06 | Lộ trình học tập — xem, quản lý lộ trình dạng đồ thị kỹ năng | **Hòa** | `features/learning-path/` | Chưa |
| 07 | Node & cạnh lộ trình — thêm/xóa node, cạnh, chọn node xem khóa học gợi ý | **Hòa** | `features/learning-path/` (chung với 06, component đồ thị trong `components/graph/`) | Chưa |
| 08 | AI Tutor — giải thích kiến thức, ví dụ mã, câu hỏi củng cố | **Tâm** | `features/tutor/` | Chưa |
| 09 | Ôn tập — bài 20 câu theo khóa học, kết quả, xem lại đáp án | **Tuấn** | `features/review/` | Chưa (backend GĐ 16–25/11) |
| 10 | Phản hồi — trang "Liên hệ & góp ý" | **Tâm** | `features/feedback/` | Chưa |
| 11 | Quản trị khóa học, kỹ năng | **Khôi** | `features/admin-courses/` | Chưa |
| 12 | Quản trị quan hệ kỹ năng — sơ đồ quan hệ | **Hòa** | `features/admin-skill-relations/` | Chưa |
| 13 | Quản trị phản hồi — xem, lọc, sắp xếp | **Tâm** | `features/admin-feedback/` | Chưa |
| 14 | Quản trị lộ trình người dùng — xem (chỉ đọc) lộ trình, tiến độ | **Hòa** | `features/admin-user-paths/` | Chưa |

Thư mục dùng chung (không thuộc riêng ai):

| Thư mục | Nội dung | Ghi chú |
|---|---|---|
| `features/layout/` | Header (học viên), PublicHeader (khách), Footer, PageBackdrop, PageLayout, `nav.js` | Thêm mục menu: **chỉ sửa `nav.js`** |
| `features/common/` | TextField, PasswordField, PasswordRules, icons, StatusPanel, ComingSoon, trang 404 / 503 | Component ai cũng dùng được |
| `features/home/` | Trang chủ cho khách `/` | Khóa học nổi bật đang là dữ liệu mẫu — thay khi có API của Khôi |

Trang của tính năng **chưa làm** đang hiện "Tạm thời chưa khả dụng" (`ComingSoon`). Khi làm xong, thêm route trang thật vào `routes/index.jsx` **phía trên** dòng `MAIN_NAV.map(...)` (đã ghi chú trong file).

## 4. Thêm CSS cho tính năng của bạn — 3 bước

```jsx
// 1. Tạo file:  src/features/courses/styles/CourseCard.module.css
//    .card { padding: 20px; border-radius: var(--r-lg); }
//    .title { color: var(--accent); }

// 2. Import trong component:  src/features/courses/components/CourseCard.jsx
import styles from '../styles/CourseCard.module.css';

// 3. Dùng — kết hợp class riêng (styles.x) với class chung (chuỗi)
export default function CourseCard({ course }) {
  return (
    <article className={`card ${styles.card}`}>
      <h3 className={styles.title}>{course.title}</h3>
      <button className="btn btn-primary">Xem khóa học</button>
    </article>
  );
}
```

Tên class viết ngắn thoải mái (`.card`, `.title`): CSS Module tự đổi thành tên duy nhất (vd `_card_182pj_28`), nên **không bao giờ trùng** với tính năng của người khác.

## 5. Quy tắc

| ✅ Được | ❌ Không được |
|---|---|
| Import CSS trong `styles/` **của chính tính năng mình** | Import `.module.css` của tính năng người khác |
| Dùng **component** của tính năng khác (vd `TextField` từ `common`) — component tự mang CSS | Copy CSS của người khác sang file mình |
| Dùng biến màu `var(--accent)`, `var(--card)`… trong `tokens.css` | Viết mã màu cứng (`#f5a524`) — theme Sáng sẽ sai |
| CSS chung giữa nhiều component **trong cùng tính năng** → 1 file riêng trong `styles/` (vd `auth/styles/AuthCard.module.css`) | Viết `style={{…}}` cho thứ lặp lại nhiều lần |
| Đề xuất đưa vào `src/styles/` khi **≥ 2 tính năng** cần cùng một kiểu | Sửa `src/styles/*` cho riêng một trang — ảnh hưởng **cả app** |
| Thêm file vào `src/styles/` → thêm `@import` vào `styles/index.css` **đúng thứ tự** (trước `reduced-motion.css`) | Đặt `@keyframes` dùng chung trong module của mình |

Trước khi đẩy code: `npm run build` không lỗi + mở thử ở chế độ **Tối và Sáng**, khổ **điện thoại** (DevTools → 375px) và **laptop**.

## 6. Hỏi nhanh

| Tôi muốn… | Làm ở đâu |
|---|---|
| Đổi màu chủ đạo / màu theme | `styles/tokens.css` — báo nhóm trước |
| Thêm kiểu nút mới dùng nhiều nơi | `styles/buttons.css` |
| Thêm mục menu trên header / footer | `features/layout/nav.js` |
| Trang mới cần layout có header + footer | Đặt route trong nhóm `<PageLayout />` ở `routes/index.jsx` |
| Hiện "đang phát triển" cho trang chưa xong | `<ComingSoon feature="Tên tính năng" />` |
| Hiệu ứng vào trang | class chung `page-in`, `enter`, `stagger` (`styles/animations.css`) |

## 7. Việc còn lại / đề xuất (chờ chốt)

- [ ] **Chia `src/styles/` thành thư mục con** khi phần dùng chung tăng lên (đề xuất của Tuấn, 08/11):
  `foundation/` (tokens, base) · `components/` (buttons, forms, surfaces, tables, sau này modal, pagination…) · `layout/` · `motion/` (animations, reduced-motion). `main.jsx` vẫn chỉ import `styles/index.css`.
- [ ] 39 chỗ `style={{…}}` trong code của Tuấn chuyển thành class.
- [ ] Gom keyframe lặp (`rise`, `breathe`…) — chưa làm vì các bản có thời gian/biên độ khác nhau.
- [ ] File khung rỗng cũ trong `src/components/*`, `src/pages/*` (course, review, tutor, admin…) — **chủ tính năng tự chuyển** sang `features/` khi bắt đầu làm.

## 8. Lịch sử thay đổi

**08/11/2026 — chuyển sang cấu trúc theo tính năng (Tuấn chọn "phương án A: CSS Module theo thư mục tính năng")**

- Trước: `index.css` 668 dòng ôm mọi thứ; CSS một tính năng rải ở `components/` lẫn `pages/`; 3 chỗ component "mượn" CSS của file khác.
- Làm: tách `index.css` → `src/styles/` (9 file); dời 57 file của Tuấn vào `src/features/{auth,profile,home,layout,common}` bằng `git mv` (giữ lịch sử), tự sửa import trong 34 file; tách `AuthCard.module.css`, `QuickStartCard.module.css` để bỏ "mượn" CSS.
- Kiểm chứng giao diện **không đổi**: file CSS build ra giống hệt từng byte sau khi tách / dời; sau khi tách file mượn, đo vị trí – kích thước – màu – font – khoảng cách của mọi phần tử trên 14 trang × 2 khổ màn hình so với bản cũ: giống hệt.
- Phương án B (mỗi tính năng 1 file CSS thường, nạp tự động bằng `import.meta.glob`) không chọn vì CSS thường là toàn cục — 4 người cùng code dễ trùng tên class.
