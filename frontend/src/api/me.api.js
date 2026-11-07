// API /api/me* — hồ sơ người đang đăng nhập (module 01 · Tuấn · FĐ1, 07/11/2026).
// client.js tự gắn access token và tự refresh khi hết hạn.
import client from './client.js';

// GET /me → { user_id, full_name, email, role, avatar_url, created_at }
export async function getMe() {
  const response = await client.get('/me');
  return response.data;
}

// PATCH /me — chỉ sửa họ tên
export async function updateMe({ fullName }) {
  const response = await client.patch('/me', { full_name: fullName });
  return response.data;
}

// POST /me/change-password — thành công: backend thu hồi mọi refresh token (Q10)
export async function changePassword({ currentPassword, newPassword, confirmNewPassword }) {
  const response = await client.post('/me/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
    confirm_new_password: confirmNewPassword,
  });
  return response.data;
}

// POST /me/avatar — multipart/form-data, field "file" (PNG/JPEG ≤ 5 MB)
export async function uploadAvatar(file) {
  const form = new FormData();
  form.append('file', file);
  const response = await client.post('/me/avatar', form); // axios tự đặt Content-Type multipart
  return response.data;
}

// GET /me/skills, PATCH /me/skills, GET /me/summary: thêm ở FĐ6 khi backend GĐ4, 7.2 xong.
