// Đoạn tài liệu (đoạn tri thức RAG) của MỘT kỹ năng — khối trên trang Câu hỏi ôn tập (module 09 · Tuấn · G3a, 24/11/2026).
// AI soạn câu ôn tập bám vào các đoạn này (RAG). Admin xem / thêm / sửa / xóa; nút "AI viết đoạn tài liệu" cho AI viết các
// đoạn còn thiếu (3 đoạn / kỹ năng) từ mô tả các khóa dạy kỹ năng — lưu NGAY (dùng trước, kiểm sau — D1). Kỹ năng phải
// "Mở" ở trang Phạm vi kỹ năng. Docs: docs/Review-AI-Tu-Soan-On-Tap.md mục 7.1.
import { useCallback, useEffect, useState } from 'react';

import * as reviewAdminApi from '../../../api/reviewAdmin.api.js';
import { parseApiError } from '../../../utils/errors.js';

const SOURCE = {
  manual: { text: 'Nhóm soạn', chip: 'chip-ok' },
  ai: { text: 'AI viết', chip: 'chip-info' },
  admin: { text: 'Admin sửa', chip: 'chip-accent' },
};
const MIN_CHARS = 200;
const MAX_CHARS = 1500;

function ChunkForm({ initial, busy, onSave, onCancel }) {
  const [title, setTitle] = useState(initial?.title || '');
  const [content, setContent] = useState(initial?.content || '');
  const length = content.trim().length;
  const ok = length >= MIN_CHARS && length <= MAX_CHARS;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <input className="input" placeholder="Tiêu đề (không bắt buộc)" value={title} maxLength={200}
             onChange={(e) => setTitle(e.target.value)} />
      <textarea className="input" rows={6} placeholder="Nội dung đoạn tài liệu (tiếng Anh, 200–1.500 ký tự)"
                value={content} onChange={(e) => setContent(e.target.value)} />
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
        <span className={`small ${ok ? 'muted' : ''}`} style={ok ? undefined : { color: 'var(--danger-fg)' }}>
          {length} ký tự {ok ? '' : `(cần ${MIN_CHARS}–${MAX_CHARS})`}
        </span>
        <span style={{ flex: 1 }} />
        <button type="button" className="btn btn-sm" onClick={onCancel} disabled={busy}>
          Hủy
        </button>
        <button type="button" className="btn btn-sm btn-primary" disabled={!ok || busy}
                onClick={() => onSave({ title: title.trim() || null, content: content.trim() })}>
          {busy ? 'Đang lưu…' : 'Lưu'}
        </button>
      </div>
    </div>
  );
}

export default function ChunkManager({ skillId, skillName }) {
  const [chunks, setChunks] = useState(null);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null); // chunk_id | 'new' | null
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const load = useCallback(async () => {
    try {
      setChunks(await reviewAdminApi.getSkillChunks(skillId));
    } catch (err) {
      setError(parseApiError(err).message);
      setChunks([]);
    }
  }, [skillId]);

  useEffect(() => {
    setChunks(null);
    setEditing(null);
    setError('');
    setNotice('');
    load();
  }, [load]);

  async function run(action, message) {
    setBusy(true);
    setError('');
    setNotice('');
    try {
      await action();
      setNotice(message);
      setEditing(null);
      await load();
    } catch (err) {
      setError(parseApiError(err).message);
    } finally {
      setBusy(false);
    }
  }

  async function generate() {
    setBusy(true);
    setError('');
    setNotice('');
    try {
      const result = await reviewAdminApi.generateSkillChunks(skillId);
      setNotice(result.created.length ? `AI đã viết ${result.created.length} đoạn mới.` : 'Kỹ năng đã đủ 3 đoạn.');
      setOpen(true);
      await load();
    } catch (err) {
      setError(parseApiError(err).message);
    } finally {
      setBusy(false);
    }
  }

  const count = chunks?.length ?? 0;
  return (
    <section className="card" style={{ padding: '14px 18px', display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
        <button type="button" className="btn btn-sm" aria-expanded={open} onClick={() => setOpen(!open)}>
          {open ? '▾' : '▸'} Đoạn tài liệu ({chunks === null ? '…' : count})
        </button>
        <span className="small muted">
          {skillName} — AI soạn câu ôn tập bám vào các đoạn này{count < 3 && chunks !== null ? ' · chưa đủ 3 đoạn' : ''}
        </span>
        <span style={{ flex: 1 }} />
        <button type="button" className="btn btn-sm btn-soft" disabled={busy || count >= 3} onClick={generate}
                title={count >= 3 ? 'Đã đủ 3 đoạn' : 'AI viết các đoạn còn thiếu từ mô tả khóa học (10–30 giây)'}>
          {busy && editing === null ? 'AI đang viết…' : 'AI viết đoạn tài liệu'}
        </button>
        <button type="button" className="btn btn-sm" disabled={busy || editing !== null}
                onClick={() => { setOpen(true); setEditing('new'); }}>
          + Thêm đoạn
        </button>
      </div>

      {notice && <div className="alert alert-ok">{notice}</div>}
      {error && <div className="alert">{error}</div>}

      {open && editing === 'new' && (
        <div className="card" style={{ padding: 12 }}>
          <ChunkForm busy={busy} onCancel={() => setEditing(null)}
                     onSave={(body) => run(() => reviewAdminApi.createSkillChunk(skillId, body), 'Đã thêm đoạn.')} />
        </div>
      )}

      {open && chunks?.length === 0 && editing !== 'new' && (
        <p className="muted small" style={{ margin: 0 }}>Chưa có đoạn nào. Bấm "AI viết đoạn tài liệu" hoặc "+ Thêm đoạn".</p>
      )}

      {open &&
        chunks?.map((c) => (
          <article key={c.chunk_id} className="card" style={{ padding: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
            {editing === c.chunk_id ? (
              <ChunkForm initial={c} busy={busy} onCancel={() => setEditing(null)}
                         onSave={(body) => run(() => reviewAdminApi.updateChunk(c.chunk_id, body), 'Đã lưu đoạn.')} />
            ) : (
              <>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                  <strong>{c.title || c.code || `Đoạn #${c.chunk_id}`}</strong>
                  <span className={`chip ${SOURCE[c.source]?.chip || 'chip'}`}>{SOURCE[c.source]?.text || c.source}</span>
                  {!c.has_embedding && <span className="chip chip-danger" title="RAG xếp đoạn này cuối">Chưa có vector</span>}
                  <span style={{ flex: 1 }} />
                  <button type="button" className="btn btn-sm" disabled={busy} onClick={() => setEditing(c.chunk_id)}>
                    Sửa
                  </button>
                  <button type="button" className="btn btn-sm" disabled={busy}
                          onClick={() => window.confirm('Xóa đoạn này?') &&
                            run(() => reviewAdminApi.deleteChunk(c.chunk_id), 'Đã xóa đoạn.')}>
                    Xóa
                  </button>
                </div>
                <p className="small" style={{ margin: 0, whiteSpace: 'pre-wrap', lineHeight: 1.55 }}>{c.content}</p>
              </>
            )}
          </article>
        ))}
    </section>
  );
}
