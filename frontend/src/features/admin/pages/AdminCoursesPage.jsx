// Trang Quản trị khóa học (/admin/courses) — F11
import React, { useState, useEffect, useCallback } from 'react';
import { adminApi } from '../../../api/admin.api.js';
import Pagination from '../../common/components/Pagination.jsx';
import AdminCourseDrawer from '../components/AdminCourseDrawer.jsx';
import AdminCourseDetailModal from '../components/AdminCourseDetailModal.jsx';
import styles from '../styles/AdminCourses.module.css';

function formatLevel(lvl) {
  if (!lvl) return 'Chưa phân cấp';
  const lower = lvl.toLowerCase();
  if (lower === 'beginner') return 'Cơ bản';
  if (lower === 'intermediate') return 'Trung cấp';
  if (lower === 'advanced') return 'Nâng cao';
  return lvl;
}

export default function AdminCoursesPage() {
  const [courses, setCourses] = useState([]);
  const [totalCourses, setTotalCourses] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [allSkills, setAllSkills] = useState([]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState(null);

  // Modal xem chi tiết khóa học
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [selectedCourseForDetail, setSelectedCourseForDetail] = useState(null);

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchInput.trim());
      setPage(1); // Reset về trang 1 khi đổi từ khóa tìm kiếm
    }, 350);
    return () => clearTimeout(timer);
  }, [searchInput]);

  // Tải danh sách kỹ năng cho dropdown của drawer
  useEffect(() => {
    adminApi
      .getSkills({ page: 1, pageSize: 200 })
      .then((res) => {
        if (res && res.items) {
          setAllSkills(res.items);
        }
      })
      .catch((err) => {
        console.error('Lỗi khi tải danh sách kỹ năng:', err);
      });
  }, []);

  // Tải danh sách khóa học từ backend
  const fetchCourses = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminApi.getCourses({
        page,
        pageSize,
        search: debouncedSearch,
      });
      setCourses(data.items || []);
      setTotalCourses(data.total || 0);
    } catch (err) {
      console.error('Lỗi khi tải danh sách khóa học:', err);
      setError('Không thể tải danh sách khóa học từ máy chủ. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  }, [page, debouncedSearch]);

  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);

  function handleOpenCreate() {
    setEditingCourse(null);
    setDrawerOpen(true);
  }

  function handleOpenDetail(course) {
    setSelectedCourseForDetail(course);
    setDetailModalOpen(true);
  }

  async function handleOpenEdit(course) {
    setEditingCourse(course);
    setDrawerOpen(true);
    try {
      const detail = await adminApi.getCourseDetail(course.course_id);
      if (detail) {
        setEditingCourse(detail);
      }
    } catch (err) {
      console.warn('Không thể tải thêm chi tiết khóa học, sử dụng dữ liệu danh sách:', err);
    }
  }

  async function handleDeleteCourse(courseId, title) {
    if (!window.confirm(`Bạn có chắc chắn muốn xóa khóa học "${title}"?`)) {
      return;
    }
    try {
      await adminApi.deleteCourse(courseId);
      if (editingCourse && editingCourse.course_id === courseId) {
        setDrawerOpen(false);
        setEditingCourse(null);
      }
      // Nếu đang ở trang cuối và xóa hết phần tử thì lùi lại 1 trang
      if (courses.length === 1 && page > 1) {
        setPage((prev) => prev - 1);
      } else {
        fetchCourses();
      }
    } catch (err) {
      console.error('Lỗi khi xóa khóa học:', err);
      alert('Không thể xóa khóa học. Vui lòng kiểm tra lại.');
    }
  }

  const totalPages = Math.ceil(totalCourses / pageSize) || 1;

  return (
    <>
      <div className={styles.head}>
        <div style={{ display: 'flex', alignItems: 'baseline' }}>
          <h1>Khóa học</h1>
          {totalCourses > 0 && (
            <span className={styles.totalBadge}>
              ({totalCourses.toLocaleString()} khóa học)
            </span>
          )}
        </div>
        <button type="button" className={styles.addBtn} onClick={handleOpenCreate}>
          <svg
            aria-hidden="true"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 5v14M5 12h14" />
          </svg>
          Thêm khóa học
        </button>
      </div>

      <div className={`${styles.split} ${!drawerOpen ? styles.splitClosed : ''}`}>
        <div className={styles.tableStack}>
          {/* Ô tìm kiếm */}
          <div className={styles.searchBar}>
            <svg
              aria-hidden="true"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
            <input
              className={styles.searchInput}
              placeholder="Tìm khóa học theo tên hoặc đơn vị..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              aria-label="Tìm khóa học"
            />
            {searchInput && (
              <button
                type="button"
                className={styles.chipRemove}
                onClick={() => setSearchInput('')}
                aria-label="Xóa từ khóa tìm kiếm"
              >
                ✕
              </button>
            )}
          </div>

          {/* Báo lỗi nếu có */}
          {error && (
            <div style={{ padding: '12px 16px', background: 'rgba(239, 68, 68, 0.1)', color: '#f87171', borderRadius: '8px', fontSize: '14px' }}>
              {error}
            </div>
          )}

          {/* Bảng danh sách khóa học */}
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th style={{ width: '32%' }}>Khóa học</th>
                  <th style={{ width: '15%' }}>Cấp độ</th>
                  <th style={{ width: '12%' }}>Đánh giá</th>
                  <th style={{ width: '28%' }}>Kỹ năng</th>
                  <th style={{ width: '13%', textAlign: 'right' }}>Thao tác</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="5" style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
                      Đang tải danh sách khóa học...
                    </td>
                  </tr>
                ) : courses.length === 0 ? (
                  <tr>
                    <td colSpan="5" style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
                      {debouncedSearch
                        ? `Không tìm thấy khóa học nào phù hợp với "${debouncedSearch}"`
                        : 'Chưa có khóa học nào trong hệ thống.'}
                    </td>
                  </tr>
                ) : (
                  courses.map((c) => {
                    const isEditingThis = editingCourse && editingCourse.course_id === c.course_id;
                    const skillsList =
                      c.skills_info && c.skills_info.length > 0
                        ? c.skills_info.map((s) => s.skill).join(', ')
                        : 'Chưa gắn kỹ năng';

                    const hasSkills = c.skills_info && c.skills_info.length > 0;

                    return (
                      <tr key={c.course_id} className={isEditingThis ? styles.rowEditing : ''}>
                        <td>
                          <button
                            type="button"
                            className={styles.titleBtn}
                            onClick={() => handleOpenDetail(c)}
                            title="Nhấp để xem chi tiết khóa học"
                          >
                            {c.title}
                          </button>
                          {c.organization ? (
                            <div className={styles.platform}>[{c.organization}]</div>
                          ) : (
                            <div className={styles.platformMuted}>[Chưa cập nhật đơn vị]</div>
                          )}
                        </td>
                        <td>
                          <span className={c.level ? '' : styles.mutedText}>
                            {formatLevel(c.level)}
                          </span>
                        </td>
                        <td className={c.rating != null ? styles.rating : styles.ratingEmpty}>
                          {c.rating != null ? `★ ${Number(c.rating).toFixed(1)}` : 'Chưa có đánh giá'}
                        </td>
                        <td className={styles.skillsText}>
                          {hasSkills ? (
                            c.skills_info.map((s) => s.skill).join(', ')
                          ) : (
                            <span className={styles.mutedText}>Chưa gắn kỹ năng</span>
                          )}
                        </td>
                        <td>
                          <div className={styles.actions}>
                            <button
                              type="button"
                              className={styles.iconBtn}
                              aria-label={`Sửa ${c.title}`}
                              onClick={() => handleOpenEdit(c)}
                            >
                              <svg
                                aria-hidden="true"
                                width="16"
                                height="16"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="1.8"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                              >
                                <path d="M4 20h4L19 9l-4-4L4 16zM14 6l4 4" />
                              </svg>
                            </button>
                            <button
                              type="button"
                              className={`${styles.iconBtn} ${styles.deleteBtn}`}
                              aria-label={`Xóa ${c.title}`}
                              onClick={() => handleDeleteCourse(c.course_id, c.title)}
                            >
                              <svg
                                aria-hidden="true"
                                width="16"
                                height="16"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="1.8"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                              >
                                <path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13" />
                              </svg>
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Phân trang */}
          {!loading && totalPages > 1 && (
            <div className={styles.paginationWrap}>
              <Pagination
                page={page}
                totalPages={totalPages}
                onChange={(newPage) => setPage(newPage)}
                label="Phân trang danh sách khóa học"
              />
            </div>
          )}
        </div>

        {/* Drawer bên phải thêm/sửa */}
        <AdminCourseDrawer
          course={editingCourse}
          allSkills={allSkills}
          isOpen={drawerOpen}
          onClose={() => {
            setDrawerOpen(false);
            setEditingCourse(null);
          }}
          onSaved={fetchCourses}
        />
      </div>

      {/* Modal xem chi tiết khóa học */}
      <AdminCourseDetailModal
        course={selectedCourseForDetail}
        isOpen={detailModalOpen}
        onClose={() => {
          setDetailModalOpen(false);
          setSelectedCourseForDetail(null);
        }}
        onEdit={(courseToEdit) => {
          setDetailModalOpen(false);
          handleOpenEdit(courseToEdit);
        }}
        onDelete={(courseId, title) => {
          handleDeleteCourse(courseId, title);
        }}
      />
    </>
  );
}
