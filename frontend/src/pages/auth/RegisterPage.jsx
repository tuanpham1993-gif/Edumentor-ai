// Trang đăng ký — CHỖ GIỮ (FĐ2). FĐ3 làm đầy đủ theo màn demo Register.
import { Link } from 'react-router-dom';

export default function RegisterPage() {
  return (
    <main className="container page-in" style={{ maxWidth: 440 }}>
      <div className="card stack" style={{ padding: 28 }}>
        <h1 style={{ margin: 0 }}>Đăng ký</h1>
        <p className="muted">Trang đăng ký sẽ được làm ở FĐ3.</p>
        <Link to="/login">← Quay lại đăng nhập</Link>
      </div>
    </main>
  );
}
