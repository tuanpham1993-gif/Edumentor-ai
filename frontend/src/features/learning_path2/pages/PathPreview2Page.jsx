import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import PathGraph2 from '../components/PathGraph2.jsx';
import ProfileView, { fromNormalized } from '../components/ProfileView.jsx';
import LearningPathFeedbackModal from '../../learning_path/components/LearningPathDisagreeFeedback';
import { confirmLearningPath2, generateLearningPath2 } from '../../../api/learningPaths.api.js';
import { STATE_META } from '../labels.js';
import styles from '../styles/PathPages2.module.css';

export default function PathPreview2Page() {
  const location = useLocation();
  const navigate = useNavigate();
  const [preview, setPreview] = useState(location.state?.preview ?? null);
  const [request, setRequest] = useState(location.state?.request ?? null);
  const [answers, setAnswers] = useState({});
  const [selected, setSelected] = useState(null);
  const [tab, setTab] = useState('graph');
  const [busy, setBusy] = useState('');          // '' | 'regenerate' | 'save'
  const [error, setError] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);

  if (!preview) {
    return (
      <main className={styles.page}>
        <div className={styles.errorBox}>
          <p>Chưa có lộ trình để xem. Hãy tạo lộ trình trước.</p>
          <Link className="btn btn-primary" to="/me/my-learning-path">Về Lộ trình của tôi</Link>
        </div>
      </main>
    );
  }

  const canSave = preview.nodes.length > 0;
  const questions = preview.clarification_required ?? [];
  const stats = preview.stats;

  async function regenerate() {
    const extra = questions
      .map((q, i) => answers[i]?.trim() && `${q.question} ${answers[i].trim()}`)
      .filter(Boolean)
      .join('\n');
    if (!extra || !request) return;
    const next = { ...request, original_query: `${request.original_query}\n${extra}`.slice(0, 2000) };
    setBusy('regenerate');
    setError('');
    try {
      setPreview(await generateLearningPath2(next));
      setRequest(next);
      setAnswers({});
    } catch {
      setError('Không tạo lại được lộ trình. Vui lòng thử lại.');
    } finally {
      setBusy('');
    }
  }

  async function save() {
    setBusy('save');
    setError('');
    try {
      const res = await confirmLearningPath2(preview, true);
      navigate(`/me/my-learning-path/details/${res.record_id}`, { replace: true });
    } catch (err) {
      const d = err.response?.data?.detail;
      setError(typeof d === 'string' ? d : 'Không lưu được lộ trình. Vui lòng thử lại.');
    } finally {
      setBusy('');
    }
  }

  return (
    <main className={styles.page}>
      <header className={styles.previewHero}>
        <div className={styles.previewHeroText}>
          <span className={styles.eyebrow}>Bản xem trước · chưa lưu</span>
          <h1>{preview.original_query}</h1>
          <div className={styles.tagRow}>
            <span className={styles.tag}>{preview.goal_type === 'project' ? '🛠 Dự án' : '🎓 Nghề nghiệp'}</span>
            {preview.role && <span className={styles.tagAccent}>Vị trí: {preview.role.role_name}</span>}
            {preview.retrieval_status === 'incomplete' && <span className={styles.tagWarn}>Đồ thị bị rút gọn</span>}
          </div>
        </div>
        {canSave && (
          <div className={styles.statGrid}>
            <div><strong>{stats.remaining_to_learn}</strong><span>kỹ năng cần học</span></div>
            <div><strong>{stats.eligible_now}</strong><span>học được ngay</span></div>
            <div><strong>{stats.known_or_satisfied}</strong><span>đã biết / đủ nền</span></div>
            <div><strong>{stats.trimmed_nodes}</strong><span>đã bỏ qua</span></div>
          </div>
        )}
      </header>

      {questions.length > 0 && (
        <section className={styles.clarify} aria-labelledby="lp2-clarify">
          <h2 id="lp2-clarify">🤔 AI cần bạn làm rõ thêm</h2>
          {questions.map((q, i) => (
            <div key={`${q.field}-${i}`} className={styles.question}>
              <p>{q.question}</p>
              {q.options?.length ? (
                <div className={styles.optionRow}>
                  {q.options.map((o) => (
                    <button key={o} type="button" aria-pressed={answers[i] === o}
                      className={answers[i] === o ? styles.optionActive : styles.option}
                      onClick={() => setAnswers((a) => ({ ...a, [i]: o }))}>{o}</button>
                  ))}
                </div>
              ) : (
                <input className={styles.search} value={answers[i] ?? ''} placeholder="Câu trả lời của bạn…"
                  onChange={(e) => setAnswers((a) => ({ ...a, [i]: e.target.value }))} />
              )}
            </div>
          ))}
          <div className={styles.clarifyActions}>
            {canSave && <span className={styles.muted}>Bạn vẫn có thể lưu lộ trình hiện tại.</span>}
            <button type="button" className="btn btn-primary" onClick={regenerate}
              disabled={busy !== '' || !Object.values(answers).some((a) => a?.trim())}>
              {busy === 'regenerate' ? 'Đang tạo lại…' : 'Trả lời & tạo lại'}
            </button>
          </div>
        </section>
      )}

      {canSave && (
        <>
          <div className={styles.targetStrip}>
            <span>Kỹ năng đích:</span>
            {preview.targets.map((t) => (
              <span key={t.skill_id} className={styles.targetChip}>
                {t.skill_name}<small>{t.source === 'role' ? 'vị trí' : 'công nghệ'}</small>
              </span>
            ))}
          </div>

          <nav className={styles.tabs} role="tablist">
            <button type="button" role="tab" aria-selected={tab === 'graph'} onClick={() => setTab('graph')}
              className={tab === 'graph' ? styles.tabActive : ''}>Đồ thị kỹ năng</button>
            <button type="button" role="tab" aria-selected={tab === 'profile'} onClick={() => setTab('profile')}
              className={tab === 'profile' ? styles.tabActive : ''}>AI hiểu về bạn</button>
          </nav>

          {tab === 'graph' ? (
            <div className={styles.graphLayout}>
              <PathGraph2 graph={preview} selectedId={selected?.skillId} onSelect={setSelected} height={600} />
              <aside className={styles.sidePanel}>
                {selected ? (
                  <>
                    <span className={styles.eyebrow}>{STATE_META[selected.state]?.label}</span>
                    <h3>{selected.skillName}</h3>
                    <p className={styles.muted}>{STATE_META[selected.state]?.hint}</p>
                    {selected.isTarget && <p className={styles.tagAccent}>★ Kỹ năng đích của lộ trình</p>}
                  </>
                ) : (
                  <>
                    <h3>Cách đọc đồ thị</h3>
                    <p className={styles.muted}>Học từ trái sang phải. Ô <b>Học ngay</b> là điểm bắt đầu;
                      ô <b>Đã biết</b> là kỹ năng AI ghi nhận từ mô tả và hồ sơ của bạn.</p>
                    <p className={styles.muted}>Bấm vào một kỹ năng để xem chi tiết.</p>
                  </>
                )}
                {preview.warnings.length > 0 && (
                  <details className={styles.warnings}>
                    <summary>Ghi chú kỹ thuật ({preview.warnings.length})</summary>
                    <ul>{preview.warnings.map((w) => <li key={w}>{w}</li>)}</ul>
                  </details>
                )}
              </aside>
            </div>
          ) : (
            <ProfileView view={fromNormalized(preview.profile, preview.role)} />
          )}
        </>
      )}

      {error && <p className={styles.errorInline} role="alert">{error}</p>}

      <footer className={styles.stickyFooter}>
        <button type="button" className="btn btn-soft" disabled={busy !== ''}
          onClick={() => setShowFeedback(true)}>Không phù hợp</button>
        <button type="button" className="btn btn-primary" disabled={!canSave || busy !== ''} onClick={save}>
          {busy === 'save' ? 'Đang lưu…' : 'Lưu lộ trình'}
        </button>
      </footer>

      {showFeedback && <LearningPathFeedbackModal onClose={() => navigate('/me/my-learning-path')} />}
    </main>
  );
}
