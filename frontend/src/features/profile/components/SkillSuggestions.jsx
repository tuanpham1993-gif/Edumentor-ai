// Dải "Gợi ý cho bạn" ở đầu trang Khám phá kỹ năng (FĐ6, 08/11/2026 — Tuấn chọn phương án 3).
// Dữ liệu: GET /api/me/skills/suggestions — kỹ năng CHƯA có trong hồ sơ, theo thứ tự:
//   Học tiếp  (sau kỹ năng bạn đã có, vd có Python → Pandas)
//   Liên quan (cùng nhóm với kỹ năng bạn đã có)
//   Phổ biến  (dạy trong nhiều khóa học nhất — cho người mới chưa có kỹ năng nào)
// Chọn ở đây dùng CHUNG danh sách "Đã chọn N kỹ năng" với lưới danh mục (picked / onToggle của trang cha).
//   refreshKey: đổi giá trị (sau khi "Thêm vào hồ sơ") → tải lại gợi ý theo hồ sơ mới.
import { useEffect, useState } from 'react';

import * as meApi from '../../../api/me.api.js';
import styles from '../styles/SkillSuggestions.module.css';

const STATUS_TEXT = { known: 'Đã biết', learning: 'Đang học' };

function reasonText(s) {
  if (s.reason === 'next') return `Học tiếp sau ${s.via}`;
  if (s.reason === 'related') return `Liên quan ${s.via}`;
  return s.course_count ? `Phổ biến · ${s.course_count} khóa học` : 'Phổ biến';
}

export default function SkillSuggestions({ picked, onToggle, refreshKey }) {
  const [items, setItems] = useState(null); // null = đang tải

  useEffect(() => {
    let cancelled = false;
    setItems(null);
    meApi
      .getSkillSuggestions(6) // 6 thẻ = 2 hàng chẵn ở 3 cột
      .then((data) => !cancelled && setItems(data))
      .catch(() => !cancelled && setItems([]));
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  if (items !== null && items.length === 0) return null; // không có gợi ý → ẩn cả dải

  const personal = items?.some((s) => s.reason !== 'popular');

  return (
    <section className={styles.strip} aria-labelledby="suggest-title">
      <div className={styles.head}>
        <h3 id="suggest-title">
          <span aria-hidden="true">✨</span> Gợi ý cho bạn
        </h3>
        <span className="small muted">
          {personal ? 'Dựa trên kỹ năng bạn đã có' : 'Kỹ năng được dạy nhiều nhất'}
        </span>
      </div>

      <ul className={styles.list} aria-busy={items === null}>
        {items === null &&
          Array.from({ length: 3 }, (_, i) => (
            <li key={i} className="skeleton" style={{ height: 92 }} aria-hidden="true" />
          ))}
        {items?.map((s) => {
          const choice = picked[s.skill_id]?.status;
          return (
            <li key={s.skill_id} className={`${styles.card} ${choice ? styles.cardPicked : ''}`}>
              <div className={styles.cardHead}>
                <strong>{s.skill}</strong>
                <span className={`${styles.reason} ${styles[s.reason] ?? ''}`}>{reasonText(s)}</span>
              </div>
              <div className={styles.choices} role="group" aria-label={`Thêm ${s.skill}`}>
                {['known', 'learning'].map((status) => (
                  <button
                    key={status}
                    type="button"
                    className={`${styles.choice} ${choice === status ? styles.choiceOn : ''}`}
                    aria-pressed={choice === status}
                    onClick={() => onToggle(s, status)}
                  >
                    {choice === status ? '✓ ' : '+ '}
                    {STATUS_TEXT[status]}
                  </button>
                ))}
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
