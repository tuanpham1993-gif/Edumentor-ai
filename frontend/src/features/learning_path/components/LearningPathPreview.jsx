
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
            LỘ TRÌNH ĐÃ TẠO
          </span>

          <h2 className={styles.titlePreview}>
            Xem lại lộ trình của bạn
          </h2>
        </div>

        <span className={styles.skillCount}>
          {learningPath.nodes?.length ?? 0} skills
        </span>
      </header>

      <div className={styles.goalInformation}>
        <span className={styles.goalLabel}>
          Mục tiêu ban đầu
        </span>

        <p className={styles.originalQuery}>
          {learningPath.original_query}
        </p>

        <span className={styles.goalType}>
          Goal type: {goalType}
        </span>
      </div>

      <div className={styles.reviewMessage}>
        <strong>Đây là lộ trình gợi ý cho bạn.</strong>
        <span>Bạn có thể chỉnh sửa sau.</span>
      </div>

      <LearningPathGraph learningPath={learningPath} />

      <footer className={styles.previewFooter}>
        <button
          type="button"
          className={styles.cancelButtonPreview}
          onClick={onCancel}
          disabled={isConfirming}>
          Hủy
        </button>

        <button
          type="button"
          className={styles.confirmButtonPreview}
          onClick={onConfirm}
          disabled={isConfirming}
        >
          {isConfirming ? 'Đang lưu...' : 'Lưu lộ trình'}
        </button>
      </footer>

    </section>
  );
}
