// Trang "Khóa học của tôi" (/me/courses) dành cho học viên
// Đã kết nối đầy đủ các API Backend thực tế:
//   - GET /api/me/courses?status= (ongoing, completed, abandoned)
//   - GET /api/me/bookmarks
//   - POST /api/courses/{id}/join (Tham gia học)
//   - DELETE /api/me/courses/{id} (Ngừng theo dõi)
//   - DELETE /api/me/bookmarks/{id} (Bỏ lưu)
//   - PATCH /api/me/courses/{id}/status (Khôi phục học lại)
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import {
  abandonCourse,
  addBookmark,
  getMyBookmarks,
  getMyCourses,
  joinCourse,
  removeBookmark,
  updateCourseStatus,
} from '../../../api/courseTracking.api.js';
import CourseDetailModal from '../components/CourseDetailModal.jsx';
import styles from '../styles/MyCoursesPage.module.css';

/** Định dạng ngày tháng kiểu Việt Nam (dd/mm/yyyy) */
function formatDate(dateString) {
  if (!dateString) return 'Mới đây';
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return 'Mới đây';
    return d.toLocaleDateString('vi-VN');
  } catch {
    return 'Mới đây';
  }
}

/** Trích xuất chuỗi kỹ năng từ danh sách skills_info */
function getSkillsText(skillsInfo) {
  if (!skillsInfo || skillsInfo.length === 0) return 'Kiến thức cốt lõi';
  return skillsInfo.map((s) => s.skill).join(', ');
}

export default function MyCoursesPage() {
  // Tab đang chọn: 'ongoing' | 'bookmarked' | 'completed' | 'abandoned'
  const [activeTab, setActiveTab] = useState('ongoing');

  // Dữ liệu khóa học từ Backend
  const [ongoingCourses, setOngoingCourses] = useState([]);
  const [bookmarkedCourses, setBookmarkedCourses] = useState([]);
  const [completedCourses, setCompletedCourses] = useState([]);
  const [abandonedCourses, setAbandonedCourses] = useState([]);

  // Trạng thái tải dữ liệu
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Tập hợp ID các khóa học đang xử lý thao tác gọi API (để disable nút tránh double-click)
  const [busyIds, setBusyIds] = useState(new Set());

  // Khóa học đang chọn xem modal chi tiết
  const [selectedCourse, setSelectedCourse] = useState(null);

  // Thông báo phản hồi nhẹ (Toast / Alert)
  const [actionNotice, setActionNotice] = useState(null);

  function showNotice(text) {
    setActionNotice(text);
    setTimeout(() => {
      setActionNotice(null);
    }, 3800);
  }

  function setCourseBusy(courseId, isBusy) {
    setBusyIds((prev) => {
      const next = new Set(prev);
      if (isBusy) next.add(courseId);
      else next.delete(courseId);
      return next;
    });
  }

  // Tải toàn bộ dữ liệu từ Backend API
  const fetchAllTrackingData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [ongoingRes, bookmarksRes, completedRes, abandonedRes] = await Promise.allSettled([
        getMyCourses({ status: 'ongoing', page_size: 50 }),
        getMyBookmarks(1),
        getMyCourses({ status: 'completed', page_size: 50 }),
        getMyCourses({ status: 'abandoned', page_size: 50 }),
      ]);

      if (ongoingRes.status === 'fulfilled' && ongoingRes.value?.items) {
        setOngoingCourses(ongoingRes.value.items);
      }
      if (bookmarksRes.status === 'fulfilled' && bookmarksRes.value?.items) {
        setBookmarkedCourses(bookmarksRes.value.items);
      }
      if (completedRes.status === 'fulfilled' && completedRes.value?.items) {
        setCompletedCourses(completedRes.value.items);
      }
      if (abandonedRes.status === 'fulfilled' && abandonedRes.value?.items) {
        setAbandonedCourses(abandonedRes.value.items);
      }
    } catch (err) {
      const msg = err?.response?.data?.error?.message || err?.message || 'Không thể tải danh sách khóa học.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllTrackingData();
  }, [fetchAllTrackingData]);

  // 1. Thao tác: Ngừng theo dõi khóa đang học (Gọi DELETE /api/me/courses/{id})
  async function handleAbandonCourse(course) {
    const confirmed = window.confirm(`Bạn có chắc muốn ngừng theo dõi khóa học "${course.title}"?`);
    if (!confirmed) return;

    setCourseBusy(course.course_id, true);
    try {
      await abandonCourse(course.course_id);
      setOngoingCourses((prev) => prev.filter((c) => c.course_id !== course.course_id));
      setAbandonedCourses((prev) => [{ ...course, status: 'abandoned' }, ...prev]);
      showNotice(`Đã chuyển "${course.title}" sang mục Đã bỏ.`);
    } catch (err) {
      const msg = err?.response?.data?.error?.message || 'Không thể ngừng theo dõi khóa học.';
      alert(msg);
    } finally {
      setCourseBusy(course.course_id, false);
    }
  }

  // 2. Thao tác: Bỏ lưu khỏi danh sách Đã lưu (Gọi DELETE /api/me/bookmarks/{id})
  async function handleRemoveBookmark(course) {
    setCourseBusy(course.course_id, true);
    try {
      await removeBookmark(course.course_id);
      setBookmarkedCourses((prev) => prev.filter((c) => c.course_id !== course.course_id));
      showNotice(`Đã xóa "${course.title}" khỏi danh sách đã lưu.`);
    } catch (err) {
      const msg = err?.response?.data?.error?.message || 'Không thể bỏ lưu khóa học.';
      alert(msg);
    } finally {
      setCourseBusy(course.course_id, false);
    }
  }

  // 3. Thao tác: Tham gia học khóa đã lưu (Gọi POST /api/courses/{id}/join)
  async function handleJoinFromBookmark(course) {
    setCourseBusy(course.course_id, true);
    try {
      const res = await joinCourse(course.course_id);
      setBookmarkedCourses((prev) => prev.filter((c) => c.course_id !== course.course_id));
      setOngoingCourses((prev) => [{ ...course, status: 'ongoing', joined_at: new Date().toISOString() }, ...prev]);

      const targetUrl = res?.url || course.url;
      if (targetUrl) {
        window.open(targetUrl, '_blank', 'noopener,noreferrer');
      }
      showNotice(`Đã bắt đầu học "${course.title}".`);
    } catch (err) {
      const msg = err?.response?.data?.error?.message || 'Không thể tham gia khóa học.';
      alert(msg);
    } finally {
      setCourseBusy(course.course_id, false);
    }
  }

  // 4. Thao tác: Khôi phục khóa học đã bỏ (Gọi PATCH /api/me/courses/{id}/status -> ongoing)
  async function handleRestoreCourse(course) {
    setCourseBusy(course.course_id, true);
    try {
      await updateCourseStatus(course.course_id, 'ongoing');
      setAbandonedCourses((prev) => prev.filter((c) => c.course_id !== course.course_id));
      setOngoingCourses((prev) => [{ ...course, status: 'ongoing', joined_at: new Date().toISOString() }, ...prev]);
      showNotice(`Đã khôi phục "${course.title}" về mục Đang học.`);
    } catch (err) {
      const msg = err?.response?.data?.error?.message || 'Không thể khôi phục khóa học.';
      alert(msg);
    } finally {
      setCourseBusy(course.course_id, false);
    }
  }

  return (
    <div className={styles.pageWrapper}>
      {/* Đèn treo nghệ thuật ấm cúng bên trái */}
      <div className={styles.ambientLamp} aria-hidden="true">
        <div className={styles.lampGlow} />
        <svg width="120" height="340" viewBox="0 0 120 340">
          <line x1="60" y1="0" x2="60" y2="230" stroke="#2b2622" strokeWidth="3" />
          <path d="M32 230h56l20 50H12z" fill="#1b1a19" stroke="#3a342d" />
          <ellipse cx="60" cy="280" rx="48" ry="7" fill="#ffb347" />
          <circle cx="60" cy="287" r="11" fill="#ffd27a" />
          <line x1="82" y1="280" x2="82" y2="332" stroke="#6b5a40" />
          <circle cx="82" cy="336" r="4" fill="var(--accent, #f59e0b)" />
        </svg>
      </div>

      <div className={styles.contentContainer}>
        {/* Tiêu đề trang */}
        <div className={styles.pageHead}>
          <h1 className={styles.heading}>Khóa học của tôi</h1>
          <p className={styles.subheading}>
            Theo dõi khóa học đã lưu, đang học và đã hoàn thành.
          </p>
        </div>

        {/* Thông báo thao tác (nếu có) */}
        {actionNotice && (
          <div className={styles.actionNotice} role="status">
            <span>{actionNotice}</span>
            <button
              type="button"
              className={styles.closeNoticeBtn}
              onClick={() => setActionNotice(null)}
              aria-label="Đóng thông báo"
            >
              ✕
            </button>
          </div>
        )}

        {/* Thông báo lỗi khi tải nếu có */}
        {error && (
          <div className={styles.errorBox}>
            <p>{error}</p>
            <button
              type="button"
              className={styles.retryBtn}
              onClick={fetchAllTrackingData}
            >
              Thử lại
            </button>
          </div>
        )}

        {/* Thanh Tab dạng viên thuốc (Pill Tabs) */}
        <div role="tablist" aria-label="Trạng thái khóa học" className={styles.tabsList}>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'ongoing'}
            className={`${styles.tabBtn} ${activeTab === 'ongoing' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('ongoing')}
          >
            Đang học
            <span className={styles.tabCount}>&nbsp;({ongoingCourses.length})</span>
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'bookmarked'}
            className={`${styles.tabBtn} ${activeTab === 'bookmarked' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('bookmarked')}
          >
            Đã lưu
            <span className={styles.tabCount}>&nbsp;({bookmarkedCourses.length})</span>
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'completed'}
            className={`${styles.tabBtn} ${activeTab === 'completed' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('completed')}
          >
            Hoàn thành
            <span className={styles.tabCount}>&nbsp;({completedCourses.length})</span>
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'abandoned'}
            className={`${styles.tabBtn} ${activeTab === 'abandoned' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('abandoned')}
          >
            Đã bỏ
            {abandonedCourses.length > 0 && (
              <span className={styles.tabCount}>&nbsp;({abandonedCourses.length})</span>
            )}
          </button>
        </div>

        {/* Trạng thái Đang tải Skeleton */}
        {loading ? (
          <div className={styles.cardContainer}>
            <div className={styles.skeletonList}>
              <div className={styles.skeletonItem} />
              <div className={styles.skeletonItem} />
              <div className={styles.skeletonItem} />
            </div>
          </div>
        ) : (
          <>
            {/* ===================== KHỐI 1: KHÓA HỌC ĐANG HỌC ===================== */}
            {activeTab === 'ongoing' && (
              <div className={styles.sectionBlock}>
                <div className={styles.cardContainer}>
                  {ongoingCourses.length === 0 ? (
                    <div className={styles.emptyState}>
                      <p>Bạn chưa tham gia khóa học nào.</p>
                      <p className={styles.emptyHint}>
                        Hãy chọn một khóa học từ danh mục hoặc danh sách đã lưu để bắt đầu học ngay!
                      </p>
                      <Link to="/courses" className={styles.browseLink}>
                        Khám phá danh mục khóa học →
                      </Link>
                    </div>
                  ) : (
                    <div className={styles.itemsList}>
                      {ongoingCourses.map((c) => (
                        <div key={c.course_id} className={styles.courseItem}>
                          <div className={styles.itemInfo}>
                            <h3 className={styles.courseTitle}>
                              <button
                                type="button"
                                className={styles.courseTitleBtn}
                                onClick={() => setSelectedCourse(c)}
                                title="Bấm để xem chi tiết khóa học"
                              >
                                {c.title}
                              </button>
                            </h3>
                            <p className={styles.courseMeta}>
                              [{c.organization || 'Coursera'}] · Kỹ năng: {getSkillsText(c.skills_info)} · Tham gia {formatDate(c.joined_at || c.created_at)}
                            </p>
                          </div>

                          <div className={styles.itemActions}>
                            <span className={styles.ongoingBadge}>Đang học</span>
                            {c.url && (
                              <a
                                href={c.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={styles.openMoocBtn}
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
                            <button
                              type="button"
                              className={styles.abandonBtn}
                              disabled={busyIds.has(c.course_id)}
                              onClick={() => handleAbandonCourse(c)}
                            >
                              Ngừng theo dõi
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ===================== KHỐI 2: ĐÃ LƯU ĐỂ HỌC SAU ===================== */}
            {(activeTab === 'ongoing' || activeTab === 'bookmarked') && (
              <section className={styles.bookmarkSection}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>Đã lưu để học sau</h2>
                  <p className={styles.sectionDesc}>
                    Bỏ lưu chỉ xóa khỏi danh sách đã lưu, không chuyển sang Đã bỏ.
                  </p>
                </div>

                <div className={styles.cardContainer}>
                  {bookmarkedCourses.length === 0 ? (
                    <div className={styles.emptyState}>
                      <p>Bạn chưa lưu khóa học nào để học sau.</p>
                      <Link to="/courses" className={styles.browseLink}>
                        Tìm kiếm và lưu khóa học →
                      </Link>
                    </div>
                  ) : (
                    <div className={styles.itemsList}>
                      {bookmarkedCourses.map((c) => (
                        <div key={c.course_id} className={styles.courseItem}>
                          <div className={styles.itemInfo}>
                            <h3 className={styles.courseTitle}>
                              <button
                                type="button"
                                className={styles.courseTitleBtn}
                                onClick={() => setSelectedCourse(c)}
                                title="Bấm để xem chi tiết khóa học"
                              >
                                {c.title}
                              </button>
                            </h3>
                            <p className={styles.courseMeta}>
                              [{c.organization || 'Coursera'}]
                              {c.rating != null ? ` · ★ ${Number(c.rating).toFixed(1)}` : ''}
                              {` · Lưu ${formatDate(c.created_at)}`}
                            </p>
                          </div>

                          <div className={styles.itemActions}>
                            <span className={styles.bookmarkedBadge}>Đã lưu</span>
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
                              className={styles.removeBookmarkBtn}
                              disabled={busyIds.has(c.course_id)}
                              onClick={() => handleRemoveBookmark(c)}
                            >
                              Bỏ lưu
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* ===================== KHỐI 3: HOÀN THÀNH ===================== */}
            {activeTab === 'completed' && (
              <div className={styles.sectionBlock}>
                <div className={styles.cardContainer}>
                  {completedCourses.length === 0 ? (
                    <div className={styles.emptyState}>
                      <p>Bạn chưa hoàn thành khóa học nào.</p>
                      <p className={styles.emptyHint}>
                        Khóa học sẽ được đánh dấu Hoàn thành sau khi bạn đạt bài ôn tập tối thiểu 70%.
                      </p>
                    </div>
                  ) : (
                    <div className={styles.itemsList}>
                      {completedCourses.map((c) => (
                        <div key={c.course_id} className={styles.courseItem}>
                          <div className={styles.itemInfo}>
                            <h3 className={styles.courseTitle}>
                              <button
                                type="button"
                                className={styles.courseTitleBtn}
                                onClick={() => setSelectedCourse(c)}
                                title="Bấm để xem chi tiết khóa học"
                              >
                                {c.title}
                              </button>
                            </h3>
                            <p className={styles.courseMeta}>
                              [{c.organization || 'Coursera'}] · Hoàn thành ngày {formatDate(c.completed_at || c.updated_at)}
                            </p>
                          </div>

                          <div className={styles.itemActions}>
                            <span className={styles.completedBadge}>✓ Hoàn thành</span>
                            {c.url && (
                              <a
                                href={c.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={styles.openMoocBtn}
                              >
                                Xem lại MOOC ↗
                              </a>
                            )}
                            <Link
                              to={`/courses/${c.course_id}/review`}
                              className={styles.reviewBtn}
                            >
                              Ôn tập lại
                            </Link>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ===================== KHỐI 4: ĐÃ BỎ (ABANDONED) ===================== */}
            {activeTab === 'abandoned' && (
              <div className={styles.sectionBlock}>
                <div className={styles.cardContainer}>
                  {abandonedCourses.length === 0 ? (
                    <div className={styles.emptyState}>
                      <p>Không có khóa học nào trong danh sách Đã bỏ.</p>
                      <p className={styles.emptyHint}>
                        Khi bạn bấm "Ngừng theo dõi" ở một khóa đang học, khóa đó sẽ được lưu tại đây.
                      </p>
                    </div>
                  ) : (
                    <div className={styles.itemsList}>
                      {abandonedCourses.map((c) => (
                        <div key={c.course_id} className={styles.courseItem}>
                          <div className={styles.itemInfo}>
                            <h3 className={styles.courseTitle}>
                              <button
                                type="button"
                                className={styles.courseTitleBtn}
                                onClick={() => setSelectedCourse(c)}
                                title="Bấm để xem chi tiết khóa học"
                              >
                                {c.title}
                              </button>
                            </h3>
                            <p className={styles.courseMeta}>
                              [{c.organization || 'Coursera'}] · Ngừng theo dõi ngày {formatDate(c.updated_at)}
                            </p>
                          </div>

                          <div className={styles.itemActions}>
                            <span className={styles.abandonedBadge}>Đã bỏ</span>
                            <button
                              type="button"
                              className={styles.joinBtn}
                              disabled={busyIds.has(c.course_id)}
                              onClick={() => handleRestoreCourse(c)}
                            >
                              Học lại
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Hộp thoại chi tiết khóa học đồng bộ như trang Danh mục khóa học */}
      {selectedCourse && (
        <CourseDetailModal
          course={selectedCourse}
          isBookmarked={bookmarkedCourses.some((c) => c.course_id === selectedCourse.course_id)}
          isOngoing={ongoingCourses.some((c) => c.course_id === selectedCourse.course_id)}
          isCompleted={completedCourses.some((c) => c.course_id === selectedCourse.course_id)}
          onToggleBookmark={async (courseId) => {
            const isSaved = bookmarkedCourses.some((c) => c.course_id === courseId);
            if (isSaved) {
              await handleRemoveBookmark(selectedCourse);
            } else {
              try {
                await addBookmark(courseId);
                setBookmarkedCourses((prev) => [selectedCourse, ...prev]);
                showNotice(`Đã lưu "${selectedCourse.title}" vào mục học sau.`);
              } catch (err) {
                const msg = err?.response?.data?.detail || 'Không thể lưu khóa học.';
                showNotice(msg);
              }
            }
          }}
          onJoinCourse={async () => {
            await handleJoinFromBookmark(selectedCourse);
          }}
          onClose={() => setSelectedCourse(null)}
        />
      )}
    </div>
  );
}
