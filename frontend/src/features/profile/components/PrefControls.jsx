// Ô điều khiển dùng chung cho trang Giao diện / Thông báo qua email (module 01 · Tuấn · 11/11/2026).
//   <PrefRow title desc>{điều khiển}</PrefRow>        — một dòng: tên + mô tả bên trái, điều khiển bên phải
//   <Segmented label value options onChange />        — nhóm nút chọn một (vd Tối / Sáng / Theo hệ thống)
//   <Switch label checked onChange disabled />        — công tắc bật / tắt
import styles from '../styles/Preferences.module.css';

export function PrefRow({ title, desc, children }) {
  return (
    <div className={styles.row}>
      <div className={styles.rowText}>
        <strong>{title}</strong>
        {desc && <span>{desc}</span>}
      </div>
      <div className={styles.rowControl}>{children}</div>
    </div>
  );
}

export function Segmented({ label, value, options, onChange }) {
  return (
    <div className={styles.segmented} role="radiogroup" aria-label={label}>
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          role="radio"
          aria-checked={value === option.value}
          className={`${styles.segment} ${value === option.value ? styles.segmentOn : ''}`}
          onClick={(event) => onChange(option.value, event)}
        >
          {option.text}
        </button>
      ))}
    </div>
  );
}

export function Switch({ label, checked, onChange, disabled = false }) {
  return (
    <button
      type="button"
      role="switch"
      aria-label={label}
      aria-checked={checked}
      disabled={disabled}
      className={`${styles.switch} ${checked ? styles.switchOn : ''}`}
      onClick={() => onChange(!checked)}
    >
      <span className={styles.knob} aria-hidden="true" />
    </button>
  );
}
