// API thông báo — chuông trên header (module 01 · Tuấn · 11/11/2026). client.js tự gắn token + tự refresh.
// Backend: backend/app/routers/v1/endpoints/notifications.py
import client from './client.js';

// GET /me/notifications?unread_only=&page=&size= → { items, total, unread_count, page, size }
export async function getNotifications({ unreadOnly = false, page = 1, size = 20 } = {}) {
  const params = { page, size };
  if (unreadOnly) params.unread_only = true;
  const response = await client.get('/me/notifications', { params });
  return response.data;
}

// GET /me/notifications/unread-count → { unread_count } (chuông hỏi ~60 giây/lần)
export async function getUnreadCount() {
  const response = await client.get('/me/notifications/unread-count');
  return response.data.unread_count;
}

// PATCH /me/notifications/{id}/read
export async function markRead(notificationId) {
  const response = await client.patch(`/me/notifications/${notificationId}/read`);
  return response.data;
}

// POST /me/notifications/read-all → { updated }
export async function markAllRead() {
  const response = await client.post('/me/notifications/read-all');
  return response.data;
}
