// Thêm / sửa câu hỏi ôn tập — 7.6 P2 sửa có phiên bản, P3 thêm câu (module 09 · Tuấn · 16/11/2026).
//
// Thêm (detail không có question_id — dùng blankQuestion): chọn loại TN / TL, mã điền sẵn mã gợi ý (để trống →
// backend tự cấp như lúc Duyệt), gửi đủ trường → câu phiên bản 1, đã duyệt, bật ngay.
//
// Quy tắc nằm ở backend (review_bank_service.update_question), form chỉ gửi TRƯỜNG ĐÃ ĐỔI:
//   - Câu chưa ai làm / đang chờ duyệt → sửa tại chỗ (nút "Lưu").
//   - Câu đã có bài làm → "Lưu phiên bản mới" (bài cũ giữ đúng đề + điểm lúc làm) hoặc "Sửa nhỏ"
//     (chỉ giải thích / đoạn tri thức / nhóm loại trừ / chính tả đề ≥ 90% giống — sai → 409 kèm lý do).
//   - Nội dung câu sai (4 lựa chọn, số ý barem, tổng 10…) → 422 kèm danh sách lỗi → hiện từng dòng.
import { useEffect, useMemo, useState } from 'react';

import * as reviewAdminApi from '../../../api/reviewAdmin.api.js';
import { parseApiError } from '../../../utils/errors.js';
import { OPTION_LETTERS, formatScore } from '../../review/reviewFormat.js';
import styles from '../styles/AdminReviewQuestions.module.css';

const LEVELS = {
  mcq: [
    { value: 'recognize', text: 'Nhận biết' },
    { value: 'understand', text: 'Thông hiểu' },
  ],
  essay: [
    { value: 'easy', text: 'Dễ' },
    { value: 'advanced', text: 'Nâng cao' },
  ],
};
const RUBRIC_SIZE = { easy: [2, 3], advanced: [4, 5] }; // khớp validator backend (chốt 09/11)

// Câu trống cho form "Thêm câu hỏi" — barem mặc định 3 ý 4 + 3 + 3 (câu dễ cần 2–3 ý, tổng 10)
export function blankQuestion(type, skillId, skillName) {
  return {
    type,
    skill_id: skillId,
    skill_name: skillName,
    chunk_id: null,
    level: type === 'mcq' ? 'recognize' : 'easy',
    content: '',
    options: ['', '', '', ''],
    correct_index: 0,
    rubric: [4, 3, 3].map((max_points) => ({ text: '', max_points, main_keywords: [], sub_keywords: [] })),
    explanation: '',
    exclusion_group: '',
    used_count: 0,
    version: 0,
    review_status: 'approved',
  };
}

function toForm(d) {
  return {
    type: d.type,
    skill_id: d.skill_id,
    chunk_id: d.chunk_id ?? '',
    level: d.level,
    content: d.content,
    options: d.type === 'mcq' ? [...(d.options || ['', '', '', ''])] : null,
    correct_index: d.type === 'mcq' ? d.correct_index : null,
    rubric:
      d.type === 'essay'
        ? (d.rubric || []).map((r) => ({
            text: r.text,
            max_points: r.max_points,
            main_keywords: [...(r.main_keywords || [])],
            sub_keywords: [...(r.sub_keywords || [])],
          }))
        : null,
    explanation: d.explanation ?? '',
    exclusion_group: d.exclusion_group ?? '',
  };
}

// form → giá trị đúng kiểu backend (rỗng → null, điểm → số)
function normalize(f) {
  return {
    skill_id: Number(f.skill_id),
    chunk_id: f.chunk_id === '' ? null : Number(f.chunk_id),
    level: f.level,
    content: f.content,
    options: f.options,
    correct_index: f.correct_index,
    rubric: f.rubric && f.rubric.map((r) => ({ ...r, max_points: Number(r.max_points) })),
    explanation: f.explanation.trim() === '' ? null : f.explanation,
    exclusion_group: f.exclusion_group.trim() === '' ? null : f.exclusion_group.trim(),
  };
}

function changedFields(detail, form) {
  const before = normalize(toForm(detail));
  const after = normalize(form);
  const out = {};
  for (const key of Object.keys(after)) {
    if (after[key] === null && before[key] === null) continue;
    if (JSON.stringify(after[key]) !== JSON.stringify(before[key])) out[key] = after[key];
  }
  if (detail.type === 'mcq') delete out.rubric;
  else {
    delete out.options;
    delete out.correct_index;
  }
  return out;
}

// Thêm câu: gửi đủ trường theo loại (TN không có barem, TL không có phương án)
function createBody(form, code) {
  const body = { ...normalize(form), type: form.type, code: code.trim() || null };
  if (form.type === 'mcq') delete body.rubric;
  else {
    delete body.options;
    delete body.correct_index;
  }
  return body;
}

function KeywordInput({ label, value, onChange, tone }) {
  const [text, setText] = useState('');
  function add() {
    const word = text.trim();
    if (word && !value.includes(word)) onChange([...value, word]);
    setText('');
  }
  return (
    <div className={styles.kwBox}>
      <span className="small muted">{label}</span>
      <div className={styles.kwList}>
        {value.map((word) => (
          <span key={word} className={`chip ${tone} ${styles.kw}`}>
            {word}
            <button
              type="button"
              className={styles.kwRemove}
              aria-label={`Bỏ từ khóa ${word}`}
              onClick={() => onChange(value.filter((w) => w !== word))}
            >
              ×
            </button>
          </span>
        ))}
        <input
          className={styles.kwInput}
          value={text}
          placeholder="gõ rồi Enter"
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ',') {
              e.preventDefault();
              add();
            }
          }}
          onBlur={add}
        />
      </div>
    </div>
  );
}

function RubricEditor({ rubric, level, onChange }) {
  const [low, high] = RUBRIC_SIZE[level] || [2, 5];
  const total = rubric.reduce((sum, r) => sum + Number(r.max_points || 0), 0);
  const set = (i, patch) => onChange(rubric.map((r, j) => (j === i ? { ...r, ...patch } : r)));
  return (
    <div className={styles.rubricEdit}>
      <span className="small muted">
        Barem · câu {level === 'easy' ? 'dễ' : 'nâng cao'} cần {low}–{high} ý · mỗi ý Đạt (đủ điểm) hoặc Chưa đạt (0)
      </span>
      {rubric.map((r, i) => (
        <div key={i} className={styles.rubricItem}>
          <div className={styles.rubricHead}>
            <b>Ý {i + 1}</b>
            <label className={styles.points}>
              <span className="small muted">Điểm</span>
              <input
                type="number"
                min="0"
                max="10"
                step="0.5"
                value={r.max_points}
                onChange={(e) => set(i, { max_points: e.target.value })}
              />
            </label>
            <button
              type="button"
              className="btn btn-soft btn-sm"
              disabled={rubric.length <= low}
              onClick={() => onChange(rubric.filter((_, j) => j !== i))}
            >
              Bỏ ý
            </button>
          </div>
          <textarea
            className={styles.textarea}
            rows={2}
            value={r.text}
            onChange={(e) => set(i, { text: e.target.value })}
            aria-label={`Nội dung ý ${i + 1}`}
          />
          <KeywordInput
            label="Từ khóa chính"
            tone="chip-info"
            value={r.main_keywords}
            onChange={(v) => set(i, { main_keywords: v })}
          />
          <KeywordInput
            label="Từ khóa phụ"
            tone=""
            value={r.sub_keywords}
            onChange={(v) => set(i, { sub_keywords: v })}
          />
        </div>
      ))}
      <div className={styles.rubricFoot}>
        <button
          type="button"
          className="btn btn-soft btn-sm"
          disabled={rubric.length >= high}
          onClick={() => onChange([...rubric, { text: '', max_points: 0, main_keywords: [], sub_keywords: [] }])}
        >
          + Thêm ý
        </button>
        <span className={`small ${total === 10 ? 'muted' : styles.warn}`}>
          Tổng điểm barem: {formatScore(total)} · phải đúng 10
        </span>
      </div>
    </div>
  );
}

export default function QuestionEditor({ detail, skills, onSaved, onCancel }) {
  const creating = !detail.question_id;
  const [form, setForm] = useState(() => toForm(detail));
  const [code, setCode] = useState('');
  const [chunks, setChunks] = useState([]);
  const [note, setNote] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [errorList, setErrorList] = useState([]);

  const used = detail.used_count > 0 && detail.review_status !== 'pending';
  const set = (patch) => setForm((f) => ({ ...f, ...patch }));

  // kỹ năng của khóa đang chọn + kỹ năng hiện tại của câu (nếu khóa chưa chọn / câu thuộc kỹ năng khác)
  const skillOptions = useMemo(() => {
    const list = [...(skills || [])];
    if (!list.some((s) => s.skill_id === detail.skill_id)) {
      list.unshift({ skill_id: detail.skill_id, skill: detail.skill_name || `Kỹ năng ${detail.skill_id}` });
    }
    return list;
  }, [skills, detail.skill_id, detail.skill_name]);

  // Thêm câu: mã gợi ý theo kỹ năng + loại (đổi kỹ năng / loại → gợi ý lại)
  useEffect(() => {
    if (!creating) return undefined;
    let alive = true;
    reviewAdminApi
      .getSkillSuggestedCode(form.skill_id, form.type)
      .then((suggested) => alive && setCode(suggested || ''))
      .catch(() => alive && setCode(''));
    return () => {
      alive = false;
    };
  }, [creating, form.skill_id, form.type]);

  // đổi loại câu khi thêm → làm lại phần riêng của loại (mức, phương án / barem), giữ đề + kỹ năng
  function switchType(type) {
    if (type === form.type) return;
    const blank = toForm(blankQuestion(type, form.skill_id));
    setForm((f) => ({
      ...f,
      type,
      level: blank.level,
      options: blank.options,
      correct_index: blank.correct_index,
      rubric: blank.rubric,
    }));
  }

  useEffect(() => {
    let alive = true;
    reviewAdminApi
      .getSkillChunks(form.skill_id)
      .then((list) => alive && setChunks(list))
      .catch(() => alive && setChunks([]));
    return () => {
      alive = false;
    };
  }, [form.skill_id]);

  function showError(err) {
    const detailBody = err?.response?.data?.detail;
    if (err?.response?.status === 422 && detailBody?.errors) {
      setError(detailBody.message || 'Câu hỏi không hợp lệ');
      setErrorList(detailBody.errors);
    } else {
      setError(parseApiError(err).message);
    }
  }

  async function create() {
    setBusy(true);
    setError('');
    setErrorList([]);
    try {
      const q = await reviewAdminApi.createQuestion(createBody(form, code));
      onSaved(q, `Đã thêm câu ${q.code} — đang bật, có thể vào đề ôn tập.`);
    } catch (err) {
      showError(err);
      setBusy(false);
    }
  }

  async function save(minor) {
    const changes = changedFields(detail, form);
    if (!Object.keys(changes).length) {
      setError('Chưa có gì thay đổi.');
      setErrorList([]);
      return;
    }
    setBusy(true);
    setError('');
    setErrorList([]);
    try {
      const result = await reviewAdminApi.updateQuestion(detail.question_id, {
        ...changes,
        minor,
        ...(note.trim() ? { note: note.trim() } : {}),
      });
      const q = result.question;
      onSaved(
        q,
        result.versioned
          ? `Đã lưu phiên bản v${q.version}${q.code ? ` (${q.code})` : ''}. ${detail.used_count} bài làm cũ vẫn giữ phiên bản v${detail.version}.`
          : `Đã lưu${minor ? ' (sửa nhỏ, không tạo phiên bản)' : ''}.`,
      );
    } catch (err) {
      showError(err);
      setBusy(false);
    }
  }

  return (
    <form className={styles.editor} onSubmit={(e) => e.preventDefault()}>
      <div className={styles.editorHead}>
        <b>
          {creating ? 'Thêm câu hỏi' : 'Sửa câu'} {form.type === 'mcq' ? 'trắc nghiệm' : 'tự luận'}
        </b>
        {creating ? (
          <div className={styles.seg} role="radiogroup" aria-label="Loại câu">
            {[
              ['mcq', 'Trắc nghiệm'],
              ['essay', 'Tự luận'],
            ].map(([value, text]) => (
              <button
                key={value}
                type="button"
                role="radio"
                aria-checked={form.type === value}
                className={form.type === value ? styles.segOn : ''}
                onClick={() => switchType(value)}
              >
                {text}
              </button>
            ))}
          </div>
        ) : (
          <span className="small muted">
            {detail.code || 'chưa có mã'} · v{detail.version} · {detail.used_count} bài làm
          </span>
        )}
      </div>

      <div className={styles.editorGrid}>
        <label className={styles.field}>
          <span className="small muted">Kỹ năng</span>
          <select
            className="select"
            value={form.skill_id}
            onChange={(e) => set({ skill_id: Number(e.target.value), chunk_id: '' })}
          >
            {skillOptions.map((s) => (
              <option key={s.skill_id} value={s.skill_id}>
                {s.skill}
              </option>
            ))}
          </select>
        </label>
        <label className={styles.field}>
          <span className="small muted">Đoạn tri thức</span>
          <select className="select" value={form.chunk_id} onChange={(e) => set({ chunk_id: e.target.value })}>
            <option value="">— không gắn —</option>
            {chunks.map((c) => (
              <option key={c.chunk_id} value={c.chunk_id}>
                {c.code ? `${c.code} · ` : ''}
                {c.title || `Đoạn ${c.chunk_id}`}
              </option>
            ))}
          </select>
        </label>
        <div className={styles.field}>
          <span className="small muted">Mức độ</span>
          <div className={styles.seg} role="radiogroup" aria-label="Mức độ">
            {LEVELS[form.type].map((lv) => (
              <button
                key={lv.value}
                type="button"
                role="radio"
                aria-checked={form.level === lv.value}
                className={form.level === lv.value ? styles.segOn : ''}
                onClick={() => set({ level: lv.value })}
              >
                {lv.text}
              </button>
            ))}
          </div>
        </div>
        {creating && (
          <label className={styles.field}>
            <span className="small muted">Mã câu (không bắt buộc)</span>
            <span className="input">
              <input
                value={code}
                maxLength={50}
                placeholder="để trống → tự cấp"
                onChange={(e) => setCode(e.target.value)}
              />
            </span>
            <span className="small muted">Điền sẵn mã gợi ý theo kỹ năng; sửa được.</span>
          </label>
        )}
        <label className={styles.field}>
          <span className="small muted">Nhóm loại trừ (không bắt buộc)</span>
          <span className="input">
            <input
              value={form.exclusion_group}
              maxLength={50}
              placeholder="vd COND-print"
              onChange={(e) => set({ exclusion_group: e.target.value })}
            />
          </span>
          <span className="small muted">Hai câu cùng nhóm không rơi vào một đề.</span>
        </label>
      </div>

      <label className={styles.field}>
        <span className="small muted">Đề bài</span>
        <textarea
          className={styles.textarea}
          rows={4}
          value={form.content}
          onChange={(e) => set({ content: e.target.value })}
        />
      </label>

      {form.type === 'mcq' ? (
        <div className={styles.field}>
          <span className="small muted">Phương án · chọn đáp án đúng</span>
          {form.options.map((opt, i) => (
            <div key={OPTION_LETTERS[i]} className={`${styles.optionEdit} ${form.correct_index === i ? styles.correct : ''}`}>
              <input
                type="radio"
                name={`correct-${detail.question_id ?? 'new'}`}
                checked={form.correct_index === i}
                onChange={() => set({ correct_index: i })}
                aria-label={`Đáp án đúng là ${OPTION_LETTERS[i]}`}
              />
              <span className={styles.letter}>{OPTION_LETTERS[i]}.</span>
              <input
                className={styles.optionInput}
                value={opt}
                onChange={(e) => set({ options: form.options.map((o, j) => (j === i ? e.target.value : o)) })}
              />
            </div>
          ))}
        </div>
      ) : (
        <RubricEditor rubric={form.rubric} level={form.level} onChange={(rubric) => set({ rubric })} />
      )}

      <label className={styles.field}>
        <span className="small muted">{form.type === 'mcq' ? 'Giải thích' : 'Đáp án mẫu'}</span>
        <textarea
          className={styles.textarea}
          rows={3}
          value={form.explanation}
          onChange={(e) => set({ explanation: e.target.value })}
        />
      </label>

      {used && (
        <div className={styles.versionWarn}>
          <b>Câu này đã có {detail.used_count} bài làm.</b>{' '}
          <span>
            Lưu sẽ tạo phiên bản v{detail.version + 1}. Các bài cũ vẫn hiện đúng đề và điểm lúc làm. Chỉ sửa chính tả,
            giải thích, đoạn tri thức hoặc nhóm thì chọn <b>Sửa nhỏ</b> để không tạo phiên bản.
          </span>
          <label className={styles.field}>
            <span className="small muted">Ghi chú phiên bản (không bắt buộc)</span>
            <span className="input">
              <input
                value={note}
                maxLength={200}
                placeholder="vd sửa đáp án C, thêm từ khóa ý 2"
                onChange={(e) => setNote(e.target.value)}
              />
            </span>
          </label>
        </div>
      )}

      {error && (
        <div className="alert" role="alert">
          {error}
          {errorList.length > 0 && (
            <ul className={styles.errorList}>
              {errorList.map((e) => (
                <li key={e}>{e}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      <div className={styles.buttons}>
        {creating ? (
          <button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={create}>
            Thêm câu
          </button>
        ) : used ? (
          <>
            <button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={() => save(false)}>
              Lưu phiên bản mới
            </button>
            <button type="button" className="btn btn-soft btn-sm" disabled={busy} onClick={() => save(true)}>
              Sửa nhỏ
            </button>
          </>
        ) : (
          <button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={() => save(false)}>
            Lưu
          </button>
        )}
        <button type="button" className="btn btn-soft btn-sm" disabled={busy} onClick={onCancel}>
          Hủy
        </button>
      </div>
    </form>
  );
}
