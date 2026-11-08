// Cảnh 3D chuyển động ánh sáng cho trang Đăng nhập / Đăng ký / Quên mật khẩu (FĐ7, 08/11/2026).
// CSS + SVG thuần (không thư viện, không ảnh GIF): nhẹ, nét ở mọi kích thước màn hình.
//
//   variant="hero"    : bên trái trang Đăng nhập / Đăng ký — 3 ô kính nổi 3D (mũ tốt nghiệp,
//                       sách, nút play), sóng ánh sáng chạy, hạt bụi sáng bay lên, bàn sách + chậu cây.
//   variant="ambient" : nền phía sau thẻ form — quầng sáng thở, hạt bụi, sóng sáng dưới đáy.
//   on                : đèn đang bật? Tắt → cảnh tối mờ, gần như không thấy (giữ ý tưởng kéo đèn).
//
// Toàn bộ là trang trí → aria-hidden. Người dùng chọn "giảm chuyển động" → index.css tắt hiệu ứng.
import styles from './AuthScene.module.css';

// Hạt bụi sáng: vị trí / cỡ / thời gian cố định (không random → mỗi lần vẽ giống nhau)
const PARTICLES = [
  [6, 3, 0, 11], [14, 2, 3.2, 9], [22, 4, 6.1, 13], [31, 2, 1.4, 10], [38, 3, 8.3, 12],
  [46, 2, 4.6, 9], [53, 4, 2.2, 14], [61, 2, 7.4, 10], [68, 3, 0.8, 12], [75, 2, 5.5, 11],
  [83, 4, 3.9, 13], [90, 2, 9.1, 10], [95, 3, 6.7, 12], [27, 2, 10.2, 9], [58, 3, 11.5, 11],
];

const ICON = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.6,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};

function Particles() {
  return (
    <div className={styles.particles}>
      {PARTICLES.map(([left, size, delay, duration]) => (
        <span
          key={`${left}-${delay}`}
          style={{
            left: `${left}%`,
            width: size,
            height: size,
            animationDelay: `-${delay}s`,
            animationDuration: `${duration}s`,
          }}
        />
      ))}
    </div>
  );
}

/** Sóng ánh sáng: 3 đường cong mờ + các vệt sáng chạy dọc theo đường. */
function Waves() {
  const paths = [
    'M-20 150 C 120 60, 260 210, 420 120 S 640 40, 720 110',
    'M-20 175 C 140 100, 300 230, 460 150 S 650 90, 720 140',
    'M-20 128 C 100 40, 240 170, 400 95 S 620 20, 720 80',
  ];
  return (
    <svg className={styles.waves} viewBox="0 0 700 240" preserveAspectRatio="none">
      <defs>
        <linearGradient id="em-wave" x1="0" x2="1">
          <stop offset="0" stopColor="#f5a524" stopOpacity="0" />
          <stop offset="0.35" stopColor="#ffc35c" stopOpacity="0.9" />
          <stop offset="0.7" stopColor="#f5a524" stopOpacity="0.7" />
          <stop offset="1" stopColor="#f5a524" stopOpacity="0" />
        </linearGradient>
      </defs>
      {paths.map((d, i) => (
        <g key={d}>
          <path d={d} className={styles.waveBase} stroke="url(#em-wave)" />
          <path
            d={d}
            className={styles.waveFlow}
            stroke="url(#em-wave)"
            style={{ animationDelay: `${-i * 1.7}s`, animationDuration: `${6 + i * 1.5}s` }}
          />
        </g>
      ))}
    </svg>
  );
}

/** Ô kính nổi 3D chứa icon phát sáng. */
function Tile({ className, children, size = 88 }) {
  return (
    <div className={`${styles.tile} ${className}`} style={{ '--tile': `${size}px` }}>
      <div className={styles.face}>
        <svg viewBox="0 0 48 48" width={size * 0.5} height={size * 0.5} {...ICON}>
          {children}
        </svg>
      </div>
      <span className={styles.reflect} />
    </div>
  );
}

/** Chồng sách + chậu cây trên mặt bàn, có quầng sáng. */
function Desk() {
  return (
    <div className={styles.desk}>
      <span className={styles.deskGlow} />
      <svg viewBox="0 0 220 170" width="220" height="170">
        {/* Chồng sách */}
        <rect x="18" y="128" width="118" height="20" rx="3" fill="#2a1d10" stroke="#5a4220" />
        <rect x="18" y="128" width="118" height="4" rx="2" fill="#f5a524" opacity=".55" />
        <rect x="28" y="108" width="100" height="20" rx="3" fill="#3a2a14" stroke="#6b4e22" />
        <rect x="28" y="108" width="100" height="4" rx="2" fill="#ffc35c" opacity=".5" />
        <rect x="22" y="90" width="108" height="18" rx="3" fill="#24180c" stroke="#5a4220" />
        <rect x="22" y="90" width="108" height="3" rx="1.5" fill="#f5a524" opacity=".45" />
        {/* Chậu cây */}
        <g className={styles.plant}>
          <path d="M165 72c-4-18 2-34 14-44-2 16-4 30-14 44z" fill="#6b8f3a" />
          <path d="M168 76c8-14 22-20 36-18-10 10-20 16-36 18z" fill="#82a84a" />
          <path d="M164 78c-12-10-28-12-40-6 12 8 24 10 40 6z" fill="#5d7f32" />
          <path d="M166 70c-2-20 6-38 22-50-4 18-8 34-22 50z" fill="#93b85a" />
        </g>
        <path d="M148 80h40l-6 68h-28z" fill="#e9dcc6" stroke="#b8a582" />
        <rect x="146" y="76" width="44" height="8" rx="3" fill="#f3e8d4" />
        {/* Mặt bàn */}
        <rect x="0" y="148" width="220" height="6" rx="3" fill="#1d1813" />
      </svg>
    </div>
  );
}

export default function AuthScene({ variant = 'hero', on = true }) {
  const rootClass = [styles.scene, styles[variant], on ? styles.on : styles.off].join(' ');

  if (variant === 'ambient') {
    return (
      <div className={rootClass} aria-hidden="true">
        <span className={styles.ambientGlow} />
        <Particles />
        <Waves />
      </div>
    );
  }

  return (
    <div className={rootClass} aria-hidden="true">
      <Waves />
      <Particles />

      {/* Mũ tốt nghiệp */}
      <Tile className={styles.tileCap} size={92}>
        <path d="M4 18 24 9l20 9-20 9z" />
        <path d="M12 22v9c0 3 5.5 6 12 6s12-3 12-6v-9" />
        <path d="M44 18v12" />
        <circle cx="44" cy="32" r="1.6" fill="currentColor" />
      </Tile>

      {/* Sách mở */}
      <Tile className={styles.tileBook} size={84}>
        <path d="M24 14c-5-3-11-4-18-3v24c7-1 13 0 18 3 5-3 11-4 18-3V11c-7-1-13 0-18 3z" />
        <path d="M24 14v24" />
        <path d="M10 18c3-.3 6 0 9 1M10 24c3-.3 6 0 9 1M29 19c3-1 6-1.3 9-1M29 25c3-1 6-1.3 9-1" />
      </Tile>

      {/* Nút play */}
      <Tile className={styles.tilePlay} size={58}>
        <path d="M19 14.5v19l15-9.5z" fill="currentColor" />
      </Tile>

      <Desk />
    </div>
  );
}
