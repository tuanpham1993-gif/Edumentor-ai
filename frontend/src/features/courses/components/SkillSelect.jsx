// Component Searchable Combobox chọn Kỹ năng cho bộ lọc khóa học.
// Ưu tiên kỹ năng phổ biến nhất (nhiều khóa học nhất) kèm số khóa học,
// hỗ trợ tải thêm, điều hướng bàn phím (↑/↓/Enter/Escape) và tương thích Theme Tối / Sáng.
import { useCallback, useEffect, useId, useRef, useState } from 'react';

import { getPopularSkills } from '../../../api/courses.api.js';
import { parseApiError } from '../../../utils/errors.js';
import styles from '../styles/SkillSelect.module.css';

const PAGE_SIZE = 60;

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
  const listboxId = useId();
  const [isOpen, setIsOpen] = useState(false);
  const [keyword, setKeyword] = useState('');
  const [skills, setSkills] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(-1);

  const containerRef = useRef(null);
  const triggerRef = useRef(null);
  const searchInputRef = useRef(null);
  const optionRefs = useRef([]);
  const popularCacheRef = useRef(null);
  const requestIdRef = useRef(0);

  const closeDropdown = useCallback((returnFocus = false) => {
    setIsOpen(false);
    setHighlightedIndex(-1);
    if (returnFocus) {
      requestAnimationFrame(() => triggerRef.current?.focus());
    }
  }, []);

  // Đóng khi click ngoài component
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        closeDropdown(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, closeDropdown]);

  // Focus ô tìm kiếm khi mở popup; reset từ khóa khi đóng
  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => {
        searchInputRef.current?.focus();
      }, 30);
      return () => clearTimeout(timer);
    }
    setKeyword('');
    setError('');
    setHighlightedIndex(-1);
    return undefined;
  }, [isOpen]);

  // Tải danh sách kỹ năng phổ biến / kết quả tìm kiếm
  const fetchSkillsPage = useCallback(async (searchText, targetPage = 1, append = false) => {
    const trimmed = searchText.trim();
    const reqId = ++requestIdRef.current;

    // Dùng cache trang đầu kỹ năng phổ biến để mở dropdown tức thì
    if (!trimmed && targetPage === 1 && !append && popularCacheRef.current) {
      setSkills(popularCacheRef.current.items);
      setTotal(popularCacheRef.current.total);
      setPage(1);
      setError('');
      setLoading(false);
      return;
    }

    if (append) {
      setLoadingMore(true);
    } else {
      setLoading(true);
      setError('');
    }

    try {
      const res = await getPopularSkills({
        keyword: trimmed,
        page: targetPage,
        size: PAGE_SIZE,
      });

      if (reqId !== requestIdRef.current) return;

      const nextItems = res.items || [];
      setTotal(res.total ?? nextItems.length);
      setPage(targetPage);

      if (append) {
        setSkills((prev) => {
          const seen = new Set(prev.map((item) => item.skill_id));
          const merged = [...prev];
          for (const item of nextItems) {
            if (!seen.has(item.skill_id)) {
              seen.add(item.skill_id);
              merged.push(item);
            }
          }
          return merged;
        });
      } else {
        setSkills(nextItems);
        setHighlightedIndex(-1);
        if (!trimmed && targetPage === 1) {
          popularCacheRef.current = { items: nextItems, total: res.total ?? nextItems.length };
        }
      }
    } catch (err) {
      if (reqId !== requestIdRef.current) return;
      const parsed = parseApiError(err);
      setError(parsed.message || 'Không thể tải danh sách kỹ năng.');
      if (!append) {
        setSkills([]);
        setTotal(0);
      }
    } finally {
      if (reqId === requestIdRef.current) {
        setLoading(false);
        setLoadingMore(false);
      }
    }
  }, []);

  // Gọi API khi mở dropdown hoặc đổi từ khóa (debounce 250ms khi gõ)
  useEffect(() => {
    if (!isOpen) return undefined;

    const trimmed = keyword.trim();
    if (!trimmed && popularCacheRef.current) {
      fetchSkillsPage('', 1, false);
      return undefined;
    }

    const delay = trimmed ? 250 : 0;
    const timer = setTimeout(() => {
      fetchSkillsPage(trimmed, 1, false);
    }, delay);

    return () => clearTimeout(timer);
  }, [keyword, isOpen, fetchSkillsPage]);

  // Cuộn mục đang highlight bằng bàn phím vào vùng nhìn thấy
  useEffect(() => {
    if (highlightedIndex >= 0 && optionRefs.current[highlightedIndex]) {
      optionRefs.current[highlightedIndex].scrollIntoView({ block: 'nearest' });
    }
  }, [highlightedIndex]);

  const handleSelect = useCallback(
    (skillObj) => {
      onSkillChange?.(skillObj);
      closeDropdown(true);
    },
    [onSkillChange, closeDropdown]
  );

  const handleClear = (e) => {
    e.stopPropagation();
    onSkillChange?.(null);
  };

  const handleLoadMore = () => {
    if (loadingMore || skills.length >= total) return;
    fetchSkillsPage(keyword, page + 1, true);
  };

  // Điều hướng bàn phím trong popup (↑ / ↓ / Enter / Escape)
  const handleKeyDown = (e) => {
    if (!isOpen) return;

    const totalOptions = 1 + skills.length; // 0 = Tất cả kỹ năng, 1..N = skills

    if (e.key === 'Escape') {
      e.preventDefault();
      closeDropdown(true);
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (totalOptions > 0) {
        setHighlightedIndex((prev) => (prev + 1) % totalOptions);
      }
      return;
    }

    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (totalOptions > 0) {
        setHighlightedIndex((prev) => (prev <= 0 ? totalOptions - 1 : prev - 1));
      }
      return;
    }

    if (e.key === 'Enter' && highlightedIndex >= 0) {
      e.preventDefault();
      if (highlightedIndex === 0) {
        handleSelect(null);
      } else {
        const picked = skills[highlightedIndex - 1];
        if (picked) handleSelect(picked);
      }
    }
  };

  const trimmedKeyword = keyword.trim();
  const hasMore = !loading && !error && skills.length > 0 && skills.length < total;
  const activeOptionId =
    highlightedIndex >= 0 ? `${listboxId}-opt-${highlightedIndex}` : undefined;

  return (
    <div className={styles.container} ref={containerRef} onKeyDown={handleKeyDown}>
      {/* Nút bấm mở dropdown */}
      <button
        ref={triggerRef}
        type="button"
        className={`${styles.trigger} ${selectedSkill ? styles.triggerActive : ''} ${
          isOpen ? styles.triggerOpen : ''
        }`}
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-controls={isOpen ? listboxId : undefined}
      >
        <span className={styles.triggerContent}>
          {selectedSkill ? (
            <>
              <span className={styles.selectedText} title={selectedSkill.skill}>
                {selectedSkill.skill}
              </span>
              {typeof selectedSkill.course_count === 'number' && (
                <span className={styles.selectedCount}>({selectedSkill.course_count})</span>
              )}
            </>
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
        <div className={styles.dropdown}>
          {/* Ô gõ tìm kiếm kỹ năng */}
          <div className={styles.searchBox}>
            <SearchIcon />
            <input
              ref={searchInputRef}
              type="text"
              role="combobox"
              aria-autocomplete="list"
              aria-expanded={isOpen}
              aria-controls={listboxId}
              aria-activedescendant={activeOptionId}
              className={styles.searchInput}
              placeholder="Gõ để tìm kỹ năng..."
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              aria-label="Tìm kỹ năng"
            />
            {keyword && (
              <button
                type="button"
                className={styles.clearInputBtn}
                onClick={() => {
                  setKeyword('');
                  searchInputRef.current?.focus();
                }}
                aria-label="Xóa từ khóa tìm kỹ năng"
                title="Xóa từ khóa"
              >
                <ClearIcon />
              </button>
            )}
          </div>

          {/* Danh sách kỹ năng */}
          <div id={listboxId} className={styles.optionsList} role="listbox" aria-label="Danh sách kỹ năng">
            {/* Lựa chọn 'Tất cả kỹ năng' */}
            <button
              id={`${listboxId}-opt-0`}
              ref={(el) => {
                optionRefs.current[0] = el;
              }}
              type="button"
              className={`${styles.optionItem} ${!selectedSkill ? styles.optionSelected : ''} ${
                highlightedIndex === 0 ? styles.optionHighlighted : ''
              }`}
              onClick={() => handleSelect(null)}
              onMouseEnter={() => setHighlightedIndex(0)}
              role="option"
              aria-selected={!selectedSkill}
            >
              <span className={styles.optionLabel}>Tất cả kỹ năng</span>
              {!selectedSkill && <CheckIcon />}
            </button>

            {/* Nhãn phân nhóm ngữ cảnh */}
            <div className={styles.groupHeader} aria-hidden="true">
              <span>{trimmedKeyword ? 'Kết quả tìm kiếm' : 'Kỹ năng phổ biến nhất'}</span>
              {!loading && !error && total > 0 && (
                <span className={styles.groupCount}>
                  {total.toLocaleString('vi-VN')} kỹ năng
                </span>
              )}
            </div>

            {loading ? (
              <div className={styles.skeletonList} aria-label="Đang tải danh sách kỹ năng">
                {Array.from({ length: 5 }).map((_, idx) => (
                  <div key={idx} className={`skeleton ${styles.skeletonRow}`} aria-hidden="true" />
                ))}
              </div>
            ) : error ? (
              <div className={styles.errorBox} role="alert">
                <span>{error}</span>
                <button
                  type="button"
                  className="btn btn-sm"
                  onClick={() => fetchSkillsPage(keyword, 1, false)}
                >
                  Thử lại
                </button>
              </div>
            ) : skills.length === 0 ? (
              <div className={styles.statusMessage}>
                Không tìm thấy kỹ năng phù hợp{trimmedKeyword ? ` với "${trimmedKeyword}"` : ''}.
              </div>
            ) : (
              <>
                {skills.map((s, idx) => {
                  const optionIndex = idx + 1;
                  const isSelected = selectedSkill?.skill_id === s.skill_id;
                  const isHighlighted = highlightedIndex === optionIndex;
                  return (
                    <button
                      key={s.skill_id}
                      id={`${listboxId}-opt-${optionIndex}`}
                      ref={(el) => {
                        optionRefs.current[optionIndex] = el;
                      }}
                      type="button"
                      className={`${styles.optionItem} ${isSelected ? styles.optionSelected : ''} ${
                        isHighlighted ? styles.optionHighlighted : ''
                      }`}
                      onClick={() => handleSelect(s)}
                      onMouseEnter={() => setHighlightedIndex(optionIndex)}
                      role="option"
                      aria-selected={isSelected}
                    >
                      <span className={styles.optionLabel} title={s.skill}>
                        {s.skill}
                      </span>
                      <span className={styles.optionMeta}>
                        {typeof s.course_count === 'number' && (
                          <span
                            className={styles.courseCount}
                            title={`${s.course_count.toLocaleString('vi-VN')} khóa học`}
                          >
                            ({s.course_count.toLocaleString('vi-VN')})
                          </span>
                        )}
                        {isSelected && <CheckIcon />}
                      </span>
                    </button>
                  );
                })}

                {hasMore && (
                  <button
                    type="button"
                    className={styles.loadMoreBtn}
                    disabled={loadingMore}
                    onClick={handleLoadMore}
                  >
                    {loadingMore
                      ? 'Đang tải thêm...'
                      : `Xem thêm kỹ năng (${skills.length.toLocaleString('vi-VN')} / ${total.toLocaleString('vi-VN')})`}
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
