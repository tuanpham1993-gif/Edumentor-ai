// Khung trang cho KHÁCH ở các trang công khai không phải trang chủ (19/11/2026 — G1 kế hoạch luồng trang chủ).
// Header khách (menu neo về trang chủ + nút Đăng nhập) + nội dung (<Outlet />) + Footer bản khách.
// Dùng qua OpenRoute: khách thấy khung này, người đã đăng nhập thấy PageLayout như mọi trang khác.
import { Outlet, useLocation } from 'react-router-dom';

import Footer from './Footer.jsx';
import PageBackdrop from './PageBackdrop.jsx';
import PublicHeader from './PublicHeader.jsx';

export default function GuestLayout() {
  const { pathname } = useLocation();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      <PageBackdrop />
      <PublicHeader />
      <main key={pathname} className="container page-in" style={{ width: '100%' }}>
        <Outlet />
      </main>
      <Footer guest />
    </div>
  );
}
