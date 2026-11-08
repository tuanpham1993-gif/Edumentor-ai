// Header cho trang cần đăng nhập (FĐ2; FĐ7 08/11: làm lại theo màn demo).
//   Logo · menu chính (gạch chân vàng ở mục đang mở) · (admin) Quản trị · avatar + tên → /me
//   Điện thoại: menu xuống hàng riêng, vuốt ngang; chỉ hiện avatar.
// Mục menu khai báo ở nav.js (dùng chung với Footer).
import { NavLink, useLocation } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth.js';
import { initials } from '../../utils/formatters.js';
import { BrandLogo } from '../auth/icons.jsx';
import styles from './Header.module.css';
import { ADMIN_NAV, MAIN_NAV } from './nav.js';

const linkClass = ({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`;

// Avatar sáng khi đang ở Hồ sơ / Cài đặt tài khoản (không sáng ở /me/courses, /me/learning-paths…)
const PROFILE_PATHS = ['/me', '/me/edit', '/me/password', '/me/skills'];

export default function Header() {
  const { user } = useAuth();
  const { pathname } = useLocation();
  const onProfile = PROFILE_PATHS.includes(pathname);
  const items = user?.role === 'admin' ? [...MAIN_NAV, ADMIN_NAV] : MAIN_NAV;

  return (
    <header className={styles.header}>
      {/* inner: khung 1200px giữa màn → thẳng hàng nội dung trang & header khách */}
      <div className={styles.inner}>
      <NavLink to="/me" className={styles.brand} aria-label="EduMentor AI — về trang hồ sơ">
        <BrandLogo />
        <span>
          EduMentor <b>AI</b>
        </span>
      </NavLink>

      <nav className={styles.nav} aria-label="Điều hướng chính">
        {items.map((item) => (
          <NavLink key={item.to} to={item.to} className={linkClass}>
            {item.text}
          </NavLink>
        ))}
      </nav>

      {user && (
        <NavLink
          to="/me"
          className={`${styles.user} ${onProfile ? styles.userActive : ''}`}
          aria-current={onProfile ? 'page' : undefined}
          title="Hồ sơ của bạn"
        >
          <span className={styles.avatar} aria-hidden="true">
            {user.avatar_url ? <img src={user.avatar_url} alt="" /> : initials(user.full_name)}
          </span>
          <span className={styles.name}>{user.full_name}</span>
        </NavLink>
      )}
      </div>
    </header>
  );
}
