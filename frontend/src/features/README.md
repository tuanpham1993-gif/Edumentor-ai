# `src/features/` — mỗi tính năng một thư mục

Áp dụng từ 08/11/2026. **Tài liệu đầy đủ cho cả nhóm (thư mục của 14 tính năng, quy tắc): `SetUp-CSS.md` ở thư mục gốc repo.**

```
src/
├── styles/                  CSS DÙNG CHUNG toàn app — main.jsx chỉ import styles/index.css
│   ├── tokens.css           màu theme Tối/Sáng, tốc độ chuyển động, bo góc
│   ├── base.css             reset, body, font, link, focus
│   ├── animations.css       keyframes + .page-in, .enter, .stagger, .shake
│   ├── buttons.css  forms.css  surfaces.css  tables.css  layout.css
│   └── reduced-motion.css   luôn nạp CUỐI
└── features/
    ├── auth/                Đăng nhập, Đăng ký, Quên / Đặt lại mật khẩu      (Tuấn · 01)
    ├── profile/             Hồ sơ, Sửa hồ sơ, Đổi mật khẩu, Kỹ năng            (Tuấn · 01)
    ├── home/                Trang chủ cho khách                               (Tuấn)
    ├── layout/              Header, PublicHeader, Footer, PageBackdrop, PageLayout, nav.js
    └── common/              ô nhập (TextField, PasswordField, PasswordRules), icons,
                             StatusPanel, ComingSoon, trang 404 / 503
```

Mỗi tính năng:

```
features/<tên>/
├── pages/        trang (gắn vào routes/index.jsx)
├── components/   component chỉ dùng trong tính năng này
└── styles/       CSS Module của tính năng: <Component>.module.css
```

## Thêm CSS cho một tính năng — 3 bước

1. Tạo file cạnh tính năng: `features/<tên>/styles/<Component>.module.css`
2. Trong component: `import styles from '../styles/<Component>.module.css';`
3. Dùng: `<div className={styles.card}>` — Vite **tự nạp** file CSS khi component hiện ra.

Tên class viết ngắn (`.card`, `.title`): CSS Module tự đổi thành tên duy nhất (vd `_card_182pj_28`),
nên **không bao giờ trùng** với class của tính năng khác.

## Quy tắc

| Được | Không được |
|---|---|
| Import CSS trong `styles/` **của chính tính năng đó** | Import file `.module.css` của tính năng khác |
| Dùng class chung trong `src/styles/` (`btn`, `card`, `input`, `stack`…) bằng chuỗi: `className="btn btn-primary"` | Viết lại màu bằng mã hex — dùng biến trong `tokens.css` (`var(--accent)`) |
| Dùng **component** của tính năng khác (vd `TextField` từ `common`) — component tự mang CSS của nó | Sửa `src/styles/*` cho riêng một trang — chỉ sửa khi thay đổi đúng là dùng chung |
| CSS chung giữa các component **trong cùng tính năng** → một file riêng trong `styles/` (vd `auth/styles/AuthCard.module.css`) | Đặt `@keyframes` dùng chung trong module — đưa vào `styles/animations.css` |

## Nhóm khác (Khôi, Tâm, Hòa)

Khi bắt đầu trang của mình, tạo thư mục mới theo cùng mẫu, ví dụ `features/courses/`, `features/tutor/`,
`features/learning-path/`, `features/review/` (Tuấn · 09), `features/admin/`.
Các file khung rỗng cũ trong `src/components/*` và `src/pages/*` vẫn để nguyên — chuyển sang `features/` khi làm thật.
