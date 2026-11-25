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

// ─── Phạm vi ôn tập theo kỹ năng (G3.0, 24/11/2026) ───
// GET /admin/review/skill-scopes → { items: [{ skill_id, skill, label, category, reason, source, model, prompt_version,
//   updated_by_name, updated_at }], total, page, size, counts: { open, closed, unsure, unlabeled } }
//   params: label ('open' | 'closed' | 'unsure' | 'unlabeled'), category, source ('ai' | 'admin'), q, skill_id, page, size
export async function listSkillScopes(params = {}) {
  const response = await client.get('/admin/review/skill-scopes', { params });
  return response.data;
}

// PATCH /admin/review/skill-scopes/{skill_id} — body { label, category?, reason? } → nguồn "admin"
export async function updateSkillScope(skillId, body) {
  const response = await client.patch(`/admin/review/skill-scopes/${skillId}`, body);
  return response.data;
}

// ─── Kho đoạn tài liệu (G3a, 24/11/2026) ───
// POST /admin/review/skills/{skill_id}/chunks — body { title?, content } (200–1.500 ký tự) → đoạn mới (nguồn "admin")
export async function createSkillChunk(skillId, body) {
  const response = await client.post(`/admin/review/skills/${skillId}/chunks`, body);
  return response.data;
}

// POST /admin/review/skills/{skill_id}/chunks/generate → { created: [đoạn], existing }
//   AI viết các đoạn còn thiếu (tối đa 3 / kỹ năng), mất 10–30 giây → timeout riêng 120 giây
export async function generateSkillChunks(skillId) {
  const response = await client.post(`/admin/review/skills/${skillId}/chunks/generate`, null, { timeout: 120000 });
  return response.data;
}

// PATCH /admin/review/chunks/{chunk_id} — body { title?, content } → đoạn đã sửa (tính lại vector)
export async function updateChunk(chunkId, body) {
  const response = await client.patch(`/admin/review/chunks/${chunkId}`, body);
  return response.data;
}

// DELETE /admin/review/chunks/{chunk_id} → 204; đoạn đang là nguồn của câu hỏi → 409
export async function deleteChunk(chunkId) {
  await client.delete(`/admin/review/chunks/${chunkId}`);
}

// ─── Mentor phản ánh câu hỏi + tài khoản mentor (G3f, 25/11/2026 — D19–D23) ───
// GET /admin/review/reports → { items: [{ question, people, reason_counts, latest_at, reports: [...] }], total, page,
//   size, open_total }   params: status ('open' | 'handled' | 'all'), reason, skill_id, page, size
export async function listReports(params = {}) {
  const response = await client.get('/admin/review/reports', { params });
  return response.data;
}

// GET /admin/review/reports/count → { open_total } (số câu đang chờ xử lý)
export async function countReports() {
  const response = await client.get('/admin/review/reports/count');
  return response.data;
}

// POST /admin/review/reports/{question_id}/resolve — body { action: 'dismiss' (bác, bật lại) | 'keep_disabled', note? }
export async function resolveReports(questionId, action, note) {
  const response = await client.post(`/admin/review/reports/${questionId}/resolve`, { action, note: note || null });
  return response.data;
}

// GET /admin/review/mentors → [{ user_id, full_name, email, is_active, passed, reported }]
export async function listMentors() {
  const response = await client.get('/admin/review/mentors');
  return response.data;
}

// POST /admin/review/mentors — body { email } → 201 mentor · 404 không có tài khoản · 409 đã là mentor / là admin
export async function addMentor(email) {
  const response = await client.post('/admin/review/mentors', { email });
  return response.data;
}

// DELETE /admin/review/mentors/{user_id} → 204 (về học viên)
export async function removeMentor(userId) {
  await client.delete(`/admin/review/mentors/${userId}`);
}
