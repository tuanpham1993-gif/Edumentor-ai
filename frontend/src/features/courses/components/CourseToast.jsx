// Component Toast thông báo nổi khi thao tác Khóa học (Lưu / Bỏ lưu / Lỗi)
// Tuân thủ thiết kế dark amber, tokens.css, không dùng thư viện ngoài.
import { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Link } from 'react-router-dom';

import styles from '../styles/CourseToast.module.css';

/**
 * Biểu tượng dấu tích tròn cho trạng thái thành công
 */
function SuccessCheckIcon() {
  return (
    <svg
      aria-hidden="true"
      width={20}
      height={20}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2.4}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={styles.iconSvg}
    >
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  );
}

/**
 * Biểu tượng ruy-băng bookmark
 */
function BookmarkInfoIcon() {
  return (
    <svg
      aria-hidden="true"
      width={20}
      height={20}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={styles.iconSvg}
    >
      <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
    </svg>
  );
}

/**
 * Biểu tượng cảnh báo
 */
function WarningIcon() {
  return (
    <svg
      aria-hidden="true"
      width={20}
      height={20}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={styles.iconSvg}
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

/**
 * Biểu tượng đóng thông báo (X)
 */
function CloseIcon() {
  return (
    <svg
      aria-hidden="true"
      width={14}
      height={14}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2.5}
      strokeLinecap="round"
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

export default function CourseToast({ toast, onClose }) {
  useEffect(() => {
    if (!toast) return;
    const duration = toast.duration ?? 3800;
    const timer = setTimeout(() => {
      onClose?.();
    }, duration);

    return () => clearTimeout(timer);
  }, [toast, onClose]);

  if (!toast) return null;

  const { type = 'success', message, courseTitle, actionText, actionLink } = toast;

  const typeClass =
    type === 'success'
      ? styles.toastSuccess
      : type === 'warning'
        ? styles.toastWarning
        : type === 'error'
          ? styles.toastError
          : styles.toastInfo;

  return createPortal(
    <div className={styles.toastContainer} role="status" aria-live="polite">
      <div className={`${styles.toast} ${typeClass}`}>
        {/* Biểu tượng trạng thái */}
        <div className={styles.iconWrap}>
          {type === 'success' && <SuccessCheckIcon />}
          {type === 'info' && <BookmarkInfoIcon />}
          {(type === 'warning' || type === 'error') && <WarningIcon />}
        </div>

        {/* Nội dung thông báo */}
        <div className={styles.content}>
          <div className={styles.message}>{message}</div>
          {courseTitle && (
            <div className={styles.subtext} title={courseTitle}>
              {courseTitle}
            </div>
          )}
        </div>

        {/* Nút hành động nhanh (ví dụ: Xem danh sách đã lưu) */}
        {actionLink && actionText && (
          <Link to={actionLink} className={styles.actionBtn} onClick={onClose}>
            {actionText}
          </Link>
        )}

        {/* Nút đóng */}
        <button
          type="button"
          className={styles.closeBtn}
          onClick={onClose}
          aria-label="Đóng thông báo"
        >
          <CloseIcon />
        </button>
      </div>
    </div>,
    document.body
  );
}
