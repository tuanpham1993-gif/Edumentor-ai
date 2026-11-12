// Khối "Ôn tập gần đây" trên trang Hồ sơ (module 01 · Tuấn · 11/11/2026) — thay PendingBlock, theo demo Profile.
// Dữ liệu thật từ module 09: GET /api/me/review-history?size=3 (3 lượt đã nộp mới nhất).
// Mỗi dòng: tên khóa · ngày nộp · điểm /10 (demo ghi "85% · 17/20 câu" — đề đã chốt 15 câu, thang 10).
// Bấm một dòng → trang kết quả lượt đó; "Xem tất cả" → Lịch sử ôn tập.
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import * as reviewApi from '../../../api/review.api.js';
import { formatDate } from '../../../utils/formatters.js';
import styles from '../styles/SkillsSummary.module.css'; // cùng kiểu khối với "Kỹ năng của tôi"

const SIZE = 3;

export default function RecentReviews() {
  const [items, setItems] = useState(null); // null = đang tải
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    reviewApi
      .getHistory({ size: SIZE })
      .then((data) => !cancelled && setItems(data.items))
      .catch(() => !cancelled && setError(true));
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className={`card ${styles.block}`}>
      <div className="between">
        <h2>Ôn tập gần đây</h2>
        <Link to="/me/review-history" className="small" style={{ fontWeight: 600 }}>
          Xem tất cả
        </Link>
      </div>

      {error && <p className="muted small">Không tải được lịch sử ôn tập.</p>}

      {!error && items === null && (
        <div className="stack" style={{ gap: 10 }} aria-hidden="true">
          {[0, 1].map((i) => (
            <div key={i} className="skeleton" style={{ height: 34 }} />
          ))}
        </div>
      )}

      {!error && items?.length === 0 && (
        <p className={styles.empty}>Chưa có bài ôn tập nào.</p>
      )}

      {items?.length > 0 && (
        <ul className={styles.list}>
          {items.map((a) => (
            <li key={a.attempt_id}>
              <Link to={`/review/${a.attempt_id}/result`} style={{ color: 'inherit', minWidth: 0 }}>
                <span style={{ display: 'block', fontWeight: 600 }}>{a.course_title}</span>
                <span className="small muted">
                  {formatDate(a.submitted_at)} ·{' '}
                  {a.status === 'grading' ? 'Đang chấm' : a.passed ? 'Đạt' : 'Chưa đạt'}
                </span>
              </Link>
              <strong style={{ color: a.passed ? 'var(--accent)' : 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                {a.status === 'grading' ? '…' : `${a.score}/10`}
              </strong>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
