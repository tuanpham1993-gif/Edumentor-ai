// Trang 404 — URL không khớp route nào. (FĐ2)
import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <main className="container page-in">
      <h1>Không tìm thấy trang</h1>
      <p className="muted">Trang bạn tìm không tồn tại hoặc chưa được làm.</p>
      <Link to="/">← Về trang chính</Link>
    </main>
  );
}
