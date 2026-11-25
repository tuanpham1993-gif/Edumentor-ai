import { useEffect, useMemo, useState } from 'react';
import CourseRecommendation from './CourseRecommendation';
import LearningPathGraph from './LearningPath';
import styles from '../styles/LearningPathPreview.module.css';

const GOAL_TYPE_LABELS = {
  career: 'Nghề nghiệp',
  project: 'Dự án',
};

export default function LearningPathPreview({
  learningPath,
  onConfirm,
  onCancel,
  isConfirming = false,
}) {
  const [selectedSkill, setSelectedSkill] = useState(null);

  useEffect(() => {
    setSelectedSkill(null);
  }, [learningPath]);

  const roleCounts = useMemo(() => {
    const nodes = learningPath?.nodes || [];
    const counts = { prerequisite: 0, extension: 0, related: 0 };
    nodes.forEach((n) => {
      if (n.node_role === 'prerequisite') counts.prerequisite += 1;
      else if (n.node_role === 'extension') counts.extension += 1;
      else if (n.node_role === 'related') counts.related += 1;
    });
    return counts;
  }, [learningPath]);

  if (!learningPath) {
    return null;
  }

  const goalType = learningPath.goal_type ?? 'learning';
  const goalTypeText = GOAL_TYPE_LABELS[goalType] || goalType;

  return (
    <section className={styles.previewContainer}>
      <header className={styles.previewHeader}>
        <div>
          <span className={styles.eyebrowPreview}>LỘ TRÌNH ĐÃ TẠO</span>
          <h2 className={styles.titlePreview}>Xem lại lộ trình của bạn</h2>
        </div>

        <span className={styles.skillCount}>
          {learningPath.nodes?.length ?? 0} kỹ năng
        </span>
      </header>

      <div className={styles.goalInformation}>
        <span className={styles.goalLabel}>Mục tiêu ban đầu</span>
        <p className={styles.originalQuery}>{learningPath.original_query}</p>
        <span className={styles.goalType}>Loại mục tiêu: {goalTypeText}</span>
      </div>

      <div className={styles.reviewMessage}>
        <strong>Đây là lộ trình gợi ý cho bạn.</strong>
        <span>
          Bấm vào từng kỹ năng trên đồ thị để xem khóa học gợi ý phù hợp trước khi lưu.
        </span>
      </div>

      {/* Bố cục 2 cột: Đồ thị bên trái + Khóa học gợi ý bên phải */}
      <div className={styles.previewBody}>
        <div className={styles.previewGraphPane}>
          <div className={styles.previewGraphHint}>
            <svg
              aria-hidden="true"
              width="15"
              height="15"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 16v-4" />
              <path d="M12 8h.01" />
            </svg>
            <span>Bấm vào 1 node kỹ năng để xem các khóa học gợi ý để học</span>
          </div>

          <LearningPathGraph
            learningPath={learningPath}
            onSelectSkill={(skillData) => setSelectedSkill(skillData)}
          />
        </div>

        <aside className={styles.previewCoursePane} aria-label="Khóa học gợi ý theo kỹ năng">
          {selectedSkill ? (
            <CourseRecommendation skill={selectedSkill} isPreviewMode />
          ) : (
            <div className={styles.coursePlaceholder}>
              <div className={styles.placeholderIcon} aria-hidden="true">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
                </svg>
              </div>
              <h3>Chọn một kỹ năng</h3>
              <p>
                Bấm vào bất kỳ kỹ năng nào trên đồ thị bên trái để xem ngay các khóa học phù hợp nhất để bắt đầu.
              </p>
              <div className={styles.roleSummaryPills}>
                {roleCounts.prerequisite > 0 && (
                  <span className={styles.rolePill}>
                    {roleCounts.prerequisite} tiên quyết
                  </span>
                )}
                {roleCounts.extension > 0 && (
                  <span className={styles.rolePill}>
                    {roleCounts.extension} mở rộng
                  </span>
                )}
                {roleCounts.related > 0 && (
                  <span className={styles.rolePill}>
                    {roleCounts.related} liên quan
                  </span>
                )}
              </div>
            </div>
          )}
        </aside>
      </div>

      <footer className={styles.previewFooter}>
        <button
          type="button"
          className={styles.cancelButtonPreview}
          onClick={onCancel}
          disabled={isConfirming}
        >
          Hủy
        </button>

        <button
          type="button"
          className={styles.confirmButtonPreview}
          onClick={onConfirm}
          disabled={isConfirming}
        >
          {isConfirming ? 'Đang lưu...' : 'Lưu lộ trình'}
        </button>
      </footer>
    </section>
  );
}
