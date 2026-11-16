import styles from '../styles/TutorBotIcon.module.css';

/**
 * Icon/Mascot nhỏ của AI Tutor
 * @param {Object} props
 * @param {number} [props.size=28] - Kích thước icon (px)
 * @param {string} [props.className] - Class bổ sung nếu cần
 */
export default function TutorBotIcon({ size = 28, className = '' }) {
  return (
    <div
      className={`${styles.botIconWrapper} ${className}`}
      style={{ width: size, height: size }}
      title="EduMentor AI Tutor"
      aria-label="EduMentor AI Tutor"
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 36 36"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={styles.botSvg}
      >
        {/* Nền hình tròn phát sáng */}
        <circle cx="18" cy="18" r="17" fill="var(--card-inner)" stroke="var(--accent)" strokeWidth="1.5" />
        
        {/* Mũ học giả / Tai nghe cố vấn nhỏ phía trên */}
        <path
          d="M18 7L27 11.5L18 16L9 11.5L18 7Z"
          fill="var(--accent)"
        />
        <path
          d="M25 13.5V17.5"
          stroke="var(--accent)"
          strokeWidth="1.2"
          strokeLinecap="round"
        />
        <circle cx="25" cy="18.5" r="1" fill="var(--accent)" />

        {/* Mặt bot */}
        <rect
          x="11"
          y="15.5"
          width="14"
          height="11"
          rx="3.5"
          fill="var(--card)"
          stroke="var(--accent)"
          strokeWidth="1.2"
        />

        {/* Đôi mắt phát sáng công nghệ */}
        <circle cx="14.5" cy="20.5" r="1.6" fill="var(--accent)" className={styles.eyeBlink} />
        <circle cx="21.5" cy="20.5" r="1.6" fill="var(--accent)" className={styles.eyeBlink} />

        {/* Nụ cười vui vẻ */}
        <path
          d="M16 23.5Q18 25.5 20 23.5"
          stroke="var(--accent)"
          strokeWidth="1.2"
          strokeLinecap="round"
          fill="none"
        />
      </svg>
    </div>
  );
}
