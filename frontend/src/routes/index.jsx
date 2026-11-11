// Khai báo toàn bộ route của app (module 01 · Tuấn · FĐ2, 07/11/2026).
//
// Cách đọc: <Route element={<Lớp bảo vệ />}> bọc các route con.
//   PublicRoute    — chỉ cho khách (đã đăng nhập → về /me); "/" = trang chủ khách (08/11)
//   ProtectedRoute — phải đăng nhập (khách → /login)
//   AdminRoute     — phải là admin
//   PageLayout     — thêm Header cho các trang bên trong
// Nhóm khác thêm route của mình vào đúng nhóm bảo vệ (vd /courses, /tutor vào ProtectedRoute).
import { Route, Routes } from 'react-router-dom';

import ComingSoon from '../features/common/components/ComingSoon.jsx';
import PageLayout from '../features/layout/components/PageLayout.jsx';
import { MAIN_NAV } from '../features/layout/nav.js';
import ForgotPasswordPage from '../features/auth/pages/ForgotPasswordPage.jsx';
import ForgotSentPage from '../features/auth/pages/ForgotSentPage.jsx';
import LoginPage from '../features/auth/pages/LoginPage.jsx';
import RegisterPage from '../features/auth/pages/RegisterPage.jsx';
import ResetExpiredPage from '../features/auth/pages/ResetExpiredPage.jsx';
import ResetPasswordPage from '../features/auth/pages/ResetPasswordPage.jsx';
import HomePage from '../features/home/pages/HomePage.jsx';
import NotFoundPage from '../features/common/pages/NotFoundPage.jsx';
import AppearancePage from '../features/profile/pages/AppearancePage.jsx';
import ChangePasswordPage from '../features/profile/pages/ChangePasswordPage.jsx';
import EmailNotificationsPage from '../features/profile/pages/EmailNotificationsPage.jsx';
import EditProfilePage from '../features/profile/pages/EditProfilePage.jsx';
import ProfilePage from '../features/profile/pages/ProfilePage.jsx';
import SkillBrowsePage from '../features/profile/pages/SkillBrowsePage.jsx';
import SkillsPage from '../features/profile/pages/SkillsPage.jsx';
import ReviewHistoryPage from '../features/review/pages/ReviewHistoryPage.jsx';
import ReviewQuizPage from '../features/review/pages/ReviewQuizPage.jsx';
import ReviewResultPage from '../features/review/pages/ReviewResultPage.jsx';
import ReviewStartPage from '../features/review/pages/ReviewStartPage.jsx';
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
        <Route path="/" element={<HomePage />} />
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
          {/* Cài đặt: Giao diện + Thông báo qua email (11/11) */}
          <Route path="/me/appearance" element={<AppearancePage />} />
          <Route path="/me/email-notifications" element={<EmailNotificationsPage />} />
          {/* Ôn tập — module 09 (Tuấn, GĐ4 09/11) */}
          <Route path="/me/review-history" element={<ReviewHistoryPage />} />
          <Route path="/courses/:courseId/review" element={<ReviewStartPage />} />
          <Route path="/review/:attemptId" element={<ReviewQuizPage />} />
          <Route path="/review/:attemptId/result" element={<ReviewResultPage />} />
          {/* Trang của nhóm khác / module 09 chưa làm → "Tạm thời chưa khả dụng" (08/11).
              Nhóm làm xong: thêm <Route path="..." element={<TrangThat />} /> PHÍA TRÊN dòng này
              (React Router chọn route khớp cụ thể nhất, route thật sẽ được dùng). */}
          {MAIN_NAV.map((item) => (
            <Route
              key={item.to}
              path={item.to}
              element={<ComingSoon feature={item.text} backTo="/me" />}
            />
          ))}
          <Route path="/me/skills" element={<SkillsPage />} />
          <Route path="/me/skills/browse" element={<SkillBrowsePage />} />
        </Route>
      </Route>

      {/* Quản trị */}
      <Route element={<AdminRoute />}>
        <Route element={<PageLayout />}>
          <Route path="/admin" element={<AdminHomePlaceholder />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
