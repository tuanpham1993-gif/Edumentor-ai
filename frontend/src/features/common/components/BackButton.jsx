// Nút quay lại dạng icon (FĐ6, 08/11/2026 — Tuấn: thay chữ "← Hồ sơ" bằng icon Back).
//   <BackButton to="/me" label="Hồ sơ" />
// Chỉ hiện mũi tên; rê chuột / bàn phím hiện chữ "Quay lại Hồ sơ" (title + aria-label cho trình đọc màn hình).
// Dùng <Link> tới trang cha (không phải history.back) → luôn về đúng chỗ, kể cả khi mở thẳng bằng URL.
import { Link } from 'react-router-dom';

import styles from '../styles/BackButton.module.css';
import { BackArrowIcon } from './icons.jsx';

export default function BackButton({ to, label }) {
  const text = `Quay lại ${label}`;
  return (
    <Link to={to} className={styles.back} aria-label={text} title={text}>
      <BackArrowIcon />
      <span className={styles.tip} aria-hidden="true">
        {label}
      </span>
    </Link>
  );
}
