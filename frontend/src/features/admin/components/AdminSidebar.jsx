// Sidebar điều hướng dành riêng cho phân hệ Quản trị (Admin)
import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import styles from '../styles/AdminLayout.module.css';

const ADMIN_NAV_LINKS = [
  { to: '/admin/courses', label: 'Khóa học' },
  { to: '/admin/skills', label: 'Kỹ năng và quan hệ' },
  { to: '/admin/base-paths', label: 'Mẫu lộ trình' },
  { to: '/admin/historical', label: 'Dữ liệu lịch sử' },
  { to: '/admin/feedback', label: 'Phản hồi' },
  { to: '/admin/user-paths', label: 'Lộ trình người dùng' },
  { to: '/admin/questions', label: 'Câu hỏi ôn tập' }, // Tuấn · module 09 (16/11, Tuấn duyệt thêm)
  { to: '/admin/review-flags', label: 'Kết Quả - AI Chấm' }, // Tuấn · module 09 (17/11, Tuấn duyệt thêm)
  { to: '/admin/skill-scopes', label: 'Phạm vi kỹ năng' }, // Tuấn · module 09 G3.0 (24/11)
  { to: '/admin/review-reports', label: 'Câu bị phản ánh' }, // Tuấn · module 09 G3f (25/11 — mentor phản ánh)
  { to: '/admin/review-mentors', label: 'Mentor ôn tập' }, // Tuấn · module 09 G3f (25/11)
];

export default function AdminSidebar() {
  return (
    <nav aria-label="Quản trị" className={styles.side}>
      {ADMIN_NAV_LINKS.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `${styles.navItem} ${isActive ? styles.navItemActive : ''}`
          }
        >
          {item.label}
        </NavLink>
      ))}

      <Link to="/courses" className={`${styles.navItem} ${styles.backItem}`}>
        ← Về trang học viên
      </Link>

      {/* Đèn vàng treo đặc trưng EduMentor */}
      <div className={styles.lampContainer} aria-hidden="true">
        <div className={styles.lampGlow} />
        <svg width="120" height="330" viewBox="0 0 120 330">
          <line x1="60" y1="0" x2="60" y2="220" stroke="#2b2622" strokeWidth="3" />
          <path d="M32 220h56l20 50H12z" fill="#1b1a19" stroke="#3a342d" />
          <ellipse cx="60" cy="270" rx="48" ry="7" fill="#ffb347" />
          <circle cx="60" cy="277" r="11" fill="#ffd27a" />
          <line x1="82" y1="270" x2="82" y2="322" stroke="#6b5a40" />
          <circle cx="82" cy="326" r="4" fill="var(--accent, #f5a524)" />
        </svg>
      </div>
    </nav>
  );
}
