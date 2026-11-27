import client from './client.js';
import { getAccessToken } from './tokenStorage.js';

export const API_KEY_STORAGE_KEY = 'edumentor_gemini_api_key';

/**
 * Trích xuất ID người dùng hiện tại từ JWT access token.
 * Trả về chuỗi ID (ví dụ: "1", "2") hoặc null nếu chưa đăng nhập.
 */
export function getCurrentUserId() {
  try {
    const token = getAccessToken();
    if (!token) return null;
    const parts = token.split('.');
    if (parts.length >= 2) {
      const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      const data = JSON.parse(jsonPayload);
      return data.sub ? String(data.sub) : null;
    }
  } catch {
    return null;
  }
  return null;
}

/**
 * Tạo khóa lưu trữ riêng biệt theo ID người dùng:
 * Mỗi người dùng có một khóa riêng 'edumentor_gemini_api_key_user_<id>',
 * tránh việc các tài khoản dùng chung hoặc nhìn thấy API key của nhau.
 */
export function getApiKeyStorageKey(userId = null) {
  const uid = userId ? String(userId) : getCurrentUserId();
  if (uid) {
    return `edumentor_gemini_api_key_user_${uid}`;
  }
  return 'edumentor_gemini_api_key_guest';
}

export function getStoredApiKey(userId = null) {
  try {
    // Tự động dọn dẹp key dùng chung cũ nếu còn tồn tại trong trình duyệt
    if (localStorage.getItem(API_KEY_STORAGE_KEY)) {
      localStorage.removeItem(API_KEY_STORAGE_KEY);
    }
    const storageKey = getApiKeyStorageKey(userId);
    return localStorage.getItem(storageKey) || '';
  } catch {
    return '';
  }
}

export function setStoredApiKey(key, userId = null) {
  try {
    const storageKey = getApiKeyStorageKey(userId);
    if (key && key.trim()) {
      localStorage.setItem(storageKey, key.trim());
    } else {
      localStorage.removeItem(storageKey);
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
 * 6. Đổi tên phiên chat
 * @param {string} sessionId
 * @param {string} topic
 */
export async function renameChatSession(sessionId, topic) {
  const response = await client.patch(`/chat/sessions/${sessionId}`, { topic });
  return response.data;
}

/**
 * 7. Xóa một phiên chat
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
