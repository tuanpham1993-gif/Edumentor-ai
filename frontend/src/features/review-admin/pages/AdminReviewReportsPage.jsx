// Câu bị phản ánh — /admin/review-reports (module 09 · Tuấn · G3f, 25/11/2026 — D19–D23).
// MENTOR phản ánh câu AI soạn (học viên không phản ánh) → câu TẮT NGAY, chờ admin. Trang gom theo câu hỏi. Admin:
//   Sửa câu      → mở trang Câu hỏi ôn tập; lưu xong: phản ánh tự đóng, câu bật lại, coi như Đạt
//   Giữ tắt      → mentor đúng, câu không dùng nữa
//   Bác phản ánh → câu đúng: bật lại, coi như Đạt
// Xử lý xong → chuông báo mentor.
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import * as reviewAdminApi from '../../../api/reviewAdmin.api.js';
import { parseApiError } from '../../../utils/errors.js';
import { formatDateTime } from '../../../utils/formatters.js';
import styles from '../styles/AdminReviewFlags.module.css';

const PAGE_SIZE = 10;
const LETTERS = ['A', 'B', 'C', 'D'];
export const REPORT_REASON_TEXT = {
  wrong_answer: 'Đáp án đúng bị sai',
  ambiguous: 'Câu mơ hồ / 2 đáp án đúng',
  wrong_knowledge: 'Sai kiến thức',
  bad_rubric: 'Barem không hợp lý',
  other: 'Khác',
};
const STATUS_TEXT = { open: 'Chờ xử lý', resolved: 'Đã sửa / giữ tắt', dismissed: 'Đã bác' };

function ReportCard({ item, onResolve, busy }) {
  const q = item.question;
  const isOpen = item.reports.some((r) => r.status === 'open');
  return (
    <article className={`card ${styles.card}`}>
      <div className={styles.cardHead}>
        <div className={styles.who}>
          <strong>
            Câu #{q.question_id}
            {q.code ? ` (${q.code})` : ''} · {q.skill} · {q.type === 'mcq' ? 'Trắc nghiệm' : 'Tự luận'}
          </strong>
          <span className="small muted">Mới nhất {formatDateTime(item.latest_at)}</span>
        </div>
        <div className={styles.chips}>
          <span className="chip chip-info">AI soạn</span>
          {q.disabled_by_report && <span className="chip chip-danger">Đang tắt · chờ xử lý</span>}
          {!q.is_active && !q.disabled_by_report && <span className="chip">Đang tắt</span>}
          {q.is_active && <span className="chip chip-ok">Đang bật</span>}
        </div>
      </div>

      <p className={styles.question}>{q.content}</p>
      {q.type === 'mcq' && (
        <ul className="small" style={{ margin: 0, paddingLeft: 18 }}>
          {(q.options || []).map((opt, i) => (
            <li key={LETTERS[i]} style={i === q.correct_index ? { fontWeight: 700 } : undefined}>
              {LETTERS[i]}. {opt} {i === q.correct_index && '← đáp án đang ghi'}
            </li>
          ))}
        </ul>
      )}

      <ul className="small" style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 4 }}>
        {item.reports.map((r) => (
          <li key={r.report_id}>
            <b>{REPORT_REASON_TEXT[r.reason]}</b>
            {r.note ? ` — "${r.note}"` : ''} <span className="muted">(mentor {r.user_name}, {formatDateTime(r.created_at)}</span>
            {r.status !== 'open' && <span className="muted"> · {STATUS_TEXT[r.status]}</span>}
            <span className="muted">)</span>
          </li>
        ))}
      </ul>

      {isOpen && (
        <div className={styles.actions}>
          <Link
            to={`/admin/questions?${new URLSearchParams({ skill: q.skill_id, skill_name: q.skill,
              q: q.code || q.content.slice(0, 40) })}`}
            className="btn btn-sm btn-primary"
          >
            Sửa câu
          </Link>
          <button type="button" className="btn btn-sm" disabled={busy}
                  onClick={() => window.confirm('Giữ tắt câu này? Câu sẽ không vào đề nữa.') &&
                    onResolve(q.question_id, 'keep_disabled')}>
            Giữ tắt
          </button>
          <button type="button" className="btn btn-sm" disabled={busy}
                  onClick={() => window.confirm('Bác phản ánh? Câu được bật lại và coi như đã duyệt Đạt.') &&
                    onResolve(q.question_id, 'dismiss')}>
            Câu đúng — bác phản ánh
          </button>
        </div>
      )}
    </article>
  );
}

export default function AdminReviewReportsPage() {
  const [status, setStatus] = useState('open');
  const [reason, setReason] = useState('');
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setError('');
    try {
      const params = { status, page, size: PAGE_SIZE };
      if (reason) params.reason = reason;
      setData(await reviewAdminApi.listReports(params));
    } catch (err) {
      setError(parseApiError(err).message);
      setData({ items: [], total: 0, open_total: 0 });
    }
  }, [status, reason, page]);

  useEffect(() => {
    load();
  }, [load]);

  function choose(setter, value) {
    setter(value);
    setPage(1);
    setNotice('');
  }

  async function resolve(questionId, action) {
    setBusy(true);
    setNotice('');
    setError('');
    try {
      const r = await reviewAdminApi.resolveReports(questionId, action);
      setNotice(action === 'keep_disabled'
        ? `Đã giữ tắt câu #${questionId} và báo mentor.`
        : `Đã bác phản ánh câu #${questionId}${r.is_active ? ', câu đã bật lại' : ''} và báo mentor.`);
      await load();
    } catch (err) {
      setError(parseApiError(err).message);
    } finally {
      setBusy(false);
    }
  }

  const pages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;
  return (
    <div className={styles.page}>
      <header className={styles.head}>
        <div>
          <h1 className={styles.title}>Câu bị phản ánh</h1>
          <p className="muted small" style={{ margin: 0 }}>
            Mentor báo câu AI soạn bị lỗi. Câu bị phản ánh đã tắt ngay; bạn sửa, giữ tắt hoặc bác phản ánh.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Link to="/admin/review-mentors" className="btn btn-sm">
            Mentor ôn tập
          </Link>
          <Link to="/admin/questions" className="btn btn-sm">
            ← Câu hỏi ôn tập
          </Link>
        </div>
      </header>

      <div className={`card ${styles.filters}`}>
        <div className={styles.seg} role="radiogroup" aria-label="Trạng thái">
          {[
            ['open', `Chờ xử lý${data ? ` (${data.open_total})` : ''}`],
            ['handled', 'Đã xử lý'],
            ['all', 'Tất cả'],
          ].map(([value, text]) => (
            <button key={value} type="button" role="radio" aria-checked={status === value}
                    className={status === value ? styles.segOn : ''} onClick={() => choose(setStatus, value)}>
              {text}
            </button>
          ))}
        </div>
        <select className="select" aria-label="Lý do" value={reason} onChange={(e) => choose(setReason, e.target.value)}>
          <option value="">Lý do: tất cả</option>
          {Object.entries(REPORT_REASON_TEXT).map(([value, text]) => (
            <option key={value} value={value}>
              {text}
            </option>
          ))}
        </select>
      </div>

      {notice && <div className="alert alert-ok">{notice}</div>}
      {error && <div className="alert">{error}</div>}

      {data === null ? (
        <p className="muted">Đang tải…</p>
      ) : data.items.length === 0 ? (
        <div className={`card ${styles.empty}`}>{status === 'open' ? 'Không có phản ánh nào đang chờ. 🎉' : 'Chưa có phản ánh nào.'}</div>
      ) : (
        <>
          {data.items.map((item) => (
            <ReportCard key={item.question.question_id} item={item} onResolve={resolve} busy={busy} />
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
