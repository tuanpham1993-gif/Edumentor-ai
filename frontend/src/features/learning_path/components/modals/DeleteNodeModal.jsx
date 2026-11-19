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
        'Unable to delete this skill.'
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
          <h2 id="delete-node-title">Delete skill?</h2>

          <button
            type="button"
            className={styles.closeDeleteNodeModal}
            onClick={onClose}
            disabled={loading}
            aria-label="Close"
          >
            ×
          </button>
        </header>

        <div className={styles.bodyDeleteNodeModal}>
          <p>
            Are you sure you want to remove{' '}
            <strong>{selectedSkill.skillName}</strong>?
          </p>

          <p>
            Its relationships in this learning path will also be removed.
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
            Cancel
          </button>

          <button
            type="button"
            className="btn btn-danger"
            onClick={handleDelete}
            disabled={loading}
          >
            {loading ? 'Deleting...' : 'Delete skill'}
          </button>
        </footer>
      </section>
    </div>
  );
}