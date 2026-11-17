import { getLearningPathSummary } from "../../../utils/learningPathUtils";
import { useNavigate } from "react-router-dom";
import styles from '../styles/LearningPathCard.module.css';

const STATUS_CONFIG = {
  ongoing: {
    label: 'In Progress',
    className: 'ongoing',
  },
  not_started: {
    label: 'Not Started',
    className: 'notStarted',
  },
  completed: {
    label: 'Completed',
    className: 'completed',
  },
  abandoned: {
    label: 'Abandoned',
    className: 'abandoned',
  },
};

export default function LearningPathCard({ learningPath }) {
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
    <article className={styles.cardLearningPath}>
      <div className={styles.cardHeaderLearningPath}>
        <h2 className={styles.titleLearningPath}>{original_query}</h2>
        <span className={`${styles.statusLearningPath} ${styles[statusInfo.className]}`}>
          {statusInfo.label}
        </span>
      </div>

      <p className={styles.goalInfoLearningPath}>
        Goal type: {goal_type === 'career' ? 'Career' : 'Project'}
        {' · '}
        {totalSkills} skills
      </p>

      <div className={styles.progressInfoLearningPath}>
        <span>Progress</span>
        <span>{completedSkills}/{totalSkills} skills</span>
      </div>

      <div className={styles.progressTrackLearningPath}
        role="progressbar"
        aria-label={`${original_query} progress`}
        aria-valuenow={progressPercentage}
        aria-valuemin={0} aria-valuemax={100}>
        <div className={styles.progressFillLearningPath}
          style={{ width: `${progressPercentage}%` }}/>
      </div>

      <div className={styles.cardFooterLearningPath}>
        <span>{progressPercentage}% completed</span>
      </div>

      <button type="button" className={styles.viewButtonLearningPath} 
      onClick={handleViewPath}> View Learning Path </button>
    </article>
  );
}