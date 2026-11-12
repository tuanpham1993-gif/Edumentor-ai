// Trang đăng nhập (module 01 · Tuấn · FĐ3, 07/11/2026) — theo màn demo Main / Main-LampOff.
//   - Mở trang đèn tắt; kéo dây để hiện form (AuthLayout).
//   - Sai (401) → DƯỚI Ô MẬT KHẨU: "Email hoặc mật khẩu không đúng. Vui lòng nhập lại."
//       · Câu CHUNG cho mọi lý do (bảo mật): không để lộ email nào đã có tài khoản.
//       · Viền đỏ 2 ô, xóa trắng ô mật khẩu + đặt sẵn con trỏ để gõ lại, rung form.
//       · Sai từ 2 lần → tô sáng "Quên mật khẩu?".
//   - Cảnh báo "Caps Lock đang bật" khi gõ mật khẩu.
//   - Đúng → quay lại trang định vào (hoặc /me). Bỏ dòng "Tài khoản demo" của bản demo.
import { useRef, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import AuthLayout from '../components/AuthLayout.jsx';
import { ArrowIcon, MailIcon } from '../../common/components/icons.jsx';
import PasswordField from '../../common/components/PasswordField.jsx';
import TextField from '../../common/components/TextField.jsx';
import { useAuth } from '../../../hooks/useAuth.js';
import { parseApiError } from '../../../utils/errors.js';
import { validateEmail } from '../../../utils/validators.js';

const WRONG_CREDENTIALS = 'Email hoặc mật khẩu không đúng. Vui lòng nhập lại.';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state ?? {};
  const passwordRef = useRef(null);

  const [email, setEmail] = useState(state.email ?? ''); // đăng ký xong → điền sẵn email
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({}); // lỗi từng ô (kiểm tra trên trình duyệt)
  const [wrongCredentials, setWrongCredentials] = useState(false); // vừa sai email / mật khẩu (401)
  const [failCount, setFailCount] = useState(0);
  const [formError, setFormError] = useState(''); // lỗi khác (mất mạng, máy chủ…)
  const [submitting, setSubmitting] = useState(false);
  const [shake, setShake] = useState(false);

  // Thông báo khi được chuyển tới đây
  let notice = null;
  if (state.registered) {
    // 12/11: backend gửi email chào mừng tới địa chỉ vừa đăng ký
    notice = {
      ok: true,
      text: `Đăng ký thành công! Chúng tôi đã gửi email chào mừng tới ${state.email ?? 'email của bạn'}. Đăng nhập để bắt đầu.`,
    };
  }
  else if (state.passwordChanged) notice = { ok: true, text: state.message };
  else if (state.expired) {
    notice = { ok: false, text: 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.' };
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setFormError('');
    setWrongCredentials(false);

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
      const { status, message } = parseApiError(err);
      if (status === 401) {
        setWrongCredentials(true);
        setFailCount((count) => count + 1);
        setPassword(''); // xóa trắng để gõ lại
        setTimeout(() => passwordRef.current?.focus(), 0); // đặt con trỏ vào ô mật khẩu
      } else {
        setFormError(message); // vd "Không kết nối được máy chủ…"
      }
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

      {notice && !formError && !wrongCredentials && (
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
          onChange={(event) => {
            setEmail(event.target.value);
            setWrongCredentials(false);
          }}
          error={errors.email}
          invalid={wrongCredentials}
        />
        <PasswordField
          id="password"
          label="Mật khẩu"
          placeholder="Nhập mật khẩu"
          autoComplete="current-password"
          inputRef={passwordRef}
          value={password}
          onChange={(event) => {
            setPassword(event.target.value);
            if (errors.password) setErrors((prev) => ({ ...prev, password: undefined }));
          }}
          error={errors.password || (wrongCredentials ? WRONG_CREDENTIALS : undefined)}
          capsLockHint
        />

        <div style={{ display: 'flex', justifyContent: 'flex-end', fontSize: 13, marginTop: -8 }}>
          <Link
            to="/forgot-password"
            style={failCount >= 2 ? { fontWeight: 700, color: 'var(--accent)' } : undefined}
          >
            {failCount >= 2 ? 'Quên mật khẩu? Đặt lại tại đây →' : 'Quên mật khẩu?'}
          </Link>
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
