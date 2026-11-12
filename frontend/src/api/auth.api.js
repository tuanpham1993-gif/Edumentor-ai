// API /api/auth/* (module 01 · Tuấn · FĐ1, 07/11/2026). Mỗi hàm = một endpoint backend.
// Hàm trả về `response.data`; lỗi thì ném ra (bắt bằng try/catch + parseApiError).
import client from './client.js';

// POST /auth/register → thông tin user (201)
export async function register({ fullName, email, password, confirmPassword }) {
  const response = await client.post('/auth/register', {
    full_name: fullName,
    email,
    password,
    confirm_password: confirmPassword,
  });
  return response.data;
}

// POST /auth/login → { access_token, refresh_token, token_type, user }
export async function login({ email, password }) {
  const response = await client.post('/auth/login', { email, password });
  return response.data;
}

// POST /auth/logout — thu hồi refresh token của phiên này (backend luôn trả 200)
export async function logout(refreshToken) {
  const response = await client.post('/auth/logout', { refresh_token: refreshToken });
  return response.data;
}

// POST /auth/forgot-password — luôn trả cùng một thông báo
export async function forgotPassword(email) {
  const response = await client.post('/auth/forgot-password', { email });
  return response.data;
}

// POST /auth/reset-password — token lấy từ link trong email
export async function resetPassword({ token, newPassword, confirmNewPassword }) {
  const response = await client.post('/auth/reset-password', {
    token,
    new_password: newPassword,
    confirm_new_password: confirmNewPassword,
  });
  return response.data;
}

// POST /auth/refresh do client.js tự gọi khi gặp 401 — không cần hàm riêng ở đây.
