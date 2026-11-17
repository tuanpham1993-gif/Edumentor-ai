// Drawer chi tiết phản hồi học viên (FĐ Admin · F13, Screen 7)
import React from 'react';
import styles from '../styles/AdminFeedback.module.css';

export default function AdminFeedbackDrawer({ feedback, onClose }) {
  if (!feedback) return null;

  const mailtoLink = `mailto:${feedback.senderEmail}?subject=${encodeURIComponent(
    `[EduMentor AI] Phản hồi về góp ý #${feedback.id}`
  )}&body=${encodeURIComponent(
    `Chào ${feedback.senderName},\n\nCảm ơn bạn đã đóng góp ý kiến về "${
      feedback.targetDetail || feedback.target
    }":\n"${feedback.content}"\n\n`
  )}`;

  return (
    <aside className={styles.drawer} aria-label={`Chi tiết phản hồi #${feedback.id}`}>
      <div className={styles.drawerHeader}>
        <h2>Phản hồi #{feedback.id}</h2>
        <button
          type="button"
          className={styles.clearFilterBtn}
          onClick={onClose}
          aria-label="Đóng"
          style={{ textDecoration: 'none', fontSize: '18px', color: 'var(--text-muted)' }}
        >
          ✕
        </button>
      </div>

      <div className={styles.drawerBadges}>
        <span className={styles.badgePill}>{feedback.target}</span>
        <span className={styles.badgeType}>{feedback.type}</span>
      </div>

      <div className={styles.metaList}>
        <span className={styles.metaKey}>Người gửi</span>
        <span className={styles.metaVal}>
          <b>{feedback.senderName}</b>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{feedback.senderEmail}</div>
        </span>

        {feedback.targetDetail && (
          <>
            <span className={styles.metaKey}>Khóa học</span>
            <span className={styles.metaVal}>
              {feedback.targetDetail} {feedback.platform && `[${feedback.platform}]`}
            </span>
          </>
        )}

        <span className={styles.metaKey}>Thời gian</span>
        <span className={styles.metaVal}>{feedback.time}</span>
      </div>

      <div className={styles.quoteBox}>{feedback.content}</div>

      {feedback.instructorContact && (
        <div className={styles.instructorCard}>
          <span className={styles.instructorLabel}>Liên hệ của khóa học</span>
          <span className={styles.instructorVal}>{feedback.instructorContact}</span>
        </div>
      )}

      <a href={mailtoLink} className={styles.replyEmailBtn}>
        <svg
          aria-hidden="true"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect width="20" height="16" x="2" y="4" rx="2" />
          <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
        </svg>
        Trả lời qua email
      </a>
    </aside>
  );
}
