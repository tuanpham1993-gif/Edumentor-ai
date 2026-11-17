// API client cho Khóa học (Module 02 - Danh mục khóa học & Trang chủ).
// Tuân thủ quy ước: Page/Component -> courses.api.js -> client.js (Axios) -> Backend.
import client from './client.js';

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
