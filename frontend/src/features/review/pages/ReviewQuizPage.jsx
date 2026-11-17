// Làm bài ôn tập (module 09 · Tuấn · GĐ4, 09/11/2026) — màn demo ReviewQuiz, route /review/:attemptId.
//   - 12 trắc nghiệm (4 lựa chọn đã xáo) + 3 tự luận; bảng số câu bên phải (đã trả lời / chưa / đang xem).
//   - TỰ LƯU (FR-29): trắc nghiệm lưu ngay khi chọn; tự luận lưu sau 1 giây ngừng gõ; đổi câu / Tạm rời /
//     Nộp bài → lưu nốt phần đang chờ. Lưu lỗi → giữ lại, thử lại ở lần lưu sau (có nút "Lưu lại").
//   - "Tạm rời, làm tiếp sau" → lưu rồi về trang Bắt đầu ôn tập (ở đó có nút "Tiếp tục bài đang làm").
//   - Nộp bài → hộp xác nhận (báo số câu còn bỏ trống) → chấm → trang Kết quả.
import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';

import * as reviewApi from '../../../api/review.api.js';
import StatusPanel from '../../common/components/StatusPanel.jsx';
import { parseApiError } from '../../../utils/errors.js';
import { LEVEL_TEXT, OPTION_LETTERS, formatScore, isAnswered } from '../reviewFormat.js';
import styles from '../styles/ReviewQuizPage.module.css';

const ESSAY_SAVE_DELAY = 1000; // ms ngừng gõ thì lưu
const MAX_ESSAY_CHARS = 5000; // khớp backend (schemas/review.py)

const SAVE_TEXT = {
  idle: '',
  saving: 'Đang lưu…',
  saved: 'Đã lưu',
  error: 'Chưa lưu được — sẽ thử lại',
};

export default function ReviewQuizPage() {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [attempt, setAttempt] = useState(() => {
    const fromStart = location.state?.attempt;
    return fromStart && String(fromStart.attempt_id) === attemptId ? fromStart : null;
  });
  const [loadError, setLoadError] = useState(null);
  const [index, setIndex] = useState(0);
  const [saveState, setSaveState] = useState('idle');
  const [confirming, setConfirming] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const pending = useRef(new Map()); // position → payload chưa lưu
  const timer = useRef(null);
  const saving = useRef(null); // Promise của lần lưu đang chạy

  // ---------- Tải đề ----------
  const load = useCallback(async () => {
    setLoadError(null);
    try {
      setAttempt(await reviewApi.getAttempt(attemptId));
    } catch (error) {
      setLoadError(parseApiError(error));
    }
  }, [attemptId]);

  useEffect(() => {
    if (!attempt) load();
  }, [attempt, load]);

  // Bài đã nộp (vd mở lại link cũ) → sang trang kết quả
  useEffect(() => {
    if (attempt && attempt.status !== 'in_progress') {
      navigate(`/review/${attemptId}/result`, { replace: true });
    }
  }, [attempt, attemptId, navigate]);

  // ---------- Lưu ----------
  const flush = useCallback(async () => {
    clearTimeout(timer.current);
    if (saving.current) await saving.current; // chờ lần lưu trước xong (giữ thứ tự)
    if (pending.current.size === 0) return true;

    const batch = new Map(pending.current);
    pending.current.clear();
    setSaveState('saving');
    const request = reviewApi
      .saveAnswers(attemptId, [...batch.values()])
      .then(() => {
        setSaveState(pending.current.size ? 'idle' : 'saved');
        return true;
      })
      .catch((error) => {
        if (parseApiError(error).status === 409) {
          navigate(`/review/${attemptId}/result`, { replace: true }); // đã nộp ở tab khác
          return false;
        }
        // Trả lại phần chưa lưu (trừ câu đã có bản mới hơn) để lần sau gửi lại
        for (const [position, payload] of batch) {
          if (!pending.current.has(position)) pending.current.set(position, payload);
        }
        setSaveState('error');
        return false;
      })
      .finally(() => {
        saving.current = null;
      });
    saving.current = request;
    return request;
  }, [attemptId, navigate]);

  // Đóng tab / tải lại khi còn câu chưa lưu → trình duyệt hỏi lại
  useEffect(() => {
    function warn(event) {
      if (pending.current.size || saving.current) {
        event.preventDefault();
        event.returnValue = '';
      }
    }
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, []);

  useEffect(() => () => clearTimeout(timer.current), []);

  function updateQuestion(position, changes, payload, { immediate }) {
    setAttempt((current) => ({
      ...current,
      questions: current.questions.map((q) => (q.position === position ? { ...q, ...changes } : q)),
    }));
    pending.current.set(position, payload);
    setSaveState('idle');
    clearTimeout(timer.current);
    if (immediate) flush();
    else timer.current = setTimeout(flush, ESSAY_SAVE_DELAY);
  }

  function choose(question, selected) {
    updateQuestion(
      question.position,
      { selected_index: selected },
      { position: question.position, selected_index: selected },
      { immediate: true },
    );
  }

  function write(question, text) {
    updateQuestion(
      question.position,
      { text_answer: text },
      { position: question.position, text_answer: text },
      { immediate: false },
    );
  }

  function goTo(nextIndex) {
    flush();
    setIndex(nextIndex);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function leave() {
    await flush();
    navigate(`/courses/${attempt.course_id}/review`);
  }

  async function submit() {
    setSubmitting(true);
    setSubmitError('');
    const ok = await flush();
    if (!ok && pending.current.size) {
      setSubmitError('Chưa lưu được câu trả lời. Kiểm tra kết nối rồi bấm Nộp bài lại.');
      setSubmitting(false);
      return;
    }
    try {
      const result = await reviewApi.submitAttempt(attemptId);
      navigate(`/review/${attemptId}/result`, { replace: true, state: { result } });
    } catch (error) {
      const { status, message } = parseApiError(error);
      if (status === 409) {
        navigate(`/review/${attemptId}/result`, { replace: true });
        return;
      }
      setSubmitError(message);
      setSubmitting(false);
    }
  }

  // ---------- Giao diện ----------
  if (loadError) {
    return (
      <StatusPanel
        icon={loadError.status === 404 ? 'search' : 'server'}
        title={loadError.status === 404 ? 'Không tìm thấy bài ôn tập' : 'Không tải được bài ôn tập'}
        actions={
          <>
            {loadError.status !== 404 && (
              <button type="button" className="btn btn-primary" onClick={load}>
                Thử lại
              </button>
            )}
            <Link to="/me/review-history" className="btn">
              Lịch sử ôn tập
            </Link>
          </>
        }
      >
        {loadError.message}
      </StatusPanel>
    );
  }

  if (!attempt || attempt.status !== 'in_progress') {
    return <div className="skeleton" style={{ height: 480 }} aria-busy="true" />;
  }

  const questions = attempt.questions;
  const question = questions[index];
  const answered = questions.filter(isAnswered).length;
  const blank = questions.length - answered;
  const progress = Math.round(((index + 1) / questions.length) * 100);

  return (
    <>
      <div className={styles.topbar}>
        <p className={styles.course}>
          Ôn tập · <b>{attempt.course_title}</b>
        </p>
        <div className={styles.topActions}>
          <span className={`small ${styles.save} ${styles[saveState] ?? ''}`} role="status" aria-live="polite">
            {SAVE_TEXT[saveState]}
            {saveState === 'error' && (
              <button type="button" className={styles.retry} onClick={flush}>
                Lưu lại
              </button>
            )}
          </span>
          <button type="button" className="btn btn-sm" onClick={leave}>
            Tạm rời, làm tiếp sau
          </button>
        </div>
      </div>

      <div className={styles.layout}>
        <section className={styles.main}>
          <div className={styles.meta}>
            <span>
              Kỹ năng: <b>{question.skill}</b>
            </span>
            <span>
              Câu <b>{question.position}</b> / {questions.length}
            </span>
          </div>
          <div className={styles.track} aria-hidden="true">
            <span style={{ width: `${progress}%` }} />
          </div>

          <article key={question.position} className={`card enter ${styles.card}`}>
            <p className={styles.level}>
              {LEVEL_TEXT[question.level]} · {formatScore(question.max_points)} điểm
            </p>
            <h1 className={styles.question}>
              Câu {question.position}: <span className={styles.content}>{question.content}</span>
            </h1>

            {question.type === 'mcq' ? (
              <div className={styles.options} role="radiogroup" aria-label={`Lựa chọn câu ${question.position}`}>
                {question.options.map((option, i) => {
                  const selected = question.selected_index === i;
                  return (
                    <button
                      key={OPTION_LETTERS[i]}
                      type="button"
                      role="radio"
                      aria-checked={selected}
                      className={`${styles.option} ${selected ? styles.selected : ''}`}
                      onClick={() => choose(question, selected ? null : i)}
                    >
                      <span className={styles.radio} aria-hidden="true" />
                      <span className={styles.letter}>{OPTION_LETTERS[i]}.</span>
                      <span className={styles.optionText}>{option}</span>
                    </button>
                  );
                })}
                <p className="muted small">Bấm lại lựa chọn đang chọn để bỏ chọn.</p>
              </div>
            ) : (
              <div className={styles.essay}>
                <label htmlFor={`essay-${question.position}`} className="muted small">
                  Bài làm của bạn — viết thành câu đầy đủ, nêu đủ các ý (chấm theo từng ý).
                </label>
                <textarea
                  id={`essay-${question.position}`}
                  className={styles.textarea}
                  rows={9}
                  maxLength={MAX_ESSAY_CHARS}
                  value={question.text_answer ?? ''}
                  onChange={(event) => write(question, event.target.value)}
                  onBlur={flush}
                  placeholder="Nhập câu trả lời…"
                />
                <span className={`small muted ${styles.counter}`}>
                  {(question.text_answer ?? '').length}/{MAX_ESSAY_CHARS}
                </span>
              </div>
            )}
          </article>

          <div className={styles.stepper}>
            <button type="button" className="btn" disabled={index === 0} onClick={() => goTo(index - 1)}>
              ← Câu trước
            </button>
            {index < questions.length - 1 ? (
              <button type="button" className="btn btn-primary" onClick={() => goTo(index + 1)}>
                Câu tiếp →
              </button>
            ) : (
              <button type="button" className="btn btn-primary" onClick={() => setConfirming(true)}>
                Nộp bài
              </button>
            )}
          </div>
        </section>

        <aside className={`card ${styles.nav}`} aria-label="Danh sách câu hỏi">
          <div className={styles.navHead}>
            <h2>Danh sách câu hỏi</h2>
            <span className="muted small">
              Đã trả lời {answered}/{questions.length}
            </span>
          </div>
          <ol className={styles.grid}>
            {questions.map((q, i) => (
              <li key={q.position}>
                <button
                  type="button"
                  className={`${styles.cell} ${isAnswered(q) ? styles.done : ''} ${i === index ? styles.current : ''}`}
                  aria-current={i === index ? 'step' : undefined}
                  aria-label={`Câu ${q.position}${isAnswered(q) ? ', đã trả lời' : ', chưa trả lời'}${
                    q.type === 'essay' ? ', tự luận' : ''
                  }`}
                  onClick={() => goTo(i)}
                >
                  {q.position}
                  {q.type === 'essay' && <span className={styles.essayDot} aria-hidden="true" />}
                </button>
              </li>
            ))}
          </ol>
          <ul className={styles.legend} aria-hidden="true">
            <li>
              <span className={`${styles.swatch} ${styles.done}`} /> Đã trả lời
            </li>
            <li>
              <span className={styles.swatch} /> Chưa trả lời
            </li>
            <li>
              <span className={`${styles.swatch} ${styles.current}`} /> Đang xem
            </li>
          </ul>
          <p className={styles.hint}>
            {blank > 0
              ? `Còn ${blank} câu chưa trả lời. Câu bỏ trống được 0 điểm.`
              : 'Bạn đã trả lời tất cả các câu.'}
          </p>
          <button type="button" className="btn btn-primary btn-block" onClick={() => setConfirming(true)}>
            Nộp bài
          </button>
        </aside>
      </div>

      {confirming && (
        <div className={styles.scrim} role="presentation" onClick={() => !submitting && setConfirming(false)}>
          <div
            className={`card ${styles.dialog}`}
            role="dialog"
            aria-modal="true"
            aria-labelledby="submit-title"
            onClick={(event) => event.stopPropagation()}
          >
            <h2 id="submit-title">Nộp bài ôn tập?</h2>
            <p className="muted">
              {blank > 0
                ? `Bạn còn ${blank} câu chưa trả lời — các câu này được 0 điểm.`
                : 'Bạn đã trả lời đủ 15 câu.'}{' '}
              Sau khi nộp không sửa được nữa.
            </p>
            {submitting && (
              <p className="small muted" role="status">
                AI đang chấm phần tự luận — thường vài giây, tối đa khoảng 20 giây. Đừng đóng trang.
              </p>
            )}
            {submitError && (
              <p className="alert" role="alert">
                {submitError}
              </p>
            )}
            <div className={styles.dialogActions}>
              <button type="button" className="btn" onClick={() => setConfirming(false)} disabled={submitting}>
                Làm tiếp
              </button>
              <button type="button" className="btn btn-primary" onClick={submit} disabled={submitting} autoFocus>
                {submitting ? 'Đang chấm…' : 'Nộp bài'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
