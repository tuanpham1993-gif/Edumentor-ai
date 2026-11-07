// Khai báo toàn bộ route của app (module 01 · Tuấn · FĐ2, 07/11/2026).
//
// Cách đọc: <Route element={<Lớp bảo vệ />}> bọc các route con.
//   PublicRoute    — chỉ cho khách (đã đăng nhập → về /me)
//   ProtectedRoute — phải đăng nhập (khách → /login)
//   AdminRoute     — phải là admin
//   PageLayout     — thêm Header cho các trang bên trong
// Nhóm khác thêm route của mình vào đúng nhóm bảo vệ (vd /courses, /tutor vào ProtectedRoute).
import { Navigate, Route, Routes } from 'react-router-dom';

import PageLayout from '../components/layout/PageLayout.jsx';
import ForgotPasswordPage from '../pages/auth/ForgotPasswordPage.jsx';
import ForgotSentPage from '../pages/auth/ForgotSentPage.jsx';
import LoginPage from '../pages/auth/LoginPage.jsx';
import RegisterPage from '../pages/auth/RegisterPage.jsx';
import ResetExpiredPage from '../pages/auth/ResetExpiredPage.jsx';
import ResetPasswordPage from '../pages/auth/ResetPasswordPage.jsx';
import NotFoundPage from '../pages/NotFoundPage.jsx';
import ChangePasswordPage from '../pages/profile/ChangePasswordPage.jsx';
import EditProfilePage from '../pages/profile/EditProfilePage.jsx';
import ProfilePage from '../pages/profile/ProfilePage.jsx';
import AdminRoute from './AdminRoute.jsx';
import ProtectedRoute from './ProtectedRoute.jsx';
import PublicRoute from './PublicRoute.jsx';

function AdminHomePlaceholder() {
  return <p className="muted">Trang quản trị (Khôi / Tâm / Hòa) — đang phát triển.</p>;
}

export default function AppRoutes() {
  return (
    <Routes>
      {/* Khách */}
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/forgot-sent" element={<ForgotSentPage />} />
      </Route>

      {/* Link trong email: ai cũng mở được, kể cả đang đăng nhập → để NGOÀI mọi lớp bảo vệ */}
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/reset-expired" element={<ResetExpiredPage />} />

      {/* Học viên (đã đăng nhập) */}
      <Route element={<ProtectedRoute />}>
        <Route element={<PageLayout />}>
          <Route path="/me" element={<ProfilePage />} />
          <Route path="/me/edit" element={<EditProfilePage />} />
          <Route path="/me/password" element={<ChangePasswordPage />} />
          {/* FĐ6: /me/skills */}
        </Route>
      </Route>

      {/* Quản trị */}
      <Route element={<AdminRoute />}>
        <Route element={<PageLayout />}>
          <Route path="/admin" element={<AdminHomePlaceholder />} />
        </Route>
      </Route>

      <Route path="/" element={<Navigate to="/me" replace />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
