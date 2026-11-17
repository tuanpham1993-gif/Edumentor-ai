// Hộp thoại "Đăng xuất?" (module 01 · Tuấn · FĐ5, 07/11/2026).
// Dùng ở menu avatar (header) và menu trái Cài đặt tài khoản.
//   - Esc / bấm nền mờ / "Hủy" → đóng. Mở ra con trỏ đặt sẵn ở "Hủy" (an toàn hơn).
//   - "Đăng xuất" → POST /auth/logout (thu hồi phiên trên server) → /login.
import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../../hooks/useAuth.js';
import styles from '../styles/LogoutDialog.module.css';

export default function LogoutDialog({ open, onClose }) {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const cancelRef = useRef(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!open) return undefined;
    cancelRef.current?.focus();
    function onKey(event) {
      if (event.key === 'Escape' && !busy) onClose();
    }
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [open, busy, onClose]);

  if (!open) return null;

  async function handleLogout() {
    setBusy(true);
    await logout(); // lỗi mạng vẫn xóa phiên trên trình duyệt (authStore)
    navigate('/login', { replace: true });
  }

  // Portal ra <body> (12/11): mở từ menu avatar trong header — header có backdrop-filter nên
  // position: fixed bên trong bị tính theo header (hộp bị kẹt / cắt ở mép trên). Ra <body> → luôn giữa màn hình.
  return createPortal(
    <div
      className={styles.backdrop}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !busy) onClose();
      }}
    >
      <div
        className={styles.dialog}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="logout-title"
        aria-describedby="logout-desc"
      >
        <span className={styles.icon} aria-hidden="true">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 17l-5-5 5-5M5 12h11" />
          </svg>
        </span>
        <h2 id="logout-title">Đăng xuất?</h2>
        <p id="logout-desc">Bạn sẽ cần đăng nhập lại để tiếp tục học.</p>
        <div className={styles.actions}>
          <button ref={cancelRef} type="button" className="btn" onClick={onClose} disabled={busy}>
            Hủy
          </button>
          <button
            type="button"
            className={`btn btn-danger ${busy ? 'loading' : ''}`}
            onClick={handleLogout}
            disabled={busy}
          >
            Đăng xuất
            <span className="spinner" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
