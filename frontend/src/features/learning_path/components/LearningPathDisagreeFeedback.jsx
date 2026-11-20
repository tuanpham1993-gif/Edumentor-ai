
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
        aria-label="Đóng thông báo"
        >
        ×
        </button>

        <div className={styles.iconFeedbackModal} aria-hidden="true">
        !
        </div>

        <div className={styles.contentFeedbackModal}>
        <h2 id="feedback-title">
            Cùng cải thiện nhé!
        </h2>

        <p>
            Lần sau hãy mô tả mục tiêu chi tiết hơn
            để chúng tôi tạo lộ trình phù hợp hơn cho bạn.
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
