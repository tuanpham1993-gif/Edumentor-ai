import { useEffect, useState } from 'react';
import {
  enableLearningPathShare,
  disableLearningPathShare,
} from '../../../../api/learningPaths.api';
import styles from '../../styles/ShareLearningPathModal.module.css';

export default function ShareLearningPathModal({
  recordId,
  learningPath,
  onClose,
  onSuccess,
}) {
  const [isShared, setIsShared] = useState(Boolean(learningPath?.is_shared));
  const [shareCode, setShareCode] = useState(learningPath?.share_code || '');
  const [cloneCount, setCloneCount] = useState(learningPath?.clone_count || 0);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');

  const shareUrl = shareCode
    ? `${window.location.origin}/shared/learning-paths/${shareCode}`
    : '';

  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === 'Escape' && !loading) {
        onClose();
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [loading, onClose]);

  async function handleToggleShare() {
    setLoading(true);
    setError('');
    try {
      if (!isShared) {
        const result = await enableLearningPathShare(recordId);
        setIsShared(true);
        setShareCode(result.share_code);
        setCloneCount(result.clone_count || 0);
        onSuccess?.(result);
      } else {
        const result = await disableLearningPathShare(recordId);
        setIsShared(false);
        onSuccess?.(result);
      }
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Không thể thay đổi trạng thái chia sẻ.'
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy() {
    if (!shareUrl) return;
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Fallback
      setError('Không thể tự động sao chép. Bạn vui lòng chọn và copy link bằng tay.');
    }
  }

  return (
    <div
      className={styles.backdrop}
      onClick={() => !loading && onClose()}
    >
      <section
        className={styles.modal}
        role="dialog"
        aria-modal="true"
        aria-labelledby="share-path-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header className={styles.header}>
          <div className={styles.headerTitleGroup}>
            <span className={styles.headerIcon}>🔗</span>
            <h2 id="share-path-title">Chia sẻ lộ trình học tập</h2>
          </div>
          <button
            type="button"
            className={styles.closeButton}
            onClick={onClose}
            disabled={loading}
            aria-label="Đóng"
          >
            ×
          </button>
        </header>

        <div className={styles.body}>
          <p className={styles.pathQuery}>
            <strong>Lộ trình:</strong> {learningPath?.original_query || 'Lộ trình cá nhân'}
          </p>

          <div className={styles.statusBox}>
            <div className={styles.statusRow}>
              <div>
                <p className={styles.statusLabel}>Trạng thái liên kết</p>
                <p className={styles.statusValue}>
                  {isShared ? (
                    <span className={styles.badgeActive}>● Đang chia sẻ</span>
                  ) : (
                    <span className={styles.badgeInactive}>○ Riêng tư</span>
                  )}
                </p>
              </div>

              <button
                type="button"
                className={`btn ${isShared ? 'btn-soft' : 'btn-primary'}`}
                onClick={handleToggleShare}
                disabled={loading}
              >
                {loading
                  ? 'Đang xử lý...'
                  : isShared
                  ? 'Tắt chia sẻ'
                  : 'Bật chia sẻ'}
              </button>
            </div>

            {isShared && (
              <div className={styles.shareContent}>
                <p className={styles.shareGuide}>
                  Bất kỳ ai có liên kết này đều có thể xem đồ thị lộ trình và lưu làm lộ trình học tập của riêng họ.
                </p>

                <div className={styles.linkGroup}>
                  <input
                    type="text"
                    readOnly
                    value={shareUrl}
                    className={`input ${styles.urlInput}`}
                    onClick={(e) => e.target.select()}
                  />
                  <button
                    type="button"
                    className={`btn ${copied ? 'btn-soft' : 'btn-primary'} ${styles.copyButton}`}
                    onClick={handleCopy}
                  >
                    {copied ? '✓ Đã sao chép' : 'Sao chép'}
                  </button>
                </div>

                <div className={styles.statsNotice}>
                  <span className={styles.statsIcon}>👥</span>
                  <span>
                    Đã có <strong>{cloneCount}</strong> học viên học theo lộ trình này.
                  </span>
                </div>
              </div>
            )}

            {!isShared && (
              <p className={styles.privateGuide}>
                Lộ trình hiện đang được giữ riêng tư cho bạn. Hãy bật chia sẻ để bạn bè hoặc cộng đồng học viên cùng tham khảo!
              </p>
            )}
          </div>

          {error && (
            <p className={styles.errorMessage} role="alert">
              {error}
            </p>
          )}
        </div>

        <footer className={styles.footer}>
          <button
            type="button"
            className="btn"
            onClick={onClose}
            disabled={loading}
          >
            Đóng
          </button>
        </footer>
      </section>
    </div>
  );
}
