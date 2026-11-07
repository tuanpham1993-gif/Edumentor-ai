// "Kiểm tra email của bạn" (module 01 · Tuấn · FĐ4) — theo màn demo ForgotSent.
// Có email (từ trang trước) → nút "Gửi lại yêu cầu" gửi lại ngay, chờ 30 giây giữa 2 lần.
// Không có (vd mở thẳng URL) → nút dẫn về trang Quên mật khẩu.
// Bỏ link "Mở thử liên kết trong email (demo)" của bản demo.
import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

import * as authApi from '../../api/auth.api.js';
import CenterLayout, { BackToLogin, Orb, centerStyles } from '../../components/auth/CenterLayout.jsx';
import { CheckCircleIcon, SendIcon } from '../../components/auth/icons.jsx';
import { parseApiError } from '../../utils/errors.js';

const RESEND_WAIT_SECONDS = 30;

export default function ForgotSentPage() {
  const email = useLocation().state?.email;
  const [wait, setWait] = useState(0); // giây còn phải chờ trước khi gửi lại
  const [notice, setNotice] = useState(null); // { ok, text }
  const [sending, setSending] = useState(false);

  // Đếm ngược mỗi giây
  useEffect(() => {
    if (wait <= 0) return undefined;
    const timer = setTimeout(() => setWait((s) => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [wait]);

  async function handleResend() {
    setSending(true);
    try {
      await authApi.forgotPassword(email);
      setNotice({ ok: true, text: 'Đã gửi lại yêu cầu. Vui lòng kiểm tra hộp thư.' });
      setWait(RESEND_WAIT_SECONDS);
    } catch (err) {
      setNotice({ ok: false, text: parseApiError(err).message });
    } finally {
      setSending(false);
    }
  }

  return (
    <CenterLayout>
      <Orb large animation="fly">
        <SendIcon />
      </Orb>
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ fontSize: 26 }}>Kiểm tra email của bạn</h1>
        <p className="sub">
          Nếu email bạn nhập đã được đăng ký, bạn sẽ nhận được hướng dẫn đặt lại mật khẩu trong vài
          phút tới.
        </p>
      </div>

      <ul className={`inner ${centerStyles.checks}`}>
        {[
          'Liên kết chỉ dùng được một lần.',
          'Liên kết hết hạn sau 30 phút.',
          'Không thấy email? Hãy xem thư mục Spam.',
        ].map((text) => (
          <li key={text}>
            <CheckCircleIcon size={16} />
            {text}
          </li>
        ))}
      </ul>

      {notice && (
        <p className={`alert ${notice.ok ? 'alert-ok' : ''}`} role="status">
          {notice.text}
        </p>
      )}

      {email ? (
        <button
          type="button"
          className={`btn btn-lg btn-block ${sending ? 'loading' : ''}`}
          onClick={handleResend}
          disabled={sending || wait > 0}
        >
          {wait > 0 ? `Gửi lại sau ${wait} giây` : 'Gửi lại yêu cầu'}
          <span className="spinner" aria-hidden="true" />
        </button>
      ) : (
        <Link className="btn btn-lg btn-block" to="/forgot-password">
          Gửi lại yêu cầu
        </Link>
      )}

      <BackToLogin center />
    </CenterLayout>
  );
}
