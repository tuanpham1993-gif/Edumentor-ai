// Thanh tab dạng "viên thuốc" có nền vàng trượt theo tab đang chọn (FĐ6, 08/11/2026) —
// theo màn demo (_tabs_aoy8b). Dùng chung: Kỹ năng của tôi (Tuấn), Khóa học của tôi (Tâm)…
//
//   <Tabs label="Lọc kỹ năng" value={tab} onChange={setTab}
//         items={[{ value: 'all', text: 'Tất cả', count: 6 }, …]} />
//   count: không bắt buộc — có thì hiện " (6)" sau chữ.
// Bàn phím: ← → chuyển tab (chuẩn role="tablist").
import { useLayoutEffect, useRef, useState } from 'react';

import styles from '../styles/Tabs.module.css';

export default function Tabs({ items, value, onChange, label }) {
  const listRef = useRef(null);
  const [pill, setPill] = useState(null); // vị trí / kích thước nền trượt

  // Đo nút đang chọn để đặt nền trượt đúng chỗ (chạy lại khi đổi tab hoặc số đếm đổi độ rộng)
  useLayoutEffect(() => {
    const active = listRef.current?.querySelector('[aria-selected="true"]');
    if (!active) return;
    setPill({ x: active.offsetLeft, y: active.offsetTop, w: active.offsetWidth, h: active.offsetHeight });
  }, [value, items]);

  function handleKeyDown(event) {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    const index = items.findIndex((item) => item.value === value);
    const step = event.key === 'ArrowRight' ? 1 : -1;
    const next = items[(index + step + items.length) % items.length];
    onChange(next.value);
    listRef.current?.querySelector(`[data-value="${next.value}"]`)?.focus();
  }

  return (
    <div ref={listRef} className={styles.tabs} role="tablist" aria-label={label} onKeyDown={handleKeyDown}>
      {pill && (
        <span
          className={styles.pill}
          aria-hidden="true"
          style={{ transform: `translate(${pill.x}px, ${pill.y}px)`, width: pill.w, height: pill.h }}
        />
      )}
      {items.map((item) => {
        const selected = item.value === value;
        return (
          <button
            key={item.value}
            type="button"
            role="tab"
            data-value={item.value}
            aria-selected={selected}
            tabIndex={selected ? 0 : -1}
            className={`${styles.tab} ${selected ? styles.active : ''}`}
            onClick={() => onChange(item.value)}
          >
            {item.text}
            {item.count !== undefined && <span className={styles.count}>&nbsp;({item.count})</span>}
          </button>
        );
      })}
    </div>
  );
}
