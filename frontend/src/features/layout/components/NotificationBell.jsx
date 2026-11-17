// Chuông thông báo trên header (module 01 · Tuấn · 11/11/2026) — kiểu thông báo Facebook.
//   - Nút chuông + số chưa đọc (99+). Hỏi số chưa đọc mỗi 60 giây và khi quay lại tab.
//   - Bấm → khung: 2 tab "Tất cả" / "Chưa đọc", "Đánh dấu đã đọc tất cả".
//   - Bấm một thông báo → đánh dấu đã đọc rồi mở link của nó.
//   - Đóng: bấm ra ngoài, phím Esc, hoặc bấm lại chuông.
// API: api/notifications.api.js · Backend: routers/v1/endpoints/notifications.py
import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import * as notificationsApi from '../../../api/notifications.api.js';
import { timeAgo } from '../../../utils/formatters.js';
import styles from '../styles/NotificationBell.module.css';

const POLL_MS = 60_000;
const TABS = [
  { value: 'all', text: 'Tất cả' },
  { value: 'unread', text: 'Chưa đọc' },
];

// Icon nhỏ theo loại thông báo (models/notification.TYPES)
const TYPE_ICON = {
  review_graded: <path d="M9 11l3 3 8-8M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h9" />,
  course_completed: <path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4zM17 6h3v2a3 3 0 0 1-3 3M7 6H4v2a3 3 0 0 0 3 3" />,
  password_changed: <path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z" />,
  welcome: <path d="M12 3l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.4 6.8 19.1l1-5.8L3.5 9.2l5.9-.9L12 3z" />,
};

function BellIcon() {
  return (
    <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9M10.3 21a1.9 1.9 0 0 0 3.4 0" />
    </svg>
  );
}

export default function NotificationBell() {
  const navigate = useNavigate();
  const wrapRef = useRef(null);
  const buttonRef = useRef(null);
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState('all');
  const [unread, setUnread] = useState(0);
  const [data, setData] = useState(null); // null = đang tải; { items, total }
  const [error, setError] = useState(false);

  const refreshCount = useCallback(() => {
    notificationsApi.getUnreadCount().then(setUnread).catch(() => {});
  }, []);

  // Hỏi số chưa đọc: ngay khi vào, mỗi 60 giây (chỉ khi tab đang hiện) và khi quay lại tab
  useEffect(() => {
    refreshCount();
    const timer = setInterval(() => document.visibilityState === 'visible' && refreshCount(), POLL_MS);
    const onFocus = () => refreshCount();
    window.addEventListener('focus', onFocus);
    return () => {
      clearInterval(timer);
      window.removeEventListener('focus', onFocus);
    };
  }, [refreshCount]);

  // Mở khung / đổi tab → tải danh sách
  useEffect(() => {
    if (!open) return undefined;
    let cancelled = false;
    setData(null);
    setError(false);
    notificationsApi
      .getNotifications({ unreadOnly: tab === 'unread' })
      .then((page) => {
        if (cancelled) return;
        setData(page);
        setUnread(page.unread_count);
      })
      .catch(() => !cancelled && setError(true));
    return () => {
      cancelled = true;
    };
  }, [open, tab]);

  // Bấm ra ngoài / Esc → đóng
  useEffect(() => {
    if (!open) return undefined;
    const onDown = (event) => {
      if (!wrapRef.current?.contains(event.target)) setOpen(false);
    };
    const onKey = (event) => {
      if (event.key === 'Escape') {
        setOpen(false);
        buttonRef.current?.focus();
      }
    };
    document.addEventListener('mousedown', onDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  async function openItem(item) {
    if (!item.is_read) {
      setUnread((n) => Math.max(0, n - 1));
      setData((d) => d && { ...d, items: d.items.map((x) => (x.notification_id === item.notification_id ? { ...x, is_read: true } : x)) });
      notificationsApi.markRead(item.notification_id).catch(() => {});
    }
    setOpen(false);
    if (item.link) navigate(item.link);
  }

  async function readAll() {
    try {
      await notificationsApi.markAllRead();
      setUnread(0);
      setData((d) =>
        d && (tab === 'unread' ? { ...d, items: [], total: 0 } : { ...d, items: d.items.map((x) => ({ ...x, is_read: true })) }),
      );
    } catch {
      // lỗi mạng: giữ nguyên, lần mở sau tải lại
    }
  }

  const badge = unread > 99 ? '99+' : unread;

  return (
    <div className={styles.wrap} ref={wrapRef}>
      <button
        ref={buttonRef}
        type="button"
        className={`${styles.bell} ${open ? styles.bellOpen : ''}`}
        aria-label={unread > 0 ? `Thông báo, ${unread} chưa đọc` : 'Thông báo'}
        aria-haspopup="dialog"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        <BellIcon />
        {unread > 0 && (
          <span className={styles.badge} aria-hidden="true">
            {badge}
          </span>
        )}
      </button>

      {open && (
        <div className={styles.panel} role="dialog" aria-label="Thông báo">
          <div className={styles.head}>
            <h2>Thông báo</h2>
            <button type="button" className={styles.readAll} onClick={readAll} disabled={unread === 0}>
              Đánh dấu đã đọc tất cả
            </button>
          </div>

          <div className={styles.tabs} role="tablist" aria-label="Lọc thông báo">
            {TABS.map((t) => (
              <button
                key={t.value}
                type="button"
                role="tab"
                aria-selected={tab === t.value}
                className={`${styles.tab} ${tab === t.value ? styles.tabActive : ''}`}
                onClick={() => setTab(t.value)}
              >
                {t.text}
                {t.value === 'unread' && unread > 0 && <span className={styles.tabCount}>{badge}</span>}
              </button>
            ))}
          </div>

          <div className={styles.list}>
            {error && <p className={styles.empty}>Không tải được thông báo.</p>}
            {!error && data === null &&
              [0, 1, 2].map((i) => <div key={i} className="skeleton" style={{ height: 52, margin: '6px 8px' }} aria-hidden="true" />)}
            {!error && data?.items.length === 0 && (
              <p className={styles.empty}>{tab === 'unread' ? 'Bạn đã đọc hết thông báo.' : 'Chưa có thông báo nào.'}</p>
            )}
            {data?.items.map((item) => (
              <button
                key={item.notification_id}
                type="button"
                className={`${styles.item} ${item.is_read ? '' : styles.unread}`}
                onClick={() => openItem(item)}
              >
                <span className={`${styles.icon} ${styles[`icon_${item.type}`] ?? ''}`} aria-hidden="true">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    {TYPE_ICON[item.type] ?? TYPE_ICON.welcome}
                  </svg>
                </span>
                <span className={styles.text}>
                  <strong>{item.title}</strong>
                  {item.body && <span className={styles.body}>{item.body}</span>}
                  <span className={styles.time}>{timeAgo(item.created_at)}</span>
                </span>
                {!item.is_read && <span className={styles.dot} aria-label="Chưa đọc" />}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
