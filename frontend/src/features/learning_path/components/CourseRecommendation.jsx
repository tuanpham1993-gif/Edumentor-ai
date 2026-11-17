import styles from '../styles/CourseRecommendation.module.css';

export default function CourseRecommendation({
  skill, learningPathId}) {
  if (!skill) return null;
  return (
    <section className={styles.recommendationContainer}>
      <header className={styles.recommendationHeader}>
        <span className={styles.sectionLabel}>
          COURSE RECOMMENDATIONS
        </span>
        <h2>{skill.skillName}</h2>
        <p>Courses related to this skill.</p>
      </header>

      <div className={styles.recommendationContent}>
        {/* Course cards will be rendered here later. */}

        <div className={styles.emptyCourses}>
          <span className={styles.emptyIcon}>▤</span>
          <h3>No courses loaded yet</h3>
          <p>
            Recommended courses for {skill.skillName}
            will appear here.
          </p>
        </div>
      </div>
    </section>
  );
}