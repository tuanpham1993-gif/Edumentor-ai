// Ô nhập có nhãn, icon và dòng báo lỗi (FĐ3). Dùng class chung trong index.css:
// .field (nhãn + ô), .input (khung ô), .input.invalid (viền đỏ), .field-error (chữ lỗi).
//   <TextField id="email" label="Email" icon={<MailIcon />} error={errors.email} value=... onChange=... />
// Các prop còn lại (type, placeholder, autoComplete…) truyền thẳng vào <input>.
export default function TextField({ id, label, icon, error, trailing, ...inputProps }) {
  const errorId = error ? `${id}-error` : undefined;
  return (
    <div className="stack" style={{ gap: 6 }}>
      <label className="field" htmlFor={id}>
        {label}
        <span className={`input ${error ? 'invalid' : ''}`}>
          {icon}
          <input id={id} aria-invalid={Boolean(error)} aria-describedby={errorId} {...inputProps} />
          {trailing}
        </span>
      </label>
      {error && (
        <span id={errorId} className="field-error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
