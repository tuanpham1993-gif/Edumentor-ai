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
 * @param {boolean} [props.isOpenMobile=false]
 * @param {() => void} [props.onCloseMobile]
 */
export default function TutorSidebar({
  sessions = [],
  activeSessionId,
  onSelectSession,
  onCreateNewSession,
  onDeleteSession,
  isOpenMobile = false,
  onCloseMobile,
}) {
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
              return (
                <div
                  key={s.session_id}
                  className={`${styles.sessionItem} ${isActive ? styles.activeItem : ''}`}
                  onClick={() => onSelectSession(s.session_id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') onSelectSession(s.session_id);
                  }}
                >
                  <div className={styles.sessionInfo}>
                    <div className={styles.sessionTitle} title={s.topic || 'Phiên học tập'}>
                      {s.topic || 'Phiên học tập'}
                    </div>
                    <div className={styles.sessionTime}>
                      {formatTime(s.created_at)}
                    </div>
                  </div>

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
                      width="15"
                      height="15"
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
