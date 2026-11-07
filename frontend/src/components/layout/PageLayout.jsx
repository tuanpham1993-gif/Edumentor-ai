// Khung trang cho người đã đăng nhập: Header + nội dung trang con (<Outlet />). (FĐ2)
import { Outlet } from 'react-router-dom';

import Header from './Header.jsx';

export default function PageLayout() {
  return (
    <>
      <Header />
      <main className="container page-in">
        <Outlet />
      </main>
    </>
  );
}
