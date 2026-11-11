// Khung "Cài đặt tài khoản" (module 01 · Tuấn · FĐ5, 07/11/2026) — theo màn demo EditProfile / ChangePassword.
//   nút Back (icon, về Hồ sơ) · tiêu đề · menu trái (Thông tin cá nhân, Mật khẩu, Kỹ năng của tôi, Giao diện,
//   Thông báo qua email, Đăng xuất — 11/11: công tắc giao diện nhỏ thay bằng trang Giao diện)
//   · khung phải = nội dung trang con (children).
import { useCallback, useState } from 'react';
import { NavLink } from 'react-router-dom';

import BackButton from '../../common/components/BackButton.jsx';
import LogoutDialog from './LogoutDialog.jsx';
import styles from '../styles/SettingsLayout.module.css';

const MENU = [
  { to: '/me/edit', text: 'Thông tin cá nhân' },
  { to: '/me/password', text: 'Mật khẩu' },
  { to: '/me/skills', text: 'Kỹ năng của tôi' },
  { to: '/me/appearance', text: 'Giao diện' }, // 11/11
  { to: '/me/email-notifications', text: 'Thông báo qua email' }, // 11/11
];

// back: nút Back trên cùng — mặc định về Hồ sơ; trang con sâu hơn truyền nơi khác
//   (vd Khám phá kỹ năng: { to: '/me/skills', label: 'Kỹ năng của tôi' }).
const DEFAULT_BACK = { to: '/me', label: 'Hồ sơ' };

export default function SettingsLayout({ children, back = DEFAULT_BACK }) {
  const [logoutOpen, setLogoutOpen] = useState(false);
  // useCallback: giữ nguyên hàm giữa các lần vẽ → hộp thoại không đặt lại con trỏ mỗi lần
  const closeLogout = useCallback(() => setLogoutOpen(false), []);

  return (
    <>
      <BackButton to={back.to} label={back.label} />
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
        </nav>

        <section className={`card ${styles.panel}`}>{children}</section>
      </div>

      <LogoutDialog open={logoutOpen} onClose={closeLogout} />
    </>
  );
}
