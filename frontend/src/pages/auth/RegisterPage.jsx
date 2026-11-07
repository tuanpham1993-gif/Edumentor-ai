// Trang đăng ký (module 01 · Tuấn · FĐ3, 07/11/2026) — theo màn demo Register.
//   - 4 ô: Họ và tên, Email, Mật khẩu, Xác nhận mật khẩu (Q3).
//   - Kiểm tra ngay trên trình duyệt theo CÙNG quy tắc với backend; lỗi hiện dưới từng ô.
//   - Lỗi từ server: 409 (email đã có) → ô Email; 422 → đúng ô theo fieldErrors.
//   - Thành công → /login, điền sẵn email + thông báo "Đăng ký thành công".
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import * as authApi from '../../api/auth.api.js';
import AuthLayout from '../../components/auth/AuthLayout.jsx';
import { ArrowIcon, MailIcon, UserIcon } from '../../components/auth/icons.jsx';
import PasswordField from '../../components/auth/PasswordField.jsx';
import TextField from '../../components/auth/TextField.jsx';
import { parseApiError } from '../../utils/errors.js';
import { validateEmail, validateFullName, validatePassword } from '../../utils/validators.js';

const EMPTY = { fullName: '', email: '', password: '', confirmPassword: '' };

function validate(values) {
  const errors = {};
  const fullName = validateFullName(values.fullName);
  if (fullName) errors.fullName = fullName;
  const email = validateEmail(values.email);
  if (email) errors.email = email;
  const password = validatePassword(values.password);
  if (password) errors.password = password;
  if (!values.confirmPassword) errors.confirmPassword = 'Vui lòng nhập lại mật khẩu.';
  else if (values.confirmPassword !== values.password) {
    errors.confirmPassword = 'Mật khẩu xác nhận không khớp.';
  }
  return errors;
}

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
  const [values, setValues] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [shake, setShake] = useState(false);

  // Một hàm onChange cho mọi ô: đọc tên ô từ thuộc tính name
  function handleChange(event) {
    const { name, value } = event.target;
    setValues((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: undefined })); // gõ lại → ẩn lỗi ô đó
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setFormError('');
    const nextErrors = validate(values);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) {
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
          value={values.password}
          onChange={handleChange}
          error={errors.password}
        />
        <PasswordField
          id="reg-confirm"
          name="confirmPassword"
          label="Xác nhận mật khẩu"
          placeholder="Nhập lại mật khẩu"
          autoComplete="new-password"
          value={values.confirmPassword}
          onChange={handleChange}
          error={errors.confirmPassword}
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
