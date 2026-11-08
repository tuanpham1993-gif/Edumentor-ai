// Hiện trạng thái kết nối backend (module 01 · Tuấn · FĐ0, 07/11/2026).
// Bài tập React đầu tiên: useState (biến trạng thái) + useEffect (gọi API sau khi hiện lên).
// Gọi "/api/..." (đường dẫn tương đối) → đi qua proxy Vite sang backend :8000.
import { useEffect, useState } from 'react';

export default function BackendStatus() {
  // 'loading' | 'ok' | 'error' — đổi giá trị bằng setStatus → React tự vẽ lại
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    // Chạy 1 lần sau khi component hiện lên (mảng [] rỗng)
    fetch('/api/health/health')
      .then((response) => response.json())
      .then((data) => setStatus(data.database === 'connected' ? 'ok' : 'error'))
      .catch(() => setStatus('error')); // backend tắt / lỗi mạng
  }, []);

  if (status === 'loading') {
    return <p className="muted">Đang kiểm tra backend…</p>;
  }
  if (status === 'ok') {
    return <p className="alert alert-ok">Backend: đã kết nối ✓</p>;
  }
  return (
    <p className="alert">
      Backend: không kết nối được. Hãy chạy <code>uvicorn app.main:app --reload</code> trong
      thư mục backend.
    </p>
  );
}
