// Một chiếc đèn treo; chiếc đầu tiên có dây kéo (FĐ3, theo màn demo Main / Register).
//   right    : khoảng cách tới mép phải (px)
//   cord     : chiều dài dây treo (px) — 3 đèn dài ngắn khác nhau
//   glowTop  : vị trí quầng sáng
//   delay    : lệch nhịp đung đưa
//   onPull   : có truyền → hiện dây kéo; bấm dây → gọi onPull()
import { useEffect, useRef, useState } from 'react';

import styles from '../styles/Lamp.module.css';

export default function Lamp({ on, right, cord, glowTop, delay = 0, onPull }) {
  const [pulling, setPulling] = useState(false); // dây đang bị kéo xuống (160 ms)
  const [flick, setFlick] = useState(false); // nhấp nháy khi vừa bật
  const wasOn = useRef(on); // trạng thái lần vẽ trước

  useEffect(() => {
    const justTurnedOn = on && !wasOn.current; // chỉ nhấp nháy khi TẮT → BẬT,
    wasOn.current = on; //                      không nhấp nháy khi vào trang mà đèn đã sáng sẵn
    if (!justTurnedOn) return undefined;
    setFlick(true);
    const timer = setTimeout(() => setFlick(false), 420);
    return () => clearTimeout(timer);
  }, [on]);

  function handlePull() {
    setPulling(true);
    setTimeout(() => setPulling(false), 160);
    onPull();
  }

  const height = cord + 64; // dây + chao đèn + bóng
  return (
    <div
      className={`${styles.lamp} ${on ? '' : styles.off}`}
      style={{ right, animationDelay: `${delay}s` }}
    >
      <div
        className={`${styles.glow} ${flick ? styles.flick : ''}`}
        aria-hidden="true"
        style={{ top: glowTop }}
      />
      <svg width="120" height={height} viewBox={`0 0 120 ${height}`} aria-hidden="true">
        <line x1="60" y1="0" x2="60" y2={cord} stroke="#2b2622" strokeWidth="3" />
        <path d={`M32 ${cord}h56l20 50H12z`} fill="#1b1a19" stroke="#3a342d" />
        <ellipse className={styles.ring} cx="60" cy={cord + 50} rx="48" ry="7" />
        <circle className={styles.core} cx="60" cy={cord + 57} r="11" />
      </svg>

      {onPull && (
        <button
          type="button"
          className={`${styles.pull} ${pulling ? styles.pulling : ''}`}
          aria-pressed={on}
          aria-label={on ? 'Tắt đèn (ẩn trang)' : 'Bật đèn (hiện trang)'}
          onClick={handlePull}
          style={{ top: cord + 49, '--dy': pulling ? '16px' : '0px', '--sy': pulling ? 1.3 : 1 }}
        >
          <span className={styles.string} />
          <span className={styles.bead} />
        </button>
      )}
    </div>
  );
}
