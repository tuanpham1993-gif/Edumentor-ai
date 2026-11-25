import {
  CAREER_LEVEL_LABELS, DURATION_UNIT_LABELS, EVIDENCE_LABELS, PERIOD_LABELS, PROFICIENCY_LABELS, UNIT_LABELS, label,
} from '../labels.js';
import styles from '../styles/ProfileView.module.css';

// One view model for both shapes:
//  - preview.profile  (NormalizedG1Output, from /generate_ai_2)
//  - saved profile    (LearnerProfileResponse, from /learning-paths/{id}/profile)
export function fromNormalized(p, role) {
  const cb = p.career_background;
  const lc = p.learning_constraints ?? {};
  const st = lc.available_study_time;
  const dl = lc.deadline;
  return {
    goalType: p.goal.goal_type,
    roleRaw: p.goal.target_role?.raw_name,
    roleName: role?.role_name ?? p.goal.target_role?.canonical_name,
    technologies: p.goal.target_technologies.map((t) => ({ name: t.raw_name, linked: t.skill_id != null })),
    careerLevel: cb.career_level,
    jobTitle: cb.current_job_title?.raw_name,
    industry: cb.industry?.raw_name,
    experience: cb.relevant_it_work_experience,
    domains: cb.technical_domains.map((d) => d.canonical_name ?? d.raw_name),
    certifications: cb.certifications.map((c) => c.canonical_name ?? c.raw_name),
    previousRoles: cb.previous_job_roles.map((r) => r.raw_name),
    skills: p.skill_profiles.map((s) => ({
      name: s.skill_name, linkedName: s.link?.canonical_name, linked: s.link?.skill_id != null,
      proficiency: s.proficiency_level, duration: s.experience_duration, evidence: s.evidence_type,
    })),
    experiences: p.practical_experience.map((e) => ({ description: e.description, skills: e.related_skills.map((r) => r.raw_name) })),
    studyTime: st ? { value: st.value, unit: st.unit, period: st.period } : null,
    deadline: dl ? { type: dl.deadline_type, date: dl.target_date, value: dl.duration_value, unit: dl.duration_unit } : null,
  };
}

export function fromSaved(p) {
  return {
    goalType: p.goal_type,
    roleRaw: p.target_role_raw,
    roleName: p.role_name,
    technologies: p.target_technologies.map((t) => ({ name: t.raw_name, linked: t.skill_id != null })),
    careerLevel: p.career_level,
    jobTitle: p.current_job_title,
    industry: p.industry,
    experience: p.relevant_it_work_experience,
    domains: p.technical_domains,
    certifications: p.certifications,
    previousRoles: p.previous_job_roles,
    skills: p.skill_profiles.map((s) => ({
      name: s.raw_skill_name, linked: s.skill_id != null,
      proficiency: s.proficiency_level, duration: s.experience_duration, evidence: s.evidence_type,
    })),
    experiences: p.practical_experiences.map((e) => ({ description: e.description, skills: e.related_skills.map((r) => r.raw_name) })),
    studyTime: p.study_time_value ? { value: p.study_time_value, unit: p.study_time_unit, period: p.study_time_period } : null,
    deadline: p.deadline_type ? { type: p.deadline_type, date: p.deadline_target_date,
                                  value: p.deadline_duration_value, unit: p.deadline_duration_unit } : null,
  };
}

function Row({ k, children }) {
  return (
    <div className={styles.row}>
      <dt>{k}</dt>
      <dd>{children ?? <span className={styles.none}>—</span>}</dd>
    </div>
  );
}

function Chips({ items, empty = '—' }) {
  if (!items?.length) return <span className={styles.none}>{empty}</span>;
  return <span className={styles.chips}>{items.map((x) => <span key={x} className={styles.chip}>{x}</span>)}</span>;
}

export default function ProfileView({ view, compact = false }) {
  const v = view;
  const deadline = v.deadline
    ? v.deadline.type === 'fixed_date'
      ? `Đến ${v.deadline.date}`
      : `Trong ${v.deadline.value} ${label(DURATION_UNIT_LABELS, v.deadline.unit, '')}`
    : null;
  const study = v.studyTime
    ? `${v.studyTime.value} ${label(UNIT_LABELS, v.studyTime.unit, '')} ${label(PERIOD_LABELS, v.studyTime.period, '')}`
    : null;

  return (
    <div className={`${styles.wrap} ${compact ? styles.compact : ''}`}>
      <section className={styles.section}>
        <h3>🎯 Mục tiêu</h3>
        <dl>
          <Row k="Loại">{v.goalType === 'project' ? 'Dự án' : 'Nghề nghiệp'}</Row>
          {(v.roleRaw || v.roleName) && (
            <Row k="Vị trí">
              {v.roleName ?? v.roleRaw}
              {v.roleRaw && v.roleName && v.roleRaw.toLowerCase() !== v.roleName.toLowerCase() && (
                <small className={styles.muted}> (bạn ghi: “{v.roleRaw}”)</small>
              )}
            </Row>
          )}
          {v.technologies.length > 0 && <Row k="Công nghệ"><Chips items={v.technologies.map((t) => t.name)} /></Row>}
        </dl>
      </section>

      <section className={styles.section}>
        <h3>💼 Nền tảng</h3>
        <dl>
          <Row k="Cấp độ">{v.careerLevel ? label(CAREER_LEVEL_LABELS, v.careerLevel) : null}</Row>
          <Row k="Công việc">{v.jobTitle}</Row>
          <Row k="Kinh nghiệm IT">{v.experience}</Row>
          <Row k="Ngành">{v.industry}</Row>
          <Row k="Mảng kỹ thuật"><Chips items={v.domains} /></Row>
          <Row k="Chứng chỉ"><Chips items={v.certifications} /></Row>
          {v.previousRoles?.length > 0 && <Row k="Vị trí trước đây"><Chips items={v.previousRoles} /></Row>}
        </dl>
      </section>

      <section className={styles.section}>
        <h3>🧠 Kỹ năng đã có</h3>
        {v.skills.length === 0 ? <p className={styles.none}>Chưa ghi nhận kỹ năng nào.</p> : (
          <ul className={styles.skills}>
            {v.skills.map((s) => (
              <li key={s.name} className={s.linked ? '' : styles.unlinked}
                title={s.linked ? EVIDENCE_LABELS[s.evidence] : 'Chưa khớp với danh mục kỹ năng'}>
                <strong>{s.name}</strong>
                {s.linkedName && s.linkedName.toLowerCase() !== s.name.toLowerCase() && (
                  <small className={styles.muted}>→ {s.linkedName}</small>
                )}
                <span className={styles.meta}>
                  {s.proficiency && <span className={styles.badge}>{label(PROFICIENCY_LABELS, s.proficiency)}</span>}
                  {s.duration && <span className={styles.badgeSoft}>{s.duration}</span>}
                  {s.evidence === 'inferred_from_context' && <span className={styles.badgeSoft}>suy ra</span>}
                </span>
              </li>
            ))}
          </ul>
        )}
        {v.experiences.length > 0 && !compact && (
          <>
            <h4>Kinh nghiệm thực tế</h4>
            <ul className={styles.experiences}>
              {v.experiences.map((e) => (
                <li key={e.description}>{e.description}{e.skills.length > 0 && <Chips items={e.skills} />}</li>
              ))}
            </ul>
          </>
        )}
      </section>

      <section className={styles.section}>
        <h3>⏱ Thời gian</h3>
        <dl>
          <Row k="Thời gian học">{study}</Row>
          <Row k="Hạn">{deadline}</Row>
        </dl>
      </section>
    </div>
  );
}
