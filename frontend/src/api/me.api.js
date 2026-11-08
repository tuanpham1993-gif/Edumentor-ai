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

// GET /me/skills?status=known|learning (FĐ6, 08/11) — không truyền status → tất cả
// → [{ skill_id, skill, status, source, updated_at }], sắp theo tên
export async function getMySkills(status) {
  const response = await client.get('/me/skills', { params: status ? { status } : undefined });
  return response.data;
}

// PATCH /me/skills — mọi thay đổi của MỘT lần bấm "Lưu" (FR-04):
//   { add: [{ skill_id, status }], update: [{ skill_id, status }], remove: [skill_id] }
// Thành công → danh sách kỹ năng SAU khi lưu. Lỗi: 409 đã có · 404 không có trong hồ sơ ·
// 422 không có trong danh mục — có lỗi là backend KHÔNG lưu gì.
export async function updateMySkills({ add = [], update = [], remove = [] }) {
  const response = await client.patch('/me/skills', { add, update, remove });
  return response.data;
}

// GET /me/skills/suggestions — gợi ý cho ô "Thêm kỹ năng" (FĐ6, 08/11), kỹ năng CHƯA có trong hồ sơ:
// [{ skill_id, skill, reason: 'next'|'related'|'popular', via?, course_count? }]
export async function getSkillSuggestions(limit = 12) {
  const response = await client.get('/me/skills/suggestions', { params: { limit } });
  return response.data;
}

// Trang "Khám phá kỹ năng" (FĐ6, 08/11 — gợi ý của thầy): danh mục + duyệt có phân trang
// → [{ key, label, count }]
export async function getSkillCategories() {
  const response = await client.get('/me/skills/catalog/categories');
  return response.data;
}

// params: { category?, q?, sort: 'popular'|'name', page, size }
// → { total, page, size, items: [{ skill_id, skill, category, course_count, my_status }] }
export async function browseSkillCatalog(params) {
  const response = await client.get('/me/skills/catalog', { params });
  return response.data;
}

// GET /me/summary (4 ô thống kê trên Hồ sơ): thêm khi backend 7.2 xong.
