// Trang MENTOR (G3f, 25/11 — Tuấn): khách → /login; không phải mentor / admin → về /me.
// Backend vẫn chặn bằng require_mentor (403) — đây chỉ là lớp giao diện.
import { Navigate, Outlet, useLocation } from 'react-router-dom';

import FullPageLoading from '../features/common/components/FullPageLoading.jsx';
import ServerErrorPage from '../features/common/pages/ServerErrorPage.jsx';
import { useAuth } from '../hooks/useAuth.js';

export default function MentorRoute() {
  const { status, user, retry } = useAuth();
  const location = useLocation();

  if (status === 'loading') return <FullPageLoading />;
  if (status === 'error') return <ServerErrorPage onRetry={retry} />;
  if (status !== 'authenticated') {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  if (user.role !== 'mentor' && user.role !== 'admin') return <Navigate to="/me" replace />;
  return <Outlet />;
}
