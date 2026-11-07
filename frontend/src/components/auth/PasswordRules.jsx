// Danh sách quy tắc mật khẩu, 3 trạng thái (FĐ4; nâng cấp 07/11):
//   ○ xám  — chưa gõ gì (không "mắng" người dùng khi vừa mở trang)
//   ✓ xanh — quy tắc đã đạt (nảy nhẹ khi vừa đạt)
//   ✗ đỏ   — đã gõ mà chưa đạt, hoặc đã bấm gửi (showErrors) khi còn trống
// Quy tắc lấy từ utils/validators.js → luôn khớp backend.
//
//   password   : mật khẩu đang gõ
//   confirm    : (tuỳ chọn) có truyền → thêm dòng "Hai mật khẩu trùng khớp"
//   showErrors : true sau khi bấm gửi → dòng đang xám chuyển đỏ
//   hint       : dòng gợi ý phía trên danh sách
import { PASSWORD_RULES } from '../../utils/validators.js';
import styles from './PasswordRules.module.css';
import StatusIcon from './StatusIcon.jsx';

const STATE_LABEL = { ok: 'đạt', error: 'chưa đạt', neutral: 'chưa kiểm tra' };

function ruleState(passed, touched, showErrors) {
  if (passed) return 'ok';
  if (touched || showErrors) return 'error';
  return 'neutral';
}

export default function PasswordRules({
  password,
  confirm,
  showErrors = false,
  hint = 'Mật khẩu gồm chữ hoa, chữ thường, số và ký tự đặc biệt.',
}) {
  const typed = password.length > 0;
  const rules = PASSWORD_RULES.map((rule) => ({
    text: rule.text,
    state: ruleState(rule.test(password), typed, showErrors),
  }));

  if (confirm !== undefined) {
    rules.push({
      text: 'Hai mật khẩu trùng khớp',
      state: ruleState(typed && password === confirm, confirm.length > 0, showErrors),
    });
  }

  return (
    <div className={styles.box}>
      <span className={styles.hint}>{hint}</span>
      <ul aria-live="polite">
        {rules.map((rule) => (
          <li key={rule.text} className={styles[rule.state] ?? ''}>
            <span className={styles.mark}>
              <StatusIcon state={rule.state} />
            </span>
            {rule.text}
            <span className="sr-only"> — {STATE_LABEL[rule.state]}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
