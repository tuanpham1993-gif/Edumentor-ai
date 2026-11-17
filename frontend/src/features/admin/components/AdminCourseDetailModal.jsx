// Hộp thoại Modal Xem Chi Tiết Khóa Học Quản Trị (Admin Course Detail Modal)
import React, { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { adminApi } from '../../../api/admin.api.js';
import styles from '../styles/AdminCourseDetailModal.module.css';

const LEVEL_MAP = {
  beginner: 'Cơ bản',
  intermediate: 'Trung cấp',
  advanced: 'Nâng cao',
};

function formatDateTime(dateStr) {
  if (!dateStr) return null;
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return null;
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  return `${day}/${month}/${year} ${hours}:${minutes}`;
}

function getCourseMonogram(title) {
  if (!title) return 'ED';
  const words = title.trim().split(/\s+/);
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return (words[0][0] + words[1][0]).toUpperCase();
}

export default function AdminCourseDetailModal({
  course,
  isOpen,
  onClose,
  onEdit,
  onDelete,
}) {
  const [detail, setDetail] = useState(course);
  const [bannerError, setBannerError] = useState(false);
  const modalRef = useRef(null);

  // Khởi tạo và tải thêm chi tiết mới nhất từ server
  useEffect(() => {
    let active = true;
    setBannerError(false);
    if (course?.course_id) {
      setDetail(course);
      adminApi
        .getCourseDetail(course.course_id)
        .then((data) => {
          if (active && data) {
            setDetail(data);
          }
        })
        .catch((err) => {
          console.warn('Không thể nạp thêm chi tiết khóa học:', err);
        });
    }
    return () => {
      active = false;
    };
  }, [course, isOpen]);

  // Khóa cuộn trang khi mở modal
  useEffect(() => {
    if (!isOpen) return;
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    function handleKeyDown(e) {
      if (e.key === 'Escape') {
        onClose?.();
      }
    }
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      document.body.style.overflow = originalOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen || !course) return null;

  const current = detail || course;
  const title = current.title || 'Khóa học';
  const levelText = LEVEL_MAP[current.level?.toLowerCase()] || current.level || 'Chưa phân cấp';
  const monogram = getCourseMonogram(title);

  const hasRating = current.rating != null;
  const ratingText = hasRating ? `★ ${Number(current.rating).toFixed(1)}` : 'Chưa có đánh giá';

  const hasReviews = current.num_reviews != null && current.num_reviews > 0;
  const reviewsText = hasReviews
    ? `${Number(current.num_reviews).toLocaleString('vi-VN')} đánh giá`
    : 'Chưa có đánh giá';

  const hasEnrolled = current.num_enrolled != null && current.num_enrolled > 0;
  const enrolledText = hasEnrolled
    ? `${Number(current.num_enrolled).toLocaleString('vi-VN')} học viên`
    : 'Chưa có học viên';

  const scheduleText = current.schedule || 'Chưa cập nhật thời lượng';
  const modulesText = current.modules || 'Chưa cập nhật số chương';
  const instructorText = current.instructor || 'Chưa cập nhật giảng viên';
  const orgText = current.organization || 'Chưa cập nhật đơn vị';

  const createdAtText = formatDateTime(current.created_at) || 'Chưa xác định';
  const updatedAtText = formatDateTime(current.updated_at) || 'Chưa có chỉnh sửa';

  function handleEditClick() {
    onClose?.();
    onEdit?.(current);
  }

  function handleDeleteClick() {
    if (onDelete) {
      onDelete(current.course_id, current.title);
      onClose?.();
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
      aria-labelledby="admin-course-detail-title"
    >
      <div className={styles.modal} ref={modalRef}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <div className={styles.pillsRow}>
              <span className={styles.idBadge}>ID #{current.course_id}</span>
              <span className={styles.orgBadge}>[{orgText}]</span>
            </div>
            <h2 id="admin-course-detail-title" className={styles.title}>
              {title}
            </h2>
          </div>
          <button
            type="button"
            className={styles.closeBtn}
            onClick={onClose}
            aria-label="Đóng hộp thoại"
          >
            ✕
          </button>
        </div>

        {/* Nội dung cuộn */}
        <div className={styles.content}>
          {/* Banner ảnh hoặc Monogram Art */}
          <div className={styles.bannerWrap}>
            {current.image && !bannerError ? (
              <img
                src={current.image}
                alt={title}
                className={styles.bannerImg}
                onError={() => setBannerError(true)}
              />
            ) : (
              <div className={styles.bannerArt} aria-hidden="true">
                <span className={styles.bannerMonogram}>{monogram}</span>
              </div>
            )}
          </div>

          {/* Hàng huy hiệu tóm tắt */}
          <div className={styles.badgesRow}>
            <span className={styles.badgeLevel}>{levelText}</span>
            <span className={hasRating ? styles.badgeRating : styles.badgeRatingEmpty}>
              {ratingText}
            </span>
            <span className={styles.badgeReviews}>{reviewsText}</span>
            <span className={styles.badgeEnrolled}>{enrolledText}</span>
            <span className={styles.badgeSchedule}>{scheduleText}</span>
            <span className={styles.badgeModules}>{modulesText}</span>
          </div>

          {/* Lưới thông tin quản trị 2 cột */}
          <div className={styles.metaGrid}>
            <div className={styles.metaItem}>
              <span className={styles.metaLabel}>Giảng viên</span>
              <span className={styles.metaValue}>{instructorText}</span>
            </div>

            <div className={styles.metaItem}>
              <span className={styles.metaLabel}>Đơn vị / Nền tảng</span>
              <span className={styles.metaValue}>{orgText}</span>
            </div>

            <div className={styles.metaItem}>
              <span className={styles.metaLabel}>Ngày thêm vào hệ thống</span>
              <span className={styles.metaValue}>{createdAtText}</span>
            </div>

            <div className={styles.metaItem}>
              <span className={styles.metaLabel}>Cập nhật lần cuối</span>
              <span className={styles.metaValue}>{updatedAtText}</span>
            </div>

            <div className={styles.metaItem} style={{ gridColumn: 'span 2' }}>
              <span className={styles.metaLabel}>Đường dẫn khóa học gốc (URL)</span>
              {current.url ? (
                <a
                  href={current.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.externalLink}
                >
                  {current.url}
                  <svg
                    aria-hidden="true"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                    <polyline points="15 3 21 3 21 9" />
                    <line x1="10" y1="14" x2="21" y2="3" />
                  </svg>
                </a>
              ) : (
                <span className={styles.emptyText}>Chưa cập nhật liên kết gốc</span>
              )}
            </div>
          </div>

          {/* Mô tả khóa học */}
          <div className={styles.section}>
            <span className={styles.sectionTitle}>Mô tả nội dung</span>
            <div className={styles.descriptionBox}>
              {current.description || 'Khóa học này hiện chưa có mô tả chi tiết từ đơn vị cung cấp.'}
            </div>
          </div>

          {/* Kỹ năng liên kết */}
          <div className={styles.section}>
            <span className={styles.sectionTitle}>
              Kỹ năng đào tạo ({current.skills_info?.length || 0})
            </span>
            <div className={styles.skillsList}>
              {current.skills_info && current.skills_info.length > 0 ? (
                current.skills_info.map((sk) => (
                  <span key={sk.skill_id} className={styles.skillChip}>
                    <svg
                      aria-hidden="true"
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                    {sk.skill}
                  </span>
                ))
              ) : (
                <span className={styles.emptyText}>Khóa học này chưa được liên kết với kỹ năng nào.</span>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className={styles.footer}>
          <button
            type="button"
            className={styles.deleteBtn}
            onClick={handleDeleteClick}
          >
            <svg
              aria-hidden="true"
              width="15"
              height="15"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13" />
            </svg>
            Xóa khóa học
          </button>

          <div className={styles.footerRight}>
            <button type="button" className={styles.cancelBtn} onClick={onClose}>
              Đóng
            </button>
            <button
              type="button"
              className={styles.editBtn}
              onClick={handleEditClick}
            >
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
                <path d="M4 20h4L19 9l-4-4L4 16zM14 6l4 4" />
              </svg>
              Chỉnh sửa khóa học
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
}
