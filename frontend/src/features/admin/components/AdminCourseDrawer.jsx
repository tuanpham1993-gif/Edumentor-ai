// Drawer thêm / chỉnh sửa khóa học trong Quản trị (Admin) — F11
import React, { useState, useEffect } from 'react';
import { adminApi } from '../../../api/admin.api.js';
import styles from '../styles/AdminCourses.module.css';

const LEVEL_OPTIONS = [
  { value: '', label: '-- Chưa phân cấp --' },
  { value: 'beginner', label: 'Cơ bản' },
  { value: 'intermediate', label: 'Trung cấp' },
  { value: 'advanced', label: 'Nâng cao' },
];

export default function AdminCourseDrawer({
  course,
  allSkills = [],
  isOpen,
  onClose,
  onSaved,
}) {
  // 1. Nhóm Thông tin cơ bản
  const [title, setTitle] = useState('');
  const [instructor, setInstructor] = useState('');
  const [organization, setOrganization] = useState('');
  const [level, setLevel] = useState('');
  const [modules, setModules] = useState('');

  // 2. Nhóm Chỉ số & Thời lượng
  const [rating, setRating] = useState('');
  const [numReviews, setNumReviews] = useState('');
  const [numEnrolled, setNumEnrolled] = useState('');
  const [schedule, setSchedule] = useState('');

  // 3. Nhóm Liên kết & Hình ảnh
  const [url, setUrl] = useState('');
  const [image, setImage] = useState('');
  const [imageError, setImageError] = useState(false);

  // 4. Nhóm Nội dung & Kỹ năng
  const [description, setDescription] = useState('');
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [skillToAddId, setSkillToAddId] = useState('');

  // Trạng thái form
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    setErrorMsg('');
    setImageError(false);

    if (course) {
      setTitle(course.title || '');
      setInstructor(course.instructor || '');
      setOrganization(course.organization || '');
      setLevel(course.level || '');
      setModules(course.modules || '');

      setRating(course.rating != null ? String(course.rating) : '');
      setNumReviews(course.num_reviews != null ? String(course.num_reviews) : '');
      setNumEnrolled(course.num_enrolled != null ? String(course.num_enrolled) : '');
      setSchedule(course.schedule || '');

      setUrl(course.url || '');
      setImage(course.image || '');

      setDescription(course.description || '');
      setSelectedSkills(course.skills_info ? [...course.skills_info] : []);
    } else {
      setTitle('');
      setInstructor('');
      setOrganization('');
      setLevel('');
      setModules('');

      setRating('');
      setNumReviews('');
      setNumEnrolled('');
      setSchedule('');

      setUrl('');
      setImage('');

      setDescription('');
      setSelectedSkills([]);
    }
  }, [course, isOpen]);

  if (!isOpen) return null;

  function handleAddSkill() {
    if (!skillToAddId) return;
    const skillObj = allSkills.find((s) => String(s.skill_id) === String(skillToAddId));
    if (skillObj && !selectedSkills.some((s) => s.skill_id === skillObj.skill_id)) {
      setSelectedSkills([...selectedSkills, { skill_id: skillObj.skill_id, skill: skillObj.skill }]);
    }
    setSkillToAddId('');
  }

  function handleRemoveSkill(skillIdToRemove) {
    setSelectedSkills(selectedSkills.filter((s) => s.skill_id !== skillIdToRemove));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!title.trim()) {
      setErrorMsg('Vui lòng nhập tên khóa học.');
      return;
    }

    // Kiểm tra định dạng số nếu có nhập
    let parsedRating = null;
    if (rating.trim() !== '') {
      const val = parseFloat(rating);
      if (isNaN(val) || val < 0 || val > 5) {
        setErrorMsg('Điểm đánh giá phải là số từ 0.0 đến 5.0.');
        return;
      }
      parsedRating = val;
    }

    let parsedReviews = null;
    if (numReviews.trim() !== '') {
      const val = parseInt(numReviews, 10);
      if (isNaN(val) || val < 0) {
        setErrorMsg('Số lượt đánh giá phải là số nguyên không âm (≥ 0).');
        return;
      }
      parsedReviews = val;
    }

    let parsedEnrolled = null;
    if (numEnrolled.trim() !== '') {
      const val = parseInt(numEnrolled, 10);
      if (isNaN(val) || val < 0) {
        setErrorMsg('Số người đã đăng ký phải là số nguyên không âm (≥ 0).');
        return;
      }
      parsedEnrolled = val;
    }

    setIsSubmitting(true);
    setErrorMsg('');

    try {
      const payload = {
        title: title.trim(),
        instructor: instructor.trim() || null,
        organization: organization.trim() || null,
        level: level || null,
        modules: modules.trim() || null,
        rating: parsedRating,
        num_reviews: parsedReviews,
        num_enrolled: parsedEnrolled,
        schedule: schedule.trim() || null,
        url: url.trim() || null,
        image: image.trim() || null,
        description: description.trim() || null,
      };

      if (course) {
        // 1. Cập nhật khóa học hiện tại (PATCH)
        await adminApi.updateCourse(course.course_id, payload);

        // 2. Đồng bộ kỹ năng liên kết
        const originalSkills = course.skills_info || [];
        const toAdd = selectedSkills.filter(
          (s) => !originalSkills.some((orig) => orig.skill_id === s.skill_id)
        );
        const toRemove = originalSkills.filter(
          (orig) => !selectedSkills.some((s) => s.skill_id === orig.skill_id)
        );

        await Promise.allSettled([
          ...toAdd.map((s) => adminApi.addCourseSkill(course.course_id, s.skill_id)),
          ...toRemove.map((s) => adminApi.deleteCourseSkill(course.course_id, s.skill_id)),
        ]);
      } else {
        // 1. Tạo khóa học mới (POST)
        const created = await adminApi.createCourse(payload);
        const newCourseId = created.course_id;

        // 2. Gắn các kỹ năng ban đầu
        if (selectedSkills.length > 0 && newCourseId) {
          await Promise.allSettled(
            selectedSkills.map((s) => adminApi.addCourseSkill(newCourseId, s.skill_id))
          );
        }
      }

      if (onSaved) {
        await onSaved();
      }
      onClose();
    } catch (err) {
      console.error('Lỗi khi lưu khóa học:', err);
      const detail = err.response?.data?.detail;
      const msg =
        typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
          ? detail[0]?.msg
          : 'Có lỗi xảy ra khi lưu khóa học.';
      setErrorMsg(msg);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <aside className={styles.drawer} aria-label={course ? 'Sửa khóa học' : 'Thêm khóa học'}>
      {/* Header Drawer */}
      <div className={styles.drawerHeader}>
        <h2>{course ? 'Sửa khóa học' : 'Thêm khóa học'}</h2>
        <button
          type="button"
          className={styles.iconBtn}
          onClick={onClose}
          aria-label="Đóng"
          disabled={isSubmitting}
        >
          ✕
        </button>
      </div>

      {errorMsg && (
        <div style={{ padding: '8px 12px', background: 'rgba(239, 68, 68, 0.15)', color: '#f87171', borderRadius: '8px', fontSize: '13px' }}>
          {errorMsg}
        </div>
      )}

      {/* Form cuộn nội dung */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
        <div className={styles.drawerBody}>
          {/* ============================================================ */}
          {/* NHÓM 1: THÔNG TIN CƠ BẢN */}
          {/* ============================================================ */}
          <div className={styles.sectionHeader}>
            <span className={styles.sectionTitle}>1. Thông tin cơ bản</span>
            <div className={styles.sectionLine} />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="course-title">Tên khóa học *</label>
            <input
              id="course-title"
              className={styles.formInput}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="vd: Deep Learning Cơ bản đến Nâng cao"
              required
              disabled={isSubmitting}
            />
          </div>

          <div className={styles.twoCols}>
            <div className={styles.formGroup}>
              <label htmlFor="course-instructor">Giảng viên</label>
              <input
                id="course-instructor"
                className={styles.formInput}
                value={instructor}
                onChange={(e) => setInstructor(e.target.value)}
                placeholder="vd: Andrew Ng"
                disabled={isSubmitting}
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="course-platform">Đơn vị / Nền tảng</label>
              <input
                id="course-platform"
                className={styles.formInput}
                list="platform-options"
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
                placeholder="vd: Coursera, IBM"
                disabled={isSubmitting}
              />
              <datalist id="platform-options">
                <option value="Coursera" />
                <option value="edX" />
                <option value="Udemy" />
                <option value="Khan Academy" />
                <option value="IBM" />
                <option value="Google Cloud" />
                <option value="Microsoft" />
                <option value="Stanford Online" />
              </datalist>
            </div>
          </div>

          <div className={styles.twoCols}>
            <div className={styles.formGroup}>
              <label htmlFor="course-level">Cấp độ</label>
              <select
                id="course-level"
                className={styles.formSelect}
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                disabled={isSubmitting}
              >
                {LEVEL_OPTIONS.map((lvl) => (
                  <option key={lvl.value} value={lvl.value}>
                    {lvl.label}
                  </option>
                ))}
              </select>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="course-modules">Số chương / Modules</label>
              <input
                id="course-modules"
                className={styles.formInput}
                value={modules}
                onChange={(e) => setModules(e.target.value)}
                placeholder="vd: 6 modules, 12 bài học"
                disabled={isSubmitting}
              />
            </div>
          </div>

          {/* ============================================================ */}
          {/* NHÓM 2: CHỈ SỐ & THỜI LƯỢNG */}
          {/* ============================================================ */}
          <div className={styles.sectionHeader}>
            <span className={styles.sectionTitle}>2. Chỉ số & Thời lượng</span>
            <div className={styles.sectionLine} />
          </div>

          <div className={styles.twoCols}>
            <div className={styles.formGroup}>
              <label htmlFor="course-rating">Đánh giá sao (0.0 - 5.0)</label>
              <input
                id="course-rating"
                type="number"
                step="0.1"
                min="0"
                max="5"
                className={styles.formInput}
                value={rating}
                onChange={(e) => setRating(e.target.value)}
                placeholder="vd: 4.8 (để trống nếu chưa có)"
                disabled={isSubmitting}
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="course-duration">Thời lượng / Lịch học</label>
              <input
                id="course-duration"
                className={styles.formInput}
                value={schedule}
                onChange={(e) => setSchedule(e.target.value)}
                placeholder="vd: 20 giờ, 4 tuần"
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className={styles.twoCols}>
            <div className={styles.formGroup}>
              <label htmlFor="course-reviews">Lượt đánh giá (reviews)</label>
              <input
                id="course-reviews"
                type="number"
                min="0"
                className={styles.formInput}
                value={numReviews}
                onChange={(e) => setNumReviews(e.target.value)}
                placeholder="vd: 320"
                disabled={isSubmitting}
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="course-enrolled">Số người đã đăng ký</label>
              <input
                id="course-enrolled"
                type="number"
                min="0"
                className={styles.formInput}
                value={numEnrolled}
                onChange={(e) => setNumEnrolled(e.target.value)}
                placeholder="vd: 1250"
                disabled={isSubmitting}
              />
            </div>
          </div>

          {/* ============================================================ */}
          {/* NHÓM 3: LIÊN KẾT & HÌNH ẢNH */}
          {/* ============================================================ */}
          <div className={styles.sectionHeader}>
            <span className={styles.sectionTitle}>3. Liên kết & Hình ảnh</span>
            <div className={styles.sectionLine} />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="course-url">Đường dẫn khóa học gốc (URL)</label>
            <input
              id="course-url"
              type="url"
              className={styles.formInput}
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://coursera.org/learn/..."
              disabled={isSubmitting}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="course-image">Ảnh đại diện (Image URL)</label>
            <div className={styles.imageRow}>
              <div className={styles.thumbBox} title={image && !imageError ? 'Xem trước ảnh' : 'Chưa có ảnh hợp lệ'}>
                {image.trim() && !imageError ? (
                  <img
                    src={image.trim()}
                    alt="Preview"
                    className={styles.thumbImg}
                    onError={() => setImageError(true)}
                  />
                ) : (
                  <svg
                    aria-hidden="true"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.6"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
                    <circle cx="9" cy="9" r="2" />
                    <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
                  </svg>
                )}
              </div>
              <input
                id="course-image"
                type="url"
                className={styles.formInput}
                value={image}
                onChange={(e) => {
                  setImage(e.target.value);
                  setImageError(false);
                }}
                placeholder="https://images.unsplash.com/... (link ảnh thumbnail)"
                style={{ flex: 1 }}
                disabled={isSubmitting}
              />
            </div>
            {imageError && (
              <span className={styles.helperText} style={{ color: '#f87171' }}>
                Không thể tải ảnh từ liên kết trên. Vui lòng kiểm tra lại URL.
              </span>
            )}
          </div>

          {/* ============================================================ */}
          {/* NHÓM 4: NỘI DUNG & KỸ NĂNG */}
          {/* ============================================================ */}
          <div className={styles.sectionHeader}>
            <span className={styles.sectionTitle}>4. Nội dung & Kỹ năng</span>
            <div className={styles.sectionLine} />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="course-desc">Mô tả tóm tắt</label>
            <textarea
              id="course-desc"
              className={styles.formTextarea}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Mục tiêu đầu ra, nội dung kiến thức chính của khóa..."
              disabled={isSubmitting}
            />
          </div>

          <div className={styles.formGroup}>
            <label>Kỹ năng liên kết ({selectedSkills.length})</label>
            <div className={styles.chips}>
              {selectedSkills.length === 0 ? (
                <span style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>Chưa có kỹ năng nào</span>
              ) : (
                selectedSkills.map((s) => (
                  <span key={s.skill_id} className={styles.skillChip}>
                    {s.skill}
                    <button
                      type="button"
                      className={styles.chipRemove}
                      onClick={() => handleRemoveSkill(s.skill_id)}
                      aria-label={`Xóa kỹ năng ${s.skill}`}
                      disabled={isSubmitting}
                    >
                      ✕
                    </button>
                  </span>
                ))
              )}
            </div>

            <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
              <select
                className={styles.formSelect}
                value={skillToAddId}
                onChange={(e) => setSkillToAddId(e.target.value)}
                style={{ flex: 1 }}
                disabled={isSubmitting}
              >
                <option value="">-- Chọn kỹ năng để gắn --</option>
                {allSkills
                  .filter((sk) => !selectedSkills.some((s) => s.skill_id === sk.skill_id))
                  .map((sk) => (
                    <option key={sk.skill_id} value={sk.skill_id}>
                      {sk.skill}
                    </option>
                  ))}
              </select>
              <button
                type="button"
                className={styles.cancelBtn}
                onClick={handleAddSkill}
                style={{ padding: '0 14px' }}
                disabled={!skillToAddId || isSubmitting}
              >
                Gắn
              </button>
            </div>
          </div>
        </div>

        {/* Footer Drawer */}
        <div className={styles.drawerFooter}>
          <button
            type="button"
            className={styles.cancelBtn}
            onClick={onClose}
            disabled={isSubmitting}
          >
            Hủy
          </button>
          <button
            type="submit"
            className={styles.saveBtn}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Đang lưu...' : (course ? 'Cập nhật' : 'Lưu khóa học')}
          </button>
        </div>
      </form>
    </aside>
  );
}
