// Component Thanh bộ lọc và sắp xếp khóa học
import styles from '../styles/CoursesPage.module.css';

export default function CourseFilters({
  level = '',
  onLevelChange,
  sortBy = 'rating',
  onSortByChange,
  total = 0,
}) {
  return (
    <div className={styles.filterRow}>
      {/* Bộ lọc cấp độ */}
      <label className={styles.filterField}>
        <span>Cấp độ</span>
        <select value={level} onChange={(e) => onLevelChange?.(e.target.value)}>
          <option value="">Tất cả cấp độ</option>
          <option value="beginner">Cơ bản</option>
          <option value="intermediate">Trung cấp</option>
          <option value="advanced">Nâng cao</option>
        </select>
      </label>

      {/* Sắp xếp */}
      <label className={styles.filterField}>
        <span>Sắp xếp</span>
        <select value={sortBy} onChange={(e) => onSortByChange?.(e.target.value)}>
          <option value="rating">Đánh giá cao nhất</option>
          <option value="num_reviews">Nhiều lượt đánh giá nhất</option>
        </select>
      </label>

      {/* Số lượng kết quả */}
      <span className={styles.totalCount}>
        {Number(total).toLocaleString('vi-VN')} khóa học
      </span>
    </div>
  );
}
