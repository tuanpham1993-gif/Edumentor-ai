// Trang Hồ sơ (module 01 · Tuấn · FĐ5, 07/11/2026) — theo màn demo Profile.
//   - Thẻ đầu: ảnh / chữ viết tắt, họ tên, email, vai trò, ngày tham gia.
//   - Nút: Chỉnh sửa hồ sơ (/me/edit). (12/11: bỏ nút Đổi mật khẩu — vào từ menu avatar "Cài đặt tài khoản".) (12/11: bỏ nút Đăng xuất — đã có trong
//     menu avatar và cột trái Cài đặt.)
//   - (12/11) Bỏ công tắc Tối / Sáng ở đầu trang — đã có trang "Giao diện" trong menu avatar.
//   - 4 ô thống kê: "Kỹ năng đã biết" lấy từ GET /me/skills (FĐ6, 08/11); 3 ô còn lại chờ
//     GET /me/summary (backend 7.2) → tạm hiện "—".
//   - 3 khối dưới: Kỹ năng của tôi = dữ liệu thật (SkillsSummary, FĐ6); Ôn tập gần đây = dữ liệu thật
//     module 09 (RecentReviews, 11/11); Khóa học của tôi (module khóa học) chưa có API → <PendingBlock>.
//   - Icon trên 3 nút theo demo (11/11).
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import * as meApi from '../../../api/me.api.js';
import { PencilIcon } from '../../common/components/icons.jsx';
import PendingBlock from '../components/PendingBlock.jsx';
import RecentReviews from '../components/RecentReviews.jsx';
import SkillsSummary from '../components/SkillsSummary.jsx';
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
  const [skills, setSkills] = useState(null); // null = đang tải
  const [skillsError, setSkillsError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    meApi
      .getMySkills()
      .then((data) => !cancelled && setSkills(data))
      .catch(() => !cancelled && setSkillsError(true));
    return () => {
      cancelled = true;
    };
  }, []);

  // Giá trị từng ô thống kê; undefined → "—" (chưa có API)
  const statValue = {
    known_skills: skills ? skills.filter((s) => s.status === 'known').length : undefined,
  };

  return (
    <div className={`stack ${styles.enter}`} style={{ gap: 24 }}>
      <div className="page-head">
        <div>
          <h1>Hồ sơ người dùng</h1>
          <p>Quản lý thông tin tài khoản và theo dõi tiến độ học tập của bạn.</p>
        </div>
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
            <PencilIcon /> Chỉnh sửa hồ sơ
          </Link>
        </div>
      </section>

      <section className={styles.stats} aria-label="Thống kê học tập">
        {STATS.map((stat) => (
          <div key={stat.key} className={`card ${styles.stat}`}>
            {statValue[stat.key] === undefined ? (
              <b title="Đang cập nhật">—</b>
            ) : (
              <b>{statValue[stat.key]}</b>
            )}
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
          <SkillsSummary skills={skills} error={skillsError} />
          <RecentReviews />
        </div>
      </div>

    </div>
  );
}
