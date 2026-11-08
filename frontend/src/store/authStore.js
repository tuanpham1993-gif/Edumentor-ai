// Trạng thái đăng nhập dùng chung cho cả app (module 01 · Tuấn · FĐ2, 07/11/2026).
//
// React Context = "kho dữ liệu chung": component nào cũng đọc được (qua useAuth()),
// không phải truyền user qua từng tầng component.
//
//   status : 'loading'  → đang kiểm tra (mở app có token → đang gọi GET /me)
//            'authenticated' → đã đăng nhập (user có dữ liệu)
//            'guest'    → khách
//            'error'    → có token nhưng KHÔNG tới được máy chủ (tắt / mất mạng / 5xx) — FĐ7 08/11
//                         giữ nguyên token, route hiện trang 503 + nút Thử lại (retry)
//   user   : { user_id, full_name, email, role, avatar_url, created_at } | null
//   login(email, password), logout(), refreshUser(), setUser(user), retry()
//
// File .js (không phải .jsx) nên dùng createElement thay cho cú pháp <Provider>.
import { createContext, createElement, useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import * as authApi from '../api/auth.api.js';
import { setOnSessionExpired } from '../api/client.js';
import * as meApi from '../api/me.api.js';
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from '../api/tokenStorage.js';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const navigate = useNavigate(); // AuthProvider phải nằm TRONG <BrowserRouter>
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState(() => (getAccessToken() ? 'loading' : 'guest'));

  // Mở app (hoặc F5) mà còn token → hỏi backend "tôi là ai". client.js tự refresh nếu access hết hạn.
  //   - 401 / 403 (phiên không còn hợp lệ) → xóa token, về khách.
  //   - Không tới được máy chủ / 5xx → GIỮ token, status 'error' (trang 503). Trước 08/11 chỗ này
  //     xóa token luôn → backend tắt một lúc là người dùng bị đăng xuất oan.
  const checkSession = useCallback(async () => {
    if (!getAccessToken()) {
      setStatus('guest');
      return;
    }
    try {
      const me = await meApi.getMe();
      setUser(me);
      setStatus('authenticated');
    } catch (err) {
      const code = err?.response?.status ?? 0;
      if (code === 0 || code >= 500) {
        setStatus('error');
        return;
      }
      clearTokens();
      setUser(null);
      setStatus('guest');
    }
  }, []);

  useEffect(() => {
    checkSession();
  }, [checkSession]);

  // client.js báo "hết phiên" (refresh thất bại) → về khách + chuyển /login kèm lý do.
  useEffect(() => {
    setOnSessionExpired(() => {
      setUser(null);
      setStatus('guest');
      navigate('/login', { replace: true, state: { expired: true } });
    });
  }, [navigate]);

  const login = useCallback(async (email, password) => {
    const data = await authApi.login({ email, password }); // lỗi → ném ra cho trang Login xử lý
    setTokens(data.access_token, data.refresh_token);
    setUser(data.user);
    setStatus('authenticated');
    return data.user;
  }, []);

  const logout = useCallback(async () => {
    const refreshToken = getRefreshToken();
    try {
      if (refreshToken) await authApi.logout(refreshToken); // thu hồi phiên trên server
    } catch {
      // Mạng lỗi vẫn đăng xuất phía trình duyệt.
    }
    clearTokens();
    setUser(null);
    setStatus('guest');
  }, []);

  const refreshUser = useCallback(async () => {
    const me = await meApi.getMe();
    setUser(me);
    return me;
  }, []);

  // useMemo: chỉ tạo object mới khi dữ liệu đổi → tránh vẽ lại thừa mọi component dùng useAuth().
  const value = useMemo(
    () => ({ user, status, login, logout, refreshUser, setUser, retry: checkSession }),
    [user, status, login, logout, refreshUser, checkSession],
  );

  return createElement(AuthContext.Provider, { value }, children);
}
