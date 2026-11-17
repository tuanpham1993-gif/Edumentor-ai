import styles from '../styles/LearningPathToolbar.module.css';

export default function LearningPathToolbar({
  recordId, selectedSkill,}) {
  function handleAddNode() {
    console.log('Add new node to path:', recordId);
  }

  function handleDeleteNode() {
    if (!selectedSkill) return;
    console.log('Delete skill:', selectedSkill.skillId);
  }

  function handleAddRelationship() {
    if (!selectedSkill) return;
    console.log(
      'Add relationship for skill:',
      selectedSkill.skillId
    );
  }

  function handleFixRelationship() {
    if (!selectedSkill) return;
    console.log(
      'Fix relationship for skill:',
      selectedSkill.skillId
    );
  }

  function handleRemoveRelationship() {
    if (!selectedSkill) return;
    console.log(
      'Remove relationship for skill:',
      selectedSkill.skillId
    );
  }

  return (
    <div className={styles.toolbarLearningPath}>
      <button type="button"
        className={`${styles.toolbarButton} ${styles.addButton}`}
        onClick={handleAddNode}>
        + Add node
      </button>

      <button type="button"
        className={styles.toolbarButton}
        onClick={handleDeleteNode}
        disabled={!selectedSkill}>
        Delete node
      </button>

      <button
        type="button"
        className={styles.toolbarButton}
        onClick={handleAddRelationship}
        disabled={!selectedSkill}>
        + Relationship
      </button>

      <button
        type="button"
        className={styles.toolbarButton}
        onClick={handleFixRelationship}
        disabled={!selectedSkill}>
        Fix relationship
      </button>

      <button
        type="button"
        className={`${styles.toolbarButton} ${styles.removeButton}`}
        onClick={handleRemoveRelationship}
        disabled={!selectedSkill}>
        Remove relationship
      </button>
    </div>
  );
}