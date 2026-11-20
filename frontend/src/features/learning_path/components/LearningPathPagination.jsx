
import styles from '../styles/LearningPathPagination.module.css';

export default function LearningPathPagination({
  currentPage, totalPages, onPageChange}) {
  if (totalPages <= 1) { return null; }
  function handlePrevious() {
    if (currentPage > 1) {
        onPageChange(currentPage - 1);
    }
  }

  function handleNext() {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  }

  return (
    <nav className={styles.paginationLearningPaths}
        aria-label="Trang lộ trình">
      <button type="button"
        className={styles.pageButtonLearningPaths}
        onClick={handlePrevious}
        disabled={currentPage === 1}>
        Trước
      </button>

      <span className={styles.pageInfoLearningPaths}>
        Page {currentPage} of {totalPages}
      </span>

      <button
        type="button"
        className={styles.pageButtonLearningPaths}
        onClick={handleNext}
        disabled={currentPage === totalPages}>
        Sau
      </button>
    </nav>
  );
}
