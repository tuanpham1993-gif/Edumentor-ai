// Trang dành cho KHÁCH (đăng nhập, đăng ký…): đã đăng nhập thì chuyển về hồ sơ. (FĐ2)
import { Navigate, Outlet } from 'react-router-dom';

import FullPageLoading from '../components/common/FullPageLoading.jsx';
import { useAuth } from '../hooks/useAuth.js';

export default function PublicRoute() {
  const { status } = useAuth();

  if (status === 'loading') return <FullPageLoading />;
  if (status === 'authenticated') return <Navigate to="/me" replace />;
  return <Outlet />; // <Outlet /> = vẽ trang con khớp với URL
}
