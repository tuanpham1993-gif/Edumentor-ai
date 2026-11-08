// Khám phá kỹ năng theo danh mục (module 01 · Tuấn · FĐ6, 08/11/2026 — gợi ý của thầy) — /me/skills/browse
//   - Danh mục (chip, có số lượng) · tìm trong danh mục · sắp xếp Phổ biến / A–Z · phân trang 24 / trang.
//   - Mỗi kỹ năng: số khóa học dạy nó; đã có trong hồ sơ → nhãn "Đã có"; chưa có → chọn Đã biết / Đang học.
//   - Chọn nhiều kỹ năng (giữ khi đổi trang / danh mục) → "Thêm vào hồ sơ" = MỘT request PATCH /me/skills (add).
//   - Danh mục / trang / chữ tìm nằm trên URL (?category=ai&page=2) → nút Back của trình duyệt hoạt động.
// Danh mục do backend phân loại theo từ khóa (app/utils/skill_categories.py) — là ước lượng.
import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import * as meApi from '../../../api/me.api.js';
import { parseApiError } from '../../../utils/errors.js';
import Pagination from '../../common/components/Pagination.jsx';
import SettingsLayout from '../components/SettingsLayout.jsx';
import styles from '../styles/SkillBrowsePage.module.css';

const SIZE = 24;
const STATUS_TEXT = { known: 'Đã biết', learning: 'Đang học' };

export default function SkillBrowsePage() {
  const [params, setParams] = useSearchParams();
  const category = params.get('category') || '';
  const sort = params.get('sort') === 'name' ? 'name' : 'popular';
  const page = Math.max(1, Number(params.get('page')) || 1);
  const q = params.get('q') || '';

  const [categories, setCategories] = useState([]);
  const [data, setData] = useState(null); // trang hiện tại; null = đang tải
  const [error, setError] = useState('');
  const [search, setSearch] = useState(q); // chữ đang gõ (đẩy lên URL sau 300 ms)
  const [picked, setPicked] = useState({}); // { skill_id: { skill, status } } — chưa lưu
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState(null);
  const [reloadKey, setReloadKey] = useState(0);
  const catsRef = useRef(null);

  // Điện thoại: hàng chip vuốt ngang → tự cuộn để chip đang chọn luôn nhìn thấy
  useEffect(() => {
    const row = catsRef.current;
    const activeChip = row?.querySelector('[aria-pressed="true"]');
    if (row && activeChip && row.scrollWidth > row.clientWidth) {
      row.scrollTo({ left: activeChip.offsetLeft - (row.clientWidth - activeChip.offsetWidth) / 2 });
    }
  }, [category, categories]);

  /** Đổi tham số trên URL; đổi bộ lọc thì về trang 1.
   *  replace=true (khi gõ tìm): THAY mục lịch sử hiện tại → nút Back không phải bấm qua từng chữ đã gõ. */
  const update = useCallback(
    (changes, resetPage = true, replace = false) => {
      const next = new URLSearchParams(params);
      Object.entries(changes).forEach(([k, v]) => (v ? next.set(k, v) : next.delete(k)));
      if (resetPage) next.delete('page');
      if (next.toString() === params.toString()) return; // không đổi gì → không thêm lịch sử
      setParams(next, { replace });
    },
    [params, setParams],
  );

  useEffect(() => {
    meApi.getSkillCategories().then(setCategories).catch(() => setCategories([]));
  }, [reloadKey]);

  useEffect(() => {
    let cancelled = false;
    setData(null);
    setError('');
    meApi
      .browseSkillCatalog({ category: category || undefined, q: q || undefined, sort, page, size: SIZE })
      .then((d) => !cancelled && setData(d))
      .catch((err) => !cancelled && setError(parseApiError(err).message));
    return () => {
      cancelled = true;
    };
  }, [category, q, sort, page, reloadKey]);

  // URL đổi từ bên ngoài (nút Back / Forward, bấm danh mục) → ô tìm hiện đúng chữ trên URL.
  // Không có bước này: Back về trang chưa tìm nhưng ô vẫn còn chữ cũ → lại tự đẩy chữ đó lên URL.
  useEffect(() => {
    setSearch((current) => (current.trim() === q ? current : q));
  }, [q]);

  // Gõ tìm → chờ 300 ms rồi mới đổi URL (đỡ gọi API mỗi phím)
  useEffect(() => {
    if (search.trim() === q) return undefined;
    const timer = setTimeout(() => update({ q: search.trim() }, true, true), 300);
    return () => clearTimeout(timer);
  }, [search, q, update]);

  const pickedList = Object.entries(picked);
  useEffect(() => {
    if (pickedList.length === 0) return undefined;
    const warn = (event) => {
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [pickedList.length]);

  function toggle(item, status) {
    setNotice(null);
    setPicked((prev) => {
      const next = { ...prev };
      if (next[item.skill_id]?.status === status) delete next[item.skill_id];
      else next[item.skill_id] = { skill: item.skill, status };
      return next;
    });
  }

  async function handleSave() {
    setSaving(true);
    setNotice(null);
    try {
      await meApi.updateMySkills({
        add: pickedList.map(([id, p]) => ({ skill_id: Number(id), status: p.status })),
      });
      setNotice({ ok: true, text: `Đã thêm ${pickedList.length} kỹ năng vào hồ sơ.` });
      setPicked({});
      setReloadKey((k) => k + 1); // tải lại để hiện nhãn "Đã có"
    } catch (err) {
      const { status, message } = parseApiError(err);
      setNotice({
        ok: false,
        text: status === 409 ? `${message} Hãy bỏ chọn kỹ năng đã có rồi thử lại.` : message,
      });
      if (status === 409) setReloadKey((k) => k + 1);
    } finally {
      setSaving(false);
    }
  }

  const totalAll = categories.reduce((sum, c) => sum + c.count, 0);
  const labelOf = Object.fromEntries(categories.map((c) => [c.key, c.label]));
  const totalPages = data ? Math.max(1, Math.ceil(data.total / SIZE)) : 1;

  return (
    <SettingsLayout back={{ to: '/me/skills', label: 'Kỹ năng của tôi' }}>
      <h2>Khám phá kỹ năng</h2>
      <p>Duyệt kỹ năng theo danh mục, chọn những kỹ năng bạn đã biết hoặc đang học rồi thêm vào hồ sơ.</p>

      {notice && (
        <div className={`alert ${notice.ok ? 'alert-ok' : ''}`} role={notice.ok ? 'status' : 'alert'}>
          {notice.text}{' '}
          {notice.ok && (
            <Link to="/me/skills" style={{ fontWeight: 600 }}>
              Xem Kỹ năng của tôi →
            </Link>
          )}
        </div>
      )}

      {/* Danh mục */}
      <div ref={catsRef} className={styles.cats} role="group" aria-label="Danh mục kỹ năng">
        <button
          type="button"
          className={`${styles.cat} ${!category ? styles.catActive : ''}`}
          aria-pressed={!category}
          onClick={() => update({ category: '' })}
        >
          Tất cả <span>{totalAll || ''}</span>
        </button>
        {categories.map((c) => (
          <button
            key={c.key}
            type="button"
            className={`${styles.cat} ${category === c.key ? styles.catActive : ''}`}
            aria-pressed={category === c.key}
            onClick={() => update({ category: c.key })}
          >
            {c.label} <span>{c.count}</span>
          </button>
        ))}
      </div>

      {/* Tìm + sắp xếp */}
      <div className={styles.toolbar}>
        <label className="field" htmlFor="browse-q" style={{ flex: '1 1 240px' }}>
          <span className="sr-only">Tìm kỹ năng</span>
          <span className="input">
            <input
              id="browse-q"
              placeholder={category ? `Tìm trong "${labelOf[category] ?? ''}"` : 'Tìm trong tất cả kỹ năng'}
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </span>
        </label>
        <label className="field" htmlFor="browse-sort" style={{ flex: '0 1 200px' }}>
          <span className="sr-only">Sắp xếp</span>
          <select
            id="browse-sort"
            className="select"
            value={sort}
            onChange={(event) => update({ sort: event.target.value === 'name' ? 'name' : '' })}
          >
            <option value="popular">Phổ biến nhất</option>
            <option value="name">Tên A–Z</option>
          </select>
        </label>
      </div>

      {error && (
        <div className="alert" role="alert">
          {error}{' '}
          <button type="button" className="btn btn-sm" onClick={() => setReloadKey((k) => k + 1)}>
            Thử lại
          </button>
        </div>
      )}

      {data && (
        <p className="small muted" style={{ margin: 0 }}>
          {data.total} kỹ năng{q ? ` khớp "${q}"` : ''} · trang {page}/{totalPages}
        </p>
      )}

      {/* Lưới kỹ năng */}
      <ul className={styles.grid} aria-busy={data === null}>
        {data === null &&
          Array.from({ length: 9 }, (_, i) => (
            <li key={i} className="skeleton" style={{ height: 96 }} aria-hidden="true" />
          ))}
        {data?.items.map((item) => {
          const mine = item.my_status;
          const choice = picked[item.skill_id]?.status;
          return (
            <li
              key={item.skill_id}
              className={`${styles.item} ${choice ? styles.itemPicked : ''} ${mine ? styles.itemMine : ''}`}
            >
              <div className={styles.itemHead}>
                <strong>{item.skill}</strong>
                <span className="small muted">
                  {item.course_count > 0 ? `${item.course_count} khóa học` : 'Chưa có khóa học'}
                  {!category && labelOf[item.category] ? ` · ${labelOf[item.category]}` : ''}
                </span>
              </div>
              {mine ? (
                <span className={`chip ${mine === 'known' ? 'chip-accent' : 'chip-info'}`}>
                  Đã có · {STATUS_TEXT[mine]}
                </span>
              ) : (
                <div className={styles.choices} role="group" aria-label={`Thêm ${item.skill}`}>
                  {['known', 'learning'].map((status) => (
                    <button
                      key={status}
                      type="button"
                      className={`${styles.choice} ${choice === status ? styles.choiceOn : ''}`}
                      aria-pressed={choice === status}
                      onClick={() => toggle(item, status)}
                    >
                      {choice === status ? '✓ ' : '+ '}
                      {STATUS_TEXT[status]}
                    </button>
                  ))}
                </div>
              )}
            </li>
          );
        })}
      </ul>
      {data && data.items.length === 0 && (
        <p className={styles.empty}>Không có kỹ năng nào khớp. Thử danh mục khác hoặc bỏ chữ tìm.</p>
      )}

      <Pagination
        page={page}
        totalPages={totalPages}
        onChange={(p) => {
          update({ page: p > 1 ? String(p) : '' }, false);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
      />

      {pickedList.length > 0 && (
        <div className={styles.bar} role="status">
          <span>
            Đã chọn <b>{pickedList.length}</b> kỹ năng
          </span>
          <div className="row" style={{ gap: 8 }}>
            <button type="button" className="btn btn-sm" disabled={saving} onClick={() => setPicked({})}>
              Bỏ chọn
            </button>
            <button
              type="button"
              className={`btn btn-sm btn-primary ${saving ? 'loading' : ''}`}
              disabled={saving}
              onClick={handleSave}
            >
              Thêm vào hồ sơ
              <span className="spinner" aria-hidden="true" />
            </button>
          </div>
        </div>
      )}
    </SettingsLayout>
  );
}
