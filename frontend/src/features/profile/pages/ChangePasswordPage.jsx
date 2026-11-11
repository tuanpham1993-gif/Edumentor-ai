// Đổi mật khẩu (module 01 · Tuấn · FĐ5, 07/11/2026) — theo màn demo ChangePassword.
//   - 3 ô: Mật khẩu hiện tại, Mật khẩu mới, Xác nhận. Bên phải: quy tắc 3 trạng thái
//     + "Khác mật khẩu hiện tại" + "Hai mật khẩu trùng khớp".
//   - 400 (mật khẩu hiện tại sai) → báo dưới ô "Mật khẩu hiện tại", xóa ô đó, đặt con trỏ.
//   - Thành công → backend thu hồi MỌI phiên (Q10) → đăng xuất máy này → /login kèm thông báo.
//   - Mật khẩu mới trùng mật khẩu cũ: trình duyệt chặn trước; backend cũng chặn (400
//     "Mật khẩu này đã được sử dụng.", 08/11) → hiện dưới ô "Mật khẩu mới".
import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import * as meApi from '../../../api/me.api.js';
import PasswordField from '../../common/components/PasswordField.jsx';
import PasswordRules from '../../common/components/PasswordRules.jsx';
import SettingsLayout from '../components/SettingsLayout.jsx';
import { useAuth } from '../../../hooks/useAuth.js';
import { parseApiError } from '../../../utils/errors.js';
import { passwordExtraError, validatePassword } from '../../../utils/validators.js';
import styles from '../styles/Settings.module.css';

const EMPTY = { current: '', password: '', confirm: '' };
const SAME_PASSWORD = 'Mật khẩu này đã được sử dụng.'; // khớp detail 400 của backend

export default function ChangePasswordPage() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const currentRef = useRef(null);

  const [values, setValues] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [submitted, setSubmitted] = useState(false); // bấm Lưu → quy tắc trống chuyển đỏ
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { current, password, confirm } = values;

  function handleChange(event) {
    const { name, value } = event.target;
    setValues((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: undefined }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitted(true);
    setFormError('');

    const nextErrors = {};
    if (!current) nextErrors.current = 'Vui lòng nhập mật khẩu hiện tại.';
    const extra = passwordExtraError(password); // > 72 byte: không nằm trong danh sách quy tắc
    if (extra) nextErrors.password = extra;
    setErrors(nextErrors);

    const rulesOk =
      validatePassword(password) === null && password !== current && confirm === password;
    if (Object.keys(nextErrors).length > 0 || !rulesOk) return;

    setSubmitting(true);
    try {
      await meApi.changePassword({
        currentPassword: current,
        newPassword: password,
        confirmNewPassword: confirm,
      });
      await logout(); // phiên trên máy này cũng đã bị thu hồi
      navigate('/login', {
        replace: true,
        state: {
          passwordChanged: true,
          message: 'Đổi mật khẩu thành công. Đăng nhập lại bằng mật khẩu mới.',
        },
      });
    } catch (err) {
      const { status, message, fieldErrors } = parseApiError(err);
      const detail = err?.response?.data?.detail;
      if (status === 400 && detail === SAME_PASSWORD) {
        // Phòng hờ: thường trình duyệt đã chặn trước (quy tắc "Khác mật khẩu hiện tại")
        setErrors({ password: SAME_PASSWORD });
      } else if (status === 400) {
        setErrors({ current: 'Mật khẩu hiện tại không đúng.' });
        setValues((prev) => ({ ...prev, current: '' }));
        setTimeout(() => currentRef.current?.focus(), 0);
      } else if (status === 422) {
        setErrors({
          current: fieldErrors.current_password,
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
    <SettingsLayout>
      <h2>Đổi mật khẩu</h2>
      <p>Nhập mật khẩu hiện tại và mật khẩu mới.</p>

      {formError && (
        <p className="alert" role="alert">
          {formError}
        </p>
      )}

      <div className={styles.pwGrid}>
        <form
          id="change-pw-form"
          className="stack"
          style={{ gap: 16 }}
          noValidate
          onSubmit={handleSubmit}
        >
          <PasswordField
            id="current-pw"
            name="current"
            label="Mật khẩu hiện tại"
            placeholder="Nhập mật khẩu hiện tại"
            autoComplete="current-password"
            inputRef={currentRef}
            value={current}
            onChange={handleChange}
            error={errors.current}
            capsLockHint
          />
          <PasswordField
            id="new-pw"
            name="password"
            label="Mật khẩu mới"
            placeholder="Nhập mật khẩu mới"
            autoComplete="new-password"
            value={password}
            onChange={handleChange}
            error={errors.password}
          />
          <PasswordField
            id="new-pw2"
            name="confirm"
            label="Xác nhận mật khẩu mới"
            placeholder="Nhập lại mật khẩu mới"
            autoComplete="new-password"
            value={confirm}
            onChange={handleChange}
            error={errors.confirm}
          />
        </form>

        <div className={`card ${styles.rules}`}>
          <PasswordRules
            password={password}
            confirm={confirm}
            notSameAs={current}
            showErrors={submitted}
          />
        </div>
      </div>

      <div className={`${styles.buttons} ${styles.pwButtons}`}>
        <button
          type="button"
          className="btn"
          onClick={() => navigate('/me')}
          disabled={submitting}
        >
          Hủy
        </button>
        <button
          type="submit"
          form="change-pw-form"
          className={`btn btn-primary ${submitting ? 'loading' : ''}`}
          disabled={submitting}
        >
          Lưu thay đổi
          <span className="spinner" aria-hidden="true" />
        </button>
      </div>
    </SettingsLayout>
  );
}
