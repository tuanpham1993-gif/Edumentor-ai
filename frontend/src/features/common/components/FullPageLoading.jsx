// Màn chờ khi đang kiểm tra đăng nhập (status = 'loading'). (FĐ2)
export default function FullPageLoading() {
  return (
    <main className="container" aria-busy="true">
      <p className="muted">Đang tải…</p>
    </main>
  );
}
