// Trang đăng nhập — BẢN TẠM (FĐ2) để kiểm tra luồng đăng nhập / route bảo vệ.
// FĐ3 sẽ làm lại giống màn demo Main: dây kéo đèn, hiện/ẩn mật khẩu, rung form khi sai.
import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import BackendStatus from '../../components/common/BackendStatus.jsx';
import { useAuth } from '../../hooks/useAuth.js';
import { parseApiError } from '../../utils/errors.js';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const expired = location.state?.expired; // client.js báo hết phiên
  const from = location.state?.from || '/me'; // trang định vào trước khi bị chuyển tới đây

  async function handleSubmit(event) {
    event.preventDefault(); // chặn trình duyệt tải lại trang khi submit form
    setError('');
    setSubmitting(true);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(parseApiError(err).message); // vd "Lỗi 401: Email hoặc mật khẩu không đúng."
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="container page-in" style={{ maxWidth: 440 }}>
      <form className="card stack" style={{ padding: 28, gap: 18 }} onSubmit={handleSubmit}>
        <h1 style={{ margin: 0 }}>Đăng nhập</h1>

        {expired && !error && (
          <p className="alert">Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.</p>
        )}
        {error && <p className="alert">{error}</p>}

        <label className="field">
          Email
          <span className="input">
            <input
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </span>
        </label>

        <label className="field">
          Mật khẩu
          <span className="input">
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </span>
        </label>

        <button type="submit" className="btn btn-primary btn-lg btn-block" disabled={submitting}>
          {submitting ? 'Đang đăng nhập…' : 'Đăng nhập'}
        </button>

        <p className="muted small" style={{ margin: 0 }}>
          Chưa có tài khoản? <Link to="/register">Đăng ký ngay</Link>
        </p>
      </form>
      <BackendStatus />
    </main>
  );
}
