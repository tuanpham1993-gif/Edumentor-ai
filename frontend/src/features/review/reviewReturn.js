// Nhớ "đến từ lộ trình nào" để màn Kết quả có nút "← Quay lại lộ trình" (module 09 · Tuấn · 20/11/2026 — mẫu
// review-on-graph). Huy hiệu ôn tập trên node ghi theo khóa; màn Bắt đầu chép sang bài làm khi tạo bài; màn Kết quả
// đọc theo bài làm. Lưu sessionStorage (theo tab) → tải lại trang vẫn còn; tab mới / đóng tab thì quên.
// Chỉ nhận đường dẫn trang lộ trình của chính app (không cho chuyển sang trang lạ).

const PREFIX = 'review-return:';
const ALLOWED = /^\/me\/my-learning-path\/[\w\-/]*$/;

export function isReturnPath(path) {
  return typeof path === 'string' && ALLOWED.test(path);
}

export function saveReturn(key, path) {
  if (!isReturnPath(path)) return;
  try {
    sessionStorage.setItem(PREFIX + key, path);
  } catch {
    /* trình duyệt chặn lưu → chỉ mất nút quay lại, không ảnh hưởng ôn tập */
  }
}

export function readReturn(key) {
  try {
    const path = sessionStorage.getItem(PREFIX + key);
    return isReturnPath(path) ? path : null;
  } catch {
    return null;
  }
}

export const courseKey = (courseId) => `course:${courseId}`;
export const skillKey = (skillId) => `skill:${skillId}`; // G2 (22/11): ôn theo kỹ năng
export const attemptKey = (attemptId) => `attempt:${attemptId}`;
