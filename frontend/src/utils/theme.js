// Theme Sáng/Tối và tùy chọn giảm chuyển động — theo bản demo (docs/decisions.md D-FE-02).
// Chỉ lưu tùy chọn giao diện; không lưu token hay dữ liệu người dùng.
import { useSyncExternalStore } from 'react';

const THEME_KEY = 'em-theme';
const MOTION_KEY = 'em-motion';
const FONT_KEY = 'em-font';
const THEMES = ['dark', 'light'];
const THEME_CHOICES = ['dark', 'light', 'system']; // 'system' = theo Windows / điện thoại (11/11)
const MOTIONS = ['reduce', 'full'];
const FONTS = ['sm', 'md', 'lg']; // cỡ chữ nội dung bài học / câu hỏi ôn tập (11/11)
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

const systemDark = () => window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? true;
const resolve = (choice) => (choice === 'system' ? (systemDark() ? 'dark' : 'light') : choice);

let currentChoice = readStored(THEME_KEY, THEME_CHOICES) ?? DEFAULT_THEME;
let currentTheme = resolve(currentChoice);

/** Áp theme, chuyển động, cỡ chữ đã lưu. Gọi trước khi render để không nháy màu. */
export function initTheme() {
  root().dataset.theme = currentTheme;
  const motion = readStored(MOTION_KEY, MOTIONS);
  if (motion) root().dataset.motion = motion;
  const font = readStored(FONT_KEY, FONTS);
  if (font) root().dataset.font = font;
  // "Theo hệ thống": Windows / điện thoại đổi sáng ↔ tối thì trang đổi theo ngay
  window.matchMedia?.('(prefers-color-scheme: dark)').addEventListener?.('change', () => {
    if (currentChoice === 'system') applyTheme(resolve('system'), 'system');
  });
}

/** Lựa chọn của người dùng: 'dark' | 'light' | 'system'. */
export function getThemeChoice() {
  return currentChoice;
}

export function getTheme() {
  return currentTheme;
}

function applyTheme(theme, choice = theme) {
  currentTheme = theme;
  currentChoice = choice;
  root().dataset.theme = theme;
  writeStored(THEME_KEY, choice);
  listeners.forEach((notify) => notify());
}

/**
 * Đổi theme. Có View Transitions thì theme mới lan ra thành hình tròn từ `origin`
 * (toạ độ điểm bấm, 520ms); không có thì chuyển màu mượt qua class `theme-anim`.
 */
export function setTheme(choice, origin) {
  if (!THEME_CHOICES.includes(choice) || choice === currentChoice) return;
  const theme = resolve(choice);
  if (theme === currentTheme) {
    applyTheme(theme, choice); // vd đang Tối → "Theo hệ thống" (hệ thống cũng tối): chỉ đổi lựa chọn
    return;
  }
  const el = root();

  if (prefersReducedMotion()) {
    applyTheme(theme, choice);
    return;
  }

  if (document.startViewTransition && origin) {
    const { x, y } = origin;
    const radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
    document
      .startViewTransition(() => applyTheme(theme, choice))
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
  applyTheme(theme, choice);
  setTimeout(() => el.classList.remove('theme-anim'), 400);
}

/** Lựa chọn hiện tại ('dark' | 'light' | 'system') — trang Giao diện. */
export function useThemeChoice() {
  return useSyncExternalStore(
    (notify) => {
      listeners.add(notify);
      return () => listeners.delete(notify);
    },
    getThemeChoice,
    () => DEFAULT_THEME,
  );
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

/** Giảm chuyển động đang BẬT không (tùy chọn của người dùng, không tính cài đặt hệ điều hành). */
export function getMotionChoice() {
  return root().dataset.motion === 'reduce';
}

/** Cỡ chữ nội dung bài học / câu hỏi ôn tập: 'sm' | 'md' | 'lg' (mặc định 'md'). */
export function getFontSize() {
  return FONTS.includes(root().dataset.font) ? root().dataset.font : 'md';
}

export function setFontSize(size) {
  if (!FONTS.includes(size)) return;
  root().dataset.font = size;
  writeStored(FONT_KEY, size);
}
