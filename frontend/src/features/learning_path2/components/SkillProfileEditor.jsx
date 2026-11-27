import { useEffect, useState } from 'react';
import { getSkills } from '../../../api/skill.api.js';
import { PROFICIENCY_LABELS } from '../labels.js';
import styles from '../styles/CreatePathModal.module.css';

// G1 expects short English durations ("1 year", "6 months").
const DURATIONS = [
  ['', 'Thời gian dùng'],
  ['less than 1 year', '< 1 năm'],
  ['1 year', '1 năm'],
  ['2 years', '2 năm'],
  ['3 years', '3 năm'],
  ['over 5 years', '> 5 năm'],
];

// rows: [{ skill_name, proficiency_level, experience_duration }]
export default function SkillProfileEditor({ rows, onChange, proficiencyLevels }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    const q = query.trim();
    if (q.length < 2) { setResults([]); return undefined; }
    let alive = true;
    const timer = setTimeout(() => {
      getSkills({ keyword: q, limit: 8 })
        .then((res) => { if (alive) setResults(res.data?.data ?? []); })
        .catch(() => { if (alive) setResults([]); });
    }, 250);
    return () => { alive = false; clearTimeout(timer); };
  }, [query]);

  const taken = new Set(rows.map((r) => r.skill_name.toLowerCase()));

  function add(name) {
    const text = name.trim();
    if (!text || taken.has(text.toLowerCase()) || rows.length >= 30) return;
    onChange([...rows, { skill_name: text, proficiency_level: null, experience_duration: null }]);
    setQuery('');
    setResults([]);
  }

  function update(index, patch) {
    onChange(rows.map((r, i) => (i === index ? { ...r, ...patch } : r)));
  }

  return (
    <div className={styles.skillEditor}>
      <div className={styles.chipField}>
        <input
          className={styles.input}
          value={query}
          placeholder="Tìm kỹ năng bạn đã có, vd: Python, SQL…"
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') { e.preventDefault(); add(results[0]?.skill ?? query); }
          }}
        />
        {results.length > 0 && (
          <ul className={styles.dropdown} role="listbox">
            {results.filter((s) => !taken.has(s.skill.toLowerCase())).map((s) => (
              <li key={s.skill_id} role="option" aria-selected="false"
                onMouseDown={(e) => { e.preventDefault(); add(s.skill); }}>
                <span>{s.skill}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {rows.length > 0 && (
        <ul className={styles.skillRows}>
          {rows.map((row, i) => (
            <li key={row.skill_name} className={styles.skillRow}>
              <span className={styles.skillName}>{row.skill_name}</span>
              <select className={styles.select} value={row.proficiency_level ?? ''}
                aria-label={`Mức độ ${row.skill_name}`}
                onChange={(e) => update(i, { proficiency_level: e.target.value || null })}>
                <option value="">Mức độ</option>
                {proficiencyLevels.map((p) => <option key={p} value={p}>{PROFICIENCY_LABELS[p] ?? p}</option>)}
              </select>
              <select className={styles.select} value={row.experience_duration ?? ''}
                aria-label={`Thời gian dùng ${row.skill_name}`}
                onChange={(e) => update(i, { experience_duration: e.target.value || null })}>
                {DURATIONS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
              <button type="button" className={styles.iconButton} aria-label={`Bỏ ${row.skill_name}`}
                onClick={() => onChange(rows.filter((_, j) => j !== i))}>×</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
