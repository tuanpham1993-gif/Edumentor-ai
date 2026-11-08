// Khung trang căn giữa cho Quên mật khẩu / Đã gửi / Đặt lại / Hết hiệu lực (FĐ4, theo màn demo).
// Header khách dùng chung (PublicHeader), 2 đèn trang trí luôn sáng, thẻ ở giữa.
// Thẻ dùng lại style `.card` của AuthLayout để giống hệt trang Đăng nhập.
import { Link } from 'react-router-dom';

import authStyles from './AuthLayout.module.css';
import styles from './CenterLayout.module.css';
import AuthScene from './AuthScene.jsx';
import PublicHeader from '../layout/PublicHeader.jsx';
import { BackArrowIcon } from './icons.jsx';

function DecorLamp({ side, delay, glowTop }) {
  return (
    <div className={styles.lamp} aria-hidden="true" style={{ ...side, animationDelay: `${delay}s` }}>
      <div className={styles.glow} style={{ top: glowTop }} />
      <svg width="120" height="330" viewBox="0 0 120 330">
        <line x1="60" y1="0" x2="60" y2="220" stroke="#2b2622" strokeWidth="3" />
        <path d="M32 220h56l20 50H12z" fill="#1b1a19" stroke="#3a342d" />
        <ellipse cx="60" cy="270" rx="48" ry="7" fill="#ffb347" />
        <circle cx="60" cy="277" r="11" fill="#ffd27a" />
        <line x1="82" y1="270" x2="82" y2="322" stroke="#6b5a40" />
        <circle cx="82" cy="326" r="4" fill="var(--accent)" />
      </svg>
    </div>
  );
}

export default function CenterLayout({ children }) {
  return (
    <div className={styles.page}>
      <AuthScene variant="ambient" />
      {/* Header khách dùng chung (08/11) — thay thanh trên riêng của trang này */}
      <PublicHeader />

      <DecorLamp side={{ left: '12%' }} delay={0} glowTop={70} />
      <DecorLamp side={{ right: '12%' }} delay={-2} glowTop={150} />

      <main className={styles.main}>
        <div className={authStyles.card}>{children}</div>
      </main>
    </div>
  );
}

/** "← Quay lại đăng nhập" */
export function BackToLogin({ center = false }) {
  return (
    <Link className={styles.back} to="/login" style={center ? { alignSelf: 'center' } : undefined}>
      <BackArrowIcon />
      Quay lại đăng nhập
    </Link>
  );
}

/** Vòng tròn phát sáng chứa icon. animation: 'fly' (gửi đi) | 'tick' (đồng hồ) */
export function Orb({ children, large = false, animation }) {
  const classes = [styles.orb, large && styles.orbLg, animation && styles[animation]];
  return <span className={classes.filter(Boolean).join(' ')}>{children}</span>;
}

export { styles as centerStyles };
