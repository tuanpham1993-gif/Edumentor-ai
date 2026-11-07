// Ô mật khẩu có icon khóa + nút hiện / ẩn + cảnh báo Caps Lock (FĐ3; Caps Lock 07/11).
// Dùng lại ở Đăng nhập, Đăng ký, Đặt lại, Đổi mật khẩu.
//   capsLockHint: true → hiện "⇪ Caps Lock đang bật" khi người dùng gõ lúc bật Caps Lock
//                (nguyên nhân sai mật khẩu hay gặp nhất)
import { useState } from 'react';

import { EyeClosedIcon, EyeOpenIcon, LockIcon } from './icons.jsx';
import styles from './PasswordField.module.css';
import TextField, { FieldStatus } from './TextField.jsx';

export default function PasswordField({ capsLockHint = false, below, onKeyDown, onKeyUp, ...props }) {
  const [visible, setVisible] = useState(false);
  const [capsLock, setCapsLock] = useState(false);

  // Mỗi lần nhấn / nhả phím, hỏi trình duyệt Caps Lock có đang bật không
  function checkCapsLock(event) {
    if (event.getModifierState) setCapsLock(event.getModifierState('CapsLock'));
  }

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
    <TextField
      {...props}
      type={visible ? 'text' : 'password'}
      icon={<LockIcon />}
      trailing={eyeButton}
      onKeyDown={(event) => {
        checkCapsLock(event);
        onKeyDown?.(event);
      }}
      onKeyUp={(event) => {
        checkCapsLock(event);
        onKeyUp?.(event);
      }}
      below={
        <>
          {capsLockHint && capsLock && <FieldStatus tone="warn">Caps Lock đang bật</FieldStatus>}
          {below}
        </>
      }
    />
  );
}
