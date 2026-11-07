// Công tắc giao diện Tối / Sáng (module 01 · Tuấn · FĐ5, 07/11/2026) — FR-49.
// Lưu lựa chọn ở localStorage (utils/theme.js); theme mới lan ra từ điểm bấm.
//   compact: true → bản gọn trong menu Cài đặt tài khoản (không hiện chữ "Giao diện")
import { setTheme, useTheme } from '../../utils/theme.js';
import styles from './ThemeToggle.module.css';

const ICON_PROPS = {
  'aria-hidden': true,
  width: 15,
  height: 15,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};

function MoonIcon() {
  return (
    <svg {...ICON_PROPS}>
      <path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z" />
    </svg>
  );
}

function SunIcon() {
  return (
    <svg {...ICON_PROPS}>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
  );
}

const OPTIONS = [
  { value: 'dark', text: 'Tối', Icon: MoonIcon },
  { value: 'light', text: 'Sáng', Icon: SunIcon },
];

export default function ThemeToggle({ compact = false }) {
  const theme = useTheme();

  function choose(value, event) {
    // Bấm bằng bàn phím thì clientX/Y = 0 → lan từ giữa nút
    const rect = event.currentTarget.getBoundingClientRect();
    const x = event.clientX || rect.left + rect.width / 2;
    const y = event.clientY || rect.top + rect.height / 2;
    setTheme(value, { x, y });
  }

  // Nhóm radio: phím ← → đổi lựa chọn
  function handleKeyDown(event) {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    const next = theme === 'dark' ? 'light' : 'dark';
    const button = event.currentTarget.querySelector(`[data-value="${next}"]`);
    button?.focus();
    button?.click();
  }

  return (
    <div className={`${styles.wrap} ${compact ? styles.compact : ''}`}>
      {!compact && <span className={styles.label}>Giao diện</span>}
      <div
        className={`${styles.track} ${theme === 'light' ? styles.isLight : ''}`}
        role="radiogroup"
        aria-label="Giao diện"
        onKeyDown={handleKeyDown}
      >
        <span className={styles.knob} aria-hidden="true" />
        {OPTIONS.map(({ value, text, Icon }) => (
          <button
            key={value}
            type="button"
            role="radio"
            data-value={value}
            aria-checked={theme === value}
            tabIndex={theme === value ? 0 : -1}
            className={styles.opt}
            onClick={(event) => choose(value, event)}
          >
            <Icon />
            {text}
          </button>
        ))}
      </div>
    </div>
  );
}
