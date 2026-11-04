# Token quan sát được

Tài liệu dẫn xuất (D-DOC-06 (4), (6)). **Chưa phải Design System chính thức**: chỉ ghi lại các biến CSS (custom property) đang có trong hai file nguồn dưới đây, không đặt token mới. Khi khác file nguồn, file nguồn thắng.

| Ký hiệu | File nguồn | Vai trò |
|---|---|---|
| UI | [`docs/ui-design/html/app.css`](../ui-design/html/app.css) | CSS của bộ UI (D-FE-12) |
| FE | [`frontend/src/index.css`](../../frontend/src/index.css) | CSS của frontend (code) |

Chủ đề tối là mặc định (khối `:root`); chủ đề sáng ghi đè trong khối `:root[data-theme=light]` (UI) và `:root[data-theme='light']` (FE). Giá trị trong bảng chép theo FE; UI ghi cùng giá trị, chỉ khác cách viết số thập phân (ví dụ `.02` thay cho `0.02`).

Không có trong hai file nguồn, nên **không** ghi ở đây: token khoảng cách (spacing), thang cỡ chữ (typography scale), token bóng đổ hoàn chỉnh (chỉ có hai tham số `--shadow-rgb`, `--shadow-k`), token breakpoint.

## 1. Màu theo chủ đề — có ở cả UI và FE

UI: 65 token ở `:root`, 54 token ở chủ đề sáng. FE: cùng 65 token (thêm 6 token bo góc, mục 3), cùng 54 token ở chủ đề sáng.

### Nền, bề mặt, viền

| Token | Tối (`:root`) | Sáng |
|---|---|---|
| `--bg` | `#100e0c` | `#f6f1e9` |
| `--bg-deep` | `#0b0a09` | `#eee6d9` |
| `--bg-header` | `#121110` | `#fbf8f2` |
| `--card` | `#16171a` | `#fffdf9` |
| `--card-inner` | `#1c1d20` | `#f9f4ec` |
| `--card-border` | `#2c2b29` | `#e5dccd` |
| `--line` | `#221f1c` | `#ebe3d6` |
| `--input` | `#1f2024` | `#fffdf9` |
| `--input-border` | `#33322f` | `#dcd1bf` |
| `--outline` | `#3a3835` | `#cdc1ad` |
| `--surface-sunk` | `#131417` | `#f2ece2` |
| `--hover` | `#1a1b1e` | `#f4ede2` |
| `--row-hover` | `rgba(255, 255, 255, 0.02)` | `rgba(150, 110, 40, 0.05)` |
| `--header-glass` | `rgba(18, 17, 16, 0.92)` | `rgba(251, 248, 242, 0.9)` |
| `--card-fade` | `rgba(22, 23, 26, 0.92)` | `rgba(255, 253, 249, 0.96)` |
| `--code-bg` | `#0f1012` | `#f3ede3` |
| `--hero-dark` | `#070606` | `#efe5d5` |
| `--glass` | `rgba(16, 14, 12, 0.7)` | `rgba(255, 252, 246, 0.78)` |
| `--glass-border` | `rgba(255, 255, 255, 0.1)` | `rgba(120, 90, 40, 0.14)` |
| `--skeleton-hi` | `#1d1e21` | `#f6f0e6` |
| `--scrim` | `rgba(8, 7, 6, 0.7)` | `rgba(70, 52, 28, 0.32)` |
| `--scrim-strong` | `rgba(8, 7, 6, 0.78)` | `rgba(70, 52, 28, 0.42)` |

### Chữ

| Token | Tối (`:root`) | Sáng |
|---|---|---|
| `--text` | `#f3efe8` | `#2b2219` |
| `--text-muted` | `#a39d93` | `#786c5c` |
| `--text-soft` | `#c9c2b7` | `#4e4436` |
| `--text-dim` | `#8f897f` | `#998d7c` |

### Màu nhấn

| Token | Tối (`:root`) | Sáng |
|---|---|---|
| `--accent` | `#f5a524` | `#dc8a0c` |
| `--accent-hover` | `#ffc35c` | `#b97200` |
| `--on-accent` | `#1a1206` | `#fffaf0` |
| `--accent-soft-bg` | `#2e2414` | `#fcefd6` |
| `--accent-soft-fg` | `#f5c46d` | `#93570a` |
| `--accent-soft-border` | `#5a4220` | `#efcd92` |
| `--accent-tint` | `#2a2114` | `#fdf1db` |
| `--accent-tint-strong` | `#3a2a10` | `#fbe3b4` |
| `--lamp-glow` | `rgba(245, 165, 36, 0.26)` | `rgba(245, 165, 36, 0.18)` |

### Màu trạng thái

| Token | Tối (`:root`) | Sáng |
|---|---|---|
| `--info-bg` | `#1f2a36` | `#e6eff9` |
| `--info-fg` | `#a9c6e8` | `#2e5d8f` |
| `--info-border` | `#34465a` | `#bad1ea` |
| `--danger-bg` | `#2a1a17` | `#fcebe7` |
| `--danger-fg` | `#f4a58e` | `#ad3f28` |
| `--danger-border` | `#5a2e25` | `#efc0b5` |
| `--danger-icon` | `#f08a6c` | `#cf5236` |
| `--ok-bg` | `#16241a` | `#e7f4e9` |
| `--ok-fg` | `#a8e0b5` | `#2d7541` |
| `--ok-border` | `#2f5a3a` | `#b7dcc0` |

### Thành phần

| Token | Tối (`:root`) | Sáng |
|---|---|---|
| `--avatar-bg` | `#3a4150` | `#e8dfd1` |
| `--track` | `#26272b` | `#ebe3d6` |
| `--track-strong` | `#3a3b40` | `#d8cdbb` |
| `--chip-bg` | `#232427` | `#f0eadf` |
| `--node-bg` | `#1b1c20` | `#fffdf9` |
| `--node-border` | `#34363c` | `#d8cdbb` |
| `--edge` | `#6b6458` | `#b1a38c` |

### Bóng đổ (tham số)

| Token | Tối (`:root`) | Sáng |
|---|---|---|
| `--shadow-rgb` | `0, 0, 0` | `110, 80, 35` |
| `--shadow-k` | `1` | `0.32` |

## 2. Chuyển động — có ở cả UI và FE

Chỉ khai báo ở `:root`, không đổi theo chủ đề.

| Token | Giá trị |
|---|---|
| `--ease-out` | `cubic-bezier(0.22, 0.9, 0.24, 1)` |
| `--d-instant` | `80ms` |
| `--d-fast` | `0.15s` |
| `--d-base` | `0.22s` |
| `--d-slow` | `0.32s` |
| `--d-emph` | `0.6s` |
| `--e-std` | `cubic-bezier(0.2, 0, 0, 1)` |
| `--e-in` | `cubic-bezier(0, 0, 0.2, 1)` |
| `--e-exit` | `cubic-bezier(0.4, 0, 1, 1)` |
| `--e-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` |
| `--stagger` | `40ms` |

## 3. Bo góc — chỉ có ở FE

UI không khai báo token bo góc; `app.css` ghi trực tiếp giá trị `border-radius`.

| Token | Giá trị |
|---|---|
| `--r-sm` | `8px` |
| `--r-md` | `10px` |
| `--r-lg` | `12px` |
| `--r-xl` | `16px` |
| `--r-2xl` | `18px` |
| `--r-pill` | `999px` |

## 4. Biến cục bộ của thành phần — chỉ có ở UI

Khai báo trong lớp CSS của thành phần (tên lớp do công cụ build sinh ra), không phải token toàn cục.

| Lớp | Biến | Tối | Sáng |
|---|---|---|---|
| `._card_1tkz0_2` | `--mx` | `50%` | — |
| `._card_1tkz0_2` | `--my` | `0%` | — |
| `._cover_1tkz0_28` | `--cb` | `var(--cover-base, var(--card-inner))` | `var(--cover-base-l, var(--card-inner))` |
| `._cover_1tkz0_28` | `--ci` | `var(--cover-ink)` | `var(--cover-ink-l)` |
| `._cover_1tkz0_28` | `--cover-end` | `#121212` | `#fffaf2` |
| `._cover_1tkz0_28` | `--cover-line` | `rgba(255, 255, 255, .035)` | `rgba(120, 90, 40, .07)` |

## 5. Font và media query

Font không khai báo bằng token; đây là giá trị `font-family` ghi trực tiếp trong file.

| | UI | FE |
|---|---|---|
| `font-family` | `Be Vietnam Pro,system-ui,sans-serif`, `ui-monospace,SFMono-Regular,Menlo,monospace` | `'Be Vietnam Pro', system-ui, sans-serif` |
| `@media` | `(max-width: 1100px)`, `(max-width: 960px)`, `(max-width: 900px)`, `(max-width: 860px)`, `(max-width: 820px)`, `(max-width: 720px)`, `(max-width: 700px)`, `(max-width: 640px)`, `(max-width: 560px)`, `(max-width: 520px)`, `(prefers-reduced-motion: reduce)` | `(max-width: 720px)`, `(prefers-reduced-motion: reduce)` |

Các mốc `max-width` ở trên chỉ là giá trị đang có trong CSS, **không** phải breakpoint đã chốt; quy định kiểm thử responsive đang chờ ND-68.
