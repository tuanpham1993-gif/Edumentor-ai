// Bắt đầu ôn tập (module 09 · Tuấn · GĐ4, 09/11/2026) — màn demo ReviewStart, route /courses/:courseId/review.
//   - Cấu trúc đề (chốt 09/11): 15 câu = 12 trắc nghiệm + 3 tự luận, đạt ≥ 6/10, làm lại không giới hạn.
//   - Có lượt đang làm dở → nút "Tiếp tục bài đang làm" (backend trả lại đúng lượt đó).
//   - Chưa thể ôn (chưa tham gia / đã bỏ khóa / chưa có đề) → hiện lý do, ẩn nút Bắt đầu.
import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import * as reviewApi from '../../../api/review.api.js';
import StatusPanel from '../../common/components/StatusPanel.jsx';
import { parseApiError } from '../../../utils/errors.js';
import { formatDateTime } from '../../../utils/formatters.js';
import { formatScore } from '../reviewFormat.js';
import styles from '../styles/ReviewStartPage.module.css';

function CheckIcon() {
  return (
    <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm-1.2 14.2-4-4 1.4-1.4 2.6 2.6 5.4-5.4 1.4 1.4-6.8 6.8Z" />
    </svg>
  );
}

export default function ReviewStartPage() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [info, setInfo] = useState(null);
  const [loadError, setLoadError] = useState(null); // { status, message }
  const [starting, setStarting] = useState(false);
  const [startError, setStartError] = useState('');

  const load = useCallback(async () => {
    setLoadError(null);
    try {
      setInfo(await reviewApi.getReviewInfo(courseId));
    } catch (error) {
      setLoadError(parseApiError(error));
    }
  }, [courseId]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleStart() {
    setStarting(true);
    setStartError('');
    try {
      const attempt = await reviewApi.startReview(courseId);
      navigate(`/review/${attempt.attempt_id}`, { state: { attempt } });
    } catch (error) {
      setStartError(parseApiError(error).message);
      setStarting(false);
    }
  }

  if (loadError) {
    return (
      <StatusPanel
        icon={loadError.status === 404 ? 'search' : 'server'}
        title={loadError.status === 404 ? 'Không tìm thấy khóa học' : 'Không tải được thông tin ôn tập'}
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

  if (!info) {
    return (
      <div className={styles.layout} aria-busy="true">
        <div className="skeleton" style={{ height: 420 }} />
        <div className="skeleton" style={{ height: 240 }} />
      </div>
    );
  }

  const { structure } = info;
  const graded = info.attempts.filter((a) => a.status !== 'in_progress');
  const resumable = Boolean(info.in_progress_attempt_id);

  return (
    <>
      <nav className="crumb" aria-label="Đường dẫn">
        <Link to="/me/review-history">Ôn tập</Link> / <span>{info.course_title}</span>
      </nav>

      <div className={styles.layout}>
        <section className={`card ${styles.main}`}>
          <span className={`chip ${info.can_start ? 'chip-info' : 'chip-danger'}`}>
            {info.can_start ? 'Có thể ôn tập' : 'Chưa thể ôn tập'}
          </span>
          <h1 className={styles.title}>Ôn tập: {info.course_title}</h1>
          <p className="muted">Kỹ năng khóa học dạy:</p>
          <ul className={styles.skills}>
            {info.skills.map((s) => (
              <li key={s.skill_id} className="chip">
                {s.skill}
              </li>
            ))}
          </ul>

          <div className={styles.stats}>
            <div className={styles.stat}>
              <strong>{structure.total_questions}</strong>
              <span>
                câu: {structure.recognize + structure.understand} trắc nghiệm + {structure.easy + structure.advanced} tự
                luận, chia theo kỹ năng
              </span>
            </div>
            <div className={styles.stat}>
              <strong>≥ {formatScore(info.pass_score)}/10</strong>
              <span>để đạt bài ôn tập</span>
            </div>
            <div className={styles.stat}>
              <strong>∞</strong>
              <span>làm lại không giới hạn — mỗi lần một đề mới</span>
            </div>
          </div>

          <ul className={styles.notes}>
            <li>
              <CheckIcon />
              <span>
                Đạt lần đầu: khóa học chuyển sang <b>Hoàn thành</b> và các kỹ năng trên được ghi nhận <b>Đã biết</b>.
              </span>
            </li>
            <li>
              <CheckIcon />
              <span>Trắc nghiệm 0,5 điểm/câu · tự luận dễ 1 điểm, nâng cao 2 điểm (chấm theo từng ý).</span>
            </li>
            <li>
              <CheckIcon />
              <span>Câu bỏ trống được 0 điểm, không trừ điểm câu sai. Kết quả được gửi qua email.</span>
            </li>
          </ul>

          {resumable && (
            <div className={styles.resume}>
              <span>Bạn có một bài đang làm dở — câu trả lời đã lưu vẫn còn.</span>
            </div>
          )}

          {startError && (
            <p className="alert" role="alert">
              {startError}
            </p>
          )}

          <div className={styles.actions}>
            {info.can_start && (
              <button type="button" className="btn btn-primary btn-lg" onClick={handleStart} disabled={starting}>
                {starting ? 'Đang tạo đề…' : resumable ? 'Tiếp tục bài đang làm →' : 'Bắt đầu ôn tập →'}
              </button>
            )}
            <Link to="/me/review-history" className="btn btn-lg">
              Lịch sử ôn tập
            </Link>
          </div>
        </section>

        <aside className={styles.side}>
          <section className={`card ${styles.panel}`}>
            <div className={styles.panelHead}>
              <h2>Các lần trước</h2>
              <Link to={`/me/review-history?course=${info.course_id}`} className="small">
                Lịch sử
              </Link>
            </div>
            {graded.length === 0 ? (
              <p className="muted small">Chưa có lần nào. Bài đầu tiên của bạn sẽ hiện ở đây.</p>
            ) : (
              <ul className={styles.attempts}>
                {graded.slice(0, 5).map((a) => (
                  <li key={a.attempt_id}>
                    <Link to={`/review/${a.attempt_id}/result`} className={styles.attempt}>
                      <span>{formatDateTime(a.submitted_at ?? a.started_at)}</span>
                      <span className={`chip ${a.passed ? 'chip-ok' : 'chip-danger'}`}>
                        {formatScore(a.score)}/10 · {a.passed ? 'Đạt' : 'Chưa đạt'}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {info.blocked && (
            <section className={`card ${styles.panel}`} role="status">
              <h2>Khi chưa thể ôn tập</h2>
              <div className={styles.blocked}>
                <strong>
                  {info.blocked.code === 'no_question_bank' ? 'Bài ôn tập chưa sẵn sàng' : 'Bạn chưa thể ôn khóa này'}
                </strong>
                <p className="muted small">{info.blocked.message}</p>
              </div>
            </section>
          )}
        </aside>
      </div>
    </>
  );
}
