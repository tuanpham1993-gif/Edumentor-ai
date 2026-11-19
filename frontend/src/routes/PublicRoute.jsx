// Trang dành cho KHÁCH (đăng nhập, đăng ký…): đã đăng nhập thì chuyển về trang nhà —
// học viên /me, admin /admin (FĐ2; 19/11 thêm admin).
import { Navigate, Outlet } from 'react-router-dom';

import FullPageLoading from '../features/common/components/FullPageLoading.jsx';
import { useAuth } from '../hooks/useAuth.js';
import ServerErrorPage from '../features/common/pages/ServerErrorPage.jsx';
import { homePathFor } from './homePath.js';

export default function PublicRoute() {
  const { status, retry, user } = useAuth();

  if (status === 'loading') return <FullPageLoading />;
  if (status === 'error') return <ServerErrorPage onRetry={retry} />; // máy chủ không phục vụ (503)
  if (status === 'authenticated') return <Navigate to={homePathFor(user)} replace />;
  return <Outlet />; // <Outlet /> = vẽ trang con khớp với URL
}
