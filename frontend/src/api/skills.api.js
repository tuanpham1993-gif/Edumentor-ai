// Danh mục kỹ năng (API của Hòa: GET /api/skills) — FĐ6, 08/11/2026.
// Chỉ trả kỹ năng đang bật (is_active). Dùng cho ô "Thêm kỹ năng" ở trang Kỹ năng của tôi.
import client from './client.js';

// → { total, data: [{ skill_id, skill, is_active }] } — limit tối đa 50 (backend chặn);
// skip: bỏ qua N kết quả đầu (nút "Xem thêm kết quả")
export async function searchSkills(keyword, limit = 20, skip = 0) {
  const response = await client.get('/skills', { params: { keyword, limit, skip } });
  return response.data;
}
