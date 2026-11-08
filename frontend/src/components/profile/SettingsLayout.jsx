// Khung "Cài đặt tài khoản" (module 01 · Tuấn · FĐ5, 07/11/2026) — theo màn demo EditProfile / ChangePassword.
//   ← Hồ sơ · tiêu đề · menu trái (Thông tin cá nhân, Mật khẩu, Đăng xuất, công tắc giao diện)
//   · khung phải = nội dung trang con (children).
import { useCallback, useState } from 'react';
import { Link, NavLink } from 'react-router-dom';

import LogoutDialog from './LogoutDialog.jsx';
import styles from './SettingsLayout.module.css';
import ThemeToggle from './ThemeToggle.jsx';

const MENU = [
  { to: '/me/edit', text: 'Thông tin cá nhân' },
  { to: '/me/password', text: 'Mật khẩu' },
  { to: '/me/skills', text: 'Kỹ năng của tôi' }, // tạm hiện "Tạm thời chưa khả dụng" tới FĐ6
];

export default function SettingsLayout({ children }) {
  const [logoutOpen, setLogoutOpen] = useState(false);
  // useCallback: giữ nguyên hàm giữa các lần vẽ → hộp thoại không đặt lại con trỏ mỗi lần
  const closeLogout = useCallback(() => setLogoutOpen(false), []);

  return (
    <>
      <Link to="/me" className="crumb">
        ← Hồ sơ
      </Link>
      <h1 className={styles.title}>Cài đặt tài khoản</h1>

      <div className={styles.layout}>
        <nav className={`card ${styles.menu}`} aria-label="Cài đặt tài khoản">
          {MENU.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `${styles.item} ${isActive ? styles.active : ''}`}
            >
              {item.text}
            </NavLink>
          ))}
          <button
            type="button"
            className={`${styles.item} ${styles.logout}`}
            onClick={() => setLogoutOpen(true)}
          >
            Đăng xuất
          </button>
          <div className={styles.theme}>
            <span>Giao diện</span>
            <ThemeToggle compact />
          </div>
        </nav>

        <section className={`card ${styles.panel}`}>{children}</section>
      </div>

      <LogoutDialog open={logoutOpen} onClose={closeLogout} />
    </>
  );
}
