// Ô "Thêm kỹ năng" có danh sách sổ xuống (FĐ6, 08/11/2026 · theo màn demo Skills: _addRow / _suggest)
//
// Người dùng không nhớ hết tên kỹ năng (danh mục ~5.900 kỹ năng) → bấm vào ô hoặc nút ▾ là có gợi ý:
//   - CHƯA GÕ: "Gợi ý cho bạn" (GET /api/me/skills/suggestions) chia 3 nhóm
//       Học tiếp  — sau kỹ năng bạn đã có (vd có Python → Pandas, Django)
//       Liên quan — cùng nhóm với kỹ năng bạn đã có
//       Phổ biến  — được dạy trong nhiều khóa học nhất
//   - ĐANG GÕ: tìm trong danh mục (GET /api/skills của Hòa), chờ 250 ms; nhiều kết quả → "Xem thêm".
//   - Ẩn kỹ năng đã có trong hồ sơ (excludeIds). Bàn phím: ↑ ↓ chọn, Enter, Esc đóng.
//   onAdd(skill, status): trang cha thêm vào bản nháp (chưa gửi server).
//   refreshKey: đổi giá trị (vd sau khi Lưu) → tải lại gợi ý theo hồ sơ mới.
import { useEffect, useId, useRef, useState } from 'react';

import * as meApi from '../../../api/me.api.js';
import * as skillsApi from '../../../api/skills.api.js';
import styles from '../styles/SkillsPage.module.css';

const PAGE = 20;
const GROUPS = [
  { reason: 'next', title: 'Học tiếp' },
  { reason: 'related', title: 'Liên quan' },
  { reason: 'popular', title: 'Phổ biến' },
];

const ICON = { 'aria-hidden': true, width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round', strokeLinejoin: 'round' };
const SearchIcon = () => (<svg {...ICON}><circle cx="11" cy="11" r="6.5" /><path d="m20 20-4.2-4.2" /></svg>);
const PlusIcon = () => (<svg {...ICON} strokeWidth={2}><path d="M12 5v14M5 12h14" /></svg>);
const ChevronIcon = () => (<svg {...ICON}><path d="m6 9 6 6 6-6" /></svg>);

function hint(s) {
  if (s.reason === 'next') return `Sau ${s.via}`;
  if (s.reason === 'related') return `Liên quan ${s.via}`;
  if (s.course_count) return `${s.course_count} khóa học`;
  return '';
}

export default function SkillSearch({ excludeIds, onAdd, disabled, refreshKey }) {
  const listId = useId();
  const inputRef = useRef(null);
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('known');
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const [selected, setSelected] = useState(null); // { skill_id, skill }
  const [error, setError] = useState('');

  const [suggestions, setSuggestions] = useState(null); // null = đang tải
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [searching, setSearching] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);

  const keyword = query.trim();
  const searchMode = keyword !== '' && !(selected && selected.skill === query);

  // Gợi ý theo hồ sơ — tải lần đầu và sau mỗi lần lưu
  useEffect(() => {
    let cancelled = false;
    setSuggestions(null);
    meApi
      .getSkillSuggestions(15)
      .then((data) => !cancelled && setSuggestions(data))
      .catch(() => !cancelled && setSuggestions([]));
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  // Tìm theo chữ đang gõ (chờ 250 ms sau phím cuối)
  useEffect(() => {
    if (!searchMode) {
      setResults([]);
      setTotal(0);
      return undefined;
    }
    let cancelled = false;
    setSearching(true);
    const timer = setTimeout(async () => {
      try {
        const data = await skillsApi.searchSkills(keyword, PAGE, 0);
        if (cancelled) return;
        setResults(data.data);
        setTotal(data.total);
        setActive(-1);
        setError('');
      } catch {
        if (!cancelled) setError('Không tải được danh mục kỹ năng. Thử lại sau.');
      } finally {
        if (!cancelled) setSearching(false);
      }
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [keyword, searchMode]);

  async function loadMore() {
    setLoadingMore(true);
    try {
      const data = await skillsApi.searchSkills(keyword, PAGE, results.length);
      setResults((prev) => [...prev, ...data.data]);
      setTotal(data.total);
    } catch {
      setError('Không tải thêm được. Thử lại sau.');
    } finally {
      setLoadingMore(false);
    }
  }

  // Danh sách đang hiện (đã bỏ kỹ năng có trong hồ sơ) — dùng chung cho chuột và bàn phím
  const items = (searchMode ? results : suggestions ?? []).filter((s) => !excludeIds.has(s.skill_id));
  const hiddenCount = searchMode ? results.length - items.length : 0;
  const remaining = searchMode ? Math.max(0, total - results.length) : 0;

  function choose(skill) {
    setSelected(skill);
    setQuery(skill.skill);
    setOpen(false);
    setActive(-1);
    setError('');
  }

  function handleKeyDown(event) {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setOpen(true);
      if (items.length) setActive((i) => (i + 1) % items.length);
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      if (items.length) setActive((i) => (i <= 0 ? items.length - 1 : i - 1));
    } else if (event.key === 'Enter' && open && active >= 0 && items[active]) {
      event.preventDefault();
      choose(items[active]);
    } else if (event.key === 'Escape') {
      setOpen(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    const skill = selected ?? items.find((s) => s.skill.toLowerCase() === keyword.toLowerCase());
    if (!skill) {
      setError('Chọn một kỹ năng trong danh sách sổ xuống.');
      setOpen(true);
      inputRef.current?.focus();
      return;
    }
    if (excludeIds.has(skill.skill_id)) {
      setError(`"${skill.skill}" đã có trong hồ sơ.`);
      return;
    }
    onAdd(skill, status);
    setQuery('');
    setSelected(null);
    setError('');
    inputRef.current?.focus();
  }

  function renderItem(s, index) {
    return (
      <li key={s.skill_id} id={`${listId}-${index}`} role="option" aria-selected={index === active}>
        <button
          type="button"
          className={index === active ? styles.menuActive : ''}
          onMouseDown={(event) => event.preventDefault()} // giữ focus ở ô nhập
          onMouseEnter={() => setActive(index)}
          onClick={() => choose(s)}
        >
          <span>{s.skill}</span>
          {!searchMode && hint(s) && <span className={styles.menuHint}>{hint(s)}</span>}
        </button>
      </li>
    );
  }

  // Nhóm gợi ý; chỉ số (index) liên tục qua các nhóm để ↑ ↓ đi xuyên nhóm
  let groupStart = 0;
  const grouped = GROUPS.map((group) => {
    const list = items.filter((s) => s.reason === group.reason);
    const start = groupStart;
    groupStart += list.length;
    return { ...group, list, start };
  }).filter((g) => g.list.length > 0);

  return (
    <form className={`inner ${styles.addRow}`} onSubmit={handleSubmit} noValidate>
      <div className={`field ${styles.suggest}`}>
        <label htmlFor="skill-q">Thêm kỹ năng</label>
        <span className={`input ${error ? 'invalid' : ''}`}>
          <SearchIcon />
          <input
            id="skill-q"
            ref={inputRef}
            autoComplete="off"
            placeholder="Tìm hoặc chọn trong danh sách gợi ý"
            role="combobox"
            aria-expanded={open}
            aria-controls={listId}
            aria-activedescendant={open && active >= 0 ? `${listId}-${active}` : undefined}
            value={query}
            disabled={disabled}
            onChange={(event) => {
              setQuery(event.target.value);
              setSelected(null);
              setOpen(true);
              setError('');
            }}
            onKeyDown={handleKeyDown}
            onFocus={() => setOpen(true)}
            onClick={() => setOpen(true)}
            onBlur={() => setTimeout(() => setOpen(false), 150)}
          />
          {searching && <span className={styles.miniSpin} aria-hidden="true" />}
          <button
            type="button"
            className={`${styles.toggle} ${open ? styles.toggleOpen : ''}`}
            aria-label={open ? 'Đóng danh sách kỹ năng' : 'Mở danh sách kỹ năng'}
            tabIndex={-1}
            disabled={disabled}
            onMouseDown={(event) => event.preventDefault()}
            onClick={() => {
              setOpen((o) => !o);
              inputRef.current?.focus();
            }}
          >
            <ChevronIcon />
          </button>
        </span>

        {open && !disabled && (
          <div id={listId} className={styles.menu} role="listbox" aria-label="Kỹ năng gợi ý">
            {searchMode ? (
              <>
                <div className={styles.menuHead}>
                  {searching ? 'Đang tìm…' : `Kết quả cho "${keyword}" · ${total}`}
                </div>
                {!searching && items.length === 0 && (
                  <p className={styles.menuEmpty}>
                    {hiddenCount > 0 ? 'Các kỹ năng tìm thấy đều đã có trong hồ sơ.' : 'Không tìm thấy kỹ năng phù hợp.'}
                  </p>
                )}
                <ul>{items.map((s, i) => renderItem(s, i))}</ul>
                {remaining > 0 && !searching && (
                  <button
                    type="button"
                    className={styles.more}
                    disabled={loadingMore}
                    onMouseDown={(event) => event.preventDefault()}
                    onClick={loadMore}
                  >
                    {loadingMore ? 'Đang tải…' : `Xem thêm kết quả (còn ${remaining})`}
                  </button>
                )}
              </>
            ) : (
              <>
                <div className={styles.menuHead}>Gợi ý cho bạn — hoặc gõ để tìm</div>
                {suggestions === null && <p className={styles.menuEmpty}>Đang tải gợi ý…</p>}
                {suggestions !== null && items.length === 0 && (
                  <p className={styles.menuEmpty}>Chưa có gợi ý. Gõ tên kỹ năng để tìm.</p>
                )}
                {grouped.map((g) => (
                  <div key={g.reason}>
                    <div className={styles.menuGroup}>{g.title}</div>
                    <ul>{g.list.map((s, i) => renderItem(s, g.start + i))}</ul>
                  </div>
                ))}
              </>
            )}
          </div>
        )}

        {error && (
          <span className="field-error" role="alert">
            {error}
          </span>
        )}
      </div>

      <label className="field" htmlFor="skill-st" style={{ flex: '0 1 180px' }}>
        Trạng thái
        <select
          id="skill-st"
          className="select"
          value={status}
          disabled={disabled}
          onChange={(event) => setStatus(event.target.value)}
        >
          <option value="known">Đã biết</option>
          <option value="learning">Đang học</option>
        </select>
      </label>

      <button type="submit" className="btn btn-soft" disabled={disabled}>
        <PlusIcon />
        Thêm
      </button>
    </form>
  );
}
