import styles from '../styles/LearningPathToolbar.module.css';
import AddNodeModal from './modals/AddNodeModal';
import UpdateNodeModal from './modals/UpdateNodeModal';
import DeleteNodeModal from './modals/DeleteNodeModal';
import RelationshipModal from './modals/RelationshipModal';
import ShareLearningPathModal from './modals/ShareLearningPathModal';
import { useState } from 'react';

export default function LearningPathToolbar({
  recordId,
  learningPath,
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
        <h2>Công cụ lộ trình</h2>

        {selectedSkill ? (
          <span className={styles.selectedChip}>
            Đang chọn: <strong>{selectedSkill.skillName}</strong>
          </span>
        ) : (
          <span className={styles.placeholderHint}>Chọn một kỹ năng để chỉnh sửa</span>
        )}
      </div>
      
      <div className={styles.toolbarActionsLearningPath}>
        <button type="button"
          className='btn btn-soft'
          onClick={() => openModal('add-node')}>
          + Thêm kỹ năng
        </button>

        <button type="button"
            className="btn btn-primary"
            disabled={!hasSelectedSkill}
            onClick={() => openModal('update-node')}>
            Đổi vai trò
        </button>
        
        <button type="button"
          className="btn btn-danger"
          onClick={() => openModal('delete-node')}
          disabled={!hasSelectedSkill}>
          Xóa kỹ năng
        </button>

        <button
            type="button"
            className="btn btn-primary"
            disabled={!hasSelectedSkill}
            onClick={() => openModal('add-relationship')}>
          Thêm quan hệ
        </button>

        <button
          type="button"
          className="btn btn-danger"
          disabled={!hasSelectedSkill}
          onClick={() => openModal('remove-relationship')}>
          Gỡ quan hệ
        </button>

        <button
          type="button"
          className={`btn btn-soft ${styles.shareBtn}`}
          onClick={() => openModal('share-path')}
          title="Chia sẻ lộ trình này cho người khác">
          <svg
            aria-hidden="true"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="18" cy="5" r="3" />
            <circle cx="6" cy="12" r="3" />
            <circle cx="18" cy="19" r="3" />
            <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
            <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
          </svg>
          Chia sẻ
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

      {activeModal === 'share-path' && (
        <ShareLearningPathModal
          recordId={recordId}
          learningPath={learningPath}
          onClose={closeModal}
          onSuccess={onRefresh}
        />
      )}
    </div>
  );
}