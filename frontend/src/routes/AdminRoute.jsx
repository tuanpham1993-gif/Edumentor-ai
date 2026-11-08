// Trang QUẢN TRỊ: khách → /login; đăng nhập nhưng không phải admin → về /me. (FĐ2)
// Backend vẫn chặn bằng require_admin (403) — đây chỉ là lớp giao diện.
import { Navigate, Outlet, useLocation } from 'react-router-dom';

import FullPageLoading from '../components/common/FullPageLoading.jsx';
import { useAuth } from '../hooks/useAuth.js';
import ServerErrorPage from '../pages/ServerErrorPage.jsx';

export default function AdminRoute() {
  const { status, user, retry } = useAuth();
  const location = useLocation();

  if (status === 'loading') return <FullPageLoading />;
  if (status === 'error') return <ServerErrorPage onRetry={retry} />; // máy chủ không phục vụ (503)
  if (status !== 'authenticated') {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  if (user.role !== 'admin') return <Navigate to="/me" replace />;
  return <Outlet />;
}
