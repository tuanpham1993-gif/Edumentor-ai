// Trang AI CŨNG XEM ĐƯỢC (19/11/2026 — G1 kế hoạch luồng trang chủ; BA UC-06: khách xem khóa học).
//   Khách          → khung GuestLayout (header khách, footer khách).
//   Đã đăng nhập   → khung PageLayout (header học viên) như các trang khác.
// Khác PublicRoute: KHÔNG đẩy người đã đăng nhập đi chỗ khác. Khác ProtectedRoute: KHÔNG bắt đăng nhập.
// Trong trang: nút cần tài khoản (Lưu, Tham gia, Ôn tập…) tự kiểm tra `useAuth().status` và chuyển khách tới
//   navigate('/login', { state: { from: location.pathname } })  → đăng nhập xong quay lại đúng trang.
import { useAuth } from '../hooks/useAuth.js';
import FullPageLoading from '../features/common/components/FullPageLoading.jsx';
import ServerErrorPage from '../features/common/pages/ServerErrorPage.jsx';
import GuestLayout from '../features/layout/components/GuestLayout.jsx';
import PageLayout from '../features/layout/components/PageLayout.jsx';

export default function OpenRoute() {
  const { status, retry } = useAuth();

  if (status === 'loading') return <FullPageLoading />;
  if (status === 'error') return <ServerErrorPage onRetry={retry} />; // máy chủ không phục vụ (503)
  return status === 'authenticated' ? <PageLayout /> : <GuestLayout />;
}
