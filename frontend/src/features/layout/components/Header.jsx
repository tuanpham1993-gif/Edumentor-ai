// Header cho trang cần đăng nhập (FĐ2; FĐ7 08/11: làm lại theo màn demo; 11/11: chuông + menu avatar).
//   Logo → /courses (trang chính sau đăng nhập — chốt 11/11; trang của Khôi, chưa xong thì hiện
//          "Tạm thời chưa khả dụng", Khôi làm xong tự chuyển tới trang thật)
//   · menu chính (gạch chân vàng ở mục đang mở) · (admin) Quản trị
//   · 🔔 chuông thông báo (TRƯỚC avatar) · avatar + tên ▾ (rê chuột / bấm → menu tài khoản)
//   Điện thoại: menu xuống hàng riêng, vuốt ngang; chỉ hiện chuông + avatar.
// Mục menu khai báo ở nav.js (dùng chung với Footer).
import { Link, NavLink, useLocation } from 'react-router-dom';

import { useAuth } from '../../../hooks/useAuth.js';
import { BrandLogo } from '../../common/components/icons.jsx';
import styles from '../styles/Header.module.css';
import { ADMIN_NAV, MAIN_NAV, activeNavItem } from '../nav.js';
import NotificationBell from './NotificationBell.jsx';
import UserMenu from './UserMenu.jsx';

export default function Header() {
  const { user } = useAuth();
  const { pathname } = useLocation();
  const items = user?.role === 'admin' ? [...MAIN_NAV, ADMIN_NAV] : MAIN_NAV;
  const active = activeNavItem(items, pathname); // mục đang mở (xét cả `match` trong nav.js)

  return (
    <header className={styles.header}>
      {/* inner: khung 1200px giữa màn → thẳng hàng nội dung trang & header khách */}
      <div className={styles.inner}>
      <NavLink to="/courses" className={styles.brand} aria-label="EduMentor AI — về trang chính">
        <BrandLogo />
        <span>
          EduMentor <b>AI</b>
        </span>
      </NavLink>

      <nav className={styles.nav} aria-label="Điều hướng chính">
        {items.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className={`${styles.link} ${item === active ? styles.active : ''}`}
            aria-current={item === active ? 'page' : undefined}
          >
            {item.text}
          </Link>
        ))}
      </nav>

      {user && (
        <div className={styles.account}>
          <NotificationBell />
          <UserMenu />
        </div>
      )}
      </div>
    </header>
  );
}
