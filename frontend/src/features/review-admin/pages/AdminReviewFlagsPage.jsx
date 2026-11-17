// Bài cần xem lại — /admin/review-flags (module 09 · Tuấn · 17/11/2026).
// Human-in-the-loop: câu tự luận bị pipeline gắn cờ (lệch chấm từ khóa, sát ngưỡng đạt, ra lệnh cho AI, thiếu bằng
// chứng, AI lỗi) → admin chọn Đạt / Không đạt từng ý. Đổi sang Đạt → backend tự Hoàn thành khóa + chuông + email.
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import * as reviewAdminApi from '../../../api/reviewAdmin.api.js';
import { parseApiError } from '../../../utils/errors.js';
import FlagCard, { REASON_TEXT } from '../components/FlagCard.jsx';
import styles from '../styles/AdminReviewFlags.module.css';

const PAGE_SIZE = 10;

function resultMessage(result) {
  const { item } = result;
  if (result.completed_course) return `Đã lưu. Lượt ${item.attempt_id} chuyển sang Đạt — khóa học Hoàn thành, đã báo học viên.`;
  if (result.passed_changed) return `Đã lưu. Lượt ${item.attempt_id} đổi kết quả: ${item.attempt_passed ? 'Đạt' : 'Chưa đạt'}.`;
  if (result.score_changed) return `Đã lưu. Điểm lượt ${item.attempt_id}: ${item.attempt_score}/10 (đã cập nhật chuông cho học viên).`;
  return 'Đã xác nhận AI chấm đúng.';
}

export default function AdminReviewFlagsPage() {
  const [status, setStatus] = useState('open');
  const [reason, setReason] = useState('');
  const [courseId, setCourseId] = useState('');
  const [courses, setCourses] = useState([]);
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    reviewAdminApi
      .getReadiness()
      .then((r) => setCourses(r.courses || []))
      .catch(() => {});
  }, []);

  const load = useCallback(async () => {
    setData(null);
    setError('');
    try {
      const params = { status, page, size: PAGE_SIZE };
      if (reason) params.reason = reason;
      if (courseId) params.course_id = courseId;
      setData(await reviewAdminApi.listFlags(params));
    } catch (err) {
      setError(parseApiError(err).message);
      setData({ items: [], total: 0, open_total: 0, resolved_total: 0, reason_counts: {} });
    }
  }, [status, reason, courseId, page]);

  useEffect(() => {
    load();
  }, [load, reloadKey]);

  function choose(setter, value) {
    setter(value);
    setPage(1);
    setNotice('');
  }

  function handleResolved(result) {
    setNotice(resultMessage(result));
    setReloadKey((k) => k + 1);
  }

  const pages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  return (
    <div className={styles.page}>
      <header className={styles.head}>
        <div>
          <h1 className={styles.title}>Bài cần xem lại</h1>
          <p className="muted small" style={{ margin: 0 }}>
            Câu tự luận AI chấm chưa chắc chắn — chọn Đạt / Không đạt từng ý. Đổi sang Đạt thì khóa học tự Hoàn
            thành và học viên được báo qua chuông + email.
          </p>
        </div>
        <Link to="/admin/questions" className="btn btn-sm">
          ← Câu hỏi ôn tập
        </Link>
      </header>

      <div className={`card ${styles.filters}`}>
        <div className={styles.seg} role="radiogroup" aria-label="Trạng thái">
          {[
            ['open', `Chờ xem lại${data ? ` (${data.open_total})` : ''}`],
            ['resolved', `Đã xem lại${data ? ` (${data.resolved_total})` : ''}`],
          ].map(([value, text]) => (
            <button
              key={value}
              type="button"
              role="radio"
              aria-checked={status === value}
              className={status === value ? styles.segOn : ''}
              onClick={() => choose(setStatus, value)}
            >
              {text}
            </button>
          ))}
        </div>
        <select
          className="select"
          aria-label="Lý do"
          value={reason}
          onChange={(e) => choose(setReason, e.target.value)}
        >
          <option value="">Lý do: tất cả</option>
          {Object.entries(REASON_TEXT).map(([value, text]) => (
            <option key={value} value={value}>
              {text}
              {status === 'open' && data?.reason_counts?.[value] !== undefined ? ` (${data.reason_counts[value]})` : ''}
            </option>
          ))}
        </select>
        <select
          className="select"
          aria-label="Khóa học"
          value={courseId}
          onChange={(e) => choose(setCourseId, e.target.value)}
        >
          <option value="">Khóa học: tất cả</option>
          {courses.map((c) => (
            <option key={c.course_id} value={c.course_id}>
              {c.title}
            </option>
          ))}
        </select>
      </div>

      {notice && <div className="alert alert-ok">{notice}</div>}
      {error && <div className="alert">{error}</div>}

      {data === null ? (
        <p className="muted">Đang tải…</p>
      ) : data.items.length === 0 ? (
        <div className={`card ${styles.empty}`}>
          {status === 'open' ? 'Không có câu nào cần xem lại. 🎉' : 'Chưa có câu nào được xem lại.'}
        </div>
      ) : (
        <>
          {data.items.map((item) => (
            <FlagCard key={`${item.attempt_id}-${item.position}-${status}`} item={item} onResolved={handleResolved} />
          ))}
          {pages > 1 && (
            <nav className={styles.pager} aria-label="Phân trang">
              <button type="button" className="btn btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                ← Trước
              </button>
              <span className="small muted">
                Trang {page}/{pages} · {data.total} câu
              </span>
              <button type="button" className="btn btn-sm" disabled={page >= pages} onClick={() => setPage(page + 1)}>
                Sau →
              </button>
            </nav>
          )}
        </>
      )}
    </div>
  );
}
