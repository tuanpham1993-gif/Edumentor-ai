// Khối thông báo trạng thái dùng chung (module 01 · Tuấn · FĐ7, 08/11/2026).
// Dùng cho: trang 404, "Đang phát triển" (501), máy chủ không phục vụ (503).
// Nhóm khác dùng lại được, vd: <StatusPanel icon={...} title="..." actions={...}>Nội dung</StatusPanel>
//   icon     : 'tool' | 'server' | 'search'
//   tone     : 'accent' (mặc định) | 'danger'
//   code     : dòng mã nhỏ phía dưới, vd "Mã: 501 · Chưa hỗ trợ" (không bắt buộc)
//   fullPage : true → căn giữa cả màn hình (trang không có Header)
import styles from '../styles/StatusPanel.module.css';

const ICON_PROPS = {
  'aria-hidden': true,
  width: 30,
  height: 30,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.7,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};

const ICONS = {
  // cờ lê: đang làm
  tool: (
    <svg {...ICON_PROPS}>
      <path d="M14.7 6.3a4 4 0 0 0-5.4 5.1L3.6 17.1a1.5 1.5 0 0 0 2.1 2.1l5.7-5.7a4 4 0 0 0 5.1-5.4l-2.4 2.4-2.1-.4-.4-2.1z" />
    </svg>
  ),
  // máy chủ có dấu !
  server: (
    <svg {...ICON_PROPS}>
      <rect x="3" y="4" width="18" height="7" rx="2" />
      <rect x="3" y="13" width="18" height="7" rx="2" />
      <path d="M7 7.5h.01M7 16.5h.01M15 7.5h3M15 16.5h3" />
    </svg>
  ),
  // kính lúp: không tìm thấy
  search: (
    <svg {...ICON_PROPS}>
      <circle cx="11" cy="11" r="6.5" />
      <path d="m20 20-4.2-4.2M9 9l4 4M13 9l-4 4" />
    </svg>
  ),
};

export default function StatusPanel({
  icon = 'tool',
  tone = 'accent',
  title,
  code,
  actions,
  fullPage = false,
  children,
}) {
  const panel = (
    <div className={styles.panel} role="status">
      <span className={`${styles.icon} ${tone === 'danger' ? styles.danger : ''}`}>{ICONS[icon]}</span>
      <h2>{title}</h2>
      {children && <p>{children}</p>}
      {actions && <div className={styles.actions}>{actions}</div>}
      {code && <span className={styles.code}>{code}</span>}
    </div>
  );

  return fullPage ? <main className={styles.page}>{panel}</main> : panel;
}
