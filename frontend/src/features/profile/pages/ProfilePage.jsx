// Trang Hồ sơ (module 01 · Tuấn · FĐ5, 07/11/2026) — theo màn demo Profile.
//   - Thẻ đầu: ảnh / chữ viết tắt, họ tên, email, vai trò, ngày tham gia.
//   - Nút: Chỉnh sửa hồ sơ (/me/edit), Đổi mật khẩu (/me/password), Đăng xuất (hộp thoại xác nhận).
//   - Công tắc giao diện Tối / Sáng (FR-49).
//   - 4 ô thống kê: chờ GET /me/summary (backend 7.2) → tạm hiện "—".
//   - 3 khối dưới (08/11): Khóa học của tôi (module khóa học), Kỹ năng của tôi (GĐ4 → FĐ6),
//     Ôn tập gần đây (module 09). Chưa có API → <PendingBlock> "Đang cập nhật";
//     có API thì thay bằng component dữ liệu thật, giữ nguyên tiêu đề / link.
import { useCallback, useState } from 'react';
import { Link } from 'react-router-dom';

import LogoutDialog from '../components/LogoutDialog.jsx';
import PendingBlock from '../components/PendingBlock.jsx';
import ThemeToggle from '../components/ThemeToggle.jsx';
import { useAuth } from '../../../hooks/useAuth.js';
import { formatDate, initials, roleLabel } from '../../../utils/formatters.js';
import styles from '../styles/ProfilePage.module.css';

// Thứ tự & nhãn theo demo. value: null = chưa có dữ liệu (chờ /me/summary).
const STATS = [
  { key: 'courses_in_progress', label: 'Khóa học đang học' },
  { key: 'courses_completed', label: 'Khóa học đã hoàn thành' },
  { key: 'known_skills', label: 'Kỹ năng đã biết' },
  { key: 'active_paths', label: 'Lộ trình đang theo đuổi' },
];

export default function ProfilePage() {
  const { user } = useAuth();
  const [logoutOpen, setLogoutOpen] = useState(false);
  const closeLogout = useCallback(() => setLogoutOpen(false), []);

  return (
    <div className={`stack ${styles.enter}`} style={{ gap: 24 }}>
      <div className="page-head">
        <div>
          <h1>Hồ sơ người dùng</h1>
          <p>Quản lý thông tin tài khoản và theo dõi tiến độ học tập của bạn.</p>
        </div>
        <ThemeToggle />
      </div>

      <section className={`card ${styles.header}`}>
        <span className={styles.avatar} aria-hidden="true">
          {user.avatar_url ? <img src={user.avatar_url} alt="" /> : initials(user.full_name)}
        </span>
        <div className={styles.who}>
          <strong>{user.full_name}</strong>
          <span className="muted">{user.email}</span>
          <div className="row" style={{ gap: 8 }}>
            <span className="chip chip-accent">{roleLabel(user.role)}</span>
            <span className="chip">Tham gia {formatDate(user.created_at)}</span>
          </div>
        </div>
        <div className={styles.actions}>
          <Link to="/me/edit" className="btn btn-primary">
            Chỉnh sửa hồ sơ
          </Link>
          <Link to="/me/password" className="btn">
            Đổi mật khẩu
          </Link>
          <button type="button" className="btn btn-danger" onClick={() => setLogoutOpen(true)}>
            Đăng xuất
          </button>
        </div>
      </section>

      <section className={styles.stats} aria-label="Thống kê học tập">
        {STATS.map((stat) => (
          <div key={stat.key} className={`card ${styles.stat}`}>
            <b title="Đang cập nhật">—</b>
            <span>{stat.label}</span>
          </div>
        ))}
      </section>

      {/* Bố cục theo demo: trái rộng = khóa học, phải hẹp = kỹ năng + ôn tập */}
      <div className={styles.grid}>
        <PendingBlock title="Khóa học của tôi">
          Danh sách khóa học Đang học / Đã lưu / Đã hoàn thành sẽ hiện ở đây khi module khóa học
          hoàn tất.
        </PendingBlock>

        <div className="stack" style={{ gap: 20 }}>
          <PendingBlock title="Kỹ năng của tôi" link={{ to: '/me/skills', text: 'Quản lý' }}>
            Các kỹ năng Đã biết / Đang học của bạn sẽ hiện ở đây.
          </PendingBlock>
          <PendingBlock title="Ôn tập gần đây">
            Kết quả các bài ôn tập gần nhất sẽ hiện ở đây.
          </PendingBlock>
        </div>
      </div>

      <LogoutDialog open={logoutOpen} onClose={closeLogout} />
    </div>
  );
}
