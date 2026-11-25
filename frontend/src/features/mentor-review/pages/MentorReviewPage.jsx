// Duyệt câu hỏi — /mentor/review (module 09 · Tuấn · G3f, 25/11/2026 — docs/Review-AI-Tu-Soan-On-Tap.md D19–D23).
// Mentor xem câu AI soạn (đã dùng ngay cho học viên — D1): câu hỏi, đáp án, giải thích / barem, đoạn tài liệu AI dựa vào.
//   Đạt           → câu được đánh dấu "Mentor đã duyệt"
//   Phản ánh lỗi  → câu TẮT NGAY, chuyển admin xác nhận (D20); admin xử lý xong → chuông báo mentor
// Mentor KHÔNG sửa / xóa / bật tắt câu (D23). Chỉ câu AI soạn (D21). Admin vào được để kiểm tra.
import { useCallback, useEffect, useState } from 'react';

import * as mentorApi from '../../../api/mentorReview.api.js';
import { parseApiError } from '../../../utils/errors.js';
import { formatDateTime } from '../../../utils/formatters.js';
import { LEVEL_TEXT } from '../../review/reviewFormat.js';
import styles from '../../review-admin/styles/AdminReviewFlags.module.css';

const PAGE_SIZE = 10;
const LETTERS = ['A', 'B', 'C', 'D'];
export const REASONS = [
  ['wrong_answer', 'Đáp án đúng bị sai'],
  ['ambiguous', 'Câu mơ hồ / có 2 đáp án đúng'],
  ['wrong_knowledge', 'Sai kiến thức'],
  ['bad_rubric', 'Barem tự luận không hợp lý', 'essay'],
  ['other', 'Khác (ghi rõ)'],
];
const REASON_TEXT = Object.fromEntries(REASONS.map(([value, text]) => [value, text]));
const TABS = [
  ['pending', 'Chờ duyệt'],
  ['passed', 'Đã Đạt'],
  ['reported', 'Đã phản ánh'],
];

function ReportForm({ question, busy, onSend, onCancel }) {
  const [reason, setReason] = useState('');
  const [note, setNote] = useState('');
  const choices = REASONS.filter(([, , only]) => !only || only === question.type);
  const needNote = reason === 'other' && !note.trim();
  return (
    <div className="card" style={{ padding: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
      <strong className="small">Câu này lỗi gì? (câu sẽ tắt ngay, chờ admin xác nhận)</strong>
      <div role="radiogroup" aria-label="Lý do" style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 16px' }}>
        {choices.map(([value, text]) => (
          <label key={value} className="small" style={{ display: 'inline-flex', gap: 6, alignItems: 'center' }}>
            <input type="radio" name={`reason-${question.question_id}`} value={value} checked={reason === value}
                   onChange={() => setReason(value)} />
            {text}
          </label>
        ))}
      </div>
      <textarea className="input" rows={2} maxLength={500} value={note} onChange={(e) => setNote(e.target.value)}
                placeholder={reason === 'other' ? 'Ghi chú (bắt buộc)' : 'Ghi chú cho admin, ví dụ đáp án đúng là gì'} />
      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
        <button type="button" className="btn btn-sm" onClick={onCancel} disabled={busy}>
          Hủy
        </button>
        <button type="button" className="btn btn-sm btn-danger" disabled={!reason || needNote || busy}
                onClick={() => onSend(reason, note.trim())}>
          Gửi phản ánh
        </button>
      </div>
    </div>
  );
}

function QuestionCard({ item, tab, onPass, onReport, busy }) {
  const [showChunk, setShowChunk] = useState(false);
  const [reporting, setReporting] = useState(false);
  return (
    <article className={`card ${styles.card}`}>
      <div className={styles.cardHead}>
        <div className={styles.who}>
          <strong>
            {item.skill} · {item.type === 'mcq' ? 'Trắc nghiệm' : 'Tự luận'} · {LEVEL_TEXT[item.level] || item.level}
          </strong>
          <span className="small muted">Câu #{item.question_id}{item.code ? ` (${item.code})` : ''} · AI soạn</span>
        </div>
        <div className={styles.chips}>
          {tab === 'passed' && <span className="chip chip-ok">Đạt</span>}
          {tab === 'reported' && <span className="chip chip-danger">{item.is_active ? 'Đã phản ánh' : 'Đang tắt · chờ admin'}</span>}
        </div>
      </div>

      <p className={styles.question}>{item.content}</p>
      {item.type === 'mcq' ? (
        <ul className="small" style={{ margin: 0, paddingLeft: 18 }}>
          {(item.options || []).map((opt, i) => (
            <li key={LETTERS[i]} style={i === item.correct_index ? { fontWeight: 700 } : undefined}>
              {LETTERS[i]}. {opt} {i === item.correct_index && <span className="chip chip-ok">đáp án</span>}
            </li>
          ))}
        </ul>
      ) : (
        <div className="small">
          <b>Barem chấm:</b>
          <ul style={{ margin: '4px 0 0', paddingLeft: 18 }}>
            {(item.rubric || []).map((r, i) => (
              <li key={i}>
                {r.text} <span className="muted">({r.max_points} điểm · từ khóa: {(r.main_keywords || []).join(', ')})</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      {item.explanation && (
        <p className="small" style={{ margin: 0 }}>
          <b>Giải thích:</b> {item.explanation}
        </p>
      )}

      {item.chunk ? (
        <div className="small">
          <button type="button" className="btn btn-sm" aria-expanded={showChunk} onClick={() => setShowChunk(!showChunk)}>
            {showChunk ? 'Ẩn đoạn tài liệu' : 'Xem đoạn tài liệu AI dựa vào'}
          </button>
          {showChunk && (
            <blockquote className={styles.evidence} style={{ marginTop: 8, whiteSpace: 'pre-wrap' }}>
              {item.chunk.title && <b>{item.chunk.title}. </b>}
              {item.chunk.content}
            </blockquote>
          )}
        </div>
      ) : (
        <p className="small muted" style={{ margin: 0 }}>Câu không gắn đoạn tài liệu.</p>
      )}

      {item.report && (
        <p className="small" style={{ margin: 0 }}>
          <b>Phản ánh:</b> {REASON_TEXT[item.report.reason]}
          {item.report.note ? ` — "${item.report.note}"` : ''}
        </p>
      )}
      {item.mentor_name && tab !== 'pending' && (
        <p className="small muted" style={{ margin: 0 }}>
          {item.mentor_name} · {formatDateTime(item.mentor_at)}
        </p>
      )}

      {tab !== 'reported' && !reporting && (
        <div className={styles.actions}>
          {tab === 'pending' && (
            <button type="button" className="btn btn-sm btn-primary" disabled={busy} onClick={() => onPass(item.question_id)}>
              ✓ Đạt
            </button>
          )}
          <button type="button" className="btn btn-sm" disabled={busy} onClick={() => setReporting(true)}>
            ⚑ Phản ánh lỗi
          </button>
        </div>
      )}
      {reporting && (
        <ReportForm question={item} busy={busy} onCancel={() => setReporting(false)}
                    onSend={(reason, note) => onReport(item.question_id, reason, note)} />
      )}
    </article>
  );
}

export default function MentorReviewPage() {
  const [tab, setTab] = useState('pending');
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setError('');
    try {
      setData(await mentorApi.listQueue({ status: tab, page, size: PAGE_SIZE }));
    } catch (err) {
      setError(parseApiError(err).message);
      setData({ items: [], total: 0, counts: null });
    }
  }, [tab, page]);

  useEffect(() => {
    load();
  }, [load]);

  function chooseTab(value) {
    setTab(value);
    setPage(1);
    setNotice('');
  }

  async function act(fn, message) {
    setBusy(true);
    setError('');
    setNotice('');
    try {
      await fn();
      setNotice(message);
      await load();
    } catch (err) {
      setError(parseApiError(err).message);
    } finally {
      setBusy(false);
    }
  }

  const counts = data?.counts;
  const pages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;
  return (
    <div className={styles.page}>
      <header className={styles.head}>
        <div>
          <h1 className={styles.title}>Duyệt câu hỏi ôn tập</h1>
          <p className="muted small" style={{ margin: 0 }}>
            Câu do AI soạn, học viên đang dùng. Bấm <b>Đạt</b> nếu câu đúng; <b>Phản ánh lỗi</b> nếu sai — câu tắt ngay và
            chuyển admin xác nhận.
          </p>
        </div>
      </header>

      <div className={`card ${styles.filters}`}>
        <div className={styles.seg} role="radiogroup" aria-label="Trạng thái">
          {TABS.map(([value, text]) => (
            <button key={value} type="button" role="radio" aria-checked={tab === value}
                    className={tab === value ? styles.segOn : ''}
                    onClick={() => chooseTab(value)}>
              {text}{counts ? ` (${counts[value]})` : ''}
            </button>
          ))}
        </div>
      </div>

      {notice && <div className="alert alert-ok">{notice}</div>}
      {error && <div className="alert">{error}</div>}

      {data === null ? (
        <p className="muted">Đang tải…</p>
      ) : data.items.length === 0 ? (
        <div className={`card ${styles.empty}`}>
          {tab === 'pending' ? 'Không còn câu nào chờ duyệt. 🎉' : 'Chưa có câu nào.'}
        </div>
      ) : (
        <>
          {data.items.map((item) => (
            <QuestionCard key={item.question_id} item={item} tab={tab} busy={busy}
                          onPass={(id) => act(() => mentorApi.passQuestion(id), `Đã duyệt Đạt câu #${id}.`)}
                          onReport={(id, reason, note) => act(() => mentorApi.reportQuestion(id, reason, note),
                            `Đã phản ánh câu #${id}: câu đã tắt, chờ admin xác nhận.`)} />
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
