// Mentor ôn tập — /admin/review-mentors (module 09 · Tuấn · G3f, 25/11/2026 — D22).
// Admin gán vai trò mentor cho tài khoản CÓ SẴN (theo email) / thu hồi về học viên. Không đổi được tài khoản admin.
// Mentor duyệt câu AI soạn ở /mentor/review (Đạt / Phản ánh lỗi) và vẫn học như học viên.
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import * as reviewAdminApi from '../../../api/reviewAdmin.api.js';
import { parseApiError } from '../../../utils/errors.js';
import styles from '../styles/AdminReviewFlags.module.css';

export default function AdminReviewMentorsPage() {
  const [mentors, setMentors] = useState(null);
  const [email, setEmail] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const load = useCallback(async () => {
    try {
      setMentors(await reviewAdminApi.listMentors());
    } catch (err) {
      setError(parseApiError(err).message);
      setMentors([]);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function run(fn, message) {
    setBusy(true);
    setError('');
    setNotice('');
    try {
      await fn();
      setNotice(message);
      await load();
      return true;
    } catch (err) {
      setError(parseApiError(err).message);
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function add(event) {
    event.preventDefault();
    const value = email.trim();
    if (await run(() => reviewAdminApi.addMentor(value), `Đã gán mentor cho ${value}.`)) setEmail('');
  }

  function remove(m) {
    if (!window.confirm(`Thu hồi vai trò mentor của ${m.full_name}? Tài khoản trở về học viên.`)) return;
    run(() => reviewAdminApi.removeMentor(m.user_id), `Đã thu hồi mentor ${m.full_name}.`);
  }

  return (
    <div className={styles.page}>
      <header className={styles.head}>
        <div>
          <h1 className={styles.title}>Mentor ôn tập</h1>
          <p className="muted small" style={{ margin: 0 }}>
            Mentor duyệt câu hỏi AI soạn (Đạt / Phản ánh lỗi). Câu bị phản ánh tắt ngay và chờ bạn xử lý ở{' '}
            <Link to="/admin/review-reports">Câu bị phản ánh</Link>.
          </p>
        </div>
        <Link to="/mentor/review" className="btn btn-sm">
          Xem trang mentor →
        </Link>
      </header>

      <form className={`card ${styles.filters}`} onSubmit={add}>
        <input className="input" type="email" required placeholder="Email tài khoản đã đăng ký" value={email}
               onChange={(e) => setEmail(e.target.value)} aria-label="Email" style={{ flex: 1, minWidth: 220 }} />
        <button type="submit" className="btn btn-sm btn-primary" disabled={busy || !email.trim()}>
          Gán mentor
        </button>
      </form>

      {notice && <div className="alert alert-ok">{notice}</div>}
      {error && <div className="alert">{error}</div>}

      {mentors === null ? (
        <p className="muted">Đang tải…</p>
      ) : mentors.length === 0 ? (
        <div className={`card ${styles.empty}`}>Chưa có mentor nào.</div>
      ) : (
        <div className={`card ${styles.tableWrap}`}>
          <table className="table">
            <thead>
              <tr>
                <th>Họ tên</th>
                <th>Email</th>
                <th style={{ textAlign: 'right' }}>Đã Đạt</th>
                <th style={{ textAlign: 'right' }}>Đã phản ánh</th>
                <th aria-label="Thao tác" />
              </tr>
            </thead>
            <tbody>
              {mentors.map((m) => (
                <tr key={m.user_id}>
                  <td>
                    {m.full_name} {!m.is_active && <span className="chip">Đã khóa</span>}
                  </td>
                  <td className="small">{m.email}</td>
                  <td style={{ textAlign: 'right' }}>{m.passed}</td>
                  <td style={{ textAlign: 'right' }}>{m.reported}</td>
                  <td style={{ textAlign: 'right' }}>
                    <button type="button" className="btn btn-sm" disabled={busy} onClick={() => remove(m)}>
                      Thu hồi
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
