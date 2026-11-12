// Lấy trạng thái đăng nhập ở bất kỳ component nào (module 01 · Tuấn · FĐ2).
//   const { user, status, login, logout } = useAuth();
import { useContext } from 'react';

import { AuthContext } from '../store/authStore.js';

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error('useAuth() phải dùng bên trong <AuthProvider> (xem App.jsx).');
  }
  return value;
}
