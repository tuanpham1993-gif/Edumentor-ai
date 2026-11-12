// "Tạm thời chưa khả dụng" cho tính năng chưa làm xong (module 01 · Tuấn · FĐ7, 08/11/2026).
// Không phải lỗi máy chủ → KHÔNG dùng 500 / 503. Mã đúng nghĩa: 501 Not Implemented.
// Dùng: <ComingSoon feature="Kỹ năng của tôi" />  (vd /me/skills cho tới khi có FĐ6)
// Nhóm khác dùng lại cho trang chưa làm (khóa học, AI Tutor…).
import { Link } from 'react-router-dom';

import StatusPanel from './StatusPanel.jsx';

export default function ComingSoon({ feature, backTo = '/me', backText = '← Về hồ sơ' }) {
  return (
    <StatusPanel
      icon="tool"
      title="Tạm thời chưa khả dụng"
      code="Mã: 501 · Chưa hỗ trợ"
      actions={
        <>
          <Link to={backTo} className="btn">
            {backText}
          </Link>
          {/* Tải lại trang: khi tính năng đã được cập nhật sẽ hiện ra */}
          <button type="button" className="btn btn-primary" onClick={() => window.location.reload()}>
            Thử lại
          </button>
        </>
      }
    >
      Tính năng {feature} đang được phát triển, sẽ sớm có.
    </StatusPanel>
  );
}
