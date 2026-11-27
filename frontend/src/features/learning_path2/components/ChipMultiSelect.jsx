import { useId, useMemo, useState } from 'react';
import styles from '../styles/CreatePathModal.module.css';

// Searchable multi-select with chips. options: [{ value, label, sub? }]. value: string[].
// allowCustom: Enter adds the typed text when it is not in the list.
export default function ChipMultiSelect({ options, value, onChange, placeholder, allowCustom = false, max = 15 }) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const listId = useId();

  const matches = useMemo(() => {
    const q = query.trim().toLowerCase();
    return options
      .filter((o) => !value.includes(o.value))
      .filter((o) => !q || o.label.toLowerCase().includes(q) || o.sub?.toLowerCase().includes(q))
      .slice(0, 8);
  }, [options, value, query]);

  function add(v) {
    const text = v.trim();
    if (!text || value.includes(text) || value.length >= max) return;
    onChange([...value, text]);
    setQuery('');
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      if (matches[0]) add(matches[0].value);
      else if (allowCustom) add(query);
    } else if (event.key === 'Backspace' && !query && value.length) {
      onChange(value.slice(0, -1));
    } else if (event.key === 'Escape') {
      setOpen(false);
    }
  }

  return (
    <div className={styles.chipField}>
      <div className={styles.chipBox} onClick={() => setOpen(true)}>
        {value.map((v) => (
          <span key={v} className={styles.chip}>
            {v}
            <button type="button" aria-label={`Bỏ ${v}`} onClick={() => onChange(value.filter((x) => x !== v))}>×</button>
          </span>
        ))}
        <input
          className={styles.chipInput}
          value={query}
          placeholder={value.length ? '' : placeholder}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 120)}
          onKeyDown={handleKeyDown}
          role="combobox"
          aria-expanded={open}
          aria-controls={listId}
        />
      </div>
      {open && (matches.length > 0 || (allowCustom && query.trim())) && (
        <ul id={listId} className={styles.dropdown} role="listbox">
          {matches.map((o) => (
            <li key={o.value} role="option" aria-selected="false"
              onMouseDown={(e) => { e.preventDefault(); add(o.value); }}>
              <span>{o.label}</span>
              {o.sub && <small>{o.sub}</small>}
            </li>
          ))}
          {allowCustom && query.trim() && !matches.some((o) => o.label.toLowerCase() === query.trim().toLowerCase()) && (
            <li role="option" aria-selected="false" className={styles.customOption}
              onMouseDown={(e) => { e.preventDefault(); add(query); }}>
              Thêm “{query.trim()}”
            </li>
          )}
        </ul>
      )}
    </div>
  );
}
