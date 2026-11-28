import { useCallback, useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { getRecommendedCoursesBySkill } from '../../../api/courses.api.js';
import { addBookmark, joinCourse, removeBookmark } from '../../../api/courseTracking.api.js';
import { useAuth } from '../../../hooks/useAuth.js';
import CourseDetailModal from '../../courses/components/CourseDetailModal.jsx';
import { getCourseMonogram, getCoursePalette } from '../../courses/components/CourseMonogram.jsx';
import { roleLabel } from '../roleLabels.js';
import styles from '../styles/CourseRecommendation.module.css';

const LEVEL_FILTERS = [
  { key: '', label: 'Tất cả' },
  { key: 'beginner', label: 'Cơ bản' },
  { key: 'intermediate', label: 'Trung cấp' },
  { key: 'advanced', label: 'Nâng cao' },
];

const LEVEL_MAP = {
  beginner: 'Cơ bản',
  intermediate: 'Trung cấp',
  advanced: 'Nâng cao',
};

const SKILL_STATUS_LABELS = {
  known: 'Đã biết',
  learning: 'Đang học',
};

function BookmarkIcon({ filled }) {
  return (
    <svg
      aria-hidden="true"
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill={filled ? 'currentColor' : 'none'}
      stroke="currentColor"
      strokeWidth="2"
      strokeLinejoin="round"
    >
      <path d="M6 3h12v18l-6-4-6 4z" />
    </svg>
  );
}

function ExternalArrowIcon() {
  return (
    <svg
      aria-hidden="true"
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M7 17 17 7" />
      <path d="M8 7h9v9" />
    </svg>
  );
}

export default function CourseRecommendation({ skill, isPreviewMode = false }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { status: authStatus } = useAuth();
  const isAuthenticated = authStatus === 'authenticated';

  const skillId = skill?.skillId ?? skill?.skill_id ?? skill?.id ?? null;
  const skillName = skill?.skillName ?? skill?.skill_name ?? skill?.skill?.skill ?? '';

  const [levelFilter, setLevelFilter] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [actionMsg, setActionMsg] = useState('');
  const [joiningId, setJoiningId] = useState(null);
  const [bookmarkingId, setBookmarkingId] = useState(null);
  const [detailCourse, setDetailCourse] = useState(null);
  const [imgErrors, setImgErrors] = useState({});

  // Reset bộ lọc khi người dùng chuyển sang bấm node kỹ năng khác
  useEffect(() => {
    setLevelFilter('');
    setActionMsg('');
    setDetailCourse(null);
  }, [skillId]);

  const fetchRecommendations = useCallback(async () => {
    if (!skillId) return;
    setLoading(true);
    setError('');
    try {
      const res = await getRecommendedCoursesBySkill({
        skillId,
        level: levelFilter,
        limit: 8,
      });
      setData(res);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          'Không thể tải khóa học gợi ý cho kỹ năng này.'
      );
    } finally {
      setLoading(false);
    }
  }, [skillId, levelFilter]);

  useEffect(() => {
    let active = true;
    if (!skillId) return undefined;

    setLoading(true);
    setError('');
    getRecommendedCoursesBySkill({
      skillId,
      level: levelFilter,
      limit: 8,
    })
      .then((res) => {
        if (active) setData(res);
      })
      .catch((err) => {
        if (active) {
          setError(
            err?.response?.data?.detail ||
              'Không thể tải khóa học gợi ý cho kỹ năng này.'
          );
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [skillId, levelFilter]);

  if (!skill) return null;

  async function handleToggleBookmark(courseId) {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    const target = data?.items?.find((c) => c.course_id === courseId);
    if (!target) return;

    setBookmarkingId(courseId);
    setActionMsg('');
    try {
      if (target.is_bookmarked) {
        await removeBookmark(courseId);
        setData((prev) =>
          prev
            ? {
                ...prev,
                items: prev.items.map((c) =>
                  c.course_id === courseId
                    ? { ...c, is_bookmarked: false, user_status: null }
                    : c
                ),
              }
            : prev
        );
        setActionMsg(`Đã bỏ lưu "${target.title}".`);
      } else {
        await addBookmark(courseId);
        setData((prev) =>
          prev
            ? {
                ...prev,
                items: prev.items.map((c) =>
                  c.course_id === courseId
                    ? {
                        ...c,
                        is_bookmarked: true,
                        user_status:
                          c.user_status === 'ongoing' || c.user_status === 'completed'
                            ? c.user_status
                            : 'bookmarked',
                      }
                    : c
                ),
              }
            : prev
        );
        setActionMsg(`Đã lưu "${target.title}" vào mục học sau.`);
      }
    } catch (err) {
      setActionMsg(
        err?.response?.data?.detail || 'Không thể cập nhật trạng thái lưu khóa học.'
      );
    } finally {
      setBookmarkingId(null);
    }
  }

  async function handleJoinCourse(course) {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: location.pathname } });
      return;
    }
    setJoiningId(course.course_id);
    setActionMsg('');
    try {
      const res = await joinCourse(course.course_id);
      setData((prev) =>
        prev
          ? {
              ...prev,
              items: prev.items.map((c) =>
                c.course_id === course.course_id
                  ? { ...c, is_bookmarked: false, user_status: 'ongoing' }
                  : c
              ),
            }
          : prev
      );
      setActionMsg(`Đã ghi nhận tham gia "${course.title}" vào Khóa học của tôi.`);
      const targetUrl = res?.url || course.url;
      if (targetUrl) {
        window.open(targetUrl, '_blank', 'noopener,noreferrer');
      }
    } catch (err) {
      setActionMsg(
        err?.response?.data?.detail || 'Không thể tham gia khóa học lúc này.'
      );
    } finally {
      setJoiningId(null);
    }
  }

  const items = data?.items || [];
  const totalCount = data?.total ?? 0;
  const skillStatus = data?.user_skill_status;

  return (
    <section className={styles.recommendationContainer} aria-live="polite">
      <header className={styles.recommendationHeader}>
        <div className={styles.headerTopRow}>
          <span className={styles.sectionLabel}>KHÓA HỌC GỢI Ý</span>
          {skillStatus && (
            <span
              className={`${styles.skillStatusBadge} ${
                skillStatus === 'known' ? styles.skillKnown : styles.skillLearning
              }`}
            >
              {SKILL_STATUS_LABELS[skillStatus]}
            </span>
          )}
        </div>

        <h2>{skillName}</h2>

        <p className={styles.headerSub}>
          {skill.nodeRole ? `${roleLabel(skill.nodeRole)} · ` : ''}
          {isPreviewMode
            ? 'Xem trước các khóa học phù hợp trước khi lưu lộ trình.'
            : 'Khóa học xếp hạng theo mức độ liên quan đến kỹ năng này.'}
        </p>

        {/* Bộ lọc nhanh theo cấp độ */}
        <div className={styles.levelFilters} role="group" aria-label="Lọc theo cấp độ">
          {LEVEL_FILTERS.map((lv) => {
            const active = levelFilter === lv.key;
            return (
              <button
                key={lv.key || 'all'}
                type="button"
                aria-pressed={active}
                className={`${styles.levelChip} ${active ? styles.levelChipActive : ''}`}
                onClick={() => setLevelFilter(lv.key)}
              >
                {lv.label}
              </button>
            );
          })}
        </div>
      </header>

      {actionMsg && (
        <div className={styles.actionBanner} role="status">
          {actionMsg}
        </div>
      )}

      <div className={styles.recommendationContent}>
        {!skillId ? (
          <div className={styles.emptyCourses}>
            <h3>Chưa xác định mã kỹ năng</h3>
            <p>Không tìm thấy thông tin kỹ năng để truy xuất khóa học.</p>
          </div>
        ) : loading ? (
          <div className={styles.skeletonList} aria-busy="true">
            {[1, 2, 3].map((n) => (
              <div key={n} className={styles.skeletonCard} />
            ))}
          </div>
        ) : error ? (
          <div className={styles.errorBox} role="alert">
            <p>{error}</p>
            <button type="button" className={styles.retryBtn} onClick={fetchRecommendations}>
              Thử lại
            </button>
          </div>
        ) : items.length === 0 ? (
          <div className={styles.emptyCourses}>
            <h3>Chưa có khóa học phù hợp</h3>
            <p>
              {levelFilter
                ? `Không có khóa học cấp độ ${LEVEL_MAP[levelFilter]} cho "${skillName}".`
                : `Chưa có khóa học liên kết trực tiếp với kỹ năng "${skillName}".`}
            </p>
            <div className={styles.emptyActions}>
              {levelFilter && (
                <button
                  type="button"
                  className={styles.retryBtn}
                  onClick={() => setLevelFilter('')}
                >
                  Xem mọi cấp độ
                </button>
              )}
              <Link to="/courses" className={styles.browseLink}>
                Khám phá danh mục khóa học
              </Link>
            </div>
          </div>
        ) : (
          <>
            <div className={styles.resultMeta}>
              Tìm thấy <strong>{totalCount}</strong> khóa học phù hợp
              {items[0]?.match_type === 'keyword_fallback' && ' (theo từ khóa kỹ năng)'}
            </div>

            <div className={styles.courseList}>
              {items.map((course) => {
                const palette = getCoursePalette(course.course_id, course.title);
                const monogram = getCourseMonogram(course.title);
                const showImage = course.image && !imgErrors[course.course_id];
                const levelText =
                  LEVEL_MAP[course.level?.toLowerCase()] || course.level || 'Mọi cấp độ';
                const isOngoing = course.user_status === 'ongoing';
                const isCompleted = course.user_status === 'completed';

                return (
                  <article key={course.course_id} className={styles.courseCard}>
                    <div className={styles.cardMain}>
                      <div
                        className={styles.thumbBox}
                        style={{
                          background: palette.base,
                          color: palette.ink,
                        }}
                      >
                        {showImage ? (
                          <img
                            src={course.image}
                            alt=""
                            className={styles.thumbImg}
                            onError={() =>
                              setImgErrors((prev) => ({
                                ...prev,
                                [course.course_id]: true,
                              }))
                            }
                          />
                        ) : (
                          <span className={styles.monogramText}>{monogram}</span>
                        )}
                      </div>

                      <div className={styles.cardInfo}>
                        <div className={styles.cardBadges}>
                          <span className={styles.levelBadge}>{levelText}</span>
                          {isCompleted ? (
                            <span className={styles.statusCompleted}>Hoàn thành</span>
                          ) : isOngoing ? (
                            <span className={styles.statusOngoing}>Đang học</span>
                          ) : null}
                        </div>

                        <h3 className={styles.courseTitle} title={course.title}>
                          {course.title}
                        </h3>

                        <div className={styles.courseMetaLine}>
                          <span>{course.organization || 'EduMentor Partner'}</span>
                          {course.rating != null && (
                            <span className={styles.ratingMeta}>
                              ★ {Number(course.rating).toFixed(1)}
                              {course.num_reviews > 0 &&
                                ` (${Number(course.num_reviews).toLocaleString('vi-VN')})`}
                            </span>
                          )}
                        </div>

                        <div className={styles.relevanceReason}>
                          {course.relevance_reason}
                        </div>
                      </div>
                    </div>

                    <div className={styles.cardActions}>
                      <button
                        type="button"
                        className={styles.detailBtn}
                        onClick={() => {
                          if (!isAuthenticated) {
                            navigate('/login', { state: { from: location.pathname } });
                            return;
                          }
                          setDetailCourse(course);
                        }}
                      >
                        Chi tiết
                      </button>

                      {!isOngoing && !isCompleted && (
                        <button
                          type="button"
                          className={`${styles.bookmarkBtn} ${
                            course.is_bookmarked ? styles.bookmarkBtnActive : ''
                          }`}
                          disabled={bookmarkingId === course.course_id}
                          onClick={() => handleToggleBookmark(course.course_id)}
                          aria-label={
                            course.is_bookmarked ? 'Bỏ lưu khóa học' : 'Lưu khóa học'
                          }
                          title={course.is_bookmarked ? 'Đã lưu' : 'Lưu để học sau'}
                        >
                          <BookmarkIcon filled={course.is_bookmarked} />
                        </button>
                      )}

                      <button
                        type="button"
                        className={styles.joinBtn}
                        disabled={joiningId === course.course_id}
                        onClick={() => handleJoinCourse(course)}
                      >
                        {joiningId === course.course_id
                          ? 'Đang mở...'
                          : isOngoing
                          ? 'Tiếp tục'
                          : 'Học ngay'}
                        <ExternalArrowIcon />
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>
          </>
        )}
      </div>

      {detailCourse && (
        <CourseDetailModal
          course={detailCourse}
          isBookmarked={detailCourse.is_bookmarked}
          isOngoing={detailCourse.user_status === 'ongoing'}
          isCompleted={detailCourse.user_status === 'completed'}
          onToggleBookmark={(cid) => handleToggleBookmark(cid)}
          onJoinCourse={() => handleJoinCourse(detailCourse)}
          onClose={() => setDetailCourse(null)}
        />
      )}
    </section>
  );
}
