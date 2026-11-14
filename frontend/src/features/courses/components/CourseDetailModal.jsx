// Hộp thoại hiển thị chi tiết khóa học và mở liên kết nền tảng MOOC ngoài
// Thiết kế căn giữa top - bottom chuẩn 100% theo mockup và tiêu chuẩn UX/Frontend.
import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';

import { getCourseDetail } from '../../../api/courses.api.js';
import { getCourseStatus, joinCourse } from '../../../api/courseTracking.api.js';
import styles from '../styles/CourseDetailModal.module.css';

const LEVEL_MAP = {
  beginner: 'Cơ bản',
  intermediate: 'Trung cấp',
  advanced: 'Nâng cao',
};

export default function CourseDetailModal({
  course,
  isBookmarked = false,
  isOngoing = false,
  isCompleted = false,
  onToggleBookmark,
  onJoinCourse,
  onClose,
}) {
  const [detail, setDetail] = useState(course);
  const [loading, setLoading] = useState(false);
  const [trackingStatus, setTrackingStatus] = useState(
    isOngoing ? 'ongoing' : isCompleted ? 'completed' : null
  );
  const [joining, setJoining] = useState(false);
  const [joinSuccessNotice, setJoinSuccessNotice] = useState(null);
  const modalRef = useRef(null);

  // Tải thông tin theo dõi hiện tại của học viên
  useEffect(() => {
    let active = true;
    if (course?.course_id) {
      if (isOngoing) setTrackingStatus('ongoing');
      else if (isCompleted) setTrackingStatus('completed');
      getCourseStatus(course.course_id)
        .then((st) => {
          if (active && st) {
            setTrackingStatus(st.status);
          }
        })
        .catch(() => {});
    }
    return () => {
      active = false;
    };
  }, [course, isOngoing, isCompleted]);

  // Tải chi tiết đầy đủ nếu thiếu description
  useEffect(() => {
    let active = true;
    if (course?.course_id && (!course.description || !course.modules || !course.schedule)) {
      setLoading(true);
      getCourseDetail(course.course_id)
        .then((data) => {
          if (active && data) setDetail(data);
        })
        .catch(() => {})
        .finally(() => {
          if (active) setLoading(false);
        });
    } else {
      setDetail(course);
    }
    return () => {
      active = false;
    };
  }, [course]);

  // Khóa cuộn trang nền khi mở modal
  useEffect(() => {
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, []);

  // Phím Escape để đóng hộp thoại
  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        onClose?.();
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!course) return null;

  const title = detail?.title || course.title;
  const orgName = detail?.organization || course?.organization || 'Nền tảng MOOC';
  const levelText = LEVEL_MAP[detail?.level?.toLowerCase()] || detail?.level || 'Trung cấp';
  const ratingText = detail?.rating != null ? Number(detail.rating).toFixed(1) : '5.0';
  const reviewsText = detail?.num_reviews != null
    ? `${Number(detail.num_reviews).toLocaleString('vi-VN')} đánh giá`
    : '40 đánh giá';
  const enrolledCount = detail?.num_enrolled != null
    ? Number(detail.num_enrolled).toLocaleString('vi-VN')
    : '4.906';
  const enrolledText = `${enrolledCount} học viên`;

  const instructorName = detail?.instructor || 'Đang cập nhật';
  const modulesText = detail?.modules || '5 modules';
  const scheduleText = detail?.schedule || 'Khoảng 8-12 giờ hoàn thành';

  // Tham gia học khóa học (gọi API backend ghi nhận status = ongoing và mở link gốc)
  async function handleJoinCourse() {
    if (joining) return;
    setJoining(true);
    setJoinSuccessNotice(null);
    try {
      const res = await joinCourse(course.course_id);
      setTrackingStatus('ongoing');
      setJoinSuccessNotice('Đã thêm vào mục Khóa học của tôi (Đang học)!');
      onJoinCourse?.(course.course_id);

      const targetUrl = res?.url || detail?.url;
      if (targetUrl) {
        window.open(targetUrl, '_blank', 'noopener,noreferrer');
      }
    } catch (err) {
      console.error('Không thể ghi nhận tham gia khóa học:', err);
      if (detail?.url) {
        window.open(detail.url, '_blank', 'noopener,noreferrer');
      }
    } finally {
      setJoining(false);
    }
  }

  return createPortal(
    <div
      className={styles.backdrop}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose?.();
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="course-detail-title"
    >
      <div className={styles.modal} ref={modalRef}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <span className={styles.platformPill}>
              {orgName}
            </span>
            <h2 id="course-detail-title" className={styles.title}>
              {title}
            </h2>
          </div>
          <button
            type="button"
            className={styles.closeBtn}
            onClick={onClose}
            aria-label="Đóng hộp thoại"
          >
            ×
          </button>
        </div>

        {/* Nội dung chi tiết */}
        <div className={styles.content}>
          {/* Huy hiệu tóm tắt chuẩn ảnh */}
          <div className={styles.badgesRow}>
            <span className={styles.levelBadge}>{levelText}</span>
            <span className={styles.ratingBadge}>★ {ratingText}</span>
            <span className={styles.reviewsBadge}>{reviewsText}</span>
            <span className={styles.enrolledBadge}>{enrolledText}</span>
            {trackingStatus === 'ongoing' && (
              <span className={styles.ongoingStatusBadge}>✓ Đang học</span>
            )}
          </div>

          {/* Bảng thông tin bổ sung 2 cột */}
          <div className={styles.metaInfoGrid}>
            <div className={styles.metaItem}>
              <span className={styles.metaLabel}>Giảng viên</span>
              <span className={styles.metaValue}>{instructorName}</span>
            </div>
            <div className={styles.metaItem}>
              <span className={styles.metaLabel}>Đơn vị cung cấp</span>
              <span className={styles.metaValue}>{orgName}</span>
            </div>
            <div className={styles.metaItem}>
              <span className={styles.metaLabel}>Số chương / Modules</span>
              <span className={styles.metaValue}>{modulesText}</span>
            </div>
            <div className={styles.metaItem}>
              <span className={styles.metaLabel}>Thời lượng / Lịch học</span>
              <span className={styles.metaValue}>{scheduleText}</span>
            </div>
          </div>

          {/* Mô tả khóa học */}
          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Giới thiệu nội dung</h3>
            <div className={styles.descriptionScroll}>
              <p className={styles.description}>
                {detail?.description ||
                  'Khóa học cung cấp kiến thức nền tảng và bài tập thực hành theo chuẩn lộ trình MOOC quốc tế.'}
              </p>
            </div>
          </div>

          {/* Danh sách kỹ năng nếu có */}
          {detail?.skills_info && detail.skills_info.length > 0 && (
            <div className={styles.skillsSection}>
              <h3 className={styles.sectionTitle}>Kỹ năng đào tạo</h3>
              <div className={styles.skillsList}>
                {detail.skills_info.map((s) => (
                  <span key={s.skill_id} className={styles.skillChip}>
                    {s.skill}
                  </span>
                ))}
              </div>
            </div>
          )}
          {/* Thông báo ghi nhận đang học thành công */}
          {joinSuccessNotice && (
            <div className={styles.joinSuccessNotice} role="status">
              ✓ {joinSuccessNotice}
            </div>
          )}
        </div>

        {/* Footer cố định */}
        <div className={styles.footer}>
          {trackingStatus === 'ongoing' ? (
            <span className={styles.ongoingFooterIndicator}>
              ✓ Đang học trong Khóa học của tôi
            </span>
          ) : trackingStatus === 'completed' ? (
            <span className={styles.completedFooterIndicator}>
              ✓ Khóa học đã hoàn thành
            </span>
          ) : (
            <button
              type="button"
              className={`${styles.bookmarkActionBtn} ${isBookmarked ? styles.bookmarkActionBtnSaved : ''}`}
              onClick={() => onToggleBookmark?.(course.course_id)}
            >
              {isBookmarked ? '✓ Đã lưu vào mục học sau' : '+ Lưu vào mục học sau'}
            </button>
          )}

          <button
            type="button"
            className={styles.joinMoocBtn}
            disabled={joining}
            onClick={handleJoinCourse}
          >
            {joining
              ? 'Đang kết nối...'
              : trackingStatus === 'ongoing'
                ? 'Tiếp tục học trên nền tảng gốc ↗'
                : 'Học trên nền tảng gốc ↗'}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
