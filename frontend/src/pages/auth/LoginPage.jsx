// Trang đăng nhập (module 01 · Tuấn · FĐ3, 07/11/2026) — theo màn demo Main / Main-LampOff.
//   - Mở trang đèn tắt; kéo dây để hiện form (AuthLayout).
//   - Sai → "Lỗi 401: …" + rung form. Đúng → quay lại trang định vào (hoặc /me).
//   - Bỏ dòng "Tài khoản demo" của bản demo (chỉ dành cho demo).
import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import AuthLayout from '../../components/auth/AuthLayout.jsx';
import { ArrowIcon, MailIcon } from '../../components/auth/icons.jsx';
import PasswordField from '../../components/auth/PasswordField.jsx';
import TextField from '../../components/auth/TextField.jsx';
import { useAuth } from '../../hooks/useAuth.js';
import { parseApiError } from '../../utils/errors.js';
import { validateEmail } from '../../utils/validators.js';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state ?? {};

  const [email, setEmail] = useState(state.email ?? ''); // đăng ký xong → điền sẵn email
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({}); // lỗi từng ô
  const [formError, setFormError] = useState(''); // lỗi chung (401, mất mạng…)
  const [submitting, setSubmitting] = useState(false);
  const [shake, setShake] = useState(false);

  // Thông báo khi được chuyển tới đây
  let notice = null;
  if (state.registered) notice = { ok: true, text: 'Đăng ký thành công. Đăng nhập để bắt đầu.' };
  else if (state.passwordChanged) notice = { ok: true, text: state.message };
  else if (state.expired) notice = { ok: false, text: 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.' };

  async function handleSubmit(event) {
    event.preventDefault();
    setFormError('');

    const nextErrors = {};
    const emailError = validateEmail(email);
    if (emailError) nextErrors.email = emailError;
    if (!password) nextErrors.password = 'Vui lòng nhập mật khẩu.';
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) {
      setShake(true);
      return;
    }

    setSubmitting(true);
    try {
      await login(email.trim(), password);
      navigate(state.from || '/me', { replace: true });
    } catch (err) {
      setFormError(parseApiError(err).message); // "Lỗi 401: Email hoặc mật khẩu không đúng."
      setShake(true);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthLayout cardClassName={shake ? 'shake' : ''} onCardAnimationEnd={() => setShake(false)}>
      <div>
        <h1>Đăng nhập</h1>
        <p className="sub">Chào mừng trở lại! Đăng nhập để tiếp tục hành trình học tập của bạn.</p>
      </div>

      {notice && !formError && (
        <p className={`alert ${notice.ok ? 'alert-ok' : ''}`} role="status">
          {notice.text}
        </p>
      )}
      {formError && (
        <p className="alert" role="alert">
          {formError}
        </p>
      )}

      <form className="stack" style={{ gap: 18 }} noValidate onSubmit={handleSubmit}>
        <TextField
          id="email"
          label="Email"
          icon={<MailIcon />}
          type="email"
          placeholder="Nhập email của bạn"
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          error={errors.email}
        />
        <PasswordField
          id="password"
          label="Mật khẩu"
          placeholder="Nhập mật khẩu"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          error={errors.password}
        />

        <div style={{ display: 'flex', justifyContent: 'flex-end', fontSize: 13, marginTop: -8 }}>
          <Link to="/forgot-password">Quên mật khẩu?</Link>
        </div>

        <button
          type="submit"
          className={`btn btn-primary btn-lg btn-block ${submitting ? 'loading' : ''}`}
          disabled={submitting}
        >
          Đăng nhập <ArrowIcon />
          <span className="spinner" aria-hidden="true" />
        </button>
      </form>

      <div style={{ height: 1, background: 'var(--card-border)' }} />
      <p style={{ margin: 0, textAlign: 'center', fontSize: 13, color: 'var(--text-muted)' }}>
        Chưa có tài khoản?{' '}
        <Link to="/register" style={{ fontWeight: 600 }}>
          Đăng ký ngay
        </Link>
      </p>
    </AuthLayout>
  );
}
