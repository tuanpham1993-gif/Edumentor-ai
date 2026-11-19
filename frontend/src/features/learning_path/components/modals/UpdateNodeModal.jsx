import { useState } from 'react';
import { updateLearningPathNode } from '../../../../api/learningPaths.api';

import styles from '../../styles/UpdateNodeModal.module.css';

const RELATION_TYPES = [
  'prerequisite',
  'related',
  'extension',
];

export default function UpdateNodeModal({
  recordId,
  selectedSkill,
  onClose,
  onSuccess,
}) {
  const [nodeRole, setNodeRole] = useState(
    selectedSkill.nodeRole || 'prerequisite'
  );

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit() {
    setLoading(true);
    setError('');

    try {
      await updateLearningPathNode(
        recordId,
        selectedSkill.skillId,
        { node_role: nodeRole }
      );

      await onSuccess?.();
      onClose();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Unable to update this skill.'
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className={styles.backdropUpdateNodeModal}
      onClick={() => !loading && onClose()}
    >
      <section
        className={styles.modalUpdateNodeModal}
        role="dialog"
        aria-modal="true"
        aria-labelledby="update-node-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className={styles.headerUpdateNodeModal}>
          <h2 id="update-node-title">Update skill role</h2>

          <button
            type="button"
            className={styles.closeUpdateNodeModal}
            onClick={onClose}
            disabled={loading}
            aria-label="Close"
          >
            ×
          </button>
        </header>

        <div className={styles.bodyUpdateNodeModal}>
          <p>
            Selected skill: <strong>{selectedSkill.skillName}</strong>
          </p>

          <label htmlFor="node-role">
            Skill role
          </label>

          <select
            id="node-role"
            value={nodeRole}
            onChange={(event) => setNodeRole(event.target.value)}
            disabled={loading}
          >
            {RELATION_TYPES.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>

          {error && (
            <p className={styles.errorUpdateNodeModal} role="alert">
              {error}
            </p>
          )}
        </div>

        <footer className={styles.footerUpdateNodeModal}>
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
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? 'Updating...' : 'Confirm'}
          </button>
        </footer>
      </section>
    </div>
  );
}