// Sửa hồ sơ (module 01 · Tuấn · FĐ5, 07/11/2026) — theo màn demo EditProfile.
//   - Ảnh đại diện: bấm vào ảnh → chọn file → tải lên NGAY (POST /me/avatar).
//       Kiểm tra trước trên trình duyệt: PNG / JPEG, ≤ 5 MB (Q8). Server vẫn kiểm lại (413 / 415).
//   - Họ và tên + thông tin cá nhân (12/11): ngày sinh, giới tính, quê quán, số điện thoại, CCCD → PATCH /me
//     (chỉ gửi trường đã đổi). Email, Vai trò, Ngày tham gia chỉ để xem.
//   - CCCD: chỉ hiện bản che (vd 345*********) — để trống = giữ số cũ; gõ 12 số mới = thay. Server mã hóa khi lưu.
//   - Lưu xong cập nhật user trong authStore → Header & trang Hồ sơ đổi theo ngay.
import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import * as meApi from '../../../api/me.api.js';
import { ArrowIcon } from '../../common/components/icons.jsx';
import { Segmented } from '../components/PrefControls.jsx';
import TextField from '../../common/components/TextField.jsx';
import SettingsLayout from '../components/SettingsLayout.jsx';
import { useAuth } from '../../../hooks/useAuth.js';
import { parseApiError } from '../../../utils/errors.js';
import { formatDate, initials, roleLabel } from '../../../utils/formatters.js';
import { validateFullName } from '../../../utils/validators.js';
import styles from '../styles/Settings.module.css';

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

  // Thông tin cá nhân (12/11). Giá trị '' = chưa nhập.
  const initial = {
    date_of_birth: user.date_of_birth ?? '',
    gender: user.gender ?? '',
    hometown: user.hometown ?? '',
    phone: user.phone ?? '',
  };
  const [details, setDetails] = useState(initial);
  const [citizenId, setCitizenId] = useState(''); // để trống = giữ số cũ
  const [fieldErrors, setFieldErrors] = useState({});
  const setDetail = (key, value) => {
    setDetails((d) => ({ ...d, [key]: value }));
    if (fieldErrors[key]) setFieldErrors((e) => ({ ...e, [key]: '' }));
  };
  // Chỉ gửi trường đã đổi; ô bị xóa trắng → null (xóa trên server)
  const changedDetails = Object.fromEntries(
    Object.keys(initial)
      .filter((key) => details[key].trim() !== initial[key])
      .map((key) => [key, details[key].trim() || null]),
  );
  if (citizenId.trim()) changedDetails.citizen_id = citizenId.replace(/\s/g, '');

  const changed = fullName.trim() !== user.full_name || Object.keys(changedDetails).length > 0;

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
    const errors = {};
    const phone = details.phone.replace(/[\s.\-()]/g, '').replace(/^\+84/, '0');
    if (phone && !/^0\d{9}$/.test(phone)) errors.phone = 'Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0.';
    if (citizenId && !/^\d{12}$/.test(citizenId)) errors.citizen_id = 'Số CCCD phải gồm đúng 12 chữ số.';
    setFieldErrors(errors);
    if (error || Object.keys(errors).length > 0 || !changed) return;

    setSaving(true);
    try {
      const updated = await meApi.updateMe({ fullName: fullName.trim(), details: changedDetails });
      setUser(updated);
      setFullName(updated.full_name);
      setDetails({
        date_of_birth: updated.date_of_birth ?? '',
        gender: updated.gender ?? '',
        hometown: updated.hometown ?? '',
        phone: updated.phone ?? '',
      });
      setCitizenId('');
      setNotice({ ok: true, text: 'Đã lưu thay đổi.' });
    } catch (err) {
      const { status, message, fieldErrors: apiErrors } = parseApiError(err);
      if (status === 422 && apiErrors.full_name) setNameError(apiErrors.full_name);
      else if (status === 422 && Object.keys(apiErrors).length > 0) setFieldErrors(apiErrors);
      else if (status === 409) setFieldErrors({ citizen_id: err?.response?.data?.detail ?? message });
      else setNotice({ ok: false, text: message });
    } finally {
      setSaving(false);
    }
  }

  return (
    <SettingsLayout>
      <h2>Thông tin cá nhân</h2>
      <p>Cập nhật ảnh đại diện và thông tin cá nhân của bạn.</p>

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
        <span className="stack" style={{ gap: 2 }}>
          <strong style={{ fontSize: 14 }}>Ảnh đại diện</strong>
          <span className="small muted">
            Bấm vào ảnh để đổi. JPG/PNG, tối đa {AVATAR_MAX_MB} MB.
          </span>
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
            id="date_of_birth"
            label="Ngày tháng năm sinh"
            type="date"
            min="1900-01-01"
            max={new Date().toISOString().slice(0, 10)}
            value={details.date_of_birth}
            onChange={(event) => setDetail('date_of_birth', event.target.value)}
            error={fieldErrors.date_of_birth}
          />
          <div className="stack" style={{ gap: 6 }}>
            <span className="field">Giới tính</span>
            <Segmented
              label="Giới tính"
              value={details.gender}
              options={[
                { value: 'male', text: 'Nam' },
                { value: 'female', text: 'Nữ' },
              ]}
              onChange={(value) => setDetail('gender', details.gender === value ? '' : value)}
            />
          </div>
          <TextField
            id="email"
            label="Email"
            value={user.email}
            readOnly
            below={<span className="small muted">Email là tên đăng nhập, không thể thay đổi.</span>}
          />
          <TextField
            id="hometown"
            label="Quê quán"
            maxLength={100}
            placeholder="vd Đồng Nai"
            value={details.hometown}
            onChange={(event) => setDetail('hometown', event.target.value)}
            error={fieldErrors.hometown}
          />
          <TextField
            id="citizen_id"
            label="Số CCCD"
            inputMode="numeric"
            maxLength={12}
            autoComplete="off"
            placeholder={user.citizen_id_masked ?? 'Nhập 12 chữ số'}
            value={citizenId}
            onChange={(event) => {
              setCitizenId(event.target.value.replace(/\D/g, ''));
              if (fieldErrors.citizen_id) setFieldErrors((e) => ({ ...e, citizen_id: '' }));
            }}
            error={fieldErrors.citizen_id}
            below={
              <span className="small muted">
                {user.citizen_id_masked
                  ? `Đang lưu: ${user.citizen_id_masked} (đã ẩn). Để trống nếu không đổi.`
                  : 'Số CCCD được mã hóa khi lưu, chỉ hiển thị 3 số đầu.'}
              </span>
            }
          />
          <TextField
            id="phone"
            label="Số điện thoại"
            type="tel"
            inputMode="tel"
            maxLength={15}
            autoComplete="tel"
            placeholder="vd 0912345678"
            value={details.phone}
            onChange={(event) => setDetail('phone', event.target.value)}
            error={fieldErrors.phone}
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
            Lưu thay đổi <ArrowIcon />
            <span className="spinner" aria-hidden="true" />
          </button>
        </div>
      </form>
    </SettingsLayout>
  );
}
