
import { useCallback, useEffect, useMemo, useState } from 'react';
import LearningPathCard from '../components/LearningPathCardList';
import LearningPathPagination from '../components/LearningPathPagination';
import MakeLearningPathPage from './MakeLearningPathPage';
import { getMyLearningPaths } from '../../../api/learningPaths.api';

import styles from '../styles/MyLearningPaths.module.css';

const LIMIT = 15; // 22/11: 3 hàng × 5 thẻ mỗi trang (lưới 5 cột)

const FILTERS = [
  { value: 'all', label: 'Tất cả' },
  { value: 'ongoing', label: 'Đang theo' },
  { value: 'completed', label: 'Hoàn thành' },
  { value: 'abandoned', label: 'Đã bỏ' },
];

export default function MyLearningPathsPage() {
  const [learningPaths, setLearningPaths] = useState([]);
  const [activeFilter, setActiveFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const skip = (currentPage - 1) * LIMIT;

  const loadLearningPaths = useCallback(async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await getMyLearningPaths({
        skip, limit: LIMIT,
        status: activeFilter === 'all' ? '' : activeFilter,
      });
      setLearningPaths(response.data);
      setTotal(response.total);
    } 
    catch (err) {
      console.error('Failed to load learning paths:', err);
      setError('Không tải được danh sách lộ trình. Vui lòng thử lại.');
    } 
    finally {
      setIsLoading(false);
    }
  }, [skip, activeFilter]);

  useEffect(() => {
    loadLearningPaths();
  }, [loadLearningPaths]);

  const totalPages = Math.ceil(total / LIMIT);
  const pageSummary = useMemo(() => {
    return learningPaths.reduce(
      (summary, path) => {
        const nodes = path.nodes ?? [];
        const completedCount = nodes.filter(
            (node) => node.is_target === true).length;
        if (path.status === 'completed') {
          summary.completed += 1;
        } else if (path.status === 'abandoned') {
          summary.abandoned += 1;
        } else if (completedCount > 0) {
          summary.ongoing += 1;
        } else {
          summary.notStarted += 1;
        }
        return summary;
      },
      {
        ongoing: 0,
        notStarted: 0,
        completed: 0,
        abandoned: 0,
      }
    );
  }, [learningPaths]);

  function handleFilterChange(filter) {
    setActiveFilter(filter);
    setCurrentPage(1);
  }

  function handlePageChange(page) {
    setCurrentPage(page);
  }

  function handleCreateOpen() {
    setIsCreateOpen(true);
  }

  function handleCreateClose() {
    setIsCreateOpen(false);
  }

  return (
    <>
    <main className={styles.pageLearningPaths}>
      <div className={styles.containerLearningPaths}>

        {/* Page heading */}
        <header className={styles.headerLearningPaths}>
          <div>
            <h1>Lộ trình của tôi</h1>
            <p>Các lộ trình đã lưu từ những lần tư vấn với AI.</p>
          </div>

          <button type="button"
            className={`btn btn-primary btn-lg ${styles.createButtonLearningPaths}`}
            onClick={handleCreateOpen}>
            <span aria-hidden="true">＋</span>
            Tạo lộ trình mới với AI
          </button>
        </header>

        {/* Loading */}
        {isLoading && (
          <div className={styles.messageLearningPaths}>
            Đang tải lộ trình...
          </div>
        )}

        {/* Error */}
        {!isLoading && error && (
          <div className={styles.errorLearningPaths} role="alert">
            <p>{error}</p>
            <button
              type="button"
              className="btn btn-primary"
              onClick={loadLearningPaths}>
              Thử lại
            </button>
          </div>
        )}

        {/* Empty state */}
        {!isLoading && !error && total === 0 && (
          <section className={styles.emptyLearningPaths}>
            <div className={styles.emptyIconLearningPaths}>
              <span aria-hidden="true">✦</span>
            </div>
            <h2>Chưa có lộ trình nào</h2>
            <p>
              Bạn chưa có lộ trình học nào.
              Nhập mục tiêu để AI tạo lộ trình cho bạn ngay!
            </p>
            <button
              type="button"
              className="btn btn-primary btn-lg"
              onClick={handleCreateOpen}>
              ＋ Tạo lộ trình đầu tiên
            </button>
          </section>
        )}

        {/* Learning paths */}
        {!isLoading && !error && total > 0 && (
          <>
            <nav
              className={styles.filtersLearningPaths}
              aria-label="Lọc lộ trình">
              {FILTERS.map((filter) => {
                const count = filter.value === 'all' ? total : pageSummary[filter.value];
                return (count > 0 && (
                    <button
                      key={filter.value}
                      type="button"
                      className={
                          activeFilter === filter.value?
                          styles.activeFilterLearningPaths:
                          styles.filterLearningPaths}
                      onClick={() => handleFilterChange(filter.value)}
                      aria-pressed={activeFilter === filter.value}>
                      {filter.label} ({count})
                    </button>)
                  )
                })}
            </nav>

            {learningPaths.length > 0 ? (
              <section
                className={styles.gridLearningPaths}
                key={`${activeFilter}-${currentPage}`} /* đổi bộ lọc / trang → thẻ hiện dần lại */
              >
                {learningPaths.map((path, index) => (
                  <LearningPathCard
                    key={path.record_id}
                    learningPath={path}
                    index={index}
                  />
                ))}
              </section>
            ) : (
              <div className={styles.noResultsLearningPaths}>
                Không có lộ trình nào ở mục này.
              </div>
            )}

            <LearningPathPagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          </>
        )}

      </div>
    </main>
    {/* Reuse the existing AI creation flow */}
      {isCreateOpen && (
        <MakeLearningPathPage
          onClose={handleCreateClose}
        />
      )}
    </>
  );

}
