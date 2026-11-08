// Danh sách mục điều hướng dùng chung cho Header và Footer (FĐ7, 08/11/2026).
// Đường dẫn theo bộ màn demo (docs/EduMentor-UI-design). Trang nào chưa làm → routes/index.jsx
// tạm trỏ tới "Tạm thời chưa khả dụng"; nhóm làm xong trang thì thay route, KHÔNG cần sửa file này.
//   owner: ai phụ trách trang đó (để nhóm biết route nào của mình)
export const MAIN_NAV = [
  { to: '/courses', text: 'Khóa học', owner: 'Khôi' },
  { to: '/me/learning-paths', text: 'Lộ trình', owner: 'Hòa' },
  { to: '/me/courses', text: 'Khóa học của tôi', owner: 'Tâm' },
  { to: '/me/review-history', text: 'Ôn tập', owner: 'Tuấn (09)' },
  { to: '/tutor', text: 'AI Tutor', owner: 'Tâm' },
  { to: '/contact', text: 'Liên hệ', owner: 'Tâm' },
];

export const ADMIN_NAV = { to: '/admin', text: 'Quản trị' };
