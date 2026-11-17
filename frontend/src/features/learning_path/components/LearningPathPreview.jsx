
import LearningPathGraph from './LearningPath';
import styles from '../styles/LearningPathPreview.module.css';

export default function LearningPathPreview({
  learningPath, onConfirm, 
  onCancel, isConfirming = false}) {
  if (!learningPath) { return null; }
  const goalType = learningPath.goal_type ?? 'learning';

  return (
    <section className={styles.previewContainer}>

      <header className={styles.previewHeader}>
        <div>
          <span className={styles.eyebrowPreview}>
            GENERATED LEARNING PATH
          </span>

          <h2 className={styles.titlePreview}>
            Review your learning path
          </h2>
        </div>

        <span className={styles.skillCount}>
          {learningPath.nodes?.length ?? 0} skills
        </span>
      </header>

      <div className={styles.goalInformation}>
        <span className={styles.goalLabel}>
          Your original goal
        </span>

        <p className={styles.originalQuery}>
          {learningPath.original_query}
        </p>

        <span className={styles.goalType}>
          Goal type: {goalType}
        </span>
      </div>

      <div className={styles.reviewMessage}>
        <strong>Here is your learning path review.</strong>
        <span>You can adjust this later.</span>
      </div>

      <LearningPathGraph learningPath={learningPath} />

      <footer className={styles.previewFooter}>
        <button
          type="button"
          className={styles.cancelButtonPreview}
          onClick={onCancel}
          disabled={isConfirming}>
          Cancel
        </button>

        <button
          type="button"
          className={styles.confirmButtonPreview}
          onClick={onConfirm}
          disabled={isConfirming}
        >
          {isConfirming ? 'Confirming...' : 'Confirm path'}
        </button>
      </footer>

    </section>
  );
}
