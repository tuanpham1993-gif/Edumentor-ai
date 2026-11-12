// Khối trên trang Hồ sơ khi CHƯA có API (module 01 · Tuấn · FĐ7, 08/11/2026).
// Cùng kiểu trang "Tạm thời chưa khả dụng": icon, "Đang cập nhật", một câu giải thích.
// Khi có API: thay <PendingBlock> bằng component dữ liệu thật, giữ nguyên tiêu đề / link.
//
//   title    : tiêu đề khối, vd "Kỹ năng của tôi"
//   link     : { to, text } — link góc phải (vd "Quản lý" → /me/skills); bỏ trống nếu chưa có trang
//   children : câu giải thích ngắn
import { Link } from 'react-router-dom';

import styles from '../styles/PendingBlock.module.css';

export default function PendingBlock({ title, link, children }) {
  return (
    <section className={`card ${styles.block}`}>
      <div className="between">
        <h2>{title}</h2>
        {link && (
          <Link to={link.to} className="small" style={{ fontWeight: 600 }}>
            {link.text}
          </Link>
        )}
      </div>

      <div className={styles.empty} role="status">
        <span className={styles.icon} aria-hidden="true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14.7 6.3a4 4 0 0 0-5.4 5.1L3.6 17.1a1.5 1.5 0 0 0 2.1 2.1l5.7-5.7a4 4 0 0 0 5.1-5.4l-2.4 2.4-2.1-.4-.4-2.1z" />
          </svg>
        </span>
        <strong>Đang cập nhật</strong>
        <p>{children}</p>
      </div>
    </section>
  );
}
