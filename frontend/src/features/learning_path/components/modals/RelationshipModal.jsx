import { useMemo, useState } from 'react';

import { addLearningPathEdge, updateLearningPathEdge, deleteLearningPathEdge } from '../../../../api/learningPaths.api';

import styles from '../../styles/RelationshipModal.module.css';

const RELATION_TYPES = [
  'prerequisite',
  'related',
  'extension',
];

export default function RelationshipModal({
  mode,
  recordId,
  selectedSkill,
  nodes,
  edges,
  onClose,
  onSuccess,
}) {
  const isRemoveMode = mode === 'remove-relationship';

  const [otherSkillId, setOtherSkillId] = useState('');
  const [direction, setDirection] = useState('selected-first');
  const [relationType, setRelationType] = useState('prerequisite');
  const [selectedEdgeIndex, setSelectedEdgeIndex] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const otherNodes = nodes.filter(
    (node) => node.skill_id !== selectedSkill.skillId
  );

  const relatedEdges = useMemo(
    () =>
      edges.filter(
        (edge) =>
          edge.from_skill_id === selectedSkill.skillId ||
          edge.to_skill_id === selectedSkill.skillId
      ),
    [edges, selectedSkill.skillId]
  );

  const selectedEdge =
    selectedEdgeIndex === ''
      ? null
      : relatedEdges[Number(selectedEdgeIndex)];

  async function handleSubmit() {
    setLoading(true);
    setError('');

    try {
      if (isRemoveMode) {
        if (!selectedEdge) {
          setError('Please select a relationship.');
          return;
        }

        await deleteLearningPathEdge(recordId, {
          from_skill_id: selectedEdge.from_skill_id,
          to_skill_id: selectedEdge.to_skill_id,
        });

      } else {
        if (!otherSkillId) {
          setError('Please select another skill.');
          return;
        }

        const otherId = Number(otherSkillId);

        const fromSkillId =
          direction === 'selected-first'
            ? selectedSkill.skillId
            : otherId;

        const toSkillId =
          direction === 'selected-first'
            ? otherId
            : selectedSkill.skillId;

        const payload = {
          from_skill_id: fromSkillId,
          to_skill_id: toSkillId,
          relation_type: relationType,
        };

        const existingEdge = edges.find(
          (edge) =>
            edge.from_skill_id === fromSkillId &&
            edge.to_skill_id === toSkillId
        );

        if (existingEdge) {
          await updateLearningPathEdge(recordId, payload);
        } else {
          await addLearningPathEdge(recordId, payload);
        }
      }

      await onSuccess?.();
      onClose();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Unable to update this relationship.'
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className={styles.backdropRelationshipModal}
      onClick={() => !loading && onClose()}
    >
      <section
        className={styles.modalRelationshipModal}
        role="dialog"
        aria-modal="true"
        aria-labelledby="relationship-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className={styles.headerRelationshipModal}>
          <h2 id="relationship-title">
            {isRemoveMode
              ? 'Remove relationship'
              : 'Add or update relationship'}
          </h2>

          <button
            type="button"
            className={styles.closeRelationshipModal}
            onClick={onClose}
            disabled={loading}
            aria-label="Close"
          >
            ×
          </button>
        </header>

        <div className={styles.bodyRelationshipModal}>
          {isRemoveMode ? (
            <>
              <p>
                Choose a relationship connected to{' '}
                <strong>{selectedSkill.skillName}</strong>.
              </p>

              {relatedEdges.length === 0 ? (
                <p>This skill has no relationships to remove.</p>
              ) : (
                <div className={styles.edgeListRelationshipModal}>
                  {relatedEdges.map((edge, index) => (
                    <label key={`${edge.from_skill_id}-${edge.to_skill_id}`}>
                      <input
                        type="radio"
                        name="selected-edge"
                        value={index}
                        checked={selectedEdgeIndex === String(index)}
                        onChange={(event) =>
                          setSelectedEdgeIndex(event.target.value)
                        }
                      />

                      <span>
                        {edge.from_skill.skill} → {edge.to_skill.skill} 
                        <small> ({edge.relation_type})</small>
                      </span>
                    </label>
                  ))}
                </div>
              )}
            </>
          ) : (
            <>
              <p>
                Current Selected skill:{' '}
                <strong>{selectedSkill.skillName}</strong>
              </p>

              <label htmlFor="other-skill">
                You want connect to
              </label>

              <select
                id="other-skill"
                value={otherSkillId}
                onChange={(event) =>
                  setOtherSkillId(event.target.value)
                }
              >
                <option value="">Choose another skill</option>

                {otherNodes.map((node) => (
                  <option
                    key={node.skill_id}
                    value={node.skill_id}
                  >
                    {node.skill?.skill ?? node.skill_name}
                  </option>
                ))}
              </select>

              <label htmlFor="edge-direction">
                Relationship direction
              </label>

              <select
                id="edge-direction"
                value={direction}
                onChange={(event) =>
                  setDirection(event.target.value)
                }
              >
                <option value="selected-first">
                  This selected skill → Other skill
                </option>

                <option value="other-first">
                  Other skill → This selected skill
                </option>
              </select>

              <label htmlFor="edge-relation-type">
                Relationship type
              </label>

              <select
                id="edge-relation-type"
                value={relationType}
                onChange={(event) =>
                  setRelationType(event.target.value)
                }
              >
                {RELATION_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </>
          )}

          {error && (
            <p
              className={styles.errorRelationshipModal}
              role="alert"
            >
              {error}
            </p>
          )}
        </div>

        <footer className={styles.footerRelationshipModal}>
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
            className={
              isRemoveMode
                ? 'btn btn-danger'
                : 'btn btn-primary'
            }
            onClick={handleSubmit}
            disabled={
              loading ||
              (isRemoveMode && relatedEdges.length === 0)
            }
          >
            {loading
              ? 'Processing...'
              : isRemoveMode
                ? 'Remove relationship'
                : 'Confirm'}
          </button>
        </footer>
      </section>
    </div>
  );
}