// Component hiển thị 1 khóa học nổi bật theo mỗi cấp độ (Cơ bản, Trung cấp, Nâng cao)
// sắp xếp theo số lượt đánh giá cao nhất (num_reviews).
// Tuân thủ quy ước: Page -> Component -> courses.api.js -> client.js -> Backend.
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { getFeaturedCoursesByLevels } from '../../../api/courses.api.js';
import { ArrowIcon } from '../../common/components/icons.jsx';
import { FEATURED_COURSES } from '../homeContent.js';
import HomeIcon from './HomeIcon.jsx';
import styles from '../styles/FeaturedCourses.module.css';

/**
 * Biểu tượng liên kết ngoài
 */
function ExternalLinkIcon() {
  return (
    <svg
      aria-hidden="true"
      width={14}
      height={14}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={styles.externalIcon}
    >
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" y1="14" x2="21" y2="3" />
    </svg>
  );
}

export default function FeaturedCourses() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);

  async function loadCourses() {
    setLoading(true);
    setErrorMessage(null);
    try {
      const data = await getFeaturedCoursesByLevels();

      // Kiểm tra xem có lấy được ít nhất 1 khóa học từ API không
      const hasAnyCourse = data.some((item) => item.course !== null);

      if (!hasAnyCourse) {
        // Nếu API không có dữ liệu thật hoặc lỗi mạng, sử dụng dữ liệu mẫu dự phòng
        const fallback = data.map((item, idx) => ({
          ...item,
          course: {
            title: FEATURED_COURSES[idx]?.title || 'Khóa học đang cập nhật',
            organization: 'EduMentor AI',
            instructor: 'Đang cập nhật',
            rating: 5.0,
            num_reviews: 1200,
            skills_info: [],
            url: null,
          },
        }));
        setItems(fallback);
        setErrorMessage('Đang hiển thị danh mục mẫu do máy chủ chưa phản hồi dữ liệu.');
      } else {
        setItems(data);
      }
    } catch (err) {
      const msg = err?.response?.data?.error?.message || err?.message || 'Không thể tải khóa học.';
      setErrorMessage(msg);
      // Fallback về dữ liệu mẫu trong homeContent.js
      setItems(
        FEATURED_COURSES.map((mock) => ({
          key: mock.level.toLowerCase(),
          label: mock.level,
          tone: mock.tone,
          course: {
            title: mock.title,
            organization: 'EduMentor AI',
            instructor: 'Đang cập nhật',
            rating: 4.8,
            num_reviews: 1000,
            skills_info: [],
            url: null,
          },
        })),
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCourses();
  }, []);

  // 1. Trạng thái Đang tải (Loading Skeleton)
  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.coursesGrid}>
          {[1, 2, 3].map((n) => (
            <div key={n} className={styles.skeletonCard} aria-hidden="true">
              <div className={`skeleton ${styles.skeletonThumb}`} />
              <div className={styles.skeletonBody}>
                <div className={`skeleton ${styles.skeletonPill}`} />
                <div className={`skeleton ${styles.skeletonTitle}`} />
                <div className={`skeleton ${styles.skeletonTitleSub}`} />
                <div className={`skeleton ${styles.skeletonMeta}`} />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // 2. Trạng thái Rỗng (Empty)
  if (!items || items.length === 0) {
    return (
      <div className={styles.container}>
        <div className={`card ${styles.emptyCard}`}>
          <p>Hiện chưa có khóa học nổi bật nào trong hệ thống.</p>
          <button type="button" className="btn btn-sm" onClick={loadCourses}>
            Tải lại
          </button>
        </div>
      </div>
    );
  }

  // 3 & 4. Trạng thái Thành công (có thể kèm banner cảnh báo nếu dùng fallback)
  return (
    <div className={styles.container}>
      {errorMessage && (
        <div className={styles.errorBanner} role="status">
          <span>{errorMessage}</span>
          <button type="button" className={`btn ${styles.retryBtn}`} onClick={loadCourses}>
            Thử lại
          </button>
        </div>
      )}

      <div className={styles.coursesGrid}>
        {items.map(({ key, label, tone, course }, index) => {
          if (!course) return null;

          const ratingText = course.rating ? Number(course.rating).toFixed(1) : '5.0';
          const reviewsText = course.num_reviews
            ? Number(course.num_reviews).toLocaleString('vi-VN')
            : '0';

          return (
            <article
              key={key}
              className={styles.courseCard}
              style={{ animationDelay: `${index * 90}ms` }}
            >
              {/* Thumbnail / Header của card */}
              <div className={styles.courseThumb}>
                <div className={styles.thumbBadges}>
                  <span className={`chip chip-${tone}`}>{label}</span>
                  {course.organization && (
                    <span className={styles.orgBadge} title={course.organization}>
                      {course.organization}
                    </span>
                  )}
                </div>
                <HomeIcon name="book" size={38} />
              </div>

              {/* Thân card */}
              <div className={styles.courseBody}>
                <div className={styles.titleArea}>
                  <h3 className={styles.courseTitle} title={course.title}>
                    {course.title}
                  </h3>
                  {course.instructor && (
                    <p className={styles.instructorText} title={`Giảng viên: ${course.instructor}`}>
                      Giảng viên: {course.instructor}
                    </p>
                  )}
                </div>

                {/* Danh sách kỹ năng tiêu biểu */}
                {course.skills_info && course.skills_info.length > 0 && (
                  <div className={styles.skillTags}>
                    {course.skills_info.slice(0, 3).map((s) => (
                      <span key={s.skill_id} className={styles.skillTag} title={s.skill}>
                        {s.skill}
                      </span>
                    ))}
                  </div>
                )}

                {/* Thông số đánh giá & Lượt review */}
                <div className={styles.metaRow}>
                  <span className={styles.rating} title={`Đánh giá: ${ratingText}/5.0`}>
                    ★ {ratingText}
                  </span>
                  <span className={styles.reviewsCount} title="Số lượt đánh giá">
                    ({reviewsText} đánh giá)
                  </span>
                </div>

                {/* Hành động xem khóa học: Ưu tiên link ngoài nếu có URL */}
                <div className={styles.actionRow}>
                  {course.url ? (
                    <a
                      href={course.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={styles.courseLink}
                    >
                      Xem khóa học <ExternalLinkIcon />
                    </a>
                  ) : (
                    <Link to="/courses" className={styles.courseLink}>
                      Xem khóa học <ArrowIcon />
                    </Link>
                  )}
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}
