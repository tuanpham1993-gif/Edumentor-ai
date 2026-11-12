// Danh sách mục điều hướng dùng chung cho Header và Footer (FĐ7, 08/11/2026).
// Đường dẫn theo bộ màn demo (docs/EduMentor-UI-design). Trang nào chưa làm → routes/index.jsx
// tạm trỏ tới "Tạm thời chưa khả dụng"; nhóm làm xong trang thì thay route, KHÔNG cần sửa file này.
//   owner: ai phụ trách trang đó (để nhóm biết route nào của mình)
//   match: (không bắt buộc) các đường dẫn KHÁC cũng thuộc mục này → mục được tô sáng, và được ưu tiên hơn
//          mục có `to` là tiền tố (vd /courses/312/review thuộc "Ôn tập", không phải "Khóa học").
export const MAIN_NAV = [
  { to: '/courses', text: 'Khóa học', owner: 'Khôi' },
  { to: '/me/learning-paths', text: 'Lộ trình', owner: 'Hòa' },
  { to: '/me/courses', text: 'Khóa học của tôi', owner: 'Tâm' },
  {
    to: '/me/review-history',
    text: 'Ôn tập',
    owner: 'Tuấn (09)',
    match: [/^\/review\//, /^\/courses\/[^/]+\/review/],
  },
  { to: '/tutor', text: 'AI Tutor', owner: 'Tâm' },
  { to: '/contact', text: 'Liên hệ', owner: 'Tâm' },
];

export const ADMIN_NAV = { to: '/admin', text: 'Quản trị' };

/** Mục đang mở: ưu tiên `match`; nếu không, mục có `to` trùng hoặc là tiền tố dài nhất của đường dẫn. */
export function activeNavItem(items, pathname) {
  const matched = items.find((item) => item.match?.some((re) => re.test(pathname)));
  if (matched) return matched;
  const prefix = items.filter((item) => pathname === item.to || pathname.startsWith(`${item.to}/`));
  return prefix.sort((a, b) => b.to.length - a.to.length)[0] ?? null;
}
