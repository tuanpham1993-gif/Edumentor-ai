// Ô "Tìm kỹ năng" trên trang Ngân hàng câu hỏi (module 09 · Tuấn · G1, 21/11/2026 — docs/Review-Skill-Search.md).
// Gõ tên kỹ năng (tiếng Anh / tiếng Việt, sai chính tả nhẹ) → GET /admin/review/skills/search → danh sách kỹ năng kèm
// số câu đang bật / chờ duyệt và các tên trùng. Chọn một kỹ năng → onPick({ skill_id, skill }) — không cần chọn khóa.
// confident = true (khớp nguyên văn / rất gần) → đánh dấu "khớp nhất"; không chắc thì chỉ liệt kê, người dùng tự chọn.
import { useEffect, useId, useRef, useState } from 'react';

import * as reviewAdminApi from '../../../api/reviewAdmin.api.js';
import { parseApiError } from '../../../utils/errors.js';
import styles from '../styles/AdminReviewQuestions.module.css';

const DELAY_MS = 300;
const MATCH_TEXT = { exact: 'khớp tên', keyword: 'theo chữ', vector: 'theo nghĩa', hybrid: 'chữ + nghĩa' };

export default function SkillSearchBox({ onPick }) {
  const [text, setText] = useState('');
  const [state, setState] = useState({ loading: false, data: null, error: '' });
  const [open, setOpen] = useState(false);
  const boxRef = useRef(null);
  const listId = useId();

  useEffect(() => {
    const q = text.trim();
    if (!q) {
      setState({ loading: false, data: null, error: '' });
      return undefined;
    }
    let alive = true;
    setState((s) => ({ ...s, loading: true, error: '' }));
    const timer = setTimeout(() => {
      reviewAdminApi
        .searchSkills(q)
        .then((data) => alive && setState({ loading: false, data, error: '' }))
        .catch((err) => alive && setState({ loading: false, data: null, error: parseApiError(err).message }));
    }, DELAY_MS);
    return () => {
      alive = false;
      clearTimeout(timer);
    };
  }, [text]);

  useEffect(() => {
    if (!open) return undefined;
    const onDown = (event) => boxRef.current && !boxRef.current.contains(event.target) && setOpen(false);
    document.addEventListener('mousedown', onDown);
    return () => document.removeEventListener('mousedown', onDown);
  }, [open]);

  function pick(result) {
    onPick({ skill_id: result.skill_id, skill: result.skill });
    setText('');
    setOpen(false);
  }

  const results = state.data?.results || [];
  return (
    <div className={styles.skillSearch} ref={boxRef}>
      <input
        type="search"
        className="input"
        placeholder="Tìm kỹ năng theo tên — vd: java, lập trình python, vòng lặp"
        aria-label="Tìm kỹ năng"
        aria-controls={listId}
        aria-expanded={open && Boolean(text.trim())}
        value={text}
        maxLength={100}
        onChange={(e) => {
          setText(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={(e) => {
          if (e.key === 'Escape') setOpen(false);
          if (e.key === 'Enter' && state.data?.confident && results[0]) pick(results[0]);
        }}
      />
      {open && text.trim() && (
        <div id={listId} className={`card ${styles.skillResults}`} role="listbox" aria-label="Kết quả tìm kỹ năng">
          {state.loading && <p className="muted small">Đang tìm…</p>}
          {state.error && <p className="alert">{state.error}</p>}
          {!state.loading && !state.error && results.length === 0 && (
            <p className="muted small">Không tìm thấy kỹ năng nào.</p>
          )}
          {!state.loading && results.length > 0 && !state.data.confident && (
            <p className="muted small">Chưa chắc chắn — chọn kỹ năng đúng trong danh sách.</p>
          )}
          {!state.loading &&
            results.map((r, i) => (
              <button
                key={r.skill_id}
                type="button"
                role="option"
                aria-selected={false}
                className={styles.skillResult}
                onClick={() => pick(r)}
              >
                <span>
                  <strong>{r.skill}</strong> <span className="muted small">#{r.skill_id}</span>
                  {i === 0 && state.data.confident && <span className="chip chip-ok">khớp nhất · Enter</span>}
                  {r.aliases.length > 0 && (
                    <span className="muted small" title={r.aliases.map((a) => `${a.skill} #${a.skill_id}`).join(', ')}>
                      {' '}
                      · {r.aliases.length} tên trùng
                    </span>
                  )}
                </span>
                <span className="muted small">
                  {r.active_questions ? `${r.active_questions} câu` : 'chưa có câu'}
                  {r.pending_questions ? ` · ${r.pending_questions} chờ duyệt` : ''} · {MATCH_TEXT[r.match] || r.match}
                </span>
              </button>
            ))}
        </div>
      )}
    </div>
  );
}
