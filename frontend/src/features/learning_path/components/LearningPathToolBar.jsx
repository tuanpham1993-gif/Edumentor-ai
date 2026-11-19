import styles from '../styles/LearningPathToolbar.module.css';
import AddNodeModal from './modals/AddNodeModal';
import UpdateNodeModal from './modals/UpdateNodeModal';
import DeleteNodeModal from './modals/DeleteNodeModal';
import RelationshipModal from './modals/RelationshipModal';
import { useState } from 'react';

export default function LearningPathToolbar({
  recordId,
  selectedSkill,
  nodes,
  edges,
  onRefresh,
}) {

  const [activeModal, setActiveModal] = useState(null);

  const hasSelectedSkill = Boolean(selectedSkill);

  function openModal(modalName) {
    setActiveModal(modalName);
  }

  function closeModal() {
    setActiveModal(null);
  }

  return (
    <div className={styles.toolbarLearningPath}>
      <div className={styles.toolbarTitleLearningPath}>
        <h2>Learning Path Tools</h2>

        <span>
          {selectedSkill
            ? `Selected: ${selectedSkill.skillName}`
            : 'Select a skill to manage it'}
        </span>
      </div>
      
      <div className={styles.toolbarActionsLearningPath}>
        <button type="button"
          className='btn btn-soft'
          onClick={() => openModal('add-node')}>
          + Add node
        </button>

        <button type="button"
            className="btn btn-primary"
            disabled={!hasSelectedSkill}
            onClick={() => openModal('update-node')}>
            Update node
        </button>
        
        <button type="button"
          className="btn btn-danger"
          onClick={() => openModal('delete-node')}
          disabled={!hasSelectedSkill}>
          Delete node
        </button>

        <button
            type="button"
            className="btn btn-primary"
            disabled={!hasSelectedSkill}
            onClick={() => openModal('add-relationship')}>
          Add relationship
        </button>

        <button
          type="button"
          className="btn btn-danger"
          disabled={!hasSelectedSkill}
          onClick={() => openModal('remove-relationship')}>
          Remove relationship
        </button>
      </div>
      {activeModal === 'add-node' && (
        <AddNodeModal
          recordId={recordId}
          nodes={nodes}
          onClose={closeModal}
          onSuccess={onRefresh}
        />
      )}

      {activeModal === 'update-node' && (
        <UpdateNodeModal
          recordId={recordId}
          selectedSkill={selectedSkill}
          onClose={closeModal}
          onSuccess={onRefresh}
        />
      )}

      {activeModal === 'delete-node' && (
        <DeleteNodeModal
          recordId={recordId}
          selectedSkill={selectedSkill}
          onClose={closeModal}
          onSuccess={onRefresh}
        />
      )}

      {(activeModal === 'add-relationship' ||
        activeModal === 'remove-relationship') && (
        <RelationshipModal
          mode={activeModal}
          recordId={recordId}
          selectedSkill={selectedSkill}
          nodes={nodes}
          edges={edges}
          onClose={closeModal}
          onSuccess={onRefresh}
        />
      )}
    </div>
  );
}