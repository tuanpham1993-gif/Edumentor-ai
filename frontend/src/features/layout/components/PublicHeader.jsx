// Header cho KHÁCH (FĐ7, 08/11/2026) — dùng ở trang chủ, Đăng nhập, Đăng ký, Quên mật khẩu.
//   logo · Trang chủ · Khóa học · Tính năng · Về chúng tôi · nút Đăng nhập / Đăng ký
//
// Ở trang chủ ("/"): mục là neo #id, cuộn mượt tới phần tương ứng; phần đang xem tô vàng.
// Ở trang khác: bấm mục → về trang chủ + cuộn tới phần đó (HomePage đọc location.hash).
// Nút bên phải: đang ở /login → "Đăng ký" (đổi qua lại cho tiện); còn lại → "Đăng nhập".
import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

import { ArrowIcon, BrandLogo } from '../../common/components/icons.jsx';
import styles from '../styles/PublicHeader.module.css';

export const SECTIONS = [
  { id: 'top', text: 'Trang chủ' },
  { id: 'courses', text: 'Khóa học' },
  { id: 'features', text: 'Tính năng' },
  { id: 'about', text: 'Về chúng tôi' },
];

export default function PublicHeader() {
  const { pathname } = useLocation();
  const onHome = pathname === '/';
  const [active, setActive] = useState(onHome ? 'top' : null);
  const [scrolled, setScrolled] = useState(!onHome);

  useEffect(() => {
    if (!onHome) return undefined; // trang khác: header luôn có nền, không theo dõi cuộn

    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });

    // Phần nào chiếm giữa màn hình → mục đó sáng
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setActive(entry.target.id);
        });
      },
      { rootMargin: '-45% 0px -50% 0px' },
    );
    SECTIONS.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => {
      window.removeEventListener('scroll', onScroll);
      observer.disconnect();
    };
  }, [onHome]);

  const onLogin = pathname === '/login';
  const action = onLogin ? { to: '/register', text: 'Đăng ký' } : { to: '/login', text: 'Đăng nhập' };

  return (
    <header className={`${styles.header} ${scrolled ? styles.headerScrolled : ''}`}>
      <div className={styles.headerInner}>
        <Link to="/" className={styles.brand}>
          <BrandLogo />
          <span>
            EduMentor <b>AI</b>
          </span>
        </Link>

        <nav className={styles.nav} aria-label="Điều hướng trang chủ">
          {SECTIONS.map(({ id, text }) => {
            const className = `${styles.navLink} ${active === id ? styles.navActive : ''}`;
            return onHome ? (
              <a key={id} href={`#${id}`} className={className} aria-current={active === id ? 'true' : undefined}>
                {text}
              </a>
            ) : (
              <Link key={id} to={id === 'top' ? '/' : `/#${id}`} className={className}>
                {text}
              </Link>
            );
          })}
        </nav>

        <Link
          to={action.to}
          className={`btn btn-sm ${styles.loginBtn}`}
        >
          {action.text} <ArrowIcon />
        </Link>
      </div>
    </header>
  );
}
