// Trang "nhà" sau khi đăng nhập (module 01 · Tuấn · 19/11/2026 — G2 kế hoạch luồng trang chủ).
// SRS 6.1: học viên vào trang Hồ sơ; Admin vào trang Quản trị (/admin → /admin/courses).
// Dùng ở LoginPage (đăng nhập xong) và PublicRoute (đã đăng nhập mà mở /, /login…).

export function homePathFor(user) {
  return user?.role === 'admin' ? '/admin' : '/me';
}
