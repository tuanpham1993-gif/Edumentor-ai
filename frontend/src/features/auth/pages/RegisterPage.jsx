// Trang đăng ký (module 01 · Tuấn · FĐ3, 07/11/2026) — theo màn demo Register.
//   - 4 ô: Họ và tên, Email, Mật khẩu, Xác nhận mật khẩu (Q3).
//   - Ô Mật khẩu: dòng gợi ý + 5 quy tắc 3 trạng thái (xám → xanh / đỏ) cập nhật khi gõ.
//   - Ô Xác nhận: "✓ Mật khẩu xác nhận khớp" (xanh) / "✗ … không khớp" (đỏ) khi gõ.
//   - Lỗi từ server: 409 (email đã có) → ô Email; 422 → đúng ô theo fieldErrors.
//   - Thành công → /login, điền sẵn email + thông báo "Đăng ký thành công".
//   - Đến từ trang chủ (state.fullName / state.email) → điền sẵn 2 ô đó.
import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import * as authApi from '../../../api/auth.api.js';
import AuthLayout from '../components/AuthLayout.jsx';
import { ArrowIcon, MailIcon, UserIcon } from '../../common/components/icons.jsx';
import PasswordField from '../../common/components/PasswordField.jsx';
import PasswordRules from '../../common/components/PasswordRules.jsx';
import TextField, { FieldStatus } from '../../common/components/TextField.jsx';
import { parseApiError } from '../../../utils/errors.js';
import {
  passwordExtraError,
  validateEmail,
  validateFullName,
  validatePassword,
} from '../../../utils/validators.js';

const EMPTY = { fullName: '', email: '', password: '', confirmPassword: '' };

// Tên trường backend → tên ô trên form
const SERVER_FIELD = {
  full_name: 'fullName',
  email: 'email',
  password: 'password',
  confirm_password: 'confirmPassword',
  _form: 'confirmPassword', // model_validator (xác nhận lệch) không gắn với ô nào
};

export default function RegisterPage() {
  const navigate = useNavigate();
  const location = useLocation();
  // Từ thẻ "bắt đầu nhanh" ở trang chủ → điền sẵn họ tên + email (08/11)
  const [values, setValues] = useState(() => ({
    ...EMPTY,
    fullName: location.state?.fullName ?? '',
    email: location.state?.email ?? '',
  }));
  const [errors, setErrors] = useState({}); // lỗi Họ tên / Email / lỗi từ server
  const [submitted, setSubmitted] = useState(false); // đã bấm Đăng ký → quy tắc trống chuyển đỏ
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [shake, setShake] = useState(false);

  const { password, confirmPassword } = values;
  const passwordOk = validatePassword(password) === null;
  const confirmMatches = confirmPassword.length > 0 && confirmPassword === password;

  // Một hàm onChange cho mọi ô: đọc tên ô từ thuộc tính name
  function handleChange(event) {
    const { name, value } = event.target;
    setValues((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: undefined })); // gõ lại → ẩn lỗi ô đó
  }

  // Dòng trạng thái dưới ô Xác nhận
  let confirmStatus = null;
  if (confirmPassword.length > 0) {
    confirmStatus = confirmMatches ? (
      <FieldStatus tone="ok">Mật khẩu xác nhận khớp</FieldStatus>
    ) : (
      <FieldStatus tone="error">Mật khẩu xác nhận không khớp</FieldStatus>
    );
  } else if (submitted) {
    confirmStatus = <FieldStatus tone="error">Vui lòng nhập lại mật khẩu.</FieldStatus>;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitted(true);
    setFormError('');

    const nextErrors = {};
    const fullNameError = validateFullName(values.fullName);
    if (fullNameError) nextErrors.fullName = fullNameError;
    const emailError = validateEmail(values.email);
    if (emailError) nextErrors.email = emailError;
    const extra = passwordExtraError(password); // > 72 byte: không có trong 5 quy tắc
    if (extra) nextErrors.password = extra;
    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0 || !passwordOk || !confirmMatches) {
      setShake(true);
      return;
    }

    setSubmitting(true);
    try {
      const user = await authApi.register({ ...values, email: values.email.trim() });
      navigate('/login', { replace: true, state: { registered: true, email: user.email } });
    } catch (err) {
      const { status, message, fieldErrors } = parseApiError(err);
      if (status === 409) {
        setErrors({ email: 'Email đã được sử dụng.' });
      } else if (status === 422) {
        const mapped = {};
        for (const [field, msg] of Object.entries(fieldErrors)) {
          mapped[SERVER_FIELD[field] ?? 'confirmPassword'] = msg;
        }
        setErrors(mapped);
      } else {
        setFormError(message);
      }
      setShake(true);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthLayout cardClassName={shake ? 'shake' : ''} onCardAnimationEnd={() => setShake(false)}>
      <div>
        <h1>Đăng ký tài khoản</h1>
        <p className="sub">Điền thông tin bên dưới để tạo tài khoản.</p>
      </div>

      {formError && (
        <p className="alert" role="alert">
          {formError}
        </p>
      )}

      <form className="stack" style={{ gap: 16 }} noValidate onSubmit={handleSubmit}>
        <TextField
          id="full_name"
          name="fullName"
          label="Họ và tên"
          icon={<UserIcon />}
          placeholder="Nhập họ và tên"
          autoComplete="name"
          maxLength={100}
          value={values.fullName}
          onChange={handleChange}
          error={errors.fullName}
        />
        <TextField
          id="reg-email"
          name="email"
          label="Email"
          icon={<MailIcon />}
          type="email"
          placeholder="Nhập email"
          autoComplete="email"
          value={values.email}
          onChange={handleChange}
          error={errors.email}
        />
        <PasswordField
          id="reg-password"
          name="password"
          label="Mật khẩu"
          placeholder="Nhập mật khẩu"
          autoComplete="new-password"
          value={password}
          onChange={handleChange}
          error={errors.password}
          invalid={submitted && !passwordOk}
          valid={passwordOk}
          below={<PasswordRules password={password} showErrors={submitted} />}
        />
        <PasswordField
          id="reg-confirm"
          name="confirmPassword"
          label="Xác nhận mật khẩu"
          placeholder="Nhập lại mật khẩu"
          autoComplete="new-password"
          value={confirmPassword}
          onChange={handleChange}
          error={errors.confirmPassword}
          invalid={(confirmPassword.length > 0 && !confirmMatches) || (submitted && !confirmMatches)}
          valid={confirmMatches}
          below={!errors.confirmPassword && confirmStatus}
        />

        <button
          type="submit"
          className={`btn btn-primary btn-lg btn-block ${submitting ? 'loading' : ''}`}
          disabled={submitting}
        >
          Đăng ký <ArrowIcon />
          <span className="spinner" aria-hidden="true" />
        </button>
      </form>

      <p style={{ margin: 0, textAlign: 'center', fontSize: 13, color: 'var(--text-muted)' }}>
        Đã có tài khoản?{' '}
        <Link to="/login" style={{ fontWeight: 600 }}>
          Đăng nhập
        </Link>
      </p>
    </AuthLayout>
  );
}
