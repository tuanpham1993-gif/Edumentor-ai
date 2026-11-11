// "Liên kết không còn hiệu lực" (module 01 · Tuấn · FĐ4) — theo màn demo ResetExpired.
// Tới đây khi: link không có token, token sai, đã hết hạn (30 phút) hoặc đã dùng.
import { Link } from 'react-router-dom';

import CenterLayout, { BackToLogin, Orb } from '../components/CenterLayout.jsx';
import { ArrowIcon, ClockIcon } from '../../common/components/icons.jsx';

export default function ResetExpiredPage() {
  return (
    <CenterLayout>
      <Orb large animation="tick">
        <ClockIcon />
      </Orb>
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ fontSize: 26 }}>Liên kết không còn hiệu lực</h1>
        <p className="sub">
          Liên kết đặt lại mật khẩu không đúng, đã hết hạn hoặc đã được sử dụng. Mật khẩu của bạn
          chưa thay đổi.
        </p>
      </div>
      <Link className="btn btn-primary btn-lg btn-block" to="/forgot-password">
        Gửi yêu cầu mới <ArrowIcon />
      </Link>
      <BackToLogin center />
    </CenterLayout>
  );
}
