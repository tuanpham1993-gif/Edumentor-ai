// Component Searchable Combobox chọn Kỹ năng cho bộ lọc khóa học
// Tương thích 100% Theme Tối / Sáng, không dùng thư viện ngoài.
import { useEffect, useRef, useState } from 'react';

import { getSkills } from '../../../api/courses.api.js';
import styles from '../styles/SkillSelect.module.css';

function SearchIcon() {
  return (
    <svg
      aria-hidden="true"
      width={16}
      height={16}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      className={styles.searchIcon}
    >
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" />
    </svg>
  );
}

function ClearIcon() {
  return (
    <svg
      aria-hidden="true"
      width={14}
      height={14}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2.2}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

function ChevronIcon({ open }) {
  return (
    <svg
      aria-hidden="true"
      width={16}
      height={16}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`${styles.chevronIcon} ${open ? styles.chevronOpen : ''}`}
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg
      aria-hidden="true"
      width={16}
      height={16}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2.4}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={styles.checkIcon}
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

export default function SkillSelect({ selectedSkill, onSkillChange }) {
  const [isOpen, setIsOpen] = useState(false);
  const [keyword, setKeyword] = useState('');
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(false);

  const containerRef = useRef(null);
  const searchInputRef = useRef(null);

  // Đóng khi click ngoài component
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Đóng bằng phím Escape
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  // Focus ô tìm kiếm khi mở popup
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        searchInputRef.current?.focus();
      }, 50);
    } else {
      setKeyword('');
    }
  }, [isOpen]);

  // Tìm kiếm kỹ năng theo keyword với debounce 250ms
  useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;
    setLoading(true);

    const timer = setTimeout(async () => {
      try {
        const res = await getSkills({
          keyword: keyword.trim() || undefined,
          limit: 35,
        });
        if (isMounted) {
          setSkills(res.data || []);
        }
      } catch {
        if (isMounted) {
          setSkills([]);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }, 250);

    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, [keyword, isOpen]);

  const handleSelect = (skillObj) => {
    onSkillChange?.(skillObj);
    setIsOpen(false);
  };

  const handleClear = (e) => {
    e.stopPropagation();
    onSkillChange?.(null);
  };

  return (
    <div className={styles.container} ref={containerRef}>
      {/* Nút bấm mở dropdown */}
      <button
        type="button"
        className={`${styles.trigger} ${selectedSkill ? styles.triggerActive : ''} ${
          isOpen ? styles.triggerOpen : ''
        }`}
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <span className={styles.triggerContent}>
          {selectedSkill ? (
            <span className={styles.selectedBadge} title={selectedSkill.skill}>
              {selectedSkill.skill}
            </span>
          ) : (
            <span className={styles.placeholder}>Tất cả kỹ năng</span>
          )}
        </span>

        <span className={styles.triggerActions}>
          {selectedSkill && (
            <span
              role="button"
              tabIndex={0}
              className={styles.clearBtn}
              onClick={handleClear}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleClear(e);
                }
              }}
              title="Xóa lọc kỹ năng"
              aria-label="Xóa lọc kỹ năng"
            >
              <ClearIcon />
            </span>
          )}
          <ChevronIcon open={isOpen} />
        </span>
      </button>

      {/* Popup Menu */}
      {isOpen && (
        <div className={styles.dropdown} role="listbox">
          {/* Ô gõ tìm kiếm kỹ năng */}
          <div className={styles.searchBox}>
            <SearchIcon />
            <input
              ref={searchInputRef}
              type="text"
              className={styles.searchInput}
              placeholder="Gõ để tìm kỹ năng..."
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              aria-label="Tìm kỹ năng"
            />
          </div>

          {/* Danh sách kỹ năng */}
          <div className={styles.optionsList}>
            {/* Lựa chọn 'Tất cả kỹ năng' */}
            <button
              type="button"
              className={`${styles.optionItem} ${!selectedSkill ? styles.optionSelected : ''}`}
              onClick={() => handleSelect(null)}
              role="option"
              aria-selected={!selectedSkill}
            >
              <span>Tất cả kỹ năng</span>
              {!selectedSkill && <CheckIcon />}
            </button>

            {loading ? (
              <div className={styles.statusMessage}>Đang tải danh sách kỹ năng...</div>
            ) : skills.length === 0 ? (
              <div className={styles.statusMessage}>Không tìm thấy kỹ năng phù hợp</div>
            ) : (
              skills.map((s) => {
                const isSelected = selectedSkill?.skill_id === s.skill_id;
                return (
                  <button
                    key={s.skill_id}
                    type="button"
                    className={`${styles.optionItem} ${isSelected ? styles.optionSelected : ''}`}
                    onClick={() => handleSelect(s)}
                    role="option"
                    aria-selected={isSelected}
                  >
                    <span>{s.skill}</span>
                    {isSelected && <CheckIcon />}
                  </button>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
