// Một câu tự luận cần xem lại — admin xem bài làm, kết quả AI từng ý, rồi chọn Đạt / Không đạt (module 09 · Tuấn · 17/11/2026).
// Câu đã xem lại: chỉ đọc, hiện ai chấm lại, lúc nào, nhãn trước → sau, ghi chú.
import { useMemo, useState } from 'react';

import * as reviewAdminApi from '../../../api/reviewAdmin.api.js';
import { parseApiError } from '../../../utils/errors.js';
import { formatDateTime } from '../../../utils/formatters.js';
import styles from '../styles/AdminReviewFlags.module.css';

export const REASON_TEXT = {
  needs_review: 'AI lệch chấm từ khóa',
  near_pass: 'Điểm sát ngưỡng đạt',
  instruction_in_answer: 'Bài có câu ra lệnh cho AI',
  evidence_missing: 'AI không trích được bằng chứng',
  keyword_fallback: 'Chấm bằng từ khóa (AI lỗi)',
  ai_stricter: 'AI chấm chặt hơn từ khóa', // 20/11: có ý AI Không đạt mà chấm từ khóa Đạt
};
const LEVEL_TEXT = { easy: 'Tự luận dễ', advanced: 'Tự luận nâng cao' };
const RESULT = {
  full: { text: 'Đạt', chip: 'chip-ok' },
  none: { text: 'Không đạt', chip: 'chip-danger' },
  partial: { text: 'Một phần', chip: 'chip-info' }, // bài chấm trước 15/11
};

function fmt(n) {
  return Number(n).toLocaleString('vi-VN', { maximumFractionDigits: 2 });
}

export default function FlagCard({ item, onResolved, passScore = 6 }) {
  const aiLabels = useMemo(() => item.rubric.map((r) => (r.result === 'full' ? 'full' : 'none')), [item.rubric]);
  const [labels, setLabels] = useState(aiLabels);
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [confirming, setConfirming] = useState(false); // hộp xác nhận khi kết quả lượt sẽ đổi
  const done = Boolean(item.review);

  const changed = labels.some((l, i) => l !== aiLabels[i]);
  const newPoints =
    (item.rubric.reduce((sum, r, i) => sum + (labels[i] === 'full' ? r.max_points : 0), 0) / 10) * item.max_points;
  // Điểm lượt sau khi sửa (ước tính phía giao diện — backend tính lại chính xác) và kết quả có đổi không
  const newAttemptScore = Math.round(((item.attempt_score ?? 0) - item.points + newPoints) * 100) / 100;
  const newPassed = newAttemptScore >= passScore;
  const verdictChanges = changed && newPassed !== Boolean(item.attempt_passed);

  function requestSave() {
    if (verdictChanges) setConfirming(true);
    else save();
  }

  async function save() {
    setConfirming(false);
    setSaving(true);
    setError('');
    try {
      const result = await reviewAdminApi.resolveFlag(item.attempt_id, item.position, labels, note.trim());
      onResolved(result);
    } catch (err) {
      setError(parseApiError(err).message);
      setSaving(false);
    }
  }

  return (
    <article className={`card ${styles.card}`} aria-label={`Lượt ${item.attempt_id}, câu ${item.position}`}>
      <header className={styles.cardHead}>
        <div className={styles.who}>
          <b>{item.user_name || 'Học viên'}</b>
          <span className="small muted">
            {item.user_email} · {item.course_title} · nộp {formatDateTime(item.submitted_at)}
          </span>
        </div>
        <div className={styles.chips}>
          {item.reasons.map((r) => (
            <span key={r} className="chip chip-accent">
              {REASON_TEXT[r] || r}
            </span>
          ))}
          <span className={`chip ${item.attempt_passed ? 'chip-ok' : 'chip-danger'}`}>
            Lượt {item.attempt_id}: {fmt(item.attempt_score)}/10 · {item.attempt_passed ? 'Đạt' : 'Chưa đạt'}
          </span>
        </div>
      </header>

      <p className="small muted" style={{ margin: 0 }}>
        Câu {item.position} · {LEVEL_TEXT[item.level] || item.level} · {fmt(item.max_points)} điểm
        {item.question_code ? ` · ${item.question_code}` : ''}
      </p>
      <h3 className={styles.question}>{item.content}</h3>

      <div className={styles.answer}>
        <span className="small muted">Bài làm</span>
        <p>{item.text_answer}</p>
      </div>

      <div className={styles.tableWrap}>
        <table className="table">
          <thead>
            <tr>
              <th>Ý cần có</th>
              <th className="num">Điểm</th>
              <th>AI chấm · lý do · câu trích</th>
              <th>{done ? 'Giáo viên' : 'Giáo viên chấm'}</th>
            </tr>
          </thead>
          <tbody>
            {item.rubric.map((r, i) => {
              const ai = RESULT[done ? item.review.before[i] : r.result] || RESULT.none;
              return (
                <tr key={i}>
                  <td>
                    {i + 1}. {r.text}
                  </td>
                  <td className="num">{fmt(r.max_points)}</td>
                  <td>
                    <span className={`chip ${ai.chip}`}>{ai.text}</span>
                    {!done && r.reason && <div className="small">{r.reason}</div>}
                    {!done && r.evidence && <q className={`small ${styles.evidence}`}>{r.evidence}</q>}
                  </td>
                  <td>
                    {done ? (
                      <span className={`chip ${RESULT[item.review.after[i]].chip}`}>
                        {RESULT[item.review.after[i]].text}
                      </span>
                    ) : (
                      <div className={styles.seg} role="radiogroup" aria-label={`Ý ${i + 1}`}>
                        {['full', 'none'].map((value) => (
                          <button
                            key={value}
                            type="button"
                            role="radio"
                            aria-checked={labels[i] === value}
                            className={labels[i] === value ? styles.segOn : ''}
                            onClick={() => setLabels((ls) => ls.map((l, j) => (j === i ? value : l)))}
                          >
                            {RESULT[value].text}
                          </button>
                        ))}
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {item.feedback && (
        <p className="small" style={{ margin: 0 }}>
          <b>Nhận xét của AI:</b> {item.feedback}
        </p>
      )}
      {item.model_answer && (
        <details className="small">
          <summary>Đáp án mẫu</summary>
          <p style={{ margin: '6px 0 0' }}>{item.model_answer}</p>
        </details>
      )}

      {done ? (
        <footer className={styles.reviewed}>
          Đã xem lại bởi <b>{item.review.by_name || `admin #${item.review.by}`}</b> lúc{' '}
          {formatDateTime(item.review.at)} · điểm lượt {fmt(item.review.score_before)} → <b>{fmt(item.review.score_after)}</b>
          {item.review.note && <> · Ghi chú: “{item.review.note}”</>}
        </footer>
      ) : (
        <footer className={styles.actions}>
          <span className="small">
            Điểm câu: {fmt(item.points)} → <b>{fmt(newPoints)}</b> / {fmt(item.max_points)}
          </span>
          <input
            className="input"
            maxLength={500}
            placeholder="Ghi chú (không bắt buộc)"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            aria-label="Ghi chú chấm lại"
          />
          <button
            type="button"
            className="btn btn-primary btn-sm"
            disabled={saving || confirming}
            onClick={requestSave}
          >
            {changed ? 'Lưu chấm lại' : 'Xác nhận AI chấm đúng'}
          </button>
        </footer>
      )}
      {confirming && (
        <div className={styles.confirm} role="alertdialog" aria-label="Xác nhận đổi kết quả">
          <p>
            <b>
              Lượt {item.attempt_id} sẽ đổi từ {item.attempt_passed ? 'Đạt' : 'Chưa đạt'} sang{' '}
              {newPassed ? 'Đạt' : 'Chưa đạt'}
            </b>{' '}
            (điểm khoảng {fmt(item.attempt_score)} → {fmt(newAttemptScore)}/10).
          </p>
          {newPassed ? (
            <p className="small">
              Khóa học sẽ chuyển sang <b>Hoàn thành</b>, các kỹ năng của khóa thành <b>Đã biết</b>, và học viên nhận
              thông báo trên chuông + email kết quả.
            </p>
          ) : (
            <p className="small">
              Tiến độ học <b>không bị kéo lùi</b>: khóa học vẫn <b>Hoàn thành</b>, kỹ năng vẫn <b>Đã biết</b>, lộ trình
              không đổi. Chỉ điểm và kết quả của lượt này thay đổi; học viên thấy cập nhật trên chuông (không gửi email).
            </p>
          )}
          <div className={styles.confirmButtons}>
            <button type="button" className="btn btn-sm" onClick={() => setConfirming(false)}>
              Hủy
            </button>
            <button type="button" className="btn btn-primary btn-sm" onClick={save}>
              Xác nhận đổi kết quả
            </button>
          </div>
        </div>
      )}
      {error && <div className="alert">{error}</div>}
    </article>
  );
}
