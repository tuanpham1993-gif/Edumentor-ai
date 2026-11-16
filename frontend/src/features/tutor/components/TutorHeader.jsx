import styles from '../styles/TutorHeader.module.css';

/**
 * Thanh tiêu đề phiên chat AI Tutor
 * @param {Object} props
 * @param {string} props.topic - Tên chủ đề của phiên
 * @param {string} [props.subtitle] - Ghi chú phụ
 * @param {() => void} [props.onToggleSidebar] - Mở sidebar trên mobile
 */
export default function TutorHeader({
  topic = 'Phiên học tập mới',
  subtitle = 'AI Tutor nhớ ngữ cảnh trong phiên này',
  onToggleSidebar,
}) {
  return (
    <header className={styles.header}>
      <div className={styles.titleArea}>
        {onToggleSidebar && (
          <button
            type="button"
            className={styles.menuToggleBtn}
            onClick={onToggleSidebar}
            title="Danh sách phiên chat"
            aria-label="Mở danh sách phiên chat"
          >
            ☰
          </button>
        )}
        <div className={styles.textGroup}>
          <h1 className={styles.topicTitle}>{topic}</h1>
          <p className={styles.subtitle}>{subtitle}</p>
        </div>
      </div>
    </header>
  );
}
