import { useNavigate } from 'react-router-dom';
import { getLearningPathSummary } from '../../../utils/learningPathUtils';
import styles from '../styles/PathPages2.module.css';

const STATUS = {
  ongoing: ['Đang theo', 'ongoing'],
  not_started: ['Chưa bắt đầu', 'notStarted'],
  completed: ['Hoàn thành', 'completed'],
  abandoned: ['Đã bỏ', 'abandoned'],
};

export default function PathCard2({ learningPath, onShowProfile, index = 0 }) {
  const navigate = useNavigate();
  const { record_id, original_query, goal_type, has_profile, nodes = [] } = learningPath;
  const { totalSkills, completedSkills, progressPercentage, displayStatus } = getLearningPathSummary(learningPath);
  const [statusLabel, statusClass] = STATUS[displayStatus];
  const targets = nodes.filter((n) => n.is_target).map((n) => n.skill?.skill).filter(Boolean);

  const open = () => navigate(`/me/my-learning-path/details/${record_id}`, { state: { learningPath } });

  return (
    <article className={styles.card} style={{ animationDelay: `${index * 40}ms` }}>
      <div className={styles.cardTop}>
        <span className={`${styles.goalBadge} ${goal_type === 'project' ? styles.goalProject : ''}`}>
          {goal_type === 'project' ? '🛠 Dự án' : '🎓 Nghề nghiệp'}
        </span>
        <span className={`${styles.status} ${styles[statusClass]}`}>{statusLabel}</span>
        {has_profile && (
          <button type="button" className={styles.profileIcon} onClick={() => onShowProfile(learningPath)}
            aria-label="Xem hồ sơ lộ trình" title="Xem hồ sơ lộ trình">
            <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
              <path fill="currentColor" d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.4 0-8 2.2-8 5v1h16v-1c0-2.8-3.6-5-8-5Z" />
            </svg>
          </button>
        )}
      </div>

      <h2 className={styles.cardTitle} title={original_query}>{original_query}</h2>

      {targets.length > 0 && (
        <div className={styles.cardTargets}>
          {targets.slice(0, 4).map((t) => <span key={t}>{t}</span>)}
          {targets.length > 4 && <span>+{targets.length - 4}</span>}
        </div>
      )}

      <div className={styles.progressRow}>
        <span>{completedSkills}/{totalSkills} kỹ năng</span>
        <strong>{progressPercentage}%</strong>
      </div>
      <div className={styles.track} role="progressbar" aria-valuenow={progressPercentage} aria-valuemin={0}
        aria-valuemax={100} aria-label="Tiến độ">
        <div className={styles.fill} style={{ width: `${progressPercentage}%` }} />
      </div>

      <button type="button" className={styles.cardCta} onClick={open}>
        Xem lộ trình <span aria-hidden="true">→</span>
      </button>
    </article>
  );
}
