import { useState, useEffect } from 'react';
import { getStoredApiKey } from '../../../api/tutor.api.js';
import ApiKeyModal from './ApiKeyModal.jsx';
import styles from '../styles/TutorHeader.module.css';

/**
 * Thanh tiêu đề phiên chat AI Tutor
 * @param {Object} props
 * @param {string} props.topic - Tên chủ đề của phiên
 * @param {string} [props.subtitle] - Ghi chú phụ
 * @param {() => void} [props.onToggleSidebar] - Mở sidebar trên mobile
 */
export default function TutorHeader({
  topic = 'Phiên học tập mới',
  subtitle = 'AI Tutor nhớ ngữ cảnh trong phiên này',
  onToggleSidebar,
}) {
  const [isKeyModalOpen, setIsKeyModalOpen] = useState(false);
  const [hasCustomKey, setHasCustomKey] = useState(false);

  useEffect(() => {
    setHasCustomKey(Boolean(getStoredApiKey()));
  }, []);

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
            <h1 className={styles.topicTitle}>{topic}</h1>
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
      />
    </>
  );
}
