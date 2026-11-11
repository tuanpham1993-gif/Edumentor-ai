// Kết quả ôn tập (module 09 · Tuấn · GĐ4, 09/11/2026) — màn demo ReviewResult + ReviewDetail, route
// /review/:attemptId/result.
//   - Vòng điểm (thang 10), Đạt / Chưa đạt (ngưỡng từ backend), điểm trắc nghiệm / tự luận.
//   - Đạt lần đầu: báo khóa Hoàn thành + kỹ năng "Đã biết" (B1). Kết quả cũng được gửi email.
//   - Chi tiết từng câu (lọc "Câu sai / bỏ trống", ẩn / hiện tất cả giải thích).
// Vừa nộp xong: trang nhận kết quả qua state (khỏi gọi API lại); mở từ Lịch sử: gọi GET /me/review-history/{id}.
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';

import * as reviewApi from '../../../api/review.api.js';
import StatusPanel from '../../common/components/StatusPanel.jsx';
import Tabs from '../../common/components/Tabs.jsx';
import { parseApiError } from '../../../utils/errors.js';
import { formatDateTime } from '../../../utils/formatters.js';
import ResultQuestion from '../components/ResultQuestion.jsx';
import { formatScore } from '../reviewFormat.js';
import styles from '../styles/ReviewResultPage.module.css';

function isMiss(q) {
  return q.type === 'mcq' ? !q.is_correct : q.points < q.max_points;
}

function ScoreRing({ score, passed }) {
  const ratio = Math.max(0, Math.min(1, (score ?? 0) / 10));
  return (
    <div
      className={`${styles.ring} ${passed ? styles.ringPass : styles.ringFail}`}
      style={{ '--ratio': ratio }}
      role="img"
      aria-label={`Điểm ${formatScore(score)} trên 10`}
    >
      <div className={styles.ringInner}>
        <strong>{formatScore(score)}</strong>
        <span>/ 10 điểm</span>
      </div>
    </div>
  );
}

export default function ReviewResultPage() {
  const { attemptId } = useParams();
  const location = useLocation();
  const [result, setResult] = useState(() => {
    const fromSubmit = location.state?.result;
    return fromSubmit && String(fromSubmit.attempt_id) === attemptId ? fromSubmit : null;
  });
  const justSubmitted = Boolean(location.state?.result);
  const [loadError, setLoadError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [open, setOpen] = useState(() => new Set());

  const load = useCallback(async () => {
    setLoadError(null);
    try {
      setResult(await reviewApi.getResult(attemptId));
    } catch (error) {
      setLoadError(parseApiError(error));
    }
  }, [attemptId]);

  useEffect(() => {
    if (!result) load();
  }, [result, load]);

  const skills = useMemo(
    () => (result ? [...new Map(result.questions.map((q) => [q.skill_id, q.skill])).values()] : []),
    [result],
  );

  if (loadError) {
    return (
      <StatusPanel
        icon={loadError.status === 404 ? 'search' : 'server'}
        title={loadError.status === 404 ? 'Chưa có kết quả cho bài này' : 'Không tải được kết quả'}
        actions={
          <>
            {loadError.status === 404 ? (
              <Link to={`/review/${attemptId}`} className="btn btn-primary">
                Mở bài đang làm
              </Link>
            ) : (
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
        {loadError.status === 404
          ? 'Bài chưa được nộp hoặc không thuộc tài khoản của bạn.'
          : loadError.message}
      </StatusPanel>
    );
  }

  if (!result) {
    return <div className="skeleton" style={{ height: 420 }} aria-busy="true" />;
  }

  const mcq = result.questions.filter((q) => q.type === 'mcq');
  const mcqCorrect = mcq.filter((q) => q.is_correct).length;
  const misses = result.questions.filter(isMiss);
  const shown = filter === 'miss' ? misses : result.questions;
  const allOpen = shown.every((q) => open.has(q.position));

  function toggle(position) {
    setOpen((current) => {
      const next = new Set(current);
      if (next.has(position)) next.delete(position);
      else next.add(position);
      return next;
    });
  }

  function toggleAll() {
    setOpen(allOpen ? new Set() : new Set(shown.map((q) => q.position)));
  }

  return (
    <>
      <section className={`card ${styles.summary}`}>
        <p className="muted">Kết quả ôn tập · {result.course_title}</p>
        <ScoreRing score={result.score} passed={result.passed} />
        <span className={`chip ${result.passed ? 'chip-ok' : 'chip-danger'} ${styles.verdict}`}>
          {result.passed ? 'Đạt' : 'Chưa đạt'} (điểm đạt từ {formatScore(result.pass_score)}/10)
        </span>
        <p className="muted small">
          Nộp lúc {formatDateTime(result.submitted_at)} · Trắc nghiệm {mcqCorrect}/{mcq.length} câu đúng (
          {formatScore(result.mcq_score)}đ) · Tự luận {formatScore(result.essay_score)}đ
        </p>

        <ul className={styles.facts}>
          {result.completed_course && (
            <>
              <li>
                <span>
                  ✔ Khóa học đã chuyển sang <b className={styles.accent}>Hoàn thành</b>.
                </span>
              </li>
              <li>
                <span>
                  ✔ Kỹ năng được ghi nhận <b>Đã biết</b>:
                </span>
                {skills.map((s) => (
                  <span key={s} className="chip chip-accent">
                    {s}
                  </span>
                ))}
              </li>
            </>
          )}
          {result.passed && !result.completed_course && (
            <li>Bạn đã đạt khóa này trước đó — lần này được lưu vào lịch sử.</li>
          )}
          {!result.passed && <li>Bạn có thể ôn lại bất cứ lúc nào — mỗi lần là một đề mới.</li>}
          {justSubmitted && <li>✉ Kết quả cũng được gửi tới email của bạn.</li>}
        </ul>

        <div className={styles.actions}>
          <a href="#chi-tiet" className="btn btn-primary">
            Xem chi tiết đáp án ↓
          </a>
          <Link to={`/courses/${result.course_id}/review`} className="btn">
            Làm lại
          </Link>
          <Link to="/me/review-history" className="btn">
            Lịch sử ôn tập
          </Link>
        </div>
      </section>

      <section id="chi-tiet" className={styles.detail}>
        <div className={styles.detailHead}>
          <Tabs
            label="Lọc câu hỏi"
            value={filter}
            onChange={setFilter}
            items={[
              { value: 'all', text: 'Tất cả', count: result.questions.length },
              { value: 'miss', text: 'Câu sai hoặc chưa đủ điểm', count: misses.length },
            ]}
          />
          <button type="button" className="btn btn-sm" onClick={toggleAll} disabled={shown.length === 0}>
            {allOpen ? 'Ẩn tất cả giải thích' : 'Hiện tất cả giải thích'}
          </button>
        </div>
        {shown.length === 0 ? (
          <p className="muted">Không có câu nào sai — làm tốt lắm!</p>
        ) : (
          <div className="stack">
            {shown.map((q) => (
              <ResultQuestion
                key={q.position}
                question={q}
                showExplanation={open.has(q.position)}
                onToggle={() => toggle(q.position)}
              />
            ))}
          </div>
        )}
      </section>
    </>
  );
}
