// ⚠️ TẠM THỜI (Tuấn · 12/11/2026) — nút "Tham gia khóa học" trên trang ôn tập, chờ Khôi làm trang khóa học.
// Lý do (L6, docs/Review-Assessment.md): sau khi nối user_courses của Khôi, phải tham gia khóa mới ôn được,
// nhưng frontend chưa có nút Tham gia ở đâu cả.
// KHI KHÔI XONG: xóa file này + 2 dòng dùng nó trong ReviewStartPage.jsx (tìm "TempJoinCourseButton"),
// thay bằng nút / API của Khôi (api/courseTracking.api.js).
// Gọi API của Khôi: POST /api/courses/{courseId}/join — idempotent; thêm kỹ năng của khóa vào "Đang học".
import { useState } from 'react';

import client from '../../../api/client.js';
import { parseApiError } from '../../../utils/errors.js';

export default function TempJoinCourseButton({ courseId, rejoin = false, onJoined }) {
  const [joining, setJoining] = useState(false);
  const [error, setError] = useState('');

  async function handleJoin() {
    setJoining(true);
    setError('');
    try {
      await client.post(`/courses/${courseId}/join`);
      await onJoined();
    } catch (err) {
      setError(parseApiError(err).message);
    } finally {
      setJoining(false);
    }
  }

  return (
    <div className="stack" style={{ gap: 8, marginTop: 12 }}>
      <button type="button" className="btn btn-primary" onClick={handleJoin} disabled={joining}>
        {joining ? 'Đang tham gia…' : rejoin ? 'Tham gia lại khóa học' : 'Tham gia khóa học'}
      </button>
      {error && (
        <p className="alert" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
