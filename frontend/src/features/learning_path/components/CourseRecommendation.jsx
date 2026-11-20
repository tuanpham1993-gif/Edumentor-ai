import styles from '../styles/CourseRecommendation.module.css';

export default function CourseRecommendation({
  skill, learningPathId}) {
  if (!skill) return null;
  return (
    <section className={styles.recommendationContainer}>
      <header className={styles.recommendationHeader}>
        <span className={styles.sectionLabel}>
          KHÓA HỌC GỢI Ý
        </span>
        <h2>{skill.skillName}</h2>
        <p>Khóa học liên quan đến kỹ năng này.</p>
      </header>

      <div className={styles.recommendationContent}>
        {/* Course cards will be rendered here later. */}

        <div className={styles.emptyCourses}>
          <span className={styles.emptyIcon}>▤</span>
          <h3>Chưa có khóa học</h3>
          <p>
            Khóa học gợi ý cho {skill.skillName}
            sẽ hiện ở đây.
          </p>
        </div>
      </div>
    </section>
  );
}