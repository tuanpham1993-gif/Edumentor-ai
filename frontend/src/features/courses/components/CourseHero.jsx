// Component Hero đầu trang Khóa học với 2 chiếc đèn treo nghệ thuật & Ô tìm kiếm
// Tái tạo chuẩn visual từ prototype docs/EduMentor-UI-design/ui-design/html/Courses.html.
import { useEffect, useState } from 'react';

import styles from '../styles/CoursesPage.module.css';

function SearchIcon() {
  return (
    <svg
      aria-hidden="true"
      width={20}
      height={20}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      className={styles.searchIcon}
    >
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" />
    </svg>
  );
}

export default function CourseHero({ searchValue = '', onSearchChange }) {
  const [localSearch, setLocalSearch] = useState(searchValue);

  // Đồng bộ giá trị nếu prop từ ngoài đổi
  useEffect(() => {
    setLocalSearch(searchValue);
  }, [searchValue]);

  // Debounce 300ms khi gõ tìm kiếm để không spam API
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localSearch !== searchValue) {
        onSearchChange?.(localSearch);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [localSearch, searchValue, onSearchChange]);

  return (
    <section className={styles.hero}>
      {/* 1. Chiếc đèn treo bên trái */}
      <div className={`${styles.lamp} ${styles.lampLeft}`} aria-hidden="true">
        <div className={styles.glow} style={{ top: '30px' }} />
        <svg width="120" height="290" viewBox="0 0 120 290">
          <line x1="60" y1="0" x2="60" y2="180" stroke="#2b2622" strokeWidth="3" />
          <path d="M32 180h56l20 50H12z" fill="#1b1a19" stroke="#3a342d" />
          <ellipse cx="60" cy="230" rx="48" ry="7" fill="#ffb347" />
          <circle cx="60" cy="237" r="11" fill="#ffd27a" />
          <line x1="82" y1="230" x2="82" y2="282" stroke="#6b5a40" />
          <circle cx="82" cy="286" r="4" fill="var(--accent)" />
        </svg>
      </div>

      {/* 2. Chiếc đèn treo bên phải */}
      <div className={`${styles.lamp} ${styles.lampRight}`} aria-hidden="true">
        <div className={styles.glow} style={{ top: '-30px' }} />
        <svg width="120" height="230" viewBox="0 0 120 230">
          <line x1="60" y1="0" x2="60" y2="120" stroke="#2b2622" strokeWidth="3" />
          <path d="M32 120h56l20 50H12z" fill="#1b1a19" stroke="#3a342d" />
          <ellipse cx="60" cy="170" rx="48" ry="7" fill="#ffb347" />
          <circle cx="60" cy="177" r="11" fill="#ffd27a" />
          <line x1="38" y1="170" x2="38" y2="222" stroke="#6b5a40" />
          <circle cx="38" cy="226" r="4" fill="var(--accent)" />
        </svg>
      </div>

      {/* 3. Nội dung trung tâm */}
      <div className={styles.heroInner}>
        <h1 className={styles.heading}>
          Tìm khóa học <span>phù hợp với bạn</span>
        </h1>
        <p className={styles.sub}>
          Khóa học từ các nền tảng MOOC bên ngoài, lọc theo kỹ năng và cấp độ.
        </p>

        {/* Ô tìm kiếm lớn */}
        <label className={styles.search}>
          <span className="sr-only">Tìm khóa học</span>
          <SearchIcon />
          <input
            type="search"
            placeholder="Tìm theo tên khóa học hoặc từ khóa"
            value={localSearch}
            onChange={(e) => setLocalSearch(e.target.value)}
          />
          {localSearch && (
            <button
              type="button"
              className={styles.clearSearchBtn}
              onClick={() => {
                setLocalSearch('');
                onSearchChange?.('');
              }}
              aria-label="Xóa tìm kiếm"
            >
              ×
            </button>
          )}
        </label>
      </div>
    </section>
  );
}
