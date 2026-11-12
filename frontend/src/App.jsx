// Component gốc (FĐ2, 07/11/2026).
// Thứ tự bọc: BrowserRouter (điều hướng) → AuthProvider (trạng thái đăng nhập, cần useNavigate) → routes.
import { BrowserRouter } from 'react-router-dom';

import AppRoutes from './routes/index.jsx';
import { AuthProvider } from './store/authStore.js';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
