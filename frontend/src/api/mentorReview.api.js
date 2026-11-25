// API mentor duyệt câu ôn tập AI soạn — module 09 (Tuấn · G3f, 25/11/2026 — D19–D23).
// Backend: backend/app/routers/v1/endpoints/mentor_review.py (chỉ mentor + admin; học viên 403).
import client from './client.js';

// GET /mentor/review-questions → { items, total, page, size, counts: { pending, passed, reported } }
//   params: status ('pending' | 'passed' | 'reported'), skill_id, page, size
//   item: câu hỏi + chunk { title, content } (đoạn tài liệu AI dựa vào) + mentor_name + report { reason, note }
export async function listQueue(params = {}) {
  const response = await client.get('/mentor/review-questions', { params });
  return response.data;
}

// POST /mentor/review-questions/{id}/pass → { question_id, mentor_status: 'passed', is_active } · 409 đã duyệt / đang phản ánh
export async function passQuestion(questionId) {
  const response = await client.post(`/mentor/review-questions/${questionId}/pass`);
  return response.data;
}

// POST /mentor/review-questions/{id}/report — body { reason, note } → câu TẮT NGAY, chờ admin
//   reason: wrong_answer | ambiguous | wrong_knowledge | bad_rubric (chỉ tự luận) | other (bắt buộc ghi chú)
export async function reportQuestion(questionId, reason, note) {
  const response = await client.post(`/mentor/review-questions/${questionId}/report`, { reason, note: note || null });
  return response.data;
}
