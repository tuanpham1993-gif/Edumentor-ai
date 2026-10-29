// Theme Sáng/Tối và tùy chọn giảm chuyển động — theo bản demo (docs/decisions.md D-FE-02).
// Chỉ lưu tùy chọn giao diện; không lưu token hay dữ liệu người dùng.
import { useSyncExternalStore } from 'react';

const THEME_KEY = 'em-theme';
const MOTION_KEY = 'em-motion';
const THEMES = ['dark', 'light'];
const MOTIONS = ['reduce', 'full'];
const DEFAULT_THEME = 'dark';

const listeners = new Set();
const root = () => document.documentElement;

function readStored(key, allowed) {
  try {
    const value = localStorage.getItem(key);
    return allowed.includes(value) ? value : null;
  } catch {
    return null;
  }
}

function writeStored(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch {
    // Trình duyệt chặn localStorage: vẫn áp dụng cho phiên hiện tại.
  }
}

let currentTheme = readStored(THEME_KEY, THEMES) ?? DEFAULT_THEME;

/** Áp theme và tùy chọn chuyển động đã lưu. Gọi trước khi render để không nháy màu. */
export function initTheme() {
  root().dataset.theme = currentTheme;
  const motion = readStored(MOTION_KEY, MOTIONS);
  if (motion) root().dataset.motion = motion;
}

export function getTheme() {
  return currentTheme;
}

function applyTheme(theme) {
  currentTheme = theme;
  root().dataset.theme = theme;
  writeStored(THEME_KEY, theme);
  listeners.forEach((notify) => notify());
}

/**
 * Đổi theme. Có View Transitions thì theme mới lan ra thành hình tròn từ `origin`
 * (toạ độ điểm bấm, 520ms); không có thì chuyển màu mượt qua class `theme-anim`.
 */
export function setTheme(theme, origin) {
  if (!THEMES.includes(theme) || theme === currentTheme) return;
  const el = root();

  if (prefersReducedMotion()) {
    applyTheme(theme);
    return;
  }

  if (document.startViewTransition && origin) {
    const { x, y } = origin;
    const radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
    document
      .startViewTransition(() => applyTheme(theme))
      .ready.then(() => {
        el.animate(
          { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`] },
          { duration: 520, easing: 'cubic-bezier(0.2, 0, 0, 1)', pseudoElement: '::view-transition-new(root)' },
        );
      })
      .catch(() => {});
    return;
  }

  el.classList.add('theme-anim');
  applyTheme(theme);
  setTimeout(() => el.classList.remove('theme-anim'), 400);
}

export function useTheme() {
  return useSyncExternalStore(
    (notify) => {
      listeners.add(notify);
      return () => listeners.delete(notify);
    },
    getTheme,
    () => DEFAULT_THEME,
  );
}

/** Có giảm chuyển động không: ưu tiên tùy chọn `data-motion`, sau đó tới cài đặt hệ điều hành. */
export function prefersReducedMotion() {
  if (typeof window === 'undefined') return false;
  const motion = root().dataset.motion;
  if (MOTIONS.includes(motion)) return motion === 'reduce';
  return Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches);
}

/** Đặt tùy chọn giảm chuyển động; `null` = theo cài đặt hệ điều hành. */
export function setMotion(motion) {
  if (motion === null) {
    delete root().dataset.motion;
    try {
      localStorage.removeItem(MOTION_KEY);
    } catch {
      // Bỏ qua khi không truy cập được localStorage.
    }
    return;
  }
  if (!MOTIONS.includes(motion)) return;
  root().dataset.motion = motion;
  writeStored(MOTION_KEY, motion);
}
