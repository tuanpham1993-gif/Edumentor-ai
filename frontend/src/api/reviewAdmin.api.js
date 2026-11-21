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

// PATCH /admin/review/questions/{id} — chỉ gửi trường muốn đổi + minor ("Sửa nhỏ") + note (ghi chú phiên bản)
//   → { question: QuestionDetail (dòng MỚI nếu tạo phiên bản), versioned, changed }
//   422 { detail: { message, errors: [...] } } · 409 sửa nhỏ không hợp lệ · 400 kỹ năng / đoạn tri thức sai
export async function updateQuestion(questionId, body) {
  const response = await client.patch(`/admin/review/questions/${questionId}`, body);
  return response.data;
}

// GET /admin/review/skills/{skill_id}/chunks → [{ chunk_id, code, title }] (ô chọn "Đoạn tri thức")
export async function getSkillChunks(skillId) {
  const response = await client.get(`/admin/review/skills/${skillId}/chunks`);
  return response.data;
}

// POST /admin/review/questions → QuestionDetail (201; phiên bản 1, đã duyệt, bật). Không gửi mã → tự cấp mã gợi ý.
export async function createQuestion(body) {
  const response = await client.post('/admin/review/questions', body);
  return response.data;
}

// GET /admin/review/skills/{skill_id}/suggested-code?type=mcq|essay → mã gợi ý cho câu sắp thêm (null = tự nhập)
export async function getSkillSuggestedCode(skillId, type) {
  const response = await client.get(`/admin/review/skills/${skillId}/suggested-code`, { params: { type } });
  return response.data.code;
}

// ─── Bài cần xem lại (17/11/2026) ───
// GET /admin/review/flags → { items, total, page, size, open_total, resolved_total, reason_counts }
//   params: status ('open' | 'resolved' | 'all'), reason, course_id, page, size
export async function listFlags(params = {}) {
  const response = await client.get('/admin/review/flags', { params });
  return response.data;
}

// POST /admin/review/flags/{attempt_id}/{position}/resolve — body { labels: ['full'|'none', ...], note }
//   → { item, score_changed, passed_changed, completed_course }
export async function resolveFlag(attemptId, position, labels, note) {
  const response = await client.post(`/admin/review/flags/${attemptId}/${position}/resolve`, {
    labels,
    note: note || null,
  });
  return response.data;
}

// ─── Tìm kỹ năng theo tên (G1, 21/11/2026 — docs/Review-Skill-Search.md) ───
// GET /admin/review/skills/search?q=&limit= → { query, confident, results: [{ skill_id, skill, score, match, cosine,
//   aliases: [{ skill_id, skill }], active_questions, pending_questions }] }
export async function searchSkills(q, limit = 8) {
  const response = await client.get('/admin/review/skills/search', { params: { q, limit } });
  return response.data;
}
