// Khối "Kỹ năng của tôi" trên trang Hồ sơ (FĐ6, 08/11/2026) — thay PendingBlock, theo demo Profile.
// Hiện tối đa 6 kỹ năng (Đã biết trước, rồi Đang học) + link "Quản lý" → /me/skills.
//   skills : kết quả GET /api/me/skills (null = đang tải) · error: tải lỗi
import { Link } from 'react-router-dom';

import styles from '../styles/SkillsSummary.module.css';

const MAX = 6;

export default function SkillsSummary({ skills, error }) {
  const sorted = (skills ?? [])
    .slice()
    .sort((a, b) => (a.status === b.status ? 0 : a.status === 'known' ? -1 : 1));
  const more = sorted.length - MAX;

  return (
    <section className={`card ${styles.block}`}>
      <div className="between">
        <h2>Kỹ năng của tôi</h2>
        <Link to="/me/skills" className="small" style={{ fontWeight: 600 }}>
          Quản lý
        </Link>
      </div>

      {error && <p className="muted small">Không tải được kỹ năng.</p>}

      {!error && skills === null && (
        <div className="stack" style={{ gap: 10 }} aria-hidden="true">
          {[0, 1, 2].map((i) => (
            <div key={i} className="skeleton" style={{ height: 22 }} />
          ))}
        </div>
      )}

      {!error && skills?.length === 0 && (
        <p className={styles.empty}>
          Chưa có kỹ năng nào. <Link to="/me/skills">Thêm kỹ năng →</Link>
        </p>
      )}

      {sorted.length > 0 && (
        <ul className={styles.list}>
          {sorted.slice(0, MAX).map((s) => (
            <li key={s.skill_id}>
              <span>{s.skill}</span>
              <span className={`chip ${s.status === 'known' ? 'chip-accent' : 'chip-info'}`}>
                {s.status === 'known' ? 'Đã biết' : 'Đang học'}
              </span>
            </li>
          ))}
        </ul>
      )}
      {more > 0 && (
        <Link to="/me/skills" className="small muted">
          + {more} kỹ năng khác
        </Link>
      )}
    </section>
  );
}
