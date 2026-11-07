// Nơi lưu token trên trình duyệt (module 01 · Tuấn · FĐ1, 07/11/2026).
//
// FQ1 (đề xuất, chờ chốt): localStorage → đóng tab vẫn còn đăng nhập (refresh token sống 7 ngày).
// Muốn đổi sang sessionStorage / bộ nhớ: CHỈ sửa file này, phần còn lại không đổi.
// Rủi ro đã biết: nếu trang dính lỗi XSS, script lạ đọc được token (ghi ở Q7 backend).
// Mọi lần đọc / ghi đều bọc try/catch: trình duyệt có thể chặn localStorage (chế độ riêng tư).

const ACCESS_KEY = 'em-access-token';
const REFRESH_KEY = 'em-refresh-token';

function read(key) {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key, value) {
  try {
    if (value) localStorage.setItem(key, value);
    else localStorage.removeItem(key);
  } catch {
    // Bị chặn: chấp nhận mất đăng nhập khi tải lại trang.
  }
}

export function getAccessToken() {
  return read(ACCESS_KEY);
}

export function getRefreshToken() {
  return read(REFRESH_KEY);
}

export function setTokens(accessToken, refreshToken) {
  write(ACCESS_KEY, accessToken);
  write(REFRESH_KEY, refreshToken);
}

export function clearTokens() {
  write(ACCESS_KEY, null);
  write(REFRESH_KEY, null);
}
