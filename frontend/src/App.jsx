import { BrowserRouter } from 'react-router-dom';

// Thứ tự bọc theo docs/structure.md §1: BrowserRouter → ToastProvider → CardOpeningProvider → routes + ChatBubble.
// ToastProvider, CardOpeningProvider (C2) và khai báo route (C3) chưa được thêm ở giai đoạn C1.
export default function App() {
  return (
    <BrowserRouter>
      <main className="container page-in">
        <div className="page-head">
          <div>
            <h1>EduMentor AI</h1>
            <p>Nền frontend đã sẵn sàng. Các trang sẽ được thêm ở những giai đoạn sau.</p>
          </div>
        </div>
      </main>
    </BrowserRouter>
  );
}
