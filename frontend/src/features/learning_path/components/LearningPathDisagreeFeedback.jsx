
import styles from '../styles/FeedbackModal.module.css';

export default function LearningPathFeedbackModal({ onClose }) {
  return (
    
    <div
    className={styles.backdropFeedbackModal}
    onClick={onClose}
    >
    <section
        className={styles.containerFeedbackModal}
        role="dialog"
        aria-modal="true"
        aria-labelledby="feedback-title"
        onClick={(event) => event.stopPropagation()}
    >
        <button
        type="button"
        className={styles.closeFeedbackModal}
        onClick={onClose}
        aria-label="Close feedback message"
        >
        ×
        </button>

        <div className={styles.iconFeedbackModal} aria-hidden="true">
        !
        </div>

        <div className={styles.contentFeedbackModal}>
        <h2 id="feedback-title">
            Let's improve it!
        </h2>

        <p>
            Please provide us with more details next time
            so we can generate a better learning path for you.
        </p>
        </div>

        <footer className={styles.footerFeedbackModal}>
        <button
            type="button"
            className={styles.confirmFeedbackModal}
            onClick={onClose}
        >
            OK
        </button>
        </footer>
    </section>
    </div>

  );
}
