import { useState, useEffect } from 'react';
import { useAuth } from '../../../hooks/useAuth.js';
import { getStoredApiKey } from '../../../api/tutor.api.js';
import ApiKeyModal from './ApiKeyModal.jsx';
import styles from '../styles/TutorHeader.module.css';

/**
 * Thanh tiêu đề phiên chat AI Tutor
 * @param {Object} props
 * @param {string} props.topic - Tên chủ đề của phiên
 * @param {string} [props.subtitle] - Ghi chú phụ
 * @param {() => void} [props.onToggleSidebar] - Mở sidebar trên mobile
 * @param {string} [props.activeSessionId] - ID của phiên hiện tại
 * @param {(sessionId: string, newTopic: string) => void} [props.onRenameSession] - Hàm đổi tên phiên
 */
export default function TutorHeader({
  topic = 'Phiên học tập mới',
  subtitle = 'AI Tutor nhớ ngữ cảnh trong phiên này',
  onToggleSidebar,
  activeSessionId,
  onRenameSession,
}) {
  const { user } = useAuth();
  const [isKeyModalOpen, setIsKeyModalOpen] = useState(false);
  const [hasCustomKey, setHasCustomKey] = useState(false);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [headerTitle, setHeaderTitle] = useState(topic);

  useEffect(() => {
    setHasCustomKey(Boolean(getStoredApiKey(user?.user_id)));
  }, [user]);

  useEffect(() => {
    setHeaderTitle(topic);
    setIsEditingTitle(false);
  }, [topic, activeSessionId]);

  const handleSaveHeaderRename = () => {
    const clean = headerTitle.trim();
    if (clean && clean !== topic && onRenameSession && activeSessionId) {
      onRenameSession(activeSessionId, clean);
    }
    setIsEditingTitle(false);
  };

  return (
    <>
      <header className={styles.header}>
        <div className={styles.titleArea}>
          {onToggleSidebar && (
            <button
              type="button"
              className={styles.menuToggleBtn}
              onClick={onToggleSidebar}
              title="Danh sách phiên chat"
              aria-label="Mở danh sách phiên chat"
            >
              ☰
            </button>
          )}
          <div className={styles.textGroup}>
            {isEditingTitle ? (
              <div className={styles.headerEditRow}>
                <input
                  type="text"
                  className={styles.headerRenameInput}
                  value={headerTitle}
                  onChange={(e) => setHeaderTitle(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveHeaderRename();
                    if (e.key === 'Escape') {
                      setHeaderTitle(topic);
                      setIsEditingTitle(false);
                    }
                  }}
                  onBlur={handleSaveHeaderRename}
                  autoFocus
                  maxLength={100}
                />
                <button
                  type="button"
                  className={styles.headerSaveBtn}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={handleSaveHeaderRename}
                  title="Lưu tên"
                  aria-label="Lưu tên"
                >
                  ✓
                </button>
              </div>
            ) : (
              <div className={styles.titleWithEdit}>
                <h1 className={styles.topicTitle} title={topic}>{topic}</h1>
                {onRenameSession && activeSessionId && (
                  <button
                    type="button"
                    className={styles.headerRenameBtn}
                    onClick={() => {
                      setHeaderTitle(topic);
                      setIsEditingTitle(true);
                    }}
                    title="Đổi tên phiên chat"
                    aria-label="Đổi tên phiên chat"
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
                )}
              </div>
            )}
            <p className={styles.subtitle}>{subtitle}</p>
          </div>
        </div>

        <div className={styles.actionsArea}>
          <button
            type="button"
            className={`${styles.apiKeyBtn} ${hasCustomKey ? styles.apiKeyBtnActive : ''}`}
            onClick={() => setIsKeyModalOpen(true)}
            title="Cài đặt Gemini API Key cá nhân"
          >
            <span>🔑</span>
            <span>{hasCustomKey ? 'Key cá nhân' : 'Nhập API Key'}</span>
            {hasCustomKey && <span className={styles.activeDot} />}
          </button>
        </div>
      </header>

      <ApiKeyModal
        isOpen={isKeyModalOpen}
        onClose={() => setIsKeyModalOpen(false)}
        onKeyChanged={(hasKey) => setHasCustomKey(hasKey)}
        userId={user?.user_id}
      />
    </>
  );
}
