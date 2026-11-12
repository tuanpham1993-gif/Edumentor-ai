// Đặt lại mật khẩu (module 01 · Tuấn · FĐ4, 07/11/2026) — theo màn demo ResetPassword.
// Mở từ link trong email: /reset-password?token=...  (khi dev, link in ở terminal backend)
//   - Không có token trong URL → trang "Liên kết không còn hiệu lực".
//   - Quy tắc mật khẩu 3 trạng thái (xám / xanh / đỏ) cập nhật khi gõ (PasswordRules).
//   - 400 (token sai / hết hạn / đã dùng) → trang "Liên kết không còn hiệu lực".
//   - Thành công → backend đã thu hồi mọi phiên (Q10) → xóa đăng nhập trên máy này → /login.
import { useState } from 'react';
import { Navigate, useNavigate, useSearchParams } from 'react-router-dom';

import * as authApi from '../../../api/auth.api.js';
import CenterLayout from '../components/CenterLayout.jsx';
import { ArrowIcon } from '../../common/components/icons.jsx';
import PasswordField from '../../common/components/PasswordField.jsx';
import PasswordRules from '../../common/components/PasswordRules.jsx';
import { useAuth } from '../../../hooks/useAuth.js';
import { parseApiError } from '../../../utils/errors.js';
import { passwordExtraError, validatePassword } from '../../../utils/validators.js';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();
  const { logout } = useAuth();

  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [errors, setErrors] = useState({});
  const [submitted, setSubmitted] = useState(false); // bấm gửi → quy tắc trống chuyển đỏ
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!token) return <Navigate to="/reset-expired" replace />;

  async function handleSubmit(event) {
    event.preventDefault();
    setFormError('');
    setSubmitted(true);
    // 5 quy tắc + "trùng khớp" đã hiện trong danh sách (PasswordRules) → chỉ báo riêng lỗi > 72 byte
    const extra = passwordExtraError(password);
    setErrors(extra ? { password: extra } : {});
    if (extra || validatePassword(password) !== null || !confirm || confirm !== password) return;

    setSubmitting(true);
    try {
      await authApi.resetPassword({ token, newPassword: password, confirmNewPassword: confirm });
      await logout(); // phiên cũ trên máy này (nếu có) đã bị backend thu hồi
      navigate('/login', {
        replace: true,
        state: {
          passwordChanged: true,
          message: 'Đặt lại mật khẩu thành công. Đăng nhập bằng mật khẩu mới.',
        },
      });
    } catch (err) {
      const { status, message, fieldErrors } = parseApiError(err);
      if (status === 400) {
        navigate('/reset-expired', { replace: true });
        return;
      }
      if (status === 422) {
        setErrors({
          password: fieldErrors.new_password,
          confirm: fieldErrors._form ?? fieldErrors.confirm_new_password,
        });
      } else {
        setFormError(message);
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <CenterLayout>
      <div>
        <h1>Đặt lại mật khẩu</h1>
        <p className="sub">Nhập mật khẩu mới cho tài khoản của bạn.</p>
      </div>

      {formError && (
        <p className="alert" role="alert">
          {formError}
        </p>
      )}

      <form className="stack" style={{ gap: 16 }} noValidate onSubmit={handleSubmit}>
        <PasswordField
          id="new-pw"
          label="Mật khẩu mới"
          placeholder="Nhập mật khẩu mới"
          autoComplete="new-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          error={errors.password}
        />
        <PasswordField
          id="new-pw2"
          label="Xác nhận mật khẩu mới"
          placeholder="Nhập lại mật khẩu mới"
          autoComplete="new-password"
          value={confirm}
          onChange={(event) => setConfirm(event.target.value)}
          error={errors.confirm}
        />

        <PasswordRules password={password} confirm={confirm} showErrors={submitted} />

        <button
          type="submit"
          className={`btn btn-primary btn-lg btn-block ${submitting ? 'loading' : ''}`}
          disabled={submitting}
        >
          Đặt lại mật khẩu <ArrowIcon />
          <span className="spinner" aria-hidden="true" />
        </button>
      </form>
    </CenterLayout>
  );
}
