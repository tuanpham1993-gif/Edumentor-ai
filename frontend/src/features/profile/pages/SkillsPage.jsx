// Kỹ năng của tôi (module 01 · Tuấn · FĐ6, 08/11/2026) — màn demo S-10 Skills, route /me/skills.
//   - Tìm & thêm kỹ năng từ danh mục, đổi Đã biết / Đang học, gỡ, khôi phục, hoàn tác tất cả.
//   - Mọi thay đổi nằm trong "bản nháp" (skillDraft.js); bấm "Lưu tất cả" → MỘT request
//     PATCH /api/me/skills. Có lỗi → backend không lưu gì → bản nháp giữ nguyên để sửa.
//   - Rời trang / đóng tab khi còn thay đổi chưa lưu → trình duyệt hỏi lại.
//   - S6 (thầy, 08/11): người dùng sửa / gỡ được mọi kỹ năng, kể cả kỹ năng đạt qua ôn tập.
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import * as meApi from '../../../api/me.api.js';
import Tabs from '../../common/components/Tabs.jsx';
import { parseApiError } from '../../../utils/errors.js';
import { formatDate } from '../../../utils/formatters.js';
import SettingsLayout from '../components/SettingsLayout.jsx';
import SkillSearch from '../components/SkillSearch.jsx';
import {
  addSkill,
  buildChanges,
  changeOf,
  countChanges,
  draftFromServer,
  removeSkill,
  restoreSkill,
  setStatus,
} from '../skillDraft.js';
import styles from '../styles/SkillsPage.module.css';

const SOURCE_NOTE = {
  review: 'Xác nhận qua bài ôn tập',
  course: 'Từ khóa học đã tham gia',
};
const EMPTY_TEXT = {
  all: 'Chưa có kỹ năng nào. Tìm và thêm kỹ năng ở ô phía trên.',
  known: 'Chưa có kỹ năng nào ở trạng thái Đã biết.',
  learning: 'Chưa có kỹ năng nào ở trạng thái Đang học.',
};

// Backend báo lỗi theo mã kỹ năng, vd "…: [305]." → đổi thành tên đang hiện trên bảng: "…: SQL."
function withSkillNames(message, rows) {
  return message.replace(/\[([\d,\s]+)\]/, (whole, ids) => {
    const names = ids
      .split(',')
      .map((id) => rows.find((row) => row.skill_id === Number(id))?.skill)
      .filter(Boolean);
    return names.length ? names.map((n) => `"${n}"`).join(', ') : whole;
  });
}

function TrashIcon() {
  return (
    <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4h6v3" />
    </svg>
  );
}

export default function SkillsPage() {
  const [saved, setSaved] = useState([]); // đúng như trên server (để Hoàn tác không cần tải lại)
  const [rows, setRows] = useState([]); // bản nháp
  const [loadState, setLoadState] = useState('loading'); // loading | ready | error
  const [tab, setTab] = useState('all');
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState(null); // { ok, text }

  const load = useCallback(async () => {
    setLoadState('loading');
    try {
      const skills = await meApi.getMySkills();
      setSaved(skills);
      setRows(draftFromServer(skills));
      setNotice(null);
      setLoadState('ready');
    } catch {
      setLoadState('error');
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const pending = countChanges(rows);

  // Còn thay đổi chưa lưu → hỏi lại khi tải lại / đóng tab
  useEffect(() => {
    if (pending === 0) return undefined;
    const warn = (event) => {
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [pending]);

  const visible = rows.filter((row) => !row.removed);
  const counts = {
    all: visible.length,
    known: visible.filter((r) => r.status === 'known').length,
    learning: visible.filter((r) => r.status === 'learning').length,
  };
  // Tab "Tất cả" còn hiện dòng đang bị gỡ (gạch ngang) để khôi phục được
  const shown = tab === 'all' ? rows : visible.filter((r) => r.status === tab);
  const excludeIds = new Set(visible.map((r) => r.skill_id));

  function edit(next) {
    setRows(next);
    setNotice(null);
  }

  async function handleSave() {
    setSaving(true);
    setNotice(null);
    try {
      const skills = await meApi.updateMySkills(buildChanges(rows));
      setSaved(skills);
      setRows(draftFromServer(skills));
      setNotice({ ok: true, text: `Đã lưu ${pending} thay đổi.` });
    } catch (err) {
      const { status, message } = parseApiError(err);
      const text = withSkillNames(message, rows);
      // 404 / 409: dữ liệu trên màn hình đã cũ (vd sửa ở tab khác) → gợi ý tải lại
      const stale = status === 404 || status === 409;
      setNotice({
        ok: false,
        text: stale ? `${text} Dữ liệu có thể đã thay đổi ở nơi khác — hãy tải lại.` : text,
        reload: stale,
      });
    } finally {
      setSaving(false);
    }
  }

  return (
    <SettingsLayout>
      <h2>Kỹ năng của tôi</h2>
      <p>
        Đánh dấu kỹ năng bạn đã biết hoặc đang học. Khi làm đạt bài ôn tập, kỹ năng của khóa học tự
        chuyển sang Đã biết.
      </p>

      {notice && (
        <div className={`alert ${notice.ok ? 'alert-ok' : ''}`} role={notice.ok ? 'status' : 'alert'}>
          {notice.text}
          {notice.reload && (
            <button type="button" className="btn btn-sm" style={{ marginLeft: 12 }} onClick={load}>
              Tải lại
            </button>
          )}
        </div>
      )}

      {loadState === 'error' ? (
        <div className="alert" role="alert">
          Không tải được kỹ năng của bạn.
          <button type="button" className="btn btn-sm" style={{ marginLeft: 12 }} onClick={load}>
            Thử lại
          </button>
        </div>
      ) : (
        <>
          <SkillSearch
            excludeIds={excludeIds}
            refreshKey={saved.map((s) => s.skill_id).join(',')}
            disabled={loadState !== 'ready' || saving}
            onAdd={(skill, status) => edit(addSkill(rows, skill, status))}
          />

          <p className="small muted" style={{ margin: '-8px 0 0' }}>
            Không nhớ tên kỹ năng?{' '}
            <Link
              to="/me/skills/browse"
              style={{ fontWeight: 600 }}
              onClick={(event) => {
                // Còn thay đổi chưa lưu → hỏi trước khi rời trang (bản nháp sẽ mất)
                if (pending > 0 && !window.confirm('Bạn còn thay đổi chưa lưu. Rời trang và bỏ các thay đổi này?')) {
                  event.preventDefault();
                }
              }}
            >
              Duyệt kỹ năng theo danh mục →
            </Link>
          </p>

          <Tabs
            label="Lọc kỹ năng"
            value={tab}
            onChange={setTab}
            items={[
              { value: 'all', text: 'Tất cả', count: counts.all },
              { value: 'known', text: 'Đã biết', count: counts.known },
              { value: 'learning', text: 'Đang học', count: counts.learning },
            ]}
          />

          <div className="card table-wrap" style={{ background: 'var(--card-inner)' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Kỹ năng</th>
                  <th>Trạng thái</th>
                  <th className={styles.colDate}>Cập nhật</th>
                  <th aria-label="Thao tác" />
                </tr>
              </thead>
              <tbody>
                {loadState === 'loading' &&
                  [0, 1, 2].map((i) => (
                    <tr key={i} aria-hidden="true">
                      <td colSpan={4}>
                        <div className="skeleton" style={{ height: 20 }} />
                      </td>
                    </tr>
                  ))}

                {loadState === 'ready' && shown.length === 0 && (
                  <tr>
                    <td colSpan={4} className={styles.empty}>
                      {EMPTY_TEXT[tab]}
                    </td>
                  </tr>
                )}

                {loadState === 'ready' &&
                  shown.map((row) => {
                    const change = changeOf(row);
                    return (
                      <tr
                        key={row.skill_id}
                        className={change === 'removed' ? styles.removed : change ? styles.added : ''}
                      >
                        <td>
                          <span className={styles.name}>{row.skill}</span>
                          {SOURCE_NOTE[row.source] && change !== 'changed' && (
                            <span className={styles.note}>{SOURCE_NOTE[row.source]}</span>
                          )}
                          {change === 'added' && <span className={styles.tag}>Mới</span>}
                          {change === 'changed' && <span className={styles.tag}>Đã đổi</span>}
                        </td>
                        <td>
                          <select
                            aria-label={`Trạng thái ${row.skill}`}
                            className={`${styles.selectSm} ${row.status === 'known' ? styles.selKnown : styles.selLearning}`}
                            value={row.status}
                            disabled={row.removed || saving}
                            onChange={(event) => edit(setStatus(rows, row.skill_id, event.target.value))}
                          >
                            <option value="known">Đã biết</option>
                            <option value="learning">Đang học</option>
                          </select>
                        </td>
                        <td className={`muted ${styles.colDate}`}>
                          {row.updated_at ? formatDate(row.updated_at) : '—'}
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          {row.removed ? (
                            <button
                              type="button"
                              className="btn btn-sm"
                              disabled={saving}
                              onClick={() => edit(restoreSkill(rows, row.skill_id))}
                            >
                              Khôi phục
                            </button>
                          ) : (
                            <button
                              type="button"
                              className="icon-btn danger"
                              aria-label={`Gỡ ${row.skill}`}
                              title="Gỡ khỏi hồ sơ"
                              disabled={saving}
                              onClick={() => edit(removeSkill(rows, row.skill_id))}
                            >
                              <TrashIcon />
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </>
      )}

      {pending > 0 && (
        <div className={styles.bar} role="status">
          <span>
            <b>{pending}</b> thay đổi chưa lưu
          </span>
          <div className="row" style={{ gap: 8 }}>
            <button
              type="button"
              className="btn btn-sm"
              disabled={saving}
              onClick={() => edit(draftFromServer(saved))}
            >
              Hoàn tác
            </button>
            <button
              type="button"
              className={`btn btn-sm btn-primary ${saving ? 'loading' : ''}`}
              disabled={saving}
              onClick={handleSave}
            >
              Lưu tất cả
              <span className="spinner" aria-hidden="true" />
            </button>
          </div>
        </div>
      )}
    </SettingsLayout>
  );
}
