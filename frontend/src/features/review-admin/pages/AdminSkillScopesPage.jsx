// Phạm vi kỹ năng — /admin/skill-scopes (module 09 · Tuấn · G3.0, 24/11/2026).
// Mỗi kỹ năng một nhãn: AI có được TỰ SOẠN câu ôn tập cho kỹ năng đó không (docs/guide.md Q8, sửa 22/11).
//   Mở       = câu có đáp án đúng rõ ràng VÀ nhóm / học viên nhận ra khi AI soạn sai (Docker, SQL, Excel, Scrum…)
//   Không mở = kỹ năng mềm, chuyên ngành nhóm không kiểm chứng được (Workday, điều dưỡng…)
//   Chưa rõ  = mặc định CHƯA mở — admin xem và bật nếu hợp
// AI gắn nhãn một lần (script classify_skill_scopes); admin đổi ở đây → nguồn "Admin", chạy lại không ghi đè.
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import * as reviewAdminApi from '../../../api/reviewAdmin.api.js';
import { parseApiError } from '../../../utils/errors.js';
import styles from '../styles/AdminReviewFlags.module.css';

const PAGE_SIZE = 20;

export const LABEL_TEXT = { open: 'Mở', closed: 'Không mở', unsure: 'Chưa rõ' };
const LABEL_CHIP = { open: 'chip-ok', closed: 'chip-danger', unsure: 'chip' };
export const CATEGORY_TEXT = {
  programming: 'Lập trình',
  software_tools: 'Công cụ phần mềm',
  data_bi: 'Dữ liệu / BI',
  infra_security: 'Hạ tầng / bảo mật',
  software_process: 'Quy trình phần mềm',
  math_science: 'Toán / khoa học',
  business_domain: 'Kinh doanh',
  soft_skill: 'Kỹ năng mềm',
  specialized_domain: 'Chuyên ngành',
  other: 'Khác',
};

export default function AdminSkillScopesPage() {
  const [label, setLabel] = useState('');
  const [category, setCategory] = useState('');
  const [source, setSource] = useState('');
  const [query, setQuery] = useState('');
  const [q, setQ] = useState(''); // giá trị đã "chốt" sau khi ngừng gõ
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [saving, setSaving] = useState(null); // skill_id đang lưu

  useEffect(() => {
    const t = setTimeout(() => {
      setQ(query.trim());
      setPage(1);
    }, 350);
    return () => clearTimeout(t);
  }, [query]);

  const load = useCallback(async () => {
    setError('');
    try {
      const params = { page, size: PAGE_SIZE };
      if (label) params.label = label;
      if (category) params.category = category;
      if (source) params.source = source;
      if (q) params.q = q;
      setData(await reviewAdminApi.listSkillScopes(params));
    } catch (err) {
      setError(parseApiError(err).message);
      setData({ items: [], total: 0, counts: { open: 0, closed: 0, unsure: 0, unlabeled: 0 } });
    }
  }, [label, category, source, q, page]);

  useEffect(() => {
    load();
  }, [load]);

  function choose(setter, value) {
    setter(value);
    setPage(1);
    setNotice('');
  }

  async function changeLabel(item, newLabel) {
    if (!newLabel || newLabel === item.label) return;
    setSaving(item.skill_id);
    setNotice('');
    setError('');
    try {
      await reviewAdminApi.updateSkillScope(item.skill_id, { label: newLabel });
      setNotice(`Đã đặt "${item.skill}" → ${LABEL_TEXT[newLabel]}.`);
      await load();
    } catch (err) {
      setError(parseApiError(err).message);
    } finally {
      setSaving(null);
    }
  }

  const counts = data?.counts;
  const pages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;
  const segments = [
    ['', 'Tất cả'],
    ['open', `Mở${counts ? ` (${counts.open})` : ''}`],
    ['closed', `Không mở${counts ? ` (${counts.closed})` : ''}`],
    ['unsure', `Chưa rõ${counts ? ` (${counts.unsure})` : ''}`],
    ['unlabeled', `Chưa có nhãn${counts ? ` (${counts.unlabeled})` : ''}`],
  ];

  return (
    <div className={styles.page}>
      <header className={styles.head}>
        <div>
          <h1 className={styles.title}>Phạm vi kỹ năng</h1>
          <p className="muted small" style={{ margin: 0 }}>
            AI chỉ tự soạn câu ôn tập cho kỹ năng <b>Mở</b>: câu có đáp án đúng rõ ràng và nhóm nhận ra khi AI soạn sai.
            Chưa rõ / chưa có nhãn = chưa mở. Kỹ năng đã có ngân hàng câu soạn tay luôn ôn được.
          </p>
        </div>
        <Link to="/admin/questions" className="btn btn-sm">
          ← Câu hỏi ôn tập
        </Link>
      </header>

      <div className={`card ${styles.filters}`}>
        <div className={styles.seg} role="radiogroup" aria-label="Nhãn">
          {segments.map(([value, text]) => (
            <button
              key={value || 'all'}
              type="button"
              role="radio"
              aria-checked={label === value}
              className={label === value ? styles.segOn : ''}
              onClick={() => choose(setLabel, value)}
            >
              {text}
            </button>
          ))}
        </div>
        <select className="select" aria-label="Nhóm" value={category} onChange={(e) => choose(setCategory, e.target.value)}>
          <option value="">Nhóm: tất cả</option>
          {Object.entries(CATEGORY_TEXT).map(([value, text]) => (
            <option key={value} value={value}>
              {text}
            </option>
          ))}
        </select>
        <select className="select" aria-label="Nguồn" value={source} onChange={(e) => choose(setSource, e.target.value)}>
          <option value="">Nguồn: tất cả</option>
          <option value="ai">AI gắn</option>
          <option value="admin">Admin sửa</option>
        </select>
        <input
          className="input"
          style={{ maxWidth: 260 }}
          type="search"
          placeholder="Tìm tên kỹ năng…"
          aria-label="Tìm tên kỹ năng"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {notice && <div className="alert alert-ok">{notice}</div>}
      {error && <div className="alert">{error}</div>}

      {data === null ? (
        <p className="muted">Đang tải…</p>
      ) : data.items.length === 0 ? (
        <div className={`card ${styles.empty}`}>Không có kỹ năng nào khớp bộ lọc.</div>
      ) : (
        <div className={`card ${styles.tableWrap}`}>
          <table className="table">
            <thead>
              <tr>
                <th>Kỹ năng</th>
                <th>Nhóm</th>
                <th>Nhãn</th>
                <th>Lý do</th>
                <th>Nguồn</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr key={item.skill_id}>
                  <td>
                    {item.skill} <span className="muted small">#{item.skill_id}</span>
                  </td>
                  <td className="small">{item.category ? CATEGORY_TEXT[item.category] : '—'}</td>
                  <td>
                    <select
                      className="select"
                      aria-label={`Nhãn của ${item.skill}`}
                      value={item.label ?? ''}
                      disabled={saving === item.skill_id}
                      onChange={(e) => changeLabel(item, e.target.value)}
                    >
                      {!item.label && <option value="">Chưa có nhãn</option>}
                      {Object.entries(LABEL_TEXT).map(([value, text]) => (
                        <option key={value} value={value}>
                          {text}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="small muted">{item.reason || '—'}</td>
                  <td>
                    {item.source ? (
                      <span className={`chip ${item.source === 'admin' ? 'chip-info' : LABEL_CHIP[item.label]}`}>
                        {item.source === 'admin' ? `Admin${item.updated_by_name ? ` · ${item.updated_by_name}` : ''}` : 'AI'}
                      </span>
                    ) : (
                      '—'
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data && pages > 1 && (
        <nav className={styles.pager} aria-label="Phân trang">
          <button type="button" className="btn btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            ← Trước
          </button>
          <span className="small muted">
            Trang {page}/{pages} · {data.total} kỹ năng
          </span>
          <button type="button" className="btn btn-sm" disabled={page >= pages} onClick={() => setPage(page + 1)}>
            Sau →
          </button>
        </nav>
      )}
    </div>
  );
}
