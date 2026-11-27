import { useCallback, useEffect, useState } from 'react';
import PathCard2 from '../components/PathCard2.jsx';
import CreatePathModal from '../components/CreatePathModal.jsx';
import ProfileModal from '../components/ProfileModal.jsx';
import LearningPathPagination from '../../learning_path/components/LearningPathPagination';
import { getMyLearningPaths } from '../../../api/learningPaths.api';
import styles from '../styles/PathPages2.module.css';

const LIMIT = 9;
const FILTERS = [
  ['all', 'Tất cả'],
  ['ongoing', 'Đang theo'],
  ['completed', 'Hoàn thành'],
  ['abandoned', 'Đã bỏ'],
];

export default function MyLearningPaths2Page() {
  const [paths, setPaths] = useState([]);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState('all');
  const [keyword, setKeyword] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [profileOf, setProfileOf] = useState(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const res = await getMyLearningPaths({
        skip: (page - 1) * LIMIT, limit: LIMIT,
        status: filter === 'all' ? '' : filter,
        keyword: search || undefined,
      });
      setPaths(res.data);
      setTotal(res.total);
    } catch {
      setError('Không tải được danh sách lộ trình. Vui lòng thử lại.');
    } finally {
      setIsLoading(false);
    }
  }, [page, filter, search]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    const t = setTimeout(() => { setSearch(keyword.trim()); setPage(1); }, 350);
    return () => clearTimeout(t);
  }, [keyword]);

  const totalPages = Math.ceil(total / LIMIT);
  const isEmpty = !isLoading && !error && total === 0 && filter === 'all' && !search;

  return (
    <main className={styles.page}>
      <header className={styles.hero}>
        <div>
          <span className={styles.eyebrow}>✦ Lộ trình học cá nhân</span>
          <h1>Lộ trình của tôi</h1>
          <p>AI đọc mục tiêu và hồ sơ của bạn, dựng đồ thị kỹ năng và bỏ qua những gì bạn đã biết.</p>
        </div>
        <button type="button" className={`btn btn-primary btn-lg ${styles.heroButton}`} onClick={() => setIsCreateOpen(true)}>
          ＋ Tạo lộ trình với AI
        </button>
      </header>

      {!isEmpty && (
        <div className={styles.toolbar}>
          <nav className={styles.segmented} aria-label="Lọc lộ trình">
            {FILTERS.map(([value, text]) => (
              <button key={value} type="button" aria-pressed={filter === value}
                className={filter === value ? styles.segActive : ''}
                onClick={() => { setFilter(value); setPage(1); }}>
                {text}
              </button>
            ))}
          </nav>
          <input className={styles.search} type="search" placeholder="Tìm theo mục tiêu…" value={keyword}
            onChange={(e) => setKeyword(e.target.value)} aria-label="Tìm lộ trình" />
        </div>
      )}

      {isLoading && (
        <section className={styles.grid} aria-busy="true">
          {Array.from({ length: 3 }, (_, i) => <div key={i} className={styles.skeleton} />)}
        </section>
      )}

      {!isLoading && error && (
        <div className={styles.errorBox} role="alert">
          <p>{error}</p>
          <button type="button" className="btn btn-primary" onClick={load}>Thử lại</button>
        </div>
      )}

      {isEmpty && (
        <section className={styles.empty}>
          <div className={styles.emptyArt} aria-hidden="true">
            <span /><span /><span />
          </div>
          <h2>Chưa có lộ trình nào</h2>
          <p>Kể cho AI nghe bạn muốn trở thành ai hoặc muốn làm dự án gì. Lộ trình sẽ có trong khoảng một phút.</p>
          <button type="button" className="btn btn-primary btn-lg" onClick={() => setIsCreateOpen(true)}>
            ＋ Tạo lộ trình đầu tiên
          </button>
        </section>
      )}

      {!isLoading && !error && !isEmpty && (
        paths.length ? (
          <section className={styles.grid}>
            {paths.map((p, i) => (
              <PathCard2 key={p.record_id} learningPath={p} index={i} onShowProfile={setProfileOf} />
            ))}
          </section>
        ) : <p className={styles.noResults}>Không có lộ trình nào khớp.</p>
      )}

      {totalPages > 1 && (
        <LearningPathPagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
      )}

      {isCreateOpen && <CreatePathModal onClose={() => setIsCreateOpen(false)} />}
      {profileOf && (
        <ProfileModal recordId={profileOf.record_id} title={profileOf.original_query} onClose={() => setProfileOf(null)} />
      )}
    </main>
  );
}
