// API quản trị ngân hàng câu hỏi ôn tập — module 09 (Tuấn · 16/11/2026 · 7.6 trang /admin/questions).
// Backend: backend/app/routers/v1/endpoints/admin/review_admin.py (prefix /api/admin/review, chỉ admin).
import client from './client.js';

// GET /admin/review/questions → { total, page, size, items: [QuestionListItem] }
//   params: review_status ('pending' | 'approved' | 'rejected'), source ('ai' | 'bank'), skill_id, type, level, q, page, size
export async function listQuestions(params = {}) {
  const response = await client.get('/admin/review/questions', { params });
  return response.data;
}

// GET /admin/review/questions/{id} → chi tiết: options + correct_index (TN), rubric + explanation (TL), versions
export async function getQuestion(questionId) {
  const response = await client.get(`/admin/review/questions/${questionId}`);
  return response.data;
}

// GET /admin/review/questions/{id}/suggested-code → { code } (vd "VAR-TN-15"; null = admin tự nhập)
export async function getSuggestedCode(questionId) {
  const response = await client.get(`/admin/review/questions/${questionId}/suggested-code`);
  return response.data.code;
}

// POST /admin/review/questions/{id}/approve — mã TÙY CHỌN: bỏ trống → hệ thống tự cấp mã gợi ý; câu được bật
export async function approveQuestion(questionId, code) {
  const response = await client.post(`/admin/review/questions/${questionId}/approve`, { code: code || null });
  return response.data;
}

// POST /admin/review/questions/{id}/reject — câu giữ lại ở trạng thái Từ chối (tắt), không vào đề
export async function rejectQuestion(questionId) {
  const response = await client.post(`/admin/review/questions/${questionId}/reject`);
  return response.data;
}

// POST /admin/review/questions/{id}/activate | deactivate → QuestionDetail (409: câu chờ duyệt / từ chối không bật được)
export async function setQuestionActive(questionId, active) {
  const response = await client.post(`/admin/review/questions/${questionId}/${active ? 'activate' : 'deactivate'}`);
  return response.data;
}

// GET /admin/review/readiness (7.4) → { target_per_skill, structure, courses: [...], courses_without_questions }
//   không course_id: mọi khóa đã có câu, CHỈ tóm tắt (skills rỗng) · course_id: 1 khóa kèm bảng từng kỹ năng
export async function getReadiness(courseId) {
  const response = await client.get('/admin/review/readiness', { params: courseId ? { course_id: courseId } : {} });
  return response.data;
}
