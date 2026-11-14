// API client cho Theo dõi khóa học & Đánh dấu (Module 03 - Bookmark & Module 04 - Course Tracking).
// Tuân thủ quy ước: Page/Component -> courseTracking.api.js -> client.js (Axios) -> Backend.
import client from './client.js';

/**
 * Lấy danh sách các khóa học học viên đã bookmark (lưu để học sau).
 * Endpoint: GET /api/me/bookmarks
 *
 * @param {number} [page=1]
 * @param {number} [pageSize=50]
 * @returns {Promise<{items: Array, total: number, page: number, page_size: number}>}
 */
export async function getMyBookmarks(page = 1, pageSize = 50) {
  const response = await client.get('/me/bookmarks', {
    params: { page, page_size: Math.min(pageSize, 50) },
  });
  return response.data;
}

/**
 * Thêm một khóa học vào danh sách đã lưu (bookmark).
 * Endpoint: POST /api/me/bookmarks
 *
 * @param {number} courseId
 * @returns {Promise<Object>}
 */
export async function addBookmark(courseId) {
  const response = await client.post('/me/bookmarks', { course_id: courseId });
  return response.data;
}

/**
 * Xóa một khóa học khỏi danh sách đã lưu.
 * Endpoint: DELETE /api/me/bookmarks/{course_id}
 *
 * @param {number} courseId
 * @returns {Promise<{message: string}>}
 */
export async function removeBookmark(courseId) {
  const response = await client.delete(`/me/bookmarks/${courseId}`);
  return response.data;
}

/**
 * Lấy danh sách khóa học của học viên (hỗ trợ lọc theo status: ongoing, completed, abandoned, bookmarked).
 * Endpoint: GET /api/me/courses
 *
 * @param {Object} [params]
 * @param {'ongoing'|'completed'|'abandoned'|'bookmarked'} [params.status]
 * @param {number} [params.page=1]
 * @param {number} [params.page_size=50]
 * @returns {Promise<{items: Array, total: number, page: number, page_size: number}>}
 */
export async function getMyCourses(params = {}) {
  const response = await client.get('/me/courses', { params });
  return response.data;
}

/**
 * Tham gia khóa học (ghi nhận status = ongoing và nhận link nền tảng gốc).
 * Endpoint: POST /api/courses/{course_id}/join
 *
 * @param {number} courseId
 * @returns {Promise<{course_id: number, title: str, status: string, url: string}>}
 */
export async function joinCourse(courseId) {
  const response = await client.post(`/courses/${courseId}/join`);
  return response.data;
}

/**
 * Lấy trạng thái theo dõi hiện tại của học viên đối với một khóa học.
 * Endpoint: GET /api/me/courses/{course_id}/status
 *
 * @param {number} courseId
 * @returns {Promise<{course_id: number, status: string|null, is_bookmarked: boolean}>}
 */
export async function getCourseStatus(courseId) {
  const response = await client.get(`/me/courses/${courseId}/status`);
  return response.data;
}

/**
 * Cập nhật trạng thái theo dõi (ongoing | abandoned | bookmarked).
 * Endpoint: PATCH /api/me/courses/{course_id}/status
 *
 * @param {number} courseId
 * @param {'ongoing'|'abandoned'|'bookmarked'} status
 * @returns {Promise<Object>}
 */
export async function updateCourseStatus(courseId, status) {
  const response = await client.patch(`/me/courses/${courseId}/status`, { status });
  return response.data;
}

/**
 * Ngừng theo dõi khóa học (chuyển ongoing sang abandoned).
 * Endpoint: DELETE /api/me/courses/{course_id}
 *
 * @param {number} courseId
 * @returns {Promise<Object>}
 */
export async function abandonCourse(courseId) {
  const response = await client.delete(`/me/courses/${courseId}`);
  return response.data;
}
