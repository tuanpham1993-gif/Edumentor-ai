// Trang "Thông báo qua email" trong Cài đặt tài khoản (module 01 · Tuấn · 11/11/2026) — theo thiết kế Tuấn gửi.
//   3 công tắc, bấm là LƯU NGAY lên máy chủ (GET/PATCH /api/me/email-preferences); lỗi → trả công tắc về như cũ.
//   Email bảo mật (quên mật khẩu, mật khẩu vừa đổi) và email kết quả ôn tập luôn gửi — không có công tắc.
// ⚠️ Mới là TÙY CHỌN: 3 loại email này CHƯA được gửi (chờ: nhắc ôn tập đến hạn — module 09 bước 5.6;
//    khóa gợi ý — Khôi/Hòa; phản hồi góp ý — module góp ý). Nơi gửi phải hỏi email_preference_service.wants_email().
import { useEffect, useState } from 'react';

import * as meApi from '../../../api/me.api.js';
import { PrefRow, Switch } from '../components/PrefControls.jsx';
import SettingsLayout from '../components/SettingsLayout.jsx';
import styles from '../styles/Preferences.module.css';

const ITEMS = [
  { key: 'review_reminder', title: 'Nhắc ôn tập đến hạn', desc: 'Gửi tối đa 1 email mỗi tuần, gom mọi kỹ năng đến hạn.' },
  { key: 'course_suggestions', title: 'Khóa học gợi ý mới cho lộ trình', desc: 'Khi có khóa mới khớp kỹ năng bạn đang học.' },
  { key: 'feedback_replies', title: 'Phản hồi góp ý', desc: 'Khi quản trị viên trả lời góp ý bạn đã gửi.' },
];

export default function EmailNotificationsPage() {
  const [prefs, setPrefs] = useState(null); // null = đang tải
  const [saving, setSaving] = useState(null); // khóa đang lưu
  const [status, setStatus] = useState('');
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    meApi
      .getEmailPreferences()
      .then((data) => !cancelled && setPrefs(data))
      .catch(() => !cancelled && setLoadError(true));
    return () => {
      cancelled = true;
    };
  }, []);

  async function toggle(key, value) {
    const before = prefs;
    setPrefs({ ...prefs, [key]: value }); // đổi ngay trên màn hình
    setSaving(key);
    setStatus('');
    try {
      setPrefs(await meApi.updateEmailPreferences({ [key]: value }));
      setStatus('Đã lưu.');
    } catch {
      setPrefs(before); // lưu lỗi → trả về như cũ
      setStatus('Không lưu được, vui lòng thử lại.');
    } finally {
      setSaving(null);
    }
  }

  return (
    <SettingsLayout>
      <div className={styles.head}>
        <h2>Thông báo qua email</h2>
        <span className={styles.status} role="status">
          {status || 'Lưu vào tài khoản'}
        </span>
      </div>

      {loadError && <p className="alert" role="alert">Không tải được cài đặt email.</p>}
      {!loadError && prefs === null && <div className="skeleton" style={{ height: 180 }} aria-hidden="true" />}

      {prefs &&
        ITEMS.map((item) => (
          <PrefRow key={item.key} title={item.title} desc={item.desc}>
            <Switch
              label={item.title}
              checked={prefs[item.key]}
              disabled={saving === item.key}
              onChange={(value) => toggle(item.key, value)}
            />
          </PrefRow>
        ))}
    </SettingsLayout>
  );
}
