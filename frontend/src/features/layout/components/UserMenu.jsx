// Menu avatar trên header (module 01 · Tuấn · 11/11/2026) — thay link avatar → /me.
//   - Máy tính: rê chuột vào avatar → sổ xuống; rời chuột → chờ 150ms mới đóng (không nhấp nháy).
//   - Bấm / chạm avatar cũng mở / đóng (điện thoại không có hover). Enter mở, Esc đóng, Tab đi qua từng mục.
//   - Mục (Tuấn chốt 11/11): Hồ sơ của tôi · Cài đặt tài khoản · Giao diện · Thông báo qua email · (admin) Quản trị
//     · Đăng xuất. (Kỹ năng của tôi / Lịch sử ôn tập đã bỏ khỏi menu — vẫn vào được từ Hồ sơ / menu Ôn tập.)
import { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

import { useAuth } from '../../../hooks/useAuth.js';
import { initials, roleLabel } from '../../../utils/formatters.js';
import LogoutDialog from '../../profile/components/LogoutDialog.jsx';
import styles from '../styles/UserMenu.module.css';

const CLOSE_DELAY_MS = 150;

const ICONS = {
  profile: <path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" />,
  settings: (
    <>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" />
    </>
  ),
  appearance: <path d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9z" />,
  mail: (
    <>
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="m3 7 9 6 9-6" />
    </>
  ),
  admin: <path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z" />,
  logout: <path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 17l-5-5 5-5M5 12h11" />,
};

function Icon({ name }) {
  return (
    <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      {ICONS[name]}
    </svg>
  );
}

// Avatar sáng khi đang ở Hồ sơ / Cài đặt tài khoản
const PROFILE_PATHS = ['/me', '/me/edit', '/me/password', '/me/skills', '/me/skills/browse', '/me/appearance', '/me/email-notifications'];

export default function UserMenu() {
  const { user } = useAuth();
  const { pathname } = useLocation();
  const [open, setOpen] = useState(false);
  const [logoutOpen, setLogoutOpen] = useState(false);
  const wrapRef = useRef(null);
  const triggerRef = useRef(null);
  const closeTimer = useRef(null);
  const canHover = useRef(typeof window !== 'undefined' && window.matchMedia?.('(hover: hover)').matches);

  const onProfile = PROFILE_PATHS.includes(pathname);
  const items = [
    { to: '/me', text: 'Hồ sơ của tôi', icon: 'profile' },
    { to: '/me/password', text: 'Cài đặt tài khoản', icon: 'settings' }, // 12/11: mở thẳng trang Đổi mật khẩu
    { to: '/me/appearance', text: 'Giao diện', icon: 'appearance' },
    { to: '/me/email-notifications', text: 'Thông báo qua email', icon: 'mail' },
    ...(user?.role === 'admin' ? [{ to: '/admin', text: 'Quản trị', icon: 'admin' }] : []),
  ];

  useEffect(() => setOpen(false), [pathname]); // đổi trang → đóng menu

  // Bấm ra ngoài / Esc → đóng
  useEffect(() => {
    if (!open) return undefined;
    const onDown = (event) => !wrapRef.current?.contains(event.target) && setOpen(false);
    const onKey = (event) => {
      if (event.key === 'Escape') {
        setOpen(false);
        triggerRef.current?.focus();
      }
    };
    document.addEventListener('mousedown', onDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  useEffect(() => () => clearTimeout(closeTimer.current), []);

  function hoverOpen() {
    if (!canHover.current) return;
    clearTimeout(closeTimer.current);
    setOpen(true);
  }
  function hoverClose() {
    if (!canHover.current) return;
    clearTimeout(closeTimer.current);
    closeTimer.current = setTimeout(() => setOpen(false), CLOSE_DELAY_MS);
  }

  if (!user) return null;

  return (
    <div className={styles.wrap} ref={wrapRef} onMouseEnter={hoverOpen} onMouseLeave={hoverClose}>
      <button
        ref={triggerRef}
        type="button"
        className={`${styles.trigger} ${onProfile ? styles.active : ''}`}
        aria-haspopup="menu"
        aria-expanded={open}
        // Máy có chuột: rê vào đã mở rồi → bấm thì GIỮ mở (nếu bấm lại đóng thì vừa rê vừa bấm sẽ tắt ngay menu).
        // Điện thoại / không hover: bấm để mở, bấm lại để đóng.
        onClick={() => (canHover.current ? setOpen(true) : setOpen((v) => !v))}
      >
        <span className={styles.avatar} aria-hidden="true">
          {user.avatar_url ? <img src={user.avatar_url} alt="" /> : initials(user.full_name)}
        </span>
        <span className={styles.name}>{user.full_name}</span>
        <svg className={`${styles.chevron} ${open ? styles.chevronUp : ''}`} aria-hidden="true" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>

      {open && (
        <div className={styles.menu} role="menu" aria-label="Tài khoản">
          <div className={styles.who}>
            <span className={styles.avatarLg} aria-hidden="true">
              {user.avatar_url ? <img src={user.avatar_url} alt="" /> : initials(user.full_name)}
            </span>
            <span className={styles.whoText}>
              <strong>{user.full_name}</strong>
              <span>{user.email}</span>
              <span className="chip chip-accent" style={{ alignSelf: 'flex-start' }}>
                {roleLabel(user.role)}
              </span>
            </span>
          </div>
          <div className={styles.sep} />
          {items.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              role="menuitem"
              className={`${styles.item} ${pathname === item.to ? styles.itemActive : ''}`}
              onClick={() => setOpen(false)}
            >
              <Icon name={item.icon} />
              {item.text}
            </Link>
          ))}
          <div className={styles.sep} />
          <button
            type="button"
            role="menuitem"
            className={`${styles.item} ${styles.danger} ${styles.logout}`}
            onClick={() => {
              setOpen(false);
              setLogoutOpen(true);
            }}
          >
            <Icon name="logout" />
            Đăng xuất
          </button>
        </div>
      )}

      <LogoutDialog open={logoutOpen} onClose={() => setLogoutOpen(false)} />
    </div>
  );
}
