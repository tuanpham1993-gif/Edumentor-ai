// axios dùng chung cho MỌI lời gọi API (module 01 · Tuấn · FĐ1, 07/11/2026).
//
// 1. Tự gắn header "Authorization: Bearer <access_token>" vào mọi request.
// 2. Gặp 401 (access token hết hạn sau 30 phút) → tự gọi POST /auth/refresh → lưu cặp token mới
//    → GỬI LẠI request cũ. Người dùng không bị đá ra mỗi 30 phút.
// 3. Nhiều request cùng 401 một lúc → chỉ refresh MỘT lần, các request khác chờ chung kết quả.
//    (Backend xoay vòng refresh token: gửi cùng một token 2 lần → bị coi là đánh cắp
//     → thu hồi MỌI phiên. Refresh 2 lần song song sẽ tự đăng xuất người dùng.)
// 4. Refresh bị TỪ CHỐI (hết 7 ngày, đã đăng xuất, đổi mật khẩu… → 4xx) → xóa token → báo "hết phiên".
//    Refresh không tới được máy chủ (mất mạng / 5xx) → GIỮ token, chỉ báo lỗi (FĐ7 08/11).
//
// Các nhóm khác dùng lại file này: import client from '../api/client.js'.
import axios from 'axios';

import { clearTokens, getAccessToken, getRefreshToken, setTokens } from './tokenStorage.js';

// "/api" (tương đối) → đi qua proxy Vite sang backend :8000 (FĐ0).
const client = axios.create({ baseURL: '/api' });

// API không cần (hoặc không được) tự refresh khi 401: chính chúng là đăng nhập / làm mới.
const SKIP_REFRESH = [
  '/auth/login',
  '/auth/register',
  '/auth/refresh',
  '/auth/logout',
  '/auth/forgot-password',
  '/auth/reset-password',
];

// authStore (FĐ2) đăng ký hàm xử lý "hết phiên" (xóa user trong state, chuyển /login).
// Mặc định khi chưa đăng ký: chuyển thẳng tới trang đăng nhập.
let onSessionExpired = () => {
  if (typeof window !== 'undefined') window.location.assign('/login?expired=1');
};

export function setOnSessionExpired(handler) {
  onSessionExpired = handler;
}

// ---------- 1. Gắn access token vào mọi request ----------
client.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ---------- 3. Chỉ refresh một lần dù nhiều request cùng 401 ----------
let refreshPromise = null; // đang refresh → các request khác dùng chung Promise này

function refreshTokens() {
  if (!refreshPromise) {
    const refreshToken = getRefreshToken();
    refreshPromise = (
      refreshToken
        ? // Gọi bằng axios "trần" (không qua interceptor của client) để không tự lặp vô hạn.
          axios.post(`${client.defaults.baseURL}/auth/refresh`, { refresh_token: refreshToken })
        : Promise.reject(new Error('Không có refresh token'))
    )
      .then((response) => {
        const { access_token, refresh_token } = response.data;
        setTokens(access_token, refresh_token); // xoay vòng: lưu cặp MỚI
        return access_token;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

// ---------- 2 + 4. Gặp 401 → refresh → gửi lại ----------
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error;
    const shouldRefresh =
      response?.status === 401 &&
      config &&
      !config._retried && // mỗi request chỉ thử lại 1 lần, tránh vòng lặp
      !SKIP_REFRESH.some((path) => config.url?.startsWith(path));

    if (!shouldRefresh) return Promise.reject(error);

    config._retried = true;
    try {
      const newAccessToken = await refreshTokens();
      config.headers.Authorization = `Bearer ${newAccessToken}`;
      return client(config); // gửi lại request cũ với token mới
    } catch (refreshError) {
      const code = refreshError?.response?.status ?? 0;
      if (code === 0 || code >= 500) return Promise.reject(refreshError); // máy chủ lỗi ≠ hết phiên
      clearTokens();
      onSessionExpired();
      return Promise.reject(error);
    }
  },
);

export default client;
