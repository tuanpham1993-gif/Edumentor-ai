// Khung trang Đăng nhập / Đăng ký (FĐ3, theo màn demo Main-LampOff / Register).
//
// Mở trang: 3 đèn TẮT, form ẩn và bị khóa. Kéo dây ở đèn đầu tiên → cả 3 đèn sáng, form hiện.
// Kéo lần nữa → tắt. Thẻ `children` là nội dung bên trong thẻ form (do từng trang truyền vào).
//
//   cardClassName : thêm class cho thẻ (vd "shake" khi đăng nhập sai)
//   onCardAnimationEnd : gỡ class "shake" khi rung xong để lần sai sau rung lại được
import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

import styles from './AuthLayout.module.css';
import { BrandLogo, CheckCircleIcon } from './icons.jsx';
import Lamp from './Lamp.jsx';

const FEATURES = [
  'Lộ trình học do AI đề xuất theo mục tiêu',
  'Gợi ý khóa học theo từng kỹ năng',
  'Ôn tập 20 câu để ghi nhận kỹ năng',
];

export default function AuthLayout({ children, cardClassName = '', onCardAnimationEnd }) {
  const [lampOn, setLampOn] = useState(false);
  const [flashKey, setFlashKey] = useState(0); // đổi key → vẽ lại lớp "lóe sáng" mỗi lần bật
  const cardRef = useRef(null);

  // Đèn tắt: thẻ form không bấm / Tab được (inert). React 18 chưa hỗ trợ prop `inert` → đặt bằng ref.
  useEffect(() => {
    const card = cardRef.current;
    if (!card) return;
    if (lampOn) card.removeAttribute('inert');
    else card.setAttribute('inert', '');
  }, [lampOn]);

  function toggleLamp() {
    const next = !lampOn;
    if (next) setFlashKey((key) => key + 1); // vừa bật → lóe sáng
    setLampOn(next);
  }

  return (
    <div className={styles.split}>
      <aside className={`${styles.hero} ${lampOn ? '' : styles.dark}`}>
        <Lamp on={lampOn} right={300} cord={120} glowTop={-30} delay={0} onPull={toggleLamp} />
        <div className={styles.hideOnPhone}>
          <Lamp on={lampOn} right={150} cord={220} glowTop={70} delay={-1.8} />
          <Lamp on={lampOn} right={30} cord={70} glowTop={-80} delay={-3.1} />
        </div>

        <Link className={styles.brand} to="/login">
          <BrandLogo />
          EduMentor AI
        </Link>

        <div className={styles.copy}>
          <h2>
            Học đúng hướng,
            <br />
            <span>tiến bộ mỗi ngày.</span>
          </h2>
          <p>
            EduMentor AI gợi ý lộ trình theo mục tiêu, kết nối khóa học MOOC phù hợp và ghi nhận
            kỹ năng qua bài ôn tập.
          </p>
          <div className={styles.features}>
            {FEATURES.map((text) => (
              <span key={text}>
                <CheckCircleIcon />
                {text}
              </span>
            ))}
          </div>
          <span className={styles.lampState} aria-live="polite">
            {lampOn ? 'Kéo dây đèn lần nữa để tắt cả 3 đèn' : 'Đèn đang tắt · kéo dây đèn để mở trang'}
          </span>
          <span className={styles.copyright}>© 2026 EduMentor AI</span>
        </div>
      </aside>

      <main className={`${styles.formSide} ${lampOn ? '' : styles.formDark}`}>
        <div className={styles.stage}>
          <div
            ref={cardRef}
            className={`${styles.card} ${lampOn ? '' : styles.cardOff} ${cardClassName}`}
            aria-hidden={!lampOn}
            onAnimationEnd={(event) => {
              // Chỉ nhận hiệu ứng của CHÍNH thẻ (vd rung); hiệu ứng của phần tử con cũng "nổi bọt" lên đây.
              if (event.target === event.currentTarget) onCardAnimationEnd?.(event);
            }}
          >
            {lampOn && <div key={flashKey} className={styles.flash} aria-hidden="true" />}
            {children}
          </div>
          <p className={`${styles.darkHint} ${lampOn ? '' : styles.darkHintOn}`} aria-hidden={lampOn}>
            Trời tối quá, không thấy gì cả.
            <br />
            Kéo dây đèn để bật đèn và mở trang.
          </p>
        </div>
      </main>
    </div>
  );
}
