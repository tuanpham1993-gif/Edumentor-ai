// API client cho Khóa học (Module 02 - Danh mục khóa học & Trang chủ).
// Tuân thủ quy ước: Page/Component -> courses.api.js -> client.js (Axios) -> Backend.
import client from './client.js';
import { browseSkillCatalog } from './me.api.js';

/**
 * Lấy danh sách khóa học có hỗ trợ tìm kiếm, lọc theo cấp độ, sắp xếp và phân trang.
 * Endpoint: GET /api/courses
 *
 * @param {Object} [params]
 * @param {number} [params.page=1] - Số trang (bắt đầu từ 1)
 * @param {number} [params.page_size=10] - Số bản ghi mỗi trang (1-50)
 * @param {string} [params.search] - Từ khóa tìm kiếm
 * @param {number} [params.skill_id] - Mã kỹ năng cần lọc
 * @param {'beginner'|'intermediate'|'advanced'} [params.level] - Cấp độ khóa học
 * @param {'rating'|'num_reviews'} [params.sort_by] - Tiêu chí sắp xếp
 * @returns {Promise<{total: number, page: number, page_size: number, data: Array}>}
 */
export async function getCourses(params = {}) {
  const response = await client.get('/courses', { params });
  return response.data;
}

/**
 * Lấy thông tin chi tiết một khóa học theo course_id.
 * Endpoint: GET /api/courses/{course_id}
 *
 * @param {number|string} courseId
 * @returns {Promise<Object>}
 */
export async function getCourseDetail(courseId) {
  const response = await client.get(`/courses/${courseId}`);
  return response.data;
}

/**
 * Cấu hình 3 cấp độ chuẩn của hệ thống EduMentor AI cho trang chủ.
 */
export const FEATURED_LEVELS = [
  { key: 'beginner', label: 'Cơ bản', tone: 'ok' },
  { key: 'intermediate', label: 'Trung cấp', tone: 'info' },
  { key: 'advanced', label: 'Nâng cao', tone: 'accent' },
];

/**
 * Lấy 1 khóa học nổi bật nhất theo mỗi cấp độ (Cơ bản, Trung cấp, Nâng cao)
 * dựa vào số lượt đánh giá (num_reviews) cao nhất.
 *
 * @returns {Promise<Array<{key: string, label: string, tone: string, course: Object|null}>>}
 */
export async function getFeaturedCoursesByLevels() {
  const requests = FEATURED_LEVELS.map(async ({ key, label, tone }) => {
    try {
      const res = await getCourses({
        level: key,
        sort_by: 'num_reviews',
        page_size: 1,
        page: 1,
      });
      const course = res.data && res.data.length > 0 ? res.data[0] : null;
      return { key, label, tone, course };
    } catch (err) {
      // Giữ thông tin lỗi theo từng cấp độ để component xử lý linh hoạt
      return { key, label, tone, course: null, error: err };
    }
  });

  return Promise.all(requests);
}

/**
 * Tìm kiếm danh sách kỹ năng cho bộ lọc hoặc gợi ý.
 * Endpoint: GET /api/skills
 *
 * @param {Object} [params]
 * @param {string} [params.keyword] - Từ khóa tìm kiếm kỹ năng
 * @param {number} [params.skip=0] - Số bản ghi bỏ qua
 * @param {number} [params.limit=30] - Số kỹ năng tối đa (1-50)
 * @returns {Promise<{total: number, skip: number, limit: number, data: Array<{skill_id: number, skill: string, is_active: boolean}>}>}
 */
export async function getSkills(params = {}) {
  const response = await client.get('/skills', { params });
  return response.data;
}

/**
 * Lấy thông tin chi tiết một kỹ năng theo skill_id.
 * Endpoint: GET /api/skills/{skill_id}
 *
 * @param {number|string} skillId
 * @returns {Promise<{skill_id: number, skill: string, is_active: boolean}>}
 */
export async function getSkillDetail(skillId) {
  const response = await client.get(`/skills/${skillId}`);
  return response.data;
}

/**
 * Lấy danh sách kỹ năng sắp xếp theo độ phổ biến (nhiều khóa học nhất lên đầu)
 * kèm số lượng khóa học (course_count).
 * Ưu tiên GET /api/me/skills/catalog?sort=popular; tự động fallback sang GET /api/skills nếu 401.
 *
 * @param {Object} [params]
 * @param {string} [params.keyword=''] - Từ khóa tìm kiếm kỹ năng
 * @param {number} [params.page=1] - Số trang (bắt đầu từ 1)
 * @param {number} [params.size=60] - Số kỹ năng mỗi trang (tối đa 60)
 * @returns {Promise<{total: number, page: number, size: number, items: Array<{skill_id: number, skill: string, course_count: number|null}>}>}
 */
export async function getPopularSkills({ keyword = '', page = 1, size = 60 } = {}) {
  const trimmed = keyword.trim();
  const safeSize = Math.min(Math.max(1, size), 60);

  try {
    const res = await browseSkillCatalog({
      q: trimmed || undefined,
      sort: 'popular',
      page,
      size: safeSize,
    });
    return {
      total: res.total ?? 0,
      page: res.page ?? page,
      size: res.size ?? safeSize,
      items: (res.items || []).map((item) => ({
        skill_id: item.skill_id,
        skill: item.skill,
        course_count: typeof item.course_count === 'number' ? item.course_count : null,
      })),
    };
  } catch (err) {
    // Fallback an toàn khi chưa đăng nhập (401)
    if (err?.response?.status === 401) {
      const fallbackLimit = Math.min(safeSize, 50);
      const res = await getSkills({
        keyword: trimmed || undefined,
        skip: (page - 1) * fallbackLimit,
        limit: fallbackLimit,
      });
      return {
        total: res.total ?? 0,
        page,
        size: fallbackLimit,
        items: (res.data || []).map((s) => ({
          skill_id: s.skill_id,
          skill: s.skill,
          course_count: null,
        })),
      };
    }
    throw err;
  }
}
