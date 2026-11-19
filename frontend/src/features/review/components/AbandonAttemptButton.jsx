// Nút "Bỏ bài" cho bài ôn tập làm dở (module 09 · Tuấn · 19/11/2026).
// Bấm lần 1 → hỏi lại ngay tại chỗ (không dùng hộp thoại trình duyệt); xác nhận → DELETE /review-attempts/{id}.
// Bài bị xóa hẳn: không điểm, không vào lịch sử. Xong gọi onDone() để trang tải lại.
import { useState } from 'react';

import * as reviewApi from '../../../api/review.api.js';
import { parseApiError } from '../../../utils/errors.js';
import styles from '../styles/ReviewStartPage.module.css';

export default function AbandonAttemptButton({ attemptId, onDone, label = 'Bỏ bài' }) {
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function abandon() {
    setBusy(true);
    setError('');
    try {
      await reviewApi.abandonAttempt(attemptId);
      onDone?.();
    } catch (err) {
      setError(parseApiError(err).message);
      setBusy(false);
    }
  }

  if (!confirming) {
    return (
      <button type="button" className="btn btn-sm" onClick={() => setConfirming(true)}>
        {label}
      </button>
    );
  }
  return (
    <span className={styles.abandonConfirm} role="group" aria-label="Xác nhận bỏ bài">
      <span className="small">Bỏ bài này? Câu trả lời đã lưu sẽ mất.</span>
      <button type="button" className="btn btn-sm btn-danger" onClick={abandon} disabled={busy}>
        {busy ? 'Đang bỏ…' : 'Bỏ bài'}
      </button>
      <button type="button" className="btn btn-sm" onClick={() => setConfirming(false)} disabled={busy}>
        Giữ lại
      </button>
      {error && (
        <span className="small" role="alert">
          {error}
        </span>
      )}
    </span>
  );
}
