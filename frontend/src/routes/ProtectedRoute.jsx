// Trang CẦN ĐĂNG NHẬP: khách → chuyển /login, nhớ trang định vào để quay lại sau. (FĐ2)
// Đây chỉ là lớp tiện cho người dùng — backend vẫn kiểm tra token ở mọi API (NFR-05).
import { Navigate, Outlet, useLocation } from 'react-router-dom';

import FullPageLoading from '../components/common/FullPageLoading.jsx';
import { useAuth } from '../hooks/useAuth.js';

export default function ProtectedRoute() {
  const { status } = useAuth();
  const location = useLocation();

  if (status === 'loading') return <FullPageLoading />;
  if (status !== 'authenticated') {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return <Outlet />;
}
