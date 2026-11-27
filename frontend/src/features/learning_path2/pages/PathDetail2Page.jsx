import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';

import PathGraph2 from '../components/PathGraph2.jsx';
import ProfileModal from '../components/ProfileModal.jsx';
import LearningPathToolBar from '../../learning_path/components/LearningPathToolBar';
import CourseRecommendation from '../../learning_path/components/CourseRecommendation';
import { SkillReviewProvider } from '../../review/components/SkillReviewContext.jsx';
import { getLearningPathById, getLearningPathProfile } from '../../../api/learningPaths.api.js';
import { getMySkills } from '../../../api/me.api.js';
import { getLearningPathSummary } from '../../../utils/learningPathUtils';
import { STATE_META } from '../labels.js';
import styles from '../styles/PathPages2.module.css';

// State per node: live account profile (known / learning) > state saved at generation > derived
// from prerequisites (eligible when every prerequisite is known or satisfied).
function deriveStates(path, saved, live) {
  const nodes = path?.nodes ?? [];
  const preds = new Map(nodes.map((n) => [n.skill_id, []]));
  (path?.edges ?? []).filter((e) => e.relation_type === 'prerequisite').forEach((e) => {
    preds.get(e.to_skill_id)?.push(e.from_skill_id);
  });
  const out = {};
  nodes.forEach((n) => {
    const id = String(n.skill_id);
    const liveStatus = live.get(n.skill_id);
    if (liveStatus === 'known') out[id] = 'known';
    else if (liveStatus === 'learning') out[id] = 'learning';
    else if (saved[id] === 'known' || saved[id] === 'satisfied') out[id] = saved[id];
  });
  nodes.forEach((n) => {
    const id = String(n.skill_id);
    if (out[id]) return;
    const ready = preds.get(n.skill_id).every((p) => ['known', 'satisfied'].includes(out[String(p)]));
    out[id] = ready ? 'eligible' : 'locked';
  });
  return out;
}

export default function PathDetail2Page() {
  const { recordId } = useParams();
  const location = useLocation();
  const [path, setPath] = useState(location.state?.learningPath ?? null);
  const [profile, setProfile] = useState(null);
  const [live, setLive] = useState(() => new Map());
  const [selected, setSelected] = useState(null);
  const [showProfile, setShowProfile] = useState(false);
  const [isLoading, setIsLoading] = useState(!path);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    try {
      setError('');
      const res = await getLearningPathById(recordId);
      setPath(res.data);
      if (selected && !res.data.nodes.some((n) => n.skill_id === Number(selected.skillId))) setSelected(null);
      return res.data;
    } catch (err) {
      setError('Không tải được lộ trình này.');
      throw err;
    }
  }, [recordId, selected]);

  useEffect(() => {
    if (path && String(path.record_id) === String(recordId)) return;
    setIsLoading(true);
    refresh().catch(() => {}).finally(() => setIsLoading(false));
  }, [recordId]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    let alive = true;
    getLearningPathProfile(recordId).then((d) => alive && setProfile(d)).catch(() => {});
    return () => { alive = false; };
  }, [recordId]);

  useEffect(() => {
    let alive = true;
    getMySkills()
      .then((skills) => alive && setLive(new Map(skills.map((s) => [s.skill_id, s.status]))))
      .catch(() => {});
    return () => { alive = false; };
  }, [path]);

  const graph = useMemo(() => ({
    nodes: (path?.nodes ?? []).map((n) => ({ ...n, skill_name: n.skill?.skill })),
    edges: path?.edges ?? [],
    layer: {},
  }), [path]);
  const states = useMemo(() => deriveStates(path, profile?.node_states ?? {}, live), [path, profile, live]);

  if (isLoading) return <main className={styles.page}><div className={styles.skeletonWide} /></main>;
  if (!path) {
    return (
      <main className={styles.page}>
        <div className={styles.errorBox}>
          <p>{error || 'Không có dữ liệu lộ trình.'}</p>
          <Link className="btn btn-primary" to="/me/my-learning-path">Về Lộ trình của tôi</Link>
        </div>
      </main>
    );
  }

  const { completedSkills, totalSkills, progressPercentage } = getLearningPathSummary(path);
  const counts = Object.values(states).reduce((acc, s) => ({ ...acc, [s]: (acc[s] ?? 0) + 1 }), {});

  return (
    <main className={styles.page}>
      <nav className={styles.crumbs}><Link to="/me/my-learning-path">Lộ trình của tôi</Link> / <span>Chi tiết</span></nav>

      <header className={styles.detailHero}>
        <div className={styles.previewHeroText}>
          <div className={styles.tagRow}>
            <span className={styles.tag}>{path.goal_type === 'project' ? '🛠 Dự án' : '🎓 Nghề nghiệp'}</span>
            {profile?.profile?.role_name && <span className={styles.tagAccent}>Vị trí: {profile.profile.role_name}</span>}
          </div>
          <h1>{path.original_query}</h1>
          <div className={styles.progressRow}>
            <span>{completedSkills}/{totalSkills} kỹ năng · {progressPercentage}%</span>
          </div>
          <div className={styles.track}><div className={styles.fill} style={{ width: `${progressPercentage}%` }} /></div>
          <div className={styles.stateCounts}>
            {Object.entries(STATE_META).filter(([k]) => counts[k]).map(([k, m]) => (
              <span key={k}><b>{counts[k]}</b> {m.label}</span>
            ))}
          </div>
        </div>
        <div className={styles.detailActions}>
          {path.has_profile && (
            <button type="button" className="btn btn-soft" onClick={() => setShowProfile(true)}>
              👤 Hồ sơ lộ trình
            </button>
          )}
        </div>
      </header>

      <div className={styles.toolbarWrap}>
        <LearningPathToolBar recordId={path.record_id} learningPath={path} selectedSkill={selected} nodes={path.nodes}
          edges={path.edges} onRefresh={refresh} />
      </div>

      {error && <p className={styles.errorInline} role="alert">{error}</p>}

      <section className={styles.graphLayout}>
        <SkillReviewProvider skillIds={path.nodes.map((n) => n.skill_id)}>
          <PathGraph2 graph={graph} states={states} selectedId={selected?.skillId} onSelect={setSelected} height={620} />
        </SkillReviewProvider>
        <aside className={styles.sidePanel}>
          {selected ? (
            <CourseRecommendation skill={selected} learningPathId={Number(recordId)} />
          ) : (
            <div className={styles.placeholder}>
              <span aria-hidden="true">↖</span>
              <h3>Chọn một kỹ năng</h3>
              <p className={styles.muted}>Bấm vào kỹ năng trên đồ thị để xem khóa học gợi ý và chỉnh sửa lộ trình.</p>
            </div>
          )}
        </aside>
      </section>

      {showProfile && (
        <ProfileModal recordId={path.record_id} title={path.original_query} onClose={() => setShowProfile(false)} />
      )}
    </main>
  );
}
