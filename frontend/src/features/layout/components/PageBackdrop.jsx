// Nền chuyển động cho các trang SAU KHI đăng nhập (FĐ7, 08/11/2026) — cùng tông trang chủ.
//   - Quầng sáng vàng lớn phía trên, "thở" chậm
//   - 2 vầng sáng mờ trôi chậm hai bên (aurora)
//   - Hạt bụi sáng bay lên
// Lớp cố định phía sau nội dung (position: fixed, pointer-events: none) → không ảnh hưởng bố cục,
// cuộn trang vẫn giữ nền. Người dùng chọn "giảm chuyển động" → styles/reduced-motion.css tắt hiệu ứng.
import styles from '../styles/PageBackdrop.module.css';

// [vị trí ngang %, cỡ px, trễ s, thời gian s] — cố định để mỗi lần vẽ giống nhau
const PARTICLES = [
  [4, 3, 0, 16], [11, 2, 5, 13], [19, 3, 9, 18], [27, 2, 2, 14], [36, 3, 11, 17],
  [44, 2, 7, 12], [52, 3, 3, 19], [61, 2, 13, 15], [69, 3, 6, 16], [77, 2, 1, 13],
  [85, 3, 10, 18], [93, 2, 4, 14],
];

export default function PageBackdrop() {
  return (
    <div className={styles.backdrop} aria-hidden="true">
      <span className={styles.glow} />
      <span className={`${styles.aurora} ${styles.left}`} />
      <span className={`${styles.aurora} ${styles.right}`} />
      <div className={styles.particles}>
        {PARTICLES.map(([left, size, delay, duration]) => (
          <span
            key={`${left}-${delay}`}
            style={{
              left: `${left}%`,
              width: size,
              height: size,
              animationDelay: `-${delay}s`,
              animationDuration: `${duration}s`,
            }}
          />
        ))}
      </div>
    </div>
  );
}
