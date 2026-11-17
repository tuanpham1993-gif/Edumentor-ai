import client from './client.js';

export const API_KEY_STORAGE_KEY = 'edumentor_gemini_api_key';

export function getStoredApiKey() {
  try {
    return localStorage.getItem(API_KEY_STORAGE_KEY) || '';
  } catch {
    return '';
  }
}

export function setStoredApiKey(key) {
  try {
    if (key && key.trim()) {
      localStorage.setItem(API_KEY_STORAGE_KEY, key.trim());
    } else {
      localStorage.removeItem(API_KEY_STORAGE_KEY);
    }
  } catch (err) {
    console.error('Không thể lưu API Key vào localStorage:', err);
  }
}

/**
 * 1. Tạo phiên chat mới
 * @param {string} topic - Tiêu đề hoặc chủ đề của phiên
 */
export async function createChatSession(topic = 'Phiên học tập mới') {
  const response = await client.post('/chat/sessions', { topic });
  return response.data;
}

/**
 * 2. Lấy danh sách các phiên chat của người dùng
 */
export async function getChatSessions() {
  const response = await client.get('/chat/sessions');
  return response.data;
}

/**
 * 3. Lấy chi tiết phiên chat bao gồm toàn bộ tin nhắn
 * @param {string} sessionId
 */
export async function getChatSessionDetail(sessionId) {
  const response = await client.get(`/chat/sessions/${sessionId}`);
  return response.data;
}

/**
 * 4. Lấy lịch sử tin nhắn trong một phiên
 * @param {string} sessionId
 */
export async function getChatMessages(sessionId) {
  const response = await client.get(`/chat/sessions/${sessionId}/messages`);
  return response.data;
}

/**
 * 5. Gửi tin nhắn trong phiên chat (nhận về câu trả lời và gợi ý)
 * @param {string} sessionId
 * @param {string} content
 * @param {string} [apiKey] - Gemini API Key tùy chọn của người dùng
 */
export async function sendChatMessage(sessionId, content, apiKey = null) {
  const customKey = apiKey || getStoredApiKey();
  const headers = customKey ? { 'X-Gemini-API-Key': customKey } : {};
  const response = await client.post(
    `/chat/sessions/${sessionId}/messages`,
    {
      content,
      api_key: customKey || undefined,
    },
    { headers }
  );
  return response.data;
}

/**
 * 6. Xóa một phiên chat
 * @param {string} sessionId
 */
export async function deleteChatSession(sessionId) {
  const response = await client.delete(`/chat/sessions/${sessionId}`);
  return response.data;
}

/**
 * 7. Chat công khai dành cho khách (không lưu phiên, không cần đăng nhập)
 * @param {string} content
 * @param {string} [apiKey] - Gemini API Key tùy chọn của người dùng
 */
export async function askPublicTutor(content, apiKey = null) {
  const customKey = apiKey || getStoredApiKey();
  const headers = customKey ? { 'X-Gemini-API-Key': customKey } : {};
  const response = await client.post(
    '/chat/ask',
    {
      content,
      api_key: customKey || undefined,
    },
    { headers }
  );
  return response.data;
}
