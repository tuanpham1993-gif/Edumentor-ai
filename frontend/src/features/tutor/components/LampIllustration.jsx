import styles from '../styles/LampIllustration.module.css';

/**
 * Đèn treo trang trí góc dưới bên trái sidebar theo bản thiết kế
 */
export default function LampIllustration() {
  return (
    <div className={styles.lampContainer} aria-hidden="true">
      <svg
        width="140"
        height="220"
        viewBox="0 0 140 220"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={styles.lampSvg}
      >
        {/* Dây treo đèn kéo từ trên xuống */}
        <line x1="70" y1="0" x2="70" y2="80" stroke="#3a3835" strokeWidth="2" />

        {/* Đui đèn */}
        <rect x="66" y="80" width="8" height="8" rx="1.5" fill="#5a5650" />

        {/* Chao đèn (chụp đèn dạng hình thang nón) */}
        <path
          d="M48 94L30 140H110L92 94H48Z"
          fill="#1c1d20"
          stroke="#2c2b29"
          strokeWidth="1.5"
        />

        {/* Vành dưới của chụp đèn */}
        <ellipse cx="70" cy="140" rx="40" ry="8" fill="#18191c" stroke="#33322f" strokeWidth="1" />

        {/* Quầng sáng tỏa ra từ bóng đèn */}
        <circle cx="70" cy="144" r="38" fill="url(#lampGlowRadial)" />

        {/* Bóng đèn vàng ấm áp */}
        <circle cx="70" cy="144" r="10" fill="#f5a524" className={styles.bulb} />

        {/* Dây giật công tắc nhỏ */}
        <line x1="78" y1="140" x2="78" y2="168" stroke="#5a5650" strokeWidth="1.2" strokeDasharray="2 2" />
        <circle cx="78" cy="170" r="2.5" fill="#f5a524" />

        <defs>
          <radialGradient
            id="lampGlowRadial"
            cx="0"
            cy="0"
            r="1"
            gradientUnits="userSpaceOnUse"
            gradientTransform="translate(70 144) rotate(90) scale(42 42)"
          >
            <stop stopColor="#f5a524" stopOpacity="0.45" />
            <stop offset="0.6" stopColor="#f5a524" stopOpacity="0.15" />
            <stop offset="1" stopColor="#f5a524" stopOpacity="0" />
          </radialGradient>
        </defs>
      </svg>
    </div>
  );
}
