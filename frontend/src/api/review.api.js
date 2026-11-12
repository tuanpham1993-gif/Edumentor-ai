// API ôn tập — module 09 (Tuấn · GĐ4, 09/11/2026). client.js tự gắn token + tự refresh.
// Backend: backend/app/routers/v1/endpoints/review.py
import client from './client.js';

// GET /courses/{id}/review → { course_title, skills, structure, pass_score, can_start, blocked,
//                               in_progress_attempt_id, attempts }
export async function getReviewInfo(courseId) {
  const response = await client.get(`/courses/${courseId}/review`);
  return response.data;
}

// POST /courses/{id}/review-attempts → đề (AttemptOut). Đang có lượt dở → trả lượt đó, resumed=true.
export async function startReview(courseId) {
  const response = await client.post(`/courses/${courseId}/review-attempts`);
  return response.data;
}

// GET /review-attempts/{id} → đề + câu trả lời đã lưu (KHÔNG có đáp án)
export async function getAttempt(attemptId) {
  const response = await client.get(`/review-attempts/${attemptId}`);
  return response.data;
}

// PATCH /review-attempts/{id}/answers
//   answers: [{ position, selected_index }] (trắc nghiệm, null = bỏ chọn) | [{ position, text_answer }] (tự luận)
export async function saveAnswers(attemptId, answers) {
  const response = await client.patch(`/review-attempts/${attemptId}/answers`, { answers });
  return response.data;
}

// POST /review-attempts/{id}/submit → kết quả chi tiết (AttemptResultOut)
export async function submitAttempt(attemptId) {
  const response = await client.post(`/review-attempts/${attemptId}/submit`);
  return response.data;
}

// GET /me/review-history?course_id=&passed=&page=&size= → { items, total, page, size }
export async function getHistory({ courseId, passed, page = 1, size = 10 } = {}) {
  const params = { page, size };
  if (courseId) params.course_id = courseId;
  if (passed !== undefined && passed !== null) params.passed = passed;
  const response = await client.get('/me/review-history', { params });
  return response.data;
}

// GET /me/review-history/{id} → kết quả chi tiết của lượt đã nộp (đáp án đúng, giải thích, điểm từng ý)
export async function getResult(attemptId) {
  const response = await client.get(`/me/review-history/${attemptId}`);
  return response.data;
}
