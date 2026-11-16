// Một dòng bảng câu hỏi + phần mở rộng (đáp án / barem, lịch sử phiên bản, khung duyệt câu AI) — module 09 (Tuấn · 16/11/2026 · 7.6).
import { useState } from 'react';

import * as reviewAdminApi from '../../../api/reviewAdmin.api.js';
import { parseApiError } from '../../../utils/errors.js';
import { formatDateTime } from '../../../utils/formatters.js';
import { LEVEL_TEXT } from '../../review/reviewFormat.js';
import { SOURCE_TEXT, questionStatus } from '../reviewAdminFormat.js';
import styles from '../styles/AdminReviewQuestions.module.css';
import QuestionDetail from './QuestionDetail.jsx';

const COLUMNS = 7;

function ApproveBox({ questionId, suggested, onChanged }) {
  const [code, setCode] = useState(suggested || '');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function act(kind) {
    if (kind === 'reject' && !window.confirm('Từ chối câu này? Câu sẽ không được đưa vào đề ôn tập.')) return;
    setBusy(true);
    setError('');
    try {
      const result =
        kind === 'approve'
          ? await reviewAdminApi.approveQuestion(questionId, code.trim())
          : await reviewAdminApi.rejectQuestion(questionId);
      onChanged(
        result,
        kind === 'approve'
          ? `Đã duyệt câu → mã ${result.code || '(tự cấp)'}, câu đã bật và có thể vào đề ôn tập.`
          : 'Đã từ chối câu. Câu không được đưa vào đề ôn tập.',
      );
    } catch (err) {
      setError(parseApiError(err).message);
      setBusy(false);
    }
  }

  return (
    <div className={styles.actions}>
      <label className={styles.codeField}>
        <span className="small muted">Mã câu (không bắt buộc — để trống hệ thống tự cấp)</span>
        <span className="input">
          <input value={code} onChange={(e) => setCode(e.target.value)} maxLength={50} placeholder="vd VAR-TN-15" />
        </span>
      </label>
      <div className={styles.buttons}>
        <button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={() => act('approve')}>
          Duyệt và bật
        </button>
        <button type="button" className="btn btn-danger btn-sm" disabled={busy} onClick={() => act('reject')}>
          Từ chối
        </button>
      </div>
      {error && <div className={`alert ${styles.full}`}>{error}</div>}
    </div>
  );
}

function Versions({ versions }) {
  if (!versions || versions.length < 2) return null;
  return (
    <div className={styles.versions}>
      <span className="small muted">Lịch sử phiên bản</span>
      {versions.map((v) => (
        <div key={v.question_id} className="small">
          <b>v{v.version}</b> · {v.is_active ? 'đang dùng' : 'đã tắt'} · {formatDateTime(v.created_at)} · {v.used_count}{' '}
          bài làm{v.change_note ? ` · ${v.change_note}` : ''}
        </div>
      ))}
    </div>
  );
}

export default function QuestionRow({ item, onChanged }) {
  const [open, setOpen] = useState(false);
  const [detail, setDetail] = useState(null);
  const [suggested, setSuggested] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const status = questionStatus(item);
  const canToggle = item.review_status === 'approved';

  async function toggleOpen() {
    const next = !open;
    setOpen(next);
    if (next && !detail) {
      setError('');
      try {
        const [d, code] = await Promise.all([
          reviewAdminApi.getQuestion(item.question_id),
          item.review_status === 'pending' ? reviewAdminApi.getSuggestedCode(item.question_id) : null,
        ]);
        setDetail(d);
        setSuggested(code);
      } catch (err) {
        setError(parseApiError(err).message);
      }
    }
  }

  async function toggleActive() {
    setBusy(true);
    setError('');
    try {
      const updated = await reviewAdminApi.setQuestionActive(item.question_id, !item.is_active);
      setDetail(updated);
      onChanged(updated);
    } catch (err) {
      setError(parseApiError(err).message);
    } finally {
      setBusy(false);
    }
  }

  function handleReviewed(updated, message) {
    setDetail(updated);
    onChanged(updated, message);
  }

  return (
    <>
      <tr className={open ? styles.rowOpen : ''}>
        <td className={styles.code}>{item.code || <span className="muted">—</span>}</td>
        <td className={styles.contentCell}>
          <button type="button" className={styles.rowBtn} aria-expanded={open} onClick={toggleOpen}>
            <span className={styles.clamp}>{item.content}</span>
          </button>
          <span className="small muted">{item.skill_name || `Kỹ năng ${item.skill_id}`}</span>
        </td>
        <td className="small">{LEVEL_TEXT[item.level] || item.level}</td>
        <td>
          <span className={styles.chips}>
            <span className={`chip ${item.source === 'ai' ? 'chip-info' : ''}`}>
              {SOURCE_TEXT[item.source] || item.source}
            </span>
            {status.key !== 'active' && status.key !== 'disabled' && (
              <span className={`chip ${status.chip}`}>{status.text}</span>
            )}
          </span>
        </td>
        <td className={styles.num}>v{item.version}</td>
        <td className={styles.num}>{item.used_count}</td>
        <td className={styles.num}>
          <button
            type="button"
            role="switch"
            aria-checked={item.is_active}
            aria-label={item.is_active ? 'Tắt câu này' : 'Bật câu này'}
            title={canToggle ? (item.is_active ? 'Đang bật — bấm để tắt' : 'Đã tắt — bấm để bật') : 'Duyệt câu trước khi bật'}
            className={`${styles.switch} ${item.is_active ? styles.switchOn : ''}`}
            disabled={!canToggle || busy}
            onClick={toggleActive}
          >
            <span />
          </button>
        </td>
      </tr>
      {(open || error) && (
        <tr className={styles.detailRow}>
          <td colSpan={COLUMNS}>
            {error && <div className="alert">{error}</div>}
            {open && !detail && !error && <p className="muted small">Đang tải…</p>}
            {open && detail && (
              <div className={styles.detailBox}>
                <p className={styles.content}>{detail.content}</p>
                <QuestionDetail detail={detail} />
                <Versions versions={detail.versions} />
                {detail.review_status === 'pending' && (
                  <ApproveBox questionId={detail.question_id} suggested={suggested} onChanged={handleReviewed} />
                )}
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  );
}
