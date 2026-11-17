// Trang Danh mục khóa học (/courses) dành cho học viên
// Tuân thủ toàn diện thiết kế Mockup và quy chuẩn dự án EduMentor AI.
import { useCallback, useEffect, useState } from 'react';

import { getCourses } from '../../../api/courses.api.js';
import {
  addBookmark,
  getMyBookmarks,
  getMyCourses,
  removeBookmark,
} from '../../../api/courseTracking.api.js';
import CourseCard from '../components/CourseCard.jsx';
import CourseDetailModal from '../components/CourseDetailModal.jsx';
import CourseFilters from '../components/CourseFilters.jsx';
import CourseHero from '../components/CourseHero.jsx';
import CourseToast from '../components/CourseToast.jsx';
import { useAuth } from '../../../hooks/useAuth.js';
import styles from '../styles/CoursesPage.module.css';

const PAGE_SIZE = 12;

export default function CoursesPage() {
  const [courses, setCourses] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Bộ lọc
  const [search, setSearch] = useState('');
  const [level, setLevel] = useState('');
  const [sortBy, setSortBy] = useState('rating');
  const [page, setPage] = useState(1);

  // Xác thực người dùng
  const { status: authStatus } = useAuth();

  // Danh sách ID các khóa học đã bookmark, đang học, và đã hoàn thành
  const [bookmarkedIds, setBookmarkedIds] = useState(new Set());
  const [ongoingIds, setOngoingIds] = useState(new Set());
  const [completedIds, setCompletedIds] = useState(new Set());

  // Khóa học đang chọn để xem modal chi tiết
  const [selectedCourse, setSelectedCourse] = useState(null);

  // Thông báo Toast nổi
  const [toast, setToast] = useState(null);

  // 1. Tải danh sách theo dõi (bookmark, đang học, đã hoàn thành) khi học viên đăng nhập
  const fetchUserTracking = useCallback(async () => {
    if (authStatus === 'guest') {
      setBookmarkedIds(new Set());
      setOngoingIds(new Set());
      setCompletedIds(new Set());
      return;
    }

    try {
      const [bookmarksRes, ongoingRes, completedRes] = await Promise.allSettled([
        getMyBookmarks(1, 50),
        getMyCourses({ status: 'ongoing', page_size: 50 }),
        getMyCourses({ status: 'completed', page_size: 50 }),
      ]);

      if (bookmarksRes.status === 'fulfilled' && bookmarksRes.value?.items) {
        setBookmarkedIds(new Set(bookmarksRes.value.items.map((item) => item.course_id)));
      }
      if (ongoingRes.status === 'fulfilled' && ongoingRes.value?.items) {
        setOngoingIds(new Set(ongoingRes.value.items.map((item) => item.course_id)));
      }
      if (completedRes.status === 'fulfilled' && completedRes.value?.items) {
        setCompletedIds(new Set(completedRes.value.items.map((item) => item.course_id)));
      }
    } catch {
      // Khách chưa đăng nhập hoặc lỗi kết nối -> bỏ qua
    }
  }, [authStatus]);

  useEffect(() => {
    fetchUserTracking();
  }, [fetchUserTracking]);

  // 2. Tải danh sách khóa học theo bộ lọc
  const fetchCourses = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getCourses({
        search: search.trim() || undefined,
        level: level || undefined,
        sort_by: sortBy || undefined,
        page,
        page_size: PAGE_SIZE,
      });

      setCourses(res.data || []);
      setTotal(res.total || 0);
    } catch (err) {
      const msg = err?.response?.data?.error?.message || err?.message || 'Không thể tải danh sách khóa học.';
      setError(msg);
      setCourses([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [search, level, sortBy, page]);

  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);

  // Xử lý bật/tắt bookmark (lưu để học sau)
  async function handleToggleBookmark(courseId) {
    const isCurrentlySaved = bookmarkedIds.has(courseId);
    const targetCourse =
      courses.find((c) => c.course_id === courseId) ||
      (selectedCourse?.course_id === courseId ? selectedCourse : null);
    const courseTitle = targetCourse?.title || 'Khóa học';

    // 1. Nếu khóa học đang học -> Không cho lưu bookmark (tránh xung đột), hiển thị hướng dẫn
    if (ongoingIds.has(courseId)) {
      setToast({
        id: Date.now(),
        type: 'info',
        message: 'Khóa học này bạn đang học trong mục Khóa học của tôi rồi!',
        courseTitle: courseTitle,
        actionText: 'Xem khóa học đang học →',
        actionLink: '/me/courses',
      });
      return;
    }

    // 2. Nếu khóa học đã hoàn thành
    if (completedIds.has(courseId)) {
      setToast({
        id: Date.now(),
        type: 'info',
        message: 'Khóa học này bạn đã hoàn thành rồi!',
        courseTitle: courseTitle,
        actionText: 'Xem chứng chỉ / Đánh giá →',
        actionLink: '/me/courses',
      });
      return;
    }

    // Cập nhật giao diện tức thì (optimistic update)
    setBookmarkedIds((prev) => {
      const next = new Set(prev);
      if (isCurrentlySaved) next.delete(courseId);
      else next.add(courseId);
      return next;
    });

    if (!isCurrentlySaved) {
      // Bấm Lưu khóa học -> Hiển thị thông báo đã lưu
      setToast({
        id: Date.now(),
        type: 'success',
        message: 'Đã lưu khóa học vào mục Khóa học của tôi!',
        courseTitle: courseTitle,
        actionText: 'Xem danh sách đã lưu →',
        actionLink: '/me/courses',
      });
    } else {
      // Bấm Bỏ lưu -> Hiển thị thông báo bỏ lưu
      setToast({
        id: Date.now(),
        type: 'info',
        message: 'Đã xóa khóa học khỏi mục đã lưu.',
        courseTitle: courseTitle,
      });
    }

    try {
      if (isCurrentlySaved) {
        await removeBookmark(courseId);
      } else {
        await addBookmark(courseId);
      }
    } catch (err) {
      // Revert lại trạng thái nếu API gặp lỗi
      setBookmarkedIds((prev) => {
        const next = new Set(prev);
        if (isCurrentlySaved) next.add(courseId);
        else next.delete(courseId);
        return next;
      });

      const statusCode = err?.response?.status;
      const detail = err?.response?.data?.detail || '';

      if (statusCode === 409 || detail.includes('đang học') || detail.includes('ongoing')) {
        // Đồng bộ lại trạng thái đang học
        setOngoingIds((prev) => new Set(prev).add(courseId));
        setToast({
          id: Date.now(),
          type: 'info',
          message: 'Khóa học này bạn đang học trong mục Khóa học của tôi rồi.',
          courseTitle: courseTitle,
          actionText: 'Đến trang Khóa học của tôi →',
          actionLink: '/me/courses',
        });
      } else if (statusCode === 401) {
        setToast({
          id: Date.now(),
          type: 'warning',
          message: 'Vui lòng đăng nhập để lưu khóa học!',
          actionText: 'Đăng nhập ngay →',
          actionLink: '/login',
        });
      } else {
        setToast({
          id: Date.now(),
          type: 'error',
          message: 'Không thể cập nhật trạng thái lưu. Vui lòng thử lại!',
        });
      }
    }
  }

  // Khi đổi bộ lọc thì reset về trang 1
  function handleSearchChange(newSearch) {
    setSearch(newSearch);
    setPage(1);
  }

  function handleLevelChange(newLevel) {
    setLevel(newLevel);
    setPage(1);
  }

  function handleSortByChange(newSortBy) {
    setSortBy(newSortBy);
    setPage(1);
  }

  const totalPages = Math.ceil(total / PAGE_SIZE) || 1;

  return (
    <div className={styles.page}>
      {/* 1. Hero với 2 chiếc đèn treo nghệ thuật & Ô tìm kiếm */}
      <CourseHero searchValue={search} onSearchChange={handleSearchChange} />

      {/* 2. Nội dung chính */}
      <main className={styles.main}>
        {/* Thanh bộ lọc & Số lượng khóa học */}
        <CourseFilters
          level={level}
          onLevelChange={handleLevelChange}
          sortBy={sortBy}
          onSortByChange={handleSortByChange}
          total={total}
        />

        {/* Trạng thái 1: Đang tải (Skeletons) */}
        {loading ? (
          <div className={styles.grid}>
            {Array.from({ length: 6 }).map((_, idx) => (
              <div key={idx} className={styles.skeletonCard} aria-hidden="true">
                <div className={`skeleton ${styles.skeletonCover}`} />
                <div className={styles.skeletonBody}>
                  <div className="skeleton" style={{ height: '24px', width: '80%' }} />
                  <div className="skeleton" style={{ height: '16px', width: '40%' }} />
                  <div className="skeleton" style={{ height: '20px', width: '60%', marginTop: 'auto' }} />
                  <div className="skeleton" style={{ height: '40px', width: '100%', marginTop: '8px' }} />
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          /* Trạng thái 2: Lỗi */
          <div className={styles.errorState} role="alert">
            <p><strong>Đã xảy ra lỗi:</strong> {error}</p>
            <button type="button" className="btn btn-sm" onClick={fetchCourses}>
              Thử lại
            </button>
          </div>
        ) : courses.length === 0 ? (
          /* Trạng thái 3: Rỗng */
          <div className={styles.emptyState}>
            <h3>Không tìm thấy khóa học phù hợp</h3>
            <p>
              Hãy thử tìm kiếm với từ khóa khác hoặc bỏ các bộ lọc cấp độ để xem thêm nhiều khóa học.
            </p>
            {(search || level) && (
              <button
                type="button"
                className="btn btn-sm"
                onClick={() => {
                  setSearch('');
                  setLevel('');
                  setPage(1);
                }}
              >
                Đặt lại bộ lọc
              </button>
            )}
          </div>
        ) : (
          /* Trạng thái 4: Danh sách khóa học */
          <>
            <div className={styles.grid}>
              {courses.map((course) => (
                <CourseCard
                  key={course.course_id}
                  course={course}
                  isBookmarked={bookmarkedIds.has(course.course_id)}
                  isOngoing={ongoingIds.has(course.course_id)}
                  isCompleted={completedIds.has(course.course_id)}
                  onToggleBookmark={handleToggleBookmark}
                  onSelectCourse={setSelectedCourse}
                />
              ))}
            </div>

            {/* Phân trang */}
            {totalPages > 1 && (
              <nav className={styles.pagination} aria-label="Phân trang khóa học">
                <button
                  type="button"
                  className={styles.pageBtn}
                  disabled={page <= 1}
                  onClick={() => {
                    setPage((p) => Math.max(1, p - 1));
                    window.scrollTo({ top: 350, behavior: 'smooth' });
                  }}
                  aria-label="Trang trước"
                >
                  ←
                </button>
                <span className={styles.pageInfo}>
                  Trang {page} / {totalPages}
                </span>
                <button
                  type="button"
                  className={styles.pageBtn}
                  disabled={page >= totalPages}
                  onClick={() => {
                    setPage((p) => Math.min(totalPages, p + 1));
                    window.scrollTo({ top: 350, behavior: 'smooth' });
                  }}
                  aria-label="Trang sau"
                >
                  →
                </button>
              </nav>
            )}
          </>
        )}
      </main>

      {/* 3. Modal xem chi tiết khóa học */}
      {selectedCourse && (
        <CourseDetailModal
          course={selectedCourse}
          isBookmarked={bookmarkedIds.has(selectedCourse.course_id)}
          isOngoing={ongoingIds.has(selectedCourse.course_id)}
          isCompleted={completedIds.has(selectedCourse.course_id)}
          onToggleBookmark={handleToggleBookmark}
          onJoinCourse={(courseId) => {
            // Khi đã tham gia học: thêm vào ongoingIds và xóa khỏi bookmarkIds
            setOngoingIds((prev) => new Set(prev).add(courseId));
            setBookmarkedIds((prev) => {
              const next = new Set(prev);
              next.delete(courseId);
              return next;
            });
          }}
          onClose={() => setSelectedCourse(null)}
        />
      )}
      {/* 4. Thông báo Toast nổi tương tác */}
      <CourseToast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}
