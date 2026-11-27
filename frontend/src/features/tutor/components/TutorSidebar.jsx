import { useState } from 'react';
import LampIllustration from './LampIllustration.jsx';
import TutorBotIcon from './TutorBotIcon.jsx';
import styles from '../styles/TutorSidebar.module.css';

/**
 * Cột bên trái hiển thị danh sách phiên trò chuyện gần đây
 * @param {Object} props
 * @param {Array<{session_id: string, topic: string, created_at?: string}>} props.sessions
 * @param {string|null} props.activeSessionId
 * @param {(sessionId: string) => void} props.onSelectSession
 * @param {() => void} props.onCreateNewSession
 * @param {(sessionId: string, e: MouseEvent) => void} props.onDeleteSession
 * @param {(sessionId: string, newTopic: string) => void} [props.onRenameSession]
 * @param {boolean} [props.isOpenMobile=false]
 * @param {() => void} [props.onCloseMobile]
 */
export default function TutorSidebar({
  sessions = [],
  activeSessionId,
  onSelectSession,
  onCreateNewSession,
  onDeleteSession,
  onRenameSession,
  isOpenMobile = false,
  onCloseMobile,
}) {
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');

  const handleStartRename = (s, e) => {
    e.stopPropagation();
    setEditingSessionId(s.session_id);
    setEditingTitle(s.topic || 'Phiên học tập');
  };

  const handleSaveRename = (sessionId, e) => {
    e?.stopPropagation();
    const clean = editingTitle.trim();
    if (clean && onRenameSession) {
      onRenameSession(sessionId, clean);
    }
    setEditingSessionId(null);
  };

  const handleCancelRename = (e) => {
    e?.stopPropagation();
    setEditingSessionId(null);
  };
  const formatTime = (dateStr) => {
    if (!dateStr) return 'Gần đây';
    try {
      const d = new Date(dateStr);
      const now = new Date();
      const diffMs = now - d;
      const diffMins = Math.floor(diffMs / (1000 * 60));
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

      if (diffMins < 5) return 'Vừa xong';
      if (diffHours < 24 && d.getDate() === now.getDate()) return 'Hôm nay';
      if (diffDays === 1) return 'Hôm qua';
      return `${d.getDate().toString().padStart(2, '0')}/${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getFullYear()}`;
    } catch {
      return 'Gần đây';
    }
  };

  return (
    <>
      {/* Lớp phủ mờ backdrop trên màn hình di động */}
      {isOpenMobile && (
        <div className={styles.mobileBackdrop} onClick={onCloseMobile} aria-hidden="true" />
      )}

      <aside className={`${styles.sidebar} ${isOpenMobile ? styles.sidebarOpenMobile : ''}`}>
        {/* Nút tạo phiên trò chuyện mới */}
        <div className={styles.topAction}>
          <button
            type="button"
            className={styles.newChatBtn}
            onClick={onCreateNewSession}
          >
            <span className={styles.plusIcon}>+</span>
            <span>Phiên trò chuyện mới</span>
          </button>
        </div>

        {/* Tiêu đề mục các phiên gần đây */}
        <div className={styles.sectionHeader}>
          <span className={styles.sectionTitle}>Các phiên gần đây</span>
        </div>

        {/* Danh sách phiên */}
        <div className={styles.sessionList}>
          {sessions.length === 0 ? (
            <div className={styles.emptyNotice}>Chưa có phiên chat nào</div>
          ) : (
            sessions.map((s) => {
              const isActive = s.session_id === activeSessionId;
              const isEditing = s.session_id === editingSessionId;
              return (
                <div
                  key={s.session_id}
                  className={`${styles.sessionItem} ${isActive ? styles.activeItem : ''}`}
                  onClick={() => !isEditing && onSelectSession(s.session_id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (!isEditing && e.key === 'Enter') onSelectSession(s.session_id);
                  }}
                >
                  {isEditing ? (
                    <div className={styles.editRow} onClick={(e) => e.stopPropagation()}>
                      <input
                        type="text"
                        className={styles.renameInput}
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSaveRename(s.session_id, e);
                          if (e.key === 'Escape') handleCancelRename(e);
                        }}
                        autoFocus
                        maxLength={100}
                      />
                      <button
                        type="button"
                        className={styles.saveBtn}
                        onClick={(e) => handleSaveRename(s.session_id, e)}
                        title="Lưu tên mới"
                        aria-label="Lưu tên mới"
                      >
                        ✓
                      </button>
                      <button
                        type="button"
                        className={styles.cancelBtn}
                        onClick={handleCancelRename}
                        title="Hủy"
                        aria-label="Hủy"
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <>
                      <div className={styles.sessionInfo}>
                        <div className={styles.sessionTitle} title={s.topic || 'Phiên học tập'}>
                          {s.topic || 'Phiên học tập'}
                        </div>
                        <div className={styles.sessionTime}>
                          {formatTime(s.created_at)}
                        </div>
                      </div>

                      <div className={styles.actionBtns}>
                        <button
                          type="button"
                          className={styles.renameBtn}
                          onClick={(e) => handleStartRename(s, e)}
                          title="Đổi tên phiên"
                          aria-label="Đổi tên phiên"
                        >
                          <svg
                            width="14"
                            height="14"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          >
                            <path d="M12 20h9" />
                            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                          </svg>
                        </button>

                        <button
                          type="button"
                          className={styles.deleteBtn}
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteSession(s.session_id, e);
                          }}
                          title="Xóa phiên này"
                          aria-label="Xóa phiên"
                        >
                          <svg
                            width="14"
                            height="14"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          >
                            <polyline points="3 6 5 6 21 6" />
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                          </svg>
                        </button>
                      </div>
                    </>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Góc dưới bên trái: Mascot Bot nhỏ & Đèn trang trí */}
        <div className={styles.bottomDecor}>
          <LampIllustration />
          <div className={styles.botBadge}>
            <TutorBotIcon size={32} />
          </div>
        </div>
      </aside>
    </>
  );
}
