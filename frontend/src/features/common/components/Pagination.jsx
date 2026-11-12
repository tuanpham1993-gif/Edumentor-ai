// Phân trang dùng chung (FĐ6, 08/11/2026): « Trước  1 … 4 [5] 6 … 17  Sau »
// Dùng: <Pagination page={page} totalPages={17} onChange={setPage} />
// Ẩn khi chỉ có 1 trang. Khôi có thể dùng lại cho danh mục khóa học.
import styles from '../styles/Pagination.module.css';

/** Các số trang cần hiện: luôn có trang đầu, cuối, và 1 trang hai bên trang hiện tại. */
function pageNumbers(page, total) {
  const set = new Set([1, total, page - 1, page, page + 1]);
  const pages = [...set].filter((p) => p >= 1 && p <= total).sort((a, b) => a - b);
  const out = [];
  pages.forEach((p, i) => {
    if (i > 0 && p - pages[i - 1] > 1) out.push(`gap-${p}`); // dấu …
    out.push(p);
  });
  return out;
}

export default function Pagination({ page, totalPages, onChange, label = 'Phân trang' }) {
  if (totalPages <= 1) return null;
  return (
    <nav className={styles.pager} aria-label={label}>
      <button
        type="button"
        className={styles.step}
        disabled={page <= 1}
        onClick={() => onChange(page - 1)}
      >
        ‹ Trước
      </button>
      {pageNumbers(page, totalPages).map((p) =>
        typeof p === 'string' ? (
          <span key={p} className={styles.gap} aria-hidden="true">
            …
          </span>
        ) : (
          <button
            key={p}
            type="button"
            className={`${styles.num} ${p === page ? styles.current : ''}`}
            aria-current={p === page ? 'page' : undefined}
            onClick={() => onChange(p)}
          >
            {p}
          </button>
        ),
      )}
      <button
        type="button"
        className={styles.step}
        disabled={page >= totalPages}
        onClick={() => onChange(page + 1)}
      >
        Sau ›
      </button>
    </nav>
  );
}
