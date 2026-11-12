// Trang 404 — URL không khớp route nào. (FĐ2; FĐ7 08/11: dùng StatusPanel)
import { Link } from 'react-router-dom';

import StatusPanel from '../components/StatusPanel.jsx';

export default function NotFoundPage() {
  return (
    <StatusPanel
      fullPage
      icon="search"
      title="Không tìm thấy trang"
      code="404 · Not Found"
      codeLarge
      actions={
        <Link to="/" className="btn btn-primary">
          ← Về trang chính
        </Link>
      }
    >
      Trang bạn tìm không tồn tại hoặc đã được chuyển đi.
    </StatusPanel>
  );
}
