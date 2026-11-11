// Quên mật khẩu (module 01 · Tuấn · FĐ4, 07/11/2026) — theo màn demo ForgotPassword.
// Gửi xong LUÔN sang "Đã gửi", dù email có tài khoản hay không — khớp backend (FR-47):
// không để lộ email nào đã đăng ký.
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import * as authApi from '../../../api/auth.api.js';
import CenterLayout, { BackToLogin, Orb, centerStyles } from '../components/CenterLayout.jsx';
import { ArrowIcon, MailIcon } from '../../common/components/icons.jsx';
import TextField from '../../common/components/TextField.jsx';
import { parseApiError } from '../../../utils/errors.js';
import { validateEmail } from '../../../utils/validators.js';

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setFormError('');
    const emailError = validateEmail(email);
    setError(emailError ?? '');
    if (emailError) return;

    setSubmitting(true);
    try {
      await authApi.forgotPassword(email.trim());
      navigate('/forgot-sent', { state: { email: email.trim() } });
    } catch (err) {
      const { status, message, fieldErrors } = parseApiError(err);
      if (status === 422) setError(fieldErrors.email ?? 'Nhập email hợp lệ.');
      else setFormError(message); // mất mạng / lỗi máy chủ
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <CenterLayout>
      <div>
        <h1>Quên mật khẩu</h1>
        <p className="sub">
          Nhập email đã đăng ký. Chúng tôi sẽ gửi liên kết đặt lại mật khẩu tới hộp thư của bạn.
        </p>
      </div>

      {formError && (
        <p className="alert" role="alert">
          {formError}
        </p>
      )}

      <form className="stack" style={{ gap: 16 }} noValidate onSubmit={handleSubmit}>
        <TextField
          id="fp-email"
          label="Email"
          icon={<MailIcon />}
          type="email"
          placeholder="Nhập email của bạn"
          autoComplete="email"
          value={email}
          onChange={(event) => {
            setEmail(event.target.value);
            if (error) setError('');
          }}
          error={error}
        />
        <button
          type="submit"
          className={`btn btn-primary btn-lg btn-block ${submitting ? 'loading' : ''}`}
          disabled={submitting}
        >
          Gửi yêu cầu <ArrowIcon />
          <span className="spinner" aria-hidden="true" />
        </button>
      </form>

      <BackToLogin />

      <div className={centerStyles.iconBlock}>
        <Orb>
          <MailIcon />
        </Orb>
        <span className="small muted">Liên kết chỉ dùng được một lần và có thời hạn ngắn.</span>
      </div>
    </CenterLayout>
  );
}
