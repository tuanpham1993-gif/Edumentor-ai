import { useState, useEffect } from 'react';
import { useAuth } from '../../../hooks/useAuth.js';
import { getStoredApiKey, setStoredApiKey } from '../../../api/tutor.api.js';
import styles from '../styles/ApiKeyModal.module.css';

/**
 * Modal cấu hình Gemini API Key cá nhân
 * @param {Object} props
 * @param {boolean} props.isOpen - Trạng thái hiển thị modal
 * @param {() => void} props.onClose - Hàm đóng modal
 * @param {(hasKey: boolean) => void} [props.onKeyChanged] - Callback khi key thay đổi
 * @param {number|string} [props.userId] - ID người dùng
 */
export default function ApiKeyModal({ isOpen, onClose, onKeyChanged, userId }) {
  const { user } = useAuth();
  const effectiveUserId = userId !== undefined ? userId : user?.user_id;

  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [hasExistingKey, setHasExistingKey] = useState(false);
  const [notification, setNotification] = useState('');

  useEffect(() => {
    if (isOpen) {
      const stored = getStoredApiKey(effectiveUserId);
      setApiKey(stored);
      setHasExistingKey(Boolean(stored));
      setNotification('');
      setShowKey(false);
    }
  }, [isOpen, effectiveUserId]);

  if (!isOpen) return null;

  const handleSave = () => {
    const trimmed = apiKey.trim();
    setStoredApiKey(trimmed, effectiveUserId);
    setHasExistingKey(Boolean(trimmed));
    setNotification(trimmed ? 'Đã lưu API Key riêng thành công!' : 'Đã xóa API Key riêng, dùng key hệ thống.');
    if (onKeyChanged) onKeyChanged(Boolean(trimmed));
    setTimeout(() => {
      onClose();
    }, 600);
  };

  const handleClear = () => {
    setApiKey('');
    setStoredApiKey('', effectiveUserId);
    setHasExistingKey(false);
    setNotification('Đã xóa API Key riêng.');
    if (onKeyChanged) onKeyChanged(false);
  };

  return (
    <div className={styles.backdrop} onClick={onClose} role="dialog" aria-modal="true">
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.modalHeader}>
          <div className={styles.titleArea}>
            <span className={styles.keyIcon}>🔑</span>
            <h3 className={styles.modalTitle}>Cài đặt Gemini API Key</h3>
          </div>
          <button
            type="button"
            className={styles.closeBtn}
            onClick={onClose}
            aria-label="Đóng"
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className={styles.modalBody}>
          <p className={styles.desc}>
            Nhập Google Gemini API Key riêng của bạn để trò chuyện trực tiếp với AI Tutor mà không dùng chung hay ảnh hưởng đến tài khoản khác.
          </p>
          {user && (
            <div style={{ fontSize: '12px', color: 'var(--text-dim, #8f897f)', marginBottom: '12px' }}>
              👤 Đang cấu hình riêng cho: <strong style={{ color: 'var(--text, #f3efe8)' }}>{user.full_name || user.email}</strong>
            </div>
          )}

          {/* Status Indicator */}
          <div
            className={`${styles.statusCard} ${
              hasExistingKey ? styles.statusCustom : styles.statusDefault
            }`}
          >
            <span>{hasExistingKey ? '✅' : 'ℹ️'}</span>
            <span>
              {hasExistingKey
                ? 'Đang kích hoạt: Sử dụng API Key riêng của bạn'
                : 'Chưa cài đặt: Đang dùng API Key mặc định của EduMentor'}
            </span>
          </div>

          {notification && (
            <div style={{ color: '#22c55e', fontSize: '13px', fontWeight: 600 }}>
              {notification}
            </div>
          )}

          {/* Input Box */}
          <div className={styles.inputGroup}>
            <label className={styles.label} htmlFor="gemini-api-key-input">
              Google Gemini API Key
            </label>
            <div className={styles.inputWrapper}>
              <input
                id="gemini-api-key-input"
                type={showKey ? 'text' : 'password'}
                className={styles.input}
                placeholder="AIzaSy..."
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                autoComplete="off"
                spellCheck="false"
              />
              <button
                type="button"
                className={styles.toggleEyeBtn}
                onClick={() => setShowKey((prev) => !prev)}
                title={showKey ? 'Ẩn API Key' : 'Hiện API Key'}
              >
                {showKey ? '👁️' : '🔒'}
              </button>
            </div>
            <div className={styles.hint}>
              Chưa có key? Nhận miễn phí tại{' '}
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noreferrer"
                className={styles.link}
              >
                Google AI Studio ↗
              </a>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className={styles.modalFooter}>
          {hasExistingKey ? (
            <button
              type="button"
              className={styles.btnDanger}
              onClick={handleClear}
            >
              Xóa key cá nhân
            </button>
          ) : (
            <button
              type="button"
              className={styles.btnSecondary}
              onClick={onClose}
            >
              Hủy
            </button>
          )}

          <button
            type="button"
            className={styles.btnPrimary}
            onClick={handleSave}
          >
            Lưu API Key
          </button>
        </div>
      </div>
    </div>
  );
}
