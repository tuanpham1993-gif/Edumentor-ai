// Mức sẵn sàng ôn tập (7.4) — thẻ từng khóa + bảng từng kỹ năng của khóa đang chọn (module 09 · Tuấn · 16/11/2026).
// "Đủ để ôn" do backend tính bằng đúng hàm ráp đề của học viên → thẻ này trùng với việc học viên có bấm Bắt đầu được không.
import { READINESS_LEVELS } from '../reviewAdminFormat.js';
import styles from '../styles/AdminReviewQuestions.module.css';

const CARD_COUNT = 3;

function CourseCard({ course, selected, onSelect, targetPerSkill }) {
  return (
    <button
      type="button"
      className={`card ${styles.readyCard} ${selected ? styles.readyCardOn : ''}`}
      aria-pressed={selected}
      onClick={() => onSelect(selected ? null : course.course_id)}
    >
      <span className={styles.readyTitle}>{course.title}</span>
      <span className={styles.chips}>
        <span className={`chip ${course.ready ? 'chip-ok' : 'chip-danger'}`}>
          {course.ready ? 'Đủ để ôn' : 'Chưa đủ câu'}
        </span>
        {course.pending > 0 && <span className="chip chip-accent">{course.pending} chờ duyệt</span>}
      </span>
      <span className="small muted">
        {course.skill_count} kỹ năng · mục tiêu {targetPerSkill} câu mỗi kỹ năng
      </span>
      <span className={styles.readyCount}>
        <b>
          {course.active}/{course.target}
        </b>{' '}
        câu · {course.mcq} TN, {course.essay} TL
      </span>
      {!course.ready && course.missing[0] && <span className={`small ${styles.warn}`}>{course.missing[0]}</span>}
    </button>
  );
}

function SkillTable({ course, onPickSkill }) {
  return (
    <div className={`card ${styles.readyDetail}`}>
      <div className={styles.itemHead}>
        <b>{course.title}</b>
        <span className={`chip ${course.ready ? 'chip-ok' : 'chip-danger'}`}>
          {course.ready ? 'Học viên bắt đầu ôn được' : 'Học viên chưa ôn được'}
        </span>
      </div>
      {course.missing.length > 0 && (
        <ul className={styles.missing}>
          {course.missing.map((m) => (
            <li key={m}>{m}</li>
          ))}
        </ul>
      )}
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Kỹ năng</th>
              {READINESS_LEVELS.map((lv) => (
                <th key={lv.key} className={styles.num}>
                  {lv.text}
                </th>
              ))}
              <th className={styles.num}>Đang bật</th>
              <th className={styles.num}>Chờ duyệt</th>
            </tr>
          </thead>
          <tbody>
            {course.skills.map((s) => (
              <tr key={s.skill_id}>
                <td>
                  <button type="button" className={styles.linkBtn} onClick={() => onPickSkill(s.skill_id)}>
                    {s.skill}
                  </button>
                  {s.mcq === 0 && <span className={`small ${styles.warn}`}> · chưa có TN</span>}
                </td>
                {READINESS_LEVELS.map((lv) => (
                  <td key={lv.key} className={`${styles.num} ${s.by_level[lv.key] ? '' : styles.zero}`}>
                    {s.by_level[lv.key]}
                  </td>
                ))}
                <td className={styles.num}>
                  {s.active}/{s.target}
                </td>
                <td className={styles.num}>{s.pending || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="small muted">
        Chỉ tính câu đang bật. Câu chờ duyệt chưa vào đề cho tới khi được duyệt. Bấm tên kỹ năng để lọc câu hỏi.
      </p>
    </div>
  );
}

export default function ReadinessPanel({ summary, detail, selectedCourseId, onSelectCourse, onPickSkill }) {
  if (!summary) return <p className="muted small">Đang tải mức sẵn sàng…</p>;
  const courses = summary.courses;
  const shown = courses.slice(0, CARD_COUNT);
  // khóa đang chọn nằm ngoài 3 thẻ đầu (chọn từ ô lọc) → vẫn hiện thẻ của nó
  const picked = courses.find((c) => c.course_id === selectedCourseId);
  if (picked && !shown.includes(picked)) shown.push(picked);
  const rest = courses.filter((c) => !shown.includes(c));
  const restReady = rest.filter((c) => c.ready).length;

  return (
    <section className={styles.readiness} aria-label="Mức sẵn sàng ôn tập">
      <div className={styles.readyGrid}>
        {shown.map((c) => (
          <CourseCard
            key={c.course_id}
            course={c}
            selected={c.course_id === selectedCourseId}
            onSelect={onSelectCourse}
            targetPerSkill={summary.target_per_skill}
          />
        ))}
        <div className={`card ${styles.readyCard} ${styles.readyOther}`}>
          <span className={styles.readyTitle}>Khóa khác</span>
          <span className="small muted">
            {rest.length} khóa có câu hỏi{rest.length ? ` · ${restReady} đủ để ôn` : ''}
          </span>
          <span className="small muted">{summary.courses_without_questions} khóa chưa có câu hỏi nào</span>
          <span className="small muted">Chọn khóa ở ô lọc "Khóa học" để xem chi tiết.</span>
        </div>
      </div>
      {selectedCourseId && detail && <SkillTable course={detail} onPickSkill={onPickSkill} />}
    </section>
  );
}
