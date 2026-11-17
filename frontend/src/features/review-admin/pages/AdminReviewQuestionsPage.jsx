// Câu hỏi ôn tập — trang quản trị ngân hàng câu hỏi /admin/questions (module 09 · Tuấn · 7.6, 16/11/2026).
// Demo chuẩn: Downloads/AdminReviewQuestions.html.
//
// Đợt này (P1): mức sẵn sàng từng khóa (7.4) · lọc khóa / kỹ năng / trạng thái / loại / mức + tìm · bảng câu hỏi
// (bật / tắt, xem đáp án / barem, lịch sử phiên bản) · duyệt / từ chối câu AI soạn (7.5c: câu AI chỉ vào đề sau khi duyệt).
// P2 (16/11): sửa câu ngay trong dòng — lưu phiên bản mới / sửa nhỏ (QuestionEditor). Đợt sau: thêm câu (P3), chấm thử (P4).
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import * as reviewAdminApi from '../../../api/reviewAdmin.api.js';
import { parseApiError } from '../../../utils/errors.js';
import QuestionEditor, { blankQuestion } from '../components/QuestionEditor.jsx';
import QuestionRow from '../components/QuestionRow.jsx';
import ReadinessPanel from '../components/ReadinessPanel.jsx';
import { LEVEL_FILTERS, STATUS_FILTERS, TYPE_FILTERS } from '../reviewAdminFormat.js';
import styles from '../styles/AdminReviewQuestions.module.css';

const PAGE_SIZE = 20;
const SEARCH_DELAY_MS = 400;
const EMPTY_FILTERS = { course: '', skill: '', status: '', type: '', level: '', q: '' };

function toParams(filters, page) {
  const status = STATUS_FILTERS.find((s) => s.value === filters.status) || STATUS_FILTERS[0];
  const params = { ...status.params, page, size: PAGE_SIZE };
  if (filters.course) params.course_id = filters.course;
  if (filters.skill) params.skill_id = filters.skill;
  if (filters.type) params.type = filters.type;
  if (filters.level) params.level = filters.level;
  if (filters.q.trim()) params.q = filters.q.trim();
  return params;
}

export default function AdminReviewQuestionsPage() {
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [search, setSearch] = useState(''); // ô tìm — đẩy vào filters sau SEARCH_DELAY_MS
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null); // null = đang tải
  const [summary, setSummary] = useState(null); // mức sẵn sàng mọi khóa (tóm tắt)
  const [courseDetail, setCourseDetail] = useState(null); // mức sẵn sàng khóa đang chọn (kèm kỹ năng)
  const [counts, setCounts] = useState({ active: null, pending: null });
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [newQuestion, setNewQuestion] = useState(null); // P3: câu trống đang soạn trong form "Thêm câu hỏi"
  const [reloadKey, setReloadKey] = useState(0); // tăng → tải lại bảng (sau khi thêm câu)

  const loadCounts = useCallback(async () => {
    try {
      const [active, pending, flags] = await Promise.all([
        reviewAdminApi.listQuestions({ is_active: true, size: 1 }),
        reviewAdminApi.listQuestions({ review_status: 'pending', size: 1 }),
        reviewAdminApi.listFlags({ status: 'open', size: 1 }).catch(() => null),
      ]);
      setCounts({ active: active.total, pending: pending.total, flags: flags?.open_total ?? 0 });
    } catch {
      // chỉ là số trên tiêu đề — lỗi thật sẽ hiện ở bảng
    }
  }, []);

  const loadSummary = useCallback(async () => {
    try {
      const result = await reviewAdminApi.getReadiness();
      setSummary(result);
      // lần đầu: chọn sẵn khóa đứng đầu (ôn được, nhiều câu nhất) như demo
      setFilters((f) =>
        f.course || !result.courses.length ? f : { ...f, course: String(result.courses[0].course_id) },
      );
    } catch (err) {
      setError(parseApiError(err).message);
    }
  }, []);

  useEffect(() => {
    loadSummary();
    loadCounts();
  }, [loadSummary, loadCounts]);

  // khóa đang chọn → bảng từng kỹ năng + danh sách kỹ năng cho ô lọc
  useEffect(() => {
    if (!filters.course) {
      setCourseDetail(null);
      return undefined;
    }
    let alive = true;
    reviewAdminApi
      .getReadiness(filters.course)
      .then((r) => alive && setCourseDetail(r.courses[0] || null))
      .catch((err) => alive && setError(parseApiError(err).message));
    return () => {
      alive = false;
    };
  }, [filters.course, summary]);

  // danh sách câu hỏi theo bộ lọc
  useEffect(() => {
    let alive = true;
    setData(null);
    reviewAdminApi
      .listQuestions(toParams(filters, page))
      .then((result) => alive && setData(result))
      .catch((err) => {
        if (!alive) return;
        setError(parseApiError(err).message);
        setData({ total: 0, page, size: PAGE_SIZE, items: [] });
      });
    return () => {
      alive = false;
    };
  }, [filters, page, reloadKey]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setFilters((f) => (f.q === search ? f : { ...f, q: search }));
      setPage(1);
    }, SEARCH_DELAY_MS);
    return () => clearTimeout(timer);
  }, [search]);

  function setFilter(key, value) {
    setFilters((f) => ({ ...f, [key]: value, ...(key === 'course' ? { skill: '' } : {}) }));
    setPage(1);
    setNotice('');
  }

  // replacedId: lưu phiên bản mới → dòng cũ (id cũ) được thay bằng phiên bản mới (id mới)
  function handleChanged(updated, message, replacedId = updated.question_id) {
    setData((d) => ({
      ...d,
      items: d.items.map((q) => (q.question_id === replacedId ? { ...q, ...updated } : q)),
    }));
    if (message) setNotice(message);
    loadCounts();
    loadSummary(); // số câu đang bật / chờ duyệt của khóa đổi theo
  }

  const pages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;
  const skills = courseDetail?.skills || [];

  // Thêm câu: kỹ năng mặc định = kỹ năng đang lọc, không thì kỹ năng đầu của khóa đang chọn
  function startCreate() {
    const skill = skills.find((s) => String(s.skill_id) === filters.skill) || skills[0];
    setNotice('');
    setNewQuestion(blankQuestion('mcq', skill.skill_id, skill.skill));
  }

  function handleCreated(_question, message) {
    setNewQuestion(null);
    setNotice(message);
    setReloadKey((k) => k + 1);
    loadCounts();
    loadSummary();
  }

  return (
    <div className={styles.page}>
      <header className={styles.head}>
        <div>
          <h1 className={styles.title}>Câu hỏi ôn tập</h1>
          <p className="muted small">
            Ngân hàng câu hỏi theo kỹ năng
            {counts.active !== null && ` · ${counts.active} câu đang bật`}
            {counts.pending ? ` · ${counts.pending} câu AI soạn chờ duyệt` : ''}
          </p>
        </div>
        <div className={styles.buttons}>
          <Link to="/admin/review-flags" className={`btn btn-sm ${counts.flags ? 'btn-soft' : ''}`}>
            Bài cần xem lại{counts.flags ? ` (${counts.flags})` : ''}
          </Link>
          {counts.pending > 0 && filters.status !== 'pending' && (
            <button type="button" className="btn btn-soft btn-sm" onClick={() => setFilter('status', 'pending')}>
              Xem {counts.pending} câu chờ duyệt
            </button>
          )}
          <button
            type="button"
            className="btn btn-primary btn-sm"
            disabled={!skills.length || newQuestion !== null}
            title={skills.length ? undefined : 'Chọn khóa học trước để chọn kỹ năng'}
            onClick={startCreate}
          >
            + Thêm câu hỏi
          </button>
        </div>
      </header>

      <ReadinessPanel
        summary={summary}
        detail={courseDetail}
        selectedCourseId={filters.course ? Number(filters.course) : null}
        onSelectCourse={(id) => setFilter('course', id ? String(id) : '')}
        onPickSkill={(id) => setFilter('skill', String(id))}
      />

      <div className={`card ${styles.filters}`}>
        <select
          className="select"
          aria-label="Khóa học"
          value={filters.course}
          onChange={(e) => setFilter('course', e.target.value)}
        >
          <option value="">Khóa học: tất cả</option>
          {(summary?.courses || []).map((c) => (
            <option key={c.course_id} value={c.course_id}>
              {c.ready ? '✓ ' : ''}
              {c.title}
            </option>
          ))}
        </select>
        <select
          className="select"
          aria-label="Kỹ năng"
          value={filters.skill}
          disabled={!skills.length}
          title={skills.length ? undefined : 'Chọn khóa học trước'}
          onChange={(e) => setFilter('skill', e.target.value)}
        >
          <option value="">Kỹ năng: tất cả</option>
          {skills.map((s) => (
            <option key={s.skill_id} value={s.skill_id}>
              {s.skill}
            </option>
          ))}
        </select>
        <select
          className="select"
          aria-label="Trạng thái"
          value={filters.status}
          onChange={(e) => setFilter('status', e.target.value)}
        >
          {STATUS_FILTERS.map((s) => (
            <option key={s.value} value={s.value}>
              {s.value ? s.text : 'Trạng thái: tất cả'}
              {s.value === 'pending' && counts.pending ? ` (${counts.pending})` : ''}
            </option>
          ))}
        </select>
        <select className="select" aria-label="Loại" value={filters.type} onChange={(e) => setFilter('type', e.target.value)}>
          {TYPE_FILTERS.map((t) => (
            <option key={t.value} value={t.value}>
              {t.text}
            </option>
          ))}
        </select>
        <select
          className="select"
          aria-label="Mức độ"
          value={filters.level}
          onChange={(e) => setFilter('level', e.target.value)}
        >
          {LEVEL_FILTERS.map((l) => (
            <option key={l.value} value={l.value}>
              {l.text}
            </option>
          ))}
        </select>
        <span className={`input ${styles.search}`}>
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm theo nội dung hoặc mã câu"
            aria-label="Tìm câu hỏi"
            maxLength={200}
          />
        </span>
      </div>

      {newQuestion && (
        <div className={`card ${styles.readyDetail}`}>
          <QuestionEditor
            detail={newQuestion}
            skills={skills}
            onSaved={handleCreated}
            onCancel={() => setNewQuestion(null)}
          />
        </div>
      )}

      {notice && (
        <div className="alert alert-ok" role="status">
          {notice}
        </div>
      )}
      {error && <div className="alert">{error}</div>}

      {data === null ? (
        <p className="muted">Đang tải…</p>
      ) : data.items.length === 0 ? (
        <div className={`card ${styles.empty}`}>
          <p>Không có câu hỏi nào khớp bộ lọc.</p>
          {filters.status === 'pending' && (
            <p className="muted small">
              Câu chờ duyệt xuất hiện khi chạy AI_MODE=real và một kỹ năng có ít hơn số câu mục tiêu trong ngân hàng.
            </p>
          )}
        </div>
      ) : (
        <>
          <p className="muted small">
            {data.total} câu · bấm nội dung để xem đáp án / barem
            {filters.status === 'pending' ? ' và duyệt' : ''}
          </p>
          <div className={`card table-wrap ${styles.tableCard}`}>
            <table className={`table ${styles.qTable}`}>
              <thead>
                <tr>
                  <th>Mã</th>
                  <th>Nội dung</th>
                  <th>Loại · mức</th>
                  <th>Nguồn</th>
                  <th className={styles.num}>Phiên bản</th>
                  <th className={styles.num}>Đã dùng</th>
                  <th className={styles.num}>Bật</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((item) => (
                  // key theo HỌ câu: lưu phiên bản mới (id đổi) vẫn giữ dòng đang mở
                  <QuestionRow key={item.family_id} item={item} skills={skills} onChanged={handleChanged} />
                ))}
              </tbody>
            </table>
          </div>
          {pages > 1 && (
            <nav className={styles.pager} aria-label="Phân trang">
              <button type="button" className="btn btn-soft btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                ‹ Trước
              </button>
              <span className="small muted">
                Trang {page}/{pages}
              </span>
              <button
                type="button"
                className="btn btn-soft btn-sm"
                disabled={page >= pages}
                onClick={() => setPage(page + 1)}
              >
                Sau ›
              </button>
            </nav>
          )}
        </>
      )}
    </div>
  );
}
