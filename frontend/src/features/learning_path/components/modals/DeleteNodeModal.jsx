import { useState } from 'react';
import { deleteLearningPathNode } from '../../../../api/learningPaths.api';
import styles from '../../styles/DeleteNodeModal.module.css';

export default function DeleteNodeModal({
  recordId,
  selectedSkill,
  onClose,
  onSuccess,
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleDelete() {
    setLoading(true);
    setError('');

    try {
      await deleteLearningPathNode(
        recordId,
        selectedSkill.skillId
      );

      await onSuccess?.();
      onClose();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Không xóa được kỹ năng này.'
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className={styles.backdropDeleteNodeModal}
      onClick={() => !loading && onClose()}
    >
      <section
        className={styles.modalDeleteNodeModal}
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-node-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className={styles.headerDeleteNodeModal}>
          <h2 id="delete-node-title">Xóa kỹ năng?</h2>

          <button
            type="button"
            className={styles.closeDeleteNodeModal}
            onClick={onClose}
            disabled={loading}
            aria-label="Đóng"
          >
            ×
          </button>
        </header>

        <div className={styles.bodyDeleteNodeModal}>
          <p>
            Bạn chắc chắn muốn xóa{' '}
            <strong>{selectedSkill.skillName}</strong> khỏi lộ trình?
          </p>

          <p>
            Các quan hệ của kỹ năng này trong lộ trình cũng bị xóa.
          </p>

          {error && (
            <p className={styles.errorDeleteNodeModal} role="alert">
              {error}
            </p>
          )}
        </div>

        <footer className={styles.footerDeleteNodeModal}>
          <button
            type="button"
            className="btn"
            onClick={onClose}
            disabled={loading}
          >
            Hủy
          </button>

          <button
            type="button"
            className="btn btn-danger"
            onClick={handleDelete}
            disabled={loading}
          >
            {loading ? 'Đang xóa...' : 'Xóa kỹ năng'}
          </button>
        </footer>
      </section>
    </div>
  );
}