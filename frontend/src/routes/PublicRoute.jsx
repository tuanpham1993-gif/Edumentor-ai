// Trang dành cho KHÁCH (đăng nhập, đăng ký…): đã đăng nhập thì chuyển về hồ sơ. (FĐ2)
import { Navigate, Outlet } from 'react-router-dom';

import FullPageLoading from '../features/common/components/FullPageLoading.jsx';
import { useAuth } from '../hooks/useAuth.js';
import ServerErrorPage from '../features/common/pages/ServerErrorPage.jsx';

export default function PublicRoute() {
  const { status, retry } = useAuth();

  if (status === 'loading') return <FullPageLoading />;
  if (status === 'error') return <ServerErrorPage onRetry={retry} />; // máy chủ không phục vụ (503)
  if (status === 'authenticated') return <Navigate to="/me" replace />;
  return <Outlet />; // <Outlet /> = vẽ trang con khớp với URL
}
