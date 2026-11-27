import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { getLearningPathProfile } from '../../../api/learningPaths.api.js';
import ProfileView, { fromSaved } from './ProfileView.jsx';
import styles from '../styles/PathPages2.module.css';

// Learner profile snapshot the path was generated from (GET /learning-paths/{id}/profile).
export default function ProfileModal({ recordId, title, onClose }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let alive = true;
    getLearningPathProfile(recordId)
      .then((d) => alive && setData(d))
      .catch((err) => alive && setError(err.response?.status === 404
        ? 'Lộ trình này được tạo trước khi có hồ sơ lộ trình nên chưa có dữ liệu hồ sơ.'
        : 'Không tải được hồ sơ lộ trình.'));
    return () => { alive = false; };
  }, [recordId]);

  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  return createPortal(
    <div className={styles.backdrop} onClick={onClose}>
      <section className={styles.profileModal} role="dialog" aria-modal="true" aria-labelledby="lp2-profile-title"
        onClick={(e) => e.stopPropagation()}>
        <header className={styles.profileHeader}>
          <div>
            <span className={styles.eyebrow}>Hồ sơ lộ trình</span>
            <h2 id="lp2-profile-title">{title}</h2>
            {data?.created_at && (
              <p className={styles.muted}>Ghi nhận lúc tạo lộ trình · {new Date(data.created_at).toLocaleString('vi-VN')}</p>
            )}
          </div>
          <button type="button" className={styles.roundButton} onClick={onClose} aria-label="Đóng">×</button>
        </header>
        <div className={styles.profileBody}>
          {!data && !error && <p className={styles.muted}>Đang tải…</p>}
          {error && <p className={styles.muted}>{error}</p>}
          {data && (
            <>
              {data.targets.length > 0 && (
                <div className={styles.targetStrip}>
                  <span>Kỹ năng đích:</span>
                  {data.targets.map((t) => (
                    <span key={t.skill_id} className={styles.targetChip}>
                      {t.skill_name}
                      <small>{t.source === 'role' ? 'vị trí' : 'công nghệ'}</small>
                    </span>
                  ))}
                </div>
              )}
              <ProfileView view={fromSaved(data.profile)} />
            </>
          )}
        </div>
      </section>
    </div>,
    document.body,
  );
}
