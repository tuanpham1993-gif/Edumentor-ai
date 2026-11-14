// Component Khối "Khóa học của tôi" trên trang Hồ sơ người dùng (/me)
// Hiển thị tiến độ học tập thực tế, 4 tab trạng thái, và mở CourseDetailModal khi nhấp vào khóa học.
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import {
  getMyBookmarks,
  getMyCourses,
  joinCourse,
  removeBookmark,
  updateCourseStatus,
} from '../../../api/courseTracking.api.js';
import styles from '../styles/ProfileCourses.module.css';

/** Định dạng ngày tháng ngắn gọn */
function formatShortDate(dateString) {
  if (!dateString) return 'Mới đây';
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return 'Mới đây';
    return d.toLocaleDateString('vi-VN');
  } catch {
    return 'Mới đây';
  }
}

/** Trích xuất kỹ năng ngắn */
function getSkillsSummary(skillsInfo) {
  if (!skillsInfo || skillsInfo.length === 0) return 'Kiến thức cốt lõi';
  return skillsInfo.slice(0, 3).map((s) => s.skill).join(', ');
}

export default function ProfileCourses({ onSelectCourse, onStatsChange }) {
  const [activeTab, setActiveTab] = useState('ongoing');

  const [ongoingList, setOngoingList] = useState([]);
  const [bookmarkedList, setBookmarkedList] = useState([]);
  const [completedList, setCompletedList] = useState([]);
  const [abandonedList, setAbandonedList] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [busyIds, setBusyIds] = useState(new Set());
  const [notice, setNotice] = useState(null);

  function showNotice(text) {
    setNotice(text);
    setTimeout(() => setNotice(null), 3800);
  }

  function setBusy(courseId, isBusy) {
    setBusyIds((prev) => {
      const next = new Set(prev);
      if (isBusy) next.add(courseId);
      else next.delete(courseId);
      return next;
    });
  }

  // Tải danh sách khóa học của học viên
  const loadCoursesData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [ongoingRes, bookmarksRes, completedRes, abandonedRes] = await Promise.allSettled([
        getMyCourses({ status: 'ongoing', page_size: 5 }),
        getMyBookmarks(1, 5),
        getMyCourses({ status: 'completed', page_size: 5 }),
        getMyCourses({ status: 'abandoned', page_size: 5 }),
      ]);

      if (ongoingRes.status === 'fulfilled' && ongoingRes.value?.items) {
        setOngoingList(ongoingRes.value.items);
      }
      if (bookmarksRes.status === 'fulfilled' && bookmarksRes.value?.items) {
        setBookmarkedList(bookmarksRes.value.items);
      }
      if (completedRes.status === 'fulfilled' && completedRes.value?.items) {
        setCompletedList(completedRes.value.items);
      }
      if (abandonedRes.status === 'fulfilled' && abandonedRes.value?.items) {
        setAbandonedList(abandonedRes.value.items);
      }
    } catch (err) {
      setError(err?.message || 'Không thể tải danh sách khóa học.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCoursesData();
  }, [loadCoursesData]);

  // Hành động: Bỏ lưu khóa học
  async function handleRemoveBookmark(course) {
    setBusy(course.course_id, true);
    try {
      await removeBookmark(course.course_id);
      setBookmarkedList((prev) => prev.filter((c) => c.course_id !== course.course_id));
      showNotice(`Đã xóa "${course.title}" khỏi danh sách đã lưu.`);
      onStatsChange?.();
    } catch (err) {
      showNotice(err?.response?.data?.detail || 'Không thể bỏ lưu khóa học.');
    } finally {
      setBusy(course.course_id, false);
    }
  }

  // Hành động: Tham gia học từ mục đã lưu
  async function handleJoinFromBookmark(course) {
    setBusy(course.course_id, true);
    try {
      const res = await joinCourse(course.course_id);
      setBookmarkedList((prev) => prev.filter((c) => c.course_id !== course.course_id));
      setOngoingList((prev) => [
        { ...course, status: 'ongoing', joined_at: new Date().toISOString() },
        ...prev,
      ]);

      const targetUrl = res?.url || course.url;
      if (targetUrl) {
        window.open(targetUrl, '_blank', 'noopener,noreferrer');
      }
      showNotice(`Đã chuyển "${course.title}" sang mục Đang học!`);
      onStatsChange?.();
    } catch (err) {
      showNotice(err?.response?.data?.detail || 'Không thể tham gia khóa học.');
    } finally {
      setBusy(course.course_id, false);
    }
  }

  // Hành động: Học lại khóa học đã bỏ
  async function handleRestoreCourse(course) {
    setBusy(course.course_id, true);
    try {
      await updateCourseStatus(course.course_id, 'ongoing');
      setAbandonedList((prev) => prev.filter((c) => c.course_id !== course.course_id));
      setOngoingList((prev) => [
        { ...course, status: 'ongoing', joined_at: new Date().toISOString() },
        ...prev,
      ]);
      showNotice(`Đã khôi phục "${course.title}" về mục Đang học.`);
      onStatsChange?.();
    } catch (err) {
      showNotice(err?.response?.data?.detail || 'Không thể khôi phục khóa học.');
    } finally {
      setBusy(course.course_id, false);
    }
  }

  // Danh sách khóa học theo tab đang chọn
  const currentList =
    activeTab === 'ongoing'
      ? ongoingList
      : activeTab === 'bookmarked'
        ? bookmarkedList
        : activeTab === 'completed'
          ? completedList
          : abandonedList;

  return (
    <section className={`card ${styles.block}`}>
      {/* Header của khối */}
      <div className={styles.head}>
        <h2>Khóa học của tôi</h2>
        <Link to="/me/courses" className={styles.viewAllLink}>
          Xem tất cả →
        </Link>
      </div>

      {/* Banner thông báo nhanh nếu có */}
      {notice && (
        <div className={styles.noticeBanner} role="status">
          <span>✓ {notice}</span>
          <button
            type="button"
            className={styles.closeNoticeBtn}
            onClick={() => setNotice(null)}
            aria-label="Đóng thông báo"
          >
            ✕
          </button>
        </div>
      )}

      {/* Thanh Tab viên thuốc (Pill Tabs) */}
      <div role="tablist" aria-label="Lọc theo trạng thái" className={styles.tabsList}>
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === 'ongoing'}
          className={`${styles.tabBtn} ${activeTab === 'ongoing' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('ongoing')}
        >
          Đang học
          <span className={styles.tabCount}>&nbsp;({ongoingList.length})</span>
        </button>

        <button
          type="button"
          role="tab"
          aria-selected={activeTab === 'bookmarked'}
          className={`${styles.tabBtn} ${activeTab === 'bookmarked' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('bookmarked')}
        >
          Đã lưu
          <span className={styles.tabCount}>&nbsp;({bookmarkedList.length})</span>
        </button>

        <button
          type="button"
          role="tab"
          aria-selected={activeTab === 'completed'}
          className={`${styles.tabBtn} ${activeTab === 'completed' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('completed')}
        >
          Hoàn thành
          <span className={styles.tabCount}>&nbsp;({completedList.length})</span>
        </button>

        {abandonedList.length > 0 && (
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'abandoned'}
            className={`${styles.tabBtn} ${activeTab === 'abandoned' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('abandoned')}
          >
            Đã bỏ
            <span className={styles.tabCount}>&nbsp;({abandonedList.length})</span>
          </button>
        )}
      </div>

      {/* Trạng thái 1: Đang tải Skeletons */}
      {loading ? (
        <div className={styles.list} aria-hidden="true">
          <div className={`skeleton ${styles.skeletonItem}`} />
          <div className={`skeleton ${styles.skeletonItem}`} />
        </div>
      ) : error ? (
        /* Trạng thái 2: Lỗi */
        <div className={styles.empty}>
          <p className={styles.emptyText}>{error}</p>
          <button type="button" className="btn btn-sm" onClick={loadCoursesData}>
            Thử lại
          </button>
        </div>
      ) : currentList.length === 0 ? (
        /* Trạng thái 3: Danh sách rỗng */
        <div className={styles.empty}>
          <p className={styles.emptyText}>
            {activeTab === 'ongoing'
              ? 'Bạn chưa tham gia khóa học nào.'
              : activeTab === 'bookmarked'
                ? 'Chưa có khóa học nào được lưu để học sau.'
                : activeTab === 'completed'
                  ? 'Chưa có khóa học nào hoàn thành.'
                  : 'Không có khóa học nào trong danh sách Đã bỏ.'}
          </p>
          <Link to="/courses" className={styles.exploreLink}>
            Khám phá danh mục khóa học →
          </Link>
        </div>
      ) : (
        /* Trạng thái 4: Danh sách khóa học */
        <ul className={styles.list}>
          {currentList.map((c) => (
            <li key={c.course_id} className={styles.item}>
              {/* Thông tin khóa học */}
              <div className={styles.info}>
                <button
                  type="button"
                  className={styles.courseTitleBtn}
                  onClick={() => onSelectCourse?.(c)}
                  title="Nhấp để xem chi tiết khóa học"
                >
                  {c.title}
                </button>
                <span className={styles.meta}>
                  [{c.organization || 'Coursera'}] · Kỹ năng: {getSkillsSummary(c.skills_info)}
                  {activeTab === 'ongoing' && ` · Tham gia ${formatShortDate(c.joined_at || c.created_at)}`}
                  {activeTab === 'bookmarked' && ` · Lưu ${formatShortDate(c.created_at)}`}
                  {activeTab === 'completed' && ` · Hoàn thành ${formatShortDate(c.completed_at || c.updated_at)}`}
                </span>
              </div>

              {/* Nút hành động nhanh bên phải */}
              <div className={styles.actions}>
                {activeTab === 'ongoing' && (
                  <>
                    {c.url && (
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.openMoocLink}
                      >
                        Mở khóa học ↗
                      </a>
                    )}
                    <Link
                      to={`/courses/${c.course_id}/review`}
                      className={styles.reviewBtn}
                    >
                      Làm bài ôn tập
                    </Link>
                  </>
                )}

                {activeTab === 'bookmarked' && (
                  <>
                    <button
                      type="button"
                      className={styles.joinBtn}
                      disabled={busyIds.has(c.course_id)}
                      onClick={() => handleJoinFromBookmark(c)}
                    >
                      Tham gia học ↗
                    </button>
                    <button
                      type="button"
                      className={styles.unbookmarkBtn}
                      disabled={busyIds.has(c.course_id)}
                      onClick={() => handleRemoveBookmark(c)}
                    >
                      Bỏ lưu
                    </button>
                  </>
                )}

                {activeTab === 'completed' && (
                  <>
                    {c.url && (
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.openMoocLink}
                      >
                        Mở khóa học ↗
                      </a>
                    )}
                    <Link
                      to={`/courses/${c.course_id}/review`}
                      className={styles.reviewBtn}
                    >
                      Ôn tập lại
                    </Link>
                  </>
                )}

                {activeTab === 'abandoned' && (
                  <button
                    type="button"
                    className={styles.joinBtn}
                    disabled={busyIds.has(c.course_id)}
                    onClick={() => handleRestoreCourse(c)}
                  >
                    Học lại
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
