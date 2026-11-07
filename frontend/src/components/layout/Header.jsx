// Header cho trang cần đăng nhập: logo, (admin) link quản trị, tên + avatar → hồ sơ. (FĐ2)
// Các mục Khóa học / Lộ trình / AI Tutor / Liên hệ của nhóm khác thêm vào `nav` khi có trang.
import { Link, NavLink } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth.js';
import { initials } from '../../utils/formatters.js';
import styles from './Header.module.css';

export default function Header() {
  const { user } = useAuth();

  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <Link to="/me" className={styles.brand}>
          EduMentor <span>AI</span>
        </Link>

        <nav className={styles.nav} aria-label="Điều hướng chính">
          {user?.role === 'admin' && (
            <NavLink to="/admin" className={styles.link}>
              Quản trị
            </NavLink>
          )}
          {user && (
            <NavLink
              to="/me"
              className={({ isActive }) => `${styles.user} ${isActive ? styles.active : ''}`}
            >
              <span className={styles.avatar} aria-hidden="true">
                {user.avatar_url ? <img src={user.avatar_url} alt="" /> : initials(user.full_name)}
              </span>
              <span className={styles.name}>{user.full_name}</span>
            </NavLink>
          )}
        </nav>
      </div>
    </header>
  );
}
