// Component Thẻ khóa học (CourseCard)
// Tuân thủ thiết kế Monogram Art và UX tactile trong Docs & Mockup.
import { ArrowIcon } from '../../common/components/icons.jsx';
import { getCourseMonogram, getCoursePalette } from './CourseMonogram.jsx';
import styles from '../styles/CourseCard.module.css';

/** Icon Ruy-băng Bookmark */
function BookmarkRibbonIcon({ filled = false }) {
  return (
    <svg
      aria-hidden="true"
      width={18}
      height={18}
      viewBox="0 0 24 24"
      fill={filled ? 'currentColor' : 'none'}
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinejoin="round"
    >
      <path d="M6 3h12v18l-6-4-6 4z" />
    </svg>
  );
}

const LEVEL_MAP = {
  beginner: 'Cơ bản',
  intermediate: 'Trung cấp',
  advanced: 'Nâng cao',
};

export default function CourseCard({
  course,
  isBookmarked = false,
  isOngoing = false,
  isCompleted = false,
  onToggleBookmark,
  onSelectCourse,
}) {
  if (!course) return null;

  const { course_id, title, level, organization, rating, num_reviews, skills_info } = course;

  const monogram = getCourseMonogram(title);
  const palette = getCoursePalette(course_id, title);
  const levelText = LEVEL_MAP[level?.toLowerCase()] || level || 'Cơ bản';

  const ratingText = rating != null ? Number(rating).toFixed(1) : '5.0';
  const reviewsText = num_reviews != null
    ? `${Number(num_reviews).toLocaleString('vi-VN')} đánh giá`
    : '0 đánh giá';

  const platform = organization || 'EduMentor AI';

  function handleBookmarkClick(event) {
    event.stopPropagation();
    if (onToggleBookmark) {
      onToggleBookmark(course_id);
    }
  }

  function handleCardClick() {
    if (onSelectCourse) {
      onSelectCourse(course);
    }
  }

  return (
    <article
      className={styles.card}
      onClick={handleCardClick}
      style={{
        '--cover-base': palette.base,
        '--cover-ink': palette.ink,
        '--cover-base-l': palette.baseL,
        '--cover-ink-l': palette.inkL,
      }}
    >
      {/* 1. Phần Cover Monogram nghệ thuật */}
      <div className={styles.media}>
        <div className={styles.cover}>
          <div className={styles.coverArt} aria-hidden="true">
            <span className={styles.coverGrid} />
            <span className={styles.coverOrb} />
            <span className={styles.coverMono}>{monogram}</span>
          </div>
          <div className={styles.coverShade} aria-hidden="true" />
        </div>

        {/* Thanh platform & nút bookmark / badge trạng thái phía trên */}
        <div className={styles.mediaTop}>
          <span className={styles.platform} title={platform}>
            {platform}
          </span>
          {isOngoing ? (
            <span className={styles.ongoingBadge} title="Khóa học đang học trong Khóa học của tôi">
              ✓ Đang học
            </span>
          ) : isCompleted ? (
            <span className={styles.completedBadge} title="Khóa học đã hoàn thành">
              ✓ Đã hoàn thành
            </span>
          ) : (
            <button
              type="button"
              className={`${styles.saveBtn} ${isBookmarked ? styles.saveBtnSaved : ''}`}
              aria-pressed={isBookmarked}
              aria-label={isBookmarked ? 'Bỏ lưu khóa học' : 'Lưu khóa học'}
              onClick={handleBookmarkClick}
            >
              <BookmarkRibbonIcon filled={isBookmarked} />
            </button>
          )}
        </div>
      </div>

      {/* 2. Thân thẻ */}
      <div className={styles.body}>
        <h3 className={styles.title} title={title}>
          {title}
        </h3>
        <span className={styles.level}>{levelText}</span>

        {/* Kỹ năng liên quan */}
        <div className={styles.skills}>
          {skills_info && skills_info.length > 0 ? (
            skills_info.slice(0, 3).map((item) => (
              <span key={item.skill_id} className={styles.skill} title={item.skill}>
                {item.skill}
              </span>
            ))
          ) : (
            <span className={styles.skill}>Kỹ năng thực hành</span>
          )}
        </div>

        {/* Thông tin rating & số lượng đánh giá */}
        <div className={styles.meta}>
          <span className={styles.rating} title={`Đánh giá: ${ratingText}/5.0`}>
            ★ {ratingText}
          </span>
          <span className={styles.reviews}>{reviewsText}</span>
        </div>

        {/* Nút Xem chi tiết */}
        <button type="button" className={styles.cta} onClick={handleCardClick}>
          Xem chi tiết <ArrowIcon />
        </button>
      </div>
    </article>
  );
}
