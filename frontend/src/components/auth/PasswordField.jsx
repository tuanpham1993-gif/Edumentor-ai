// Ô mật khẩu có icon khóa + nút hiện / ẩn (FĐ3). Dùng lại ở Đăng ký, Đặt lại, Đổi mật khẩu.
import { useState } from 'react';

import { EyeClosedIcon, EyeOpenIcon, LockIcon } from './icons.jsx';
import styles from './PasswordField.module.css';
import TextField from './TextField.jsx';

export default function PasswordField(props) {
  const [visible, setVisible] = useState(false);

  const eyeButton = (
    <button
      type="button"
      className={styles.eye}
      aria-pressed={visible}
      aria-label={visible ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
      onClick={() => setVisible((v) => !v)}
    >
      <span className={styles.open}>
        <EyeOpenIcon />
      </span>
      <span className={styles.closed}>
        <EyeClosedIcon />
      </span>
    </button>
  );

  return (
    <TextField {...props} type={visible ? 'text' : 'password'} icon={<LockIcon />} trailing={eyeButton} />
  );
}
