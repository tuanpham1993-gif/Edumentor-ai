// Máy chủ tạm thời không phục vụ — 503 (module 01 · Tuấn · FĐ7, 08/11/2026).
// Hiện khi mở app (đã có token) mà không tới được backend: backend tắt, đang khởi động
// (seed ~9 giây), mất mạng, hoặc backend trả 5xx. KHÔNG xóa đăng nhập — bấm "Thử lại" là vào tiếp.
//   onRetry: hàm thử lại (authStore.retry → gọi lại GET /me)
import { useState } from 'react';

import StatusPanel from '../components/common/StatusPanel.jsx';

export default function ServerErrorPage({ onRetry }) {
  const [busy, setBusy] = useState(false);

  async function handleRetry() {
    setBusy(true);
    try {
      await onRetry();
    } finally {
      setBusy(false); // vẫn lỗi → ở lại trang này
    }
  }

  return (
    <StatusPanel
      fullPage
      icon="server"
      tone="danger"
      title="Máy chủ tạm thời không phục vụ"
      code="Mã: 503 · Service Unavailable"
      actions={
        <button
          type="button"
          className={`btn btn-primary ${busy ? 'loading' : ''}`}
          onClick={handleRetry}
          disabled={busy}
        >
          Thử lại
          <span className="spinner" aria-hidden="true" />
        </button>
      }
    >
      Không kết nối được tới máy chủ, hoặc máy chủ đang bảo trì / khởi động. Vui lòng thử lại sau ít
      phút.
    </StatusPanel>
  );
}
