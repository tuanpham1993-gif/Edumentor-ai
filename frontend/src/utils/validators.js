// Kiểm tra dữ liệu form PHÍA TRÌNH DUYỆT (FĐ3) — báo lỗi ngay, đỡ một lượt gọi server.
// Quy tắc mật khẩu GIỐNG HỆT backend `core/security.py` → validate_password (FR-48).
// Backend vẫn kiểm tra lại: đây chỉ giúp người dùng, không thay được kiểm tra ở server.

// 5 quy tắc hiển thị thành danh sách tích xanh / đỏ (PasswordRules).
export const PASSWORD_RULES = [
  { test: (pw) => pw.length >= 8, text: 'Tối thiểu 8 ký tự' },
  { test: (pw) => /[A-Z]/.test(pw), text: 'Có chữ hoa (A–Z)' },
  { test: (pw) => /[a-z]/.test(pw), text: 'Có chữ thường (a–z)' },
  { test: (pw) => /[0-9]/.test(pw), text: 'Có chữ số (0–9)' },
  { test: (pw) => /[^A-Za-z0-9]/.test(pw), text: 'Có ký tự đặc biệt (!@#$…)' },
];

/** Lỗi KHÔNG nằm trong 5 quy tắc trên (quá 72 byte) — hiện riêng dưới ô. */
export function passwordExtraError(password) {
  return new TextEncoder().encode(password).length > MAX_PASSWORD_BYTES
    ? `Mật khẩu quá dài (tối đa ${MAX_PASSWORD_BYTES} byte).`
    : null;
}

const MAX_PASSWORD_BYTES = 72; // giới hạn bcrypt

/** Trả câu lỗi đầu tiên (giống thông báo backend), hoặc null nếu hợp lệ. */
export function validatePassword(password) {
  if (password.length < 8) return 'Mật khẩu phải có tối thiểu 8 ký tự.';
  if (new TextEncoder().encode(password).length > MAX_PASSWORD_BYTES) {
    return `Mật khẩu quá dài (tối đa ${MAX_PASSWORD_BYTES} byte).`;
  }
  if (!/[A-Z]/.test(password)) return 'Mật khẩu phải có ít nhất 1 chữ hoa.';
  if (!/[a-z]/.test(password)) return 'Mật khẩu phải có ít nhất 1 chữ thường.';
  if (!/[0-9]/.test(password)) return 'Mật khẩu phải có ít nhất 1 chữ số.';
  if (!/[^A-Za-z0-9]/.test(password)) return 'Mật khẩu phải có ít nhất 1 ký tự đặc biệt.';
  return null;
}

/** Kiểm tra dạng email đơn giản (backend dùng EmailStr kiểm kỹ hơn). */
export function validateEmail(email) {
  if (!email.trim()) return 'Vui lòng nhập email.';
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) return 'Nhập email hợp lệ.';
  return null;
}

/** Họ tên: không trống, tối đa 100 ký tự (khớp String(100) trong model). */
export function validateFullName(fullName) {
  const value = fullName.trim();
  if (!value) return 'Họ tên không được để trống.';
  if (value.length > 100) return 'Họ tên tối đa 100 ký tự.';
  return null;
}
