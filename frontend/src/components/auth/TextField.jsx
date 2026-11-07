// Ô nhập có nhãn, icon và thông báo dưới ô (FĐ3; bổ sung trạng thái 07/11).
// Dùng class chung index.css: .field, .input, .input.invalid (viền đỏ), .field-error.
//   error   : chuỗi lỗi → viền đỏ + dòng ✗ đỏ dưới ô
//   invalid : true → chỉ viền đỏ, không có dòng chữ (vd ô Email khi đăng nhập sai)
//   valid   : true → viền xanh
//   below   : nội dung tùy ý dưới ô (danh sách quy tắc mật khẩu, cảnh báo Caps Lock…)
//   inputRef: ref tới thẻ <input> (để đặt con trỏ vào ô)
// Các prop còn lại (type, placeholder, autoComplete…) truyền thẳng vào <input>.
import StatusIcon from './StatusIcon.jsx';
import styles from './TextField.module.css';

export default function TextField({
  id,
  label,
  icon,
  error,
  invalid = false,
  valid = false,
  trailing,
  below,
  inputRef,
  ...inputProps
}) {
  const errorId = error ? `${id}-error` : undefined;
  const isInvalid = Boolean(error) || invalid;
  const boxClass = ['input', isInvalid && 'invalid', !isInvalid && valid && styles.valid]
    .filter(Boolean)
    .join(' ');

  return (
    <div className="stack" style={{ gap: 6 }}>
      <label className="field" htmlFor={id}>
        {label}
        <span className={boxClass}>
          {icon}
          <input
            id={id}
            ref={inputRef}
            aria-invalid={isInvalid}
            aria-describedby={errorId}
            {...inputProps}
          />
          {trailing}
        </span>
      </label>
      {error && (
        <span id={errorId} className={`${styles.status} ${styles.statusError}`} role="alert">
          <StatusIcon state="error" size={14} />
          {error}
        </span>
      )}
      {below}
    </div>
  );
}

/** Một dòng trạng thái có icon dưới ô: tone 'ok' | 'error' | 'warn'. */
export function FieldStatus({ tone, children }) {
  const toneClass = { ok: styles.statusOk, error: styles.statusError, warn: styles.statusWarn }[tone];
  return (
    <span className={`${styles.status} ${toneClass}`} role={tone === 'error' ? 'alert' : 'status'}>
      {tone === 'warn' ? <span aria-hidden="true">⇪</span> : <StatusIcon state={tone} size={14} />}
      {children}
    </span>
  );
}
