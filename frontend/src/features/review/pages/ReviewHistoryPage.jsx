// Lịch sử ôn tập (module 09 · Tuấn · GĐ4, 09/11/2026) — màn demo ReviewHistory, route /me/review-history
// (mục "Ôn tập" trên thanh điều hướng). Lọc theo khóa học + kết quả (giữ trên URL: ?course=312&result=passed),
// phân trang 10 dòng. Mỗi dòng: Xem chi tiết / Làm lại.
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import * as reviewApi from '../../../api/review.api.js';
import Pagination from '../../common/components/Pagination.jsx';
import { parseApiError } from '../../../utils/errors.js';
import { formatDateTime } from '../../../utils/formatters.js';
import { DEMO_COURSES, formatScore } from '../reviewFormat.js';
import styles from '../styles/ReviewHistoryPage.module.css';

const PAGE_SIZE = 10;
const RESULT_FILTER = { all: undefined, passed: true, failed: false };

export default function ReviewHistoryPage() {
  const [params, setParams] = useSearchParams();
  const course = params.get('course') ?? '';
  const resultFilter = params.get('result') ?? 'all';
  const page = Math.max(1, Number(params.get('page')) || 1);

  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [knownCourses, setKnownCourses] = useState(() => new Map(DEMO_COURSES.map((c) => [String(c.courseId), c.title])));

  const load = useCallback(async () => {
    setError('');
    try {
      const page_ = await reviewApi.getHistory({
        courseId: course || undefined,
        passed: RESULT_FILTER[resultFilter],
        page,
        size: PAGE_SIZE,
      });
      setData(page_);
      setKnownCourses((current) => {
        const next = new Map(current);
        page_.items.forEach((item) => next.set(String(item.course_id), item.course_title));
        return next;
      });
    } catch (err) {
      setError(parseApiError(err).message);
    }
  }, [course, resultFilter, page]);

  useEffect(() => {
    load();
  }, [load]);

  function setFilter(key, value) {
    const next = new URLSearchParams(params);
    if (value && value !== 'all') next.set(key, value);
    else next.delete(key);
    next.delete('page'); // đổi bộ lọc → về trang 1
    setParams(next, { replace: true });
  }

  function setPage(value) {
    const next = new URLSearchParams(params);
    if (value > 1) next.set('page', String(value));
    else next.delete('page');
    setParams(next);
  }

  const courseOptions = useMemo(() => [...knownCourses.entries()], [knownCourses]);
  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;
  const filtered = Boolean(course) || resultFilter !== 'all';

  return (
    <>
      <header className="page-head">
        <div>
          <h1>Lịch sử ôn tập</h1>
          <p>Xem lại các lần làm bài, điểm số và đáp án chi tiết.</p>
        </div>
      </header>

      <section className={`card ${styles.panel}`}>
        <div className={styles.filters}>
          <label className="field">
            <span>Khóa học</span>
            <select className="select" value={course} onChange={(e) => setFilter('course', e.target.value)}>
              <option value="">Tất cả khóa học</option>
              {courseOptions.map(([id, title]) => (
                <option key={id} value={id}>
                  {title}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Kết quả</span>
            <select className="select" value={resultFilter} onChange={(e) => setFilter('result', e.target.value)}>
              <option value="all">Tất cả</option>
              <option value="passed">Đạt</option>
              <option value="failed">Chưa đạt</option>
            </select>
          </label>
        </div>

        {error && (
          <div className="alert" role="alert">
            {error}{' '}
            <button type="button" className="btn btn-sm" onClick={load}>
              Thử lại
            </button>
          </div>
        )}

        {!data && !error && <div className="skeleton" style={{ height: 240 }} aria-busy="true" />}

        {data && data.items.length === 0 && (
          <div className={styles.empty}>
            {filtered ? (
              <p className="muted">Không có lần làm bài nào khớp bộ lọc.</p>
            ) : (
              <>
                <p className="muted">Bạn chưa làm bài ôn tập nào. Bắt đầu với khóa đã có đề ôn tập:</p>
                <ul className={styles.demo}>
                  {DEMO_COURSES.map((c) => (
                    <li key={c.courseId}>
                      <Link to={`/courses/${c.courseId}/review`} className="btn btn-primary">
                        Ôn tập: {c.title} →
                      </Link>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        )}

        {data && data.items.length > 0 && (
          <>
            <div className="table-wrap">
              <table className={`table ${styles.table}`}>
                <thead>
                  <tr>
                    <th>Thời gian nộp</th>
                    <th>Khóa học</th>
                    <th>Điểm</th>
                    <th>Kết quả</th>
                    <th className={styles.actionsCol}>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((item) => (
                    <tr key={item.attempt_id}>
                      <td className="muted">{formatDateTime(item.submitted_at)}</td>
                      <td className={styles.course}>
                        {item.course_title}
                        {item.completed_course && <span className="chip chip-accent">Hoàn thành khóa</span>}
                      </td>
                      <td className={styles.score}>{formatScore(item.score)}/10</td>
                      <td>
                        <span className={`chip ${item.passed ? 'chip-ok' : 'chip-danger'}`}>
                          {item.passed ? 'Đạt' : 'Chưa đạt'}
                        </span>
                      </td>
                      <td className={styles.actions}>
                        <Link to={`/review/${item.attempt_id}/result`} className="btn btn-sm">
                          Xem chi tiết
                        </Link>
                        <Link to={`/courses/${item.course_id}/review`} className="btn btn-sm btn-soft">
                          Làm lại
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className={styles.footer}>
              <span className="muted small">
                Hiển thị {(page - 1) * PAGE_SIZE + 1}–{(page - 1) * PAGE_SIZE + data.items.length} trong{' '}
                {data.total} lần làm bài
              </span>
              <Pagination page={page} totalPages={totalPages} onChange={setPage} label="Phân trang lịch sử ôn tập" />
            </div>
          </>
        )}
      </section>
    </>
  );
}
