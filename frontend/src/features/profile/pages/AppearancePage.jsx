// Trang "Giao diện" trong Cài đặt tài khoản (module 01 · Tuấn · 11/11/2026) — theo thiết kế Tuấn gửi.
//   - Chế độ màu: Tối / Sáng / Theo hệ thống (theo Windows / điện thoại, tự đổi khi hệ thống đổi).
//   - Cỡ chữ: Nhỏ / Vừa / Lớn — chỉ áp cho NỘI DUNG bài học và câu hỏi ôn tập (biến CSS --reading-scale).
//   - Giảm chuyển động: tắt hiệu ứng (đồ thị, đèn, chuyển trang…) — styles/reduced-motion.css.
// Lưu trên TRÌNH DUYỆT (localStorage, utils/theme.js) — không gửi lên máy chủ; đổi máy thì chọn lại.
import { useState } from 'react';

import { PrefRow, Segmented, Switch } from '../components/PrefControls.jsx';
import SettingsLayout from '../components/SettingsLayout.jsx';
import {
  getFontSize,
  getMotionChoice,
  setFontSize,
  setMotion,
  setTheme,
  useThemeChoice,
} from '../../../utils/theme.js';
import styles from '../styles/Preferences.module.css';

const THEMES = [
  { value: 'dark', text: 'Tối' },
  { value: 'light', text: 'Sáng' },
  { value: 'system', text: 'Theo hệ thống' },
];
const FONTS = [
  { value: 'sm', text: 'Nhỏ' },
  { value: 'md', text: 'Vừa' },
  { value: 'lg', text: 'Lớn' },
];

export default function AppearancePage() {
  const theme = useThemeChoice();
  const [font, setFont] = useState(getFontSize);
  const [reduce, setReduce] = useState(getMotionChoice);

  return (
    <SettingsLayout>
      <div className={styles.head}>
        <h2>Giao diện</h2>
        <span className={styles.badge}>Lưu trên trình duyệt</span>
      </div>

      <PrefRow title="Chế độ màu" desc="Theo hệ thống sẽ đổi theo cài đặt Windows / điện thoại.">
        <Segmented
          label="Chế độ màu"
          value={theme}
          options={THEMES}
          onChange={(value, event) => setTheme(value, { x: event.clientX, y: event.clientY })}
        />
      </PrefRow>

      <PrefRow title="Cỡ chữ" desc="Áp dụng cho nội dung bài học và câu hỏi ôn tập.">
        <Segmented
          label="Cỡ chữ"
          value={font}
          options={FONTS}
          onChange={(value) => {
            setFontSize(value);
            setFont(value);
          }}
        />
      </PrefRow>

      <PrefRow title="Giảm chuyển động" desc="Tắt hiệu ứng về đồ thị, đèn và chuyển trang.">
        <Switch
          label="Giảm chuyển động"
          checked={reduce}
          onChange={(on) => {
            setMotion(on ? 'reduce' : null); // tắt → quay về theo cài đặt hệ điều hành
            setReduce(on);
          }}
        />
      </PrefRow>
    </SettingsLayout>
  );
}
