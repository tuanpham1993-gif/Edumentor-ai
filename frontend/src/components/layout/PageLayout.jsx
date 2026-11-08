// Khung trang cho người đã đăng nhập: Header + nội dung trang con (<Outlet />) + Footer.
// (FĐ2; FĐ7 08/11: thêm Footer + nền chuyển động PageBackdrop; đổi trang → nội dung trượt lên lại)
import { Outlet, useLocation } from 'react-router-dom';

import Footer from './Footer.jsx';
import Header from './Header.jsx';
import PageBackdrop from './PageBackdrop.jsx';

export default function PageLayout() {
  const { pathname } = useLocation();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      <PageBackdrop />
      <Header />
      {/* key = đường dẫn → mỗi lần đổi trang React vẽ lại main → chạy lại hiệu ứng vào trang */}
      <main key={pathname} className="container page-in" style={{ width: '100%' }}>
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
