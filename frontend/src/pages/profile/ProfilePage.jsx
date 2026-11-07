// Trang hồ sơ — BẢN TẠM (FĐ2): thông tin cơ bản + đăng xuất để kiểm tra route bảo vệ.
// FĐ5 làm lại theo màn demo Profile (thống kê, Tối/Sáng, hộp thoại đăng xuất…).
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth.js';
import { formatDate, roleLabel } from '../../utils/formatters.js';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate('/login', { replace: true });
  }

  return (
    <section className="card stack" style={{ padding: 28 }}>
      <h1 style={{ margin: 0 }}>{user.full_name}</h1>
      <p className="muted" style={{ margin: 0 }}>
        {user.email}
      </p>
      <div className="row" style={{ gap: 8 }}>
        <span className="chip chip-accent">{roleLabel(user.role)}</span>
        <span className="chip">Tham gia {formatDate(user.created_at)}</span>
      </div>
      <div>
        <button type="button" className="btn btn-soft" onClick={handleLogout}>
          Đăng xuất
        </button>
      </div>
    </section>
  );
}
