// "Mật khẩu phải đáp ứng:" — mỗi quy tắc tích xanh NGAY KHI GÕ đạt (FĐ4, màn demo ResetPassword).
// Dùng ở Đặt lại mật khẩu và Đổi mật khẩu (FĐ5). Cùng quy tắc với backend (utils/validators.js).
import { CheckCircleIcon, EmptyCircleIcon } from './icons.jsx';
import styles from './PasswordRules.module.css';

export default function PasswordRules({ password, confirm }) {
  const rules = [
    { text: 'Tối thiểu 8 ký tự', ok: password.length >= 8 },
    {
      text: 'Có chữ hoa, chữ thường và chữ số',
      ok: /[A-Z]/.test(password) && /[a-z]/.test(password) && /[0-9]/.test(password),
    },
    { text: 'Có ký tự đặc biệt', ok: /[^A-Za-z0-9]/.test(password) },
    { text: 'Hai mật khẩu trùng khớp', ok: password.length > 0 && password === confirm },
  ];

  return (
    <div className={styles.box}>
      <span>Mật khẩu phải đáp ứng:</span>
      <ul>
        {rules.map((rule) => (
          <li key={rule.text} className={rule.ok ? styles.ok : ''}>
            <span className={styles.mark}>
              {rule.ok ? <CheckCircleIcon size={16} /> : <EmptyCircleIcon />}
            </span>
            {rule.text}
          </li>
        ))}
      </ul>
    </div>
  );
}
