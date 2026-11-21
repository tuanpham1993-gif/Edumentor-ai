import { getLearningPathSummary } from "../../../utils/learningPathUtils";
import { useNavigate } from "react-router-dom";
import styles from '../styles/LearningPathCard.module.css';

const STATUS_CONFIG = {
  ongoing: {
    label: 'Đang theo',
    className: 'ongoing',
  },
  not_started: {
    label: 'Chưa bắt đầu',
    className: 'notStarted',
  },
  completed: {
    label: 'Hoàn thành',
    className: 'completed',
  },
  abandoned: {
    label: 'Đã bỏ',
    className: 'abandoned',
  },
};

export default function LearningPathCard({ learningPath, index = 0 }) {
  const navigate = useNavigate();
  //console.log(learningPath)
  const {record_id, original_query, goal_type} = learningPath;
  const {totalSkills, completedSkills,
    progressPercentage, displayStatus} = getLearningPathSummary(learningPath);
  const statusInfo = STATUS_CONFIG[displayStatus];
  function handleViewPath(){
    navigate(`/me/my-learning-path/details/${record_id}`, {
      state: { learningPath }
    });
  }

  return (
    <article className={styles.cardLearningPath} style={{ "--i": index }}>
      <div className={styles.cardHeaderLearningPath}>
        <span className={`${styles.statusLearningPath} ${styles[statusInfo.className]}`}>
          {statusInfo.label}
        </span>
        <h2 className={styles.titleLearningPath} title={original_query}>{original_query}</h2>
      </div>

      <p className={styles.goalInfoLearningPath}>
        Mục tiêu: {goal_type === 'career' ? 'Nghề nghiệp' : 'Dự án'}
        {' · '}
        {totalSkills} kỹ năng
      </p>

      <div className={styles.progressInfoLearningPath}>
        <span>Tiến độ</span>
        <span>{completedSkills}/{totalSkills} kỹ năng</span>
      </div>

      <div className={styles.progressTrackLearningPath}
        role="progressbar"
        aria-label={`Tiến độ: ${original_query}`}
        aria-valuenow={progressPercentage}
        aria-valuemin={0} aria-valuemax={100}>
        <div className={styles.progressFillLearningPath}
          style={{ width: `${progressPercentage}%` }}/>
      </div>

      <div className={styles.cardFooterLearningPath}>
        <span>Hoàn thành {progressPercentage}%</span>
      </div>

      <button type="button" className={`btn btn-primary ${styles.viewButtonLearningPath}`} 
      onClick={handleViewPath}> Xem lộ trình </button>
    </article>
  );
}