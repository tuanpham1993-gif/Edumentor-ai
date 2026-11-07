// Sửa hồ sơ (module 01 · Tuấn · FĐ5, 07/11/2026) — theo màn demo EditProfile.
//   - Ảnh đại diện: bấm vào ảnh → chọn file → tải lên NGAY (POST /me/avatar).
//       Kiểm tra trước trên trình duyệt: PNG / JPEG, ≤ 5 MB (Q8). Server vẫn kiểm lại (413 / 415).
//   - Họ và tên: PATCH /me. Email, Vai trò, Ngày tham gia chỉ để xem.
//   - Lưu xong cập nhật user trong authStore → Header & trang Hồ sơ đổi theo ngay.
import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import * as meApi from '../../api/me.api.js';
import TextField from '../../components/auth/TextField.jsx';
import SettingsLayout from '../../components/profile/SettingsLayout.jsx';
import { useAuth } from '../../hooks/useAuth.js';
import { parseApiError } from '../../utils/errors.js';
import { formatDate, initials, roleLabel } from '../../utils/formatters.js';
import { validateFullName } from '../../utils/validators.js';
import styles from './Settings.module.css';

const AVATAR_TYPES = ['image/png', 'image/jpeg'];
const AVATAR_MAX_MB = 5; // khớp AVATAR_MAX_BYTES của backend

function CameraIcon() {
  return (
    <svg aria-hidden="true" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 8h3l2-3h6l2 3h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z" />
      <circle cx="12" cy="13" r="3.5" />
    </svg>
  );
}

export default function EditProfilePage() {
  const { user, setUser } = useAuth();
  const navigate = useNavigate();
  const fileRef = useRef(null);

  const [fullName, setFullName] = useState(user.full_name);
  const [nameError, setNameError] = useState('');
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [notice, setNotice] = useState(null); // { ok: bool, text }

  const changed = fullName.trim() !== user.full_name;

  async function handleAvatarChange(event) {
    const file = event.target.files?.[0];
    event.target.value = ''; // chọn lại đúng file cũ vẫn kích hoạt onChange
    if (!file) return;

    if (!AVATAR_TYPES.includes(file.type)) {
      setNotice({ ok: false, text: 'Chỉ chấp nhận ảnh PNG hoặc JPEG.' });
      return;
    }
    if (file.size > AVATAR_MAX_MB * 1024 * 1024) {
      setNotice({ ok: false, text: `Ảnh vượt quá ${AVATAR_MAX_MB} MB.` });
      return;
    }

    setNotice(null);
    setUploading(true);
    try {
      const updated = await meApi.uploadAvatar(file);
      setUser(updated);
      setNotice({ ok: true, text: 'Đã cập nhật ảnh đại diện.' });
    } catch (err) {
      const { status, message } = parseApiError(err);
      // 413 / 415: backend trả câu tiếng Việt sẵn → hiện nguyên văn (bỏ tiền tố "Lỗi N:")
      const detail = err?.response?.data?.detail;
      setNotice({
        ok: false,
        text: (status === 413 || status === 415) && typeof detail === 'string' ? detail : message,
      });
    } finally {
      setUploading(false);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setNotice(null);
    const error = validateFullName(fullName);
    setNameError(error ?? '');
    if (error || !changed) return;

    setSaving(true);
    try {
      const updated = await meApi.updateMe({ fullName: fullName.trim() });
      setUser(updated);
      setFullName(updated.full_name);
      setNotice({ ok: true, text: 'Đã lưu thay đổi.' });
    } catch (err) {
      const { status, message, fieldErrors } = parseApiError(err);
      if (status === 422 && fieldErrors.full_name) setNameError(fieldErrors.full_name);
      else setNotice({ ok: false, text: message });
    } finally {
      setSaving(false);
    }
  }

  return (
    <SettingsLayout>
      <h2>Thông tin cá nhân</h2>
      <p>Cập nhật tên hiển thị và ảnh đại diện.</p>

      {notice && (
        <p className={`alert ${notice.ok ? 'alert-ok' : ''}`} role={notice.ok ? 'status' : 'alert'}>
          {notice.text}
        </p>
      )}

      <div className={styles.avatarRow}>
        <input
          ref={fileRef}
          type="file"
          accept="image/png,image/jpeg"
          hidden
          onChange={handleAvatarChange}
        />
        <button
          type="button"
          className={`${styles.avatarBtn} ${uploading ? styles.busy : ''}`}
          aria-label="Đổi ảnh đại diện"
          disabled={uploading}
          onClick={() => fileRef.current?.click()}
        >
          {/* key đổi theo ảnh → chạy lại hiệu ứng "swap" khi có ảnh mới */}
          <span key={user.avatar_url ?? 'none'} className={styles.avatar}>
            {user.avatar_url ? <img src={user.avatar_url} alt="" /> : initials(user.full_name)}
          </span>
          <span className={styles.avatarHover} aria-hidden="true">
            {uploading ? 'Đang tải…' : 'Đổi ảnh'}
          </span>
          <span className={styles.cam} aria-hidden="true">
            {uploading ? <span className={styles.camSpin} /> : <CameraIcon />}
          </span>
        </button>
        <span className="small muted">
          Bấm vào ảnh để đổi. JPG/PNG, tối đa {AVATAR_MAX_MB} MB.
        </span>
      </div>

      <form className="stack" style={{ gap: 16 }} noValidate onSubmit={handleSubmit}>
        <div className={styles.two}>
          <TextField
            id="full_name"
            label="Họ và tên"
            maxLength={100}
            autoComplete="name"
            value={fullName}
            onChange={(event) => {
              setFullName(event.target.value);
              if (nameError) setNameError('');
            }}
            error={nameError}
          />
          <TextField
            id="email"
            label="Email"
            value={user.email}
            readOnly
            below={<span className="small muted">Email là tên đăng nhập, không thể thay đổi.</span>}
          />
          <TextField id="role" label="Vai trò" value={roleLabel(user.role)} readOnly />
          <TextField id="joined" label="Ngày tham gia" value={formatDate(user.created_at)} readOnly />
        </div>

        <div className={styles.buttons}>
          <button type="button" className="btn" onClick={() => navigate('/me')} disabled={saving}>
            Hủy
          </button>
          <button
            type="submit"
            className={`btn btn-primary ${saving ? 'loading' : ''}`}
            disabled={saving || !changed}
          >
            Lưu thay đổi
            <span className="spinner" aria-hidden="true" />
          </button>
        </div>
      </form>
    </SettingsLayout>
  );
}
